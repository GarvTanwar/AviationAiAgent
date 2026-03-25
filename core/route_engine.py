import networkx as nx
from typing import List

from models.schemas import RouteOption
from services.data_loader import load_routes


class RouteEngine:
    def __init__(self) -> None:
        self.routes_df = load_routes()
        self.graph = nx.DiGraph()
        self._build_graph()

    def _build_graph(self) -> None:
        for _, row in self.routes_df.iterrows():
            origin = row["origin"]
            destination = row["destination"]

            edge_data = {
                "distance_km": float(row["distance_km"]),
                "avg_time_hours": float(row["avg_time_hours"]),
                "base_cost_per_kg": float(row["base_cost_per_kg"]),
                "route_type": row["route_type"],
                "risk_score": float(row["risk_score"]),
            }

            self.graph.add_edge(origin, destination, **edge_data)
            self.graph.add_edge(destination, origin, **edge_data)

    def _get_path_metrics(self, path: List[str]) -> RouteOption:
        total_distance = 0.0
        total_time = 0.0
        total_cost_score = 0.0
        total_risk_score = 0.0
        route_types = []

        for i in range(len(path) - 1):
            edge = self.graph[path[i]][path[i + 1]]
            total_distance += edge["distance_km"]
            total_time += edge["avg_time_hours"]
            total_cost_score += edge["base_cost_per_kg"]
            total_risk_score += edge["risk_score"]
            route_types.append(edge["route_type"])

        if "long-haul" in route_types:
            overall_route_type = "long-haul"
        elif "hub" in route_types:
            overall_route_type = "hub"
        elif "transatlantic" in route_types:
            overall_route_type = "transatlantic"
        else:
            overall_route_type = "regional"

        return RouteOption(
            path=path,
            total_distance_km=round(total_distance, 2),
            total_time_hours=round(total_time, 2),
            total_cost_score=round(total_cost_score, 2),
            total_risk_score=round(total_risk_score, 2),
            route_type=overall_route_type,
        )

    def find_cheapest_route(self, origin: str, destination: str) -> RouteOption:
        path = nx.shortest_path(
            self.graph,
            source=origin.upper(),
            target=destination.upper(),
            weight="base_cost_per_kg",
        )
        return self._get_path_metrics(path)

    def find_fastest_route(self, origin: str, destination: str) -> RouteOption:
        path = nx.shortest_path(
            self.graph,
            source=origin.upper(),
            target=destination.upper(),
            weight="avg_time_hours",
        )
        return self._get_path_metrics(path)

    def find_lowest_risk_route(self, origin: str, destination: str) -> RouteOption:
        path = nx.shortest_path(
            self.graph,
            source=origin.upper(),
            target=destination.upper(),
            weight="risk_score",
        )
        return self._get_path_metrics(path)

    def find_balanced_route(self, origin: str, destination: str) -> RouteOption:
        balanced_graph = self.graph.copy()

        for u, v, data in balanced_graph.edges(data=True):
            combined_weight = (
                data["base_cost_per_kg"] * 0.4
                + data["avg_time_hours"] * 0.3
                + data["risk_score"] * 0.3
            )
            balanced_graph[u][v]["balanced_weight"] = combined_weight

        path = nx.shortest_path(
            balanced_graph,
            source=origin.upper(),
            target=destination.upper(),
            weight="balanced_weight",
        )
        return self._get_path_metrics(path)

    def get_all_route_options(self, origin: str, destination: str) -> dict:
        return {
            "cheapest": self.find_cheapest_route(origin, destination),
            "fastest": self.find_fastest_route(origin, destination),
            "lowest_risk": self.find_lowest_risk_route(origin, destination),
            "balanced": self.find_balanced_route(origin, destination),
        }