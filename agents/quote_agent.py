from models.schemas import ShipmentRequest
from core.pricing_engine import PricingEngine
from core.route_engine import RouteEngine


class QuoteAgent:
    def __init__(self) -> None:
        self.route_engine = RouteEngine()
        self.pricing_engine = PricingEngine()

    def generate_quote(
        self,
        shipment: ShipmentRequest,
        route_preference: str = "balanced",
    ):
        route_preference = route_preference.lower()

        if route_preference == "cheapest":
            selected_route = self.route_engine.find_cheapest_route(
                shipment.origin, shipment.destination
            )
        elif route_preference == "fastest":
            selected_route = self.route_engine.find_fastest_route(
                shipment.origin, shipment.destination
            )
        elif route_preference == "lowest_risk":
            selected_route = self.route_engine.find_lowest_risk_route(
                shipment.origin, shipment.destination
            )
        else:
            selected_route = self.route_engine.find_balanced_route(
                shipment.origin, shipment.destination
            )

        return self.pricing_engine.calculate_quote(shipment, selected_route)