from fastapi import FastAPI
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from .config import CORS_ORIGIN, PORT
from .schemas import ChatReq, ChatRes
from .brain import answer, stream_answer
import anyio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[CORS_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/chat", response_model=ChatRes)
async def chat(req: ChatReq):
    reply, providers = await answer(req.message)
    return ChatRes(reply=reply, providers=providers)

@app.get("/api/chat/stream")
async def chat_stream(message: str, request: Request):
    async def event_generator():
        async for chunk in stream_answer(message):
            yield chunk
            if await request.is_disconnected():
                break
    return StreamingResponse(event_generator(), media_type="text/event-stream")
