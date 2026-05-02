# EV Analytics Dashboard — Docker Setup Guide

This guide provides instructions for setting up the EV Analytics Dashboard using Docker.

## Project Overview
The EV Analytics Dashboard is a comprehensive platform for analyzing Electric Vehicle adoption, forecasting future registrations, and optimizing charging station placement.

---

## 1. Role of Docker in this Project

Docker plays a critical role in the EV Intelligence Platform by providing a consistent and isolated environment for all its moving parts. Instead of manually installing complex dependencies like C-compilers for Prophet or managing local databases, Docker packages everything into "containers."

### Benefits:
- **Zero-Config Dependencies**: Packages like `Prophet` and `statsmodels` require specific system-level libraries. Docker handles this automatically.
- **Service Orchestration**: The app relies on several services (Ollama for AI, ChromaDB for vectors, Prometheus for metrics). Docker Compose spins them all up with a single command.
- **Portability**: Ensures the dashboard runs identically on Windows, macOS, and Linux.

### Services in Docker Compose:
- `ev_ollama`: Handles local LLM inference and embeddings.
- `ev_chromadb`: Local vector store for document retrieval.
- `ev_streamlit`: The main application service.
- `ev_prometheus`: Monitors application performance (optional).

---

## 2. Docker Setup Steps

### Prerequisites
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (8 GB RAM recommended)
- A [Pinecone](https://www.pinecone.io/) API key

### Steps
1. **Clone the Repo**
   ```bash
   git clone <repo-url>
   cd EV_Project
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env and set your PINECONE_API_KEY
   ```

3. **Start Services**
   ```bash
   docker compose up -d --build
   ```

4. **Pull LLM Models (First run only)**
   ```bash
   docker compose exec ollama ollama pull llama3.2
   docker compose exec ollama ollama pull nomic-embed-text
   ```

5. **Initialize Vector DB (First run only)**
   ```bash
   docker compose exec streamlit python scripts/setup_rag.py
   ```

6. **Open Dashboard**
   Navigate to `http://localhost:8501`.

---

## 3. Maintenance Commands

| Action | Command |
|--------|---------|
| Start Containers | `docker compose up -d` |
| Stop Containers | `docker compose down` |
| View Logs | `docker compose logs -f streamlit` |
| Run Tests | `docker compose run --rm streamlit pytest tests/ -v` |
| Reset Environment | `docker compose down -v` (Destructive: removes volumes) |
| Enable Monitoring | `docker compose --profile monitoring up -d` (Access at port 9090) |

---

## 4. Troubleshooting

- **Ollama connection refused**: Ensure the Ollama container is healthy (`docker compose ps`).
- **Port 8501 in use**: You can map a different port in `docker-compose.yml`.
- **Docker hangs on health checks**: Ollama needs ~90 seconds to initialize on the first run. Check logs with `docker compose logs ollama`.
