# Interface Contract: `<boundary-name>`

> Contract template for a cross-repo boundary that is **not** an HTTP API — a
> database schema, an event or queue topic, a shared types / client SDK package,
> a file or export format, a handshake, or config keys two repos must agree on.
> For an HTTP surface use `human-contract-api.md` instead.
>
> Same job as the API contract, same freeze discipline: this file is the single
> source of truth for observable behavior **at the boundary**. The **producer**
> (must emit) and the **consumer** (must accept) are built against this file, and
> it changes *before* either side does.
>
> Keywords **MUST / SHOULD / MAY** are normative (RFC 2119). Specify observable
> behavior at the boundary only — never implementation (no frameworks, no
> internal architecture, no migration tooling).

| | |
| :-- | :-- |
| **Contract version** | `0.1.0` |
| **Kind** | `<db-schema \| event \| shared-types \| file-format \| handshake \| config>` |
| **Producer** | `<repo role that owns and emits this — e.g. service>` |
| **Consumer(s)** | `<repo role(s) that read it — e.g. ui, reporting>` |
| **Status** | Draft \| Frozen |
| **Last updated** | `<YYYY-MM-DD>` |
| **Source** | human \| refiner-program |

_`Source` records who authored this contract; it defaults to `human`. The Program
Refiner sets it to `refiner-program` when it drafts a delta, so provenance audits
can distinguish generated contracts from human-authored ones._

**Status rules**
- `Draft`: shape may still change; work on either side should treat it as provisional.
- `Frozen`: approved for implementation; incompatible changes require a version bump (§ 5).

## 1. Scope

- **In scope:** `<the exact tables / topics / exported types / files this contract covers>`
- **Out of scope (non-goals):** `<state what does NOT exist so no one invents it — e.g. "no soft-delete", "no replay", "no cross-tenant reads">`
- **Direction:** `<producer → consumer; note if it is bidirectional and why>`
- **Compatibility expectation:** `<who breaks if this changes, and what counts as breaking — expanded in § 5>`

## 2. Boundary Conventions

_Fill the rows that apply to this Kind; delete the rest._

| Item | Value |
| :-- | :-- |
| Encoding / format | `<e.g. JSON, Avro, Postgres DDL, TypeScript declarations>` |
| Naming convention | `<e.g. snake_case columns; <domain>.<event>.v<N> topics>` |
| Versioning scheme | `<e.g. topic suffix, package semver, migration sequence>` |
| Delivery semantics | `<at-least-once \| exactly-once \| n/a>` |
| Ordering guarantee | `<per-key \| none \| n/a>` |
| Idempotency | `<key the consumer dedupes on, or "not required">` |
| Time & timezone | `<e.g. all timestamps ISO-8601 with offset; storage in UTC>` |
| Nullability default | `<state it explicitly — never leave it implied>` |

## 3. Shape

_The actual surface. Concrete enough that producer and consumer can be built
independently without guessing._

### `<TableName / TopicName / ExportedType / FileName>`

```
<DDL, payload example, type declaration, or record layout — whichever the Kind calls for>
```

| Field | Type | Required | Nullable | Constraints / format | Notes |
| :-- | :-- | :-- | :-- | :-- | :-- |
| `<field>` | `<type>` | yes | no | `<e.g. unique, 1–50 chars, FK → other.id>` | |
| `<field>` | `<type>` | no | yes | | `<default, and who supplies it>` |

**Invariants:** `<rules that must hold across fields — e.g. "closed_at is null iff status = open">`

<!-- Repeat per table / topic / exported type. Define reusable shapes once and
     reference them rather than restating. -->

## 4. Reference Fixtures

_At least one valid example per shape above, plus one edge state. Both sides test
against these._

```
<fixture>
```

## 5. Compatibility & Breaking Changes

_The section that earns the freeze gate. Be explicit — "probably fine" is not a
compatibility statement._

| Change | Breaking? | Required migration path |
| :-- | :-- | :-- |
| Add optional field | no | `<consumer ignores unknown fields>` |
| Add required field | **yes** | `<expand → backfill → contract, in that order>` |
| Remove / rename field | **yes** | `<deprecate for N releases, then remove>` |
| Widen a type | `<yes/no>` | |
| Narrow a type or tighten a constraint | **yes** | |
| Change semantics of an existing field | **yes** | `<new field instead; never silently reinterpret>` |

- **Consumers MUST tolerate:** `<e.g. unknown fields, unknown enum values, out-of-order delivery>`
- **Producers MUST NOT:** `<e.g. reuse an identifier, reorder positional records, drop a column in the same release it is deprecated>`
- **Rollback story:** `<what happens if the producer is rolled back after the consumer ships>`

## 6. Failure & Edge Behavior

- **Malformed / unreadable input:** `<what the consumer does — reject, dead-letter, halt>`
- **Missing optional data:** `<default, or explicit absence>`
- **Empty / zero state:** `<what a valid empty result looks like>`
- **Volume limits:** `<max payload, max rows, retention window, or "none today">`

## 7. Conformance Checklist

> Testable assertions. Neither side is done until its column passes. Put the
> matching tests in `tests/contract/`.

- [ ] Contract status is `Frozen` before either side's implementation is considered complete.
- [ ] Producer emits every shape in § 3 exactly as documented, including nullability.
- [ ] Consumer accepts all § 4 fixtures, including the edge state.
- [ ] Consumer tolerates everything listed under "Consumers MUST tolerate" (§ 5).
- [ ] Documented invariants (§ 3) are enforced by the producer, not assumed by the consumer.
- [ ] Failure behaviors (§ 6) are covered by tests, not just described.
- [ ] Version bumped if any row marked **breaking** in § 5 was taken.

## 8. Open Questions & Assumptions

- `<undecided shapes, retention/limits nobody has set, behaviors to revisit>`
