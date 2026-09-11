# Technical Design: <Feature/Fix Name>

_Feature: [link to feature.md]_

> **Stack note:** Layer rows, file paths, and the data-flow diagram below follow the layout defined in the knowledge repo's Structure principles and your stack's layout note (entry: `README-AGENT.md`). If your selected stack differs structurally, swap layer names, paths, and language to match — the section structure (Summary → Layer Impact → Dependencies → Implementation Steps → Breaking Changes → Data Flow → Error Handling → Testing → Acceptance) stays the same.

## 1. Summary

**What:** <One sentence describing what this design achieves>

**Why:** <Link to feature spec problem statement>

## 2. Layer Impact

_Add one row per file affected. Layer names follow the knowledge repo's Structure principles and your stack's layout note (entry: `README-AGENT.md`)._

| Layer     | File          | Change                |
| --------- | ------------- | --------------------- |
| `<layer>` | `<file path>` | `<change description>` |

<details>
<summary>Example fills (Python stack)</summary>

| Layer    | File                           | Change                                |
| -------- | ------------------------------ | ------------------------------------- |
| Core     | `core/logic.py`                | New `compute_score()` pure function   |
| Core     | `core/models.py`               | Add `Score` pydantic model            |
| Adapters | `adapters/providers/api.py`    | New `fetch_raw_data()` method         |
| Services | `services/scoring.py`          | Coordinates fetch + compute           |
| CLI      | `main.py`                      | New `score` click subcommand          |

</details>

## 3. Dependencies

_New libraries, tools, or architectural dependencies introduced by this design._

| Dependency | Purpose        | Justification                        |
| ---------- | -------------- | ------------------------------------ |
| `<lib>`    | <what it does> | <why not stdlib or an existing dep>  |

_If no new dependencies: "None — implemented using existing stack."_

## 4. Implementation Steps

_Ordered steps for the Developer to follow._

### Step 1: <Layer - File>

```
<code change>
```

### Step 2: <Layer - File>

```
<code change>
```

### Step 3: Wire entry point

```
<code change>
```

<details>
<summary>Example fills (Python stack)</summary>

### Step 1: Core — `core/logic.py`

```python
def compute_score(items: list[Item]) -> Score:
    """Pure scoring computation. No I/O."""
    return Score(value=sum(i.weight for i in items))
```

### Step 2: Adapters — `adapters/providers/api.py`

```python
class APIProvider:
    def fetch_raw_data(self, query: str) -> list[dict]:
        response = httpx.get(self.url, params={"q": query})
        response.raise_for_status()
        return response.json()
```

### Step 3: Wire entry point — `main.py`

```python
@cli.command()
@click.argument("query")
def score(query: str) -> None:
    """Score items matching QUERY."""
    raw = APIProvider().fetch_raw_data(query)
    items = [Item.model_validate(r) for r in raw]
    result = compute_score(items)
    click.echo(result.value)
```

</details>

## 5. Breaking Changes

_API breakages or data migration requirements introduced by this design._

| Change                   | Impact              | Migration Path      |
| ------------------------ | ------------------- | ------------------- |
| <e.g., renamed function> | <callers affected>  | <how to migrate>    |

_If no breaking changes: "None."_

## 6. Data Flow

```
<input> → <entry point>
    → <service>.<operation>()
        → <adapter>.<call>() → <external system>
        → <logic>.<compute>()
    → <return value>
→ <output>
```

## 7. Error Handling

| Error Scenario        | Raised Exception     | Handled In                           |
| --------------------- | -------------------- | ------------------------------------ |
| <e.g., API timeout>   | `APIConnectionError` | Adapter catches, raises domain error |
| <e.g., Invalid input> | `ValidationError`    | Core logic                           |

## 8. Testing Checklist

_For the Developer to implement._

- [ ] Unit test for core logic - test the pure function
- [ ] Unit test for adapter - mock external I/O
- [ ] Integration test for CLI command - verify full flow

**Test cases:**

1. Happy path: <input> → <expected output>
2. Error case: <invalid input> → <expected error>

## 9. Acceptance Criteria

_Copied from feature spec - Developer must verify all pass._

- [ ] <Criterion 1 from feature spec>
- [ ] <Criterion 2 from feature spec>

---

## Architect Checklist (Complete before handoff)

- [ ] All feature spec acceptance criteria mapped to implementation steps
- [ ] Layer/module placement follows the knowledge repo's Structure principles
- [ ] No logic in adapters (only I/O translation)
- [ ] No external imports in core layer
- [ ] New dependencies listed in Section 3 with justification
- [ ] Breaking changes identified in Section 5
- [ ] Error scenarios identified with specific exceptions
- [ ] Test cases cover happy path and error cases
- [ ] Data flow diagram matches implementation steps

_Handoff to Developer Agent_
