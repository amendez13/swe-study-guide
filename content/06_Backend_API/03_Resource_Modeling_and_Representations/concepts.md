## Resources vs. actions

REST-style APIs organize the surface around resources such as users, orders, or invoices. The operation is expressed by the HTTP method, so the path can stay noun-focused instead of turning into verb-heavy RPC endpoints.

This discipline makes the API easier to scan and easier for generic tooling to reason about. A reader can infer a lot from `GET /orders/42` without needing framework-specific context.

```http
GET /orders/42
POST /orders

# Less RESTful
POST /getOrder
POST /createOrder
```

## Collections and single resources

A collection endpoint like `/orders` represents a group of resources and usually supports listing and creation. A singleton endpoint like `/orders/{id}` represents one resource instance and usually supports retrieval, replacement, mutation, or deletion.

Keeping those responsibilities separate produces cleaner semantics. It prevents one endpoint from becoming a grab bag that handles unrelated behaviors through ad hoc parameters.

Example:

- `GET /orders` returns a list
- `POST /orders` creates one
- `GET /orders/42` returns one specific order

## Sub-resources and associations

Some resources are naturally modeled beneath others, such as `/users/{id}/orders` or `/projects/{id}/members`. This expresses relationships and access patterns directly in the URI structure.

Nested resources should still be chosen carefully. Over-nesting can produce unreadable paths and can accidentally encode implementation detail instead of real domain relationships.

```http
GET /customers/7/orders
POST /projects/12/members
```

## Domain language and naming

Resource names should use the vocabulary the business and the client already understand. If the system talks about subscriptions and invoices, the API should too, rather than exposing internal names like `billing_record_v2`.

This is one of the fastest ways to make an API feel coherent. Good names reduce the amount of translation every consumer has to do in their head.

Example: a SaaS billing API should probably expose `/subscriptions` and `/invoices`, not `/billing_entities`.

## Resource representations

The JSON body a client sees is a representation of server state, not a raw database dump. It should contain the fields the client needs, in a shape that makes sense for the task, even if the internal storage model looks different.

That separation protects the contract from internal refactors. You can change table structure or service boundaries without forcing every client to change with you.

```json
{
  "id": 42,
  "status": "paid",
  "customer": {"id": 7, "name": "A. Example"}
}
```

## JSON structure and payload shape

Representation shape matters. Flat payloads are easy to consume, while nested payloads can better express relationships and reduce repeated requests when designed carefully.

Poor payload design shows up as overfetching, underfetching, or confusing field names. A useful API response exposes the right amount of information for the use case without leaking internals.

```text
Flat — simple to consume, easy to map to table rows:
  {"id": 42, "customerName": "A. Example", "customerEmail": "a@example.com"}

Nested — preserves relationships, avoids field-name collisions:
  {"id": 42, "customer": {"name": "A. Example", "email": "a@example.com"}}

Embedded list — natural for aggregates:
  {"id": 42, "items": [{"sku": "BOOK-123", "qty": 2}]}

Linked — keeps payloads small, client fetches related data separately:
  {"id": 42, "customerId": 7, "links": {"customer": "/customers/7"}}
```

## Hypermedia links and discoverability (HATEOAS)

HATEOAS (Hypermedia As The Engine Of Application State) is the idea that responses include links telling clients what they can do next, rather than forcing them to hardcode every workflow from documentation alone.

In practice, most modern APIs use HATEOAS lightly. A response might include `self`, `next`, or action links so the client can follow the workflow the server exposes. The key benefit is that available actions change with resource state — a shipped order offers `track` but not `cancel`.

```json
{
  "id": 42,
  "status": "paid",
  "links": {
    "self": "/orders/42",
    "cancel": "/orders/42/cancel",
    "customer": "/customers/7"
  }
}
```

```json
{
  "id": 42,
  "status": "shipped",
  "links": {
    "self": "/orders/42",
    "track": "/orders/42/tracking",
    "customer": "/customers/7"
  }
}
```
