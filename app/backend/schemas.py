"""Pydantic request bodies for the API."""
from __future__ import annotations

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    session_id: str = Field(..., description="Client-generated conversation id")
    message: str


class RagRequest(BaseModel):
    query: str
    technique: str = "vector"   # vector | keyword | hybrid
    k: int = 4


class WorkflowRequest(BaseModel):
    message: str
    max_revisions: int = 1


class AgentRequest(BaseModel):
    prompt: str


class BuilderRequest(BaseModel):
    task: str
