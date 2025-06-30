from fastapi import FastAPI, UploadFile, File, Form, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from typing import List, Dict, Any

# import from backend package to avoid ModuleNotFoundError
# utils will be imported lazily inside routes
from streaming import StreamHandler

app = FastAPI(title="Chatbot API", openapi_url="/openapi.json", docs_url="/docs")

# allow Next.js dev server
origins = ["http://localhost:3000"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str
    history: List[Dict[str, str]] | None = None
    db_uri: str | None = None


def stream_text(text: str):
    async def event_generator():
        for token in text.split():
            yield {"event": "token", "data": token + " "}
        yield {"event": "end", "data": ""}
    return EventSourceResponse(event_generator())


@app.post("/chat/basic")
async def chat_basic(req: ChatRequest):
    from backend import utils
    from langchain.chains import ConversationChain
    llm = utils.configure_llm()
    chain = ConversationChain(llm=llm, verbose=False)
    out = chain.invoke({"input": req.message})
    return stream_text(out["response"])


@app.post("/chat/sql")
async def chat_sql(req: ChatRequest):
    from backend import utils
    from langchain_community.utilities.sql_database import SQLDatabase
    from langchain_community.agent_toolkits import create_sql_agent
    llm = utils.configure_llm()
    db = SQLDatabase.from_uri(req.db_uri or "sqlite:///assets/movie.db")
    agent = create_sql_agent(llm=llm, db=db, verbose=False)
    out = agent.invoke({"input": req.message})
    return stream_text(out["output"])


@app.post("/chat/web")
async def chat_web(req: ChatRequest):
    from backend import utils
    from langchain_community.tools import DuckDuckGoSearchRun
    search = DuckDuckGoSearchRun()
    result = search.run(req.message)
    return {"messages": [{"role": "assistant", "text": result}]}


@app.post("/chat/advisory")
async def chat_advisory(message: str = Form(...), file: UploadFile = File(...)):
    from backend import utils
    from langchain_community.document_loaders import PyPDFLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.vectorstores import DocArrayInMemorySearch
    from langchain.chains import ConversationalRetrievalChain
    from langchain.memory import ConversationBufferMemory

    llm = utils.configure_llm()
    path = f"/tmp/{file.filename}"
    with open(path, "wb") as f:
        f.write(await file.read())

    loader = PyPDFLoader(path)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(docs)
    vectordb = DocArrayInMemorySearch.from_documents(chunks, utils.configure_embedding_model())
    retriever = vectordb.as_retriever(search_type="mmr", search_kwargs={"k":2,"fetch_k":4})
    memory = ConversationBufferMemory(return_messages=True, memory_key="chat_history")
    chain = ConversationalRetrievalChain.from_llm(llm, retriever=retriever, memory=memory)
    out = chain.invoke({"question": message})
    return {"messages": [{"role": "assistant", "text": out["answer"]}]}


@app.post("/chat/multi")
async def chat_multi(req: ChatRequest):
    # placeholder: combine sql + web search
    from backend import utils
    from langchain_community.utilities.sql_database import SQLDatabase
    from langchain_community.agent_toolkits import create_sql_agent
    from langchain_community.tools import DuckDuckGoSearchRun
    from langchain.chains import ConversationChain

    llm = utils.configure_llm()
    db = SQLDatabase.from_uri(req.db_uri or "sqlite:///assets/movie.db")
    agent = create_sql_agent(llm=llm, db=db, verbose=False)
    sql_out = agent.invoke({"input": req.message})
    search = DuckDuckGoSearchRun()
    web_out = search.run(req.message)
    chain = ConversationChain(llm=llm, verbose=False)
    final = chain.invoke({"input": f"SQL: {sql_out['output']}\nWeb: {web_out}"})
    return stream_text(final["response"])


@app.websocket("/ws/chat")
async def websocket_chat(ws: WebSocket):
    await ws.accept()
    try:
        while True:
            data = await ws.receive_text()
            from backend import utils
            from langchain.chains import ConversationChain
            llm = utils.configure_llm()
            chain = ConversationChain(llm=llm, verbose=False)
            out = chain.invoke({"input": data})
            await ws.send_text(out["response"])
    except WebSocketDisconnect:
        pass

