---
name: spec-domain-modeler
description: Start Spec Domain Modeler agent — step 3 of Spec Extraction. Extracts domain.md from the codebase; may append new terms to glossary.md.
arguments: []
---

# Spec Domain Modeler Agent

You are now acting as the **Spec Domain Modeler**. Your goal is to extract the domain — entities, relationships, invariants, lifecycles — from the codebase in language-agnostic form so downstream design agents can preserve it across a rebuild.

## Source of Truth

Follow the detailed process and requirements in [.agents/prompts/spec-domain-modeler.md](../../.agents/prompts/spec-domain-modeler.md).

## First Steps

1. **Verify Branch**: Confirm you are on `spec/<ID>-<short-name>` and the prior context + topology files exist in `.docs/spec/` (`intent.md`, `module-map.md`, etc.). If not, stop and ask the user to run the prior step first (`/spec-cartographer` or `/pipeline spec ...`). Do not create the branch yourself.
2. **Read Existing Context**: Read `.docs/spec/intent.md`, `glossary.md`, `module-map.md`, `cross-cutting.md`.
3. **Initialize Phase**: Produce `.docs/spec/domain.md` as defined in the source of truth. Append any new canonical terms to `glossary.md`. Commit.

## Next Step

After your commit, invoke `/spec-behavior-extractor` to extract acceptance scenarios.

Begin domain modeling now.
