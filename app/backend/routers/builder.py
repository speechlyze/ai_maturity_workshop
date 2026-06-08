"""Form Factor 5 — The Autonomous Agent.

The top rung: an agent with file + shell tools that *writes and runs code* to
build durable automation, fixing its own errors until it works. All file/shell
ops are confined to a sandbox directory. Mirrors the notebook's builder run.

⚠️  This form factor executes code (Bash/Write/Edit) with permissions bypassed,
    scoped to ``backend/sandbox``. That is the point of the demo — keep it local.
"""
from __future__ import annotations

from fastapi import APIRouter

from backend.config import settings
from backend.core.agent_runtime import AGENT_AVAILABLE, agent_env, run_agent_events
from backend.core.anthropic_client import MODEL
from backend.core.sandbox import SANDBOX, reset_sandbox
from backend.core.sse import sse_response
from backend.schemas import BuilderRequest

router = APIRouter(prefix="/api/builder", tags=["builder"])

SYSTEM_PROMPT = "You are an automation engineer. Build the smallest correct solution, then verify it runs."

DEFAULT_TASK = (
    "In the current directory there is a file `support_messages.csv` with columns id,category,message.\n"
    "1. Write a minimal, well-documented Python script `triage_report.py` (standard library only) that "
    "reads that CSV, counts how many messages are in each category, and writes the counts to "
    "`report.json` sorted by count descending.\n"
    "2. Run it with python.\n"
    "3. If it errors, fix it and re-run until it succeeds.\n"
    "4. Confirm what you built and show the contents of report.json."
)

_TEXT_EXT = {".py", ".json", ".csv", ".txt", ".md", ".cfg", ".ini", ".sh", ".yaml", ".yml", ".log"}
_MAX_FILE_BYTES = 20_000


@router.get("/default-task")
def default_task() -> dict:
    return {"task": DEFAULT_TASK}


@router.get("/artifacts")
def artifacts() -> dict:
    """List sandbox files and return text contents (so the UI can show what was built)."""
    if not SANDBOX.exists():
        return {"files": []}
    files = []
    for p in sorted(SANDBOX.iterdir()):
        if not p.is_file():
            continue
        entry = {"name": p.name, "size": p.stat().st_size, "content": None, "truncated": False}
        if p.suffix.lower() in _TEXT_EXT and p.stat().st_size <= _MAX_FILE_BYTES:
            try:
                entry["content"] = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                entry["content"] = None
        elif p.suffix.lower() in _TEXT_EXT:
            entry["truncated"] = True
        files.append(entry)
    return {"files": files, "sandbox": str(SANDBOX)}


@router.post("/run")
async def run(req: BuilderRequest):
    if not AGENT_AVAILABLE:
        async def unavailable():
            yield {"type": "error",
                   "message": "The Claude Agent SDK CLI was not found. Install it with "
                              "`npm i -g @anthropic-ai/claude-code` to enable Form Factors 4 & 5."}
        return sse_response(unavailable())

    reset_sandbox()

    from claude_agent_sdk import ClaudeAgentOptions

    options = ClaudeAgentOptions(
        model=MODEL,
        cwd=str(SANDBOX),
        allowed_tools=["Read", "Write", "Edit", "Bash"],
        permission_mode="bypassPermissions",
        max_turns=30,
        setting_sources=[],
        system_prompt=SYSTEM_PROMPT,
        cli_path=settings.claude_cli_path,
        env=agent_env(),
    )
    task = (req.task or DEFAULT_TASK).strip()

    async def events():
        async for ev in run_agent_events(task, options):
            yield ev
        yield {"type": "artifacts_ready"}

    return sse_response(events())
