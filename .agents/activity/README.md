# Activity logging & self-evaluation

This folder is the kit's **observability + self-improvement loop**: capture what the
agents actually do, turn it into metrics, and feed an agent that proposes
improvements. Three layers, all local-file based, all shipped with the chassis.

```
hooks ─▶ log_event.py ─▶ .docs/activity/events/*.jsonl   (Layer 1: raw activity)
                              │
              extract_metrics.py reads events + journals/reviews/board
                              │
                              ▼
        .docs/activity/metrics/{runs.jsonl, summary.md}  (Layer 2: metrics)
                              │
            /retrospective reads metrics + artifacts, writes
                              ▼
   .docs/activity/maintenance-retro/<ts>/retrospective.md  (Layer 3: evaluation)
```

| Layer | Producer | Output | Committed? |
|:------|:---------|:-------|:-----------|
| 1 — raw activity | `log_event.py` (run by hooks) | `.docs/activity/events/<YYYYMMDD>.jsonl` | **No** (git-ignored) |
| 2 — metrics | `extract_metrics.py` | `.docs/activity/metrics/runs.jsonl` + `summary.md` | Yes |
| 3 — evaluation | `/retrospective` agent | `.docs/activity/maintenance-retro/<ts>/retrospective.md` | Yes |

---

## Layer 1 — raw activity (hooks)

`log_event.py` reads a Claude Code hook payload on stdin and appends one compact,
redacted JSON line per event. It is **fail-open**: any error is swallowed, it
exits 0, and it never writes to stdout — so it can neither block nor slow a tool
call, nor inject text into the model's context.

### Enabling it (one manual step)

The handler is wired through Claude Code hooks declared in **`.claude/settings.json`**
(the committed, project-shared settings file — *not* the personal, git-ignored
`settings.local.json`). That file is permission-protected, so add this block
yourself and confirm the hook-trust prompt:

```json
{
  "hooks": {
    "SessionStart":     [ { "hooks": [ { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.agents/activity/log_event.py\"" } ] } ],
    "UserPromptSubmit": [ { "hooks": [ { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.agents/activity/log_event.py\"" } ] } ],
    "PreToolUse":       [ { "matcher": "*", "hooks": [ { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.agents/activity/log_event.py\"" } ] } ],
    "PostToolUse":      [ { "matcher": "*", "hooks": [ { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.agents/activity/log_event.py\"" } ] } ],
    "Stop":             [ { "hooks": [ { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.agents/activity/log_event.py\"" } ] } ],
    "SubagentStop":     [ { "hooks": [ { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.agents/activity/log_event.py\"" } ] } ]
  }
}
```

Hooks load at session start, so restart the session (or `/hooks` to reload) after
editing. Verify by hand at any time:

```bash
echo '{"hook_event_name":"PreToolUse","session_id":"test","tool_name":"Read","tool_input":{"file_path":"x"}}' \
  | python3 .agents/activity/log_event.py
cat .docs/activity/events/$(date -u +%Y%m%d).jsonl
```

### Event shape

```json
{"ts":"…Z","session":"abcd1234","event":"PreToolUse","branch":"delivery-feature/20260101-01-user-auth",
 "type":"feature","run_id":"20260101-01-user-auth","tool":"Bash","summary":"command=…"}
```

`PostToolUse` events also carry `"ok": true|false`. Each event is attributed to a
workflow **run** via the current git branch — no separate correlation id (reusing
the branch convention in `../context.md`).

### Privacy

Only a short, masked descriptor of each tool input is stored — never the full
payload. Secret-looking keys and inline tokens (Bearer, `sk-…`, `AKIA…`,
`token=…`, …) are masked, and every field is truncated. Even so, raw events can
contain command fragments and file paths, so `events/` is **git-ignored**
(rule: `.docs/activity/events/` in the root `.gitignore`); only the aggregated
`metrics/` and `maintenance-retro/` reports are committed. This mirrors the external
knowledge repo's observability principle (its central secret/PII
redaction rules, `OBS-*`).

### Disabling

Remove the `hooks` block from `.claude/settings.json` (and restart). Nothing else
depends on the hooks being present — Layer 2 still runs against the markdown
artifacts; only the raw-activity columns go quiet.

---

## Layer 2 — metrics

```bash
python3 .agents/activity/extract_metrics.py
```

Parses every `journal.md` (type, branch, branch source, start date, rework rounds,
agent phases, cited rule codes), `review-N.md` (verdict + BLOCKER/WARNING/NOTE counts, summed
across rounds), and `board.md` (completion dates) under `.docs/active/` and
`.docs/archive/`, then joins the raw events by run. Writes one row per run to
`runs.jsonl` and aggregates to `summary.md`. Safe to run anytime; produces an
empty report when there is no completed work yet.

---

## Layer 3 — `/retrospective`

```
/retrospective
```

Regenerates metrics, diagnoses recurring failure themes, and writes an
evidence-backed report proposing (a) wording edits to specific
`../prompts/<agent>.md` files and (b) new/changed rules to carry to the knowledge
repo. It is **report-only** behind a human gate — it never edits prompts, source,
tests, or the knowledge repo. Self-bootstraps a `maintenance-retro/<ts>` branch and stays off
the board (like Housekeeping). Prompt: `../prompts/retrospective.md`. Stops on
empty (no runs and no events).

---

## Optional upgrade: OpenTelemetry

For dashboards/trends beyond local files, Claude Code can export metrics and
events to an OpenTelemetry collector — set `CLAUDE_CODE_ENABLE_TELEMETRY=1` and
the relevant `OTEL_*` env vars in your environment (or `.claude/settings.json`
`env`). That is complementary to this layer and intentionally **not** enabled by
the kit; the local files here are what `/retrospective` reads.
