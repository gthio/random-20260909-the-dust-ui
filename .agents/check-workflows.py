#!/usr/bin/env python3
"""Check that workflows.yaml is internally sound and consistent with the docs.

`workflows.yaml` is the machine-readable source of truth for /pipeline, but the
human-facing tables in `.agents/README.md` and `.agents/context.md` mirror its
contents by hand ("keep them in sync"). That hand-mirroring rots. This linter is
the third in the kit's trio — `check-chassis.sh` guards stack specifics leaking
*in*, `check-references.py` guards references pointing *out*, and this guards the
*internal* wiring of the workflow definitions and their reflection in the docs.

What it validates:

  Structural (from workflows.yaml alone)
    - every workflow has branch_prefix / needs_backlog / terminal_agent / steps
    - step ids are unique within a workflow; each step names an agent
    - on_block.loop_back_to points at an earlier step id in the same workflow,
      and max_rounds is a positive int
    - terminal_agent is one of the workflow's own step agents

  Filesystem
    - every step agent has a `.claude/commands/<agent>.md` binding AND a
      `.agents/prompts/<agent>.md` prompt

  Cross-file (the drift class that has actually bitten this kit)
    - every step agent is rostered in `.agents/README.md` (its `/<agent>` token)
    - terminal_agent matches what `.agents/context.md`'s "Terminal agent by
      workflow:" line claims for that workflow

It would have caught both recent bugs: the gardening `terminal_agent: gardener`
that disagreed with the docs (and with the Reviewer being the real terminal),
and `terminal_agent` lists drifting as Spec Reviewer / Retrospective were added.

Usage:
  python3 .agents/check-workflows.py

Exit 0 if everything is consistent, 1 otherwise.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = REPO_ROOT / ".agents" / "workflows.yaml"
COMMANDS_DIR = REPO_ROOT / ".claude" / "commands"
PROMPTS_DIR = REPO_ROOT / ".agents" / "prompts"
README = REPO_ROOT / ".agents" / "README.md"
CONTEXT = REPO_ROOT / ".agents" / "context.md"

# Agent display names used in the prose tables -> slash-command / prompt slug.
DISPLAY_TO_AGENT = {
    "Tech Writer": "tech-writer",
    "Reviewer": "reviewer",
    "Strategy Auditor": "auditor-strategy",
    "Principle Auditor": "auditor-principle",
    "Spec Reviewer": "spec-reviewer",
    "Gardener": "gardener",
    "Founder Architect": "founder-architect",
    "Housekeeper": "housekeeper",
    "Retrospective": "retrospective",
}


def load_workflows() -> dict:
    """Parse workflows.yaml. Prefer PyYAML; fall back to a tailored parser so
    the linter has no third-party dependency (matching its sibling linters)."""
    text = WORKFLOWS.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore  # noqa: TID251 — linter script, not core/; PyYAML optional with fallback below

        return yaml.safe_load(text)["workflows"]
    except ImportError:
        return _minimal_parse(text)


def _scalar(raw: str):
    v = raw.strip()
    if v in ("true", "false"):
        return v == "true"
    if re.fullmatch(r"-?\d+", v):
        return int(v)
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        return [x.strip() for x in inner.split(",")] if inner else []
    if v.startswith("{") and v.endswith("}"):
        out = {}
        for pair in v[1:-1].split(","):
            if ":" in pair:
                k, val = pair.split(":", 1)
                out[k.strip()] = _scalar(val)
        return out
    return v.strip("'\"")


def _minimal_parse(text: str) -> dict:
    """Parse the constrained subset of YAML that workflows.yaml uses."""
    workflows: dict = {}
    cur_wf = cur_step = None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        line = raw.strip()
        if indent == 0:
            continue  # the top-level `workflows:` key
        if indent == 2 and line.endswith(":"):  # workflow name
            cur_wf = line[:-1]
            workflows[cur_wf] = {"steps": []}
            cur_step = None
        elif indent == 4 and cur_wf:  # workflow-level key
            if line == "steps:":
                continue
            key, _, val = line.partition(":")
            workflows[cur_wf][key.strip()] = _scalar(val)
        elif indent == 6 and line.startswith("- "):  # new step
            cur_step = {}
            workflows[cur_wf]["steps"].append(cur_step)
            key, _, val = line[2:].partition(":")
            cur_step[key.strip()] = _scalar(val)
        elif indent == 8 and cur_step is not None:  # step key
            key, _, val = line.partition(":")
            cur_step[key.strip()] = _scalar(val)
    return workflows


def parse_terminal_line() -> dict[str, str]:
    """Read context.md's 'Terminal agent by workflow:' line into {workflow: agent}.

    Tolerant: segments it can't map are skipped. Returns {} if the line is gone."""
    mapping: dict[str, str] = {}
    for line in CONTEXT.read_text(encoding="utf-8").splitlines():
        if not line.startswith("Terminal agent by workflow:"):
            continue
        body = line.split(":", 1)[1]
        for seg in body.split(";"):
            if "→" not in seg:
                continue
            left, right = seg.split("→", 1)
            display = re.sub(r"\(.*?\)", "", right).strip().rstrip(".").strip()
            agent = DISPLAY_TO_AGENT.get(display)
            if not agent:
                continue
            for wf in left.split("/"):
                wf = wf.strip()
                if wf:
                    mapping[wf] = agent
    return mapping


def main() -> int:
    workflows = load_workflows()
    if not isinstance(workflows, dict) or not workflows:
        print(f"error: no workflows parsed from {WORKFLOWS}")
        return 1

    problems: list[tuple[str, str]] = []  # (workflow-or-'-', message)

    readme_text = README.read_text(encoding="utf-8")
    terminal_map = parse_terminal_line()
    notes: list[str] = []
    if not terminal_map:
        notes.append(
            "context.md 'Terminal agent by workflow:' line not found — "
            "skipped the terminal-agent cross-check."
        )

    all_agents: set[str] = set()

    for name, wf in workflows.items():
        if not isinstance(wf, dict):
            problems.append((name, "workflow is not a mapping"))
            continue

        for key in ("branch_prefix", "needs_backlog", "terminal_agent", "steps"):
            if key not in wf:
                problems.append((name, f"missing required key '{key}'"))

        if not isinstance(wf.get("needs_backlog"), bool):
            problems.append((name, "needs_backlog must be true/false"))

        steps = wf.get("steps") or []
        if not steps:
            problems.append((name, "has no steps"))
            continue

        seen_ids: list[str] = []
        step_agents: list[str] = []
        for i, step in enumerate(steps):
            sid = step.get("id")
            agent = step.get("agent")
            if not sid:
                problems.append((name, f"step #{i + 1} missing 'id'"))
            if not agent:
                problems.append((name, f"step '{sid or i + 1}' missing 'agent'"))
                continue
            if sid in seen_ids:
                problems.append((name, f"duplicate step id '{sid}'"))
            seen_ids.append(sid)
            step_agents.append(agent)
            all_agents.add(agent)

            ob = step.get("on_block")
            if ob:
                target = ob.get("loop_back_to")
                if target not in seen_ids:
                    problems.append(
                        (
                            name,
                            f"step '{sid}' on_block.loop_back_to '{target}' "
                            "is not an earlier step id",
                        )
                    )
                mr = ob.get("max_rounds")
                if not isinstance(mr, int) or mr < 1:
                    problems.append(
                        (name, f"step '{sid}' on_block.max_rounds must be a positive int")
                    )

        terminal = wf.get("terminal_agent")
        if terminal and terminal not in step_agents:
            problems.append(
                (
                    name,
                    f"terminal_agent '{terminal}' is not one of this "
                    f"workflow's step agents ({', '.join(step_agents)})",
                )
            )

        expected = terminal_map.get(name)
        if expected and terminal and expected != terminal:
            problems.append(
                (
                    name,
                    f"terminal_agent '{terminal}' disagrees with context.md, "
                    f"which says the {name} terminal is '{expected}'",
                )
            )

    # Filesystem + roster checks, once per distinct agent.
    for agent in sorted(all_agents):
        if not (COMMANDS_DIR / f"{agent}.md").is_file():
            problems.append(("-", f"agent '{agent}': no .claude/commands/{agent}.md binding"))
        if not (PROMPTS_DIR / f"{agent}.md").is_file():
            problems.append(("-", f"agent '{agent}': no .agents/prompts/{agent}.md prompt"))
        if not re.search(rf"/{re.escape(agent)}\b", readme_text):
            problems.append(
                ("-", f"agent '{agent}': not rostered in .agents/README.md (no /{agent})")
            )

    for note in notes:
        print(f"note: {note}")

    if not problems:
        print(
            f"Workflows clean: {len(workflows)} workflow(s), "
            f"{len(all_agents)} agent(s) — all wiring and docs consistent."
        )
        return 0

    print(f"\n==> Found {len(problems)} workflow inconsistency(ies):\n")
    for scope, msg in problems:
        prefix = f"[{scope}] " if scope != "-" else ""
        print(f"    {prefix}{msg}")
    print(
        "\nFix workflows.yaml, the .claude/commands/ bindings, or the "
        "README.md / context.md tables so they agree."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
