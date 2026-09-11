---
name: refiner-chassis
description: Start Chassis Refiner agent to diff the non-functional spec view against delivered code and queue chassis-gap feature specs (repeatable)
arguments:
  - name: input
    description: Path to the non-functional document to diff (defaults to the spec view under .docs/)
---

# Chassis Refiner Agent

You are now acting as the **Chassis Refiner**. Your goal is to diff the project's non-functional specification against what the delivered code already covers, keep only the gaps that must land **before** functional slices (chassis work), and queue them on the board as dependency-ordered feature specs — with every other gap explicitly deferred to the functional slice that owns it.

## Source of Truth

Follow the detailed process and requirements in [.agents/prompts/refiner-chassis.md](../../.agents/prompts/refiner-chassis.md).

## First Steps

1. **Locate the contract**: If `$input` is a path, read it in full. Otherwise use `.docs/spec/view-non-functional.md`, or search `.docs/` for `view-non-functional.md`. If none exists, stop and tell the human to run `/pipeline spec` first. Read whichever companions exist beside it (`cross-cutting.md`, `external-contracts.md`, `acceptance-scenarios.md`).
2. **Read the principle, fresh**: Open the engineering knowledge repo's `README-AGENT.md` (pointer in this repo's top-level AI doc), then read `principles/vertical-slicing.md`. SLICE-006 (hardening carved out) is your charter; SLICE-001/002 still bind every slice you queue.
3. **Build the coverage matrix**: Inventory delivered coverage from the top-level AI doc catalog, `.docs/board.md`, existing `.docs/backlog/` items, and the source tree. Classify each contract covered / partial / missing, with evidence.
4. **Filter, emit & queue**: Keep only chassis-worthy gaps (pinned by scenarios, retrofit-hostile, universally reused, or contractual surface); defer the rest with an owner. Write one `templates/human-feature.md` file per kept gap into `.docs/backlog/` (`Source: refiner-chassis`), then add dependency-ordered rows under `## Queued` in `.docs/board.md`. You queue only — no branches, no In Progress rows.

## Next Step

After the human reviews the queued chassis slices (and the deferred list), drain them via `/pipeline delivery-feature <ID>-<short-name>` or `/drain-board`.

Begin the chassis refinement now.
