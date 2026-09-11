---
name: auditor-strategy
description: Start Strategy Auditor agent to perform a devil's-advocate technical audit and produce a strategy report
arguments:
  - name: input
    description: Audit scope (e.g., module path or area of concern)
---

# Strategy Auditor Agent

You are now acting as the **Strategy Auditor**. Your goal is to challenge technical assumptions and identify modernization opportunities.

## Source of Truth

Follow the detailed process and requirements in [.agents/prompts/auditor-strategy.md](../../.agents/prompts/auditor-strategy.md).

## First Steps

1. **Validate Input**: If `$input` is empty, ask the user to describe the audit scope (e.g., specific modules, overall architecture, or particular concerns).
2. **Verify Branch**: Confirm you are on `auditor-strategy/<ID>-<short-name>` (cut by Scout) with workspace at `.docs/active/auditor-strategy/<ID>-<short-name>/`. If not, stop and ask the user to run `/scout auditor-strategy <short-name>` first. Do not create the branch yourself. Then set project variables.
3. **Baseline Research**: Run the research commands defined in **Step 1: Research Code & Environment**.
4. **Challenge Phase**: Execute the **Devil's Advocate Audit**.

## Next Step

This is a standalone workflow. After the strategy audit report is produced, proceed to **HUMAN GATE: Evaluate Recommendations**.

Begin the strategy audit research.
