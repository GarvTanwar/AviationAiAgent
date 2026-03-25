import os
import json
import re
import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")


class LLMService:
    def generate(self, prompt: str) -> str:
        payload = {
            "model": MODEL,
            "prompt": prompt,
            "stream": False,
        }

        response = requests.post(OLLAMA_URL, json=payload, timeout=120)

        if response.status_code != 200:
            raise Exception(f"Ollama error: {response.text}")

        data = response.json()
        return data.get("response", "").strip()

    def _extract_json_from_text(self, text: str) -> dict:
        cleaned_text = text.strip()
        cleaned_text = cleaned_text.replace("```json", "").replace("```", "").strip()

        match = re.search(r"\{.*\}", cleaned_text, re.DOTALL)
        if not match:
            return {"error": "No JSON object found in AI response", "raw": text}

        json_text = match.group(0)

        try:
            return json.loads(json_text)
        except json.JSONDecodeError:
            return {"error": "Failed to decode JSON", "raw": text}

    def extract_shipment_details(self, user_input: str) -> dict:
        prompt = f"""
You are an AI assistant for an aviation logistics system.

Extract structured shipment details from the user input.

Return ONLY one raw JSON object.
Do not add explanations.
Do not add markdown.
Do not add code fences.

Allowed values:
- urgency: normal or urgent
- cargo_type: general, fragile, perishable, medical
- route_preference: cheapest, fastest, lowest_risk, balanced

You MUST return airport IATA codes only (3-letter codes).

Convert cities to codes:
- Delhi -> DEL
- Mumbai -> BOM
- Bangalore -> BLR
- Dubai -> DXB
- Singapore -> SIN
- Bangkok -> BKK
- Hong Kong -> HKG
- Sydney -> SYD
- Melbourne -> MEL
- London -> LHR
- Frankfurt -> FRA
- Paris -> CDG
- Amsterdam -> AMS
- New York -> JFK
- Los Angeles -> LAX
- Tokyo -> NRT
- Seoul -> ICN

If unsure, guess the most likely major airport.
DO NOT return city names.
ONLY return airport codes.

Return this format exactly:
{{
  "origin": "DEL",
  "destination": "MEL",
  "weight_kg": 200,
  "urgency": "urgent",
  "cargo_type": "general",
  "route_preference": "cheapest"
}}

User input:
{user_input}
"""
        response = self.generate(prompt)
        return self._extract_json_from_text(response)

    def answer_with_context(self, question: str, context_chunks: list[dict]) -> str:
        context_text = "\n\n".join(
            [
                f"Source: {chunk.get('source', 'unknown')}\n{chunk.get('text', '')}"
                for chunk in context_chunks
            ]
        )

        prompt = f"""
You are an aviation logistics knowledge assistant.

Answer the user's question using only the provided context.
If the answer is not in the context, say that the current knowledge base does not contain enough information.

Context:
{context_text}

User question:
{question}
"""
        return self.generate(prompt)

    def explain_quote_and_route(self, quote, route_preference: str) -> str:
        prompt = f"""
You are an aviation logistics AI assistant.

Explain the quote and selected route in a clear, professional, concise way.

Shipment details:
- Origin: {quote.shipment.origin}
- Destination: {quote.shipment.destination}
- Weight: {quote.shipment.weight_kg} kg
- Urgency: {quote.shipment.urgency}
- Cargo type: {quote.shipment.cargo_type}
- Route preference requested: {route_preference}

Selected route:
- Path: {' -> '.join(quote.selected_route.path)}
- Distance: {quote.selected_route.total_distance_km} km
- Time: {quote.selected_route.total_time_hours} hours
- Risk score: {quote.selected_route.total_risk_score}
- Route type: {quote.selected_route.route_type}

Pricing:
- Pricing rule applied: {quote.pricing_rule_applied}
- Base freight: {quote.breakdown.base_freight}
- Fuel surcharge: {quote.breakdown.fuel_surcharge}
- Customs fee: {quote.breakdown.customs_fee}
- Handling fee: {quote.breakdown.handling_fee}
- Urgency fee: {quote.breakdown.urgency_fee}
- Total price: {quote.breakdown.total_price}

Write:
1. Why this route makes sense
2. Main pricing drivers
3. A short tradeoff note if relevant

Keep it under 140 words.
"""
        return self.generate(prompt)