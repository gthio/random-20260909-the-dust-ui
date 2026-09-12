#!/usr/bin/env python3
"""Check that an intake's human gate is clear before its route runs.

For each intake record (default: every `.docs/requirements/*-intake-*.md`):

  - the answer sheet named in the record's Metadata (`Answers:`), or
    `<ID>-answers-<short-name>.md` beside it, must exist;
  - every **blocking** question in the sheet must carry an `Answer:`
    (retired questions are skipped);
  - no `<TBD Q-NN …>` marker may remain in any draft the record's § 6 lists
    (a bare `<TBD>` with no Q-NN is only warned about — it is usually the
    template's own instruction sentence, not a placeholder).

Also warns when an answered question is still `Status: open` — the answer
has not been folded in yet (re-run `/intake <record>`).

Exit 1 if any check fails, so this can gate a route or a CI job.

Usage:
  python3 .agents/check-intake.py [record.md ...]
"""
from __future__ import annotations

import glob
import re
import sys
from pathlib import Path

REQ = Path(".docs/requirements")


def find_answers_path(record: Path, text: str) -> Path:
    m = re.search(r"^Answers:\s*(\S+)", text, re.M)
    if m:
        return Path(m.group(1))
    return record.with_name(record.name.replace("-intake-", "-answers-"))


def parse_answer_sheet(text: str) -> list[dict]:
    """Return one dict per `### Q-NN` block: id, blocking, status, answer."""
    blocks: list[dict] = []
    section = None
    cur: dict | None = None
    body: list[str] = []

    def close() -> None:
        if cur is None:
            return
        joined = "\n".join(body)
        ans = re.search(r"\*\*Answer:\*\*(.*?)(?=\n\*\*Rationale:\*\*|\Z)", joined, re.S)
        cur["answer"] = ans.group(1).strip() if ans else ""
        st = re.search(r"\*\*Status:\*\*\s*([a-z]+)", joined)
        cur["status"] = st.group(1) if st else "open"
        blocks.append(cur)

    for line in text.splitlines():
        if line.startswith("## "):
            close()
            cur, body = None, []
            section = line[3:].strip().lower()
            continue
        m = re.match(r"^### (Q-\d+)", line)
        if m:
            close()
            cur = {"id": m.group(1), "blocking": section == "blocking"}
            body = []
            continue
        if cur is not None:
            body.append(line)
    close()
    return blocks


def drafts_listed(record_text: str, record: Path, answers: Path) -> list[Path]:
    paths = set()
    for m in re.finditer(r"`(\.docs/requirements/[^`]+\.md)`", record_text):
        p = Path(m.group(1))
        if p not in (record, answers) and p.exists():
            paths.add(p)
    return sorted(paths)


def check_record(record: Path) -> list[str]:
    problems: list[str] = []
    text = record.read_text(encoding="utf-8")
    answers = find_answers_path(record, text)
    if not answers.exists():
        return [f"{record}: answer sheet missing: {answers}"]

    for q in parse_answer_sheet(answers.read_text(encoding="utf-8")):
        if q["status"] == "retired":
            continue
        if q["blocking"] and not q["answer"]:
            problems.append(f"{answers}: blocking {q['id']} has no Answer")
        elif q["answer"] and q["status"] == "open":
            print(f"warning: {answers}: {q['id']} answered but not folded in — re-run /intake {record}")

    for draft in drafts_listed(text, record, answers):
        for i, line in enumerate(draft.read_text(encoding="utf-8").splitlines(), 1):
            for m in re.finditer(r"<TBD[^>]*>", line):
                if re.match(r"<TBD\s+Q-\d+", m.group(0)):
                    problems.append(f"{draft}:{i}: {m.group(0)}")
                else:
                    print(f"warning: {draft}:{i}: bare {m.group(0)} — prose, or a marker missing its Q-NN")
    return problems


def main(argv: list[str]) -> int:
    records = [Path(a) for a in argv] or [Path(p) for p in sorted(glob.glob(str(REQ / "*-intake-*.md")))]
    if not records:
        print("no intake records found")
        return 0
    failed = False
    for rec in records:
        problems = check_record(rec)
        if problems:
            failed = True
            print(f"\n{rec}: gate NOT clear")
            for p in problems:
                print(f"  - {p}")
        else:
            print(f"{rec}: gate clear")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
