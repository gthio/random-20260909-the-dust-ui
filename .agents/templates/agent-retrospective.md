# Retrospective: <TIMESTAMP>

_Generated: <YYYYMMDD>_
_Period covered: <first run> … <last run>_
_Source: `.docs/activity/metrics/` (runs.jsonl + summary.md) and the raw events log._

---

## 1. Effectiveness at a glance

| Metric | Value | Read |
|:-------|:------|:-----|
| Runs evaluated | <N> | <archived + active> |
| Avg rework rounds | <x.y> | <by type, if it varies> |
| Verdict mix | <APPROVED / NEEDS CHANGES / REJECTED counts> | |
| BLOCKER / WARNING / NOTE | <b / w / n> | over all rounds |
| Median time-to-done | <days> | <outliers> |
| Tool calls (failed %) | <count> (<pct>%) | from the events log |
| Top principle hotspots | <CODE×n, CODE×n> | most-cited rule codes |

## 2. Failure themes

> Each theme cites the evidence behind it — a metric, a run id, or a quoted artifact.

### Theme: <short name>
- **Evidence:** <metric / run id / quote>
- **Pattern:** <what recurs and where>
- **Likely cause:** <hand-off gap, brittle instruction, missing principle, …>

## 3. Proposed prompt edits (kit-local)

> Specific, quoted wording changes to `.agents/prompts/<agent>.md`. The human applies these.

- [ ] **`<agent>`** — _motivated by <metric / theme>_
  - Current: "<quote current text>"
  - Proposed: "<quote replacement text>"

## 4. Proposed principle changes (knowledge repo)

> New or amended rules to carry to the external engineering-principles repo. Sketched in its own code form; not applied here.

- [ ] **<principle-slug>** — proposed rule `<PREFIX>-NNN`
  - Applies when: <trigger>
  - Contract: <MUST / SHOULD / MAY …>
  - Evidence: <run ids / cited code such as CFG-003 / counts>

## 5. What worked

- <Positive signal worth preserving — e.g. a workflow type with low rework, a phase with zero failed tools.>

## 6. Period summary

<One short paragraph: the story of this period's agent performance and the single highest-leverage change to make next.>
