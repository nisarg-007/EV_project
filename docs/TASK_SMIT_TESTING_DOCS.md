# ✅ SMIT — Testing, Documentation & Demo Preparation
**STATUS: ✅ COMPLETED**

**Role:** QA Lead / Technical Writer / Demo Coordinator  
**Branch Name:** `smit`  
**Estimated Time:** 10-12 hours

---

## 🚨 FILE RESTRICTIONS — READ CAREFULLY

### ✅ Files you CAN create/edit:
```
tests/                              ← Test suite folder (CREATE)
  tests/__init__.py                 ← Empty init file (CREATE)
  tests/test_analytics_tools.py     ← Unit tests for Person 2's code (CREATE)
  tests/test_rag_query.py           ← Unit tests for Person 3's code (CREATE)
  tests/test_agent_workflow.py      ← Integration tests for Person 4's code (CREATE)
  tests/demo_queries.py             ← Demo script with curated questions (CREATE)
README.md                           ← Project documentation (EDIT)
docs/Project_Log.md                 ← Update with latest progress (EDIT)
docs/SETUP_GUIDE.md                 ← Step-by-step setup for new users (CREATE)
scripts/requirements.txt            ← Add test dependencies if needed (EDIT)
.gitignore                          ← Update if needed (EDIT)
```

### 🚫 Files you MUST NOT edit:
```
app.py, pages/                      ← Somil owns this
scripts/analytics_tools.py          ← Nisarg owns this
scripts/setup_rag.py                ← Parva owns this  
scripts/rag_query.py                ← Parva owns this
scripts/agent_workflow.py           ← MD owns this
scripts/agent_config.py             ← MD owns this
notebooks/                          ← Nisarg owns this
data/                               ← Nisarg & Parva own this
docs/Milestone1_Presentation.html   ← Somil owns this
```

---

## 📋 TASK DESCRIPTION

You are the **quality assurance and documentation** backbone. Your job is to:

1. **Write unit tests** for every team member's code (using `pytest`)
2. **Write a comprehensive README** that explains the project to anyone
3. **Create a setup guide** so any professor/interviewer can run the project
4. **Prepare a demo script** with curated queries that showcase the system
5. **Maintain the project log** with accurate progress updates
6. **Run all tests** and report bugs to the responsible team member

You are the **first person an interviewer talks to** when reading the repo. Your README and docs determine the first impression.

---

## 🎯 MINIMUM BENCHMARKS (Must achieve ALL)

### Benchmark 1: Test suite passes
```bash
cd EV_project
pip install pytest
pytest tests/ -v
# At least 15 tests, >80% pass rate
```

### Benchmark 2: README is complete and professional
- [ ] Project title, description, and architecture diagram (text-based is fine)
- [ ] Team member names and roles
- [ ] Tech stack with versions
- [ ] Installation instructions (step-by-step, copy-pasteable)
- [ ] How to run the project (one command)
- [ ] Screenshots or GIFs of the working dashboard (add after Person 1 is done)
- [ ] Project structure tree
- [ ] License section

### Benchmark 3: Setup guide works on a fresh machine
- [ ] A teammate who has NEVER set up the project can follow SETUP_GUIDE.md
- [ ] Every command is copy-pasteable
- [ ] Covers: Python install, pip install, Ollama install, Pinecone key, running the app

### Benchmark 4: Demo script produces impressive output
```bash
cd EV_project
python tests/demo_queries.py
# Runs 5-8 curated queries through the agent and prints answers
```

---

## 🏗️ STEP-BY-STEP INSTRUCTIONS

### Step 1: Create test directory structure
```bash
mkdir tests
# Create tests/__init__.py (empty file)
```

### Step 2: Write `tests/test_analytics_tools.py`

```python
"""Unit tests for Person 2's analytics tools."""
import pytest
import pandas as pd
import os

# Skip all tests if the Parquet file doesn't exist
PARQUET_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'processed', 'Electric_Vehicle_Population_Data.parquet')
SKIP_IF_NO_DATA = pytest.mark.skipif(
    not os.path.exists(PARQUET_PATH),
    reason="Parquet data file not found"
)

@SKIP_IF_NO_DATA
class TestAnalyticsTools:
    
    def test_import(self):
        """analytics_tools.py is importable."""
        from scripts.analytics_tools import get_ev_counts_by_county
    
    def test_county_counts_returns_dataframe(self):
        """get_ev_counts_by_county returns a DataFrame."""
        from scripts.analytics_tools import get_ev_counts_by_county
        result = get_ev_counts_by_county(PARQUET_PATH)
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
    
    def test_county_counts_has_expected_columns(self):
        """Result has County and ev_count columns."""
        from scripts.analytics_tools import get_ev_counts_by_county
        result = get_ev_counts_by_county(PARQUET_PATH)
        assert "County" in result.columns
        assert "ev_count" in result.columns
    
    def test_county_counts_king_is_top(self):
        """King County should have the most EVs in WA state."""
        from scripts.analytics_tools import get_ev_counts_by_county
        result = get_ev_counts_by_county(PARQUET_PATH)
        assert result.iloc[0]["County"] == "King"
    
    def test_adoption_growth_returns_dataframe(self):
        """get_adoption_growth_rate returns a DataFrame."""
        from scripts.analytics_tools import get_adoption_growth_rate
        result = get_adoption_growth_rate(PARQUET_PATH)
        assert isinstance(result, pd.DataFrame)
        assert len(result) > 0
    
    def test_growth_rate_has_model_year(self):
        """Result has Model Year column."""
        from scripts.analytics_tools import get_adoption_growth_rate
        result = get_adoption_growth_rate(PARQUET_PATH)
        assert "Model Year" in result.columns
    
    # Add more tests as Person 2 builds more functions:
    # test_top_makes_and_models
    # test_bev_vs_phev_breakdown
    # test_cafv_eligibility_summary
    # test_ev_range_statistics
    # test_utility_provider_summary
```

### Step 3: Write `tests/test_rag_query.py`

```python
"""Unit tests for Person 3's RAG pipeline."""
import pytest
import os

SKIP_IF_NO_KEY = pytest.mark.skipif(
    not os.getenv("PINECONE_API_KEY"),
    reason="PINECONE_API_KEY not set"
)

class TestRAGQuery:
    
    def test_import(self):
        """rag_query.py is importable."""
        try:
            from scripts.rag_query import query_policy_docs
        except ImportError:
            pytest.skip("rag_query.py not yet created")
    
    @SKIP_IF_NO_KEY
    def test_query_returns_list(self):
        """query_policy_docs returns a list."""
        from scripts.rag_query import query_policy_docs
        result = query_policy_docs("What EV incentives exist in WA?")
        assert isinstance(result, list)
    
    @SKIP_IF_NO_KEY
    def test_query_results_have_required_keys(self):
        """Each result has text, source, and score."""
        from scripts.rag_query import query_policy_docs
        results = query_policy_docs("EV tax credit eligibility")
        if len(results) > 0:
            for r in results:
                assert "text" in r
                assert "source" in r
                assert "score" in r
    
    @SKIP_IF_NO_KEY
    def test_query_results_are_relevant(self):
        """Top result should have a reasonable similarity score."""
        from scripts.rag_query import query_policy_docs
        results = query_policy_docs("Washington state electric vehicle laws")
        if len(results) > 0:
            assert results[0]["score"] > 0.3  # Minimum relevance threshold
```

### Step 4: Write `tests/test_agent_workflow.py`

```python
"""Integration tests for Person 4's agent workflow."""
import pytest

class TestAgentWorkflow:
    
    def test_import(self):
        """agent_workflow.py is importable."""
        try:
            from scripts.agent_workflow import run_agent
        except ImportError:
            pytest.skip("agent_workflow.py not yet created")
    
    def test_run_agent_returns_string(self):
        """run_agent returns a string answer."""
        try:
            from scripts.agent_workflow import run_agent
            result = run_agent("How many EVs are in King County?")
            assert isinstance(result, str)
            assert len(result) > 10  # Should be more than just "error"
        except ImportError:
            pytest.skip("agent_workflow.py not yet created")
    
    def test_router_data_classification(self):
        """Router correctly classifies data questions."""
        try:
            from scripts.agent_workflow import route_question
            result = route_question("How many EVs in King County?")
            assert result in ("data", "both")
        except ImportError:
            pytest.skip("agent_workflow.py not yet created")
    
    def test_router_policy_classification(self):
        """Router correctly classifies policy questions."""
        try:
            from scripts.agent_workflow import route_question
            result = route_question("What is the CAFV tax credit eligibility?")
            assert result in ("policy", "both")
        except ImportError:
            pytest.skip("agent_workflow.py not yet created")
```

### Step 5: Write `tests/demo_queries.py`

```python
"""
Demo script — runs curated queries through the full agent pipeline.
Use this during live demonstrations and presentations.
"""

DEMO_QUERIES = [
    "How many electric vehicles are registered in King County?",
    "What are the top 5 most popular EV makes in Washington state?",
    "What is the CAFV eligibility breakdown across all registered vehicles?",
    "What EV incentives are available in Washington state?",
    "Compare EV adoption trends: which model years saw the fastest growth?",
    "What does Washington law say about EV charging station requirements?",
    "Which utility providers serve the most EV owners in Washington?",
    "Is a 2024 Tesla Model Y eligible for any state-level tax credits?",
]

if __name__ == "__main__":
    try:
        from scripts.agent_workflow import run_agent
    except ImportError:
        print("❌ agent_workflow.py not available yet.")
        print("   Run this script after Person 4 has pushed their code.")
        exit(1)
    
    print("=" * 70)
    print("  ⚡ EV INTELLIGENCE PLATFORM — LIVE DEMO")
    print("=" * 70)
    
    for i, query in enumerate(DEMO_QUERIES, 1):
        print(f"\n{'─' * 60}")
        print(f"  🔍 Demo Query {i}/{len(DEMO_QUERIES)}")
        print(f"  Q: {query}")
        print(f"{'─' * 60}")
        
        try:
            answer = run_agent(query)
            print(f"\n  💬 Answer:\n  {answer}\n")
        except Exception as e:
            print(f"\n  ❌ Error: {e}\n")
    
    print("=" * 70)
    print("  ✅ Demo complete.")
    print("=" * 70)
```

### Step 6: Write `docs/SETUP_GUIDE.md`

This document must allow a **brand new person** (like your professor) to run the project. Include:

```markdown
# Setup Guide — EV Intelligence Platform

## Prerequisites
- Python 3.10+ installed
- Git installed
- 8GB+ RAM recommended (for Ollama)

## Step 1: Clone the Repository
\```bash
git clone https://github.com/somildoshi12/EV_project.git
cd EV_project
\```

## Step 2: Install Python Dependencies
\```bash
pip install -r scripts/requirements.txt
\```

## Step 3: Install Ollama (Local LLM)
- Download from: https://ollama.com/download
- After install, pull the required models:
\```bash
ollama pull llama3.2
ollama pull nomic-embed-text
\```

## Step 4: Set Up Pinecone (Vector DB)
1. Create a free account at https://www.pinecone.io/
2. Get your API key from the Pinecone dashboard
3. Create a `.env` file in the project root:
\```
PINECONE_API_KEY=your_key_here
\```

## Step 5: Populate the RAG Database
\```bash
cd scripts
python setup_rag.py
\```

## Step 6: Run the Application
\```bash
cd ..
streamlit run app.py
\```
The app will open at http://localhost:8501
```

### Step 7: Update README.md
Rewrite the README to be interview-ready. Include:
- Clear project title and 2-sentence description
- Architecture diagram (ASCII art or bullet points)
- "Quick Start" section (3 commands max)
- Feature list with bullet points
- Team members table
- Tech stack table with versions
- Project structure tree (use `tree` command output)

---

## 📦 DELIVERABLE CHECKLIST

```
[ ] tests/ directory exists with __init__.py
[ ] tests/test_analytics_tools.py has 6+ tests
[ ] tests/test_rag_query.py has 4+ tests
[ ] tests/test_agent_workflow.py has 4+ tests
[ ] tests/demo_queries.py runs and produces output
[ ] pytest tests/ -v runs with 0 errors (skips are OK)
[ ] README.md is comprehensive and professional
[ ] docs/SETUP_GUIDE.md allows a fresh setup
[ ] docs/Project_Log.md is updated with current status
[ ] requirements.txt includes pytest
[ ] All file restrictions respected
```

---

## ⚠️ COMMON PITFALLS TO AVOID

1. **Don't edit other people's source code to fix bugs** — Report the bug to them. You only write TESTS, not fixes.
2. **Don't hardcode paths** — Use `os.path.join()` and relative paths from the project root.
3. **Use `pytest.skip()` liberally** — If Person 2/3/4 hasn't pushed yet, skip their tests gracefully, don't fail.
4. **Don't write tests that depend on Ollama running** — Mark those with a skip decorator if Ollama isn't available.
5. **README must have copy-pasteable commands** — Don't write `cd <your-folder>`. Write the exact command.
