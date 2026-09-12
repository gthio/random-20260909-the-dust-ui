# Intake Answers: <short title of the requirement>

## Metadata

```yaml
ID: <YYYYMMDD>-<NN>
Kind: answers
Source: intake
Record: .docs/requirements/<ID>-intake-<short-name>.md
Last run: <YYYY-MM-DD>
```

_Written by `/intake`; **filled by the human**. One block per question, blocking first. Answer with an option letter, or in your own words; on a non-blocking question an empty `Answer:` accepts the default. Every **blocking** question must be answered before its route can run. When you are done, re-run `/intake <record>`: it copies each answer verbatim into the record's § 7 Decisions, replaces the matching `<TBD Q-NN>` markers in the drafts, and lists what is still open. Your text is never edited — `/intake` changes only the `Status` line. IDs are stable: a `Q-NN` keeps its number across re-runs._

## Blocking

### Q-01 · <short title>

- **Status:** open  <!-- open | answered | retired — set by /intake -->
- **Owner:** <product | engineering | legal | ops>
- **Blocks:** <which decision / which route>
- **Question:** <one sentence, stated as a choice>
- **Options:**
  - **A.** <…> *(default)*
  - **B.** <…>
  - **C.** other — describe
- **Evidence:** `<cite>` (↔ `<cite>` for a contradiction)

**Answer:**

**Rationale:**

## Non-blocking

_An empty `Answer:` accepts the default; the route applies it._

### Q-NN · <short title>

- **Status:** open
- **Owner:** <…>
- **Blocks:** <…>
- **Question:** <…>
- **Options:**
  - **A.** <…> *(default)*
  - **B.** <…>
- **Evidence:** `<cite>`

**Answer:**

**Rationale:**
