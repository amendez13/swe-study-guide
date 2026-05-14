# Resource Modeling and Representations

Once HTTP basics are in place, the next question is what the API is actually about. Resource modeling is the work of deciding what entities deserve endpoints, how they relate to each other, and what shape their representations should take on the wire.

## Key Points

- **Resources are the main nouns** - Model things like users, orders, and invoices rather than RPC-style actions.
- **Collections and singletons differ** - `/orders` and `/orders/{id}` usually support different operations and semantics.
- **Nested resources express relationships** - Paths can show ownership or containment, but too much nesting becomes noise.
- **Domain language matters** - Use the vocabulary clients already understand.
- **Representations are contracts** - Response bodies should serve consumer needs, not mirror internal storage blindly.
- **Payload shape is a design choice** - Flat, nested, embedded, and linked structures each serve different consumer needs.
- **Hypermedia links improve discoverability** - Responses can hint at related resources and available actions, and those actions can change with resource state.

## Example

The same order, stored across two database tables but represented as one cohesive resource for the API consumer:

```text
Database tables:
  orders    → id=42, customer_id=7, status='paid', internal_batch_id=98
  customers → id=7, name='A. Example', tax_code='US-CA-2024'

API response (GET /orders/42):
  {
    "id": 42,
    "status": "paid",
    "customer": {
      "id": 7,
      "name": "A. Example"
    },
    "items": [
      {"sku": "BOOK-123", "quantity": 2, "unitPrice": 15.00}
    ],
    "links": {
      "self": "/orders/42",
      "customer": "/customers/7",
      "refund": "/orders/42/refunds"
    }
  }
```

Notice what the representation includes (nested customer, hypermedia links, line items) and what it deliberately omits (internal_batch_id, tax_code). The API is shaped for the consumer's workflow, not the database's storage model.
