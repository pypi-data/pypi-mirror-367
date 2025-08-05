import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Callable, Dict, List, Optional, Type

from sibi_dst.utils import ManagedResource

class ArtifactUpdaterMultiWrapperThreaded(ManagedResource):
    """
    Updates artifacts concurrently using a ThreadPoolExecutor.

    This version is refactored for a pure multi-threaded environment, aligning
    the orchestration model with the underlying threaded workers (DataWrapper).
    """
    wrapped_classes: Dict[str, List[Type]]
    def __init__(
            self,
            wrapped_classes: Dict[str, List[Type]],
            *,
            max_workers: int = 4,
            retry_attempts: int = 3,
            backoff_base: int = 2,
            backoff_max: int = 60,
            backoff_jitter: float = 0.1,
            priority_fn: Optional[Callable[[Type], int]] = None,
            artifact_class_kwargs: Optional[Dict[str, Any]] = None,
            **kwargs: Dict[str, Any]
    ) -> None:
        super().__init__(**kwargs)
        self.wrapped_classes = wrapped_classes
        self.max_workers = max_workers
        self.retry_attempts = retry_attempts
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        self.backoff_jitter = backoff_jitter
        self.priority_fn = priority_fn
        # Default artifact init kwargs
        today = datetime.datetime.today() + datetime.timedelta(days=1)
        default_kwargs = {
            'parquet_start_date': today.strftime('%Y-%m-%d'),
            'parquet_end_date':   today.strftime('%Y-%m-%d'),
            'logger':             self.logger,
            'debug':              self.debug,
            'fs':                self.fs,
            'verbose':            self.verbose,
        }
        self.artifact_class_kwargs = artifact_class_kwargs or default_kwargs.copy()

        # State tracking
        self.completion_times: Dict[str, float] = {}
        self.failed: List[str] = []
        self.original_classes: List[Type] = []
        self.logger.info("ArtifactUpdaterMultiWrapperThreaded initialized")

    def get_artifact_classes(self, data_type: str) -> List[Type]:
        """Retrieve artifact classes by data type."""
        self.logger.info(f"Fetching artifact classes for '{data_type}'")
        classes = self.wrapped_classes.get(data_type)
        if not classes:
            raise ValueError(f"Unsupported data type: {data_type}")
        self.logger.info(f"Found {len(classes)} artifact classes for '{data_type}'")
        return classes

    def estimate_priority(self, artifact_cls: Type) -> int:
        """
        Determines task priority. Lower values run first.
        Note: This is a blocking call and will run sequentially before updates start.
        """
        name = artifact_cls.__name__
        # Custom priority function takes precedence
        if self.priority_fn:
            try:
                return self.priority_fn(artifact_cls)
            except Exception as e:
                self.logger.warning(f"priority_fn error for {name}: {e}")

        # # Fallback to size estimate if available
        # if hasattr(artifact_cls, 'get_size_estimate'):
        #     try:
        #         # This performs blocking I/O
        #         return artifact_cls(**self.artifact_class_kwargs).get_size_estimate()
        #
        #     except Exception as e:
        #         self.logger.warning(f"get_size_estimate failed for {name}: {e}")

        # Default priority
        return 999

    def _update_artifact_with_retry(self, artifact_cls: Type, update_kwargs: Dict[str, Any]) -> str:
        """
        A blocking worker function that handles instantiation, update, and retries for a single artifact.
        This function is designed to be run in a ThreadPoolExecutor.
        """
        name = artifact_cls.__name__
        self.logger.debug(f"Worker thread starting update for {name}")

        for attempt in range(1, self.retry_attempts + 1):
            try:
                # Instantiate and update directly within the worker thread
                artifact_instance = artifact_cls(**self.artifact_class_kwargs)
                artifact_instance.update_parquet(**update_kwargs)

                self.logger.info(f"✅ {name} updated successfully on attempt {attempt}")
                return name  # Return the name on success

            except Exception as e:
                self.logger.error(f"Error on {name} attempt {attempt}/{self.retry_attempts}: {e}", exc_info=self.debug)
                if attempt < self.retry_attempts:
                    delay = min(self.backoff_base ** (attempt - 1), self.backoff_max)
                    delay *= 1 + random.uniform(0, self.backoff_jitter)
                    self.logger.info(f"Sleeping {delay:.1f}s before retrying {name}")
                    time.sleep(delay)

        # If all retries fail, raise an exception to be caught by the main loop
        raise RuntimeError(f"{name} failed after {self.retry_attempts} attempts.")

    async def update_data(self, data_type: str, **kwargs: Any) -> None:
        """
        Entry point to update all artifacts of a given type using a ThreadPoolExecutor.
        """
        self.logger.debug(f"Starting multi-threaded update for '{data_type}' with kwargs={kwargs}")

        # Reset state for this run
        self.completion_times.clear()
        self.failed.clear()
        self.original_classes = self.get_artifact_classes(data_type)

        # Sequentially estimate priorities and sort classes before execution
        self.logger.debug("Estimating priorities to order tasks...")
        ordered_classes = sorted(self.original_classes, key=self.estimate_priority)
        self.logger.debug("Priority estimation complete. Submitting tasks to thread pool.")

        start_time = time.monotonic()

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_class_name = {
                executor.submit(self._update_artifact_with_retry, cls, kwargs): cls.__name__
                for cls in ordered_classes
            }

            for future in as_completed(future_to_class_name):
                name = future_to_class_name[future]
                try:
                    # result() will re-raise the exception from the worker if one occurred
                    future.result()
                    # If no exception, the task succeeded
                    self.completion_times[name] = time.monotonic() - start_time
                except Exception as e:
                    self.logger.error(f"✖️ {name} permanently failed. See error log above.")
                    self.failed.append(name)

        # Log final status
        total = len(self.original_classes)
        completed = len(self.completion_times)
        failed_count = len(self.failed)
        self.logger.info(f"All artifacts processed: total={total}, completed={completed}, failed={failed_count}")

    def get_update_status(self) -> Dict[str, Any]:
        """Returns a summary status including completion times."""
        completed_set = set(self.completion_times.keys())
        failed_set = set(self.failed)
        pending_set = {cls.__name__ for cls in self.original_classes} - completed_set - failed_set

        return {
            'total': len(self.original_classes),
            'completed': list(completed_set),
            'failed': list(failed_set),
            'pending': list(pending_set),
            'completion_times': self.completion_times,
        }

    @staticmethod
    def format_status_table(status: Dict[str, Any]) -> str:
        """Formats the status dictionary into a readable table."""
        lines = [
            f"Total: {status['total']}",
            f"Completed: {len(status['completed'])}",
            f"Failed:    {len(status['failed'])}",
            f"Pending:   {len(status['pending'])}",
            "\nPer-artifact completion times (seconds):"
        ]
        sorted_times = sorted(status['completion_times'].items(), key=lambda item: item[1], reverse=True)
        for name, duration in sorted_times:
            lines.append(f"  - {name:<30}: {duration:.2f}s")
        if status['failed']:
            lines.append("\nFailed artifacts:")
            for name in status['failed']:
                lines.append(f"  - {name}")
        return "\n".join(lines)


import asyncio
import datetime
import random
from typing import Any, Callable, Dict, List, Optional, Type

class ArtifactUpdaterMultiWrapperAsync(ManagedResource):
    """
    Simplified wrapper that updates artifacts concurrently using an asyncio.Semaphore.

    Features:
    - Caps concurrency at max_workers via semaphore
    - Optionally prioritises tasks via a priority function or static method on artifact classes
    - Tracks per-artifact completion times
    - Configurable retry/backoff strategy
    - Optional metrics integration
    - Thread-safe within a single asyncio loop

    Usage:
        wrapper = ArtifactUpdaterMultiWrapper(
            wrapped_classes={
                'mydata': [DataArtifactA, DataArtifactB],
            },
            max_workers=4,
            retry_attempts=3,
            update_timeout_seconds=600,
            backoff_base=2,
            backoff_max=60,
            backoff_jitter=0.1,
            priority_fn=None,  # or custom
            metrics_client=None,
            debug=True,
            logger=None,
            artifact_class_kwargs={
                'fs': my_fs,
                'parquet_storage_path': 's3://bucket/data',
                'logger': my_logger,
                'debug': True,
            }
        )
        await wrapper.update_data('mydata', period='ytd', overwrite=True)
    """
    def __init__(
        self,
        wrapped_classes: Dict[str, List[Type]],
        *,
        max_workers: int = 3,
        retry_attempts: int = 3,
        update_timeout_seconds: int = 600,
        backoff_base: int = 2,
        backoff_max: Optional[int] = 60,
        backoff_jitter: float = 0.1,
        priority_fn: Optional[Callable[[Type], int]] = None,
        metrics_client: Any = None,
        artifact_class_kwargs: Optional[Dict[str, Any]] = None,
        **kwargs: Dict[str, Any]
    ) -> None:
        super().__init__(**kwargs)
        self.wrapped_classes = wrapped_classes
        self.max_workers = max_workers
        self.retry_attempts = retry_attempts
        self.update_timeout_seconds = update_timeout_seconds
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        self.backoff_jitter = backoff_jitter
        self.priority_fn = priority_fn
        self.metrics_client = metrics_client

        # Default artifact init kwargs
        today = datetime.datetime.today() + datetime.timedelta(days=1)
        default_kwargs = {
            'parquet_start_date': today.strftime('%Y-%m-%d'),
            'parquet_end_date': today.strftime('%Y-%m-%d'),
            'logger': self.logger,
            'debug': self.debug,
            'fs': self.fs,
            'verbose': self.verbose,
        }
        self.artifact_class_kwargs = artifact_class_kwargs or default_kwargs.copy()

        # State
        self.completion_times: Dict[str, float] = {}
        self.failed: List[str] = []
        self.original_classes: List[Type] = []
        self.logger.info("ArtifactUpdaterMultiWrapperAsync initialized")

    def get_artifact_classes(self, data_type: str) -> List[Type]:
        """
        Retrieve artifact classes by data type.
        """
        self.logger.info(f"Fetching artifact classes for '{data_type}'")
        if data_type not in self.wrapped_classes:
            raise ValueError(f"Unsupported data type: {data_type}")
        classes = self.wrapped_classes[data_type]
        self.logger.info(f"Found {len(classes)} artifact classes for '{data_type}'")
        return classes

    def estimate_priority(self, artifact_cls: Type) -> int:
        """
        Determine task priority for ordering. Lower values run first.
        """
        name = artifact_cls.__name__
        if self.priority_fn:
            try:
                pr = self.priority_fn(artifact_cls)
                self.logger.debug(f"priority_fn for {name}: {pr}")
                return pr
            except Exception as e:
                self.logger.warning(f"priority_fn error for {name}: {e}")
        try:
            fs = self.artifact_class_kwargs.get('fs')
            path = self.artifact_class_kwargs.get('parquet_storage_path')
            pr=1
            if hasattr(artifact_cls, 'get_size_estimate'):
                pr = artifact_cls.get_size_estimate(fs, path)
            self.logger.debug(f"Estimated priority for {name}: {pr}")
            return pr
        except Exception:
            return 1

    async def _bounded_update(self, artifact_cls: Type, sem: asyncio.Semaphore, **update_kwargs) -> None:
        """
        Wrap update_artifact in a semaphore slot to limit concurrency.
        """
        async with sem:
            name = artifact_cls.__name__
            start = asyncio.get_event_loop().time()
            self.logger.info(f"Starting update for {name}")
            try:
                for attempt in range(1, self.retry_attempts + 1):
                    try:
                        artifact = await asyncio.to_thread(
                            artifact_cls, **self.artifact_class_kwargs
                        )
                        await asyncio.wait_for(
                            asyncio.to_thread(
                                artifact.update_parquet, **update_kwargs
                            ),
                            timeout=self.update_timeout_seconds
                        )
                        duration = asyncio.get_event_loop().time() - start
                        self.completion_times[name] = duration
                        self.logger.info(f"✅ {name} updated in {duration:.2f}s (attempt {attempt})")
                        if self.metrics_client:
                            self.metrics_client.increment('task_succeeded')
                        return
                    except asyncio.TimeoutError:
                        self.logger.warning(f"Timeout on {name}, attempt {attempt}")
                    except Exception as e:
                        self.logger.error(f"Error on {name} attempt {attempt}: {e}")

                    delay = min(self.backoff_base ** (attempt - 1), self.backoff_max)
                    delay *= 1 + random.uniform(0, self.backoff_jitter)
                    self.logger.info(f"Sleeping {delay:.1f}s before retrying {name}")
                    await asyncio.sleep(delay)

            except asyncio.CancelledError:
                self.logger.warning(f"{name} update cancelled")
                raise

            # permanent failure
            self.logger.error(f"✖️  {name} permanently failed after {self.retry_attempts} attempts")
            if self.metrics_client:
                self.metrics_client.increment('task_failed')
            self.failed.append(name)

    async def update_data(self, data_type: str, **kwargs: Any) -> None:
        """
        Entry point to update all artifacts of a given type concurrently.
        """
        self.logger.info(f"Starting update_data for '{data_type}' with kwargs={kwargs}")

        # RESET STATE
        self.completion_times.clear()
        self.failed.clear()
        self.original_classes = self.get_artifact_classes(data_type)

        # NON-DESTRUCTIVE SORTING
        ordered = sorted(self.original_classes, key=self.estimate_priority)

        sem = asyncio.Semaphore(self.max_workers)
        tasks = [
            asyncio.create_task(self._bounded_update(cls, sem, **kwargs))
            for cls in ordered
        ]

        try:
            for coro in asyncio.as_completed(tasks):
                await coro
        except asyncio.CancelledError:
            self.logger.warning("update_data was cancelled—aborting remaining retries")
            for t in tasks:
                t.cancel()
            raise
        finally:
            total = len(self.original_classes)
            completed = len(self.completion_times)
            failed = len(self.failed)
            self.logger.info(f"All artifacts processed: total={total}, completed={completed}, failed={failed}")

    def get_update_status(self) -> Dict[str, Any]:
        """
        Returns summary status including completion times.
        """
        total = len(self.original_classes)
        completed = set(self.completion_times.keys())
        failed = set(self.failed)
        pending = {cls.__name__ for cls in self.original_classes} - completed - failed

        return {
            'total': total,
            'completed': list(completed),
            'failed':    list(failed),
            'pending':   list(pending),
            'completion_times': self.completion_times,
        }

    @staticmethod
    def format_status_table(status: Dict[str, Any]) -> str:
        """
        Formats the status dict into a readable table.
        """
        lines = [
            f"Total: {status['total']}",
            f"Completed: {len(status['completed'])}  {status['completed']}",
            f"Failed:    {len(status['failed'])}  {status['failed']}",
            f"Pending:   {len(status['pending'])}  {status['pending']}",
            "",
            "Per-artifact timings:"
        ]
        for name, dur in status['completion_times'].items():
            lines.append(f"  {name}: {dur:.2f}s")
        return "\n".join(lines)
