"""
VectorStore — 向量存储 & 检索

基于 ChromaDB 实现，支持持久化和相似度搜索。
"""

import chromadb
from chromadb.config import Settings
from .document_loader import Document
from .embeddings import EmbeddingService
import uuid


class VectorStore:
    """ChromaDB 向量存储"""

    def __init__(
        self,
        embedding_service: EmbeddingService,
        persist_dir: str = "./data/chroma",
        collection_name: str = "documents",
    ):
        self.embedding_service = embedding_service

        os.makedirs(persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=persist_dir,
            settings=Settings(anonymized_telemetry=False),
        )

        # 删除旧 collection 重建（简易方案；生产环境应使用 update）
        try:
            self.client.delete_collection(collection_name)
        except Exception:
            pass

        self.collection = self.client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def add_documents(self, documents: list[Document]):
        """将文档块存入向量库"""
        if not documents:
            return

        texts = [doc.content for doc in documents]
        embeddings = self.embedding_service.embed(texts)
        ids = [str(uuid.uuid4()) for _ in documents]
        metadatas = [doc.metadata for doc in documents]

        # ChromaDB 需要 list of lists
        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=metadatas,
        )

        print(f"[VectorStore] 已存入 {len(documents)} 个文档块")

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """语义搜索，返回最相关的 top_k 个文档块"""
        query_embedding = self.embedding_service.embed_query(query)

        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        # 格式化结果
        hits = []
        for i in range(len(results["ids"][0])):
            hits.append({
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "score": 1 - results["distances"][0][i],  # cosine distance → similarity
            })
        return hits

    def count(self) -> int:
        return self.collection.count()


import os
