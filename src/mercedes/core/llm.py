from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

from mercedes.utils.conf import settings


def get_llm(model: str = None):
    model = model or settings.DEFAULT_MODEL
    return ChatOllama(
        model=model,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0,
    )


def get_llm(model: str = None):
    model = model or settings.DEFAULT_MODEL
    return ChatOpenAI(
        model=model,
        base_url=settings.OPENAI_BASE_URL,
        api_key=settings.OPENAI_API_KEY,
        temperature=1,
    )
