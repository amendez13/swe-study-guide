# Querying, Pagination, and API Evolution

Collection endpoints and long-lived APIs fail in slow, expensive ways when filtering is inconsistent or changes are introduced carelessly. This topic covers how to shape list endpoints well and how to evolve them without surprising clients.

## Key Points

- **Filtering should be predictable** - Similar collection endpoints should use similar filter patterns.
- **Sorting is contract-level behavior** - Stable ordering matters especially when pagination is involved.
- **Pagination keeps responses bounded** - Offset is simple; cursor pagination is often more robust under change.
- **Metadata helps clients continue** - Counts, cursors, and next links remove guesswork.
- **Backward compatibility is expensive to break** - Changes that seem small on the server can break real clients.
- **Versioning is a deliberate strategy** - Path, header, and media-type approaches all trade clarity against flexibility.
- **Prefer additive change** - Deprecate before removing or redefining existing behavior.

## Example

A collection endpoint that supports filtering, sorting, and cursor pagination — the full query pattern in one request:

```http
GET /orders?status=paid&sort=-created_at&limit=3&cursor=eyJpZCI6MTAwfQ HTTP/1.1
Authorization: Bearer <token>

HTTP/1.1 200 OK
{
  "items": [
    {"id": 99, "status": "paid", "created_at": "2026-05-12T10:00:00Z"},
    {"id": 97, "status": "paid", "created_at": "2026-05-11T14:30:00Z"},
    {"id": 95, "status": "paid", "created_at": "2026-05-10T09:15:00Z"}
  ],
  "pagination": {
    "limit": 3,
    "next_cursor": "eyJpZCI6OTV9",
    "has_more": true
  }
}
```

The client filters by `status`, sorts by `created_at` descending, requests 3 items after the cursor, and gets back the page plus metadata to fetch the next one. Each concern — filtering, sorting, pagination — is a separate query parameter with predictable behavior.
