from langchain_core.tools import tool

from mercedes.core.rag import get_vector_store


@tool
def rag_search(query: str) -> str:
    """从向量数据库中搜索相关文档。"""
    vector_store = get_vector_store()
    results = vector_store.similarity_search(query, k=3)
    if not results:
        return "没有找到相关的文档。"

    formatted_results = []
    for i, doc in enumerate(results):
        formatted_results.append(f"结果 {i+1}:\n内容: {doc.page_content}\n元数据: {doc.metadata}")

    return "\n\n".join(formatted_results)


@tool
def rag_add_document(content: str, metadata: dict = None) -> str:
    """向向量数据库中添加文档。"""
    vector_store = get_vector_store()
    vector_store.add_texts(texts=[content], metadatas=[metadata] if metadata else None)
    return "文档已成功添加到向量数据库。"
