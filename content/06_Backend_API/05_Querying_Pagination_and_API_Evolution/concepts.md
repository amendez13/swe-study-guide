## Filtering collections

Collection endpoints rarely return every resource. Filters let clients narrow the result set to what matters, such as `status=paid` or `created_after=2026-01-01`.

The main design goal is predictability. If each endpoint invents a different filter style, the API becomes harder to learn than the business problem it is meant to solve.

## Sorting result sets

Sorting gives clients control over result order and affects everything from UI presentation to batch-processing correctness. A good API makes sort fields and sort direction explicit instead of relying on unstable implicit defaults.

This matters because ordering is part of the observable contract. If pagination is involved, an unstable sort can cause duplicates or missing records between pages.

## Pagination strategies

Pagination keeps collection responses bounded and makes large datasets traversable. Offset pagination is simple and familiar, while cursor pagination is usually more stable for large or frequently changing datasets.

The right choice depends on usage patterns. Offset is easier for "go to page 5"; cursor is better when consistency under insertion and deletion matters more than random page jumps.

## Result metadata

Paginated responses often need more than a list of items. Counts, page size, cursors, and next-page links help clients continue the workflow without guessing how the server expects traversal to work.

Without metadata, consumers end up reverse-engineering behavior from trial and error. That usually means brittle integrations.

## Backward compatibility

Once clients ship against an API, behavior becomes sticky. Renaming fields, changing defaults, or redefining semantics can break consumers even if the server still compiles and tests pass locally.

This is why compatibility is a product decision, not just a code decision. The cost of breaking a contract is often borne by teams outside the one making the change.

## Versioning strategies

Versioning is how teams introduce meaningful incompatible change without silently breaking everyone. Common approaches include path-based versioning like `/v2/orders`, header-based versioning, and media-type versioning.

Each approach has tradeoffs. Path versioning is obvious and easy to debug; header or media-type versioning keeps URLs cleaner but makes requests harder to inspect casually.

## Deprecation and additive change

The safest API evolution is usually additive: introduce optional fields or new endpoints without changing the meaning of old ones. When removal is necessary, deprecation should be explicit, documented, and scheduled.

Clients need time and guidance to migrate. A backend team that removes behavior without a transition plan pushes operational risk downstream to everyone else.
