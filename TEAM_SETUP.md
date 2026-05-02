# Teammate Quickstart Guide

If you are joining this project, follow these steps to get everything running in minutes.

## 1. Prerequisites
Install these if you don't have them:
* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Required)
* [Git](https://git-scm.com/downloads)
* [VS Code](https://code.visualstudio.com/)

## 2. Setup Commands
Run these in your terminal from the folder where you want the project:

```bash
# Clone the repository
git clone <repo-url>
cd EV_Project

# Create your environment file
cp .env.example .env
# IMPORTANT: Open .env and add the PINECONE_API_KEY provided by the team

# Start the Docker containers
docker compose up -d --build

# Pull the AI models (Only required once)
docker compose exec ollama ollama pull llama3.2
docker compose exec ollama ollama pull nomic-embed-text

# Initialize the vector database
docker compose exec streamlit python scripts/setup_rag.py
```

## 3. Access the App
Once the commands finish:
* **Dashboard:** http://localhost:8501
* **Logs:** `docker compose logs -f streamlit` (to see if things are working)

## 4. Useful Commands
* **Stop everything:** `docker compose down`
* **Restart:** `docker compose restart streamlit`
* **Check status:** `docker compose ps`
