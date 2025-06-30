import asyncio
from typing import AsyncGenerator
from langchain_core.callbacks import AsyncCallbackHandler

class StreamHandler(AsyncCallbackHandler):
    """Collects tokens from an LLM and exposes them as an async generator."""

    def __init__(self):
        self.queue: asyncio.Queue[str | None] = asyncio.Queue()
        self.text = ""

    async def on_llm_new_token(self, token: str, **kwargs):
        self.text += token
        await self.queue.put(token)

    async def generator(self) -> AsyncGenerator[str, None]:
        while True:
            token = await self.queue.get()
            if token is None:
                break
            yield token

    async def close(self):
        await self.queue.put(None)
