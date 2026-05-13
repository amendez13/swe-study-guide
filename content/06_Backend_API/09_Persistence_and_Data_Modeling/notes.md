# Persistence and Data Modeling

Backend APIs are shaped as much by storage choices as by HTTP choices. This topic focuses on how persistence models influence contracts, performance, and the internal boundaries that keep database concerns from leaking across the whole codebase.

## Key Points

- **Public models and storage models differ** - The API contract should not be a raw mirror of the database.
- **Relational and document stores trade off differently** - Storage shape affects endpoint behavior and query flexibility.
- **Relationships need deliberate modeling** - Aggregates, embedding, and linking all change client workflows.
- **Repositories keep storage code localized** - Queries and transaction logic belong in a dedicated layer.
- **Migrations make schema change repeatable** - They keep code and database evolution aligned.
- **Transaction boundaries define consistency** - Multi-step workflows need a clear story about atomicity.

## Example

```python
db_row = {"order_id": 42, "customer_id": 7, "customer_name": "A. Example"}

api_response = {
    "id": db_row["order_id"],
    "customer": {"id": db_row["customer_id"], "name": db_row["customer_name"]},
}

print(api_response)
```

The database row and the API representation describe the same business entity, but they serve different audiences and should not be assumed to have the same shape.
