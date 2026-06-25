"""
Retriever — 检索器

组合 EmbeddingService + VectorStore，提供统一的检索接口。
"""

from .embeddings import EmbeddingService
from .vector_store import VectorStore


class Retriever:
    """文档检索器"""

    def __init__(self, vector_store: VectorStore, top_k: int = 5):
        self.vector_store = vector_store
        self.top_k = top_k

    def retrieve(self, query: str) -> list[dict]:
        """检索相关文档块"""
        return self.vector_store.search(query, top_k=self.top_k)

    def format_context(self, hits: list[dict]) -> str:
        """将检索结果格式化为 LLM 上下文"""
        if not hits:
            return ""

        parts = []
        for i, hit in enumerate(hits, 1):
            source = hit["metadata"].get("source", "unknown")
            parts.append(
                f"[片段 {i}] 来源: {source} (相关度: {hit['score']:.2f})\n{hit['content']}"
            )

        return "\n\n---\n\n".join(parts)
