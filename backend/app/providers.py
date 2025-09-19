import httpx
from .config import OPENAI_API_KEY, GOOGLE_API_KEY, OPENAI_MODEL, GEMINI_MODEL, TIMEOUT_SECS

OPENAI_URL = "https://api.openai.com/v1/chat/completions"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
GEMINI_STREAM_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent"

async def call_openai(prompt: str) -> str:
    if not OPENAI_API_KEY:
        return "OpenAI provider not configured."
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": OPENAI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    async with httpx.AsyncClient(timeout=TIMEOUT_SECS) as client:
        try:
            resp = await client.post(OPENAI_URL, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            return f"OpenAI error: {str(e)}"

async def call_gemini(prompt: str) -> str:
    if not GOOGLE_API_KEY:
        return "Gemini provider not configured."
    url = GEMINI_URL.format(model=GEMINI_MODEL)
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    async with httpx.AsyncClient(timeout=TIMEOUT_SECS) as client:
        try:
            resp = await client.post(f"{url}?key={GOOGLE_API_KEY}", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"Gemini error: {str(e)}"

async def stream_openai(prompt: str):
    if not OPENAI_API_KEY:
        yield "OpenAI provider not configured."
        return
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": OPENAI_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }
    async with httpx.AsyncClient(timeout=TIMEOUT_SECS) as client:
        try:
            async with client.stream("POST", OPENAI_URL, headers=headers, json=payload) as resp:
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        chunk = httpx.Response(200, content=data).json()
                        delta = chunk["choices"][0]["delta"].get("content", "")
                        if delta:
                            yield delta
        except Exception as e:
            yield f"OpenAI stream error: {str(e)}"

async def stream_gemini(prompt: str):
    if not GOOGLE_API_KEY:
        yield "Gemini provider not configured."
        return
    # Gemini streaming endpoint may not be available; fallback to chunking
    text = await call_gemini(prompt)
    for i in range(0, len(text), 32):
        yield text[i:i+32]
