"""
RAG 智能文档问答系统 — FastAPI 入口
"""

import os
import sys

# 确保 server 目录在 Python path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import upload, chat, index_
from server_state import init_rag_state


def create_app() -> FastAPI:
    app = FastAPI(
        title="RAG QA System",
        description="基于 RAG 的智能文档问答系统",
        version="1.0.0",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 路由注册
    app.include_router(upload.router)
    app.include_router(chat.router)
    app.include_router(index_.router)

    return app


app = create_app()


@app.on_event("startup")
async def startup():
    """服务启动时初始化 RAG 引擎"""
    api_key = os.getenv("OPENAI_API_KEY", "")
    base_url = os.getenv("OPENAI_BASE_URL", "")
    model = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

    if api_key:
        init_rag_state(api_key, base_url, model)
        print(f"[Server] 使用模型: {model}")
    else:
        print("[Server] ⚠ OPENAI_API_KEY 未设置，问答功能暂不可用")
        print("[Server] 请在 .env 文件中配置 API Key")


@app.get("/api/health")
async def health():
    state = __import__('server_state').get_rag_state()
    return {
        "status": "ok",
        "rag_ready": state["initialized"],
        "documents": state["vector_store"].count() if state["vector_store"] else 0,
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
