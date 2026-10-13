# Trade Copilot Technical Guide
# ==================================

## Architecture Overview
Trade Copilot is built as a decoupled system:
- **Frontend**: Next.js (App Router) with Tailwind CSS and Framer Motion.
- **Backend**: FastAPI (Python) using an asynchronous architecture.
- **Data Layer**: PostgreSQL (relational data) and ChromaDB (vector storage for RAG).
- **Workers**: Celery + Redis for durable background document processing.

## AI Pipeline
The AI layer uses a gateway pattern (`LLMService`) allowing seamless switching between Ollama (local) and OpenAI (cloud). 
- **Streaming**: Responses are streamed via Server-Sent Events (SSE).
- **Grounding**: Documents are indexed into ChromaDB; the chat service retrieves relevant excerpts to ground the LLM response.

## Deployment
1. Run `docker compose up -d` to start the data services.
2. Install backend dependencies: `pip install -r requirements.txt`.
3. Run the backend: `uvicorn main:app --reload`.
4. Run the frontend: `npm install && npm run dev`.
