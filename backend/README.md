# Math Routing Agent: Backend

## Setup

1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and fill in your API keys.
3. Start Qdrant and MCP server:
   ```sh
   docker-compose up -d
   ```
4. Run FastAPI backend:
   ```sh
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## Endpoints
- `/api/kb_search` — Knowledge base search (Qdrant)
- `/api/web_search` — Web search (MCP Tavily)
- `/api/feedback` — Human-in-the-loop feedback
- `/api/generate_proposal_pdf` — Generate PDF proposal

## Agent Pipeline
- See `agent_pipeline.py` for LangGraph agent setup (to be implemented)

## Data
- Use `normalize_datasets.py` and `embed_kb.py` to prepare and upload KB

---

# Math Routing Agent: Frontend

## Setup

1. (To be initialized with Vite + shadcn/ui)
2. Connect to backend at `http://localhost:8000`

---

# Infrastructure
- Qdrant: http://localhost:6333
- MCP Tavily: http://localhost:8080
- FastAPI: http://localhost:8000
- React: http://localhost:5173 (default Vite)
