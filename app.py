import streamlit as st

from agents.route_agent import RouteAgent
from agents.quote_agent import QuoteAgent
from core.parser import build_shipment_request
from core.utils import format_currency, format_route_path
from services.llm_service import LLMService
from services.file_service import save_uploaded_file, ensure_knowledge_base_dir
from rag.retriever import RAGRetriever
from rag.ingest import ingest_knowledge_base


st.set_page_config(
    page_title="Aviation AI Agent",
    page_icon="✈️",
    layout="wide",
)

st.title("✈️ Aviation AI Agent")
st.markdown("Smart Pricing / Quote Generator + Route Optimization + Knowledge RAG")

route_agent = RouteAgent()
quote_agent = QuoteAgent()
llm_service = LLMService()


def get_rag_retriever() -> RAGRetriever:
    return RAGRetriever()


def initialize_session_state() -> None:
    defaults = {
        "origin": "DEL",
        "destination": "MEL",
        "weight_kg": 200.0,
        "urgency": "normal",
        "cargo_type": "general",
        "route_preference": "balanced",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


initialize_session_state()
ensure_knowledge_base_dir()

tab1, tab2 = st.tabs(["Shipment Agent", "Knowledge Assistant"])

with tab1:
    st.subheader("Ask in Natural Language")
    ai_request = st.text_area(
        "Example: Ship 200kg from Delhi to Melbourne urgently using the cheapest route",
        height=100,
        key="shipment_ai_request",
    )

    if st.button("Parse with AI"):
        try:
            ai_result = llm_service.extract_shipment_details(ai_request)

            if "error" in ai_result:
                st.error(f"AI parsing failed: {ai_result.get('raw', 'Unknown error')}")
            else:
                st.session_state.origin = str(
                    ai_result.get("origin", st.session_state.origin)
                ).upper()
                st.session_state.destination = str(
                    ai_result.get("destination", st.session_state.destination)
                ).upper()
                st.session_state.weight_kg = float(
                    ai_result.get("weight_kg", st.session_state.weight_kg)
                )

                urgency_value = str(
                    ai_result.get("urgency", st.session_state.urgency)
                ).lower()
                st.session_state.urgency = (
                    urgency_value if urgency_value in ["normal", "urgent"] else "normal"
                )

                cargo_value = str(
                    ai_result.get("cargo_type", st.session_state.cargo_type)
                ).lower()
                st.session_state.cargo_type = (
                    cargo_value
                    if cargo_value in ["general", "fragile", "perishable", "medical"]
                    else "general"
                )

                route_value = str(
                    ai_result.get("route_preference", st.session_state.route_preference)
                ).lower()
                st.session_state.route_preference = (
                    route_value
                    if route_value in ["balanced", "cheapest", "fastest", "lowest_risk"]
                    else "balanced"
                )

                st.success("AI parsed shipment details successfully.")
                st.json(ai_result)
                st.rerun()

        except Exception as e:
            st.error(f"Error using AI parser: {e}")

    with st.sidebar:
        st.header("Shipment Details")

        st.text_input("Origin Airport Code", key="origin")
        st.text_input("Destination Airport Code", key="destination")
        st.number_input("Weight (kg)", min_value=1.0, step=1.0, key="weight_kg")
        st.selectbox("Urgency", options=["normal", "urgent"], key="urgency")
        st.selectbox(
            "Cargo Type",
            options=["general", "fragile", "perishable", "medical"],
            key="cargo_type",
        )
        st.selectbox(
            "Quote Route Preference",
            options=["balanced", "cheapest", "fastest", "lowest_risk"],
            key="route_preference",
        )

        get_routes_btn = st.button("Show Route Options")
        get_quote_btn = st.button("Generate Quote")

    def display_route_card(title: str, route) -> None:
        st.subheader(title)
        st.write(f"**Path:** {format_route_path(route.path)}")
        st.write(f"**Distance:** {route.total_distance_km} km")
        st.write(f"**Time:** {route.total_time_hours} hours")
        st.write(f"**Cost Score:** {route.total_cost_score}")
        st.write(f"**Risk Score:** {route.total_risk_score}")
        st.write(f"**Route Type:** {route.route_type}")

    if get_routes_btn:
        try:
            routes = route_agent.recommend_routes(
                st.session_state.origin,
                st.session_state.destination,
            )

            st.success("Route options generated successfully.")

            col1, col2 = st.columns(2)

            with col1:
                display_route_card("Cheapest Route", routes["cheapest"])
                display_route_card("Lowest Risk Route", routes["lowest_risk"])

            with col2:
                display_route_card("Fastest Route", routes["fastest"])
                display_route_card("Balanced Route", routes["balanced"])

        except Exception as e:
            st.error(f"Error generating route options: {e}")

    if get_quote_btn:
        try:
            shipment = build_shipment_request(
                origin=st.session_state.origin,
                destination=st.session_state.destination,
                weight_kg=st.session_state.weight_kg,
                urgency=st.session_state.urgency,
                cargo_type=st.session_state.cargo_type,
            )

            quote = quote_agent.generate_quote(
                shipment=shipment,
                route_preference=st.session_state.route_preference,
            )

            st.success("Quote generated successfully.")

            st.header("Quote Summary")
            st.write(f"**Origin:** {quote.shipment.origin}")
            st.write(f"**Destination:** {quote.shipment.destination}")
            st.write(f"**Weight:** {quote.shipment.weight_kg} kg")
            st.write(f"**Urgency:** {quote.shipment.urgency}")
            st.write(f"**Cargo Type:** {quote.shipment.cargo_type}")

            st.header("Selected Route")
            st.write(f"**Path:** {format_route_path(quote.selected_route.path)}")
            st.write(f"**Distance:** {quote.selected_route.total_distance_km} km")
            st.write(f"**Time:** {quote.selected_route.total_time_hours} hours")
            st.write(f"**Risk Score:** {quote.selected_route.total_risk_score}")
            st.write(f"**Route Type:** {quote.selected_route.route_type}")

            st.header("Pricing Breakdown")
            st.write(f"**Pricing Rule Applied:** {quote.pricing_rule_applied}")
            st.write(f"**Base Freight:** {format_currency(quote.breakdown.base_freight)}")
            st.write(f"**Fuel Surcharge:** {format_currency(quote.breakdown.fuel_surcharge)}")
            st.write(f"**Customs Fee:** {format_currency(quote.breakdown.customs_fee)}")
            st.write(f"**Handling Fee:** {format_currency(quote.breakdown.handling_fee)}")
            st.write(f"**Urgency Fee:** {format_currency(quote.breakdown.urgency_fee)}")
            st.subheader(f"Total Price: {format_currency(quote.breakdown.total_price)}")

            if quote.notes:
                st.info(quote.notes)

            st.header("AI Explanation")
            explanation = llm_service.explain_quote_and_route(
                quote,
                st.session_state.route_preference,
            )
            st.write(explanation)

        except Exception as e:
            st.error(f"Error generating quote: {e}")

with tab2:
    st.subheader("Upload Knowledge Files")
    uploaded_files = st.file_uploader(
        "Upload .txt or .pdf files",
        type=["txt", "pdf"],
        accept_multiple_files=True,
    )

    col_upload_1, col_upload_2 = st.columns(2)

    with col_upload_1:
        if st.button("Save Uploaded Files"):
            try:
                if not uploaded_files:
                    st.warning("Please upload at least one file.")
                else:
                    saved_files = []
                    for uploaded_file in uploaded_files:
                        saved_path = save_uploaded_file(uploaded_file)
                        saved_files.append(saved_path.name)

                    st.success(f"Saved files: {', '.join(saved_files)}")
            except Exception as e:
                st.error(f"File upload error: {e}")

    with col_upload_2:
        if st.button("Rebuild Knowledge Base"):
            try:
                chunk_count = ingest_knowledge_base()
                st.success(f"Knowledge base rebuilt successfully with {chunk_count} chunks.")
            except Exception as e:
                st.error(f"Knowledge base rebuild error: {e}")

    st.divider()

    st.subheader("Ask the Knowledge Base")
    kb_question = st.text_area(
        "Example: What affects urgency pricing?",
        height=100,
        key="kb_question",
    )

    if st.button("Ask Knowledge Base"):
        try:
            rag_retriever = get_rag_retriever()
            retrieved_chunks = rag_retriever.retrieve(kb_question, top_k=3)

            if not retrieved_chunks:
                st.warning("No relevant knowledge base chunks found. Upload files and rebuild first.")
            else:
                answer = llm_service.answer_with_context(kb_question, retrieved_chunks)

                st.success("Answer generated from knowledge base.")

                st.markdown("### Answer")
                st.write(answer)

                st.markdown("### Retrieved Context")
                for i, chunk in enumerate(retrieved_chunks, start=1):
                    with st.expander(f"Chunk {i} - {chunk.get('source', 'unknown')}"):
                        st.write(chunk.get("text", ""))
                        st.caption(f"Similarity score: {chunk.get('score', 0):.4f}")

        except Exception as e:
            st.error(f"Knowledge base error: {e}")