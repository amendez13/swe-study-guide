## Request and response anatomy

Every backend API request has the same core pieces: method, path, headers, optional query string, and optional body. Every response returns a status code, headers, and optionally a body describing the result.

Understanding that anatomy makes debugging concrete. Most API failures reduce to one of those pieces being wrong: the method is incorrect, the body shape is invalid, or the response status does not match what the client expects.

```http
GET /orders/42?include=items HTTP/1.1
Accept: application/json
Authorization: Bearer <token>
```

## HTTP methods communicate intent

`GET`, `POST`, `PUT`, `PATCH`, and `DELETE` are not just routing labels. They tell clients, proxies, SDKs, and observability systems whether an operation is a read, a create, a full replacement, a partial mutation, or a removal.

Using the wrong method creates confusion fast. A `POST` that really behaves like a read, or a `GET` that mutates state, breaks assumptions that tooling and humans rely on.

```http
GET    /orders/42        # fetch one order
POST   /orders           # create a new order
PUT    /orders/42        # replace the full order
PATCH  /orders/42        # update part of the order
DELETE /orders/42        # remove the order
```

## Status codes are part of the contract

Status codes are how the server classifies the outcome of a request. `2xx` means success, `4xx` means the client asked incorrectly or lacks access, and `5xx` means the server failed while handling an otherwise valid request.

Clients build behavior around these codes. Retry logic, error handling, and monitoring dashboards all depend on them, so choosing the right code is part of API design, not a last-minute detail.

```text
Code  Meaning             When to use
────  ──────────────────  ──────────────────────────────────────────
200   OK                  Successful GET, PUT, PATCH
201   Created             Successful POST that creates a resource
204   No Content          Successful DELETE or action with no body
400   Bad Request         Malformed syntax, missing required field
401   Unauthorized        No credentials or expired token
403   Forbidden           Valid identity, insufficient permission
404   Not Found           Resource does not exist
409   Conflict            Duplicate key, state conflict
422   Unprocessable       Valid syntax but semantically invalid
429   Too Many Requests   Rate limit exceeded
500   Internal Error      Unhandled server failure
503   Service Unavailable Overloaded or in maintenance
```

## Stable and readable URIs

A good URI names a resource clearly and remains durable over time. Paths like `/users/42/orders` tell a reader what they are looking at without exposing internal storage details.

Consistency matters as much as cleverness. Teams should choose conventions for pluralization, separators, and nesting depth and apply them everywhere so clients can predict endpoint shapes.

```text
Good: /customers/7/invoices
Good: /invoice-items/42
Avoid: /getCustomerInvoicesById
Avoid: /tbl_invoice_rows_v2
```

## Path parameters vs. query parameters

Path parameters identify the primary resource being addressed, while query parameters shape or narrow the result. `/orders/42` identifies one order; `/orders?status=paid&limit=20` filters a collection.

Mixing those roles creates unclear APIs. If identity and filtering are not separated cleanly, clients have to memorize endpoint quirks instead of following a stable mental model.

```http
GET /orders/42
GET /orders?status=paid&sort=-created_at&limit=20
```

## Idempotency and safe retries

An operation is idempotent when repeating the same request leads to the same final state. `PUT` and `DELETE` are designed with this property in mind, which makes retries safer under network uncertainty.

This matters in production more than in tutorials. Load balancers, timeouts, and client retry middleware all assume some methods can be repeated safely and others cannot.

```text
Method   Safe?   Idempotent?   Retry-safe?   Typical use
──────   ─────   ───────────   ───────────   ──────────────────
GET      Yes     Yes           Yes           Read a resource
HEAD     Yes     Yes           Yes           Check existence
PUT      No      Yes           Yes           Replace a resource
DELETE   No      Yes           Yes           Remove a resource
POST     No      No            No*           Create a resource
PATCH    No      No            No*           Partial update

* POST and PATCH can be made retry-safe with an idempotency key:
  POST /orders  +  Idempotency-Key: abc-123
  Server checks the key → if already processed, returns stored result.
```

## Headers as control information

Headers carry metadata that shapes how requests are processed without changing the resource body itself. Authentication, content negotiation, caching directives, correlation IDs, and version hints often belong in headers.

This separation keeps resource representations cleaner. It also lets infrastructure like proxies and gateways participate in authentication, caching, or tracing using standard HTTP fields.

```http
Authorization: Bearer <token>
If-None-Match: "orders-v17"
X-Request-ID: 8e5d3f0a
Accept: application/json
```
