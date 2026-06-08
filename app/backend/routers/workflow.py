"""Form Factor 3 — The LLM-Driven Workflow.

A fixed, code-orchestrated pipeline: classify → route → retrieve → draft →
review-and-revise. Each stage streams a `step` event so the UI can render the
pipeline filling in live. *Your code* owns the control flow; the model fills in
each step (this is the contrast with the agent in FF4).
"""
from __future__ import annotations

from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool

from backend.core.anthropic_client import MAX_TOKENS, MODEL, client, structured_json, text_of
from backend.core.retrieval import store
from backend.core.sse import sse_response
from backend.schemas import WorkflowRequest

router = APIRouter(prefix="/api/workflow", tags=["workflow"])

CLASSIFY_SCHEMA = {
    "type": "object",
    "properties": {
        "category": {"type": "string",
                     "enum": ["billing", "technical", "account", "feature_request", "other"]},
        "urgency": {"type": "string", "enum": ["low", "medium", "high"]},
        "summary": {"type": "string", "description": "One-line summary of the request."},
    },
    "required": ["category", "urgency", "summary"],
    "additionalProperties": False,
}

REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "approved": {"type": "boolean"},
        "feedback": {"type": "string", "description": "What to fix if not approved."},
    },
    "required": ["approved", "feedback"],
    "additionalProperties": False,
}


def _classify(message: str) -> dict:
    return structured_json(
        system="Classify the incoming Acme Cloud support message.",
        user=message,
        schema=CLASSIFY_SCHEMA,
    )


def _draft_reply(message: str, context: str) -> str:
    system = (
        "You are an Acme Cloud support agent. Write a friendly, accurate reply using ONLY "
        "the provided context. Cite facts with [n]. Keep it under 120 words."
    )
    response = client.messages.create(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": f"Customer message:\n{message}\n\nContext:\n{context}"}],
    )
    return text_of(response)


def _review(message: str, draft: str, context: str) -> dict:
    system = (
        "You are a support QA reviewer. Approve the draft only if it is accurate per the "
        "context, on-topic, and professional. Otherwise set approved=false and say what to fix."
    )
    prompt = f"Customer message:\n{message}\n\nContext:\n{context}\n\nDraft reply:\n{draft}"
    return structured_json(system=system, user=prompt, schema=REVIEW_SCHEMA, max_tokens=512)


@router.post("/run")
async def run(req: WorkflowRequest):
    async def events():
        # ① classify (LLM)
        yield {"type": "step", "step": "classify", "status": "running"}
        info = await run_in_threadpool(_classify, req.message)
        yield {"type": "step", "step": "classify", "status": "done", "data": info}

        # ② route (your code)
        escalate = info.get("category") == "billing" and info.get("urgency") == "high"
        yield {"type": "step", "step": "route", "status": "done",
               "data": {"escalated": escalate,
                        "reason": "Urgent billing → flag for a human" if escalate
                                  else "Handled by the automated pipeline"}}

        # ③ retrieve (RAG, reused from FF2)
        yield {"type": "step", "step": "retrieve", "status": "running"}
        hits = await run_in_threadpool(store.search, req.message, "vector", 3)
        context = "\n".join(f"[{i + 1}] {h.content}" for i, h in enumerate(hits))
        yield {"type": "step", "step": "retrieve", "status": "done",
               "data": {"hits": [h.as_dict() for h in hits], "backend": store.backend}}

        # ④ draft (LLM)
        yield {"type": "step", "step": "draft", "status": "running"}
        draft = await run_in_threadpool(_draft_reply, req.message, context)
        yield {"type": "step", "step": "draft", "status": "done", "data": {"draft": draft, "attempt": 1}}

        # ⑤ review-and-revise gate (your code controls the loop)
        for attempt in range(req.max_revisions + 1):
            yield {"type": "step", "step": "review", "status": "running", "data": {"attempt": attempt + 1}}
            verdict = await run_in_threadpool(_review, req.message, draft, context)
            yield {"type": "step", "step": "review", "status": "done",
                   "data": {**verdict, "attempt": attempt + 1}}
            if verdict.get("approved") or attempt >= req.max_revisions:
                break
            yield {"type": "step", "step": "draft", "status": "running",
                   "data": {"attempt": attempt + 2, "revising": True}}
            draft = await run_in_threadpool(
                _draft_reply, req.message,
                context + f"\n\nReviewer feedback to address: {verdict.get('feedback', '')}",
            )
            yield {"type": "step", "step": "draft", "status": "done",
                   "data": {"draft": draft, "attempt": attempt + 2}}

        yield {"type": "final", "classification": info, "escalated": escalate, "reply": draft}

    return sse_response(events())
