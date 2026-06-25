"""
DocumentLoader — 文档加载器

支持格式：PDF、TXT、Markdown
返回统一的 Document 对象列表。
"""

import os
from dataclasses import dataclass, field
from PyPDF2 import PdfReader


@dataclass
class Document:
    """文档对象"""
    content: str
    metadata: dict = field(default_factory=dict)


class DocumentLoader:
    """从多种格式加载文档"""

    @staticmethod
    def load(file_path: str) -> list[Document]:
        ext = os.path.splitext(file_path)[1].lower()
        file_name = os.path.basename(file_path)

        if ext == '.pdf':
            return DocumentLoader._load_pdf(file_path, file_name)
        elif ext in ('.txt', '.md', '.markdown'):
            return DocumentLoader._load_text(file_path, file_name)
        else:
            raise ValueError(f"不支持的文件格式: {ext}")

    @staticmethod
    def _load_pdf(file_path: str, file_name: str) -> list[Document]:
        docs = []
        reader = PdfReader(file_path)
        for i, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():
                docs.append(Document(
                    content=text.strip(),
                    metadata={"source": file_name, "page": i + 1}
                ))
        return docs

    @staticmethod
    def _load_text(file_path: str, file_name: str) -> list[Document]:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return [Document(content=content, metadata={"source": file_name})] if content.strip() else []
