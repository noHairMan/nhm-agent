from langchain_ollama import ChatOllama

from mercedes.utils.conf import settings


def get_llm(model: str = None):
    model = model or settings.DEFAULT_OLLAMA_MODEL
    return ChatOllama(
        model=model,
        base_url=settings.OLLAMA_BASE_URL,
        temperature=0,
    )
