## Push Notification System

Northwick Allotments tells a plot holder that the west tap is free, that frost is forecast, or that Saturday's seed list is posted. The desk does not hold a connection to the handset. An iOS notice goes to Apple Push Notification service (APNs). An Android notice goes to Firebase Cloud Messaging (FCM). A text goes to an SMS provider. A letter goes to an email provider. The provider keeps the last hop, and the desk's job ends when that provider accepts the notice.

Two product budgets sit on push, counted apart. A promotional push, the seed list or the plant sale, stops at 2 per member in a week. A transactional push, a tap turn, a frost warning, or a tool due back, stops at 20 per member in a day, so a flapping moisture sensor cannot page the afternoon away. The third seed-list push of the week is dropped. A frost warning in that same hour still sends, until the day count reaches 20. The window and the counter that enforce those numbers are the Rate Limiter in [Rate Limiting and Throttling](../17_Rate_Limiting_and_Throttling/). This card names the budgets. The provider credential the allotments were issued lives in one server-side adapter, and the handset never receives it. That adapter is Third-Party Integration in [Microservices and System Decomposition](../12_Microservices_and_System_Decomposition/). A provider that asks the desk to slow down waits on Timeouts and Retries in [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/). A token the provider calls unregistered is removed on Device Tokens.

```text
iOS            APNs
Android        FCM
text           an SMS provider
letter         an email provider
promo push     2 per member each week
transactional  20 per member each day
counter        Rate Limiter
credential     Third-Party Integration
slow provider  Timeouts and Retries
dead token     Device Tokens
```

## Device Tokens

Member 14 allows alerts on two installs. APNs or FCM returns a token for that install, and the app sends the token to the desk. The SMS row is the number they wrote at the shed. The email row is the address on the membership record. The book is one member to many rows. Each row is a channel, an address, and the install it belongs to. The shed handset and the pocket handset are both stored.

A later token for the same install replaces that install's row. The pocket row stays, so a refresh does not grow a third address for one phone. When a send comes back unregistered, the desk deletes that row and leaves every other row. The next send uses what remains. A dead token left in the book returns as another reject, and the queue fills with work the provider has already refused.

```text
gather      a provider token, the shed number, the membership email
book        member → channel, address, install
two phones  two rows
refresh     replace the row for that install
rejected    delete that row, keep the others
```

## Notification Preferences

Member 14 can turn a channel off and can turn a type off. The channels are push, SMS, and email. The types are tap, frost, tool, and seed-list. Seed-list is promotional. Tap, frost, and tool are transactional. The switches are the member's, and the service reads them on every notice.

The gate runs before a template is rendered and before a message is written to a queue. Push is on, SMS is off, and seed-list is off. A seed-list push stops. A frost text stops. A frost push passes the switches, and the product budgets on Push Notification System still apply. A notice that fails the gate leaves nothing behind: no rendered body, no queued message, no provider call. The counter under those budgets is the Rate Limiter in [Rate Limiting and Throttling](../17_Rate_Limiting_and_Throttling/).

```text
channels     push, SMS, email
types        tap, frost, tool, seed-list
promo        seed-list
gate         before render, before the queue
SMS off      a frost text stops
type off     a seed-list push stops
budgets      Push Notification System
counter      Rate Limiter
```

## Notification Service Architecture

A tap event, or a call from the shed desk, enters the notification service. The service applies Notification Preferences, fills one template, and writes one message for each channel that passed. The tap template reads "Plot 14, the west tap is yours until 18:00." The wording lives in the template, so a frost notice and a tap notice share the rest of the path.

Each message goes to a queue, and one worker per channel performs the provider call. The buffer is a Message Queue in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/). Whether the provider call belongs off the request is When to Queue in that topic. The desk returns once the event is accepted. The service stores a status on the notice id: queued, accepted by the provider, or opened. A worker that falls behind shows up as queue depth, which is Backpressure in the same topic. A product that charts that depth for the membership is Metrics Monitoring System in [Classic Design Problems](../24_Classic_Design_Problems/).

```text
in        a tap event or a desk call
gate      Notification Preferences
wording   one template per type
then      one queued message per channel that passed
queue     Message Queue, When to Queue
workers   one per channel
status    queued, provider-accepted, opened
depth     Backpressure
charts    Metrics Monitoring System
```

## Presence

The desk marks a member online from a beat or from a connection. The app sends a beat every 20 seconds, and each beat refreshes a key that lives 50 seconds. A gap of 20 seconds still finds the key, so the member stays online. A gap of 50 seconds expires the key, and the member is offline.

An open socket is the other mark. The socket is WebSockets and SSE in [Networking and Communication](../10_Networking_and_Communication/). When it closes, a grace of 12 seconds starts. A reconnect at 8 seconds keeps the member online, and shed partners hear nothing about the gap. An explicit logout expires the mark immediately. The 12 seconds belong to a drop. A change, when the mark actually moves, goes to shed partners who are online now. An offline partner reads the mark the next time they open the app. A member watched by a large list is a choice on Fan-Out Strategies. The chat screen that paints the dot is Chat System in [Classic Design Problems](../24_Classic_Design_Problems/).

```text
beat        every 20 seconds, key lives 50
gap of 20   still online
gap of 50   offline
socket      WebSockets and SSE
grace       12 seconds after a drop
8 seconds   reconnect, tell nobody
logout      offline immediately
told        online shed partners
large list  Fan-Out Strategies
chat dot    Chat System
```

## Fan-Out Strategies

Fan-out is how one allotment event becomes a notice for many members. The choice is write, read, or hybrid, and it follows the size of the recipient set.

Fan-out on write copies the notice into each recipient's list when the event is saved. Six neighbors share the west tap. Six is at or under the write line of 500, so the event becomes six rows, and opening the list is one read of that member's rows. Fan-out on read stores the notice once. The pump alert names 18,000 members, at or over the read line of 5,000. Each member pulls recent shared alerts on open and keeps the ones that name them. The write is a single row.

A tool recall names 900 members. That count sits between the lines. Copying 900 rows is already an expensive write, and a pure pull makes every open scan a list that size. The desk writes a row for each on-duty steward inside the 900 and stores one notice for the other recipients to pull. That split is the hybrid. Placing the written rows beside the pulled notice, ranking that screen, and caching it are News Feed / Timeline in [Classic Design Problems](../24_Classic_Design_Problems/).

```text
write line    500, copy a row per recipient
6 neighbors   write
read line     5,000, store the notice once
18,000        read
900           hybrid, stewards written, the rest pull
screen, rank, cache   News Feed / Timeline
```

## In-App or Push

The path is chosen after Notification Preferences have passed the notice. Member 14 is in the app, watching the tap board. The tap notice rides the connection the app already holds. How that connection is kept, including a poll or a long poll, is Polling and Long-Polling and WebSockets and SSE in [Networking and Communication](../10_Networking_and_Communication/).

Member 14 is away, and Device Tokens still has a push row. The same tap notice goes out as a platform push on Push Notification System. Saturday's seed list can wait, so it goes by email even while the member is online. A frost warning with no push row, and SMS still allowed, goes by text. A walk along the plots is a stream of positions on that same transport topic. A test that the member entered the shed polygon is Geofencing in [Geospatial and Location-Based Services](../20_Geospatial_and_Location_Based_Services/). The notice that follows the test uses the path above.

```text
in the app, watching    the open connection
away, token on file     platform push
seed list               email, including while online
frost, no token         SMS
transports              Polling and Long-Polling, WebSockets and SSE
shed polygon            Geofencing
```

## Delivery Guarantees for Notifications

The channel worker calls the provider until the provider accepts the notice. When that accept is lost on the way back, the worker sends the same notice again, and the handset can receive it twice. The send is at-least-once. The broker's promise on that message is Message Delivery Guarantees in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/), the same class of promise. A duplicate is part of the design. Exactly-once would need the provider accept and the handset display to commit together, and those two sides do not share a commit. The notice id is what makes the second copy harmless: the handset keeps the ids it has shown and displays each id once.

Notices for one plot also carry a sequence. The handset orders by that sequence when a retry arrives after a later notice. A member who was away can have a pile waiting. Nine tap updates become one summary once the pile passes 3. The summary names the count and the latest turn. The nine rows stay on the server. A token the provider rejects is deleted on Device Tokens. The pause between tries is Timeouts and Retries in [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/). After that retry budget, the message is a Dead Letter Queue in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/).

```text
provider      retry until accept
lost accept   a second send of the same id
broker        Message Delivery Guarantees, at-least-once
handset       show each id once
order         a sequence per plot
pile past 3   one summary
pause         Timeouts and Retries
park          Dead Letter Queue
```
