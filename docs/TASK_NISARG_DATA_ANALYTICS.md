# 📊 NISARG — Data Engineering & Analytics

**Role:** Data Analyst / ML Engineer  
**Branch Name:** `Nisarg`  
**Estimated Time:** 12-15 hours

---

## 🚨 FILE RESTRICTIONS — READ CAREFULLY

### ✅ Files you CAN create/edit:
```
scripts/analytics_tools.py      ← Add more DuckDB tool functions (EDIT)
notebooks/                      ← Create this folder (CREATE)
  notebooks/01_EDA.ipynb        ← Exploratory Data Analysis (CREATE)
  notebooks/02_clustering.ipynb ← K-Means clustering analysis (CREATE)
data/processed/                 ← Can add new processed datasets here
  data/processed/ev_with_clusters.parquet  ← Output from clustering (CREATE)
```

### 🚫 Files you MUST NOT edit:
```
app.py, pages/                  ← Somil owns this
scripts/setup_rag.py            ← Parva owns this
scripts/agent_workflow.py       ← MD owns this
tests/                          ← Smit owns this
docs/                           ← Somil & Smit own this
data/raw/                       ← Parva owns this
```

---

## 📋 TASK DESCRIPTION

You are the **data backbone** of this project. Your job is to:

1. **Explore and understand** the 276k-row WA DOL dataset thoroughly
2. **Build deterministic analytics tools** (Python functions using DuckDB) that the LangGraph agent will call
3. **Run K-Means clustering** to identify EV adoption hotspots and charger demand gaps
4. **Document findings** in Jupyter notebooks that can be shown during the demo

The existing `analytics_tools.py` has 2 basic functions. You need to expand this to **at least 8 tool functions** that cover the questions stakeholders would actually ask.

---

## 🎯 MINIMUM BENCHMARKS (Must achieve ALL)

### Benchmark 1: Complete EDA notebook
- [ ] Load the Parquet file, display `.shape`, `.dtypes`, `.describe()`
- [ ] Document: How many unique counties? Zip codes? Makes? Models?
- [ ] Visualize: Top 15 counties by EV count (bar chart)
- [ ] Visualize: EV adoption trend by model year (line chart)
- [ ] Visualize: BEV vs PHEV distribution (pie chart)
- [ ] Visualize: CAFV eligibility breakdown (bar chart)
- [ ] Identify and document any missing/null values
- [ ] Export a summary statistics table

### Benchmark 2: K-Means clustering notebook
- [ ] Select features: County, Zip Code, EV count per zip, avg model year, BEV ratio
- [ ] Use the Elbow Method to determine optimal K (test K=3 to K=10)
- [ ] Run K-Means with optimal K
- [ ] Visualize clusters on a scatter plot (or map if lat/lon available)
- [ ] Interpret each cluster (e.g., "Cluster 1 = High adoption, new vehicles, urban")
- [ ] Save the clustered data as `data/processed/ev_with_clusters.parquet`

### Benchmark 3: At least 8 tool functions in analytics_tools.py
Every function must:
- Take a `parquet_path` parameter with a default value
- Return a `pd.DataFrame`
- Use `duckdb.query()` for SQL execution
- Have a clear docstring explaining what it does

### Benchmark 4: All functions work independently
```bash
cd EV_project
python scripts/analytics_tools.py
# Must print sample output from all tools without error
```

---

## 🏗️ REQUIRED TOOL FUNCTIONS

You already have `get_ev_counts_by_county()` and `get_adoption_growth_rate()`. Add these:

### Function 3: `get_ev_counts_by_zipcode(county=None)`
Return EV count per zip code. If county is provided, filter to that county only.

### Function 4: `get_top_makes_and_models(top_n=10)`
Return the most popular EV makes and models with their counts.

### Function 5: `get_bev_vs_phev_breakdown(county=None)`
Return count of Battery Electric vs Plug-in Hybrid by county or overall.

### Function 6: `get_cafv_eligibility_summary()`
Return counts for each CAFV eligibility status:
- "Clean Alternative Fuel Vehicle Eligible"
- "Eligibility unknown as battery range has not been researched"
- "Not eligible due to low battery range"

### Function 7: `get_ev_range_statistics(make=None)`
Return average, min, max electric range by make or overall.

### Function 8: `get_newest_registrations(top_n=20)`
Return the most recent model year vehicles with their details.

### Function 9: `get_utility_provider_summary()`
Return EV count grouped by Electric Utility provider — this helps utilities understand their exposure.

### Function 10: `get_county_growth_comparison(county1, county2)`
Compare two counties' adoption timelines side by side.

---

## 📦 COLUMN REFERENCE

The Parquet file has these columns (use exact names with double quotes in DuckDB SQL):
```
"VIN (1-10)", "County", "City", "State", "Postal Code",
"Model Year", "Make", "Model", "Electric Vehicle Type",
"Clean Alternative Fuel Vehicle (CAFV) Eligibility",
"Electric Range", "Base MSRP", "Legislative District",
"DOL Vehicle ID", "Vehicle Location", "Electric Utility",
"2020 Census Tract"
```

---

## 📦 DELIVERABLE CHECKLIST

```
[ ] notebooks/01_EDA.ipynb runs top-to-bottom without error
[ ] notebooks/02_clustering.ipynb runs top-to-bottom without error
[ ] At least 6 visualizations in EDA notebook
[ ] K-Means with Elbow Method plot
[ ] Cluster interpretation documented in notebook
[ ] ev_with_clusters.parquet saved in data/processed/
[ ] analytics_tools.py has 8+ functions
[ ] python scripts/analytics_tools.py runs without error
[ ] Every function has a docstring
[ ] No hardcoded absolute paths
```

---

## ⚠️ COMMON PITFALLS TO AVOID

1. **Don't use `pd.read_parquet()` in tool functions** — Use `duckdb.query()` instead. DuckDB reads Parquet 5-10x faster than Pandas for SQL queries.
2. **Don't create new Python files** — All tool functions go in `analytics_tools.py`. Person 4 needs to import from ONE file.
3. **Column names have spaces** — Always use `"Column Name"` with double quotes inside DuckDB SQL strings.
4. **Don't overwrite the original Parquet** — Save clustered output as a NEW file.
