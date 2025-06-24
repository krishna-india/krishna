import streamlit as st
from PIL import Image, UnidentifiedImageError
import os
import utils
import auth
import bcrypt
import time
import validators
import requests
import traceback
import asyncio
import aiohttp
import sqlite3
from pathlib import Path
from sqlalchemy import create_engine
from bs4 import BeautifulSoup

try:
    from googlesearch import search
except ImportError:
    st.error("Install googlesearch-python: pip install googlesearch-python")
    raise

# LangChain imports
from streaming import StreamHandler
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.documents.base import Document
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain import hub
from langchain_openai import ChatOpenAI
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent, AgentType
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.callbacks import StreamlitCallbackHandler

# -------------------------
# Application Setup & Theme
# -------------------------
st.set_page_config(page_title="Search Markets Chatbot", page_icon="💬", layout="wide")
auth.init_db()

# Custom CSS for enhanced theme and readability
# ─────────────────────────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* Main background + padding */
    .reportview-container, .main {
        background-color: #202021 !important;
        padding: 1rem !important;
    }


    /* Sidebar background and text */
    [data-testid="stSidebar"] {
        background-color: #003366 !important;
        color: #ffffff !important;
        padding-top: 1rem !important;
        width: 260px !important;
    }
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] .block-container,
    [data-testid="stSidebar"] .stRadio > div > label,
    [data-testid="stSidebar"] .stButton > button {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] .stRadio > div > div[data-baseweb="radio"] {
        margin-bottom: 0.5rem !important;
    }

    /* Headers */
    h1, h2, h3, h4 {
        color: #ffffff !important;
        margin-top: 1rem !important;
        margin-bottom: 0.5rem !important;
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif !important;
    }

    /* Chat messages */
    .stChatMessage > div {
        background-color: #e8f0fe !important;
        color: #003366 !important;
        border-radius: 8px !important;
        padding: 0.75rem !important;
    }

    /* Chat input box styling */
    .stTextInput > div > input {
        border: 1px solid #ffffff !important;
        border-radius: 4px !important;
        padding: 0.5rem !important;
        background-color: #003366 !important;
    }

    /* Buttons */
    .stButton > button {
        background-color: #0055a5 !important;
        color: #ffffff !important;
        border-radius: 4px !important;
        padding: 0.5rem 1rem !important;
    }
    .stButton > button:hover {
        background-color: #004080 !important;
    }

    /* Captions */
    .stCaption {
        font-size: 0.8rem !important;
        color: #555555 !important;
    }


    /* Placeholder text */
    [data-testid="stChatInput"] .public-DraftEditorPlaceholder-root {
        color: rgba(255,255,255,0.6) !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Require user authentication before showing the app
auth.require_login()


# -------------------------
# Sidebar: Logo & Navigation
# -------------------------
logo_path = r"C:\Users\ROG\Desktop\SearchMarket\updated cod\logo.png"
if os.path.exists(logo_path):
    try:
        logo = Image.open(logo_path)
        st.sidebar.image(logo, width=120)
    except UnidentifiedImageError:
        st.sidebar.error(f"⚠️ Could not identify logo at {logo_path}")
else:
    st.sidebar.error(f"⚠️ Logo not found at {logo_path}")

st.sidebar.markdown("## Search Markets Chatbot")
page = st.sidebar.radio(
    "Navigate to:",
    [
        "Home",
        "Search Markets GPT",
        "SM Data GPT",
        "SM Web GPT",
        "SM Net GPT",
        "SM Advisory GPT"
    ],
    key="NAV_MENU"
)
auth.logout_button()

# Sidebar spacing tweak
st.markdown(
    """
    <style>
      [data-testid="stSidebar"] > div:first-child { padding-top: 0.5rem; }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize chat history
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# -------------------------
# Configure LLM & Embedding (once)
# -------------------------
# Only call configure_llm() a single time to avoid duplicate widget keys
llm = utils.configure_llm(widget_key="SELECTED_LLM_GLOBAL")
embed_model = utils.configure_embedding_model()

# -------------------------
# SqlChatbot Class (for SM Data GPT page)
# -------------------------
class SqlChatbot:
    def __init__(self, llm_instance):
        utils.sync_st_session()
        # Reuse the already-configured LLM to prevent duplicate radio widgets
        self.llm = utils.configure_llm(widget_key="SELECTED_LLM_SM Data GPT")

    def setup_db(self, db_uri: str) -> SQLDatabase:
        if db_uri == 'USE_SAMPLE_DB':
            # assets folder is alongside app.py
            db_filepath = (Path(__file__).parent / "assets" / "output.db").absolute()
            if not db_filepath.exists():
                st.error(f"⚠️ Sample database not found at:\n{db_filepath}")
                st.stop()
            # Use forward slashes in URI
            uri_path = db_filepath.as_posix()
            # SQLite in read-only mode via creator
            creator = lambda: sqlite3.connect(f"file:{uri_path}?mode=ro", uri=True)
            engine = create_engine("sqlite:///", creator=creator)
            db = SQLDatabase(engine)
        else:
            try:
                db = SQLDatabase.from_uri(database_uri=db_uri)
            except Exception as e:
                st.error(f"❌ Could not connect to provided URI:\n{e}")
                st.stop()

        with st.sidebar.expander('Database tables', expanded=True):
            try:
                tables = db.get_usable_table_names()
            except Exception:
                tables = []
            st.info('\n- ' + '\n- '.join(tables))
        return db

    def setup_sql_agent(self, db: SQLDatabase):
        agent = create_sql_agent(
            llm=self.llm,
            db=db,
            top_k=180,
            verbose=False,
            agent_type="openai-tools",
            handle_parsing_errors=True,
            handle_sql_errors=True
        )
        return agent

    @utils.enable_chat_history
    def main(self):
        st.subheader("📂 SQL Database Chat")

        # Option: sample DB or custom URI
        radio_opt = ['Use sample db - data.db', 'Connect to your SQL db']
        selected_opt = st.sidebar.radio(
            label='Choose an option',
            options=radio_opt,
            key="SM Data GPT_CHOICE"
        )

        if radio_opt.index(selected_opt) == 1:
            with st.sidebar.expander('⚠️ Security note', expanded=True):
                warning = (
                    "Building Q&A systems on SQL databases requires executing model-generated SQL queries. "
                    "There are inherent risks in doing this. Make sure that your database connection permissions "
                    "are scoped as narrowly as possible for your chain/agent's needs.\n\n"
                    "For more on general security best practices - "
                    "[read this](https://python.langchain.com/docs/security)."
                )
                st.warning(warning)

            db_uri = st.sidebar.text_input(
                label='Database URI',
                placeholder='e.g., mysql://user:pass@hostname:port/db',
                key='SM Data GPT_URI'
            )
        else:
            db_uri = 'USE_SAMPLE_DB'

        if not db_uri:
            st.error("Please enter a database URI to continue.")
            st.stop()

        db = self.setup_db(db_uri)
        agent = self.setup_sql_agent(db)

        user_query = st.chat_input(placeholder="Ask me anything about your database...", key='SQL_CHAT_INPUT')
        if user_query:
            st.session_state['messages'].append({"role": "user", "content": user_query})
            st.chat_message("user").write(user_query)

            with st.chat_message("assistant"):
                st_cb = StreamlitCallbackHandler(st.container())
                result = agent.invoke(
                    {"input": user_query},
                    {"callbacks": [st_cb]}
                )
                response = result["output"]
                st.session_state['messages'].append({"role": "assistant", "content": response})
                st.write(response)
                utils.print_qa(SqlChatbot, user_query, response)

# -------------------------
# Page: Home
# -------------------------
if page == "Home":
    st.header("Welcome to the Search Markets Chatbot")
    st.write(
        """
        **Discover multiple levels of AI-driven chat services in one place.**  
        - **Search Markets GPT**: Free conversational AI for all visitors.  
        - **SM Data GPT**: Connect your SQL database or query our specialized Search Markets dataset (paid/subscription).  
        - **SM Web GPT**: Get real-time, web-sourced answers (premium).    
        - **SM Net GPT**: Combine website, SQL, and internet data for the most comprehensive answers (premium).  
        - **SM Advisory GPT**: One-on-one expert guidance and insights (chargeable).
        """
    )

# -------------------------
# Page: Search Markets GPT
# -------------------------
elif page == "Search Markets GPT":
    st.header("Search Markets GPT")
    st.write("Interact with a simple conversational LLM. Free for all visitors.")

    utils.sync_st_session()
    chain = ConversationChain(llm=llm, verbose=False)

    user_query = st.chat_input("Ask me anything!", key='BASIC_QUERY')
    if user_query:
        utils.display_msg(user_query, 'user')
        with st.chat_message("assistant"):
            handler = StreamHandler(st.empty())
            result = chain.invoke({"input": user_query}, {"callbacks": [handler]})
            response = result["response"]
            st.session_state['messages'].append({"role": "assistant", "content": response})
            utils.print_qa(ConversationChain, user_query, response)

# -------------------------
# Page: SM Data GPT
# -------------------------
elif page == "SM Data GPT":
    # Instantiate and run the SqlChatbot class, passing in the already-configured llm
    sql_bot = SqlChatbot(llm_instance=llm)
    sql_bot.main()

# -------------------------
# Page: Internet (Premium)
# -------------------------
elif page == "SM Web GPT":
    st.header("SM Web GPT")
    st.write("Premium service: Get answers about recent events using live web search tools.")

    def safe_free_search(query: str, max_results: int = 5) -> str:
        """
        1. Try googlesearch-python signature: search(query, num_results=…)
        2. Fallback to original googlesearch signature: search(query, stop=…)
        3. Scrape each URL for title + snippet and return markdown.
        """
        try:
            urls = search(query, num_results=max_results)
        except TypeError:
            urls = search(query, stop=max_results, pause=1.0)

        entries = []
        headers = {"User-Agent": "Mozilla/5.0"}
        for url in urls:
            title = url
            snippet = ""
            try:
                resp = requests.get(url, headers=headers, timeout=5)
                soup = BeautifulSoup(resp.text, "html.parser")

                if soup.title and soup.title.string:
                    title = soup.title.string.strip()

                meta = soup.find("meta", {"name": "description"})
                if meta and meta.get("content"):
                    snippet = meta["content"].strip()
                else:
                    p = soup.find("p")
                    if p and p.get_text():
                        snippet = p.get_text().strip().replace("\n", " ")
            except Exception:
                pass

            if snippet:
                entries.append(f"**{title}**  \n{snippet}  \n<{url}>")
            else:
                entries.append(f"**{title}**  \n<{url}>")

        if not entries:
            return f"ℹ️ No results found for '{query}'."
        return "\n\n".join(entries)

    class InternetChatbot:
        def __init__(self):
            utils.sync_st_session()
            self.llm = utils.configure_llm(widget_key="SELECTED_LLM_INTERNET")

        def setup_agent(self):
            web_tool = Tool(
                name="WebSearch",
                func=safe_free_search,
                description="Fetch live web results: returns top page titles, snippets, and links."
            )
            prompt = hub.pull("hwchase17/react-chat")
            memory = ConversationBufferMemory(memory_key="chat_history")
            agent = create_react_agent(self.llm, [web_tool], prompt)
            executor = AgentExecutor(
                agent=agent,
                tools=[web_tool],
                memory=memory,
                verbose=False,
                handle_parsing_errors=True
            )
            return executor, memory

        @utils.enable_chat_history
        def main(self):
            executor, memory = self.setup_agent()
            user_query = st.chat_input("Ask me anything!", key="INT_QUERY")
            if not user_query:
                return

            utils.display_msg(user_query, "user")
            with st.chat_message("assistant"):
                st_cb = StreamlitCallbackHandler(st.container())
                try:
                    out = executor.invoke(
                        {"input": user_query, "chat_history": memory.chat_memory.messages},
                        {"callbacks": [st_cb]}
                    )
                    answer = out.get("output", "⚠️ No answer.")
                except Exception as e:
                    answer = f"⚠️ Oops, something went wrong: {e}"

                st.session_state['messages'].append({"role": "assistant", "content": answer})
                st.write(answer)
                utils.print_qa(InternetChatbot, user_query, answer)

    # Kick off this page’s chatbot:
    InternetChatbot().main()

# -------------------------
# Page: SM Advisory GPT (Chargeable)
# -------------------------
elif page == "SM Advisory GPT":
    st.header("SM Advisory GPT")
    st.write('Has access to custom documents and can respond to user queries by referring to the content within those documents')

    class CustomDocChatbot:

        def __init__(self):
            utils.sync_st_session()
            self.llm = utils.configure_llm()
            self.embedding_model = utils.configure_embedding_model()

        def save_file(self, file):
            folder = 'tmp'
            if not os.path.exists(folder):
                os.makedirs(folder)
            
            file_path = f'./{folder}/{file.name}'
            with open(file_path, 'wb') as f:
                f.write(file.getvalue())
            return file_path

        @st.spinner('Analyzing documents…')
        def setup_qa_chain(self, uploaded_files):
            # Load docs from each PDF
            docs = []
            for file in uploaded_files:
                file_path = self.save_file(file)
                loader = PyPDFLoader(file_path)
                docs.extend(loader.load())
            
            # Split into chunks and embed
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = text_splitter.split_documents(docs)
            vectordb = DocArrayInMemorySearch.from_documents(splits, self.embedding_model)

            # Retriever over embedded chunks
            retriever = vectordb.as_retriever(search_type='mmr', search_kwargs={'k':2, 'fetch_k':4})

            # Conversation memory
            memory = ConversationBufferMemory(memory_key='chat_history', output_key='answer', return_messages=True)

            # Build RAG chain
            qa_chain = ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=retriever,
                memory=memory,
                return_source_documents=True,
                verbose=False
            )
            return qa_chain

        @utils.enable_chat_history
        def main(self):
            # Sidebar file uploader
            uploaded_files = st.sidebar.file_uploader(
                label='Upload PDF files',
                type=['pdf'],
                accept_multiple_files=True
            )
            if not uploaded_files:
                st.error("Please upload PDF documents to continue!")
                st.stop()

            # Chat input
            user_query = st.chat_input(placeholder="Ask me anything about your PDFs…")
            if not user_query:
                return

            # Build or reuse QA chain
            qa_chain = self.setup_qa_chain(uploaded_files)

            utils.display_msg(user_query, 'user')
            with st.chat_message("assistant"):
                st_cb = StreamHandler(st.empty())
                result = qa_chain.invoke(
                    {"question": user_query},
                    {"callbacks": [st_cb]}
                )
                answer = result["answer"]
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.write(answer)
                utils.print_qa(CustomDocChatbot, user_query, answer)

                # Show source references
                for idx, doc in enumerate(result["source_documents"], 1):
                    filename = os.path.basename(doc.metadata["source"])
                    page_num = doc.metadata.get("page", "–")
                    ref_title = f":blue[Reference {idx}: *{filename} – page {page_num}*]"
                    with st.popover(ref_title):
                        st.caption(doc.page_content)

    # Instantiate and run
    CustomDocChatbot().main()
    

# -------------------------
# Page: SM Net GPT (Premium)
# -------------------------
elif page == "SM Net GPT":
    st.header("SM Net GPT")
    st.write("Combine your SQL database, live web search, and website content into one comprehensive answer.")

    # --- helper: live web search ---
    def safe_free_search(query: str, max_results: int = 5) -> str:
        try:
            urls = search(query, num_results=max_results)
        except TypeError:
            urls = search(query, stop=max_results, pause=1.0)

        entries, headers = [], {"User-Agent": "Mozilla/5.0"}
        for url in urls:
            title, snippet = url, ""
            try:
                resp = requests.get(url, headers=headers, timeout=5)
                soup = BeautifulSoup(resp.text, "html.parser")
                if soup.title and soup.title.string:
                    title = soup.title.string.strip()
                meta = soup.find("meta", {"name": "description"})
                if meta and meta.get("content"):
                    snippet = meta["content"].strip()
                else:
                    p = soup.find("p")
                    if p and p.get_text():
                        snippet = p.get_text().strip().replace("\n", " ")
            except Exception:
                pass
            if snippet:
                entries.append(f"**{title}**  \n{snippet}  \n<{url}>")
            else:
                entries.append(f"**{title}**  \n<{url}>")
        return "\n\n".join(entries) if entries else f"ℹ️ No results for '{query}'."

    class MultiSourceChatbot:
        def __init__(self):
            utils.sync_st_session()
            # reuse your global LLM & embedding
            self.llm = utils.configure_llm(widget_key="SELECTED_LLM_MULTI")
            self.embed_model = utils.configure_embedding_model()

        # --- SQL setup (same pattern as your SqlChatbot) ---
        def setup_db(self, db_uri: str) -> SQLDatabase:
            if db_uri == "USE_SAMPLE_DB":
                db_fp = (Path(__file__).parent / "assets" / "output.db").absolute()
                creator = lambda: sqlite3.connect(f"file:{db_fp.as_posix()}?mode=ro", uri=True)
                engine = create_engine("sqlite:///", creator=creator)
                return SQLDatabase(engine)
            else:
                return SQLDatabase.from_uri(database_uri=db_uri)

        def setup_sql_agent(self, db: SQLDatabase):
            return create_sql_agent(
                llm=self.llm,
                db=db,
                top_k=180,
                verbose=False,
                agent_type="openai-tools",
                handle_parsing_errors=True,
                handle_sql_errors=True,
            )

        # --- Website retrieval setup ---
        async def _fetch(self, session, url: str) -> str:
            HEADERS = {"User-Agent": "Mozilla/5.0"}
            try:
                async with session.get(url, headers=HEADERS, timeout=10) as r:
                    r.raise_for_status()
                    return await r.text()
            except:
                return ""

        async def _scrape_all(self, urls: list[str]) -> list[str]:
            async with aiohttp.ClientSession() as sess:
                return await asyncio.gather(*(self._fetch(sess, u) for u in urls))

        @st.cache_data(ttl=3600, show_spinner="Scraping sites")
        def scrape_all(_self, urls: list[str]) -> list[str]:
            htmls = asyncio.run(_self._scrape_all(urls))
            return [h or "" for h in htmls]

        @st.cache_resource(ttl=86400)
        def setup_vectordb(_self, websites: list[str]):
            htmls = _self.scrape_all(websites)
            docs = [Document(page_content=html, metadata={"source": url})
                    for url, html in zip(websites, htmls)]
            splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            chunks = splitter.split_documents(docs)
            return DocArrayInMemorySearch.from_documents(chunks, _self.embed_model)

        def setup_qa_chain(self, vectordb):
            retriever = vectordb.as_retriever(search_type="mmr", search_kwargs={"k":2,"fetch_k":4})
            memory = ConversationBufferMemory(memory_key="chat_history", output_key="answer", return_messages=True)
            return ConversationalRetrievalChain.from_llm(
                llm=self.llm,
                retriever=retriever,
                memory=memory,
                return_source_documents=False,
                verbose=False,
            )

        @utils.enable_chat_history
        def main(self):
            # 1) Database choice
            db_opt = ["Use sample DB", "Connect your SQL DB"]
            choice = st.sidebar.radio("SQL source:", db_opt, key="MS_SQL_CHOICE")
            if choice == db_opt[1]:
                db_uri = st.sidebar.text_input("Database URI", placeholder="mysql://user:pass@host:port/db")
                if not db_uri:
                    st.sidebar.error("Enter a DB URI")
                    return
            else:
                db_uri = "USE_SAMPLE_DB"

            # 2) Websites
            if "ms_sites" not in st.session_state:
                st.session_state["ms_sites"] = []
            url_in = st.sidebar.text_input("Website URL to index", placeholder="https://", key="MS_URL")
            if st.sidebar.button("➕ Add Site"):
                if validators.url(url_in):
                    st.session_state["ms_sites"].append(url_in)
                    st.sidebar.success("Added")
                else:
                    st.sidebar.error("Invalid URL")
            if st.sidebar.button("🗑️ Clear Sites"):
                st.session_state["ms_sites"] = []

            sites = list(dict.fromkeys(st.session_state["ms_sites"]))
            if sites:
                st.sidebar.markdown("**Indexed sites:**")
                for s in sites:
                    st.sidebar.caption(f"- {s}")

            # Wait for user query
            query = st.chat_input("Ask anything across SQL, the web & indexed sites:", key="MS_QUERY")
            if not query:
                return

            # Echo user
            utils.display_msg(query, "user")

            # 1️⃣ Run SQL agent
            db = self.setup_db(db_uri)
            sql_agent = self.setup_sql_agent(db)
            with st.chat_message("assistant"):
                st.info("Running SQL query…")
                cb = StreamlitCallbackHandler(st.container())
                sql_out = sql_agent.invoke({"input": query}, {"callbacks":[cb]})
                sql_ans = sql_out["output"]

            # 2️⃣ Live web search
            with st.chat_message("assistant"):
                st.info("Fetching live web results…")
                web_ans = safe_free_search(query)

            # 3️⃣ Website retrieval
            site_ans = ""
            if sites:
                with st.chat_message("assistant"):
                    st.info("Searching indexed sites…")
                    vdb = self.setup_vectordb(sites)
                    qa = self.setup_qa_chain(vdb)
                    qa_out = qa.invoke({"question": query}, {"callbacks":[StreamHandler(st.empty())]})
                    site_ans = qa_out["answer"]

            # 4️⃣ Aggregate into a final answer
            aggregator_prompt = (
                f"User asked: {query}\n\n"
                f"SQL DB answer:\n{sql_ans}\n\n"
                f"Live web search results:\n{web_ans}\n\n"
                f"Indexed website answer:\n{site_ans}\n\n"
                "Please combine these into one coherent, comprehensive response."
            )
            with st.chat_message("assistant"):
                st.info("Aggregating final answer…")
                from langchain.chains import ConversationChain
                chain = ConversationChain(llm=self.llm, verbose=False)
                agg_out = chain.invoke({"input": aggregator_prompt})
                final = agg_out["response"]
                st.write(final)

    # run it
    MultiSourceChatbot().main()

