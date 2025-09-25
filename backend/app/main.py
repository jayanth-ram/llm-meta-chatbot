from __future__ import annotations

import os
from typing import AsyncIterator, Union

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

# ---- Config (with safe fallbacks if env/module not present) ----
try:
    from .config import CORS_ORIGIN, PORT  # type: ignore
except Exception:
    CORS_ORIGIN = os.getenv("CORS_ORIGIN", "*")
    PORT = int(os.getenv("PORT", "8000"))

# ---- Schemas & Brain (your modules) ----
# Expect ChatReq(message: str), ChatRes(reply: str, providers: list[str] | None)
from .schemas import ChatReq, ChatRes
from .brain import answer, stream_answer

app = FastAPI(title="LLM Meta Chatbot API", version="1.0")

# ---- CORS helpers ----
def _origins(value: Union[str, list[str]]) -> list[str]:
    # Accept "*", a single domain, comma-separated, or a list
    if isinstance(value, list):
        return value
    value = value.strip()
    if value == "*":
        return ["*"]
    if "," in value:
        return [v.strip() for v in value.split(",") if v.strip()]
    return [value]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins(CORS_ORIGIN),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Health ----
@app.get("/health")
def health():
    return {"status": "ok"}

# ---- Chat (non-streaming) ----
@app.post("/api/chat", response_model=ChatRes)
async def chat(req: ChatReq):
    msg = (req.message or "").strip()
    if not msg:
        raise HTTPException(status_code=422, detail="message must not be empty")
    reply, providers = await answer(msg)
    return ChatRes(reply=reply, providers=providers)

# ---- SSE/Streaming ----
@app.get("/api/chat/stream")
async def chat_stream(message: str, request: Request):
    msg = (message or "").strip()
    if not msg:
        raise HTTPException(status_code=422, detail="message must not be empty")

    async def sse_generator() -> AsyncIterator[Union[str, bytes]]:
        """
        Wraps chunks from stream_answer into SSE-friendly frames.
        Sends 'data: <chunk>\\n\\n'. If chunk already looks like SSE, pass through.
        Stops cleanly if client disconnects.
        """
        try:
            async for chunk in stream_answer(msg):
                if await request.is_disconnected():
                    break
                if isinstance(chunk, bytes):
                    # bytes -> assume caller already framed or wants raw bytes
                    yield chunk
                    continue
                # ensure str
                text = str(chunk)

                # If caller already provides SSE lines (data:/event:/: keep-alive), pass through
                starts_like_sse = text.startswith(("data:", "event:", ":"))
                if not starts_like_sse:
                    text = f"data: {text}"
                if not text.endswith("\n\n"):
                    text += "\n\n"
                yield text
        except Exception as e:
            # emit an SSE error event so client can surface it
            err = f"event: error\ndata: {type(e).__name__}: {e}\n\n"
            yield err

    return StreamingResponse(
        sse_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # disable proxy buffering if present
        },
    )
