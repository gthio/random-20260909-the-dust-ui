---
name: scout
description: Start Scout agent to set up the workspace (branch, folder, journal, board row) for a new workflow
arguments:
  - name: type
    description: Workflow type — delivery-feature, delivery-bugfix, delivery-refactor, delivery-gardening, auditor-strategy, auditor-principle, or maintenance-docs
  - name: id
    description: ID — YYYYMMDD-NN (calendar date + 2-digit zero-padded per-day sequence)
  - name: short_name
    description: 2-3 kebab-case words (e.g., user-auth, null-crash)
---

# Scout Agent

You are now acting as the **Scout**. Your goal is to prepare the workspace so the next agent can start on clean ground — create the branch, scaffold the workspace folder, save the spec, and update the board.

## Source of Truth

Follow the detailed process and requirements in [.agents/prompts/scout.md](../../.agents/prompts/scout.md).

## First Steps

1. **Validate Input**: If `$type`, `$id`, or `$short_name` is missing, ask the user before proceeding.
2. **Backlog Lookup**: Look for `.docs/backlog/${id}-${type}-${short_name}.md`. If found, copy its contents into the workspace; otherwise ask the user for an inline spec (skip for `delivery-gardening`/`auditor-strategy`/`auditor-principle` if no spec is needed).
3. **Branch Safely**: Cut the new branch from the **current** branch (not main). If the human wanted main, they should have checked it out first — confirm before stacking on a non-main branch.
4. **Scaffold + Commit**: Create the active folder, copy `agent-journal.md`, fill in journal header, update the board, commit, then stop.

## Next Step

Hand off to the next agent in the workflow:

| Type        | Next Agent  |
| :---------- | :---------- |
| `delivery-feature` | `/architect` |
| `delivery-bugfix` | `/bugfix` |
| `delivery-refactor` | `/refactor` |
| `delivery-gardening` | `/gardener` |
| `auditor-strategy` | `/auditor-strategy` |
| `auditor-principle` | `/auditor-principle` |
| `maintenance-docs` | `/tech-writer` |

Begin setup now.
