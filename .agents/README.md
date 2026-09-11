# AI Agent Workflows

How humans orchestrate AI agents to build features, fix bugs, and maintain this codebase.

See [context.md](context.md) for agent-facing details, templates, engineering principles, and architecture.

## Engineering Conventions & Stack

The chassis is stack-agnostic. Engineering conventions — principles, layer rules, coding hygiene, testing standards — and their per-stack notes live in the external **engineering-principles knowledge repo**, not in this kit. Agents identify the project's stack from the code and `AI.md`, then read the matching `stack-notes/<stack>/` set in the knowledge repo. See [context.md](context.md) § Engineering Principles for how agents reach it (entry: `README-AGENT.md`).

For first-time adoption, copying `.agents/` (kit prompts + templates) is the one manual step — see the `readme.md` in the dev kit repo (`ai-agentic-team-dev`). Everything else (`.docs/` structure + board, `AI.md`, `CLAUDE.md`) is scaffolded by `/groundwork` — in **Init mode** (`/groundwork --init`, or automatically when no extracted spec exists) it creates only the missing adoption artifacts and queues nothing.

## How to Start a Workflow

Once setup is in place, run `/scout` with a task type to start the first workflow.

1. **Pick a workflow** below and note its entry artifact (feature spec, bug report, request).
2. **Queue the artifact** — drop a file in `.docs/backlog/` named `<ID>-<TYPE>-<SHORT_NAME>.md` (see `.agents/context.md` for the full naming convention), or prepare to paste it inline when Scout asks. Inputs that still have to be *sliced* — a brief, story, functional spec, surface sketch, or program requirement — go in `.docs/requirements/` (`<ID>-<KIND>-<short-name>.md`); a design handoff bundle goes in `.docs/requirements-ui/<ID>-<short-name>/`. See `.agents/context.md` § Intake folders. **Material that is none of those shapes yet** — a deck export, a spec folder with fixtures, an email, a paste — is dropped under `.docs/requirements/` with any name and handed to `/intake` first (§ Intake below); it writes the record and drafts the kit-shaped inputs the next agent needs.
3. **Invoke the first agent** with its slash command. Scout runs first in every workflow except Product Bootstrap, Groundwork, Spec Extraction, and Housekeeping — each of those self-bootstraps its own branch (or, for Product Bootstrap and Groundwork, runs on the current branch with no branch of its own).
4. **Review, then trigger the next agent.** Agents commit and stop — they never auto-chain.

**HUMAN GATE** marks a point where you must review output before invoking the next agent or merging.

### Autonomous mode — `/pipeline`

Every workflow in [workflows.yaml](workflows.yaml) can also be run end-to-end without gates via `/pipeline <workflow> <input>`. The orchestrator captures uncertainty inside each step's output files (design notes, `review-N.md`, `journal.md`) instead of pausing. Use the manual chain when you want to inspect between steps; use `/pipeline` when you trust the chain to run unattended.

### Drain the whole board — `/drain-board`

`/drain-board [scope]` is a thin loop *above* `/pipeline`: it drains every row under `## Queued` to `Done` by running `/pipeline` on each, in dependency order, in one invocation. It adds no new gates — the only places it waits are the same as `/pipeline`, plus the one human gate at the very end (merge). Stalls don't stop the world: a stalled item is skipped and surfaced in the final summary. Default scope is `all`; pass a comma/space-separated list of IDs to limit the drain, and a trailing `--from-main` to cut each branch from `main` instead of the default stacked chain. Re-running is safe — it only processes rows still `Queued`.

## Utility commands

These commands sit outside the agent roster — they don't change source and aren't part of any workflow chain.

| Command | Role |
| :------ | :--- |
| `/drain-board` | Drain every `Queued` board item to `Done` via `/pipeline`, autonomously, in dependency order (see above). |
| `/write-story` | Regenerate [`readme-story.md`](../readme-story.md), the narrative teaching story covering every workflow in the kit. Follows `readme-story-prompt.md`. |

## Workflows

### Intake
> Digest **raw material** — a slide deck export, a spec folder with fixtures and guides, an email thread, a chat paste — into an **intake record**: a cited summary and stated scope, the shape each unit of work has (`brief` / `story` / `functional-spec` / `sketch` / `program` / design bundle / existing codebase) and the planning agent that consumes it, what that agent needs that the material lacks, numbered questions (blocking first, each with what it blocks, evidence, a default, an owner — a contradiction between sources cites both sides), and a stack proposal drawn only from the `stack-notes/<language>/` sets on disk. Where the route needs a brief or a stack decision the material does not provide, it **drafts** that file in template shape with `<TBD Q-NN>` markers, never invented values; a spec already in the repo is passed to the route by path, never rewritten. Repeatable — run it whenever new work arrives; a re-run overwrites the record and keeps its decisions. **Skips Scout** — it writes `.docs/requirements/` only; no branch, no workspace, no board row. It digests; the route decides.

`raw material` (any path, any name — conventionally under `.docs/requirements/`) → `/intake` → **GATE: Answer blocking questions; replace the drafts' `<TBD>`s** → the route the record names: `/founder-architect` | `/groundwork` | `/refiner` | `/api-contract-builder` | `/refiner-program` | `/refiner-ui` | `/pipeline spec`

### Product Bootstrap
> One-shot decomposition of a Product Brief into `PRODUCT.md` plus a dependency-ordered feature backlog. Runs once at project start, before any feature workflow. **Skips Scout** — there is no per-feature workspace yet.

`Product Brief` (`.docs/requirements/<ID>-brief-<short>.md`) → `/founder-architect` → **GATE: Review PRODUCT.md + backlog** _(then per-feature: `/scout` → `/architect` → ...)_

### Groundwork
> One-shot turn of a **specification** into a drainable board: stack confirmed at a single human gate, missing `.docs/` structure plus `AI.md`/`CLAUDE.md` scaffolded from the templates, and 2–3 initiation items queued (walking skeleton first, chassis riding inside behavior-carrying slices — never naked plumbing). Sibling of Product Bootstrap: brief-driven greenfield goes to `/founder-architect`; anything with a spec starts here. **Skips Scout** — it queues specs and writes root docs only; no branch, no workspace, no board row of its own. The real acceptance gate comes after the drain: the human runs the walking-skeleton command and the quality gate.
>
> Three modes, resolved from what it finds:
>
> - **Full** — an **extracted spec** (the output of Spec Extraction) at `.docs/spec/`. Spec-driven rebuilds.
> - **Requirement** — a **human-authored functional spec** at `.docs/requirements/<ID>-functional-spec-<short>.md`. Greenfield builds where the human wrote the spec rather than extracting it. Identical outputs to Full mode; it only reads differently (flat prose, possibly unnumbered scenarios, possibly self-phased — only the first delivery phase is in scope). Because the spec is still un-sliced, the handoff routes the same file to `/refiner` for the functional backlog behind the skeleton. Note `/refiner-chassis` cannot follow this mode — it requires `.docs/spec/view-non-functional.md` — so deferred chassis obligations ride the functional slices instead, and the handoff names them.
> - **Init** — **no spec** (or an explicit `--init`): scaffold the missing adoption artifacts only (board from `templates/agent-board.md`, `AI.md` with placeholders where the stack notes are silent, `CLAUDE.md`), queue nothing, and hand off to whichever backlog producer fits the input (`/founder-architect`, `/pipeline spec`, `/refiner`, `/refiner-ui`, or a human-authored spec). The intake folders those producers read (`.docs/requirements/`, `.docs/requirements-ui/`) are part of the scaffold.
>
> A `brief`, `story`, or `sketch` is **not** groundwork input — too thin to pick a walking skeleton from. Those route to `/founder-architect` or `/refiner`.
>
> The stack gate takes a bare token (`/groundwork python`) or a **stack decision file** — `.docs/requirements/<ID>-stack-<short>.md`, `templates/human-stack.md` shape — carrying the handful of values the knowledge repo cannot supply: language + framework, the display/distribution/module names, the entrypoint, and the knowledge-repo path. The file form collapses the gate entirely, which is what makes an unattended `/pipeline planning-groundwork` run possible.

`extracted spec` → `/groundwork` → **GATE: Confirm stack** → _(agent queues + commits)_ → `/drain-board` → **GATE: Run the hello world + quality gate, then merge**

`functional spec` (`.docs/requirements/`) → `/groundwork` → **GATE: Confirm stack** → _(agent queues + commits)_ → `/drain-board` → **GATE: Run the hello world + quality gate** → `/refiner <same spec>` → ...

`nothing yet` → `/groundwork --init` → _(agent scaffolds + commits, queues nothing)_ → `/founder-architect` | `/pipeline spec` | `/groundwork` | `/refiner` | `/refiner-ui`

### API Contract
> Translate **one** intent — a product brief, story, functional spec, or surface sketch — into a single reviewable **Draft API contract** (`templates/human-contract-api.md` shape). Repeatable — run it per API surface. **Skips Scout** — it writes a contract doc only; it creates no branch on `src/` and no board row. Pins observable wire behavior at the boundary; applies the knowledge repo's `api-design` / `security` / `resilience` rules, read fresh each run. Feeds Refinement: the Frozen contract is the unit of work `/refiner` slices.

`brief / story / surface sketch` (`.docs/requirements/`) → `/api-contract-builder` → **GATE: Review + Freeze the contract** → `/refiner` → ...

### Refinement
> Slice **one** story, functional spec, or API contract into a dependency-ordered backlog of vertical-slice feature specs. Repeatable — run it whenever a new unit of work arrives (unlike Founder Architect, which bootstraps the whole product once). **Skips Scout** — it queues feature specs only; it creates no branch or workspace. Applies the `vertical-slicing` principle (`SLICE-*`) from the knowledge repo, read fresh each run.

`story / functional spec` (`.docs/requirements/`) or `API contract` (`.docs/contracts/`) → `/refiner` → **GATE: Review queued feature specs** _(then per-feature: `/scout` → `/architect` → ...)_

### UI Refinement
> Slice **one** design handoff bundle (exported screens/prototypes, e.g. from Claude Design or a Figma export) into a dependency-ordered backlog of **UI-scoped** vertical-slice feature specs, plus a `design-map.md` tracing each spec to the exact design file/frame it must match. Repeatable — run it per handoff. **Skips Scout** — it queues feature specs only; it creates no branch or workspace. Hard boundary: every queued spec is front-end-implementable against existing or stubbed data contracts; new server behavior is flagged as a dependency (routed toward `/api-contract-builder`), never queued. Applies the `vertical-slicing` principle (`SLICE-*`) plus matched UI rows (`component-architecture`, `accessibility`, ...) from the knowledge repo, read fresh each run.

`design handoff bundle` (`.docs/requirements-ui/<ID>-<short>/`) → `/refiner-ui` → **GATE: Review queued feature specs + design-map + open questions** _(then per-feature: `/scout` → `/architect` → ...)_

### Chassis Refinement
> Diff the project's **non-functional** spec view (`view-non-functional.md`, produced by Spec Extraction) against what the delivered code already covers, and queue only the gaps that must land *before* functional slices — chassis work such as configuration layering, observability, persistence discipline, and quality gates. Every other gap is explicitly **deferred** to the functional slice that owns it; the deferred list is a first-class output for the human gate. Repeatable — run it after the walking-skeleton phase, after a spec refresh, or on suspected non-functional drift. **Skips Scout** — it queues feature specs only; it creates no branch or workspace. Applies `vertical-slicing` (SLICE-006 as charter; SLICE-001/002 still bind) from the knowledge repo, read fresh each run.

`non-functional spec view` → `/refiner-chassis` → **GATE: Review queued chassis slices + deferred list** _(then per-feature: `/scout` → `/architect` → ...)_

### Program Refinement
> Articulate **one** raw, program-level requirement — a brief, story, or design handoff spanning multiple repos (UI, service, contract, database) — into thin cross-repo **program stories**, then split each into per-repo **sub-stories** plus an API-contract delta, handing each sub-story off by committing it into the owning repo's backlog. Runs from the **program home repo** (where the contracts live), resolving siblings via the `role → path` map in its `AI.md`. Sub-stories are **Refiner input, not feature specs** — each repo's `/refiner` / `/refiner-ui` slices them locally, so this agent decides *who owes what*, never *how a repo builds it*. Design bundles cross **raw** to the UI repo (by reference, into that repo's `.docs/requirements-ui/`); the service repo sees the **contract only**. Repeatable — re-runs reconcile: queued sub-stories are superseded in place, in-flight work gets a delta story queued behind it, never an edit. **Skips Scout** — it writes the contract delta, a program record (`.docs/program/`), and queued sub-stories only; no branch, no workspace. Applies `vertical-slicing` at program altitude (a slice crosses repos), plus `api-design` / `security` / `resilience` for the contract delta, read fresh each run.

`program requirement / design handoff` (`.docs/requirements/<ID>-program-<short>`) → `/refiner-program` → **GATE: Review program record + contract delta; freeze the contract** _(then per repo: `/refiner` or `/refiner-ui` → `/scout` → ...)_

### Spec Extraction
> One-shot extraction of a language-agnostic specification of an existing codebase into `.docs/spec/`, so a downstream group of design + build agents can rebuild the system in another language (or another runtime) with a verifiable behavioral surface. **Skips Scout** — context-loader self-bootstraps the branch and workspace, like Product Bootstrap.
>
> Autonomous: `/pipeline spec <short-name> [note]` runs all seven agents without gates (context-loader → cartographer → domain-modeler → behavior-extractor → synthesizer → reviewer → views); open questions land in `intent.md` (Gaps), `inconsistencies.md`, `acceptance-scenarios.md` (Coverage), and `spec-review.md` instead. The trailing views step is **embedded** — it commits six derived view files directly into `.docs/spec/` alongside the 12 canonical source files: an SDLC cut (`view-architecture.md`, `view-functional.md`, `view-non-functional.md`) and a narrative human-walkthrough cut (`views-human-architecture.md`, `views-human-functional.md`, `views-human-non-functional.md`). The `view` prefix marks them as derived projections and prevents name collisions with source files. Commits onto the same `spec/<ID>-<short>` branch, with no separate branch and no extra board row. There is no standalone way to run views; re-run `/pipeline spec` to regenerate. Use the manual chain below if you want to inspect between steps.

`/spec-context-loader` → **GATE: Review intent gaps + glossary** → `/spec-cartographer` → `/spec-domain-modeler` → `/spec-behavior-extractor` → **GATE** → `/spec-synthesizer` → **GATE: Resolve BLOCKER inconsistencies** → `/spec-reviewer` → `/spec-views --embedded` (internal — invoked only by `/pipeline spec`) → **GATE: Merge spec branch (spec + views) to main**

### Feature Development
> New functionality from a feature spec.

`feature spec` → `/scout` → `/architect` → **GATE** → `/developer-tests` → **GATE** → `/developer-impl` → `/reviewer` → `/tech-writer` → **GATE: Merge**

### Bugfix
> Fix a defect with minimal change.

`Bug Report` → `/scout` → `/bugfix` → `/reviewer` → `/tech-writer` → **GATE: Merge**

### Refactor
> Improve structure; behavior preserved.

`Refactor Request` → `/scout` → `/refactor` → `/reviewer` → `/tech-writer` → **GATE: Merge**

### Gardening
> Readability polish; behavior unchanged. Modifies `src/`, so requires a queued backlog spec defining scope.

`Gardening Request` → `/scout` → `/gardener` → `/reviewer` → **GATE: Merge**

### Strategy Audit
> Devil's-advocate read-only review. Produces a report, not code.

`Request` → `/scout` → `/auditor-strategy` → **GATE: Review report** _(no merge)_

### Principles Audit
> Event-triggered sweep of the codebase against the knowledge repo's numbered rules; every finding verified (citation, lines at HEAD, deviation guidance) before it ships. Read-only; report, not code. First-class `auditor-principle` type; runs as the `auditor-principle` workflow (`/pipeline auditor-principle <short-name>`) or as the manual chain below. Never scheduled — trigger it after a run of features in one subsystem, before a milestone, or when the knowledge repo changes; invoking the pipeline **is** the human-request trigger.

`Trigger` → `/scout auditor-principle <short-name>` → `/auditor-principle` → **GATE: Review report; selected findings become refactor requests** _(no merge)_

### Documentation Sync
> Standalone audit aligning README, CHANGELOG, and `.docs/` with the codebase.

`Schedule` → `/scout` → `/tech-writer` _(General Mode)_ → **GATE: Merge**

### Architecture Documentation
> Generate or refresh the system-level architecture overview and decision log at `.docs/documentation/architecture/` (overview with inline Mermaid + ADRs sourced from feature designs). **Skips Scout** — it writes docs only, **creates no branch, no workspace, and no board row**; it runs on the current branch and commits in place. Applies the knowledge repo's `documentation-architecture` rules (`DOC-*`), read fresh each run. If a scope note names a boundary change, the doc lands in the same commit as that change (DOC-006).
>
> **When to run it:** the Architect's design handoff says `Architecture doc: needed` (a module/layer, port, datastore, or external service was added or removed) — run it on that feature branch before the merge gate. Otherwise on demand, or `refresh` after a run of merges.

`Architect handoff says needed / on demand` → `/generate-documentation-architecture` → **GATE: Review overview + ADRs** _(no separate merge gate — rides the current branch)_

### Housekeeping
> Archive completed work and prune the board. **Skips Scout** — self-bootstraps its own `maintenance-housekeeping/YYYYMMDD-HHMMSS` branch.

`Schedule` → `/housekeeper` → **GATE: Merge**

### Retrospective
> Evaluate how effectively the agent team has worked, from the activity log, and propose concrete improvements (prompt edits + knowledge-repo principle changes). Read-only: produces a report, not code. **Skips Scout** — self-bootstraps its own `maintenance-retro/YYYYMMDD-HHMMSS` branch — and stays **off the board**, like Housekeeping. See [activity/README.md](activity/README.md) for how the log is captured.

`Schedule` → `/retrospective` → **GATE: Review report; apply edits / carry principle proposals**

## Agents

| Agent                | Command              | Role                                                              |
| :------------------- | :------------------- | :---------------------------------------------------------------- |
| **Intake Analyst**   | `/intake`            | Intake: raw material → intake record (cited summary, route, gaps, questions, stack proposal) + draft brief / stack files with `<TBD>`s (repeatable; first when new work arrives). |
| **Founder Architect**| `/founder-architect` | Bootstrap: brief → `PRODUCT.md` + feature backlog (one-shot).         |
| **Groundwork**       | `/groundwork`        | Bootstrap: spec → stack gate + `.docs/`/`AI.md`/`CLAUDE.md` scaffold + initiation backlog (one-shot). Extracted spec → Full; functional spec in `.docs/requirements/` → Requirement; no spec / `--init` → Init (scaffold only). |
| **API Contract Builder** | `/api-contract-builder` | Author: brief / story / sketch → Draft API contract (repeatable).  |
| **Refiner**          | `/refiner`           | Slice one story / spec / contract → queued feature backlog (repeatable). |
| **Refiner (UI)**     | `/refiner-ui`        | Slice one design handoff bundle → queued UI feature backlog + design map (repeatable). |
| **Chassis Refiner**  | `/refiner-chassis`   | Diff non-functional spec view vs delivered code → queued chassis backlog + deferred list (repeatable). |
| **Program Refiner**  | `/refiner-program`   | Articulate one program-level requirement → cross-repo program stories → per-repo sub-stories + contract delta, handed off into sibling backlogs (repeatable). |
| **Scout**            | `/scout`             | Setup: create branch, scaffold workspace, update board.           |
| **Architect**   | `/architect`       | Design: feature spec → technical spec.                                     |
| **Test Writer** | `/developer-tests` | TDD: write failing tests from design.                             |
| **Coder**       | `/developer-impl`  | Build: write code to pass tests.                                  |
| **Reviewer**    | `/reviewer`        | QA: critique logic, security, standards.                          |
| **Tech Writer** | `/tech-writer`     | Docs: update README, CHANGELOG; run audits.                       |
| **Architecture Documenter** | `/generate-documentation-architecture` | Docs: generate/refresh `.docs/documentation/architecture/` overview + ADRs (`DOC-*`); current branch, no branch/board. |
| **Bugfix**      | `/bugfix`          | Reproduce → root-cause → test → fix.                              |
| **Refactor**    | `/refactor`        | Restructure; no new behavior.                                     |
| **Strategy Auditor** | `/auditor-strategy` | Deep-dive architectural critique.                            |
| **Principle Auditor** | `/auditor-principle` | Event-triggered sweep vs the knowledge repo; verified, cited refactoring findings. |
| **Gardener**    | `/gardener`        | Cosmetic readability polish.                                      |
| **Housekeeper** | `/housekeeper`     | Archive completed work from `.docs/active/` to `.docs/archive/`.  |
| **Retrospective** | `/retrospective` | Evaluate agent-team effectiveness from the activity log; propose prompt + principle improvements. |
| **Spec Context Loader**     | `/spec-context-loader`     | Capture intent, non-goals, glossary, external contracts; bootstrap spec branch. |
| **Spec Cartographer**       | `/spec-cartographer`       | Map modules, public surface, cross-cutting patterns, structural smells.         |
| **Spec Domain Modeler**     | `/spec-domain-modeler`     | Extract entities, value objects, invariants, domain operations.                 |
| **Spec Behavior Extractor** | `/spec-behavior-extractor` | Convert tests into Given/When/Then acceptance scenarios + coverage table.       |
| **Spec Synthesizer**        | `/spec-synthesizer`        | Cross-check spec files; produce reading-order README + inconsistencies report.  |
| **Spec Reviewer**           | `/spec-reviewer`           | Audit spec for accuracy *and* sufficiency-for-redesign.                         |
| **Spec Views**              | `/spec-views --embedded`   | Project `.docs/spec/` into classical architecture / functional / non-functional view files. Internal — invoked only by `/pipeline spec`; refuses any other invocation. |

## Branches & Storage

| Workflow     | Branch Pattern              | Documentation Path                     |
| :----------- | :-------------------------- | :------------------------------------- |
| Feature      | `delivery-feature/<ID>-<name>`  | `.docs/active/delivery-feature/<ID>-<name>/` |
| Bugfix       | `delivery-bugfix/<ID>-<name>`   | `.docs/active/delivery-bugfix/<ID>-<name>/` |
| Refactor     | `delivery-refactor/<ID>-<name>` | `.docs/active/delivery-refactor/<ID>-<name>/` |
| Gardening    | `delivery-gardening/<ID>-<scope>` | `.docs/active/delivery-gardening/<ID>-<scope>/` |
| Strategy Auditor | `auditor-strategy/<ID>-<name>` | `.docs/active/auditor-strategy/<ID>-<name>/` (report: `audit-strategy-report.md`) |
| Principle Auditor | `auditor-principle/<ID>-<name>` | `.docs/active/auditor-principle/<ID>-<name>/` (report: `audit-principle-report.md`) |
| Doc Sync     | `maintenance-docs/<ID>-<name>` | `.docs/active/maintenance-docs/<ID>-<name>/` |
| Housekeeping | `maintenance-housekeeping/YYYYMMDD-HHMMSS` | `.docs/archive/YYYYMMDD-HHMMSS/` |
| Retrospective| `maintenance-retro/YYYYMMDD-HHMMSS` | `.docs/activity/maintenance-retro/YYYYMMDD-HHMMSS/` (metrics at `.docs/activity/metrics/`) |
| Spec Extract | `spec/<ID>-<name>`          | `.docs/active/spec/<ID>-<name>/` (workspace) + `.docs/spec/` (persistent — 12 source files **and** the six derived view files: SDLC cut `view-architecture.md` / `view-functional.md` / `view-non-functional.md` plus human-walkthrough cut `views-human-*.md`, written by the trailing embedded views step and overwritten on each re-run of `/pipeline spec`) |

Scout cuts the branch off whichever branch is **currently active** — not off `main`.

### Board lifecycle

All workflows appear on `.docs/board.md` so humans can see in-flight work and Housekeeper can archive completed folders.

| Stage         | Who writes it                                                                             |
| :------------ | :---------------------------------------------------------------------------------------- |
| `In Progress` | Scout (every workflow except Spec Extraction); Spec Context Loader (Spec Extraction)      |
| `Done`        | Tech Writer (Feature / Bugfix / Refactor / Doc Sync); Reviewer (Gardening — clean verdict only); Strategy Auditor (Strategy Audit); Principle Auditor (Principles Audit); Spec Reviewer (Spec Extraction — Spec Views runs after but does not touch the board) |

If Reviewer rejects, the human flips the row back to `In Progress`.

## Rules of Engagement

1. **Human is orchestrator.** Agents commit and stop. You trigger the next step.
2. **Branch safety.** An agent stops if the current branch does not match its workflow pattern. Exception: standalone doc-authors that cut no branch of their own (Intake Analyst, API Contract Builder, Architecture Documenter) run on whatever branch is checked out and only stop on a detached HEAD.
3. **Role boundaries:**
   - **Setup-only** — Scout: creates branches, writes `.docs/` and `.docs/board.md` only.
   - **Read-only** — Architect, Strategy Auditor, Principle Auditor, Reviewer: write `.docs/` only (Strategy Auditor and Principle Auditor always, and Reviewer in Gardening mode, also update `.docs/board.md` as the terminal step).
   - **Docs-only** — Tech Writer: writes `README.md`, `CHANGELOG.md`, `.docs/`, and `.docs/board.md`. Architecture Documenter: writes `.docs/documentation/architecture/` only — no source, no board, no branch of its own (runs on the current branch). Intake Analyst: writes `.docs/requirements/` only (the intake record and its drafts) — never moves or edits human-dropped files, no board, no branch of its own.
   - **Archive-only** — Housekeeper: moves files inside `.docs/`; updates `.docs/board.md`.
   - **Implementation** — modifies `src/`. Test-writing rights vary by role:

     | Agent       | `src/` | `tests/` allowed? | Kind of tests                                                                   |
     | :---------- | :----- | :---------------- | :------------------------------------------------------------------------------ |
     | Test Writer | —      | ✅                | New-behavior tests from design (TDD). This is the only agent that writes these. |
     | Coder       | ✅     | —                 | Makes Test Writer's tests pass; no test edits.                                  |
     | Bugfix      | ✅     | ✅ (one)          | Exactly one regression test per bug; must fail before the fix is applied.       |
     | Refactor    | ✅     | ✅ (coverage)     | Safety-net tests for uncovered paths, added **before** the refactor starts.     |
     | Gardener    | ✅     | ❌                | Cosmetic-only; any new test is a BLOCKER.                                       |
