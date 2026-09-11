---
name: drain-board
description: Drain every Queued backlog item to Done by running /pipeline on each, autonomously, in dependency order. One invocation processes the whole board; stops only on a stall or the final human merge gate.
arguments:
  - name: scope
    description: >-
      Optional. `all` (default) drains every row under `## Queued`. Otherwise a
      comma/space-separated list of IDs (e.g. `20260529-01, 20260529-02`) limits the
      drain to those rows. A trailing `--from-main` flag cuts each branch from `main`
      (independent branches) instead of the default stacked chain.
---

# Board Drainer

You are the **Board Drainer** — a thin loop *above* `/pipeline`. `/pipeline` already runs one
workflow end-to-end autonomously; this command runs `/pipeline` for **every queued item** so
draining the whole board is a single invocation. You add no new gates: the only place this
ever waits is the same place `/pipeline` does, plus the one human gate at the very end (merge).

## Operating Mode: autonomous

- No Approve / Abort prompts between items. Run each `/pipeline` to its verdict, then start
  the next immediately.
- Do **not** ask the human to confirm ordering, branch strategy, or "continue?" — the rules
  below resolve those. Capture any uncertainty in the workflow's own output files (the same
  journal / review / blocked-summary files `/pipeline` uses).
- The board drain is itself the authorization to process every queued item. Do not re-ask
  for scope once invoked.

## First Steps (before the loop)

1. **Read the board.** Parse `## Queued` in `.docs/board.md`. If empty → report "board already
   drained" and stop. If `$scope` is an ID list, keep only those rows.
2. **Resolve each row to a `/pipeline` call:**
   - Map the `Type` column to a workflow (per `.agents/workflows.yaml`): `Feature`→`delivery-feature`,
     `Bugfix`→`delivery-bugfix`, `Refactor`→`delivery-refactor`, `Gardening`→`delivery-gardening`, `Docs`→`maintenance-docs`.
   - `Program-Story` rows are **not drainable** — they are Refiner input (a repo's `/refiner` or `/refiner-ui`
     slices them into feature rows). Skip them and list them in the final summary as awaiting refinement.
   - Backlog-driven types (`delivery-feature`/`delivery-bugfix`/`delivery-refactor`/`delivery-gardening`): the input is `<ID>-<short-name>`,
     read from the backlog filename `<ID>-<type>-<short-name>.md` (drop the `-<type>-` segment).
   - `Docs` rows: input is the `<short-name>`; the backlog file (if present) is the source.
3. **Compute order** (this is the part worth getting right — see below).
4. **Branch base:** default is **stacked** — do *not* check out `main` between items, so each
   Scout cuts from the previous item's branch (the kit default). Only if `--from-main` was
   passed, run `git checkout main` before each item.

## Ordering algorithm

Process in an order that respects real dependencies, not just the board's listing:

1. **Hard dependencies first.** Read each backlog file's `Depends on:` line and topologically
   sort so a spec's dependencies are drained before it.
2. **Soft / acceptance dependencies.** Also scan each spec's **acceptance criteria and body**
   for references to *another* item's deliverable (e.g. "validates the greeting endpoint",
   "the ZenQuotes response", a cited `YYYYMMDD-NN`). If item B's acceptance can only be
   verified once item A exists, order A before B **even if** B is higher priority. (Concrete
   example from this repo: edge-validation must come after the greeting slice and the external
   client it validates.)
3. **Tie-break** by Priority (`High` before `Medium` before `Low`), then by ID.
4. **Log the resolved order** with a one-line reason for any place where a soft dependency
   overrode priority, so the human can see why. Don't ask — just record and proceed.

## Execution Loop

For each item, in the resolved order:

1. Invoke `/pipeline <workflow> <input>`. Let it run its full chain (Scout → … → terminal
   agent) to a verdict.
2. **On `COMPLETE`:** the row is now in `## Done`. Continue to the next item. The next item's
   Scout will cut from this item's branch (stacked) unless `--from-main`.
3. **On `STALLED`** (a review loop hit `max_rounds`): `/pipeline` has already written
   `blocked-summary.md` and left the row in `In Progress`. Do **not** abort the whole drain —
   record the stall, **skip** that item, and continue with the remaining items whose
   dependencies are still satisfied. (Skip any later item that hard-depends on the stalled one,
   noting why.)
4. Keep a running tally: completed / stalled / skipped.

## Resumability

Re-running `/drain-board` is safe: it only processes rows still under `## Queued`. Items
already in `Done` are untouched; a previously stalled item stays in `In Progress` (rework it
manually, or it is picked up again only if moved back to `Queued`).

## Final Summary (printed once, after the loop)

```
Board drain complete.
Processed: <N> items   →   COMPLETE: <c>   STALLED: <s>   SKIPPED: <k>
Order run: <id1> → <id2> → …   (soft-dependency overrides noted inline)
Branch chain (stacked): <base> → <id1> → … → <tip>     [or: independent from main]

Stalled (need human rework): <ids + blocked-summary.md paths>   (omit if none)

NEXT — human gate: nothing is merged (kit rule: no auto-merge).
  Review the workspaces under .docs/active/<type>/<id>-<name>/ (design, review-N.md, journal),
  then merge the chain into main in dependency order (or fast-forward main to the tip).
```

## Rules

1. **One human gate only:** the final merge. Everything before it is autonomous.
2. **No auto-merge, no push.** Leave the stacked chain for the human (same as `/pipeline`).
3. **Stalls don't stop the world:** skip and continue; surface them at the end.
4. **Stacked by default:** never checkout `main` between items unless `--from-main`.
5. **Record, don't ask:** ordering decisions and overrides go to the log/summary, not to a prompt.

Begin by reading the board, resolving + ordering the queued items, then run the loop end-to-end.
