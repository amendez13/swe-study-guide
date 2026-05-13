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

```python
items = [{"id": 1}, {"id": 2}, {"id": 3}, {"id": 4}]

def paginate(values: list[dict], limit: int, offset: int) -> dict:
    page = values[offset : offset + limit]
    return {
        "items": page,
        "limit": limit,
        "offset": offset,
        "next_offset": offset + limit if offset + limit < len(values) else None,
    }

print(paginate(items, limit=2, offset=0))
print(paginate(items, limit=2, offset=2))
```

Even a tiny paginator shows the core contract: bounded results plus enough metadata for the client to continue safely.
