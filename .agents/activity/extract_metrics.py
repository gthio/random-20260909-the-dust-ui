#!/usr/bin/env python3
"""Derive workflow-effectiveness metrics from the kit's own markdown artifacts.

The qualitative trail the agents already produce carries the signal we need;
this script parses it back out. It reads every workflow workspace under
`.docs/active/` and `.docs/archive/`, joins the raw event stream written by
`log_event.py`, and writes two committed artifacts:

    .docs/activity/metrics/runs.jsonl   one JSON row per workflow run
    .docs/activity/metrics/summary.md   human-readable aggregates

What is parsed (no agent prompt has to change):

  * journal.md  -> type / branch / branch source / start date, rework rounds
                   (`## Resolutions — Round N` headings), agent phases,
                   cited rule codes (e.g. CFG-003).
  * review-N.md -> latest verdict (APPROVED / NEEDS CHANGES / REJECTED) and
                   BLOCKER / WARNING / NOTE counts from the Issues-Found table.
  * board.md    -> completion dates for the Done rows.
  * events/*.jsonl (Layer 1) -> per-run tool-call volume + failed-tool rate,
                   joined by the branch-derived run id.

Stdlib only; safe to run anytime; degrades to an empty report when there is no
completed work yet (mirrors Housekeeper's stop-on-empty behaviour).

Usage:
    python3 .agents/activity/extract_metrics.py [--root PATH]
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
from collections import Counter
from datetime import date
from pathlib import Path

# Workspace directory name -> workflow type (README "Branches & Storage").
TYPE_DIR_TO_TYPE = {
    "features": "feature",  # legacy pre-rename dirs (types now carry the delivery- prefix)
    "bugfix": "bugfix",
    "refactor": "refactor",
    "gardening": "gardening",
    "delivery-feature": "delivery-feature",
    "delivery-bugfix": "delivery-bugfix",
    "delivery-refactor": "delivery-refactor",
    "delivery-gardening": "delivery-gardening",
    "advice": "advice",  # legacy pre-rename runs (type is now auditor-strategy)
    "auditor-strategy": "auditor-strategy",
    "auditor-principle": "auditor-principle",
    "updates": "docs",  # legacy pre-rename dir (type is now maintenance-docs)
    "maintenance-docs": "maintenance-docs",
    "spec": "spec",
}

SEVERITIES = ("BLOCKER", "WARNING", "NOTE")

_HEADER_RE = {
    "type": re.compile(r"_Type:_\s*`?([a-z][a-z-]*)`?", re.I),
    "branch": re.compile(r"_Branch:_\s*`?([^`\n]+)`?"),
    "branch_source": re.compile(r"_Branch Source:_\s*`?([^`\n]+)`?"),
    "started": re.compile(r"_Started:_\s*`?(\d{8})`?"),
}
_REWORK_RE = re.compile(r"^##\s+Resolutions.*Round", re.M)
_PHASE_RE = re.compile(r"^##\s+\[([^\]]+)\]", re.M)
_CODE_RE = re.compile(r"\b[A-Z]{2,5}-\d{2,3}\b")
_STATUS_RE = re.compile(r"\*\*Status:\*\*\s*`?([A-Z][A-Z ]+?)`?\s*$", re.M)
_ID_RE = re.compile(r"^(\d{8}-\d{2,3})")
_DONE_HEADER_RE = re.compile(r"^##\s+Done", re.M)


def _read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def _count_severities(review_text: str) -> dict[str, int]:
    """Count BLOCKER/WARNING/NOTE that appear as a standalone cell in a table row.

    Restricting to `|`-delimited cells skips the severity *legend* (which uses
    `- ` bullets) and the unfilled template placeholder ("BLOCKER / WARNING /
    NOTE", which is one cell and matches no single token).
    """
    counts = dict.fromkeys(SEVERITIES, 0)
    for line in review_text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|")]
        for sev in SEVERITIES:
            if sev in cells:
                counts[sev] += 1
    return counts


def _review_paths(run_dir: Path) -> list[Path]:
    """All review files for a run, ordered review-1, review-2, … (latest last)."""
    return sorted((p for p in run_dir.glob("*review*.md")), key=lambda p: p.name)


def _parse_board_completions(root: Path) -> dict[str, str]:
    """Map run ID -> Completed date from the board's Done section."""
    board = root / ".docs" / "board.md"
    text = _read(board)
    if not text:
        return {}
    m = _DONE_HEADER_RE.search(text)
    if not m:
        return {}
    done_section = text[m.end() :]
    completions: dict[str, str] = {}
    for line in done_section.splitlines():
        if line.lstrip().startswith("##"):  # next section
            break
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip() for c in line.split("|") if c.strip()]
        if not cells:
            continue
        id_match = _ID_RE.match(cells[0])
        if id_match and len(cells) >= 1:
            date_cell = next((c for c in reversed(cells) if re.search(r"\d{8}", c)), "")
            dm = re.search(r"(\d{8})", date_cell)
            completions[id_match.group(1)] = dm.group(1) if dm else ""
    return completions


def _days_between(start: str, end: str) -> int | None:
    try:
        s = date(int(start[:4]), int(start[4:6]), int(start[6:8]))
        e = date(int(end[:4]), int(end[4:6]), int(end[6:8]))
        return (e - s).days
    except Exception:
        return None


def collect_runs(root: Path, completions: dict[str, str]) -> list[dict]:
    runs: list[dict] = []
    roots = [root / ".docs" / "active", root / ".docs" / "archive"]
    for base in roots:
        if not base.is_dir():
            continue
        for journal in base.rglob("journal.md"):
            run_dir = journal.parent
            type_dir = run_dir.parent.name
            run_name = run_dir.name
            archived = "archive" in journal.parts
            archive_ts = ""
            if archived:
                parts = journal.parts
                idx = parts.index("archive")
                if idx + 1 < len(parts):
                    archive_ts = parts[idx + 1]

            jtext = _read(journal)
            run_type = TYPE_DIR_TO_TYPE.get(type_dir)
            tm = _HEADER_RE["type"].search(jtext)
            if tm:
                run_type = tm.group(1).lower()
            branch = ""
            bm = _HEADER_RE["branch"].search(jtext)
            if bm:
                branch = bm.group(1).strip()
            branch_source = ""
            bsm = _HEADER_RE["branch_source"].search(jtext)
            if bsm:
                branch_source = bsm.group(1).strip()
            started = ""
            sm = _HEADER_RE["started"].search(jtext)
            if sm:
                started = sm.group(1)

            # Verdict reflects the final state (latest review); issue counts and
            # cited codes are aggregated across every round so blockers that
            # drove rework are not hidden by a clean final review.
            review_texts = [_read(p) for p in _review_paths(run_dir)]
            verdict = None
            if review_texts:
                vm = _STATUS_RE.search(review_texts[-1])
                if vm:
                    verdict = vm.group(1).strip()
            issues = dict.fromkeys(SEVERITIES, 0)
            for rt in review_texts:
                for sev, n in _count_severities(rt).items():
                    issues[sev] += n
            codes = sorted(set(_CODE_RE.findall("\n".join([jtext, *review_texts]))))

            id_match = _ID_RE.match(run_name)
            run_id = id_match.group(1) if id_match else run_name
            completed = completions.get(run_id, "")
            if not completed and archive_ts:
                completed = archive_ts[:8]

            runs.append(
                {
                    "id": run_id,
                    "run": run_name,
                    "type": run_type,
                    "branch": branch,
                    "branch_source": branch_source,
                    "archived": archived,
                    "started": started or None,
                    "completed": completed or None,
                    "time_to_done_days": _days_between(started, completed)
                    if started and completed
                    else None,
                    "rework_rounds": len(_REWORK_RE.findall(jtext)),
                    "verdict": verdict,
                    "issues": issues,
                    "phases": _PHASE_RE.findall(jtext),
                    "rule_codes": codes,
                }
            )
    runs.sort(key=lambda r: (r["id"], r["run"]))
    return runs


def load_events(root: Path) -> list[dict]:
    events: list[dict] = []
    base = root / ".docs" / "activity" / "events"
    if not base.is_dir():
        return events
    for f in sorted(base.glob("*.jsonl")):
        for line in _read(f).splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except Exception:
                continue
    return events


def attach_events(runs: list[dict], events: list[dict]) -> None:
    by_run: dict[str, list[dict]] = {}
    for e in events:
        by_run.setdefault(e.get("run_id", ""), []).append(e)
    for run in runs:
        ev = by_run.get(run["run"], [])
        if not ev:
            continue
        tools = Counter(e["tool"] for e in ev if e.get("tool"))
        run["events"] = {
            "count": len(ev),
            "failed_tools": sum(1 for e in ev if e.get("ok") is False),
            "top_tools": dict(tools.most_common(5)),
        }


def _md_table(headers: list[str], rows: list[list[str]]) -> str:
    out = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


def build_summary(runs: list[dict], events: list[dict]) -> str:
    today = date.today().isoformat()
    lines = ["# Activity Summary\n", f"_Generated: {today} — `extract_metrics.py`_\n"]

    if not runs and not events:
        lines.append(
            "\nNo completed workflow runs or activity events yet. This report "
            "populates after the first workflow finishes (and the events log "
            "starts collecting once the `.claude/settings.json` hooks are "
            "active).\n"
        )
        return "\n".join(lines)

    # --- run-level aggregates ---
    by_type = Counter(r["type"] for r in runs)
    archived = sum(1 for r in runs if r["archived"])
    lines.append("\n## Runs\n")
    lines.append(f"- Total: **{len(runs)}** ({archived} archived, {len(runs) - archived} active)")
    if by_type:
        lines.append("- By type: " + ", ".join(f"{t}={n}" for t, n in sorted(by_type.items())))

    # rework by type
    rework_rows = []
    for t in sorted(by_type):
        vals = [r["rework_rounds"] for r in runs if r["type"] == t]
        if vals:
            rework_rows.append([t, len(vals), round(sum(vals) / len(vals), 2), max(vals)])
    if rework_rows:
        lines.append("\n## Rework rounds by type\n")
        lines.append(_md_table(["Type", "Runs", "Avg rounds", "Max"], rework_rows))

    # verdicts
    verdicts = Counter(r["verdict"] for r in runs if r["verdict"])
    if verdicts:
        lines.append("\n## Reviewer verdicts\n")
        lines.append(_md_table(["Verdict", "Count"], [[v, n] for v, n in verdicts.most_common()]))

    # issues totals
    totals = {sev: sum(r["issues"].get(sev, 0) for r in runs) for sev in SEVERITIES}
    if any(totals.values()):
        lines.append("\n## Issues found (all runs)\n")
        lines.append(_md_table(["Severity", "Total"], [[s, totals[s]] for s in SEVERITIES]))

    # cited rule codes (principle hotspots)
    codes = Counter(c for r in runs for c in r["rule_codes"])
    if codes:
        lines.append("\n## Most-cited rule codes (principle hotspots)\n")
        lines.append(_md_table(["Code", "Times cited"], [[c, n] for c, n in codes.most_common(10)]))

    # time to done
    ttd = [r["time_to_done_days"] for r in runs if r["time_to_done_days"] is not None]
    if ttd:
        lines.append("\n## Time to done (days)\n")
        lines.append(
            _md_table(
                ["Min", "Median", "Max", "Runs"],
                [[min(ttd), round(statistics.median(ttd), 1), max(ttd), len(ttd)]],
            )
        )

    # --- raw activity ---
    if events:
        tools = Counter(e["tool"] for e in events if e.get("tool"))
        tool_calls = sum(tools.values())
        failed = sum(1 for e in events if e.get("ok") is False)
        sessions = len({e.get("session") for e in events if e.get("session")})
        lines.append("\n## Raw activity (Layer 1)\n")
        lines.append(f"- Events captured: **{len(events)}** across {sessions} session(s)")
        lines.append(
            f"- Tool calls: **{tool_calls}**, failed: **{failed}** "
            f"({(100 * failed / tool_calls):.1f}% fail rate)"
            if tool_calls
            else "- Tool calls: 0"
        )
        if tools:
            lines.append(
                "\n" + _md_table(["Tool", "Calls"], [[t, n] for t, n in tools.most_common(10)])
            )

    lines.append("")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", default=".", help="Repo root (defaults to cwd)")
    args = ap.parse_args()
    root = Path(args.root).resolve()

    completions = _parse_board_completions(root)
    runs = collect_runs(root, completions)
    events = load_events(root)
    attach_events(runs, events)

    out_dir = root / ".docs" / "activity" / "metrics"
    out_dir.mkdir(parents=True, exist_ok=True)
    with (out_dir / "runs.jsonl").open("w", encoding="utf-8") as fh:
        for run in runs:
            fh.write(json.dumps(run, ensure_ascii=False) + "\n")
    (out_dir / "summary.md").write_text(build_summary(runs, events), encoding="utf-8")

    print(f"Wrote {len(runs)} run(s) and {len(events)} event(s) to {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
