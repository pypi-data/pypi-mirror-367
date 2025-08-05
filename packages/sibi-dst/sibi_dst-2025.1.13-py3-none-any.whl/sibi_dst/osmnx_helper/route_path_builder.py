import numpy as np
import pandas as pd
import networkx as nx
import osmnx as ox
from typing import List

class RoutePathBuilder:
    """
    Builds shortest paths for consecutive GPS points (origins & destinations) within each associate's track.
    """

    def __init__(
        self,
        graph: nx.MultiDiGraph,
        lat_col: str = "latitude",
        lon_col: str = "longitude",
        grouping_col: str = "associate_id",
        sort_key=None  # Default sort key for DataFrame
    ):
        """
        :param graph: The OSMnx MultiDiGraph.
        :param lat_col: Column name for latitude.
        :param lon_col: Column name for longitude.
        :param associate_col: Column name for associate/grouping key.
        """
        if sort_key is None:
            sort_key = ["associate_id", "date_time"]
        self.graph = graph
        self.lat_col = lat_col
        self.lon_col = lon_col
        self.grouping_col = grouping_col
        self.sort_key = sort_key
        if self.sort_key is None:
            self.sort_key = [self.grouping_col, "date_time"]

    @staticmethod
    def _get_shortest_path(u: int, v: int, graph: nx.MultiDiGraph) -> List[int]:
        """Return the node sequence for the shortest path from u to v, or [] if none."""
        try:
            return nx.shortest_path(graph, u, v, weight="length")
        except nx.NetworkXNoPath:
            return []

    @staticmethod
    def _path_length_from_nodes(node_list: List[int], graph: nx.MultiDiGraph) -> float:
        """Sum up the 'length' attribute along consecutive node pairs."""
        if len(node_list) < 2:
            return np.nan
        total = 0.0
        for u, v in zip(node_list[:-1], node_list[1:]):
            edge_data = graph.get_edge_data(u, v)
            lengths = [edata.get("length", 0) for edata in edge_data.values()]
            total += min(lengths) if lengths else 0
        return total

    def build_routes(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generate destination coordinates, snap to graph nodes, and compute shortest paths.

        :param df: Input DataFrame containing grouping_col, latitude, and longitude columns.
        :return: DataFrame with added columns:
            ['dest_lat', 'dest_lon', 'origin_node', 'dest_node', 'path_nodes', 'path_coords', 'distance_m']
        """
        # 1) Build destination coordinates by shifting per grouping column
        df = df.copy()
        df["dest_lat"] = df.groupby(self.grouping_col)[self.lat_col].shift(-1)
        df["dest_lon"] = df.groupby(self.grouping_col)[self.lon_col].shift(-1)

        # Drop tail rows without next point
        df = df.dropna(subset=["dest_lat", "dest_lon"]).reset_index(drop=True)

        # 2) Snap origin & destination points to graph nodes
        df["origin_node"] = ox.nearest_nodes(
            self.graph, X=df[self.lon_col].values, Y=df[self.lat_col].values
        )
        df["dest_node"] = ox.nearest_nodes(
            self.graph, X=df["dest_lon"].values, Y=df["dest_lat"].values
        )

        # 3) Compute paths, coordinates, and distances
        df["path_nodes"] = [
            self._get_shortest_path(u, v, self.graph)
            for u, v in zip(df["origin_node"], df["dest_node"])
        ]

        df["path_coords"] = df["path_nodes"].apply(
            lambda nl: [(self.graph.nodes[n]["y"], self.graph.nodes[n]["x"]) for n in nl]
        )

        df["distance_m"] = df["path_nodes"].apply(
            lambda nl: self._path_length_from_nodes(nl, self.graph)
        )
        # Ensure NaN distances become 0
        df["distance_m"] = df["distance_m"].fillna(0)
        # Remove any legs with no path
        df = df[df["path_nodes"].str.len() > 0].reset_index(drop=True)

        return df.sort_values(self.sort_key).reset_index(drop=True)