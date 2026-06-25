"""
FastAPI 路由 — 智能问答（流式 SSE）
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from rag.retriever import Retriever
from rag.generator import Generator
from rag.vector_store import VectorStore
from server_state import get_rag_state

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    query: str
    top_k: int = 5


@router.post("/chat")
async def chat(req: ChatRequest):
    """普通问答（非流式）"""
    state = get_rag_state()
    if state["retriever"] is None:
        raise HTTPException(400, "请先上传文档")

    hits = state["retriever"].retrieve(req.query)
    context = state["retriever"].format_context(hits)

    answer = state["generator"].generate(req.query, context)

    return {
        "answer": answer,
        "sources": [
            {"content": h["content"][:150] + "...", "score": round(h["score"], 3),
             "source": h["metadata"].get("source", "")}
            for h in hits
        ],
    }


@router.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    """流式问答（Server-Sent Events）"""
    state = get_rag_state()
    if state["retriever"] is None:
        raise HTTPException(400, "请先上传文档")

    hits = state["retriever"].retrieve(req.query)
    context = state["retriever"].format_context(hits)

    async def event_stream():
        sources_json = __import__('json').dumps([
            {"content": h["content"][:150] + "...", "score": round(h["score"], 3),
             "source": h["metadata"].get("source", "")}
            for h in hits
        ])
        yield f"event: sources\ndata: {sources_json}\n\n"

        for token in state["generator"].generate_stream(req.query, context):
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
