from core.route_engine import RouteEngine


class RouteAgent:
    def __init__(self) -> None:
        self.route_engine = RouteEngine()

    def recommend_routes(self, origin: str, destination: str) -> dict:
        return self.route_engine.get_all_route_options(origin, destination)