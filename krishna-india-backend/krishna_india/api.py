import asyncio
import os
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse

from .utils import get_openai_client, load_history, append_history
from .streaming import StreamHandler

app = FastAPI(title="Krishna India API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_ORIGIN", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = get_openai_client()
MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
DUMMY_MODE = os.environ.get("OPENAI_API_KEY") == "dummy"

@app.post("/chat")
async def chat(message: str, session_id: str):
    history = load_history(session_id)
    messages = history + [{"role": "user", "content": message}]
    if DUMMY_MODE:
        reply = "test reply"
    else:
        response = await client.chat.completions.create(model=MODEL, messages=messages)
        reply = response.choices[0].message.content
    append_history(session_id, "user", message)
    append_history(session_id, "assistant", reply)
    return {"reply": reply}

@app.get("/stream")
async def stream(message: str = Query(...), session_id: str = Query(...)):
    history = load_history(session_id)
    messages = history + [{"role": "user", "content": message}]
    handler = StreamHandler()

    async def run_llm():
        if DUMMY_MODE:
            for tok in ["test", " ", "stream"]:
                await handler.on_llm_new_token(tok)
            await handler.close()
        else:
            await client.chat.completions.create(
                model=MODEL,
                messages=messages,
                stream=True,
                extra_headers={"Accept": "text/event-stream"},
                callbacks=[handler],
            )
            await handler.close()
        append_history(session_id, "user", message)
        append_history(session_id, "assistant", handler.text)

    async def event_generator():
        task = asyncio.create_task(run_llm())
        async for token in handler.generator():
            yield token
        await task

    return EventSourceResponse(event_generator())
