"""FastAPI version of the original Streamlit chatbot."""
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from typing import List, Dict, AsyncGenerator

import utils
from streaming import StreamHandler
from langchain.chains import ConversationChain, ConversationalRetrievalChain
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_core.documents.base import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
import aiohttp
import asyncio

app = FastAPI(title="Chat Backend", openapi_url="/openapi.json")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm = utils.configure_llm()
embed_model = utils.configure_embedding_model()

# --- Helpers ---------------------------------------------------------------
async def stream_response(text: str) -> AsyncGenerator[str, None]:
    for token in text.split():
        yield f"data: {token}\n\n"
        await asyncio.sleep(0.01)

# --- Routes ----------------------------------------------------------------
@app.post("/chat/basic")
# Ported from ConversationChain logic in Streamlit app
async def chat_basic(data: Dict[str, str]):
    chain = ConversationChain(llm=llm, verbose=False)
    prompt = data.get("message", "")
    result = chain.invoke({"input": prompt})
    return {"messages": [{"role": "assistant", "text": result["response"]}]}

@app.post("/chat/sql")
# Ported from SqlChatbot class
async def chat_sql(data: Dict[str, str]):
    db = SQLDatabase.from_uri("sqlite:///assets/movie.db")
    agent = create_sql_agent(llm=llm, db=db)
    query = data.get("message", "")
    result = agent.invoke({"input": query})
    return {"messages": [{"role": "assistant", "text": result["output"]}]}

@app.post("/chat/web")
# Ported from InternetChatbot
async def chat_web(data: Dict[str, str]):
    tool = DuckDuckGoSearchRun()
    query = data.get("message", "")
    result = tool.run(query)
    return {"messages": [{"role": "assistant", "text": result}]}

@app.post("/chat/advisory")
# Ported from CustomDocChatbot
async def chat_advisory(file: UploadFile = File(...), request: Request = None):
    content = await file.read()
    doc = Document(page_content=content.decode("utf-8", errors="ignore"))
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents([doc])
    vectordb = DocArrayInMemorySearch.from_documents(chunks, embed_model)
    retriever = vectordb.as_retriever()
    chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever)
    data = await request.form()
    message = data.get("message", "")
    result = chain.invoke({"question": message})
    return {"messages": [{"role": "assistant", "text": result["answer"]}]}

@app.post("/chat/multi")
# Ported from MultiSourceChatbot
async def chat_multi(data: Dict[str, str]):
    query = data.get("message", "")
    # Combine SQL, web search, and document retrieval
    web = DuckDuckGoSearchRun().run(query)
    db = SQLDatabase.from_uri("sqlite:///assets/movie.db")
    agent = create_sql_agent(llm=llm, db=db)
    sql_ans = agent.invoke({"input": query})["output"]
    combined = f"SQL: {sql_ans}\nWeb: {web}"
    return {"messages": [{"role": "assistant", "text": combined}]}

@app.post("/stream")
# Example streaming endpoint
async def stream_demo(data: Dict[str, str]):
    text = data.get("message", "")
    generator = stream_response(text)
    return EventSourceResponse(generator)

