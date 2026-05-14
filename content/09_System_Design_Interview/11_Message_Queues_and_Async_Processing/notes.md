# Message Queues and Asynchronous Processing

The mechanism for decoupling components in a distributed system. Message queues absorb traffic spikes, enable async processing, and isolate failures so a slow consumer doesn't block the producer. In system design interviews, they appear whenever you need to move work off the request path.

## Key Points

- **Message queue** — buffer between producer and consumer. Enables decoupling, load leveling, fault isolation, and async work.
- **Point-to-point vs. pub/sub** — point-to-point delivers each message to one consumer (task dispatch). Pub/sub delivers to all subscribers (event broadcasting). Kafka supports both via consumer groups.
- **Delivery guarantees** — at-most-once (lossy), at-least-once (may duplicate), exactly-once (hardest). Default to at-least-once with idempotent consumers.
- **Consumer groups** — multiple consumers sharing partitions for parallel processing within a group, while multiple groups each get all messages.
- **Backpressure** — handle overload by buffering, dropping, throttling producers, or auto-scaling consumers. Always have a plan for when the consumer falls behind.
- **Dead letter queue** — failed messages go to a separate queue for investigation. Prevents one bad message from blocking the pipeline.

## Example

Designing the order processing pipeline for an e-commerce system:

```text
User places order → API returns 201 immediately.
Order details are sent to a Kafka topic: "orders".

Consumer Group 1: Order Processor
  Validates inventory, reserves stock, writes to orders DB.
  If processing fails 3× → message goes to orders-dlq.

Consumer Group 2: Notification Service
  Sends confirmation email and push notification.
  At-most-once is acceptable (user can check order status manually).

Consumer Group 3: Analytics Pipeline
  Streams order events to the data warehouse.
  At-least-once, deduplicated on order_id.

Backpressure:
  During Black Friday, order volume spikes 20×.
  Kafka buffers messages (persistent log).
  Auto-scaler adds Order Processor consumers based on
  consumer lag metric. Orders process within 30s even at peak.

DLQ monitoring:
  Alert if orders-dlq depth > 0 for more than 5 minutes.
  On-call engineer investigates failed orders.
```

The user gets a fast 201 response. All the slow work (inventory check, email, analytics) happens asynchronously through the queue.
