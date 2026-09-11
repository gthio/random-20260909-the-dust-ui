# Review Report: <Feature/Fix Name>

*Review Date: <YYYYMMDD>*
*Reviewer: <Agent/Human>*
*Review Type: <Feature | Bugfix | Refactor>*

## Summary

**Status:** `APPROVED` | `NEEDS CHANGES` | `REJECTED`

**Verdict:** <One sentence summary of review outcome>

---

## 1. Design Compliance

*Does implementation match the design document?*

| Design Item | Expected | Actual | Status |
|-------------|----------|--------|--------|
| `<file>` | `<function/change>` | `<what was done>` | ✓ / ✗ |

**Issues:**
- <List any deviations from design>

---

## 2. Acceptance Criteria

*Are all feature spec requirements met?*

| Criterion (from feature spec) | Test | Verified |
|----------------------|------|----------|
| <criterion 1> | `test_<name>` | ✓ / ✗ |
| <criterion 2> | `test_<name>` | ✓ / ✗ |

**Issues:**
- <List any unmet criteria>

---

## 3. Architecture Compliance

| Check | Status | Notes |
|-------|--------|-------|
| No logic in adapters | ✓ / ✗ | |
| No external imports in core | ✓ / ✗ | |
| Dependencies point inward | ✓ / ✗ | |
| Protocols used for DI | ✓ / ✗ | |

---

## 4. Code Quality

| Check | Status | Notes |
|-------|--------|-------|
| Type hints complete | ✓ / ✗ | |
| No magic values | ✓ / ✗ | |
| No `print()` statements | ✓ / ✗ | |
| Naming follows conventions | ✓ / ✗ | |
| No scope creep | ✓ / ✗ | |

---

## 5. Test Quality

| Check | Status | Notes |
|-------|--------|-------|
| Tests independent | ✓ / ✗ | |
| Single assert per test | ✓ / ✗ | |
| Error cases covered | ✓ / ✗ | |
| Mocks only external I/O | ✓ / ✗ | |

---

## 6. Verification Results

```bash
${QUALITY_GATE}
```

| Check | Result |
|-------|--------|
| `<lint command>` | PASS / FAIL |
| `<typecheck command>` | PASS / FAIL |
| `<test command>` | PASS / FAIL |
| `<security command>` | PASS / FAIL |

---

## 7. Issues Found

| # | Severity | File:Line | Description |
|---|----------|-----------|-------------|
| 1 | BLOCKER / WARNING / NOTE | `<file>:<line>` | <description> |

**Severity Guide:**
- `BLOCKER` - Must fix before merge
- `WARNING` - Should fix, deviation from standards
- `NOTE` - Optional improvement

---

## 8. Required Changes

*List specific changes needed before approval (if status is NEEDS CHANGES):*

- [ ] <Change 1>
- [ ] <Change 2>

---

## 9. Sign-off

- [ ] Reviewer has verified all checks
- [ ] All BLOCKER issues resolved (if re-review)
- [ ] Ready for Human Gate

**Reviewed by:** <Agent name>
**Date:** <YYYYMMDD>
