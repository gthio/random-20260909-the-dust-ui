# Intake: <short title of the requirement>

## Metadata

```yaml
ID: <YYYYMMDD>-<NN>
Kind: intake
Source: intake
Raw:                     # every human-dropped path this record digests, as given (never moved or renamed)
  - <.docs/requirements/<as-dropped>/>
Last run: <YYYY-MM-DD>
```

_Written by `/intake`. One record per requirement — related material of several shapes (a deck and a spec folder for the same product) is one record with one row per unit of work in § 3. A re-run overwrites § 1–§ 6 and keeps § 7. Every claim cites the raw material (`<path> § n` / slide title / page); a line with no citation is an inference and says so._

## 1. Sources

| Path | Format | What it is | How it was read | Notes |
| :--- | :--- | :--- | :--- | :--- |
| `<path>` | `<markdown / packaged HTML export / PDF / JSON / chat paste>` | `<deck, spec, writers' guide, fixtures…>` | `<in full / embedded text decoded / could not read — see Notes>` | `<author / date if stated; anything skipped and why>` |

## 2. Summary and scope

- **What:** <…> (`<cite>`)
- **For whom:** <…> (`<cite>`)
- **Why / problem:** <…> (`<cite>`)
- **Success looks like:** <…> (`<cite>`) — or `not stated → Q-NN`

Capabilities the material names:

- <capability> (`<cite>`)

| | Stated in the material | Cite |
| :--- | :--- | :--- |
| **In scope** | <…> | `<…>` |
| **Out of scope / deferred** | <…> | `<…>` |
| **Phasing** | <first phase / milestones / "none stated"> | `<…>` |
| **Hard constraints** | <must / cannot — these shape architecture, not features> | `<…>` |

## 3. Route and gaps

| # | Material | Shape (`<KIND>`) | Altitude | Repos | Route | Why |
| :-- | :--- | :--- | :--- | :--- | :--- | :--- |
| U1 | `<path>` | `<brief / story / functional-spec / sketch / program / design bundle / existing codebase>` | `<product / component / feature>` | `<this repo / this + siblings / unknown → Q-NN>` | `/<agent>` | <one line> |

**Rejected routes:** <`/<agent>` — why not; or "none">

| Needed by `/<route>` | Present? | Where | Action |
| :--- | :--- | :--- | :--- |
| <e.g. brief in `templates/human-product.md` shape> | <yes / no / partial> | `<path>` | `<present / drafted → § 6 / human: Q-NN>` |
| <e.g. stack decision (`templates/human-stack.md`)> | <…> | <…> | <…> |
| <e.g. `AI.md` unlaid; `PRODUCT.md` absent; knowledge repo resolvable> | <…> | <…> | <…> |

## 4. Stack

_Observations and a proposal — never a decision. If code, a build manifest, or a filled `AI.md` already exists: `already decided at <path>` and nothing else._

- **Pinned by the material:** <…> (`<cite>`)
- **Left open:** <…>
- **Repo state:** <empty / kit only / `AI.md` placeholders / code present>
- **Stack-notes sets on disk:** <`<knowledge-repo path>/stack-notes/<a>/`, `…/<b>/` …>
- **Proposal:** <one stack, one-line reason> — alternatives: <≤ 2, one line each>. Carried into the stack draft (§ 6) as `<TBD Q-NN — proposal: …>`.

## 5. Questions

_Blocking first. **Blocking** = the route cannot start, or would harden a guess, until answered. A contradiction between sources is a question whose Evidence cites both sides. Non-blocking questions carry into the route's own open-questions section with the default applied._

| ID | Question | Blocks | Evidence | Default if unanswered | Owner | Blocking? |
| :-- | :--- | :--- | :--- | :--- | :--- | :--- |
| Q-01 | <…> | <which decision / which route> | `<cite>` (↔ `<cite>` for a contradiction) | <…> | `<product / engineering / legal / ops>` | <yes / no> |

## 6. Handoff

| Draft written | Shape | TBDs | Consumed by |
| :--- | :--- | :--- | :--- |
| `.docs/requirements/<ID>-brief-<short-name>.md` | `templates/human-product.md` | <Q-NN, …> | `/founder-architect` |
| `.docs/requirements/<ID>-stack-<short-name>.md` | `templates/human-stack.md` | <Q-NN, …> | `/groundwork` |

```text
Record:    .docs/requirements/<ID>-intake-<short-name>.md
Route:     <U1 → /<agent> <args>; U2 → /<agent> <args>>
Blocking:  <Q-01, Q-03 | none>
Review:    <drafts above — replace every <TBD> | none>
Next:      <exact command(s), in order, runnable once Blocking and Review are cleared>
```

## 7. Decisions

_Answered questions land here verbatim and keep their Q-ID. Survives re-runs._

| Date | ID | Decision | Rationale | Owner |
| :--- | :-- | :--- | :--- | :--- |
