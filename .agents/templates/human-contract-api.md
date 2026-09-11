# API Contract: `<service-name>`

> Production-ready Markdown contract template for real HTTP APIs. This file is the
> single source of truth for observable wire behavior. Both the **server**
> (must produce) and the **client** (must consume) are built against this file.
> Change this file *before* changing either side.
>
> Use this when humans need to review the API behavior clearly and when separate
> implementers or agents need enough precision to build both sides independently.
> This can be used for serious production APIs. If you also need generated SDKs,
> generated public docs, or automated schema tooling, maintain an OpenAPI spec
> alongside this contract or derive one from it.
>
> Keywords **MUST / SHOULD / MAY** are normative (RFC 2119). Specify observable
> behavior at the boundary only — never implementation (no frameworks, no internal
> architecture).

| | |
| :-- | :-- |
| **Contract version** | `0.1.0` |
| **Server version(s)** | `<branch / tag this describes>` |
| **Status** | Draft \| Frozen |
| **Last updated** | `<YYYY-MM-DD>` |
| **Source** | human \| api-contract-builder \| refiner-program |
| **Requirement** | `<path under .docs/requirements/, PRODUCT.md, or —>` |

_`Source` records who authored this contract; it is optional and defaults to `human`. The API Contract Builder sets it to `api-contract-builder` when generating a Draft contract, and the Program Refiner sets it to `refiner-program` when drafting a delta for an HTTP boundary a program story crosses — so provenance audits can distinguish generated contracts from human-authored ones. `Requirement` records the intake file the contract was built from — the path the agent read (e.g. `.docs/requirements/20260822-01-sketch-orders-api.md`, or the program requirement for a delta); `—` for a human-authored contract with no file source. Downstream agents ignore both fields; they exist so a requirement can be amended and its contract found._

**Status rules**
- `Draft`: behavior may still change; client/server work should treat this as provisional.
- `Frozen`: behavior is approved for implementation; incompatible changes require a contract version bump.

## 1. Scope

- **In scope:** `<list the endpoints / surface this contract covers>`
- **Out of scope (non-goals):** `<state what does NOT exist so no one invents it,
  e.g. "no quote endpoint", "no auth", "no pagination">`
- **Compatibility expectation:** `<who consumes this API and what changes are breaking>`

## 2. Conventions

| Item | Value |
| :-- | :-- |
| Protocol | `HTTP/1.1, JSON` |
| Base URL | Injectable; client MUST NOT hardcode host/port. Dev default: `<url>` |
| Auth | `<scheme, or "None">` |
| Request content type | `application/json` |
| Response content type | `application/json` |
| Charset | `UTF-8` |

## 3. Shared Schemas

Define each reusable object once; reference it from endpoints. Keep schemas concrete
enough that the server and client can be built independently without guessing.

Unless stated otherwise:
- Field names are case-sensitive.
- Required means the field must be present. Nullability must be stated explicitly.
- Unknown enum values in requests are invalid input.
- Clients SHOULD handle unknown enum values in responses without crashing unless
  the field explicitly says otherwise.
- Datetimes MUST be ISO-8601 and include a timezone offset. Server SHOULD return
  UTC (`Z`) unless an endpoint says otherwise.
- Array ordering is not guaranteed unless an endpoint documents it.

### `<ObjectName>`
```json
{ "<field>": "<example>" }
```
| Field | Type | Required | Nullable | Constraints / format | Notes |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `<field>` | string | yes | no | `<e.g. trimmed, 1–50 chars>` | |
| `<field>` | datetime | yes | no | ISO-8601, timezone-aware | precision not guaranteed |
| `<field>` | string | no | no | one of: `<a>`, `<b>` | enum values are case-sensitive |

## 4. Endpoints

> One subsection per endpoint. List a response row for **every** expected status
> code, success and failure. State the *exact* success status (don't assume `200`).
> Do not use `default` as a substitute for known failure modes; unknown and
> non-envelope failures are handled by §6 fallback rules.

### `<METHOD> <path>`
`<one-line purpose>`

- **Path params:** `<schema/table, or "none">`
- **Query params:** `<schema/table, or "none">`
- **Request body:** `<schema, or "none">`
- **Ordering:** `<for list responses only; otherwise omit>`
- **Responses:**

| Status | Body | When |
| :-- | :-- | :-- |
| `200` | `<Schema>` | success |
| `422` | Error envelope (`validation_error`) | `<invalid input condition>` |

**Example request**
```json
{ }
```

**Example success response**
```json
{ }
```

## 5. Reference Fixtures

> A canonical seed dataset for this contract. Both the contract tests (§9) and any
> mock server used for independent client development draw from these records, so
> every consumer sees the same data. This section is **data only** — name no mock
> tool or framework here (that is implementation). Any mock MUST serve data
> conforming to these fixtures and to the §3 schemas.

Rules:
- Every fixture **MUST** validate against its §3 schema; invalid fixtures teach
  consumers the wrong shape with false confidence.
- Cross-entity references **MUST** resolve — an ID used in one record exists as a
  record in the referenced collection.
- Cover the states the UI must render: empty collection, a single item, many
  items, and at least one instance of each error envelope from §6.
- These fixtures are the source of truth for example data; the per-endpoint
  `Example` blocks in §4 SHOULD reuse values from here rather than inventing
  one-offs, so examples and fixtures cannot disagree.

### `<EntityName>` (collection)
```json
[
  { "<field>": "<value>" },
  { "<field>": "<value>" }
]
```

### Error envelopes
```json
{ "error": { "code": "validation_error", "message": "<human text>", "fields": { "<field>": "<why>" } } }
```

### Edge-state fixtures
| State | Fixture | Used by |
| :-- | :-- | :-- |
| empty collection | `[]` | `<GET list endpoint>` |
| not found | `<error envelope + code>` | `<GET by id>` |
| `<boundary value>` | `<record at max length / min, etc.>` | `<endpoint>` |

## 6. Error Model

### Envelope
```json
{ "error": { "code": "<stable_code>", "message": "<human text>", "fields": { } } }
```
- Clients **MUST** branch on `error.code` — never on `message` or status alone.
- `error.fields` is **optional**; present only for `<which cases>`. Null-check it.
- `message` is safe to surface/log; **MUST NOT** contain a stack trace.
- If correlation is supported, the response header is the source of truth for the
  correlation ID. Include it in the body only if explicitly documented.

### Codes
| `code` | HTTP status | Meaning | Client action |
| :-- | :-- | :-- | :-- |
| `validation_error` | 422 | input rejected | fix input; do not retry unchanged |
| `<code>` | `<status>` | `<meaning>` | `<retry? surface? ...>` |

### Non-envelope errors (clients MUST handle)
> Not every error is the JSON envelope. List the exceptions explicitly.
- `<e.g. unknown path / wrong method → framework default HTML 404/405>`
- `<e.g. 5xx may arrive without the envelope>`
- **Rule:** attempt to parse `error.code`; if absent/unparseable, fall back to
  status-code handling. MUST NOT crash on a non-JSON error body.

## 7. Edge Cases & Guarantees

> The highest-value section — pin everything two implementers could disagree on.
- **Malformed / empty JSON body:** `<exact status + code>` (e.g. `422`, not `400`).
- **Unknown / extra fields:** `<rejected? ignored?>`
- **Nulls vs missing fields:** `<same behavior or different?>`
- **Boundary values:** `<empty, max length+1, etc. → expected result>`
- **Trailing slash / case sensitivity / URL-encoding:** `<behavior>`
- **Idempotency & retries:** `<is this method safe to retry? can it duplicate?>`

## 8. Headers & Cross-Cutting

- **Correlation:** `<header name>` echoed on every response; server honors an
  inbound `<header>` and MUST NOT overwrite it. Client SHOULD send it to correlate.
- **Pagination:** `<scheme, or "none today">`
- **Rate limits:** `<rules, or "none today">`
- **Caching:** `<rules, or "none today">`

## 9. Conformance Checklist

> Testable assertions. Neither side is "done" until its column passes. Put the
> matching contract tests in `tests/contract/`.

- [ ] Base URL injectable; no hardcoded host/port.
- [ ] Contract status is `Frozen` before implementation is considered complete.
- [ ] Each endpoint returns the documented status + body shape.
- [ ] Reference fixtures (§5) validate against all §3 schemas and their cross-references resolve.
- [ ] Path params, query params, and request body are handled separately as documented.
- [ ] `<error code>` raises a typed client error exposing `code` / `message` / `fields`.
- [ ] Non-envelope errors handled without crashing the parser.
- [ ] Correlation header sent (when provided) and read on every response.
- [ ] Documented edge cases (§7) covered by tests.

## 10. Open Questions & Assumptions

- `<defined-but-unreachable codes, undecided behaviors, things to revisit>`
