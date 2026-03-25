from pydantic import BaseModel, Field
from typing import List, Optional


class ShipmentRequest(BaseModel):
    origin: str = Field(..., description="Origin airport code, e.g. DEL")
    destination: str = Field(..., description="Destination airport code, e.g. MEL")
    weight_kg: float = Field(..., gt=0, description="Shipment weight in kilograms")
    urgency: str = Field(default="normal", description="normal or urgent")
    cargo_type: str = Field(default="general", description="Type of cargo")


class RouteOption(BaseModel):
    path: List[str]
    total_distance_km: float
    total_time_hours: float
    total_cost_score: float
    total_risk_score: float
    route_type: str


class QuoteBreakdown(BaseModel):
    base_freight: float
    fuel_surcharge: float
    customs_fee: float
    handling_fee: float
    urgency_fee: float
    total_price: float


class QuoteResponse(BaseModel):
    shipment: ShipmentRequest
    selected_route: RouteOption
    pricing_rule_applied: str
    breakdown: QuoteBreakdown
    notes: Optional[str] = None