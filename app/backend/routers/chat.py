"""Form Factor 1 — The Chatbot.

A stateless LLM made multi-turn by *resending the whole conversation* each call.
The "memory" is literally the growing message list. Replies stream token-by-token.
"""
from __future__ import annotations

from fastapi import APIRouter

from backend.core.anthropic_client import MAX_TOKENS, MODEL, async_client
from backend.core.sse import sse_response
from backend.schemas import ChatRequest

router = APIRouter(prefix="/api/chat", tags=["chatbot"])

SYSTEM = "You are a helpful assistant."

# Conversation memory: session_id -> list[{"role","content"}]. In-process only.
_sessions: dict[str, list[dict]] = {}


@router.post("/message")
async def message(req: ChatRequest):
    history = _sessions.setdefault(req.session_id, [])
    history.append({"role": "user", "content": req.message})

    async def events():
        parts: list[str] = []
        async with async_client.messages.stream(
            model=MODEL,
            max_tokens=MAX_TOKENS,
            system=SYSTEM,
            messages=history,
        ) as stream:
            async for text in stream.text_stream:
                parts.append(text)
                yield {"type": "delta", "text": text}
        reply = "".join(parts)
        history.append({"role": "assistant", "content": reply})
        # turns = how many messages we now resend every call — the teachable bit.
        yield {"type": "done", "turns": len(history)}

    return sse_response(events())


@router.get("/history")
def history(session_id: str) -> dict:
    return {"history": _sessions.get(session_id, [])}


@router.post("/reset")
def reset(session_id: str) -> dict:
    _sessions.pop(session_id, None)
    return {"ok": True}
