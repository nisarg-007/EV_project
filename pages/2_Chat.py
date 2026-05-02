import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.components.sidebar import render_sidebar

import re
import streamlit as st
import streamlit.components.v1 as components
import time
import contextlib

# ── Backend setup ──────────────────────────────────────────────────────────────
AGENT_AVAILABLE = False
RAG_AVAILABLE   = False
LLM_AVAILABLE   = False
CHART_AVAILABLE = False

# Last RAG sources are stored here so the UI can show the source drawer
_last_sources: list[dict] = []
# Last chart HTML so the UI can render it inline
_last_chart_html: str = ""

# Try to load chart tool
try:
    from src.tools.chart_tool import generate_chart_tool
    CHART_AVAILABLE = True
except Exception:
    pass

try:
    from scripts.agent_workflow import run_agent
    AGENT_AVAILABLE = True
except ImportError:
    pass

if not AGENT_AVAILABLE:
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
        from langchain_ollama import OllamaEmbeddings, ChatOllama
        from langchain_pinecone import PineconeVectorStore
        from langchain_core.prompts import ChatPromptTemplate
        from langchain_core.output_parsers import StrOutputParser
        from langchain_core.runnables import RunnablePassthrough

        _embeddings  = OllamaEmbeddings(model="nomic-embed-text")
        _vectorstore = PineconeVectorStore(
            index_name="ev-policy-docs",
            embedding=_embeddings,
            pinecone_api_key=os.getenv("PINECONE_API_KEY"),
            text_key="text",
        )
        _llm = ChatOllama(model="llama3.2", temperature=0.3)
        RAG_AVAILABLE = True
    except Exception:
        pass

    if not RAG_AVAILABLE:
        try:
            from langchain_ollama import ChatOllama
            _llm = ChatOllama(model="llama3.2", temperature=0.3)
            LLM_AVAILABLE = True
        except Exception:
            pass


# ── Hybrid response: Pinecone → Ollama → mock ─────────────────────────────────
def _format_docs(docs):
    return "\n\n---\n\n".join(
        f"[Source: {d.metadata.get('source','doc')}]\n{d.page_content}"
        for d in docs
    )

_CHART_KEYWORDS = re.compile(
    r'\b(chart|plot|graph|show|visuali[sz]e|pie|bar|line|scatter|map|choropleth|draw)\b',
    re.IGNORECASE
)

def _parse_chart_intent(query: str) -> dict | None:
    """
    Parse natural language chart requests into chart_tool arguments.
    Returns None if the query doesn't look like a chart request.
    """
    if not _CHART_KEYWORDS.search(query):
        return None

    q = query.lower()

    # Detect chart type
    if "pie" in q:
        chart_type = "pie"
    elif "line" in q or "trend" in q or "over time" in q or "growth" in q:
        chart_type = "line"
    elif "scatter" in q:
        chart_type = "scatter"
    elif "map" in q or "choropleth" in q or "county" in q and "map" in q:
        chart_type = "choropleth_wa"
    else:
        chart_type = "bar"

    # Build a pandas query string from county / make hints
    filters = []
    county_match = re.search(r'\b(king|pierce|snohomish|clark|spokane|thurston|kitsap|whatcom|benton|yakima)\b', q)
    if county_match:
        filters.append(f"County == '{county_match.group(0).title()}'")

    make_map = {"tesla": "TESLA", "chevrolet": "CHEVROLET", "chevy": "CHEVROLET",
                "nissan": "NISSAN", "ford": "FORD", "bmw": "BMW", "kia": "KIA",
                "hyundai": "HYUNDAI", "volkswagen": "VOLKSWAGEN", "audi": "AUDI"}
    for word, make_val in make_map.items():
        if word in q:
            filters.append(f"Make == '{make_val}'")
            break

    pandas_query = " and ".join(filters)

    return {
        "chart_type": chart_type,
        "query": pandas_query,
        "title": query[:80],
    }


def get_response_stream(query: str):
    """
    Generator that yields text chunks so we can stream into st.write_stream.
    Priority: chart intent → agent_workflow → RAG (Pinecone + Ollama) → Ollama only → mock
    Side-effect: populates _last_sources and _last_chart_html.
    """
    global _last_sources, _last_chart_html
    _last_sources = []
    _last_chart_html = ""

    # 0. Chart intent — intercept before LLM if it looks like a visualisation request
    if CHART_AVAILABLE:
        intent = _parse_chart_intent(query)
        if intent:
            result = generate_chart_tool.invoke(intent)
            if result.get("html") and not result.get("error"):
                _last_chart_html = result["html"]
                row_count = result.get("row_count", 0)
                yield f"Here's your **{intent['chart_type']}** chart"
                if intent.get("query"):
                    yield f" (filtered: `{intent['query']}`)"
                yield f" — **{row_count:,}** records plotted."
                return
            elif result.get("error"):
                yield f"I tried to generate a chart but ran into an issue: {result['error']}\n\nHere's a text answer instead:\n\n"
                # Fall through to normal LLM path

    # 1. Full agent
    if AGENT_AVAILABLE:
        result = run_agent(query)
        for ch in result:
            yield ch
        return

    # 2. RAG — search Pinecone first, then let Ollama answer with context
    if RAG_AVAILABLE:
        try:
            retriever = _vectorstore.as_retriever(search_kwargs={"k": 4})
            docs = retriever.invoke(query)

            # Capture sources for the drawer
            _last_sources = [
                {
                    "source": d.metadata.get("source", "policy-doc"),
                    "preview": d.page_content[:120],
                    "score": d.metadata.get("score", None),
                }
                for d in docs
            ]

            context = _format_docs(docs) if docs else ""

            if context:
                prompt = ChatPromptTemplate.from_template(
                    "You are an expert on Washington State electric vehicles and EV policy. "
                    "Use the policy context below if it's relevant. "
                    "If the question is about EV statistics (registrations, counties, makes, etc.), "
                    "answer using your knowledge about Washington State EV data "
                    "(276,000+ registrations, King County leads, Tesla ~45% share, etc.). "
                    "Always give a helpful, complete answer.\n\n"
                    "Policy Context (use if relevant):\n{context}\n\n"
                    "Question: {question}\n\nAnswer:"
                )
                chain = (
                    {"context": lambda _: context, "question": RunnablePassthrough()}
                    | prompt
                    | _llm
                    | StrOutputParser()
                )
            else:
                prompt = ChatPromptTemplate.from_template(
                    "You are an expert on Washington State electric vehicles. "
                    "You have knowledge of 276,000+ EV registrations: King County leads with 50k+, "
                    "Tesla has ~45% share, ~79% are BEVs, avg range ~234 miles. "
                    "Answer the following question helpfully and concisely.\n\n"
                    "Question: {question}\n\nAnswer:"
                )
                chain = (
                    {"question": RunnablePassthrough()}
                    | prompt
                    | _llm
                    | StrOutputParser()
                )

            for chunk in chain.stream(query):
                yield chunk
            return
        except Exception:
            pass

    # 3. Ollama only (no Pinecone)
    if LLM_AVAILABLE:
        try:
            prompt = ChatPromptTemplate.from_template(
                "You are an expert on Washington State electric vehicles. "
                "Answer the following question helpfully.\n\nQuestion: {question}\n\nAnswer:"
            )
            chain = ({"question": RunnablePassthrough()} | prompt | _llm | StrOutputParser())
            for chunk in chain.stream(query):
                yield chunk
            return
        except Exception:
            pass

    # 4. Mock fallback
    for ch in mock_response(query):
        yield ch


def mock_response(query: str) -> str:
    q = query.lower()
    if "county" in q and any(w in q for w in ["most","top","highest","best","lead","largest"]):
        return (
            "**King County** leads Washington State with over **50,000 EV registrations**, "
            "followed by **Snohomish** (~35,000) and **Pierce** (~28,000) counties.\n\n"
            "The Seattle–Bellevue metro corridor accounts for nearly **60%** of all statewide registrations."
        )
    elif "tesla" in q:
        return (
            "**Tesla** dominates with ~**45% market share** in Washington State.\n\n"
            "Top models: **Model Y** → **Model 3** → **Model S/X**.\n\n"
            "Chevrolet (~10%) and Nissan (~8%) are the closest competitors."
        )
    elif any(w in q for w in ["make","brand","popular","manufacturer"]):
        return (
            "| Rank | Make | Share |\n|------|------|-------|\n"
            "| 1 | **Tesla** | ~45% |\n| 2 | **Chevrolet** | ~10% |\n"
            "| 3 | **Nissan** | ~8% |\n| 4 | **Ford** | ~7% |\n| 5 | **BMW** | ~5% |"
        )
    elif "range" in q:
        return (
            "Average BEV range in WA: **~234 miles**.\n\n"
            "- Tesla Model S LR — **405 mi**\n- Tesla Model 3 LR — **358 mi**\n"
            "- Chevy Bolt — **259 mi**\n\nPHEVs: typically **20–50 mi** electric-only."
        )
    elif any(w in q for w in ["charging","hotspot","infrastructure","station"]):
        return (
            "Top charging hotspots:\n- **Seattle metro** — highest density nationally\n"
            "- **Bellevue/Redmond/Kirkland** tech corridor\n- **Spokane** — eastern WA\n"
            "- **I-5 and I-90** highway corridors\n\nWA has **3,200+** public stations."
        )
    elif any(w in q for w in ["bev","phev","hybrid","breakdown","split"]):
        return (
            "- 🔋 **BEV**: ~79% (~218,000 vehicles)\n- 🔌 **PHEV**: ~21% (~58,000 vehicles)\n\n"
            "BEV share grew from ~60% (2018) to ~79% today."
        )
    elif any(w in q for w in ["adopt","grow","trend","year","growth","history"]):
        return (
            "| Year | Cumulative EVs |\n|------|----------------|\n"
            "| 2015 | ~15,000 |\n| 2018 | ~50,000 |\n| 2020 | ~85,000 |\n"
            "| 2022 | ~160,000 |\n| 2024 | **276,000+** |"
        )
    elif any(w in q for w in ["city","seattle","bellevue","redmond","tacoma"]):
        return (
            "| City | EVs |\n|------|-----|\n"
            "| **Seattle** | ~42,800 |\n| **Bellevue** | ~13,500 |\n"
            "| **Vancouver** | ~10,300 |\n| **Redmond** | ~9,500 |\n| **Bothell** | ~9,100 |"
        )
    elif any(w in q for w in ["cafv","incentive","rebate","tax","credit"]):
        return (
            "**WA EV Incentives:**\n- Sales tax exemption on EVs under $45k MSRP\n"
            "- Up to **$9,000** state rebate (Clean Vehicle Rebate program)\n"
            "- Federal **$7,500** tax credit (IRA 2022)\n\n"
            "**CAFV eligibility**: 30+ miles electric range required."
        )
    elif any(w in q for w in ["hello","hi","hey","help","what can","capabilities"]):
        return (
            "Hi! I'm your **EV Intelligence Assistant** — powered by Pinecone + llama3.2.\n\n"
            "I can answer questions about:\n"
            "- 🗺️ County & city hotspots\n- 🚗 Makes & models\n- 📈 Adoption trends\n"
            "- 🔋 BEV vs PHEV stats\n- ⚡ Charging infrastructure\n- 💰 Incentives & CAFV eligibility"
        )
    else:
        return (
            f"I can help with Washington State EV data. Try asking about:\n"
            "- *Which county has the most EVs?*\n- *How has EV adoption grown?*\n"
            "- *BEV vs PHEV breakdown?*\n- *Average EV range?*"
        )


# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(layout="wide", page_title="EV Chat", page_icon="🤖", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

:root {
    --bg: #08090F;
    --surface: #0D1117;
    --card: #111827;
    --border: #1A2236;
    --border2: #243045;
    --cyan: #00D4FF;
    --purple: #7C3AED;
    --green: #10B981;
    --amber: #F59E0B;
    --red: #EF4444;
    --t1: #F8FAFC;
    --t2: #E2E8F0;
    --t3: #94A3B8;
    --t4: #475569;
    --user-bg: #162032;
    --user-border: #1E3A5F;
}

html, body, .main, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

/* Narrow centered layout for chat */
.block-container {
    max-width: 780px !important;
    padding: 0 1.25rem 5rem !important;
}

/* Hide header and sidebar nav */
header[data-testid="stHeader"] {
    display: none !important;
}
[data-testid="stSidebarNav"] {
    display: none !important;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
    background: #09101A !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0 !important; }
[data-testid="stSidebarContent"] { padding-top: 0 !important; }
/* Sidebar nav buttons */
div[data-testid="stSidebar"] .stButton {
    margin-bottom: 6px !important;
}
div[data-testid="stSidebar"] .stButton > button {
    background: transparent !important; color: var(--t4) !important;
    border: 1px solid transparent !important; border-radius: 10px !important;
    padding: 0.55rem 0.9rem !important; font-weight: 500 !important; font-size: 0.875rem !important;
    text-align: left !important; width: 100% !important; box-shadow: none !important;
    letter-spacing: 0 !important; transition: all 0.15s !important;
}
div[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(0,212,255,0.07) !important; border-color: rgba(0,212,255,0.2) !important;
    color: var(--cyan) !important; transform: none !important; box-shadow: none !important;
}

/* ── CHAT MESSAGES — Apple/GPT style ── */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    padding: 0.1rem 0 !important;
    max-width: 100% !important;
}

/* Avatars */
[data-testid="chatAvatarIcon-user"] {
    background: linear-gradient(135deg,#7C3AED,#00D4FF) !important;
    border-radius: 50% !important;
    box-shadow: 0 2px 8px rgba(124,58,237,0.4) !important;
}
[data-testid="chatAvatarIcon-assistant"] {
    background: #111827 !important;
    border: 1px solid var(--border2) !important;
    border-radius: 50% !important;
}

/* Message bubbles */
[data-testid="stChatMessageContent"] {
    background: var(--card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 20px !important;
    padding: 1rem 1.25rem !important;
    font-size: 0.9375rem !important;
    line-height: 1.72 !important;
    color: var(--t2) !important;
    box-shadow: 0 1px 8px rgba(0,0,0,0.2) !important;
    width: 100% !important;
}

/* User bubble — blue tint, right-side tail */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) [data-testid="stChatMessageContent"] {
    background: var(--user-bg) !important;
    border-color: var(--user-border) !important;
    border-radius: 20px 20px 4px 20px !important;
    color: var(--t1) !important;
}

/* Assistant bubble — subtle left accent */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) [data-testid="stChatMessageContent"] {
    border-color: var(--border) !important;
    border-left: 2px solid rgba(0,212,255,0.35) !important;
    border-radius: 20px 20px 20px 4px !important;
}

/* Markdown in bubbles */
[data-testid="stChatMessageContent"] p { margin: 0 0 0.55rem !important; }
[data-testid="stChatMessageContent"] p:last-child { margin-bottom: 0 !important; }
[data-testid="stChatMessageContent"] strong { color: var(--t1) !important; font-weight: 600 !important; }
[data-testid="stChatMessageContent"] em { color: #94A3B8 !important; }
[data-testid="stChatMessageContent"] ul, [data-testid="stChatMessageContent"] ol {
    padding-left: 1.25rem !important; margin: 0.35rem 0 !important;
}
[data-testid="stChatMessageContent"] li { margin: 0.2rem 0 !important; color: var(--t2) !important; }
[data-testid="stChatMessageContent"] table {
    border-collapse: collapse !important; width: 100% !important;
    margin: 0.6rem 0 !important; font-size: 0.875rem !important; border-radius: 10px !important; overflow: hidden !important;
}
[data-testid="stChatMessageContent"] th {
    background: rgba(0,212,255,0.1) !important; color: #00D4FF !important;
    padding: 0.45rem 0.8rem !important; border: 1px solid var(--border) !important;
    font-weight: 600 !important; font-size: 0.78rem !important;
    letter-spacing: 0.04em !important; text-transform: uppercase !important;
}
[data-testid="stChatMessageContent"] td {
    padding: 0.4rem 0.8rem !important; border: 1px solid #1A2236 !important; color: var(--t2) !important;
}
[data-testid="stChatMessageContent"] tr:nth-child(even) td { background: rgba(255,255,255,0.02) !important; }
[data-testid="stChatMessageContent"] code {
    background: rgba(0,212,255,0.09) !important; color: #00D4FF !important;
    padding: 0.1em 0.45em !important; border-radius: 5px !important; font-size: 0.875em !important;
}

/* ── THINKING ANIMATION ── */
@keyframes thinking-dot {
    0%, 80%, 100% { opacity: 0.15; transform: scale(0.8); }
    40%            { opacity: 1;    transform: scale(1); }
}
.thinking-dots {
    display: inline-flex; align-items: center; gap: 5px; padding: 4px 0;
}
.thinking-dots span {
    width: 7px; height: 7px; border-radius: 50%; background: #00D4FF;
    animation: thinking-dot 1.3s ease-in-out infinite;
}
.thinking-dots span:nth-child(1) { animation-delay: 0s; }
.thinking-dots span:nth-child(2) { animation-delay: 0.2s; }
.thinking-dots span:nth-child(3) { animation-delay: 0.4s; }

/* ── CHAT INPUT — Apple pill ── */
.stChatFloatingInputContainer {
    padding-bottom: 0.5rem !important;
}
[data-testid="stBottomBlockContainer"] {
    padding-bottom: 0rem !important;
}

[data-testid="stChatInput"] {
    border-radius: 28px !important;
    border: 1.5px solid var(--border2) !important;
    background: var(--surface) !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
    overflow: hidden !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
[data-testid="stChatInput"]:focus-within {
    border-color: rgba(0,212,255,0.4) !important;
    box-shadow: 0 4px 20px rgba(0,0,0,0.35), 0 0 0 3px rgba(0,212,255,0.07) !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important; color: var(--t1) !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.9375rem !important;
    border: none !important; padding: 0.8rem 1.1rem !important; line-height: 1.5 !important;
}
[data-testid="stChatInput"] textarea::placeholder { color: var(--t4) !important; }

/* ── SUGGESTION PILLS ── */
.pill-row .stButton > button {
    background: var(--surface) !important; color: var(--t3) !important;
    border: 1px solid var(--border2) !important; border-radius: 100px !important;
    padding: 0.38rem 0.95rem !important; font-size: 0.78rem !important; font-weight: 500 !important;
    box-shadow: none !important; letter-spacing: 0 !important;
    white-space: nowrap !important; transition: all 0.15s !important; height: auto !important;
}
.pill-row .stButton > button:hover {
    border-color: rgba(0,212,255,0.4) !important; color: var(--cyan) !important;
    background: rgba(0,212,255,0.06) !important; transform: none !important; box-shadow: none !important;
}

/* ── CLEAR BUTTON ── */
.clear-btn .stButton > button {
    background: rgba(239,68,68,0.06) !important; color: #F87171 !important;
    border: 1px solid rgba(239,68,68,0.2) !important; border-radius: 10px !important;
    box-shadow: none !important; font-size: 0.82rem !important;
    padding: 0.5rem 1rem !important; transition: all 0.15s !important;
}
.clear-btn .stButton > button:hover {
    background: rgba(239,68,68,0.12) !important; border-color: rgba(239,68,68,0.4) !important;
    transform: none !important; box-shadow: none !important;
}

::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,212,255,0.35); }
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    render_sidebar()

    # Backend status section
    st.markdown('<div style="padding:0 1.25rem 0.25rem;"><span style="color:#475569;font-size:0.6rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;">Backend</span></div>', unsafe_allow_html=True)


    st.markdown('<div style="height:1px;background:#1A2236;margin:0.6rem 1.25rem;"></div>', unsafe_allow_html=True)

    # Backend status
    if AGENT_AVAILABLE:
        status_bg, status_dot, status_color, status_label, status_sub = \
            "rgba(16,185,129,.07)","#10B981","#10B981","Full Agent Active","LangChain · Pinecone · Ollama"
    elif RAG_AVAILABLE:
        status_bg, status_dot, status_color, status_label, status_sub = \
            "rgba(0,212,255,.06)","#00D4FF","#00D4FF","RAG Pipeline Active","Pinecone · llama3.2 · nomic-embed"
    elif LLM_AVAILABLE:
        status_bg, status_dot, status_color, status_label, status_sub = \
            "rgba(124,58,237,.07)","#7C3AED","#7C3AED","LLM Active","llama3.2 via Ollama"
    else:
        status_bg, status_dot, status_color, status_label, status_sub = \
            "rgba(245,158,11,.06)","#F59E0B","#F59E0B","Demo Mode","Curated responses"

    st.markdown(f"""
    <div style="margin:0 1.25rem 0.6rem;padding:0.65rem 0.9rem;
                background:{status_bg};border:1px solid {status_dot}33;border-radius:12px;">
        <div style="display:flex;align-items:center;gap:0.45rem;">
            <span style="width:7px;height:7px;border-radius:50%;background:{status_dot};
                         box-shadow:0 0 7px {status_dot};flex-shrink:0;"></span>
            <span style="color:{status_color};font-size:0.8rem;font-weight:600;">{status_label}</span>
        </div>
        <div style="color:#475569;font-size:0.7rem;margin-top:0.2rem;padding-left:1rem;">{status_sub}</div>
    </div>
    """, unsafe_allow_html=True)

    # Session counter
    msg_count = max(len(st.session_state.get("messages", [])) - 1, 0)
    st.markdown(f"""
    <div style="padding:0 1.25rem 0.5rem;">
        <div style="color:#475569;font-size:0.6rem;font-weight:700;letter-spacing:0.12em;
                    text-transform:uppercase;margin-bottom:0.45rem;">Session</div>
        <div style="display:flex;justify-content:space-between;align-items:center;font-size:0.78rem;">
            <span style="color:#64748B;">Messages</span>
            <span style="color:#00D4FF;font-weight:600;background:rgba(0,212,255,0.08);
                         border:1px solid rgba(0,212,255,0.15);border-radius:6px;
                         padding:0.1rem 0.55rem;font-size:0.73rem;">{msg_count}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:#1A2236;margin:0.4rem 1.25rem 0.6rem;"></div>', unsafe_allow_html=True)

    st.markdown('<div class="clear-btn" style="padding:0 1.25rem;">', unsafe_allow_html=True)
    if st.button("🗑️  Clear conversation", use_container_width=True, key="clear_chat"):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "Conversation cleared. How can I help you explore Washington State EV data?"
        }]
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
    <div style="margin:0.75rem 1.25rem 0;padding:0.7rem 0.9rem;background:rgba(124,58,237,.06);
                border:1px solid rgba(124,58,237,.15);border-radius:12px;">
        <div style="color:#7C3AED;font-size:0.7rem;font-weight:600;margin-bottom:0.25rem;">💡 Tip</div>
        <div style="color:#475569;font-size:0.7rem;line-height:1.5;">
            Ask about specific cities, counties, EV makes, or WA state incentives.
        </div>
    </div>
    """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN CHAT
# ═══════════════════════════════════════════════════════════════════════════════

# Page header
st.markdown("""
<div style="padding:1.75rem 0 0.75rem;text-align:center;">
    <div style="display:inline-flex;align-items:center;justify-content:center;
                width:48px;height:48px;border-radius:15px;margin-bottom:0.85rem;
                background:linear-gradient(135deg,#7C3AED,#00D4FF);
                box-shadow:0 6px 20px rgba(124,58,237,0.35);">⚡</div>
    <h1 style="color:#F8FAFC;font-size:1.5rem;font-weight:700;margin:0 0 0.3rem;letter-spacing:-.4px;">
        EV Intelligence Assistant
    </h1>
    <p style="color:#475569;font-size:0.84rem;margin:0;">
        Ask me anything about Washington State electric vehicle data
    </p>
</div>
""", unsafe_allow_html=True)

# Session state
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": (
            "Hello! I'm your **EV Intelligence Assistant** — powered by Pinecone + llama3.2 + Ollama.\n\n"
            "I can help you explore **276,000+ EV registrations** across Washington State. "
            "Ask me about counties, cities, EV brands, adoption trends, BEV vs PHEV splits, "
            "charging hotspots, or WA state incentives.\n\n"
            "What would you like to know?"
        )
    }]

# Render history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("chart_html"):
            components.html(msg["chart_html"], height=480, scrolling=False)

# ── Suggestion pills ───────────────────────────────────────────────────────────
QUESTIONS = [
    ("🗺️", "Which county has the most EVs?"),
    ("🚗", "Most popular EV make?"),
    ("⚡", "Average EV range in WA?"),
    ("📈", "How has EV adoption grown?"),
    ("🔋", "BEV vs PHEV breakdown?"),
    ("🏙️", "Top cities for EVs?"),
    ("💡", "Where are charging hotspots?"),
    ("🔮", "Forecast King County EVs to 2030"),
]

CHART_PILLS = [
    ("📊", "Bar chart of top EV makes"),
    ("🥧", "Pie chart of BEV vs PHEV"),
    ("📉", "Line chart of EV adoption trend"),
    ("🗺️", "Show choropleth map of EV density by county"),
]

st.markdown("""
<div style="margin:1rem 0 0.4rem;display:flex;align-items:center;gap:0.5rem;">
    <span style="color:#334155;font-size:0.68rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;">Ask a question</span>
    <div style="flex:1;height:1px;background:#1A2236;"></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="pill-row">', unsafe_allow_html=True)
r1 = st.columns(4)
r2 = st.columns(4)
pill_q = None
for i, (icon, q) in enumerate(QUESTIONS):
    col = r1[i] if i < 4 else r2[i - 4]
    with col:
        if st.button(f"{icon} {q}", key=f"pill_{i}", use_container_width=True):
            pill_q = q
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div style="margin:.75rem 0 .4rem;display:flex;align-items:center;gap:0.5rem;">
    <span style="color:#334155;font-size:0.68rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;">Generate a chart</span>
    <div style="flex:1;height:1px;background:#1A2236;"></div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="pill-row">', unsafe_allow_html=True)
chart_cols = st.columns(4)
for i, (icon, q) in enumerate(CHART_PILLS):
    with chart_cols[i]:
        if st.button(f"{icon} {q}", key=f"cpill_{i}", use_container_width=True):
            pill_q = q
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ── Chat input ─────────────────────────────────────────────────────────────────
prompt = st.chat_input("Message EV Intelligence…")

if pill_q:
    prompt = pill_q

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown(
            """
            <div style="display:flex;align-items:center;gap:.75rem;padding:.25rem 0;">
                <div class="thinking-dots"><span></span><span></span><span></span></div>
                <span style="color:#475569;font-size:.8rem;font-style:italic;">Agent thinking…</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
        full_response = st.write_stream(get_response_stream(prompt))
        thinking_placeholder.empty()

        # Inline chart — render immediately after the text response
        chart_html = _last_chart_html
        if chart_html:
            components.html(chart_html, height=480, scrolling=False)

        # RAG source reveal drawer
        sources = list(_last_sources)
        if sources:
            with st.expander(f"Sources used ({len(sources)})", expanded=False):
                for src in sources:
                    score = src.get("score")
                    if score is not None:
                        if score > 0.8:
                            badge_color, badge_bg = "#10B981", "rgba(16,185,129,.12)"
                        elif score > 0.6:
                            badge_color, badge_bg = "#F59E0B", "rgba(245,158,11,.12)"
                        else:
                            badge_color, badge_bg = "#EF4444", "rgba(239,68,68,.10)"
                        score_badge = (
                            f'<span style="background:{badge_bg};color:{badge_color};'
                            f'border:1px solid {badge_color}40;border-radius:6px;'
                            f'padding:.1rem .4rem;font-size:.7rem;font-weight:600;">'
                            f'{score:.2f}</span>'
                        )
                    else:
                        score_badge = ""

                    st.markdown(
                        f"""
                        <div style="background:#111827;border:1px solid #1A2236;border-radius:10px;
                                    padding:.75rem 1rem;margin-bottom:.5rem;">
                            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:.35rem;">
                                <span style="color:#00D4FF;font-size:.78rem;font-weight:600;">
                                    📄 {src['source']}
                                </span>
                                {score_badge}
                            </div>
                            <div style="color:#64748B;font-size:.78rem;line-height:1.5;">
                                {src['preview']}…
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # Store chart HTML alongside the message so it re-renders on rerun
    msg_entry = {"role": "assistant", "content": full_response}
    if _last_chart_html:
        msg_entry["chart_html"] = _last_chart_html
    st.session_state.messages.append(msg_entry)
    if pill_q:
        st.rerun()
