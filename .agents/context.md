# Agent Context

> Entry point for AI agents. See the repo's top-level AI doc (e.g. `AI.md`) for commands.

## Workflows

Workflow sequences (which agent runs when, where the human gates are) live in [README.md](README.md). This file covers the agent-facing details: backlog, prompts index, templates, engineering principles, and storage layout.

## Project Metadata

Project-specific values (package name, source path, CLI script, test command, quality-gate command) live in the repo's top-level AI doc (e.g. `AI.md`) under a **Project Metadata** section.

Agents should read those values from there rather than re-deriving them by inspecting the source tree or build manifest. When `.agents/` is reused in another repo, only that repo's Project Metadata table needs updating.

### Command Placeholders

Prompts use shell-style placeholders for the values above so the framework stays stack-agnostic. Substitute from the Project Metadata table when running commands. For concrete examples, see the Project Metadata table in `.agents/templates/repo-AI.md`.

| Placeholder            | Meaning                                                                  |
| :--------------------- | :----------------------------------------------------------------------- |
| `${PKG}`               | Package or top-level module name                                         |
| `${SRC_PATH}`          | Source root (typically ends with `/`)                                    |
| `${CLI_SCRIPT}`        | Full CLI invocation prefix, including any runner (e.g. test runner, JVM) |
| `${TEST_CMD}`          | Test runner command                                                      |
| `${QUALITY_GATE}`      | Aggregate gate (lint + typecheck + test + security)                      |
| `${TESTS_DIR}`         | Test root directory (typically ends with `/`)                            |
| `${TEST_FILE_PATTERN}` | Test file path shape (per-test substitution slots stay as `<...>`)       |
| `${BUILD_MANIFEST}`    | Build/dependency manifest filename                                       |

## Backlog

Items are queued in flat `.docs/backlog/` before entering a workflow. See [`.docs/board.md`](../.docs/board.md) for the current board.

**Filename pattern:** `<ID>-<TYPE>-<SHORT_NAME>.md`

- `<ID>` is `YYYYMMDD-NN`: calendar date plus a 2-digit zero-padded per-day sequence number. `NN` resets to `01` each day and increments for every new same-day item, **regardless of type**. Once assigned, `NN` is never reused — deletions leave gaps. (Edge case: if a single day exceeds 99 items, fall through to 3 digits — `100`, `101`, …)
- `<TYPE>` is one of `delivery-feature`, `delivery-bugfix`, `delivery-refactor`, `delivery-gardening` — or `program-story`, a cross-repo sub-story committed here by a program home repo's `/refiner-program`. A `program-story` item is **Refiner input** (sliced locally by `/refiner` / `/refiner-ui`, which consumes its board row), never a Scout/workflow type, and `/drain-board` skips its row.
- `<SHORT_NAME>` is 2-3 kebab-case words.

Examples:

```text
.docs/backlog/20260418-01-delivery-feature-user-auth.md
.docs/backlog/20260418-02-delivery-bugfix-null-crash.md
.docs/backlog/20260418-03-delivery-refactor-cleanup.md
```

Scout looks up `.docs/backlog/${ID}-${TYPE}-${SHORT_NAME}.md` when preparing the workspace. If found, it is copied into `.docs/active/` under the workflow's spec filename; otherwise Scout asks the human for an inline spec.

### Intake folders

Human-authored inputs to the planning agents live **beside** the flat backlog, one persistent folder per input shape. Each is **conventional, not mandatory** — every consumer accepts any readable path — but an agent handed an inline paste transcribes it into the conventional folder first, so every input has a durable, committed path that the artifacts derived from it can cite:

| Input | Folder | Consumed by |
| :--- | :--- | :--- |
| Raw material not yet in any kit shape — a deck export, a spec folder with fixtures, an email, a paste (any name; § Requirements → raw drops) | `.docs/requirements/` | `/intake` — writes the intake record and drafts the brief / stack files below when missing |
| Prose intent — brief, story, functional spec, surface sketch, program requirement — plus the stack decision that pins how it gets built | `.docs/requirements/` (§ Requirements) | `/founder-architect`, `/refiner`, `/api-contract-builder`, `/refiner-program`, `/groundwork` |
| Design handoff bundle (exported screens/prototypes + manifest) | `.docs/requirements-ui/` (§ UI requirements) | `/refiner-ui` |
| Extracted spec (output of `/pipeline spec`) | `.docs/spec/` | `/groundwork`, `/refiner-chassis` |
| Frozen API contract | `.docs/contracts/` | `/refiner` |

None of these is ever archived by the Housekeeper (only `.docs/active/` and `.docs/backlog/` are). Work that is ready to *drain* goes in `.docs/backlog/`; inputs that still have to be *sliced* go in the folders above — never mix the two.

### Requirements

Raw, human-authored **prose** intent — the input the planning agents read before anything is sliced — lives in `.docs/requirements/`, one file (or one directory, when a design bundle rides along) per requirement. The `stack` kind is the one non-prose member: a short decision record rather than intent, kept here for the same reason as the rest — a durable, committed path that the artifacts derived from it can cite and a later amendment can resolve against.

**Filename pattern:** `<YYYYMMDD-NN>-<KIND>-<short-name>.md` (directory form: `<YYYYMMDD-NN>-<KIND>-<short-name>/` with `requirement.md` as the entry point)

- `<YYYYMMDD-NN>` is minted by the human, same rule as the backlog: scan the folder, continue the day's `NN` **regardless of kind**; never reuse an `NN`.
- `<KIND>` names the input shape, so a reader can tell at a glance what the file is and which agent consumes it:

  | `<KIND>` | What it is | Consumer |
  | :--- | :--- | :--- |
  | `brief` | Product brief (`templates/human-product.md` shape, or prose) | `/founder-architect`; `/api-contract-builder` |
  | `story` | Story / feature request | `/refiner`; `/api-contract-builder` |
  | `functional-spec` | Functional spec (`templates/human-functional-spec.md` shape) | `/refiner`; `/api-contract-builder` |
  | `sketch` | Sketch of a desired API surface | `/api-contract-builder` |
  | `program` | Program-level requirement spanning repos | `/refiner-program` (program home repo only) |
  | `stack` | Stack decision — only the values the knowledge repo cannot supply: language + framework, the three names, the entrypoint, the knowledge-repo path (`templates/human-stack.md` shape) | `/groundwork` |
  | `intake` | Intake record (`templates/agent-intake.md` shape) — agent-authored by `/intake`: cited summary, route per unit of work, gaps, `Q-NN` questions, stack proposal, drafts written. Re-runs overwrite it and keep its decisions | the human at the gate; the route it names |

- `<short-name>` is 2-3 kebab-case words.

**Raw drops.** Material that is not yet in any of these shapes — a deck export, a spec folder with fixtures and guides, an email thread — may be dropped under `.docs/requirements/` under **any name** (`20260904-deck/`, `20260904-game-engine/`); the `<ID>-<KIND>-<short-name>` convention applies to the kit-shaped files, and the intake record `/intake` writes carries the ID and kind for a raw drop. Raw drops are cited where they lie and are never moved, renamed, or edited by an agent; a spec that is already a raw drop is handed to its consumer by path. The kit-shaped files `/intake` derives (`brief`, `stack`, a `story` transcription) are written beside the drop with `Source: intake`, every unstated value a `<TBD Q-NN>` the human replaces before the consumer runs.

Examples:

```text
.docs/requirements/20260822-01-brief-api-resolver.md
.docs/requirements/20260822-02-story-bulk-export.md
.docs/requirements/20260823-01-program-checkout/      ← requirement.md + design/ (staged bundle)
```

Content is free-form — any `human-*` template shape or plain prose; there is deliberately no template. The folder is **conventional, not mandatory**: every consumer accepts any readable path, but an inline paste is always transcribed here first (the consumer mints the `<ID>`, picks the `<KIND>`, and adds a `> Transcribed from inline paste, <YYYY-MM-DD>` provenance line), so every requirement has a durable, committed path. When the material is not yet in a consumer's shape, `/intake` does that transcription and shaping up front (see **Raw drops** above). Every artifact derived from a requirement cites that path — `PRODUCT.md`'s header, a contract's `Requirement` row, each feature spec's `Requirement` metadata, a program record's § 1 Source — which is what makes a later amendment (`/founder-replan`, a `/refiner-program` re-run) resolvable instead of guessed. Long-lived like `.docs/spec/` — never archived by the Housekeeper, because each file is the **amendment anchor** those artifacts point at. Only the `program` kind takes the directory form: `requirement.md` is the entry point and `design/` stages a design handoff in the bundle shape below (manifest required); the staged copy is dead once `/refiner-program` hands the bundle across to the UI repo, whose `.docs/requirements-ui/<ID>-<short-name>/` copy is canonical.

### UI requirements — design handoff bundles

Design handoffs (exported screens/prototypes awaiting refinement) — the input `/refiner-ui` slices — live in `.docs/requirements-ui/`, one directory per handoff, named `<YYYYMMDD-NN>-<short-name>` with the ID minted by the human (scan the folder, continue the day's `NN` — two handoffs on the same day never collide). No `<KIND>` token: everything here is a bundle.

```text
.docs/requirements-ui/<YYYYMMDD-NN>-<short-name>/
├── README.md        ← manifest: primary artifact, medium, optional scope notes
├── design-map.md    ← written by /refiner-ui: spec → design-source traceability
└── ...              ← the design files (HTML/CSS prototypes, exported frames, tokens)
```

The manifest (`README.md`) is the input contract for `/refiner-ui` — it names the **primary artifact** and the **medium** (`claude-design-html` for HTML/CSS prototype exports; `figma-export` for Figma handoffs normalized into files — exported frames, tokens, Dev Mode notes). Live design-tool links are not a medium: export into the bundle first. `/refiner-ui` slices the bundle into ordinary `delivery-feature` backlog items (flat, per the naming convention above), so downstream agents never read the bundle — they follow `design-map.md` when a spec needs its pixel truth. That is why the folder is **persistent** (never archived): the map points back into it for the life of every feature it traces, and it is the one intake folder an agent writes into (`design-map.md` only — everything else in a bundle is human-exported). A bundle is not prose: a UI story or brief that arrives *with* a handoff goes in `.docs/requirements/` as a `story`, and the manifest's scope notes point at it.

## Agent Prompts

Prompts live under `prompts/`. For the agent-to-command mapping, see the Agents table in [README.md](README.md).

## Templates

Templates use a `human-` / `agent-` prefix to signal the filler. Workspace artifacts in `.docs/active/` keep their unprefixed names — the prefix lives only on the template files.

### Intake

| Template                                                 | Who Fills         | Purpose                                |
| -------------------------------------------------------- | ----------------- | -------------------------------------- |
| [agent-intake.md](templates/agent-intake.md)             | Intake Analyst    | Intake record: cited summary, route per unit of work, gaps, `Q-NN` questions, stack proposal, drafts written (drafts use `human-product.md` / `human-stack.md` with `<TBD Q-NN>` markers) |

### Product Bootstrap

| Template                                                 | Who Fills         | Purpose                                |
| -------------------------------------------------------- | ----------------- | -------------------------------------- |
| [human-product.md](templates/human-product.md)           | Human             | Product brief                          |
| [agent-product-spec.md](templates/agent-product-spec.md) | Founder Architect | Persistent product spec (`PRODUCT.md`) |

### Feature Development

| Template                                                       | Who Fills  | Purpose             |
| -------------------------------------------------------------- | ---------- | ------------------- |
| [human-feature.md](templates/human-feature.md)                 | Human      | Define requirements |
| [agent-design.md](templates/agent-design.md)                   | Architect  | Technical spec      |
| [agent-journal.md](templates/agent-journal.md)                 | All agents | Track progress      |
| [agent-review.md](templates/agent-review.md)                   | Reviewer   | Verification report |
| [agent-decision-record.md](templates/agent-decision-record.md) | Architect  | Record decisions    |

### Bugfix

| Template                               | Who Fills | Purpose    |
| -------------------------------------- | --------- | ---------- |
| [human-bug.md](templates/human-bug.md) | Human     | Report bug |

### Refactor

| Template                                         | Who Fills | Purpose          |
| ------------------------------------------------ | --------- | ---------------- |
| [human-refactor.md](templates/human-refactor.md) | Human     | Request refactor |

### Gardening

| Template                                           | Who Fills | Purpose                                          |
| -------------------------------------------------- | --------- | ------------------------------------------------ |
| [human-gardening.md](templates/human-gardening.md) | Human     | Scope a readability-polish pass (optional input) |

### Program Refinement

| Template                                                             | Who Fills        | Purpose                                                                                                  |
| -------------------------------------------------------------------- | ---------------- | -------------------------------------------------------------------------------------------------------- |
| [agent-program-record.md](templates/agent-program-record.md)         | Program Refiner  | Program record: stories, split rationale, story index, interface index, run log                          |
| [human-contract-api.md](templates/human-contract-api.md)             | Human (engineer) | HTTP API contract — wire-behavior source of truth for an HTTP boundary                                   |
| [human-contract-interface.md](templates/human-contract-interface.md) | Human (engineer) | Non-HTTP boundary contract — DB schema, event/topic, shared types, file format, handshake, shared config |

### Shared

| Template                                       | Who Fills  | Purpose               |
| ---------------------------------------------- | ---------- | --------------------- |
| [agent-journal.md](templates/agent-journal.md) | All agents | Track progress & logs |

## Document Storage

```text
.docs/active/
├── delivery-feature/<ID>-<name>/     ← Feature development
│   ├── feature.md
│   ├── design.md
│   └── ...
├── delivery-bugfix/<ID>-<name>/      ← Bug fixes
│   ├── bug-report.md
│   ├── journal.md
│   └── report.md
├── delivery-refactor/<ID>-<name>/    ← Refactoring
│   ├── refactor-request.md
│   ├── journal.md
│   └── report.md
├── delivery-gardening/<ID>-<name>/   ← Gardener tasks
│   ├── journal.md
│   └── report.md
├── maintenance-docs/<ID>-<name>/  ← General documentation maintenance
│   ├── journal.md
│   └── audit-report.md
├── auditor-strategy/<ID>-<name>/  ← Strategy audit (devil's-advocate critique)
│   ├── journal.md
│   └── audit-strategy-report.md
├── auditor-principle/<ID>-<name>/  ← Principles audit (knowledge-repo sweep)
│   ├── journal.md
│   └── audit-principle-report.md
└── spec/<ID>-<name>/       ← Spec extraction workspace (persistent spec lives at .docs/spec/)
    ├── journal.md
    └── spec-review.md
```

The Spec Extraction workflow also writes a **persistent** spec folder at `.docs/spec/` (like `PRODUCT.md` at the repo root) — this is the long-lived artifact downstream design and build agents read from. The `.docs/active/spec/<ID>-<name>/` folder above is just the per-run workspace (journal, reviewer report).

The Architecture Documenter (`/generate-documentation-architecture`) likewise maintains a **persistent** folder at `.docs/documentation/architecture/` — `overview.md` (DOC-003 system overview, with its sequence + component Mermaid diagrams inline) and `adr/` (immutable dated ADRs, each sourced from the feature design or `AI.md` note that made the decision). It has **no per-run workspace**: it runs on the current branch, cuts no branch, and writes no board row.

In a **program home repo** (the repo owning the API contracts, with a § Program Repos map in its AI doc), the Program Refiner (`/refiner-program`) likewise maintains a **persistent** folder at `.docs/program/<PID>-<short-name>/` — `record.md` (shape: `templates/agent-program-record.md`) holds the program stories, the **split rationale**, a *resolvable* story index (repo path → local ID → sub-story path; the repo's board follows from its path), an **interface index** naming every boundary the program changes with its contract path and `Draft`/`Frozen` status, the dependency map, and a run log. Long-lived like `.docs/spec/`, never archived by the Housekeeper, no per-run workspace: no branch, no board row of its own. It is **not a status board** — each sibling repo's `.docs/board.md` owns its own rows, and the record never mirrors them; sub-story status appears only as a dated snapshot inside a run-log entry. Contracts live in the repo's `.docs/contracts/` — `<short-name>-api-contract.md` (the `human-contract-api.md` shape) for HTTP surfaces, `<boundary-name>-interface-contract.md` (the `human-contract-interface.md` shape) for every other crossed boundary. The raw requirements that trigger these programs live in the persistent `.docs/requirements/` folder (§ Requirements, under Backlog) — human-authored, never archived, each file the amendment anchor its record's § 1 Source points at. The design bundle a program hands to its UI repo lands in *that* repo's persistent `.docs/requirements-ui/` (§ UI requirements).

### Activity log

Activity capture and self-evaluation live under `.docs/activity/` (the tooling is in `.agents/activity/`):

```text
.docs/activity/
├── events/<YYYYMMDD>.jsonl   ← raw events appended by .agents/activity/log_event.py (git-ignored)
├── metrics/
│   ├── runs.jsonl            ← one row per workflow run, derived by extract_metrics.py
│   └── summary.md            ← aggregates (rework, verdicts, hotspots)
└── maintenance-retro/<YYYYMMDD-HHMMSS>/
    └── retrospective.md      ← Retrospective agent's evaluation + improvement proposals
```

`events/` is git-ignored (raw, potentially sensitive — redacted at write time); `metrics/` and `maintenance-retro/` are committed. The raw stream is produced by Claude Code hooks wired in `.claude/settings.json`. See [activity/README.md](activity/README.md).

## Board Protocol

All agents that write to `.docs/board.md` follow this protocol. Individual prompts reference this section instead of restating the rules.

### Sections and columns

Match the column headings already in `.docs/board.md`:

- `## Queued` — `ID | Type | Priority | Deps | Title | File`
- `## In Progress` — `ID | Type | Priority | Title | Branch | Branch Source | Agent Phase`
- `## Done` — `ID | Type | Title | Branch | Branch Source | Completed`

Use `—` for unknown fields (e.g., Priority on standalone types).

**`Deps`** (Queued only) — IDs that must merge before this item, comma-separated
(e.g. `07` or `03, 04`); `—` when nothing blocks it. List only the direct
prerequisites, not the whole chain. Queued rows stay in dependency order, so a
row's deps always sit above it. Drop the column when a row moves to In Progress.

`Branch Source` is the base branch the work was cut from (the `${BASE_BRANCH}` recorded when the branch was created). Set once alongside `Branch` by whoever creates the row, then carried unchanged into `Done`.

### Transitions

| Trigger            | Move                                                                                              | Applied by                                        |
| :----------------- | :------------------------------------------------------------------------------------------------ | :------------------------------------------------ |
| Workflow starts    | Pipeline types: `Queued` → `In Progress`. Standalone types: insert directly into `In Progress`.   | Scout (or Spec Context Loader for `spec`)         |
| Phase handoff      | Update `Agent Phase` in `In Progress` to `<current> → <next>`                                     | Each agent, before its commit                     |
| Reviewer rejects   | Row stays in `In Progress`; human flips `Agent Phase` back to the prior developer                 | Human                                             |
| Workflow completes | `In Progress` → `Done`; fill `Completed` date                                                     | Terminal agent (Tech Writer / Reviewer / Strategy Auditor / Principle Auditor / Spec Reviewer) |
| Archive            | Remove `Done` row                                                                                 | Housekeeper                                       |

Pipeline types: `delivery-feature`, `delivery-bugfix`, `delivery-refactor`, `delivery-gardening` — workflows that modify `${SRC_PATH}` and require a queued spec in `.docs/backlog/`.
Standalone types: `auditor-strategy`, `auditor-principle`, `maintenance-docs`, `spec` — read-only or docs-only workflows that may run without a backlog file. (`spec` is also one-shot per repo and self-bootstraps via Spec Context Loader, like `maintenance-housekeeping` self-bootstraps via Housekeeper — but unlike Housekeeping, Spec Extraction is on the board because it has multi-phase agent handoff.)
Terminal agent by workflow: delivery-feature / delivery-bugfix / delivery-refactor / maintenance-docs → Tech Writer; delivery-gardening → Reviewer (on a clean verdict only — on BLOCKERs the row stays In Progress and loops back to the Gardener); auditor-strategy → Strategy Auditor; auditor-principle → Principle Auditor; spec → Spec Reviewer.
Off-board maintenance runs: `maintenance-housekeeping` and `maintenance-retro` self-bootstrap their own branch and never touch `.docs/board.md` — they have no row in any section.

### Rules

1. Only Scout (or Spec Context Loader for `spec`) adds rows to `In Progress`.
2. Only the terminal agent moves rows to `Done`.
3. Touch only the row matching your `ID` + `Type`.
4. Commit the board edit together with the phase artifacts — never in a separate commit.

## Engineering Principles

Engineering conventions are **not** stored in this kit. They live in an external **engineering-principles knowledge repo**, read by both agents and humans. The chassis stays stack-agnostic; the knowledge repo owns the principles and their per-stack notes.

**One pointer.** The knowledge repo's location is recorded once, in the repo's top-level AI doc (e.g. `AI.md`) under its **Engineering Principles** pointer. Nothing in `.agents/` hard-codes the path.

**How agents use it.** For any change, open the knowledge repo's `README-AGENT.md` first — the principle directory that maps a change to the docs it pulls in. Match the **Applies when** column, then read each matched `principles/<slug>.md` (the RFC 2119 contract) alongside its note for your project's stack (the knowledge repo's `stack-notes/<stack>/`; the stack is evident from the code and `AI.md`). Cite rule codes (e.g. `CFG-003`) in designs and reviews so reviewers can find the exact obligation — and **pair each citation with a one-line rationale** (`CFG-003 — why it applies / how this satisfies it`), so the *reasoning* lives in the artifact, not only in the agent's head. A bare code with no reason is incomplete: the reason is the part a human at the gate (and the retrospective afterward) actually reads. The knowledge repo's own `README.md` covers the full apply workflow.

## Branch Convention

The Scout agent creates the branch at the start of every workflow, cutting from whichever branch is currently active (not from `main`). Domain agents verify the branch matches the expected pattern and stop if it does not.

| Workflow     | Branch Pattern                | Example                                 |
| :----------- | :---------------------------- | :-------------------------------------- |
| Feature      | `delivery-feature/<ID>-<short-name>` | `delivery-feature/20260101-01-user-auth`    |
| Bugfix       | `delivery-bugfix/<ID>-<short-name>` | `delivery-bugfix/20260101-02-null-response`  |
| Refactor     | `delivery-refactor/<ID>-<short-name>` | `delivery-refactor/20260201-01-refactoring-cleanup` |
| Gardening    | `delivery-gardening/<ID>-<short-name>` | `delivery-gardening/20260301-01-deps-update` |
| Doc Update   | `maintenance-docs/<ID>-<short-name>` | `maintenance-docs/20260201-02-readme-fix` |
| Strategy Auditor | `auditor-strategy/<ID>-<short-name>` | `auditor-strategy/20260201-03-pydantic-v3` |
| Principle Auditor | `auditor-principle/<ID>-<short-name>` | `auditor-principle/20260601-01-post-milestone` |
| Spec Extract | `spec/<ID>-<short-name>`      | `spec/20260503-01-baseline`                |

### Relationship to backlog filenames

Branch names mirror backlog filenames almost exactly — the type is just promoted from a name segment to a path prefix for tooling-friendliness (CI hooks, branch-protection rules, and IDE branch pickers all key on path prefixes). Same identity in both places:

```text
.docs/backlog/20260101-01-delivery-feature-user-auth.md ← <ID>-<TYPE>-<SHORT_NAME>.md
                              ↓
git branch:    delivery-feature/20260101-01-user-auth   ← <TYPE>/<ID>-<SHORT_NAME>
```

The `<ID>` (`YYYYMMDD-NN`) and `<SHORT_NAME>` are byte-identical between the two; the only difference is whether `<TYPE>` lives inside the filename or as the branch prefix.

## Project Catalog

The repo's per-project catalog (architectural patterns, system capabilities, key services, key adapters, registries) lives in the top-level AI doc (e.g. `AI.md`). Read it from there. `.agents/` itself is generic and contains no per-project entities.
