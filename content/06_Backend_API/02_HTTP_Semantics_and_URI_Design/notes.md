# HTTP Semantics and URI Design

Backend API design starts with speaking HTTP correctly. If methods, status codes, URIs, and headers are used consistently, the rest of the stack becomes easier to reason about for clients, operators, and the engineers maintaining the service.

## Key Points

- **Requests and responses have a fixed shape** - Method, path, headers, query string, and body on the way in; status, headers, and body on the way out.
- **Methods carry meaning** - `GET` reads, `POST` creates, `PUT` replaces, `PATCH` mutates, and `DELETE` removes.
- **Status codes drive behavior** - Monitoring, retry logic, and client error handling all depend on them.
- **URIs should be stable and readable** - Name resources clearly and avoid coupling paths to implementation details.
- **Path and query parameters serve different roles** - Identity belongs in the path; filtering and shaping belong in the query string.
- **Idempotency matters operationally** - Some requests can be retried safely and some cannot.
- **Headers carry control metadata** - Auth, caching, tracing, and representation negotiation often belong there.

## Example

A typical CRUD lifecycle for an order resource, showing how methods, status codes, and headers work together:

```http
# 1. Create an order
POST /orders HTTP/1.1
Content-Type: application/json
Authorization: Bearer eyJhbGciOi...

{"customerId": 7, "items": [{"sku": "BOOK-123", "quantity": 2}]}

HTTP/1.1 201 Created
Location: /orders/42

{"id": 42, "status": "pending", "customerId": 7}

# 2. Fetch the order
GET /orders/42 HTTP/1.1
Authorization: Bearer eyJhbGciOi...

HTTP/1.1 200 OK
ETag: "v1"

{"id": 42, "status": "pending", "customerId": 7}

# 3. Update the order status
PATCH /orders/42 HTTP/1.1
Content-Type: application/json

{"status": "paid"}

HTTP/1.1 200 OK

{"id": 42, "status": "paid", "customerId": 7}

# 4. Delete the order
DELETE /orders/42 HTTP/1.1

HTTP/1.1 204 No Content
```

Each step uses a different method and returns the status code that communicates the outcome — `201` for creation, `200` for retrieval and update, `204` for deletion with no body.
