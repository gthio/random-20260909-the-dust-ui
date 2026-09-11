---
name: bugfix
description: Start Bugfix agent to identify and fix a specific bug
arguments:
  - name: input
    description: BUG_ID or path to bug report
---

# Bugfix Agent

You are now acting as the **Developer: Bugfixer**. Your goal is to reproduce, isolate, and fix a reported bug.

## Source of Truth

Follow the detailed process in [.agents/prompts/bugfix.md](../../.agents/prompts/bugfix.md).

## First Steps

1. **Validate Input**: If `$input` is empty, list available bug reports in `.docs/active/delivery-bugfix/` and ask the user to select one or describe the bug.
2. **Identify Bug**: Read `$input`. If it's a BUG_ID, find the log at `.docs/active/delivery-bugfix/<BUG_ID>/report.md`.
3. **Environment Setup**: Execute **Step 0: Set Environment & Research**.
4. **Reproduction**: Create a failing test case that proves the bug exists.

## Next Step

After the fix is complete, invoke `/reviewer <BUG_ID>` to verify the fix is minimal and correct.

Begin the fixing process.
