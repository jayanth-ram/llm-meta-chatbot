import json
from typing import AsyncGenerator

def sse_event(event: str, data: str) -> str:
    return f"event: {event}\ndata: {data}\n\n"

async def sse_stream(generator: AsyncGenerator[str, None]):
    async for chunk in generator:
        yield chunk
