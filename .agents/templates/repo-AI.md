# AI Agent Guidelines: <PROJECT_NAME>

Single source of truth for all AI tools (Claude Code, Codex, Gemini, etc.).

## Project Metadata

Agents read these values from this table. The `${...}` names on the left are the placeholders used in `.agents/prompts/*.md` — see [.agents/context.md](.agents/context.md) for details.

| Placeholder            | Value                                                                |
| :--------------------- | :------------------------------------------------------------------- |
| `${PKG}`               | `<package_name>` _(e.g. `myapp`)_                                    |
| `${SRC_PATH}`          | `<src/path/>` _(e.g. `src/myapp/`)_                                  |
| `${CLI_SCRIPT}`        | `<full-invocation>` _(e.g. `uv run myapp` — full prefix to invoke the CLI)_ |
| `${TEST_CMD}`          | `<test command>` _(e.g. `uv run pytest`)_                            |
| `${QUALITY_GATE}`      | `<gate command>` _(e.g. `make all`)_                                 |
| `${TESTS_DIR}`         | `<test-root-dir>` _(e.g. `tests/`)_                                  |
| `${TEST_FILE_PATTERN}` | `<test-path-shape>` _(e.g. `tests/test_<module>.py`)_                |
| `${BUILD_MANIFEST}`    | `<manifest-filename>` _(e.g. `pyproject.toml`)_                      |

_The examples are one stack's; not every stack has every concept. Where yours does not, write `n/a — <what it does instead>` (Go: `${TESTS_DIR}` → `n/a — tests colocate as <file>_test.go`; C#: `${BUILD_MANIFEST}` → the `.sln`, then the `.csproj` + `Directory.Build.props` set). Agents read these cells as commands to run — a forced value is worse than an honest gap._

## Commands

```bash
<QUALITY_GATE>                    # Quality gate (format, lint, typecheck, test, security)
<install command>                 # Install dependencies (e.g. `make install`)
<TEST_CMD>                        # Run tests
<TEST_CMD> <file>::<test>         # Run a specific test
<CLI_SCRIPT> <command>            # Run CLI
```

## Documentation

| Need                   | Go To                                                                      |
| ---------------------- | -------------------------------------------------------------------------- |
| Workflow & templates   | [.agents/context.md](.agents/context.md)                                                                       |
| Engineering principles | The knowledge repo — read its `README-AGENT.md` first (see **Engineering Principles** below)                  |

> The chassis is stack-agnostic — engineering conventions and per-stack notes live in the knowledge repo (see **Engineering Principles** below), not in this kit.

## Engineering Principles

Engineering principles and their per-stack conventions live in an external knowledge repo, **not** in this repo. Record its location here once — this is the single pointer the agents follow:

> Engineering principles are at `<knowledge-repo-path>` _(e.g. `../ai-agentic-context-mesh` — a relative path, absolute path, or Git URL your workspace can resolve)_. For any code change, read `README-AGENT.md` there first to find which principles apply; its `README.md` covers setup and the full apply workflow.

See [.agents/context.md](.agents/context.md) § Engineering Principles for how agents use it.

## Program Repos

Fill this in **only if this repo is the program home repo** — the repo that owns the API contracts, where `/refiner-program` runs. Delete this section in every other repo (including the siblings listed here).

The Program Refiner resolves sibling repos from this table and nowhere else — every path must resolve to a git repo, and a missing or dead row stops the run.

| Role      | Path                                                                          |
| :-------- | :---------------------------------------------------------------------------- |
| `ui`      | `<../your-ui-repo>` _(relative or absolute path your workspace can resolve)_   |
| `service` | `<../your-service-repo>`                                                       |
| `db`      | `<../your-db-repo>` _(only if the database is separately owned — see below)_   |

> **Ownership note:** `<FILL_IN>` _(who owns persistence — e.g. "database folds into the service: persistence changes ride the service sub-story; no `db` row" or "db repo separately owned: schema changes get their own sub-story")_

## Project Overview

- **Name**: `<PROJECT_NAME>`
- **Type**: `<FILL_IN>` _(e.g. Python CLI Application, Web Service, Library)_
- **Pattern**: `<FILL_IN>` _(e.g. Service-Adapter, Hexagonal, Layered)_
- **Primary Command**: `<CLI_SCRIPT>`

## Project Catalog

Per-project entities live here. `.agents/` itself stays generic and contains no project-specific catalog.

### Architectural Patterns

- `<FILL_IN>` _(e.g. Result pattern for service errors)_
- `<FILL_IN>` _(e.g. Protocol-based DI for external I/O)_

### Key Services

| Service        | Path                  | Role                                  |
| :------------- | :-------------------- | :------------------------------------ |
| `<ServiceName>`| `<src/path/...>`      | `<one-line role>`                     |

### Key Adapters

| Adapter        | Path                  | External system                       |
| :------------- | :-------------------- | :------------------------------------ |
| `<AdapterName>`| `<src/path/...>`      | `<API/DB/filesystem/...>`             |

### Registries

- `<FILL_IN>` _(e.g. `ADAPTER_TYPE` env var → concrete adapter class)_
