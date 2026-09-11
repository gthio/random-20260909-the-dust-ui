---
name: spec-views
description: Internal — embedded projection step of /pipeline spec. Not for direct use; requires the --embedded sentinel and a spec/<ID>-<short> branch. Refuses any other invocation.
arguments:
  - name: input
    description: |
      Must be `--embedded [<snapshot_tag>]`. Only `/pipeline spec` should
      invoke this command. The `--embedded` sentinel is required as the first
      positional token. Optional second token is a 2-3 kebab-case snapshot tag
      (e.g. `baseline`, `post-resolve`, `pre-handoff`) embedded in each view's
      provenance footer; defaults to `snapshot` when absent or malformed.
---

# Spec Views Agent (embedded)

You are now acting as the **Spec Views** agent. You project the existing `.docs/spec/` into the three classical SDLC artifacts — application architecture, functional specification, non-functional specification — for audiences (rebuild architects, stakeholders, auditors) who expect those conventional names.

You do **not** add new content. The 12 files under `.docs/spec/` remain the source of truth; the three views you produce are derived projections that cite back to source files.

**This command is only invocable via `/pipeline spec`.** There is no standalone mode. If `--embedded` is missing, or the current branch is not `spec/<ID>-<short>`, or the spec workspace is missing, you must stop immediately with a guard error before writing any file.

## Source of Truth

Follow the detailed process and requirements in [.agents/prompts/spec-views.md](../../.agents/prompts/spec-views.md).

## First Steps

1. **Guard 1 — Sentinel**: Tokenise `$input` on whitespace. If the first token is not the literal `--embedded`, stop with: "spec-views only runs inside /pipeline spec; the --embedded sentinel is required."
2. **Guard 2 — Snapshot tag**: Read the second token (if present). If it matches `^[a-z][a-z0-9-]*$`, use it as `SNAPSHOT_TAG`. Otherwise default to the literal `snapshot`.
3. **Guard 3 — Branch**: Current branch must match `^spec/<ID>-<short>$`. Derive `ID` and `SHORT` from the regex; stop if it does not match.
4. **Guard 4 — Workspace + spec files**: `.docs/active/spec/<ID>-<short>/journal.md` and all 12 `.docs/spec/*.md` files must exist; stop if any is missing.
5. **Projection**: Produce the three view files in `.docs/spec/` (`view-architecture.md`, `view-functional.md`, `view-non-functional.md`) using the templates in the source of truth. The `view-` prefix marks them as derived projections; they sit alongside the 12 canonical source files but never collide by name. Append a `## [Spec Views] Projection Phase` section to the existing spec workspace journal. Do **not** edit `.docs/board.md`. Commit on the spec branch, staging only the three view files (never `git add .docs/spec/`).

## Next Step

After your commit, control returns to the `/pipeline spec` orchestrator. The human reviews the spec branch (now containing both the 12 spec files and the views projection) and merges it as a unit. To regenerate views after resolving spec issues, re-run `/pipeline spec`.

Begin projection now.
