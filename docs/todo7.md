# 🧩 TODO 7 — Configure the autonomous builder

The top rung. The autonomous agent doesn't just *answer* — it **writes files and runs shell
commands** to build something, then fixes its own errors. That power needs guardrails, and those
guardrails live in `ClaudeAgentOptions`.

### What to implement
Replace the empty `ClaudeAgentOptions()` with a fully configured one:
- `model=MODEL`
- `cwd=str(SANDBOX)` — confine *all* file/shell ops to the sandbox directory.
- `allowed_tools=["Read", "Write", "Edit", "Bash"]` — the tools that let it build and run code.
- `permission_mode="bypassPermissions"` — autonomous: no human approval prompt per action.
- `max_turns=30` and `setting_sources=[]` — bound the loop; keep the run hermetic.
- `system_prompt="You are an automation engineer. Build the smallest correct solution, then
  verify it runs."`

> ⚠️ `bypassPermissions` + `Bash` means the agent executes code unattended. That's the whole point
> of this form factor — which is exactly why `cwd` pins it to a disposable sandbox.

## ✅ Solution

Replace the placeholder cell with this, then run the **`✅ TODO 7 check`** cell:

```python
builder_options = ClaudeAgentOptions(
    model=MODEL,
    cwd=str(SANDBOX),                                   # all file/shell ops stay in the sandbox
    allowed_tools=["Read", "Write", "Edit", "Bash"],    # the tools that let it build & run code
    permission_mode="bypassPermissions",                # autonomous: no human approval prompts
    max_turns=30,
    setting_sources=[],
    system_prompt="You are an automation engineer. Build the smallest correct solution, then verify it runs.",
)
```

_Generated from the complete notebook — this is the exact reference implementation._
