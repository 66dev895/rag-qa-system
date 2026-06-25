"""
EmbeddingService — 文本向量化服务

使用 sentence-transformers 将文本转为稠密向量。
默认模型: all-MiniLM-L6-v2（轻量、384维、中文友好）
"""

from sentence_transformers import SentenceTransformer
import numpy as np


class EmbeddingService:
    """文本向量化服务"""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        print(f"[Embedding] 加载模型: {model_name} ...")
        self.model = SentenceTransformer(model_name)
        self._dim = self.model.get_sentence_embedding_dimension()
        print(f"[Embedding] 模型加载完成，向量维度: {self._dim}")

    @property
    def dimension(self) -> int:
        return self._dim

    def embed(self, texts: list[str]) -> np.ndarray:
        """批量将文本转为向量"""
        if isinstance(texts, str):
            texts = [texts]
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings

    def embed_query(self, query: str) -> np.ndarray:
        """为查询文本生成向量（与 embed 相同，语义上区分）"""
        return self.embed([query])[0]
