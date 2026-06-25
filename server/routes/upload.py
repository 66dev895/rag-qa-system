"""
FastAPI 路由 — 文档上传
"""

import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from rag.document_loader import DocumentLoader
from rag.text_splitter import TextSplitter

router = APIRouter(prefix="/api", tags=["documents"])

UPLOAD_DIR = "./data/uploads"


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """上传文档（PDF / TXT / MD）"""
    if not file.filename:
        raise HTTPException(400, "文件名不能为空")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ('.pdf', '.txt', '.md', '.markdown'):
        raise HTTPException(400, f"不支持的文件格式: {ext}")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, file.filename)

    # 保存到磁盘
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # 解析文档
    docs = DocumentLoader.load(file_path)
    if not docs:
        raise HTTPException(400, "文档为空或无法解析")

    return {
        "status": "ok",
        "filename": file.filename,
        "pages": len(docs),
        "total_chars": sum(len(d.content) for d in docs),
    }
