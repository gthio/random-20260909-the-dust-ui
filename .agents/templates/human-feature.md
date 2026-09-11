# Feature: <Short Description>

## Metadata

```yaml
ID: <YYYYMMDD>-<NN>
Type: <Feature | Bugfix | Improvement>
Priority: <Low | Medium | High>
Source: <human | founder-architect | founder-replan | refiner | refiner-ui | groundwork>   # optional; default: human
Requirement: <path under .docs/requirements/ or .docs/requirements-ui/>   # optional; the input this spec was sliced from
```

_`Source` records who authored this feature spec. Omit it for human-authored feature specs (the default). Founder Architect sets it to `founder-architect` when generating the bootstrap backlog; `/founder-replan` uses `founder-replan`; the Refiner sets `refiner` when slicing a story or contract into features; the UI Refiner sets `refiner-ui` when slicing a design handoff bundle; the Groundwork agent sets `groundwork` on initiation items. `Requirement` records the intake file (or bundle) the spec was derived from — the path the producing agent read, e.g. `.docs/requirements/20260822-01-story-bulk-export.md`; omit it for a spec written directly into the backlog. Downstream agents ignore both fields; they exist so a requirement can be amended and its slices found._

## 1. Context

- **Problem:** <Describe the pain point or the current limitation in plain language.>
- **Objective:** <What should the application be able to do after this work is finished?>

## 2. Business Rules & Logic

_Human: List the rules the agent must follow, without worrying about code files._

- <Rule 1: e.g., "The user must be warned if the API returns data older than 24 hours.">
- <Rule 2: e.g., "All output must be formatted as a table by default.">

## 3. User Acceptance Criteria

_Human: How will you manually verify this works?_

- [ ] **Behavior 1:** <e.g., "When I run the process command with --verbose, I see the operation details.">
- [ ] **Behavior 2:** <e.g., "If I provide invalid input, I get a clear error message.">

## 4. Out of Scope

- <Anything you explicitly do NOT want changed or fixed in this task.>
