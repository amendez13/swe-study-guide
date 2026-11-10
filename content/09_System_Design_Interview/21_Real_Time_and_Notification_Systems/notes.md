# Real-Time and Notification Systems

A ride-hailing or food-delivery app tells a person that a driver is outside, that an order is at the door, or that a weekly deals mail is waiting. Slack-style chat uses the same ideas to show who is active. A notice has a channel, a stored address, a preference gate, and a product budget before it reaches a provider. Presence decides who is in the app. Fan-out decides whether a recipient list is written ahead or pulled on open. The socket, the broker, the provider credential, the retry wait, the limiter counter, the pickup-polygon test, and the chat and news-feed products stay in the topics that own them.

## Key Points

- **Push Notification System** — APNs, FCM, an SMS provider, or an email provider keeps the last hop. A provider's HTTP success means it accepted the message. This product stops promotional push at 2 per rider each week and transactional push at 20 per rider each day. The counter is the Rate Limiter. The APNs credential and the FCM service account stay in a server-side adapter.
- **Device Tokens** — one rider has many rows: a push token per install, plus a phone number and an email address. A refresh replaces that install's row. An unregistered token (APNs HTTP 410, or FCM `UNREGISTERED`) deletes that row, and the other install stays.
- **Notification Preferences** — a switch per channel and per type. Deals are promotional. The gate runs before render and before the queue, and a closed switch leaves no message behind. A notice the switches allow still has to fit the product budgets.
- **Notification Service Architecture** — the service gates, fills one template, and queues one message per channel that passed. One worker per channel calls the provider. The caller returns when the event is queued. Status is queued, provider-accepted, or opened when the app reports a tap. Queue depth is Backpressure. A chart of that depth is Metrics Monitoring System.
- **Presence** — a beat every 20 seconds refreshes a key that lives 50. A 20-second gap stays online. Fifty seconds from the last beat is offline; a last beat at 40 seconds expires at 90. A socket drop waits 12 seconds. A reconnect at 8 seconds tells nobody. Logout is offline immediately. Only subscribers who are online hear a change that sticks.
- **Fan-Out Strategies** — 6 recipients is a write, 18,000 is a read, and 900 is a hybrid that writes the on-duty dispatchers and lets the rest pull. The write line is 500 and the read line is 5,000. Ranking and a feed cache stay on News Feed.
- **In-App or Push** — an open trip screen uses the connection already held. An absent rider with a token gets a platform push. Weekly deals go by email, including while the rider is online. An urgent alert with no token goes by SMS when SMS is allowed. Polls, sockets, and the pickup-polygon test stay in their own topics.
- **Delivery Guarantees for Notifications** — the worker retries until the provider accepts, and a lost accept can deliver the same id twice. The phone shows each id once and orders one trip by sequence. A pile past 3 becomes one summary. The broker promise is at-least-once.

## Example

A driver-arrived alert with a device token is a platform push. The same alert with no token is a text. A promotional push already sent twice this week is over the weekly budget, and the third transactional push of the day is inside the daily budget. A six-person trip chat, a 900-driver safety notice, and an 18,000-rider city outage pick three fan-out shapes. Nine waiting trip rows collapse. The id `n-18` arrives twice.

```python
PROMO_CAP = 2
TX_CAP = 20
WRITE_MAX = 500
READ_MIN = 5000
EACH_MAX = 3


def channel(kind: str, has_token: bool) -> str:
    if kind == "deals":
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
    channel("arrived", True),
    channel("arrived", False),
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

The arrival with a token is a platform push. The arrival without one is SMS, and an SMS switch that is off stops that text before a template or a queue write. Two promotional pushes spend the week, so a third deals push stops, while the third trip push of the day still fits under 20. Six people in the trip chat each get a row. The 900-driver safety notice writes the on-duty dispatchers and stores one notice for the others. The city outage is stored once. Nine missed trip rows leave as a single summary that names the count and the latest update. The second `n-18` is the same notice, and the phone shows two ids. The phone's token is deleted when the provider calls it unregistered. The tablet's token stays.

## See also

- [Networking and Communication](../10_Networking_and_Communication/) — Polling and Long-Polling, and WebSockets and SSE, own the connection. The choice of an in-app connection, a platform push, or email stays here.
- [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/) — Message Queue, When to Queue, Message Delivery Guarantees, Backpressure, and Dead Letter Queue own the broker. The broker promise is at-least-once. The notice id on the phone stays here.
- [Microservices and System Decomposition](../12_Microservices_and_System_Decomposition/) — Third-Party Integration owns the provider adapter and its credential.
- [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/) — Timeouts and Retries own the wait between provider tries.
- [Rate Limiting and Throttling](../17_Rate_Limiting_and_Throttling/) — the Rate Limiter owns the counter. The promotional and transactional budgets stay here.
- [Geospatial and Location-Based Services](../20_Geospatial_and_Location_Based_Services/) — Geofencing owns the pickup-polygon test. The notice after it fires stays here.
- [Classic Design Problems](../24_Classic_Design_Problems/) — Chat System, News Feed, and Metrics Monitoring System own the chat product, feed ranking, a feed cache, and a metrics chart. Presence and the fan-out pattern stay here.
