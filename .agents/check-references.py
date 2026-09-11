#!/usr/bin/env python3
"""Check that the chassis's references into the knowledge repo actually resolve.

The dev-kit's prompts and templates point outward at the external
engineering-principles knowledge repo — principle slugs, rule codes, and file
paths. This linter loads that repo's machine-readable `principles.json`
manifest and verifies every outbound reference resolves. It is the outbound
twin of `check-chassis.sh` (which guards against stack specifics leaking *in*);
this guards against references pointing *out* at things that don't exist.

It would have caught both reference bugs found in the knowledge-repo revamp:
a prompt naming a test "skeleton" the knowledge repo never had, and a template
still pointing at a deleted `architecture.md`.

What it validates (scanning every `.md` under `.agents/`, plus `readme.md`):

  - principle / note slugs   `<slug>` principle|note   → must be a slug in principles.json
  - rule codes               CFG-003                    → if the prefix is a real
                             code_prefix (CFG, TST, …), the full code must exist
                             (codes with an unknown prefix — e.g. ADR — are ignored)
  - file paths               README-AGENT.md,           → must exist in the knowledge repo
                             principles/<x>.md,
                             stack-notes/<...>

What it can't validate: prose anchors like a named section inside a doc
("the Core logic test skeleton"). Reference principles by slug + rule code or
§N (the knowledge repo's own citation convention) to keep refs machine-checkable.

Lines containing `reference-allow` are exempt — use only for intentional or
aspirational references (e.g. a doc naming a knowledge-repo path you intend
to add later, like a not-yet-created `stack-notes/<stack>/` set).

Knowledge-repo location, in priority order:
  1. --knowledge-repo PATH
  2. $KNOWLEDGE_REPO
  3. auto-detect — a sibling directory containing both principles.json and
     README-AGENT.md

Usage:
  python3 .agents/check-references.py [--knowledge-repo PATH]

Exit 0 if every reference resolves, 1 otherwise.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Files the agents read at run time, plus the human-facing readme.
SCAN_GLOBS = sorted((REPO_ROOT / ".agents").rglob("*.md"))
if (REPO_ROOT / "readme.md").exists():
    SCAN_GLOBS.append(REPO_ROOT / "readme.md")

ALLOW_MARKER = "reference-allow"

# `<slug>` immediately before the word "principle" or "note" (singular/plural).
SLUG_RE = re.compile(r"`([a-z][a-z0-9-]+)`\s+(?:principle|note)s?\b")
# A rule code such as CFG-003. Prefix is matched broadly, then filtered to
# real code_prefixes so unrelated IDs (ADR-007, RFC-2119) are ignored.
CODE_RE = re.compile(r"\b([A-Z]{2,5})-(\d{2,3})\b")
# Explicit paths into the knowledge repo.
PATH_RE = re.compile(
    r"\b(README-AGENT\.md|principles/[A-Za-z0-9_-]+\.md|stack-notes/[A-Za-z0-9_./-]+)"
)


def find_knowledge_repo(explicit: str | None) -> Path:
    candidates: list[Path] = []
    if explicit:
        candidates = [Path(explicit).expanduser()]
    elif os.environ.get("KNOWLEDGE_REPO"):
        candidates = [Path(os.environ["KNOWLEDGE_REPO"]).expanduser()]
    else:
        # Auto-detect: a sibling dir with the knowledge-repo signature.
        found = [
            sib
            for sib in sorted(REPO_ROOT.parent.iterdir())
            if sib.is_dir()
            and (sib / "principles.json").is_file()
            and (sib / "README-AGENT.md").is_file()
        ]
        if not found:
            sys.exit(
                "error: could not locate the knowledge repo.\n"
                "  Pass --knowledge-repo PATH or set $KNOWLEDGE_REPO.\n"
                "  (Looked for a sibling dir containing principles.json + README-AGENT.md.)"
            )
        if len(found) > 1:
            listed = "\n  ".join(str(p) for p in found)
            sys.exit(
                "error: multiple knowledge-repo candidates found; pass --knowledge-repo:\n  "
                + listed
            )
        candidates = found

    kr = candidates[0].resolve()
    if not (kr / "principles.json").is_file():
        sys.exit(f"error: {kr}/principles.json not found — is this the knowledge repo?")
    return kr


def load_manifest(kr: Path) -> tuple[set[str], set[str], set[str]]:
    data = json.loads((kr / "principles.json").read_text(encoding="utf-8"))
    principles = data.get("principles", [])
    slugs = {p["slug"] for p in principles}
    prefixes = {p["code_prefix"] for p in principles}
    codes = {
        rule["code"] for p in principles for rule in p.get("rules", []) if not rule.get("removed")
    }
    return slugs, prefixes, codes


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--knowledge-repo", help="Path to the engineering-principles knowledge repo")
    args = ap.parse_args()

    kr = find_knowledge_repo(args.knowledge_repo)
    slugs, prefixes, codes = load_manifest(kr)

    # violation kind -> list of (file, lineno, detail)
    bad_slugs: list[tuple[str, int, str]] = []
    bad_codes: list[tuple[str, int, str]] = []
    bad_paths: list[tuple[str, int, str]] = []
    checked = 0

    for path in SCAN_GLOBS:
        rel = path.relative_to(REPO_ROOT)
        for n, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if ALLOW_MARKER in line:
                continue

            for m in SLUG_RE.finditer(line):
                slug = m.group(1)
                checked += 1
                if slug not in slugs:
                    bad_slugs.append((str(rel), n, slug))

            for m in CODE_RE.finditer(line):
                prefix, code = m.group(1), m.group(0)
                if prefix not in prefixes:
                    continue  # not a knowledge-repo code (e.g. ADR-007)
                checked += 1
                if code not in codes:
                    bad_codes.append((str(rel), n, code))

            for m in PATH_RE.finditer(line):
                ref = m.group(1)
                checked += 1
                if not (kr / ref).exists():
                    bad_paths.append((str(rel), n, ref))

    def report(title: str, hint: str, rows: list[tuple[str, int, str]]) -> None:
        print(f"==> {title}")
        for f, n, detail in rows:
            print(f"    {f}:{n}: {detail}")
        print(f"    {hint}\n")

    total = len(bad_slugs) + len(bad_codes) + len(bad_paths)
    if total == 0:
        print(f"References clean: {checked} reference(s) into {kr.name} all resolve.")
        return 0

    print(f"Knowledge repo: {kr}\n")
    if bad_slugs:
        report(
            "Unknown principle/note slug — no such principle in principles.json",
            "Use a real slug (see the Slug column of README-AGENT.md), or tag the line 'reference-allow'.",
            bad_slugs,
        )
    if bad_codes:
        report(
            "Unknown rule code — prefix is real but the code does not exist",
            "Fix the code, or tag the line 'reference-allow'.",
            bad_codes,
        )
    if bad_paths:
        report(
            "Broken path — file does not exist in the knowledge repo",
            "Fix the path, or tag the line 'reference-allow' if it is aspirational.",
            bad_paths,
        )
    print(f"Found {total} unresolved reference(s) into the knowledge repo.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
