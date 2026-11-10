# Real-Time and Notification Systems

Northwick Allotments notifies plot holders about tap turns, frost, tools, and the Saturday seed list. A notice has a channel, a stored address, a preference gate, and a product budget before it reaches a provider. Presence decides who is in the app. Fan-out decides whether a recipient list is written ahead or pulled on open. The transports, the broker, the provider adapter, the retry wait, the limiter counter, the shed-polygon test, and the chat and news-feed products stay in the topics that own them.

## Key Points

- **Push Notification System** — APNs, FCM, an SMS provider, or an email provider keeps the last hop. Promotional push stops at 2 per member each week. Transactional push stops at 20 per member each day. The counter is the Rate Limiter. The provider credential stays in a server-side adapter.
- **Device Tokens** — a provider token, a shed phone number, and a membership email, one row per install. A refresh replaces that install's row. An unregistered token is deleted, and the other handset stays.
- **Notification Preferences** — a switch per channel and per type. Seed-list is promotional. The gate runs before render and before the queue, and a closed switch leaves no message behind. The product budgets still apply to a notice the switches allow.
- **Notification Service Architecture** — the service gates, fills one template, and queues one message per channel that passed. Workers call the providers. Status is queued, provider-accepted, or opened. Queue depth is Backpressure. A chart of that depth is Metrics Monitoring System.
- **Presence** — a beat every 20 seconds refreshes a key that lives 50. A socket drop waits 12 seconds. A reconnect at 8 seconds tells nobody. Logout is offline immediately. Only online shed partners hear a change that sticks.
- **Fan-Out Strategies** — 6 recipients is a write, 18,000 is a read, and 900 is a hybrid that writes the stewards and lets the rest pull. Ranking and a feed cache stay on News Feed / Timeline.
- **In-App or Push** — an open tap board uses the connection already held. An absent member with a token gets a platform push. The seed list goes by email. Frost with no token goes by SMS. Polls, sockets, and the shed-polygon test stay in their own topics.
- **Delivery Guarantees for Notifications** — the worker retries until the provider accepts, and a lost accept can deliver the same id twice. The handset shows each id once. A per-plot sequence orders the screen. A pile past 3 becomes one summary. The broker promise is at-least-once.

## Example

Member 14's frost warning has a device token. The same frost with no token would be a text. A promotional push already sent twice this week is over the weekly budget, and the third transactional push of the day is inside the daily budget. The west tap, a tool recall, and a pump alert pick three fan-out shapes. Nine waiting tap rows collapse. The id `n-18` arrives twice.

```python
PROMO_CAP = 2
TX_CAP = 20
WRITE_MAX = 500
READ_MIN = 5000
EACH_MAX = 3


def channel(kind: str, has_token: bool) -> str:
    if kind == "seed-list":
        return "email"
    if has_token:
        return "push"
    return "sms"


def allow(sent: int, cap: int) -> bool:
    return sent < cap


def pick(recipients: int) -> str:
    if recipients <= WRITE_MAX:
        return "write"
    if recipients >= READ_MIN:
        return "read"
    return "hybrid"


def plan(waiting: int) -> str:
    if waiting > EACH_MAX:
        return "summary"
    return "each"


def shown(ids: tuple[str, ...]) -> int:
    return len(set(ids))


print(
    channel("frost", True),
    channel("frost", False),
    allow(2, PROMO_CAP),
    allow(3, TX_CAP),
    pick(6),
    pick(900),
    pick(18000),
    plan(9),
    shown(("n-18", "n-18", "n-19")),
)
# push sms False True write hybrid read summary 2
```

The frost with a token is a platform push. The frost without one is SMS, and an SMS switch that is off stops that text before a template or a queue write. Two promotional pushes spend the week, so a third seed-list push stops, while the third tap push of the day still fits under 20. Six neighbors are written a row each. The 900-member recall writes the on-duty stewards and stores one notice for the others. The pump alert is stored once. Nine missed tap rows leave as a single summary. The second `n-18` is the same notice, and the handset shows two ids. The shed token is deleted when the provider calls it unregistered. The pocket token stays.

## See also

- [Networking and Communication](../10_Networking_and_Communication/) — Polling and Long-Polling, and WebSockets and SSE. The transports stay there. The choice of an in-app connection, a platform push, or email stays here.
- [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/) — Message Queue, When to Queue, Message Delivery Guarantees, Backpressure, and Dead Letter Queue. The broker promise is at-least-once. The notice id on the handset stays here.
- [Microservices and System Decomposition](../12_Microservices_and_System_Decomposition/) — Third-Party Integration. The provider adapter and its credential stay there.
- [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/) — Timeouts and Retries. The wait between provider tries stays there.
- [Rate Limiting and Throttling](../17_Rate_Limiting_and_Throttling/) — the Rate Limiter. The counter shape stays there. The promotional and transactional budgets stay here.
- [Geospatial and Location-Based Services](../20_Geospatial_and_Location_Based_Services/) — Geofencing. The shed-polygon test stays there. The notice after it fires stays here.
- [Classic Design Problems](../24_Classic_Design_Problems/) — Chat System, News Feed / Timeline, and Metrics Monitoring System. The chat product, feed ranking, a feed cache, and a metrics chart stay there. Presence and the fan-out pattern stay here.
