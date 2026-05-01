# ⚡ EV Intelligence Assistant: Washington State RAG

A professional-grade, cloud-ready AI Assistant and Data Dashboard for exploring Electric Vehicle adoption and policy in Washington State.

![EV Dashboard](https://img.shields.io/badge/Streamlit-Cloud-FF4B4B?style=for-the-badge&logo=Streamlit)
![Groq](https://img.shields.io/badge/LLM-Groq_Llama_3.1-orange?style=for-the-badge)
![Pinecone](https://img.shields.io/badge/Vector_DB-Pinecone-blue?style=for-the-badge)

## 🌟 Key Features
- **🤖 Hybrid RAG Chat**: Conversational AI powered by Groq (Cloud) and Ollama (Local) with context-aware retrieval from official WA policy documents.
- **📊 Dynamic Dashboard**: Interactive visualizations of EV registration trends, county breakdowns, and market share.
- **🔋 Policy Engine**: Instant answers on federal tax credits (IRA), state rebates, and ZEV mandates.
- **☁️ Zero-Cost Cloud Deployment**: Fully optimized for Streamlit Community Cloud using Sentence-Transformers for free embeddings.

## 🛠️ Tech Stack
- **Framework**: Streamlit
- **LLM Providers**: Groq (Cloud), Ollama (Local)
- **Vector Database**: Pinecone
- **Embeddings**: HuggingFace (all-MiniLM-L6-v2)
- **Data Processing**: Pandas, DuckDB

## 🚀 Getting Started

### 1. Prerequisites
- Python 3.10+
- [Ollama](https://ollama.com/) (Optional, for local execution)

### 2. Installation
```bash
git clone https://github.com/somildoshi12/EV_project.git
cd EV_project
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file in the root directory:
```env
PINECONE_API_KEY=your_pinecone_key
GROQ_API_KEY=your_groq_key
```

### 4. Run Locally
```bash
streamlit run streamlit_app.py
```

## 📁 Project Structure
- `streamlit_app.py`: Main Landing Page
- `pages/`: 
  - `1_Dashboard.py`: Analytics & Visualizations
  - `2_Chat.py`: AI Assistant Interface
- `scripts/`: Data processing and RAG pipeline logic
- `data/`: 
  - `raw/`: Source PDF documents
  - `processed/`: Cleaned datasets for analytics
  - `policy/`: Markdown-converted policy text

## 👥 Contributors
- **Somil Doshi**
- **Md**
