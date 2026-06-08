"""AI Maturity Ladder — FastAPI application.

Mounts one router per form factor, warms the retriever in the background on
startup, and serves the static frontend from the same origin.

Run from the `app/` directory:
    uvicorn backend.main:app --reload --port 8000
"""
from __future__ import annotations

import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.config import FRONTEND_DIR
from backend.core.retrieval import store
from backend.routers import agent, builder, chat, meta, rag, workflow


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm the embedding model + Oracle connection without blocking startup.
    threading.Thread(target=store.initialize, daemon=True).start()
    yield


app = FastAPI(title="AI Maturity Ladder", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

for r in (meta.router, chat.router, rag.router, workflow.router, agent.router, builder.router):
    app.include_router(r)

# Serve the SPA last so /api/* routes take precedence.
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=False)
