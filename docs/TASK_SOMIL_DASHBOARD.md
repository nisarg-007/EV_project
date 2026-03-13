# 🖥️ SOMIL — Streamlit Dashboard & UI Integration

**Role:** Front-End / Dashboard Lead  
**Branch Name:** `somil`  
**Estimated Time:** 10-15 hours

---

## 🚨 FILE RESTRICTIONS — READ CAREFULLY

### ✅ Files you CAN create/edit:
```
app.py                          ← Main Streamlit entry point (CREATE)
pages/                          ← Streamlit multi-page folder (CREATE)
  pages/1_Dashboard.py          ← Data visualization page (CREATE)
  pages/2_Chat.py               ← Chat interface page (CREATE)
  pages/3_About.py              ← About page (CREATE)
.streamlit/                     ← Streamlit config folder (CREATE)
  .streamlit/config.toml        ← Theme/layout config (CREATE)
```

### 🚫 Files you MUST NOT edit:
```
scripts/analytics_tools.py      ← Nisarg owns this
scripts/setup_rag.py            ← Parva owns this
scripts/agent_workflow.py       ← MD owns this
tests/                          ← Smit owns this
README.md                       ← Smit owns this
notebooks/                      ← Nisarg owns this
data/                           ← Nisarg & Parva own this
```

---

## 📋 TASK DESCRIPTION

Build the **Streamlit web application** that serves as the unified front-end for the entire project. This dashboard has TWO main functions:

1. **Data Visualization Page** — Interactive charts and maps showing EV registration data
2. **AI Chat Page** — A chat interface where users ask questions and the LangGraph agent responds

You will **import** functions from other team members' files (Person 2's analytics tools, Person 4's agent workflow), but you do NOT write those functions yourself. Use **mock data / placeholder functions** until their code is ready, then swap in the imports.

---

## 🎯 MINIMUM BENCHMARKS (Must achieve ALL)

### Benchmark 1: App runs without errors
```bash
cd EV_project
streamlit run app.py
# Must open in browser without any crash or traceback
```

### Benchmark 2: Dashboard page shows at least 3 visualizations
- [ ] **Bar chart**: Top 10 counties by EV count (use Plotly)
- [ ] **Line chart**: EV adoption growth over model years (use Plotly)
- [ ] **Map**: Folium or Plotly choropleth showing EV density by county/zip

### Benchmark 3: Chat page has a working chat interface
- [ ] Text input box at bottom, messages display above
- [ ] Chat history is preserved during session (use `st.session_state`)
- [ ] Loading spinner while "agent is thinking"
- [ ] When agent code is not ready, show a placeholder response like: `"Agent not connected yet. Response will appear here."`

### Benchmark 4: Professional appearance
- [ ] Custom page title and favicon
- [ ] Sidebar navigation between pages
- [ ] Consistent color scheme (use the cyan/purple from presentation)
- [ ] No default Streamlit "Made with Streamlit" footer

---

## 🏗️ STEP-BY-STEP INSTRUCTIONS

### Step 1: Create basic app structure
```python
# app.py
import streamlit as st

st.set_page_config(
    page_title="EV Intelligence Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("⚡ EV Infrastructure & Policy Intelligence")
st.markdown("Navigate using the sidebar to explore data or chat with the AI agent.")
```

### Step 2: Create `.streamlit/config.toml`
```toml
[theme]
primaryColor = "#0891b2"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f8fafc"
textColor = "#1e293b"
font = "sans serif"

[server]
headless = true
```

### Step 3: Create `pages/1_Dashboard.py`
- Import `pandas` and read the Parquet file directly
- Path: `data/processed/Electric_Vehicle_Population_Data.parquet`
- Create 3 Plotly charts (bar, line, map)
- Use `st.plotly_chart(fig, use_container_width=True)`
- Add filter widgets: county dropdown, year range slider

### Step 4: Create `pages/2_Chat.py`
- Use `st.chat_message` and `st.chat_input` (Streamlit's built-in chat UI)
- Store conversation in `st.session_state.messages`
- When Person 4's agent is ready, call: `from scripts.agent_workflow import run_agent`
- Until then, use a placeholder function:
```python
def placeholder_agent(query):
    return f"🤖 Agent received your query: '{query}'. Agent integration pending."
```

### Step 5: Create `pages/3_About.py`
- Brief project description
- Team member names
- Tech stack pills (Ollama, LangGraph, Pinecone, etc.)
- Link to GitHub repo

---

## 📦 DELIVERABLE CHECKLIST

When you're done, run this self-check:

```
[ ] streamlit run app.py → runs without error
[ ] Dashboard page loads with 3 charts
[ ] Charts are interactive (hover, zoom)
[ ] At least 1 filter widget works (county dropdown or year slider)
[ ] Chat page has input box and message display
[ ] Chat history persists during session
[ ] Sidebar navigation works between all pages
[ ] App looks professional (not default Streamlit skeleton)
[ ] No hardcoded file paths — use relative paths from project root
[ ] All imports from other team members are wrapped in try/except
```

---

## ⚠️ COMMON PITFALLS TO AVOID

1. **Don't read CSV** — Always read the `.parquet` file. It's 10x faster.
2. **Don't install additional UI frameworks** — Stick with Streamlit + Plotly + Folium.
3. **Don't put business logic in the UI code** — The dashboard DISPLAYS results, it doesn't compute them. Analytics logic belongs in Person 2's tools.
4. **Don't hardcode absolute paths** — Use `os.path.join()` and relative paths.
