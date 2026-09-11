# Refactor Request: <Short Description>

## Metadata

```yaml
ID: <YYYYMMDD>-<NN>
Priority: <Low | Medium | High>
Risk: <Low | Medium | High>
```

## 1. Goal

**What to improve:** <One sentence describing the improvement>

**Why now:** <Why is this refactor needed?>

## 2. Scope

### Files to Refactor

| File | Current State | Desired State |
|------|---------------|---------------|
| `<file>` | <what's wrong> | <what it should be> |

### Explicit Boundaries

**In scope:**
- <What CAN be changed>

**Out of scope:**
- <What must NOT be changed>

## 3. Constraints

- [ ] Behavior must remain identical
- [ ] All existing tests must pass
- [ ] No new dependencies
- [ ] Public API signatures unchanged (unless specified below)

**Allowed signature changes:**
- <None, or list specific functions that can change>

## 4. Success Criteria

_How will we know the refactor is successful?_

- [ ] <Criterion 1: e.g., "No function longer than 20 lines">
- [ ] <Criterion 2: e.g., "All logic moved out of adapters">
- [ ] All tests pass
- [ ] `${QUALITY_GATE}` passes

## 5. Risks

| Risk | Mitigation |
|------|------------|
| <e.g., Breaking existing callers> | <e.g., Run full test suite> |

## 6. Notes

<Any additional context or preferences>
