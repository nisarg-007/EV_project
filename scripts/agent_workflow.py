import sys
import os
import re

try:
    from typing import TypedDict
    from langgraph.graph import StateGraph, START, END
    from langchain_ollama import ChatOllama
    from langchain_core.prompts import PromptTemplate
except ImportError as e:
    print(f"Required module missing: {e}. Please install langgraph, langchain-ollama, etc.")
    sys.exit(1)

try:
    from scripts.analytics_tools import (
        get_ev_counts_by_county,
        get_ev_counts_by_zipcode,
        get_top_makes_and_models,
        get_bev_vs_phev_breakdown,
        get_cafv_eligibility_summary,
        get_ev_range_statistics,
        get_newest_registrations,
        get_utility_provider_summary,
        get_county_growth_comparison
    )
except ImportError:
    try:
        from analytics_tools import (
            get_ev_counts_by_county,
            get_ev_counts_by_zipcode,
            get_top_makes_and_models,
            get_bev_vs_phev_breakdown,
            get_cafv_eligibility_summary,
            get_ev_range_statistics,
            get_newest_registrations,
            get_utility_provider_summary,
            get_county_growth_comparison
        )
    except ImportError:
        pass

try:
    from scripts.rag_query import query_policy_docs
except ImportError:
    try:
        from rag_query import query_policy_docs
    except ImportError:
        pass

try:
    from scripts.agent_config import (
        OLLAMA_MODEL,
        ROUTER_PROMPT,
        DATA_SYNTHESIS_PROMPT,
        POLICY_SYNTHESIS_PROMPT,
        COMBINED_SYNTHESIS_PROMPT
    )
except ImportError:
    try:
        from agent_config import (
            OLLAMA_MODEL,
            ROUTER_PROMPT,
            DATA_SYNTHESIS_PROMPT,
            POLICY_SYNTHESIS_PROMPT,
            COMBINED_SYNTHESIS_PROMPT
        )
    except ImportError:
        pass

class GraphState(TypedDict):
    question: str
    route: str
    data_context: str
    policy_context: str
    final_answer: str

def get_llm():
    try:
        model_name = OLLAMA_MODEL
    except NameError:
        model_name = "llama3.2"
    return ChatOllama(model=model_name)

def router_node(state: GraphState) -> GraphState:
    question = state.get("question", "")
    llm = get_llm()
    prompt = PromptTemplate.from_template(ROUTER_PROMPT)
    chain = prompt | llm
    
    try:
        route_result = chain.invoke({"question": question}).content.strip().lower()
    except Exception as e:
        print(f"Error in router: {e}")
        route_result = "both"

    if "both" in route_result:
        route = "both"
    elif "data" in route_result:
        route = "data"
    elif "policy" in route_result:
        route = "policy"
    else:
        route = "both"
        
    return {"route": route}

def data_tool_node(state: GraphState) -> GraphState:
    question = state.get("question", "")
    q_lower = question.lower()
    data_context = ""
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parquet_path = os.path.join(BASE_DIR, 'data', 'processed', 'Electric_Vehicle_Population_Data.parquet')
    
    try:
        if "county" in q_lower or "counties" in q_lower:
            df = get_ev_counts_by_county(parquet_path=parquet_path)
        elif "zip" in q_lower or "zipcode" in q_lower:
            df = get_ev_counts_by_zipcode(parquet_path=parquet_path)
        elif "make" in q_lower or "model" in q_lower:
            df = get_top_makes_and_models(parquet_path=parquet_path)
        elif "range" in q_lower:
            df = get_ev_range_statistics(parquet_path=parquet_path)
        elif "new" in q_lower or "recent" in q_lower:
            df = get_newest_registrations(parquet_path=parquet_path)
        elif "cafv" in q_lower or "eligibility" in q_lower:
            df = get_cafv_eligibility_summary(parquet_path=parquet_path)
        elif "utility" in q_lower or "provider" in q_lower:
            df = get_utility_provider_summary(parquet_path=parquet_path)
        else:
            df = get_ev_counts_by_county(parquet_path=parquet_path)
            
        data_context = df.head(10).to_string()
        print(f"\n--- DEBUG: Raw Data Tool Output ---\n{data_context}\n-----------------------------------\n")
    except Exception as e:
        data_context = f"Error retrieving data: {e}"
        print(f"\n--- DEBUG: Error in Data Tool ---\n{data_context}\n---------------------------------\n")
        
    return {"data_context": data_context}

def policy_tool_node(state: GraphState) -> GraphState:
    question = state.get("question", "")
    try:
        docs = query_policy_docs(question)
        if not docs:
            policy_context = "No relevant policy documents found."
        else:
            policy_context = "\n\n".join([f"[Source: {doc.get('source', 'unknown')}]\n{doc.get('text', '')}" for doc in docs])
        print(f"\n--- DEBUG: Raw Policy Tool Output ---\n{policy_context[:500]}...\n-------------------------------------\n")
    except Exception as e:
        policy_context = f"Error retrieving policy: {e}"
        print(f"\n--- DEBUG: Error in Policy Tool ---\n{policy_context}\n---------------------------------\n")
    return {"policy_context": policy_context}

def synthesizer_node(state: GraphState) -> GraphState:
    question = state.get("question", "")
    route = state.get("route", "both")
    data_context = state.get("data_context", "")
    policy_context = state.get("policy_context", "")
    llm = get_llm()
    
    if route == "policy" and "No relevant policy documents" in policy_context:
        return {"final_answer": "Policy data is currently unavailable because the RAG system is not configured."}
        
    try:
        if route == "data":
            prompt = PromptTemplate.from_template(DATA_SYNTHESIS_PROMPT)
            chain = prompt | llm
            final_answer = chain.invoke({"question": question, "data": data_context}).content
        elif route == "policy":
            prompt = PromptTemplate.from_template(POLICY_SYNTHESIS_PROMPT)
            chain = prompt | llm
            final_answer = chain.invoke({"question": question, "policy": policy_context}).content
        else:
            if "No relevant policy documents" in policy_context:
                policy_context = "Policy data is currently unavailable because the RAG system is not configured."
            prompt = PromptTemplate.from_template(COMBINED_SYNTHESIS_PROMPT)
            chain = prompt | llm
            final_answer = chain.invoke({
                "question": question, 
                "data": data_context, 
                "policy": policy_context
            }).content
    except Exception as e:
        final_answer = f"Error in synthesis: {e}"
        
    return {"final_answer": final_answer}

def build_graph():
    workflow = StateGraph(GraphState)

    workflow.add_node("router", router_node)
    workflow.add_node("data_tool", data_tool_node)
    workflow.add_node("policy_tool", policy_tool_node)
    workflow.add_node("synthesizer", synthesizer_node)

    workflow.add_edge(START, "router")

    workflow.add_conditional_edges(
        "router",
        lambda state: state.get("route", "both"),
        {
            "data": "data_tool",
            "policy": "policy_tool",
            "both": "data_tool"
        }
    )

    def data_edge(state: GraphState) -> str:
        if state.get("route") == "both":
            return "policy_tool"
        return "synthesizer"

    workflow.add_conditional_edges(
        "data_tool",
        data_edge,
        {
            "policy_tool": "policy_tool",
            "synthesizer": "synthesizer"
        }
    )

    workflow.add_edge("policy_tool", "synthesizer")
    workflow.add_edge("synthesizer", END)
    
    return workflow.compile()

_GREETING_PATTERNS = re.compile(
    r'^\s*(hi|hello|hey|howdy|sup|what\'s up|greetings|good\s+(morning|afternoon|evening)|'
    r'how are you|who are you|what (can|do) you do|help me|what is this|capabilities)\b',
    re.IGNORECASE
)

_FORECAST_PATTERNS = re.compile(
    r'\b(forecast|predict|projection|future|2025|2026|2027|2028|2029|2030|next year|'
    r'next \d+ years?|growth (in|for)|how many.*will|expected|estimate)\b',
    re.IGNORECASE
)


def _greeting_response() -> str:
    return (
        "Hi! I'm your **EV Intelligence Assistant**.\n\n"
        "I can help you explore **276,000+ EV registrations** across Washington State. Ask me about:\n"
        "- 🗺️ County & city EV hotspots\n"
        "- 🚗 Top makes & models (Tesla, Chevrolet, Nissan…)\n"
        "- 📈 Adoption trends & growth history\n"
        "- 🔮 Forecasts — *e.g. 'Forecast King County EVs to 2030'*\n"
        "- 🔋 BEV vs PHEV breakdown\n"
        "- ⚡ Charging infrastructure hotspots\n"
        "- 💰 WA state incentives & CAFV eligibility\n\n"
        "What would you like to know?"
    )


def _forecast_response(question: str) -> str:
    import re as _re
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    parquet_path = os.path.join(BASE_DIR, 'data', 'processed', 'Electric_Vehicle_Population_Data.parquet')

    try:
        sys.path.insert(0, BASE_DIR)
        from src.forecasting.forecaster import EVForecaster, load_registration_timeseries
        import pandas as pd

        ts_all = load_registration_timeseries(parquet_path)

        # Extract county name from question
        county_match = _re.search(
            r'\b(king|pierce|snohomish|clark|spokane|thurston|kitsap|whatcom|benton|yakima)\b',
            question, _re.IGNORECASE
        )
        counties = [county_match.group(0).title()] if county_match else ["King", "Pierce", "Snohomish"]

        # Extract horizon
        year_match = _re.search(r'\b(202[5-9]|2030)\b', question)
        horizon_match = _re.search(r'\b(\d+)\s+years?\b', question, _re.IGNORECASE)
        if year_match:
            periods = int(year_match.group(0)) - 2023
        elif horizon_match:
            periods = int(horizon_match.group(1))
        else:
            periods = 6

        lines = [f"**EV Forecast ({2023 + periods} horizon)**\n"]
        for county in counties:
            county_ts = ts_all[ts_all["county"] == county].sort_values("date")
            if len(county_ts) < 2:
                lines.append(f"- **{county}**: insufficient data for forecasting")
                continue
            fc = EVForecaster().fit(county_ts, county)
            pred = fc.predict(periods=periods)
            last_actual = int(county_ts["registrations"].iloc[-1])
            last_forecast = max(0, int(pred["yhat"].iloc[-1]))
            growth = (last_forecast - last_actual) / max(last_actual, 1) * 100
            lines.append(
                f"- **{county} County**: {last_actual:,} EVs (2023) → **{last_forecast:,} EVs ({2023 + periods})** "
                f"(+{growth:.0f}% growth, model: {fc._model_name.upper()})"
            )

        lines.append(f"\n_Forecasts use {'ARIMA' if periods < 24 else 'Prophet'} models fit on annual registration counts. "
                     f"Visit the 📈 Forecasting page for interactive charts._")
        return "\n".join(lines)

    except Exception as e:
        return (
            f"I wasn't able to run the forecast model ({e}). "
            f"Please visit the **📈 Forecasting** page for interactive county-level predictions."
        )


def run_agent(question: str) -> str:
    # Handle greetings and general capability questions without hitting the data pipeline
    if _GREETING_PATTERNS.search(question):
        return _greeting_response()

    # Handle forecast/prediction questions with the forecaster
    if _FORECAST_PATTERNS.search(question):
        return _forecast_response(question)

    try:
        graph = build_graph()
        result = graph.invoke({"question": question})
        return result.get("final_answer", "No answer generated.")
    except Exception as e:
        return f"Agent failed to run: {e}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
    else:
        q = "How many EVs are in King County?"
        
    print(f"Question: {q}\n")
    answer = run_agent(q)
    print(f"Answer:\n{answer}")
