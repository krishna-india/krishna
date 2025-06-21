import os
import openai
import streamlit as st
from datetime import datetime
from streamlit.logger import get_logger
from langchain_openai import ChatOpenAI
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

logger = get_logger('Langchain-Chatbot')

# define default session state values
defaults = {
    "messages": [{"role": "assistant", "content": "How can I help you?"}],
    "current_page": None
}

# decorator to enable chat history
def enable_chat_history(func):
    if os.environ.get("OPENAI_API_KEY"):
        # to clear chat history after switching chatbot
        current_page = func.__qualname__
        if "current_page" not in st.session_state:
            st.session_state["current_page"] = current_page
        if st.session_state["current_page"] != current_page:
            try:
                st.cache_resource.clear()
                del st.session_state["current_page"]
                del st.session_state["messages"]
            except Exception:
                pass

        # to show chat history on UI
        if "messages" not in st.session_state:
            st.session_state["messages"] = defaults["messages"].copy()
        for msg in st.session_state["messages"]:
            # removed the extra '()' to avoid DeltaGenerator being called
            st.chat_message(msg["role"]).write(msg["content"])

    def execute(*args, **kwargs):
        return func(*args, **kwargs)
    return execute


def display_msg(msg, author):
    st.session_state["messages"].append({"role": author, "content": msg})
    st.chat_message(author).write(msg)


def choose_custom_openai_key():
    openai_api_key = st.sidebar.text_input(
        label="OpenAI API Key",
        type="password",
        placeholder="sk-...",
        key="SELECTED_OPENAI_API_KEY"
    )
    if not openai_api_key:
        st.error("Please add your OpenAI API key to continue.")
        st.info("Obtain your key from this link: https://platform.openai.com/account/api-keys")
        st.stop()

    model = "gpt-4.1-mini"
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        available_models = [
            {"id": i.id, "created": datetime.fromtimestamp(i.created)}
            for i in client.models.list()
            if str(i.id).startswith("gpt")
        ]
        available_models = sorted(available_models, key=lambda x: x["created"])
        available_models = [i["id"] for i in available_models]

        model = st.sidebar.selectbox(
            label="Model",
            options=available_models,
            key="SELECTED_OPENAI_MODEL"
        )
    except openai.AuthenticationError as e:
        st.error(e.body["message"])
        st.stop()
    except Exception as e:
        st.error("Something went wrong. Please try again later.")
        st.stop()
    return model, openai_api_key


def configure_llm(widget_key: str = "SELECTED_LLM"):
    llm_opt = st.sidebar.radio(
        "LLM",
        ["gpt-4.1-mini", "llama3.2:3b", "use your openai api key"],
        key=widget_key,
    )

    if llm_opt == "llama3.2:3b":
        return ChatOllama(model="llama3.2", base_url=st.secrets["OLLAMA_ENDPOINT"])
    elif llm_opt == "gpt-4.1-mini":
        return ChatOpenAI(model_name=llm_opt, temperature=0, streaming=True, api_key=st.secrets["OPENAI_API_KEY"])
    else:
        model, openai_api_key = choose_custom_openai_key()
        return ChatOpenAI(model_name=model, temperature=0, streaming=True, api_key=openai_api_key)


def print_qa(cls, question, answer):
    log_str = "\nUsecase: {}\nQuestion: {}\nAnswer: {}\n" + "------" * 10
    logger.info(log_str.format(cls.__name__, question, answer))

@st.cache_resource
def configure_embedding_model():
    return FastEmbedEmbeddings(model_name="BAAI/bge-small-en-v1.5")


def sync_st_session():
    # set defaults only if missing
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v.copy() if isinstance(v, list) else v
