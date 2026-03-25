from models.schemas import ShipmentRequest
from core.utils import safe_upper


def build_shipment_request(
    origin: str,
    destination: str,
    weight_kg: float,
    urgency: str,
    cargo_type: str,
) -> ShipmentRequest:
    return ShipmentRequest(
        origin=safe_upper(origin),
        destination=safe_upper(destination),
        weight_kg=float(weight_kg),
        urgency=urgency.strip().lower(),
        cargo_type=cargo_type.strip().lower(),
    )


def build_shipment_request_from_ai(ai_data: dict) -> ShipmentRequest:
    return ShipmentRequest(
        origin=safe_upper(ai_data.get("origin", "")),
        destination=safe_upper(ai_data.get("destination", "")),
        weight_kg=float(ai_data.get("weight_kg", 1)),
        urgency=str(ai_data.get("urgency", "normal")).strip().lower(),
        cargo_type=str(ai_data.get("cargo_type", "general")).strip().lower(),
    )