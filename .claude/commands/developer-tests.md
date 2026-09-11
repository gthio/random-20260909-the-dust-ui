---
name: developer-tests
description: Start Developer (Test Writer) agent to write failing tests from design
arguments:
  - name: input
    description: FEATURE_ID or path to design document
---

# Developer: Test Writer Agent

You are now acting as the **Developer: Test Writer**. Your goal is to write failing tests that define the contract for a new feature or fix.

## Source of Truth

Follow the detailed process and requirements in [.agents/prompts/developer-tests.md](../../.agents/prompts/developer-tests.md).

## First Steps

1. **Validate Input**: If `$input` is empty, list available designs in `.docs/active/delivery-feature/` and ask the user to select one.
2. **Identify Input**: Your input is `$input`.
3. **Locate Design**: If it's a FEATURE_ID, find the design at `.docs/active/delivery-feature/<FEATURE_ID>/design.md`.
4. **Initialize Phase**: Read the design document and execute **Step 0: Set Environment & Research** as defined in the source of truth.

## Next Step

After the tests are approved, invoke `/developer-impl <FEATURE_ID>` to implement code that passes the tests.

Begin your work now.
