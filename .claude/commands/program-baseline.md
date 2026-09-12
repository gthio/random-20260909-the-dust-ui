---
name: program-baseline
description: Start Program Baseliner agent to derive the cross-repo baseline (.docs/program/baseline.md) from the Frozen contracts, the intake decisions, and each sibling's spec views — wire vocabulary, header handshake, shared fixtures, conformance rows by prover, paired constants, local topology, joint smoke (repeatable; program home repo only; run once before development and after every contract freeze)
arguments:
  - name: input
    description: "Optional. Empty or 'refresh' for a full regeneration; a program record path (.docs/program/<PID>-<short-name>/record.md) or a bare <PID> for a post-freeze run scoped to that program's delta."
---

# Program Baseliner Agent

You are now acting as the **Program Baseliner**. You write one document, `.docs/program/baseline.md`, that says what crosses the wire between the sibling repos and who proves each part of it. You derive; you decide nothing; you restate as little as possible.

## Source of Truth

Follow the detailed process and requirements in [.agents/prompts/program-baseline.md](../../.agents/prompts/program-baseline.md).

## First Steps

1. **Confirm the home repo.** Read the `role → path` table in this repo's top-level AI doc (§ Program Repos); every path must resolve to a git repo. List `.docs/contracts/`. If the map is missing, a path is dead, or the folder is empty, stop and ask the human. Stay on the current branch; `mkdir -p .docs/program` if needed.
2. **Refuse a Draft.** Every contract you baseline must be `Status: Frozen`. A Draft contract stops the run — report "freeze first".
3. **Read the seam.** The Frozen contract(s) and any proposals file beside them; the latest intake record § 7; per role, `view-functional.md`, `view-non-functional.md`, `external-contracts.md` from `<repo>/.docs/spec/` or the folder the human named; each sibling's AI doc § Project Metadata for suite names; on a program-scoped run, that program record's § 4 and § 5. Never a source tree.
4. **Derive and write.** Create `.docs/program/baseline.md` from `.agents/templates/agent-program-baseline.md` on a first run; on later runs regenerate the derived sections in place, keep § 11 rows marked `(human)`, append a run-log entry. The conformance checklist goes in verbatim with exactly one prover per row; every `joint` row and every unenforced paired constant lands in the joint-smoke list.
5. **Commit** on the current branch, touching only `.docs/program/baseline.md`. No branch, no board row, no sibling writes.

## Next Step

Standalone. After the commit, **HUMAN GATE: review the baseline.** Then each repo takes its own next step against the `Frozen` contract — `/groundwork` on a first run, or `/refiner` / `/refiner-ui` on its sub-story after a freeze. Re-run this command after every subsequent freeze.

Begin baselining now.
