# Gardener Request: <Short Description>

## Metadata

```yaml
ID: <YYYYMMDD>-<NN>
Priority: <Low | Medium | High>
```

## 1. Goal

**Problem:** <One sentence describing the readability issue>
**Context:** <Why this polish is needed now>

## 2. Scope

### Files to Review

| File     | Readability Problem            |
| -------- | ------------------------------ |
| `<file>` | <e.g., cryptic variable names> |

### Focus Areas

- [ ] **Naming** (cryptic/generic names)
- [ ] **Standardization** (inconsistent terminology)
- [ ] **Complexity** (long chains needing intermediate variables)
- [ ] **Idiomatic Patterns** (e.g., using pathlib)
- [ ] **Comments** (missing "why" or redundant "what")

### Constraints & Boundaries

**Strictly Prohibited:**

- Changing public function signatures or API
- Modifying business logic or conditionals
- Adding/removing dependencies
- Reorganizing files

**In scope:**

- <Specific renames or rephrasing allowed>

## 3. Success Criteria

- [ ] <Specific target, e.g., "Generic terms like 'data' replaced with specific domain terms">
- [ ] All existing tests pass
- [ ] `${QUALITY_GATE}` passes

## 4. Notes

<Additional context or specific patterns to avoid/use>
