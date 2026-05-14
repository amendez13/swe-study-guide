# Microservices and System Decomposition

How to break a system into independent, deployable pieces — and when not to. In system design interviews, you'll often draw a diagram with multiple services, but the real test is whether you can justify the boundaries and handle the distributed systems complexity that comes with decomposition.

## Key Points

- **Monolith vs. microservices** — monolith is simpler to build, deploy, and debug. Microservices offer independent scaling and team ownership. Don't default to microservices without a reason.
- **Service boundaries** — align with business domains (bounded contexts), not technical layers. Each service owns its data. If two services always deploy together, they should be one service.
- **Multi-tier architecture** — presentation, application, data tiers. Orthogonal to monolith vs. microservices — a monolith can be three-tier, a microservice can be single-tier.
- **Event-driven architecture** — services communicate through events for loose coupling, independent scaling, and fault isolation. Trade-off: eventual consistency and harder debugging.
- **Service discovery** — client-side (query a registry), server-side (LB routes), or service mesh (sidecar proxy). Kubernetes handles this automatically via Services.
- **Saga pattern** — distributed transactions via compensating actions. Orchestration (central coordinator) or choreography (event-driven). Trades ACID for eventual consistency.

## Example

Decomposing an online food delivery platform:

```text
Services:
  User Service        — profiles, addresses, preferences
  Restaurant Service  — menus, hours, ratings
  Order Service       — cart, checkout, order lifecycle
  Payment Service     — payment processing, refunds
  Delivery Service    — driver matching, tracking, ETA
  Notification Service — push, SMS, email

Why these boundaries:
  Each maps to a business domain with its own data.
  Teams: user, restaurant, order, payment, delivery, platform.
  Independent scaling: Delivery Service needs more instances
  during dinner rush; User Service load is steady.

Order saga (choreography):
  OrderCreated → Payment charges → PaymentSucceeded
  → Inventory reserves → RestaurantAccepted
  → Delivery assigns driver → DriverAssigned

  If RestaurantRejects:
    Compensate: refund payment, cancel order, notify user.

Communication:
  REST: client → API Gateway → services (user-facing)
  gRPC: service ↔ service (internal, latency-sensitive)
  Kafka: event bus for saga events and analytics
```

The design shows clear boundaries, a reason for each service, and a saga for the multi-service order flow.
