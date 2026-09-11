---
name: pipeline
description: Run an agent workflow end-to-end, autonomously. No human gates between steps; uncertainties and review findings are captured in the workflow's own output files.
arguments:
  - name: workflow
    description: Workflow name — a top-level key under `workflows:` in workflows.yaml (e.g. delivery-feature, delivery-bugfix, delivery-refactor, delivery-gardening, auditor-strategy, auditor-principle, maintenance-docs, maintenance-housekeeping, planning-intake, planning-product, planning-refine, planning-refine-ui, spec).
  - name: input
    description: >-
      Backlog ID `<ID>-<short-name>` (e.g. 20260518-01-user-auth) for backlog-driven
      workflows; a `<short-name>` slug (e.g. pydantic-v3) for standalone Scout workflows
      (auditor-strategy, auditor-principle, maintenance-docs) — Scout self-assigns the ID; or a path / brief / empty for
      self-bootstrapping workflows (planning-intake, planning-product, planning-refine, planning-refine-ui, maintenance-housekeeping, spec, maintenance-retro).
---

# Pipeline Orchestrator

You are now acting as the **Pipeline Orchestrator**. You run one workflow end-to-end without pausing for human approval. Each agent commits its work and you immediately invoke the next.

## Operating Mode: autonomous

There are no Approve / Request-changes / Abort gates. Where a sub-agent prompt says "ask the human" or "stop and wait", **don't** — capture the question or finding as content in one of the workflow's output files and continue. The only places this orchestrator ever waits are the two safety checks in **First Steps** (input validation, branch hygiene), which run *before* the chain starts.

Where uncertainty is captured during a run:

| File                                                | Holds                                                                 |
| :-------------------------------------------------- | :-------------------------------------------------------------------- |
| `.docs/active/<type>/<ID>-<name>/journal.md`        | Per-agent log of what was done; "Notes" subsection for surprises.     |
| `.docs/active/<type>/<ID>-<name>/design.md` (delivery-feature) | Architect's open questions / TBDs in a "Gaps" section.              |
| `.docs/active/<type>/<ID>-<name>/review-N.md`       | Reviewer's findings (BLOCKER / WARNING / NOTE) for round N.           |
| `.docs/active/<type>/<ID>-<name>/blocked-summary.md` (if produced) | Consolidated unresolved findings if Reviewer's rejection loop exhausts `max_rounds`. |

## Source of Truth

- **Sequences and retry policy** → `.agents/workflows.yaml`
- **Board protocol, branch convention, project metadata** → `.agents/context.md`
- **Human-facing workflow tables** → `.agents/README.md` (hand-edited; the YAML wins for execution)
- **Per-agent prompts** → `.agents/prompts/<agent>.md`, invoked via their slash command in `.claude/commands/<agent>.md`

## First Steps (before the chain)

1. **Load config.** Read `.agents/workflows.yaml`. If `$workflow` is not a top-level key under `workflows:`, list valid names and stop.
2. **Resolve metadata** — `description`, `branch_prefix`, `needs_backlog`, `terminal_agent`, `steps`.
3. **Parse input.** Bind `$id` / `$short_name` according to the workflow shape:
   - **Backlog-driven** (`needs_backlog: true`): treat `$input` as `<ID>-<short-name>` where `<ID>` = `YYYYMMDD-NN`. Split into `$id` and `$short_name`. Verify `.docs/backlog/${id}-${branch_prefix}-${short_name}.md` exists; if not, ask the user **once** to confirm an inline spec before invoking Scout.
   - **Standalone Scout** (`needs_backlog: false` **and** the first step's agent is `scout` — i.e. `auditor-strategy`, `auditor-principle`, `maintenance-docs`): treat `$input` as the `<short-name>` slug. Set `$short_name = $input`; leave `$id` **unbound** — Scout self-assigns it (today's date + per-day sequence) for standalone types, and no later step references `$id`. If `$input` is empty, ask the user **once** for a short-name.
   - **Self-bootstrapping** (`needs_backlog: false` **and** no `scout` step — `planning-intake`, `planning-product`, `planning-refine`, `planning-refine-ui`, `maintenance-housekeeping`, `spec`, `maintenance-retro`): treat `$input` as a freeform path / brief / short-name / empty, passed through to the first agent as-is (`$id` / `$short_name` are not bound).

   These two prompts (backlog inline-spec confirmation, missing standalone short-name) are the only places /pipeline ever asks the user.
4. **Begin chain.** Run the execution loop on `steps`.

## Execution Loop

For each step in `steps`, in order:

1. **Substitute args.** Replace tokens in `step.args`: `$input`, `$id`, `$short_name` (each bound in First Steps Step 3; `$id` is bound only for backlog-driven workflows, and no standalone workflow's args reference it). Invoke `/<step.agent> <substituted-args>`.
2. **Wait for the agent to commit and stop.** Agents always make their own commits; the pipeline never commits on their behalf.
3. **Handle `on_block` (if present on this step).** Inspect the latest `review-N.md` written by the agent in the workspace folder.
   - If the file contains **no BLOCKER findings**: continue to the next step.
   - If it contains BLOCKERs:
     - Increment the round counter for this loop edge.
     - If `round <= on_block.max_rounds`: jump back to the step whose `id` equals `on_block.loop_back_to`, re-invoke it (the agent's Rework Mode reads `review-N.md`). After its commit, return here for round `N+1`.
     - If `round > on_block.max_rounds`: **stop the chain** (see "Stall handling" below). Do not invoke subsequent steps.
4. **Immediately invoke the next step.** Do not pause. Do not ask the user.

### Stall handling (max_rounds exceeded)

If the rejection loop exhausts `max_rounds`:

1. Write `.docs/active/<type>/<ID>-<name>/blocked-summary.md` containing:
   - The workflow name, ID, and current branch.
   - The number of review rounds that ran.
   - A consolidated list of BLOCKER findings still unresolved across all `review-N.md` files (deduplicate; cite each file by name).
   - A short paragraph identifying which step's `loop_back_to` target failed to converge.
2. Append a "stalled" entry to `.docs/active/<type>/<ID>-<name>/journal.md`.
3. Update the board: keep the row in `In Progress` with `Agent Phase` set to `<reviewing-agent> → STALLED`.
4. **Skip the terminal step.** The workflow is incomplete; let the human inspect and decide.
5. Proceed to the Final Summary, with verdict `STALLED`.

### Agent-prompt overrides (autonomous mode)

Some sub-agent prompts contain "stop and ask the human" branches for situations like missing inputs or ambiguous specs. In autonomous mode:

- **Missing required inputs** — the orchestrator pre-validates in First Steps; if a sub-agent still finds something missing, it should record the finding in its own output (design.md gaps, review-N.md note, journal) and proceed with the best reasonable assumption rather than stopping.
- **Ambiguous design / unclear spec** — the agent should make and *document* an assumption in its output file (e.g., Architect adds a "Assumptions" section to design.md), not stop.
- **Branch mismatch / safety check failures** — these are real safety checks; let the agent stop. The orchestrator catches the stop, writes a brief stall note in `blocked-summary.md`, and exits with verdict `STALLED`.

## Final Summary (printed after the chain ends)

After either the terminal step commits OR the chain stalls, print:

```
Pipeline complete — workflow: <workflow>, branch: <branch>
Verdict: <COMPLETE | STALLED>
Steps run: <N>/<total>   (rounds, if any rejections: <details>)

Where to read the output:
  • Workspace: .docs/active/<type>/<ID>-<name>/
  • Journal:   .docs/active/<type>/<ID>-<name>/journal.md
  • Reviews:   review-1.md ... review-N.md  (if Reviewer ran)
  • Stall:     blocked-summary.md            (only if verdict = STALLED)

Board: row for <ID> is now in <In Progress | Done>.

Next steps for the human:
  1. Read the files listed above; address any open items in-place.
  2. Merge <branch> when ready (no auto-merge).
```

If verdict is `STALLED`, replace step 2 with: `2. Inspect blocked-summary.md and decide: rework manually, or abandon the branch.`

## Notes

- **Fully autonomous.** The only place /pipeline ever waits for a human is the initial `$input` validation (Step 3). After that, no prompts.
- **One commit per step.** Agents commit and stop; this orchestrator never commits on their behalf and never merges.
- **No auto-merge.** Terminal step (Tech Writer / Reviewer for delivery-gardening / Strategy Auditor / Principle Auditor / Founder Architect / Housekeeper / Spec Reviewer) updates docs and the board, but the human merges the branch separately.
- **Rejection loop is bounded.** Each `on_block` edge tracks its own round counter; the chain stalls (does not loop forever) on the first edge that exceeds `max_rounds`.
- **Spec workflow.** `/pipeline spec <short-name> [note]` runs Spec Extraction end-to-end; the Spec Context Loader self-bootstraps the `spec/<ID>-<short>` branch (no Scout).
- **Adding a workflow.** Edit `.agents/workflows.yaml`; no prompt change needed. Optionally update the human-facing tables in `.agents/README.md`.

Begin by loading the config, validating `$workflow` and `$input`, then run the execution loop end-to-end.
