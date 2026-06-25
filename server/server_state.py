"""
应用全局状态管理

简易单例模式管理 RAG 各组件。
"""

from rag.vector_store import VectorStore
from rag.retriever import Retriever
from rag.generator import Generator
from rag.embeddings import EmbeddingService

_state: dict = {
    "embedding": None,
    "vector_store": None,
    "retriever": None,
    "generator": None,
    "initialized": False,
}


def init_rag_state(api_key: str, base_url: str, model: str):
    """初始化 RAG 组件"""
    if _state["initialized"]:
        return

    embedding = EmbeddingService()
    vector_store = VectorStore(embedding)
    retriever = Retriever(vector_store)
    generator = Generator(api_key=api_key, base_url=base_url, model=model)

    _state["embedding"] = embedding
    _state["vector_store"] = vector_store
    _state["retriever"] = retriever
    _state["generator"] = generator
    _state["initialized"] = True

    print("[Server] RAG 引擎初始化完成")


def get_rag_state() -> dict:
    return _state
