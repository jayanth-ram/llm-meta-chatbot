# llm-meta-chatbot

![diagram](https://raw.githubusercontent.com/jayanth-ram/llm-meta-chatbot/main/docs/diagram.png)

## Architecture

Browser → FastAPI → (fallback/router/ensemble) → OpenAI/Gemini; plus SSE path.

## Quickstart (local)

### Backend
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp backend/.env.example backend/.env  # fill keys
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
npm create vite@latest frontend -- --template react
cd frontend && npm install
echo "VITE_API_BASE=http://localhost:8000" > .env.local
npm run dev
```

## Curl sample
```bash
curl -s -X POST http://localhost:8000/api/chat -H "Content-Type: application/json" -d '{"message":"Explain JWT in 2 lines"}'
```

## SSE sample
Use EventSource in StreamChat.jsx, or:
```bash
curl -N "http://localhost:8000/api/chat/stream?message=hello"
```

## Deploy
- Backend on **Railway** (rootDir=backend). Ensure PORT binding.
- Frontend on Vercel; set VITE_API_BASE to Railway URL.

### Railway steps
1. Push repo to GitHub.
2. On Railway, "New Project" → "Deploy from GitHub" → select repo; set Root directory = backend.
3. Add environment variables: OPENAI_API_KEY, GOOGLE_API_KEY, MODE, TIMEOUT_SECS, CORS_ORIGIN.
4. Deploy; note the public URL (e.g., https://llm-meta-chatbot.up.railway.app).

## Modes
- **fallback**: try OpenAI, fallback to Gemini on error.
- **router**: route by heuristic (code/math → OpenAI, creative/vision → Gemini).
- **ensemble**: query both, merge results.

## Notes
- Rate limits, retries/backoff, cost & latency tradeoffs.

## Roadmap
- Redis cache
- Auth/rate limiting
- RAG grounding
- Provider metrics