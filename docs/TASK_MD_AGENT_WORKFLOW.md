# 🧠 MD — LangGraph Agent Workflow

**Role:** AI Agent / Orchestration Engineer  
**Branch Name:** `md`  
**Estimated Time:** 12-15 hours

---

## 🚨 FILE RESTRICTIONS — READ CAREFULLY

### ✅ Files you CAN create/edit:
```
scripts/agent_workflow.py       ← Main LangGraph agent (CREATE)
scripts/agent_config.py         ← Agent prompts and config (CREATE)
```

### 🚫 Files you MUST NOT edit:
```
app.py, pages/                  ← Somil owns this
scripts/analytics_tools.py      ← Nisarg owns this (you IMPORT from it)
scripts/setup_rag.py            ← Parva owns this
scripts/rag_query.py            ← Parva owns this (you IMPORT from it)
tests/                          ← Smit owns this
notebooks/                      ← Nisarg owns this
data/                           ← Nisarg & Parva own this
docs/                           ← Somil & Smit own this
```

---

## 📋 TASK DESCRIPTION

You are the **brain** of this project. Your job is to build the LangGraph agentic workflow that:

1. **Routes** incoming user questions to the correct specialist
2. **Data Analyst path**: Calls deterministic functions from `analytics_tools.py` (Nisarg's code)
3. **Policy Expert path**: Calls the RAG query function from `rag_query.py` (Parva's code)
4. **Synthesizes** the results into a natural language answer using Ollama
5. Exposes a **single entry-point function** that Somil can call from the Streamlit UI:
   ```python
   from scripts.agent_workflow import run_agent
   result = run_agent("Which counties have the most EVs?")
   ```

---

## 🎯 MINIMUM BENCHMARKS (Must achieve ALL)

### Benchmark 1: Agent correctly classifies questions
Test these queries — each must route to the right path:

| Query | Expected Route |
|:---|:---|
| "How many EVs are in King County?" | → Data Analyst |
| "What is the CAFV eligibility breakdown?" | → Data Analyst |
| "What incentives exist for electric vehicles in Washington?" | → Policy Expert |
| "Is a Tesla Model 3 eligible for the state tax credit?" | → Policy Expert |
| "Compare EV adoption in King County vs Pierce County" | → Data Analyst |
| "What does RCW 82.08.809 say about exemptions?" | → Policy Expert |

### Benchmark 2: Agent produces readable answers
- [ ] Answers are in natural English sentences, not raw JSON/DataFrames
- [ ] Data answers include actual numbers from the dataset
- [ ] Policy answers cite the source document name
- [ ] Combined questions (data + policy) produce coherent responses

### Benchmark 3: Agent runs end-to-end
```bash
cd EV_project
python scripts/agent_workflow.py "How many EVs are in King County?"
# Must output a natural language answer like:
# "King County has approximately 120,000 registered EVs, making it the
#  highest-adoption county in Washington State."
```

### Benchmark 4: Graceful failure handling
- [ ] If Ollama is not running → clear error message, not a crash
- [ ] If Person 2's tools aren't ready → fallback message
- [ ] If Person 3's RAG isn't populated → fallback message
- [ ] Unknown question types → polite "I can't answer that" response

---

## 🏗️ ARCHITECTURE

```
User Query
    │
    ▼
┌────────────┐
│   Router   │  ← Ollama classifies: "data" or "policy" or "both"
└────────────┘
    │         │
    ▼         ▼
┌────────┐ ┌────────────┐
│  Data  │ │   Policy   │
│Analyst │ │   Expert   │
│        │ │            │
│ Calls  │ │ Calls      │
│DuckDB  │ │rag_query.py│
│ tools  │ │(Pinecone)  │
└────────┘ └────────────┘
    │         │
    ▼         ▼
┌────────────────────┐
│    Synthesizer     │  ← Ollama generates final natural language answer
└────────────────────┘
    │
    ▼
  Answer (string)
```

---

## 🏗️ STEP-BY-STEP INSTRUCTIONS

### Step 1: Create `scripts/agent_config.py`

```python
"""Agent configuration — prompts and model settings."""

OLLAMA_MODEL = "llama3.2"  # or "mistral" — whichever is installed

ROUTER_PROMPT = """You are a query router. Classify the user's question into one of three categories:

- "data" → if the question asks about EV counts, statistics, counties, zip codes, growth rates, makes, models, ranges, or any numerical analysis of vehicle registration data.
- "policy" → if the question asks about laws, incentives, tax credits, eligibility, regulations, RCW codes, NEVI, IRA, CAFV, or government programs.
- "both" → if the question requires both data analysis AND policy information.

Respond with ONLY one word: data, policy, or both.

User question: {question}
"""

DATA_SYNTHESIS_PROMPT = """You are a data analyst for an EV infrastructure intelligence platform.
Based on the following data results, provide a clear, professional answer to the user's question.
Include specific numbers and keep it concise.

User Question: {question}

Data Results:
{data_results}

Provide a clear 2-4 sentence answer:"""

POLICY_SYNTHESIS_PROMPT = """You are a policy expert for an EV infrastructure intelligence platform.
Based on the following policy document excerpts, provide a clear, professional answer to the user's question.
Cite the source document when possible.

User Question: {question}

Relevant Policy Excerpts:
{policy_results}

Provide a clear 2-4 sentence answer:"""

COMBINED_SYNTHESIS_PROMPT = """You are an expert at the intersection of EV data analytics and policy.
Combine the data findings and policy context below into a unified answer.

User Question: {question}

Data Findings:
{data_results}

Policy Context:
{policy_results}

Provide a clear, comprehensive 3-5 sentence answer:"""
```

### Step 2: Create `scripts/agent_workflow.py`

```python
"""
LangGraph Agent Workflow — routes queries to Data Analyst or Policy Expert.
Entry point: run_agent(question: str) -> str
"""

import ollama
from scripts.agent_config import (
    OLLAMA_MODEL, ROUTER_PROMPT, DATA_SYNTHESIS_PROMPT,
    POLICY_SYNTHESIS_PROMPT, COMBINED_SYNTHESIS_PROMPT
)

# ── Import teammate modules (with fallback) ──
try:
    from scripts.analytics_tools import (
        get_ev_counts_by_county,
        get_adoption_growth_rate,
        get_top_makes_and_models,
        get_bev_vs_phev_breakdown,
        get_cafv_eligibility_summary,
        # ... add more as Person 2 builds them
    )
    DATA_TOOLS_AVAILABLE = True
except ImportError:
    DATA_TOOLS_AVAILABLE = False
    print("⚠️ analytics_tools.py not ready. Data agent will use fallback.")

try:
    from scripts.rag_query import query_policy_docs
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("⚠️ rag_query.py not ready. Policy agent will use fallback.")


def route_question(question: str) -> str:
    """Use Ollama to classify the question as data/policy/both."""
    try:
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": ROUTER_PROMPT.format(question=question)}]
        )
        route = response["message"]["content"].strip().lower()
        if route not in ("data", "policy", "both"):
            route = "data"  # default fallback
        return route
    except Exception as e:
        print(f"Router error: {e}")
        return "data"


def handle_data_query(question: str) -> str:
    """Call analytics tools and return raw results as a string."""
    if not DATA_TOOLS_AVAILABLE:
        return "Data tools are not yet available. Please check analytics_tools.py."
    
    results = []
    q_lower = question.lower()
    
    # Simple keyword-based tool selection
    try:
        if "county" in q_lower and "compare" not in q_lower:
            df = get_ev_counts_by_county()
            results.append(f"EV Counts by County (Top 10):\n{df.head(10).to_string()}")
        
        if "growth" in q_lower or "trend" in q_lower or "year" in q_lower:
            df = get_adoption_growth_rate()
            results.append(f"Adoption by Model Year:\n{df.to_string()}")
        
        if "make" in q_lower or "model" in q_lower or "popular" in q_lower:
            df = get_top_makes_and_models()
            results.append(f"Top Makes & Models:\n{df.head(10).to_string()}")
        
        if "bev" in q_lower or "phev" in q_lower or "type" in q_lower:
            df = get_bev_vs_phev_breakdown()
            results.append(f"BEV vs PHEV:\n{df.to_string()}")
        
        if "cafv" in q_lower or "eligib" in q_lower:
            df = get_cafv_eligibility_summary()
            results.append(f"CAFV Eligibility:\n{df.to_string()}")
        
        # Default: show county counts if no keyword matched
        if not results:
            df = get_ev_counts_by_county()
            results.append(f"EV Counts by County (Top 10):\n{df.head(10).to_string()}")
    except Exception as e:
        results.append(f"Error running data tools: {e}")
    
    return "\n\n".join(results)


def handle_policy_query(question: str) -> str:
    """Query RAG pipeline and return relevant policy excerpts."""
    if not RAG_AVAILABLE:
        return "RAG pipeline is not yet available. Please check rag_query.py and Pinecone."
    
    try:
        docs = query_policy_docs(question, top_k=3)
        if not docs:
            return "No relevant policy documents found."
        
        excerpts = []
        for i, doc in enumerate(docs):
            excerpts.append(f"[Source: {doc['source']}] (relevance: {doc['score']:.2f})\n{doc['text']}")
        
        return "\n\n---\n\n".join(excerpts)
    except Exception as e:
        return f"Error querying policy docs: {e}"


def synthesize_answer(question: str, route: str, data_results: str = "", policy_results: str = "") -> str:
    """Use Ollama to generate a natural language answer from raw results."""
    try:
        if route == "data":
            prompt = DATA_SYNTHESIS_PROMPT.format(question=question, data_results=data_results)
        elif route == "policy":
            prompt = POLICY_SYNTHESIS_PROMPT.format(question=question, policy_results=policy_results)
        else:
            prompt = COMBINED_SYNTHESIS_PROMPT.format(
                question=question, data_results=data_results, policy_results=policy_results
            )
        
        response = ollama.chat(
            model=OLLAMA_MODEL,
            messages=[{"role": "user", "content": prompt}]
        )
        return response["message"]["content"].strip()
    except Exception as e:
        # If Ollama fails, return raw results
        return f"(LLM unavailable — raw results)\n\n{data_results}\n\n{policy_results}"


def run_agent(question: str) -> str:
    """
    Main entry point. Person 1 calls this from Streamlit.
    Takes a question string, returns a natural language answer string.
    """
    # Step 1: Route
    route = route_question(question)
    print(f"  [Router] → {route}")
    
    # Step 2: Execute
    data_results = ""
    policy_results = ""
    
    if route in ("data", "both"):
        data_results = handle_data_query(question)
    if route in ("policy", "both"):
        policy_results = handle_policy_query(question)
    
    # Step 3: Synthesize
    answer = synthesize_answer(question, route, data_results, policy_results)
    return answer


if __name__ == "__main__":
    import sys
    q = sys.argv[1] if len(sys.argv) > 1 else "How many EVs are registered in King County?"
    print(f"\n🔍 Question: {q}\n")
    answer = run_agent(q)
    print(f"\n💬 Answer:\n{answer}")
```

### Step 3: Test with mock data first

Before Person 2 and 3's code is ready, test the router independently:

```python
# Test just the router
questions = [
    "How many EVs in King County?",
    "What tax credits exist for EVs?",
    "Which county has the most EVs and what incentives apply there?"
]
for q in questions:
    print(f"Q: {q} → Route: {route_question(q)}")
```

---

## 📦 DELIVERABLE CHECKLIST

```
[ ] scripts/agent_workflow.py exists and is importable
[ ] scripts/agent_config.py exists with all prompts
[ ] from scripts.agent_workflow import run_agent works
[ ] Router correctly classifies 6+ test queries
[ ] Data queries return real numbers (when Person 2's tools are ready)
[ ] Policy queries return real excerpts (when Person 3's RAG is ready)
[ ] Answers are natural English sentences, not raw DataFrames
[ ] Graceful error handling (no crashes when dependencies missing)
[ ] python scripts/agent_workflow.py "test question" works from CLI
[ ] No Ollama model is hardcoded — uses OLLAMA_MODEL from agent_config.py
```

---

## ⚠️ COMMON PITFALLS TO AVOID

1. **Don't build your own RAG** — Person 3 is building `rag_query.py`. You just call `query_policy_docs(question)`.
2. **Don't build your own analytics** — Person 2 is building `analytics_tools.py`. You just import their functions.
3. **Don't use OpenAI** — We use `ollama.chat()` with a local model. No API keys needed for the LLM.
4. **Don't over-engineer the router** — A simple prompt that returns "data"/"policy"/"both" is enough. Don't build a fine-tuned classifier.
5. **Make sure Ollama is running** — `ollama serve` must be running in the background. If not, your code will fail.
6. **Wrap all imports in try/except** — Your code must not crash if Person 2 or 3 hasn't pushed yet.
