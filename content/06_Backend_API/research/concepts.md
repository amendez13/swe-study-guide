# Backend API Design and Implementation Concepts

A distilled concept reference for a student of backend API design and implementation, synthesized from the five course outlines in [course_outlines.md](course_outlines.md). The focus is on durable API and backend engineering knowledge rather than course-specific projects, setup steps, or framework branding.

---

## 1. API-First Thinking

- **API as a product surface** - An API is not just glue code for a frontend; it is a long-lived contract other software will depend on, so clarity and stability matter from the first version.
- **Design-first vs. code-first** - Design-first starts from the contract and documentation before implementation, while code-first derives the contract from working code. Each affects team coordination, reviewability, and drift risk.
- **Consumer-centered design** - Good APIs are shaped around the jobs clients need to do, not around internal database tables or ORM models.
- **Public, private, and partner APIs** - The intended audience changes the bar for ergonomics, security, governance, and backward compatibility.

## 2. HTTP as the Transport Contract

- **Request/response model** - Backend APIs are built around clients sending requests and servers returning status, headers, and bodies in a predictable shape.
- **HTTP methods** - `GET`, `POST`, `PUT`, `PATCH`, and `DELETE` are not arbitrary verbs; they communicate intent and influence caching, retries, and client expectations.
- **Status codes** - Codes like `200`, `201`, `204`, `400`, `401`, `403`, `404`, `409`, `422`, and `500` are part of the API contract, not incidental metadata.
- **Headers as control data** - Headers carry authentication, content negotiation, caching, correlation IDs, and versioning information without polluting resource bodies.

## 3. Resource Modeling

- **Resources vs. actions** - REST works best when URLs name resources and relationships, while operations are expressed through HTTP methods rather than verb-heavy endpoint names.
- **Collections and singletons** - `/users` and `/users/{id}` express different shapes of access and should have distinct semantics for listing, creation, and retrieval.
- **Sub-resources and associations** - Nested paths such as `/users/{id}/orders` express ownership or containment and should reflect domain relationships clearly.
- **Domain language** - Resource names should match the business vocabulary developers and consumers already use, reducing translation overhead.

## 4. URI Design

- **Stable identifiers** - Resource identifiers should be durable and opaque enough that clients are not coupled to storage details.
- **Naming conventions** - Consistent casing, pluralization, and path structure make an API easier to scan and harder to misuse.
- **Path vs. query parameters** - Put identity in the path and optional shaping concerns like filtering, sorting, and pagination in the query string.
- **Discoverability** - Good URI design helps clients predict adjacent endpoints instead of memorizing arbitrary route shapes.

## 5. Method Semantics and Idempotency

- **Idempotency** - `GET`, `PUT`, and `DELETE` should be safe to retry without changing the end result, which matters under network failure and load balancers.
- **Create vs. replace vs. mutate** - `POST` usually creates, `PUT` replaces, and `PATCH` partially changes; collapsing them makes client behavior harder to reason about.
- **Safe methods** - `GET` and `HEAD` should not trigger hidden state changes just because they are easy to wire into handlers.
- **Operational correctness** - Method choice influences generated SDKs, caches, monitoring dashboards, and client retry middleware.

## 6. Representations and Media

- **Resource representation** - The body returned by an API is a representation of server state, not necessarily a raw dump of database columns.
- **JSON as the default wire format** - Most modern backend APIs use JSON because it is widely supported, human-readable, and easy to validate.
- **Schema shape matters** - Flat, nested, and embedded structures have tradeoffs for readability, versioning, and payload size.
- **Hypermedia and links** - HATEOAS-style links can make workflows more discoverable by exposing allowed next steps in responses.

## 7. Request Validation and Parsing

- **Input validation** - APIs should reject malformed or incomplete requests early, with clear field-level errors rather than vague failures deeper in the stack.
- **Type coercion and strictness** - Frameworks often coerce types for convenience, but teams need to know when coercion helps and when it hides client bugs.
- **Body, path, query, header, and cookie inputs** - Each source of input has different semantics and should be validated with the same rigor.
- **Declarative schemas** - Validation models in tools like Pydantic or framework-specific request DTOs make the API contract explicit and testable.

## 8. Response Design and Error Contracts

- **Consistent success shapes** - Similar endpoints should return similarly shaped payloads so clients do not have to special-case equivalent operations.
- **Problem-focused error responses** - Error payloads should say what failed, where it failed, and what the client can do next.
- **Framework exceptions vs. domain errors** - Translate internal failures into stable HTTP-level error contracts instead of leaking stack-specific details.
- **No-content responses** - `204 No Content` is useful when a successful operation does not need to return a representation.

## 9. Filtering, Sorting, and Pagination

- **Filtering semantics** - Query parameters for narrowing result sets should be predictable and composable.
- **Sorting semantics** - Sorting rules should be explicit about field names, default order, and how ties are handled.
- **Pagination** - Offset or cursor pagination prevents unbounded list responses and defines how clients traverse large collections.
- **Result metadata** - Counts, cursors, and page links help clients navigate large datasets without guessing.

## 10. Versioning and Evolution

- **Backward compatibility** - The most expensive API mistake is breaking consumers who already shipped against your contract.
- **Versioning strategies** - Path-based, header-based, and media-type-based versioning each trade clarity against flexibility.
- **Deprecation policy** - Old behavior should be deprecated deliberately, announced clearly, and removed on a schedule consumers can act on.
- **Additive change bias** - Adding optional fields is safer than renaming or reinterpreting existing ones.

## 11. Documentation and OpenAPI

- **OpenAPI as machine-readable contract** - OpenAPI turns an API definition into something tooling can validate, render, diff, and generate against.
- **Human-readable docs** - Swagger UI, ReDoc, and similar tools help consumers explore endpoints, payloads, and authentication interactively.
- **Examples matter** - Example requests and responses shorten the path from reading docs to making a correct call.
- **Generated artifacts** - Server stubs, client SDKs, and test scaffolds can come from the API contract when the specification is kept accurate.

## 12. Layering and Code Organization

- **Transport vs. business logic** - Route handlers or controllers should translate HTTP concerns, not absorb all domain logic.
- **Service layer** - A service layer is useful when use-case logic needs to be reused across endpoints or orchestration paths.
- **Repository or data-access layer** - Separating persistence details from request handling keeps storage decisions from leaking across the application.
- **Modular routing** - Organizing routes by domain or feature reduces file sprawl and makes ownership clearer as the API grows.

## 13. Authentication

- **Authentication answers identity** - Authentication establishes who the caller is before any authorization rules can be applied.
- **Session vs. token approaches** - Cookie-backed sessions and bearer-token APIs solve different deployment and client-integration problems.
- **JWT basics** - JWTs carry signed claims and are common for stateless APIs, but they still need careful expiration and revocation strategy.
- **Credential handling** - Password storage always means hashing, never plaintext, and login flows need rate limiting and auditability.

## 14. Authorization

- **Authorization answers permission** - After identifying a caller, the backend must decide which resources and actions that caller may access.
- **Role-based access control** - Roles are a common first step, but they can become too coarse when domain rules get specific.
- **Ownership checks** - Many APIs need object-level authorization, not just broad admin/non-admin distinctions.
- **Defense in depth** - Authorization should not rely only on UI behavior; every protected backend path must enforce it server-side.

## 15. Middleware and Cross-Cutting Concerns

- **Middleware pipelines** - Middleware lets teams apply logic before and after request handling without duplicating it in every endpoint.
- **Cross-cutting concerns** - Logging, request IDs, CORS, auth extraction, compression, and timing belong in shared layers when possible.
- **Request context propagation** - Correlation IDs and per-request metadata make tracing and debugging distributed systems feasible.
- **Framework-specific hooks** - Express middleware, FastAPI dependencies, and Spring filters solve similar problems with different idioms.

## 16. Persistence and Data Modeling

- **API model vs. database model** - The shape of a table or document store record should not dictate the public API automatically.
- **Relational and document tradeoffs** - SQL and NoSQL systems shape how you model aggregates, joins, validation, and query flexibility.
- **Relationships** - One-to-many and many-to-many relationships show up in both storage design and endpoint structure.
- **Migrations and schema evolution** - Database change needs versioned migration workflows so code and schema move together safely.

## 17. Async, Concurrency, and Background Work

- **Synchronous vs. asynchronous execution** - Async helps when requests spend time waiting on I/O, but it does not make CPU work free.
- **Event loops and thread pools** - Backend engineers need a mental model for how their framework handles concurrent requests under load.
- **Background jobs** - Email sending, file processing, and other delayed work often should not block the main request path.
- **Lifespan and startup concerns** - Connection pools, configuration caches, and shared clients need explicit initialization and cleanup.

## 18. Real-Time Communication

- **WebSockets** - Some backend workloads need bidirectional communication rather than request/response polling.
- **Streaming updates** - Resource monitors, chats, and live dashboards depend on pushing data as it changes.
- **Transport choice** - Real-time features should be chosen because the use case demands them, not because they seem more advanced than REST.
- **State and fanout** - Real-time systems force decisions about client sessions, broadcast behavior, and backpressure.

## 19. Caching and Performance

- **HTTP caching** - `Cache-Control`, `ETag`, and `Last-Modified` can reduce unnecessary work and improve perceived latency.
- **Server-side caching** - Expensive reads may need in-memory or distributed caches, but cache invalidation becomes part of the design.
- **Payload discipline** - Oversized responses, unnecessary nesting, and overfetching all become performance problems under scale.
- **Rate limiting** - Rate limits protect the system from abuse and shape consumer expectations about safe usage.

## 20. Security Hardening

- **Input sanitization** - Validation and sanitization protect both the application and downstream systems from malformed or malicious input.
- **CORS and cross-domain security** - Browser-facing APIs need explicit cross-origin policy rather than accidental openness.
- **Secret management** - API keys, signing secrets, and database credentials belong in environment or secret stores, not code.
- **Least privilege** - Service accounts, database users, and background workers should have only the permissions they need.

## 21. Testing Strategy

- **Unit tests** - Unit tests isolate small pieces of logic and help keep validation, mapping, and domain rules correct.
- **Integration tests** - Integration tests prove that routes, validation, persistence, and auth work together as a system.
- **Contract testing** - API tests should verify not just behavior but the published shape of requests and responses.
- **Dependency overrides and fakes** - Swapping real services for controlled test doubles keeps API tests deterministic and fast.

## 22. Deployment and Operations

- **Environment-specific configuration** - Development, test, staging, and production should differ by configuration, not by ad hoc code edits.
- **Observability** - Logs, metrics, traces, and health checks are part of operating an API, not optional afterthoughts.
- **CI/CD for APIs** - Automated linting, tests, contract checks, migrations, and deployment steps reduce release risk.
- **Production readiness** - Error tracking, rollout strategy, rollback paths, and smoke checks distinguish a toy API from an operable one.

---

## How to use this list

This is a self-check, not a buzzword index. For any concept here, ask:

1. Can I explain what it is and when it matters?
2. Can I recognize it in an unfamiliar backend codebase or API spec?
3. Can I implement a small, correct example of it myself?

If the answer is "no" to any of those, that concept belongs in your next study block.
