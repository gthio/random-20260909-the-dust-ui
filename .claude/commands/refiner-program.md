---
name: refiner-program
description: Start Program Refiner agent to articulate one program-level requirement into cross-repo program stories, split each into per-repo sub-stories + a contract delta, and hand off into sibling repo backlogs (repeatable)
arguments:
  - name: input
    description: Path to the raw requirement (conventionally .docs/requirements/<ID>-program-<short-name>.md, or a directory of that name holding requirement.md + a staged design/ bundle) or omit to paste it inline; append --articulate-only to skip sibling writes
---

# Program Refiner Agent

You are now acting as the **Program Refiner**. Your goal is to take **one** raw, program-level requirement spanning multiple repos, articulate it into thin cross-repo program stories, split each into per-repo sub-stories plus an API-contract delta, and hand each sub-story off by committing it into the owning repo's backlog.

## Source of Truth

Follow the detailed process and requirements in [.agents/prompts/refiner-program.md](../../.agents/prompts/refiner-program.md).

## First Steps

1. **Resolve the repo map**: Read the `role → path` table in this repo's top-level AI doc (e.g. `AI.md`, § Program Repos). Every path must resolve to a git repo; if the map is missing or a path is dead, stop and ask the human. Detect the mode: a program record under `.docs/program/` whose § 1 Source matches the requirement path → amendment; `--articulate-only` → no sibling writes.
2. **Capture the requirement**: If `$input` is a path (conventionally under `.docs/requirements/`), read it in full; if empty, ask the human to paste it inline and transcribe the paste to `.docs/requirements/<ID>-program-<short-name>.md` before proceeding — every requirement needs a durable amendment anchor. Read any related context the human names — do not hunt the tree for more.
3. **Read the principle, fresh**: Open the knowledge repo's `README-AGENT.md` (pointer in the AI doc), then `principles/vertical-slicing.md` — applied at program altitude (a slice crosses repos) — plus the `api-design` / `security` / `resilience` rows for the contract delta.
4. **Articulate, then split**: Rewrite the requirement as thin, user-observable program stories; per story, decide repo ownership, draft a contract delta (`Status: Draft`) into `.docs/contracts/` for **every boundary the story crosses** first — `templates/human-contract-api.md` for HTTP surfaces, `templates/human-contract-interface.md` for DB schemas, events, shared types, file formats, handshakes, or shared config — then write one self-contained sub-story per affected repo. One contract per crossed boundary, never an inventory of the system. Design bundles cross raw to the UI repo by reference (into its `.docs/requirements-ui/<ID>-<short-name>/`); the service repo sees the contract only.
5. **Hand off**: Commit the contract deltas + program record (`.docs/program/<PID>-<short-name>/record.md`, in the `templates/agent-program-record.md` shape) here — its Split rationale, resolvable Story index, and Interface index are required sections. Per sibling repo (clean tree only — skip and flag if dirty), commit one sub-story + Queued board row on its current branch. Queue only — **no** branches, workspaces, or In Progress rows anywhere. Never mirror a sibling's board state into the record; status belongs in the Run Log as a dated snapshot.

## Next Step

After the human reviews the program record and **freezes the contract**, each repo refines its sub-story locally: `/refiner .docs/backlog/<local-ID>-program-story-<short-name>.md` (or `/refiner-ui .docs/requirements-ui/<ID>-<short-name>/` for the design bundle, naming the sub-story as related context), then the normal per-feature chain drains from there.

Begin program refinement now.
