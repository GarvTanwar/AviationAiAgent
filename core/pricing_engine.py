from models.schemas import ShipmentRequest, RouteOption, QuoteBreakdown, QuoteResponse
from services.data_loader import get_region_by_airport_code, get_pricing_rule


class PricingEngine:
    def calculate_quote(
        self,
        shipment: ShipmentRequest,
        selected_route: RouteOption,
    ) -> QuoteResponse:
        origin_region = get_region_by_airport_code(shipment.origin)
        destination_region = get_region_by_airport_code(shipment.destination)

        if not origin_region or not destination_region:
            raise ValueError("Invalid origin or destination airport code.")

        pricing_rule = get_pricing_rule(origin_region, destination_region)
        if not pricing_rule:
            raise ValueError(
                f"No pricing rule found for {origin_region} -> {destination_region}."
            )

        base_rate_per_kg = float(pricing_rule["base_rate_per_kg"])
        fuel_surcharge_percent = float(pricing_rule["fuel_surcharge_percent"])
        customs_fee = float(pricing_rule["customs_fee"])
        handling_fee = float(pricing_rule["handling_fee"])
        urgency_multiplier = float(pricing_rule["urgency_multiplier"])

        base_freight = shipment.weight_kg * base_rate_per_kg
        fuel_surcharge = base_freight * (fuel_surcharge_percent / 100)

        urgency_fee = 0.0
        subtotal_before_urgency = (
            base_freight + fuel_surcharge + customs_fee + handling_fee
        )

        if shipment.urgency.lower() == "urgent":
            urgency_fee = subtotal_before_urgency * (urgency_multiplier - 1)

        total_price = subtotal_before_urgency + urgency_fee

        breakdown = QuoteBreakdown(
            base_freight=round(base_freight, 2),
            fuel_surcharge=round(fuel_surcharge, 2),
            customs_fee=round(customs_fee, 2),
            handling_fee=round(handling_fee, 2),
            urgency_fee=round(urgency_fee, 2),
            total_price=round(total_price, 2),
        )

        pricing_rule_applied = f"{origin_region} -> {destination_region}"

        return QuoteResponse(
            shipment=shipment,
            selected_route=selected_route,
            pricing_rule_applied=pricing_rule_applied,
            breakdown=breakdown,
            notes="Quote generated using region-based pricing and selected route.",
        )