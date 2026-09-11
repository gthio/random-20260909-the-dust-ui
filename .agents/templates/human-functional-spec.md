# Functional Specification: `<feature / product / workflow name>`

> The source of truth for what this feature must do from the user's and business's point of view.
> This document defines intended behavior, user-visible outcomes, rules, edge cases, and acceptance criteria.
> It should be updated before implementation changes that alter behavior.
>
> This is a functional specification, not a technical design. Describe **what** the system must do and **how it should behave** at observable boundaries. Avoid implementation details unless they affect user-visible behavior.

| | |
| :-- | :-- |
| **Spec version** | `0.1.0` |
| **Status** | Draft \| Review \| Approved \| Deprecated |
| **Owner** | `<person / team>` |
| **Reviewers** | `<product / design / engineering / QA / support>` |
| **Related docs** | `<links to API contract, designs, tickets, metrics, research>` |
| **Last updated** | `<YYYY-MM-DD>` |

_Save this spec as `.docs/requirements/<YYYYMMDD-NN>-functional-spec-<short-name>.md` (see `.agents/context.md` § Requirements). That path is what `/refiner` or `/api-contract-builder` reads, and what the resulting feature specs or contract cite as their `Requirement`. Delete this note when the spec is filled in._

## 1. Summary

`<One or two paragraphs describing the feature, workflow, or behavior in plain language.>`

The summary should answer:
- What is being built or changed?
- Who is it for?
- What user or business problem does it solve?
- What is the expected outcome?

## 2. Content Model

> *Optional — applies only if the product has structured content entities (e.g. not a pure workflow tool with no data model). If not applicable, write exactly `Not applicable` and nothing else; do not invent entities. Delete this note when the section is filled in.*

Define the core units of content or data this feature operates on. This is not a database schema — describe what a "thing" is in product terms, its fields, and any structural layers.

### `<entity name>`

`<One sentence describing what this entity represents.>`

| Field | Type | Description | Constraints |
| :-- | :-- | :-- | :-- |
| `<field>` | `<string / number / boolean / object / list>` | `<what it is>` | `<required, max length, format, etc.>` |

**Layers (if applicable):** describe whether the entity has display layers, states, or sub-structures visible to the user (e.g. at-rest vs. revealed, draft vs. published).

---

## 3. Goals and Non-Goals

### Goals

- `<specific outcome this feature must achieve>`
- `<specific user or business capability>`
- `<specific behavior that must exist>`

### Non-Goals

State what is intentionally not part of this spec so no one invents extra scope.

- `<behavior / workflow / integration that is explicitly out of scope>`
- `<future capability that should not be built now>`
- `<manual process that remains manual>`

## 4. Users and Actors

| Actor | Description | Permissions / Role | Notes |
| :-- | :-- | :-- | :-- |
| `<actor name>` | `<who they are>` | `<what they can do>` | `<important assumptions>` |
| `<system / external service>` | `<what it represents>` | `<n/a or role>` | `<integration expectations>` |

## 5. User Scenarios

Use concrete scenarios to describe expected behavior.

### Scenario: `<short scenario name>`

**Given** `<initial state / context>` \
**When** `<user or system action>` \
**Then** `<observable outcome>`

Notes:
- `<important business rule or UX expectation>`
- `<known constraint>`

## 6. Functional Requirements

Requirements should be specific, testable, and observable.

| ID | Requirement | Priority | Acceptance Criteria |
| :-- | :-- | :-- | :-- |
| FR-001 | `<The system MUST ...>` | Must | `<How reviewers/testers know this passes>` |
| FR-002 | `<The user SHOULD be able to ...>` | Should | `<Expected observable behavior>` |
| FR-003 | `<The system MAY ...>` | May | `<Optional behavior, if implemented>` |

Keyword guidance:
- **MUST** = required for release.
- **SHOULD** = expected unless there is a documented reason not to.
- **MAY** = optional behavior.

## 7. User Experience and Interaction Rules

Describe user-visible behavior without prescribing implementation.

### Entry Points

- `<where users start this workflow: page, button, command, API consumer, automation trigger>`

### Main Flow

1. `<user/system does this>`
2. `<system responds with this>`
3. `<user/system continues with this>`
4. `<workflow completes when this happens>`

### States

| State | Meaning | User-visible behavior | Allowed actions |
| :-- | :-- | :-- | :-- |
| `<state>` | `<what it represents>` | `<what the user sees>` | `<what can happen next>` |

### Messages and Copy

| Situation | Message / Copy | Notes |
| :-- | :-- | :-- |
| `<success>` | `<exact or approximate text>` | `<whether exact wording is required>` |
| `<validation failure>` | `<text shown to user>` | `<tone / recovery guidance>` |
| `<empty state>` | `<text shown to user>` | `<CTA if any>` |

## 8. Business Rules

List rules that determine behavior, eligibility, calculations, visibility, or workflow decisions.

| Rule ID | Rule | Applies When | Outcome |
| :-- | :-- | :-- | :-- |
| BR-001 | `<If ... then ...>` | `<condition>` | `<result>` |
| BR-002 | `<User cannot ... when ...>` | `<condition>` | `<error / disabled / hidden / fallback>` |

## 9. Inputs, Outputs, and Data Expectations

This section defines functional data expectations. Detailed wire formats belong in an API contract (see `.agents/templates/human-contract-api.md`).

### Inputs

| Input | Source | Required | Valid Values / Constraints | Behavior if Missing or Invalid |
| :-- | :-- | :-- | :-- | :-- |
| `<input>` | `<user / system / API / file>` | yes/no | `<format, range, enum, length>` | `<error, default, ignored>` |

### Outputs

| Output | Recipient | Required | Notes |
| :-- | :-- | :-- | :-- |
| `<output>` | `<user / system / API / report>` | yes/no | `<visibility, timing, format expectation>` |

### Data Retention / Visibility

- **Stored data:** `<what is stored, or "none">`
- **Visible to user:** `<what users can see>`
- **Visible to admins/support:** `<what internal users can see>`
- **Deletion / expiry:** `<rules, or "not applicable">`

## 10. Validation, Errors, and Recovery

| Case | Expected Behavior | User/System Message | Recovery |
| :-- | :-- | :-- | :-- |
| `<invalid input>` | `<reject / ignore / default>` | `<message or error>` | `<what user/system can do next>` |
| `<missing dependency>` | `<fallback behavior>` | `<message or error>` | `<retry / contact support / manual step>` |
| `<permission denied>` | `<block action>` | `<message or error>` | `<request access / sign in>` |

Rules:
- Errors should explain what happened and what can be done next.
- The system MUST NOT expose internal stack traces or implementation details to end users.
- If an operation partially succeeds, this spec MUST state what is committed, what is rolled back, and what the user sees.

## 11. Edge Cases and Guarantees

Pin down behavior that two implementers or reviewers could reasonably disagree on.

- **Empty state:** `<what happens when there is no data>`
- **Duplicate action:** `<what happens if the same action is repeated>`
- **Concurrent changes:** `<last write wins / conflict shown / blocked / unspecified>`
- **Boundary values:** `<minimum, maximum, max+1 behavior>`
- **Permissions changes during workflow:** `<expected behavior>`
- **Network / dependency failure:** `<retry, fail, queue, fallback>`
- **Ordering:** `<if lists are shown, specify order or say unspecified>`
- **Timezone / date handling:** `<user locale, UTC, fixed timezone, or not applicable>`
- **Localization:** `<copy/date/number behavior, or "not in scope">`

## 12. Notifications, Emails, and External Communications

> *Optional — applies only if the feature sends user-visible communications. If not applicable, write exactly `Not applicable` and nothing else; do not invent triggers or messages. Delete this note when the section is filled in.*

| Trigger | Recipient | Channel | Content | Suppression / Frequency Rules |
| :-- | :-- | :-- | :-- | :-- |
| `<event>` | `<user/admin/external party>` | `<email/push/webhook/etc.>` | `<summary or link to copy>` | `<once, every time, rate-limited>` |

## 13. Permissions, Privacy, and Compliance

> *Fill only the lines that apply. For any line with no real constraint, write exactly `Not applicable`; do not invent compliance obligations, audit requirements, or sensitive-data categories. Delete this note when the section is filled in.*

- **Who can access this feature:** `<roles / conditions>`
- **Who can perform destructive actions:** `<roles / conditions>`
- **Sensitive data involved:** `<none, or list categories>`
- **Audit trail required:** `<yes/no; what must be recorded>`
- **Consent or disclosure required:** `<yes/no; details>`
- **Compliance constraints:** `<none, or relevant obligations>`

## 14. Dependencies and Assumptions

### Dependencies

| Dependency | Required For | Expected Behavior if Unavailable |
| :-- | :-- | :-- |
| `<service / system / team / data source>` | `<feature behavior>` | `<fallback / error / blocked>` |

### Assumptions

- `<assumption that affects behavior or scope>`
- `<assumption to validate before release>`

## 15. Metrics and Success Criteria

> *Optional — include only metrics that are actually tracked or agreed. If none exist, write exactly `Not applicable`; do not invent targets, dashboard names, or event names. Delete this note when the section is filled in.*

| Metric | Definition | Target / Expected Movement | Notes |
| :-- | :-- | :-- | :-- |
| `<metric>` | `<how it is measured>` | `<target>` | `<dashboard/event name if known>` |

Success criteria:
- `<specific measurable or reviewable release outcome>`
- `<quality or behavior threshold>`

## 16. Rollout and Compatibility

> *Fill only the lines that apply. For any line with no real constraint, write exactly `Not applicable`; do not invent migration steps, flags, or rollback procedures. Delete this note when the section is filled in.*

- **Rollout plan:** `<all users / feature flag / beta / phased rollout>`
- **Migration needed:** `<yes/no; describe>`
- **Backward compatibility:** `<what existing behavior must remain unchanged>`
- **Rollback behavior:** `<what happens if disabled or reverted>`
- **Support impact:** `<docs, training, support macros, or "none">`

## 17. Acceptance Checklist

Neither implementation nor review is complete until the checklist passes.

- [ ] Goals and non-goals are clear.
- [ ] Content model (entities, fields, layers) is defined, or the section is intentionally skipped.
- [ ] All user-visible flows are covered.
- [ ] Functional requirements are testable.
- [ ] Business rules are explicit.
- [ ] Inputs, outputs, and invalid cases are defined.
- [ ] Empty, duplicate, boundary, and failure cases are covered.
- [ ] Permissions and privacy expectations are defined.
- [ ] User-facing messages are documented or intentionally delegated.
- [ ] Dependencies and assumptions are listed.
- [ ] Metrics or release success criteria are defined.
- [ ] Rollout, compatibility, and rollback behavior are defined.
- [ ] Open questions are resolved or explicitly accepted for this release.

## 18. Open Questions and Decisions

### Open Questions

| ID | Question | Owner | Needed By | Status |
| :-- | :-- | :-- | :-- | :-- |
| OQ-001 | `<question>` | `<person/team>` | `<date/milestone>` | Open |

### Decisions

| Date | Decision | Rationale | Owner |
| :-- | :-- | :-- | :-- |
| `<YYYY-MM-DD>` | `<decision>` | `<why>` | `<person/team>` |
