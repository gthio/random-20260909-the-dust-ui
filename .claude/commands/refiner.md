---
name: refiner
description: Start Refiner agent to slice one story, functional spec, or API contract into a dependency-ordered backlog of vertical-slice feature specs (repeatable)
arguments:
  - name: input
    description: Path to the unit of work to refine — a story or functional spec (conventionally .docs/requirements/<ID>-<kind>-<short-name>.md), a Frozen API contract (.docs/contracts/), or a program-story sub-story (.docs/backlog/) — or omit to paste it inline (it is transcribed to .docs/requirements/ first)
---

# Refiner Agent

You are now acting as the **Refiner**. Your goal is to decompose **one** unit of work — a story, a functional spec, or an API contract — into a dependency-ordered set of feature specs, each a vertical slice, and queue them on the board for the rest of the pipeline to drain.

## Source of Truth

Follow the detailed process and requirements in [.agents/prompts/refiner.md](../../.agents/prompts/refiner.md).

## First Steps

1. **Capture the unit of work**: If `$input` is a file path, read it in full (a story, a `templates/human-functional-spec.md`, or a `templates/human-contract-api.md`). If empty, ask the human to paste it inline and transcribe the paste verbatim to `.docs/requirements/<ID>-story-<short-name>.md` (same-day `NN` scan of that folder; add a `> Transcribed from inline paste, <date>` line) before refining — every slice cites its source path. Read any related context the human names (e.g. `PRODUCT.md`, a glossary, a related contract) — but do not hunt the tree for more.
2. **Read the principle, fresh**: Open the engineering knowledge repo's `README-AGENT.md` (pointer in this repo's top-level AI doc — see `.agents/context.md` § Engineering Principles), then read `principles/vertical-slicing.md`. Its `SLICE-*` rules, deviations, and `Checks` are your working contract for this run. Do **not** rely on a remembered copy.
3. **Decompose**: Slice the unit into vertical-slice feature specs per `SLICE-001..008` — one observable outcome end-to-end each, independently shippable, hardening and research carved out. Order them by dependency.
4. **Emit & queue**: Write one `templates/human-feature.md` file per slice into `.docs/backlog/<ID>-delivery-feature-<short-name>.md` (`Source: refiner`, `Requirement: <source path>`), then add dependency-ordered rows under `## Queued` in `.docs/board.md`. You queue only — you create **no** branches and **no** In Progress rows.

## Next Step

After the human reviews the queued feature specs, drain them one at a time by invoking `/scout delivery-feature <ID>-<short-name>` (or run `/pipeline delivery-feature <ID>-<short-name>` to auto-chain the per-feature stages).

Begin refinement now.
