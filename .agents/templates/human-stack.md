# Stack Decision: <Project Display Name>

## Metadata

```yaml
ID: <YYYYMMDD>-<NN>
Kind: stack
Source: human
```

_The human's answer to the one gate `/groundwork` opens, in a committed file so an autonomous run can read it instead of asking. Record **only** what a stack-notes set cannot supply — a name, a path, a deliberate deviation. Everything else the agent transcribes from `stack-notes/<language>/`; see § Not in this file._

## 1. Stack

```yaml
language:  <e.g. python | go | java-spring | csharp | typescript-fastify | kotlin>
framework: <e.g. fastapi | flask | spring-boot | fastify | nestjs | none>
```

- **Why:** <One line. Not a trade-off matrix — just the reason a reader needs six months from now.>

_`language` must match a `stack-notes/<language>/` folder in the knowledge repo; if it does not, the agent stops rather than inventing conventions. `framework` is deliberately **absent** from most bootstrap notes — the notes cover structure, and the framework binding is yours to decide. `none` is a valid answer (a library, or a CLI with no HTTP surface)._

## 2. Names

Three names, and they are not interchangeable. Fill all three even where a stack collapses two of them into one value.

```yaml
display:      <Human-readable product name, e.g. Global Stock Ticker Resolver>
distribution: <Published / artifact name, e.g. chat-ai-api-resolver>
module:       <Import identity — SHORT, e.g. resolver>
```

| Stack | `distribution` is… | `module` is… |
| :--- | :--- | :--- |
| Python | `[project] name` in `pyproject.toml` | `src/<module>/` — the import root |
| Go | (the module path serves as both) | `go mod init <path>` — the import-path root |
| Java / Kotlin | `--project-name` (artifactId) | `--package com.<org>.<service>` (base package) |
| C# | `dotnet new sln --name` | root namespace, `src/<Project>/` |
| TypeScript | `package.json` `name` | the import specifier / path alias |

_**`module` appears in every import line in the codebase** — and in several stacks in the shell or venv prompt as well. Keep it to one or two short words. It is also the most expensive of the three to change later, because some toolchains bake it in at scaffold time; `display` and `distribution` stay cheap to rename._

_Where a toolchain normalizes your value (Python turns `a-b-c` into `a_b_c`), write the **normalized** form — record what the code will actually say, not what you type at the prompt._

## 3. Entrypoint

```yaml
run: <the full command that starts it, e.g. uv run uvicorn resolver.api.app:create_app --factory>
```

_Becomes `${CLI_SCRIPT}` in `AI.md` — the command every delivery agent runs to see the thing work. Most bootstrap notes describe an app **factory** rather than a runnable script, so this usually cannot be transcribed and must be stated. A library with no entrypoint: write `none`._

## 4. Knowledge repo

```yaml
path: <relative path, absolute path, or Git URL — e.g. ../ai-agentic-context-mesh>
```

_Chicken-and-egg: agents look for this pointer in `AI.md`, and `AI.md` does not exist until groundwork writes it. On a first run there is nothing to follow, and auto-detection is unsafe anywhere more than one candidate repo sits beside this one. State it once, here._

## 5. Deliberate deviations

_Optional; default empty. List only the places you knowingly depart from `stack-notes/<language>/`, one line of reason each. An empty section means "the stack notes govern" — which is the answer you want most of the time._

- <e.g. "pytest-asyncio omitted — no async code in release 1.">

## Not in this file

The agent transcribes these from `stack-notes/<language>/`. Filling them here creates a second source of truth that will drift from the knowledge repo:

- test command, quality-gate command, install command
- test directory and test-file naming
- build manifest filename
- source layout and layer names
- tooling choices — linter, formatter, type checker, logger, settings library, test runner

If a stack note is silent on one of these, that is a gap in the **knowledge repo**. Fix it there, not here.
