#!/usr/bin/env python3
"""Append a normalized, redacted activity event from a Claude Code hook.

Wired from `.claude/settings.json` on SessionStart, UserPromptSubmit, PreToolUse,
PostToolUse, Stop, and SubagentStop. Reads the hook payload as JSON on stdin and
appends ONE compact JSON line to:

    .docs/activity/events/<YYYYMMDD>.jsonl   (UTC date)

This is the raw "what the agents actually did" stream that Layer 2
(`extract_metrics.py`) and the `/retrospective` agent read back.

Design contract (do not weaken):

  * **Fail-open.** Any error is swallowed; the script always exits 0 and never
    writes to stdout, so it can neither block nor slow a tool call, nor inject
    text into the model's context (UserPromptSubmit/PreToolUse stdout would be
    fed back as context — so we stay silent and write only to the log file).
  * **Self-contained.** Standard library only — the chassis is stack-agnostic
    and must run wherever the host project runs.
  * **Redacted + capped.** Only a short, masked descriptor of each tool input is
    stored (never the full payload); secret-looking keys/values are masked and
    everything is truncated before it touches disk. Raw events are also
    git-ignored. This mirrors the knowledge repo's logging-observability
    principle (the OBS-* central-redaction rules).
  * **Branch-attributed.** Each event carries the current git branch so Layer 2
    can group events into a workflow run without inventing a correlation id,
    reusing the branch convention in `.agents/context.md`.

Usage (normally invoked by the harness, but testable by hand):

    echo '{"hook_event_name":"PreToolUse","tool_name":"Read",
           "tool_input":{"file_path":"x"}}' | python3 .agents/activity/log_event.py
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

# --- tuning knobs ---------------------------------------------------------
MAX_SUMMARY = 240  # chars kept from any free-text field

# Substring hints: a tool-input key containing any of these is masked outright.
SECRET_KEY_HINTS = (
    "password",
    "passwd",
    "secret",
    "token",
    "api_key",
    "apikey",
    "authorization",
    "auth",
    "credential",
    "access_key",
    "private_key",
)

# Per-tool field we keep a short descriptor for (first match wins).
DESCRIPTOR_KEYS = ("command", "file_path", "path", "pattern", "url", "query", "prompt")

# Inline secret patterns masked inside any free-text string.
_TOKEN_RES = (
    re.compile(r"\b(?:sk|ghp|gho|ghs|xox[baprs])[-_][A-Za-z0-9]{8,}"),
    re.compile(r"\bAKIA[0-9A-Z]{12,}"),
)
_BEARER_RE = re.compile(r"(?i)\b(bearer)\s+[A-Za-z0-9._-]{8,}")
_KV_RE = re.compile(r"(?i)\b(token|api[_-]?key|secret|password|passwd|auth)\s*[=:]\s*\S+")


def _mask_str(s: str) -> str:
    """Mask secret-looking substrings in free text."""
    for rx in _TOKEN_RES:
        s = rx.sub("[REDACTED]", s)
    s = _BEARER_RE.sub(r"\1 [REDACTED]", s)
    s = _KV_RE.sub(r"\1=[REDACTED]", s)
    return s


def _git_branch(root: Path) -> str:
    """Read the current branch from .git/HEAD without spawning git."""
    git = root / ".git"
    try:
        if git.is_file():  # worktree: ".git" is a pointer file
            gitdir = git.read_text(encoding="utf-8").split("gitdir:", 1)[1].strip()
            base = Path(gitdir) if Path(gitdir).is_absolute() else (root / gitdir)
            head = base / "HEAD"
        else:
            head = git / "HEAD"
        ref = head.read_text(encoding="utf-8").strip()
        if ref.startswith("ref:"):
            return ref.split("refs/heads/", 1)[-1]
        return ref[:12]  # detached HEAD: short sha
    except Exception:
        return ""


def _split_branch(branch: str) -> tuple[str, str]:
    """delivery-feature/20260101-01-user-auth -> ('delivery-feature', '20260101-01-user-auth')."""
    if "/" in branch:
        prefix, rest = branch.split("/", 1)
        return prefix, rest
    return branch, ""


def _descriptor(tool_input: object) -> str:
    """A short, masked one-field descriptor of a tool input."""
    if not isinstance(tool_input, dict):
        return ""
    for key in DESCRIPTOR_KEYS:
        if any(hint in key for hint in SECRET_KEY_HINTS):
            continue  # never echo a secret-named field
        value = tool_input.get(key)
        if isinstance(value, str) and value:
            return f"{key}={_mask_str(value)}"
    return ""


def _ok(tool_response: object) -> bool | None:
    """Best-effort success flag for a PostToolUse response."""
    if tool_response is None:
        return None
    if isinstance(tool_response, dict):
        if tool_response.get("is_error") or tool_response.get("error"):
            return False
        if tool_response.get("interrupted"):
            return False
    return True


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0  # nothing parseable; never fail

    try:
        root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or payload.get("cwd") or Path.cwd())
        event = payload.get("hook_event_name", "unknown")
        branch = _git_branch(root)
        wtype, run_id = _split_branch(branch)

        record: dict[str, object] = {
            "ts": datetime.now(UTC).isoformat(timespec="seconds"),
            "session": str(payload.get("session_id", ""))[:8],
            "event": event,
            "branch": branch,
            "type": wtype,
            "run_id": run_id,
        }

        tool = payload.get("tool_name")
        if tool:
            record["tool"] = tool
            record["summary"] = _descriptor(payload.get("tool_input"))[:MAX_SUMMARY]
        if event == "PostToolUse":
            record["ok"] = _ok(payload.get("tool_response"))
        if event == "UserPromptSubmit":
            record["summary"] = _mask_str(str(payload.get("prompt", "")))[:MAX_SUMMARY]
        if event == "SessionStart":
            record["summary"] = str(payload.get("source", ""))[:MAX_SUMMARY]

        out_dir = root / ".docs" / "activity" / "events"
        out_dir.mkdir(parents=True, exist_ok=True)
        day = datetime.now(UTC).strftime("%Y%m%d")
        with (out_dir / f"{day}.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        return 0  # fail-open: logging must never break a tool call

    return 0


if __name__ == "__main__":
    sys.exit(main())
