from .providers import call_openai, call_gemini, stream_openai, stream_gemini
from .config import MODE
import anyio

# Heuristic router
CODE_KEYWORDS = ["code", "sql", "math", "python", "function", "algorithm"]
CREATIVE_KEYWORDS = ["creative", "marketing", "vision", "story", "brand", "design"]

def route_model(prompt: str) -> str:
    p = prompt.lower()
    if any(k in p for k in CODE_KEYWORDS):
        return "openai"
    if any(k in p for k in CREATIVE_KEYWORDS):
        return "gemini"
    return "openai"

async def answer(prompt: str):
    providers = []
    if MODE == "fallback":
        res = await call_openai(prompt)
        if "error" in res.lower() or "not configured" in res.lower():
            res2 = await call_gemini(prompt)
            providers = ["gemini"] if "not configured" not in res2.lower() else []
            return res2, providers
        providers = ["openai"]
        return res, providers
    elif MODE == "router":
        model = route_model(prompt)
        if model == "openai":
            res = await call_openai(prompt)
            providers = ["openai"]
        else:
            res = await call_gemini(prompt)
            providers = ["gemini"]
        return res, providers
    elif MODE == "ensemble":
        async def get_openai():
            return await call_openai(prompt)
        async def get_gemini():
            return await call_gemini(prompt)
        res_openai, res_gemini = await anyio.gather(get_openai(), get_gemini())
        providers = []
        if "not configured" not in res_openai.lower():
            providers.append("openai")
        if "not configured" not in res_gemini.lower():
            providers.append("gemini")
        if all("error" not in r.lower() and "not configured" not in r.lower() for r in [res_openai, res_gemini]):
            merged = f"[OpenAI]\n{res_openai}\n---\n[Gemini]\n{res_gemini}"
            return merged[:200], providers
        elif "error" not in res_openai.lower() and "not configured" not in res_openai.lower():
            return res_openai, ["openai"]
        elif "error" not in res_gemini.lower() and "not configured" not in res_gemini.lower():
            return res_gemini, ["gemini"]
        else:
            return "No provider succeeded.", []

async def stream_answer(prompt: str):
    from .sse import sse_event
    providers = []
    if MODE in ["fallback", "router"]:
        model = route_model(prompt) if MODE == "router" else "openai"
        gen = stream_openai(prompt) if model == "openai" else stream_gemini(prompt)
        async for chunk in gen:
            yield sse_event("chunk", chunk)
        providers = [model]
    elif MODE == "ensemble":
        # Run both, buffer, then stream merged
        async def get_openai():
            return "".join([c async for c in stream_openai(prompt)])
        async def get_gemini():
            return "".join([c async for c in stream_gemini(prompt)])
        res_openai, res_gemini = await anyio.gather(get_openai(), get_gemini())
        providers = []
        if res_openai and "not configured" not in res_openai.lower():
            providers.append("openai")
        if res_gemini and "not configured" not in res_gemini.lower():
            providers.append("gemini")
        merged = f"[OpenAI]\n{res_openai}\n---\n[Gemini]\n{res_gemini}"
        for i in range(0, min(len(merged), 200), 32):
            yield sse_event("chunk", merged[i:i+32])
    yield sse_event("done", str({"providers": providers}))
