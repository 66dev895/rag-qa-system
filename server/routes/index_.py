"""
路由 — 首页 & 文档管理
"""

from fastapi import APIRouter
from fastapi.responses import FileResponse
from rag.document_loader import DocumentLoader
from rag.text_splitter import TextSplitter
from server_state import get_rag_state
import os
import glob

router = APIRouter(tags=["index"])

UPLOAD_DIR = "./data/uploads"


@router.get("/api/documents")
async def list_documents():
    """列出已上传的文档"""
    if not os.path.exists(UPLOAD_DIR):
        return {"documents": []}

    files = glob.glob(os.path.join(UPLOAD_DIR, "*"))
    return {
        "documents": [
            {
                "name": os.path.basename(f),
                "size": os.path.getsize(f),
                "type": os.path.splitext(f)[1],
            }
            for f in files
        ]
    }


@router.post("/api/documents/index")
async def index_documents():
    """将已上传文档向量化并存入向量库"""
    if not os.path.exists(UPLOAD_DIR):
        return {"status": "error", "message": "没有已上传的文档"}

    state = get_rag_state()
    if not state["initialized"]:
        return {"status": "error", "message": "RAG 引擎未初始化，请配置 API Key"}

    files = glob.glob(os.path.join(UPLOAD_DIR, "*"))
    if not files:
        return {"status": "error", "message": "没有已上传的文档"}

    splitter = TextSplitter(chunk_size=500, chunk_overlap=100)
    total_chunks = 0

    for file_path in files:
        try:
            docs = DocumentLoader.load(file_path)
            chunks = splitter.split(docs)
            state["vector_store"].add_documents(chunks)
            total_chunks += len(chunks)
        except Exception as e:
            print(f"[Index] 处理 {file_path} 失败: {e}")

    return {
        "status": "ok",
        "files_processed": len(files),
        "total_chunks": total_chunks,
        "vector_count": state["vector_store"].count(),
    }
