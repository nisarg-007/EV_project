# PROJECT PROPOSAL: AI-Driven EV Infrastructure & Policy Intelligence System

| **Project Title** | EV Infrastructure & Policy Intelligence System |
| :--- | :--- |
| **Prepared For** | [Stakeholder Name / Organization] |
| **Prepared By** | Somil Doshi |
| **Date** | February 13, 2026 |
| **Version** | 1.0 (Final Draft) |

---

## 1. Executive Summary

### 1.1 Overview
This project proposes the development of an **AI-driven decision support system** designed to optimize Electric Vehicle (EV) infrastructure planning and policy analysis. By synthesizing **270,000+ EV registration records** with complex legal policy documents, the system aims to provide actionable intelligence to policymakers, utility companies, and urban planners.

### 1.2 Key Innovation
The core innovation is the integration of **Traditional Data Engineering** (ETL, Clustering) with **Generative AI** (Retrieval-Augmented Generation, Agentic Workflows). This hybrid approach bridges the gap between quantitative metrics (e.g., *adoption rates*) and qualitative constraints (e.g., *incentive eligibility*).

### 1.3 Operational Efficiency
To ensure data privacy and cost-efficiency, the system utilizes **Local Large Language Models (LLMs)** via Ollama. This architecture guarantees zero inference costs while maintaining strict data sovereignty, making it suitable for sensitive government or enterprise deployments.

---

## 2. Business Problem & Objectives

### 2.1 The Challenge
The rapid but uneven growth of EV adoption has created three critical issues:
1.  **Inefficient Infrastructure:** Capital allocation for charging stations often mismatches actual demand hotspots.
2.  **Grid Strain:** Utility providers lack granular visibility into localized load increases from new EV registrations.
3.  **Policy Complexity:** Stakeholders struggle to navigate the intricate web of federal and state incentives (e.g., CAFV eligibility), leading to underutilization of available funds.

### 2.2 Strategic Objectives
The proposed platform addresses these challenges by answering three strategic questions:
*   **Descriptive:** *Where is adoption growing fastest?* (Geospatial Analytics)
*   **Diagnostic:** *Why are specific regions lagging?* (Demographic Clustering)
*   **Prescriptive:** *What policy levers are available to accelerate growth?* (AI-Driven Recommendations)

---

## 3. Technical Architecture & Engineering Design

The system is architected as a modular, three-tier application: the **Data Lakehouse**, the **Intelligence Engine**, and the **Presentation Layer**.

### 3.1 Data Layer (The Foundation)
*   **Structured Data:**
    *   Ingestion of Washington State Department of Licensing (DOL) data (270k+ rows).
    *   Geospatial indexing using PostGIS or pre-computed GeoJSON.
*   **Unstructured Data:**
    *   PDF parsing of legislative bills, utility commission reports, and grant documentation.
*   **Vector Storage:**
    *   Implementation of **Pinecone (Serverless)** for semantic indexing of text chunks (768-dimensional embeddings).

### 3.2 Intelligence Engine (LangGraph & Ollama)
This is the system's "Brain," utilizing a stateful graph architecture to orchestrate workflows.
*   **Orchestration:** **LangGraph** manages the state of conversation, routing user queries to specialized agents.
*   **Local LLM Inference:** **Ollama (Llama 3 / Mistral)** handles reasonining and natural language generation on local hardware.
*   **Agentic Roles:**
    1.  **Router Agent:** Classifies intent (e.g., "Is this a data query or a policy question?").
    2.  **Data Analyst Agent:** Generates Python/Pandas code to query the structured dataset.
    3.  **Policy Expert Agent (RAG):** Retrieves and synthesizes legal text from the Vector DB.

### 3.3 Presentation Layer (UI)
*   **Framework:** **Streamlit** for rapid development of data-centric web applications.
*   **Visualization:** Interactive heatmaps (Folium) and dynamic charts (Plotly).
*   **Interaction:** A unified chat interface for hybrid queries (e.g., *"Show me the map of King County and explain the tax credits available there"*).

---

## 4. End-to-End Data Engineering Lifecycle

This project demonstrates a complete, industry-standard Data Engineering pipeline.

### 4.1 Architecture Diagram

```ascii
[ RAW SOURCES ]       [ ETL & PROCESSING ]          [ SERVING LAYER ]

   (CSV)               +------------------+         +-----------------+
EV Registrations  ---> |   Pandas ETL     |  ---->  |  Streamlit App  |
                       | (Clean, Feature) |         |  (Dash + Chat)  |
   (PDF)               +------------------+         +--------+--------+
Policy Docs       ---> |    LangChain     |                  ^
                       | (Chunk & Embed)  |                  |
                       +--------+---------+                  |
                                |                            |
                                v                            |
                       +--------+---------+         +--------+--------+
                       |    Pinecone      | <-----> |   LangGraph     |
                       |   (Vector DB)    |         |  Orchestrator   |
                       +------------------+         +-----------------+
```

### 4.2 Core Engineering Concepts Applied
1.  **ETL (Extract, Transform, Load):**
    *   **Extract:** Automated ingestion of government CSVs and PDF reports.
    *   **Transform:**
        *   *Imputation:* Handling missing vehicle metadata (MSRP/Range).
        *   *Normalization:* Standardizing geographic entities for SQL compatibility.
        *   *Feature Engineering:* Calculating `Adoption_Velocity` metrics per zip code.
    *   **Load:** Persisting optimized data structures for low-latency querying.

2.  **Vector Search & RAG:**
    *   **Semantic Indexing:** Moving beyond keyword search to semantic understanding using `nomic-embed-text` findings.
    *   **Context Window Management:** Optimizing chunk sizes (e.g., 500 tokens) for local model performance.

3.  **Stateful Orchestration:**
    *   Replacing brittle "if/else" logic with **Graph-based workflows** that can handle errors, loops, and conditional branching.

---

## 5. Implementation Roadmap

### Phase 1: Data Engineering & Foundation
*   **Goal:** Establish clean data pipelines and local AI environment.
*   **Deliverables:**
    *   Cleaned Parquet/CSV dataset.
    *   Populated Pinecone Vector Index.
    *   configured Ollama instance.

### Phase 2: Analytics & Modeling
*   **Goal:** Develop the deterministic tools for the AI agents.
*   **Deliverables:**
    *   K-Means Clustering model (identifying adoption hotspots).
    *   Python library of statistical functions (`get_growth_rate`, `compare_counties`).

### Phase 3: Intelligence Engine Development
*   **Goal:** Build and test the LangGraph workflow.
*   **Deliverables:**
    *   `Router` node for intent classification.
    *   `DataAnalyst` and `PolicyExpert` chains.
    *   Validated "Chat with Data" pipeline.

### Phase 4: Application Integration
*   **Goal:** Assemble the user interface.
*   **Deliverables:**
    *   Streamlit Dashboard with side-by-side Map and Chat.
    *   Integrated error handling and latency optimization.

---

## 6. Resource & Cost Analysis

The project is designed to be **highly cost-efficient**, utilizing Open Source software and Local Compute where possible.

| Component | Technology | Cost Tier | Notes |
| :--- | :--- | :--- | :--- |
| **Compute / Inference** | **Ollama** (Llama 3) | **$0.00** | Runs on local hardware (Mac M-Series recommeded). |
| **Orchestration** | **LangGraph** | **$0.00** | Open Source MIT License. |
| **Vector Database** | **Pinecone** | **$0.00** | Free Starter Tier (1 Index, 100k vectors). |
| **Frontend Storage** | **GitHub** | **$0.00** | Code repository and version control. |
| **Frontend Framework** | **Streamlit** | **$0.00** | Open Source framework. |
| **Development Time** | -- | -- | Estimated 4-6 weeks for MVP. |

### 6.1 Requirements
*   **Hardware:** Minimum 16GB RAM (Apple Silicon M-Series preferred for optimal inference speed).
*   **Software:** Python 3.10+, Docker (optional), Git.

---

## 7. Conclusion
This proposal outlines a robust, future-proof architecture for analyzing the EV transition. By marrying **hard data engineering** with **agentic AI**, the system offers a level of interactivity and insight that traditional static dashboards cannot match. The use of **Local LLMs** ensures it remains a privacy-first, zero-cost solution suitable for academic or governmental prototyping.
