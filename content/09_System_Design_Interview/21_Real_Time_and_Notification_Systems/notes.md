# Real-Time and Notification Systems

How to deliver timely updates to users across mobile, web, and email channels. This topic combines push notifications, real-time communication patterns, and the fan-out trade-off that drives architecture decisions for feeds, chat, and live updates.

## Key Points

- **Push notification system** — delegates to APNs/FCM/Web Push. Store device tokens per user, respect preferences, retry with backoff, remove invalid tokens.
- **Notification service** — centralized dispatcher across channels. Async via message queue. Template engine + user preferences + delivery tracking.
- **Presence / online status** — heartbeat-based (TTL in Redis) or connection-based (WebSocket state). Handle flapping connections with a grace period.
- **Fan-out** — on write (push, fast reads, expensive for celebrities) vs. on read (pull, fast writes, slow reads). Hybrid: push for normal users, pull for celebrities.
- **Real-time delivery** — WebSockets for chat, SSE for server-push, push notifications for offline, polling as fallback.
- **Delivery guarantees** — at-least-once with dedup on client, ordered delivery via sequence numbers, offline queueing with summarization.

## Example

Designing notifications for a food delivery app:

```text
Notification types:
  "Your order has been confirmed"     → push + in-app
  "Driver is 5 minutes away"          → push + in-app
  "Your order has been delivered"      → push + email
  "Rate your experience"              → push (delayed 30 min)
  "Weekly deals near you"             → email only

Architecture:
  Order events → Kafka → Notification Service
  NS checks user preferences (push: on, email: on, SMS: off)
  NS renders template: "Hi Alex, your pad thai is 5 min away!"
  NS sends to push queue and email queue (separate workers)

  Push worker → FCM/APNs → user's phone
  Email worker → SES → user's inbox

Real-time tracking:
  Driver location → WebSocket → rider's app (2s updates)
  When driver enters 500m geofence → trigger "almost there" push.

Offline handling:
  If push delivery fails (device offline), FCM queues it.
  On app open, pull any missed notifications from server.
  Summarize: "You missed 3 updates on your order."

Rate limiting:
  Max 10 push notifications per hour per user.
  Promotional notifications: max 2 per week.
  Transactional (order updates): no limit.
```
