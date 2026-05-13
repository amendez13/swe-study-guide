## Filtering collections

Collection endpoints rarely return every resource. Filters let clients narrow the result set to what matters, such as `status=paid` or `created_after=2026-01-01`.

The main design goal is predictability. If each endpoint invents a different filter style, the API becomes harder to learn than the business problem it is meant to solve.

```http
GET /orders?status=paid&customer_id=7
GET /invoices?due_before=2026-05-31
```

## Sorting result sets

Sorting gives clients control over result order and affects everything from UI presentation to batch-processing correctness. A good API makes sort fields and sort direction explicit instead of relying on unstable implicit defaults.

This matters because ordering is part of the observable contract. If pagination is involved, an unstable sort can cause duplicates or missing records between pages.

```http
GET /orders?sort=-created_at
GET /orders?sort=status,created_at
```

## Pagination strategies

Pagination keeps collection responses bounded and makes large datasets traversable. Offset pagination is simple and familiar, while cursor pagination is usually more stable for large or frequently changing datasets.

The right choice depends on usage patterns. Offset is easier for "go to page 5"; cursor is better when consistency under insertion and deletion matters more than random page jumps.

```http
GET /orders?limit=20&offset=40
GET /orders?limit=20&cursor=eyJpZCI6NDJ9
```

## Result metadata

Paginated responses often need more than a list of items. Counts, page size, cursors, and next-page links help clients continue the workflow without guessing how the server expects traversal to work.

Without metadata, consumers end up reverse-engineering behavior from trial and error. That usually means brittle integrations.

```json
{
  "items": [{"id": 41}, {"id": 42}],
  "next_cursor": "eyJpZCI6NDJ9",
  "limit": 2
}
```

## Backward compatibility

Once clients ship against an API, behavior becomes sticky. Renaming fields, changing defaults, or redefining semantics can break consumers even if the server still compiles and tests pass locally.

This is why compatibility is a product decision, not just a code decision. The cost of breaking a contract is often borne by teams outside the one making the change.

Example: changing `total_cents` to `amount` may look harmless in code review, but it can break billing exports, dashboards, and mobile apps immediately.

## Versioning strategies

Versioning is how teams introduce meaningful incompatible change without silently breaking everyone. Common approaches include path-based versioning like `/v2/orders`, header-based versioning, and media-type versioning.

Each approach has tradeoffs. Path versioning is obvious and easy to debug; header or media-type versioning keeps URLs cleaner but makes requests harder to inspect casually.

```http
GET /v2/orders
Accept: application/vnd.example.orders+json;version=2
```

## Deprecation and additive change

The safest API evolution is usually additive: introduce optional fields or new endpoints without changing the meaning of old ones. When removal is necessary, deprecation should be explicit, documented, and scheduled.

Clients need time and guidance to migrate. A backend team that removes behavior without a transition plan pushes operational risk downstream to everyone else.

Example: add a new `discount_code` field first, mark `coupon` deprecated in docs and response headers, then remove it only after clients migrate.
