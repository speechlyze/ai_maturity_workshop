"""The Form Factor 5 sandbox — a disposable workspace seeded with a sample dataset.

Kept import-light (no Anthropic client, no agent SDK) so it can be seeded at
container-create time, before any API key is configured.
"""
from __future__ import annotations

import csv
import shutil

from backend.config import settings

SANDBOX = settings.sandbox_dir
SEED_FILE = "support_messages.csv"
SEED_ROWS = [
    {"id": 1, "category": "billing", "message": "I was double charged"},
    {"id": 2, "category": "technical", "message": "API returns 500 on /v1/sync"},
    {"id": 3, "category": "billing", "message": "How do I upgrade to Pro?"},
    {"id": 4, "category": "account", "message": "Need to add a teammate"},
    {"id": 5, "category": "technical", "message": "Webhooks are not firing"},
]


def reset_sandbox() -> None:
    """Clear the sandbox and (re)write the seed dataset, so each run starts clean."""
    SANDBOX.mkdir(parents=True, exist_ok=True)
    for child in SANDBOX.iterdir():
        if child.is_file():
            child.unlink()
        else:
            shutil.rmtree(child, ignore_errors=True)
    with open(SANDBOX / SEED_FILE, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "category", "message"])
        writer.writeheader()
        writer.writerows(SEED_ROWS)


def seed_if_empty() -> None:
    """Seed the sandbox only if it doesn't already contain the dataset (for setup-time use)."""
    if not (SANDBOX / SEED_FILE).exists():
        reset_sandbox()
