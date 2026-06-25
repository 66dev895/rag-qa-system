"""
TextSplitter — 文本分块器

使用递归字符分割策略，保证 chunk 语义完整性。
"""

from .document_loader import Document


class TextSplitter:
    """递归字符分割器"""

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 100,
        separators: list[str] | None = None,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators or ["\n\n", "\n", "。", ".", " ", ""]

    def split(self, documents: list[Document]) -> list[Document]:
        """分割文档列表，返回 chunk 列表"""
        chunks = []
        for doc in documents:
            chunks.extend(self._split_single(doc))
        return chunks

    def _split_single(self, doc: Document) -> list[Document]:
        """递归分割单个文档"""
        if len(doc.content) <= self.chunk_size:
            return [doc]

        for sep in self.separators:
            if sep in doc.content:
                parts = self._split_by_separator(doc, sep)
                if len(parts) > 1:
                    return parts
        # 强制按长度切分
        return self._force_split(doc)

    def _split_by_separator(self, doc: Document, sep: str) -> list[Document]:
        """按分隔符切分并保证 overlap"""
        splits = doc.content.split(sep)
        chunks = []
        current = ""

        for split in splits:
            if len(current) + len(sep) + len(split) > self.chunk_size and current:
                chunks.append(Document(
                    content=current.strip(),
                    metadata={**doc.metadata, "chunk_index": len(chunks)}
                ))
                # overlap: 保留末尾部分
                overlap_text = current[-self.chunk_overlap:] if self.chunk_overlap > 0 else ""
                current = overlap_text + sep + split if overlap_text else split
            else:
                current = current + sep + split if current else split

        if current.strip():
            chunks.append(Document(
                content=current.strip(),
                metadata={**doc.metadata, "chunk_index": len(chunks)}
            ))

        return chunks

    def _force_split(self, doc: Document) -> list[Document]:
        """按固定长度强制切分"""
        chunks = []
        text = doc.content
        for i in range(0, len(text), self.chunk_size - self.chunk_overlap):
            chunk = text[i:i + self.chunk_size]
            chunks.append(Document(
                content=chunk.strip(),
                metadata={**doc.metadata, "chunk_index": len(chunks)}
            ))
        return chunks
