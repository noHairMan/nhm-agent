from langchain_chroma import Chroma

from mercedes.core.embeddings import get_embeddings
from mercedes.utils.conf import settings


def get_vector_store(collection_name: str = "default"):
    embeddings = get_embeddings()
    return Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(settings.CHROMA_PATH),
    )
