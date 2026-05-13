# Resource Modeling and Representations

Once HTTP basics are in place, the next question is what the API is actually about. Resource modeling is the work of deciding what entities deserve endpoints, how they relate to each other, and what shape their representations should take on the wire.

## Key Points

- **Resources are the main nouns** - Model things like users, orders, and invoices rather than RPC-style actions.
- **Collections and singletons differ** - `/orders` and `/orders/{id}` usually support different operations and semantics.
- **Nested resources express relationships** - Paths can show ownership or containment, but too much nesting becomes noise.
- **Domain language matters** - Use the vocabulary clients already understand.
- **Representations are contracts** - Response bodies should serve consumer needs, not mirror internal storage blindly.
- **Payload shape is a design choice** - Flat and nested structures trade readability against convenience and size.
- **Links can improve discoverability** - Responses can hint at related resources and next actions.

## Example

```python
order = {
    "id": 42,
    "status": "paid",
    "customer": {"id": 7, "name": "A. Example"},
    "links": {
        "self": "/orders/42",
        "customer": "/customers/7",
    },
}

print(order["links"]["self"])
print(order["customer"]["name"])
```

The same order could be stored internally across several tables, but the API representation is shaped for the client: it exposes the right fields and a couple of useful relationships without leaking storage details.
