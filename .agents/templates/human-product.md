# Product Brief: <Product Name>

## Metadata

```yaml
ID: <YYYYMMDD>
Type: Product
```

_Save this brief as `.docs/requirements/<YYYYMMDD-NN>-brief-<short-name>.md` (see `.agents/context.md` § Requirements) and pass that path to `/founder-architect`. It stays there as the amendment anchor: `PRODUCT.md` and every bootstrap feature spec cite it, and a later `/founder-replan` amends against it. Delete this note when the brief is filled in._

## 1. Vision

- **For whom:** <persona / end user>
- **Problem:** <pain point in plain language>
- **Success looks like:** <how you will know the MVP is "done">

## 2. Hard Constraints

_Things the system cannot do, must do, or must work around. These shape architecture, not features._

- <e.g., "Human must clear Cloudflare manually — fully unattended scraping is not viable.">
- <e.g., "Operator runs it on a laptop; CI runs only the unattended path.">

## 3. Out of Scope (for MVP)

- <e.g., "No distributed scraping.">
- <e.g., "No web UI — CLI only.">

## 4. Open Questions

_Things to flag, not auto-decide._

- <e.g., "Legal/ToS posture for target sites.">
