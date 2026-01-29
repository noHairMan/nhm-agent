from langchain_ollama import OllamaEmbeddings

from mercedes.utils.conf import settings


def get_embeddings():
    return OllamaEmbeddings(
        model=settings.EMBEDDING_MODEL,
        base_url=settings.OLLAMA_BASE_URL,
    )
