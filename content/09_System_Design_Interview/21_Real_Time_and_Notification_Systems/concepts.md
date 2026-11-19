## Push Notification System

A push notification system delivers a short alert to a phone without your servers holding a connection to that phone. iOS alerts go to Apple Push Notification service (APNs), Android alerts to Firebase Cloud Messaging (FCM), texts to an SMS provider, and mail to an email provider. A ride-hailing app has to say "your driver is outside" while the rider's app is closed. The phone's operating system already keeps a long-lived connection to APNs or FCM, and your API servers do not, so the provider owns that last hop.

The app registers with APNs or FCM and receives a device token for that install, which is stored on Device Tokens. A trip event reaches the notification service. The service picks a channel, fills a short payload, and calls the provider with a server credential: an APNs provider token or certificate, or an FCM service account for the HTTP v1 API. The phone never sees that credential, and the adapter that holds it is Third-Party Integration in [Microservices and System Decomposition](../12_Microservices_and_System_Decomposition/). APNs returns HTTP 200 to `POST /3/device/<token>` when it accepts. Acceptance means the provider took the message. The lock screen can still stay dark if the phone is off or alerts are disabled. A lost success response is Delivery Guarantees for Notifications.

Two caps are counted separately. A promotional push, such as weekly deals, stops at 2 per rider per week. A transactional push, such as driver arrived, stops at 20 per rider per day, so a stream of updates cannot page the afternoon away. The counter is the Rate Limiter in [Rate Limiting and Throttling](../17_Rate_Limiting_and_Throttling/). An HTTP 429 asks the sender to slow down, which is Timeouts and Retries in [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/). APNs 410 `Unregistered` and FCM `UNREGISTERED` (404) remove the token. Sending every platform through FCM, which forwards to APNs, is a working one-integration alternative. Provider priority is a separate hint: APNs priority 10 and FCM `high` ask for immediate delivery, while APNs 5 or 1 and FCM `normal` may defer.

```text
iOS push       APNs             driver is outside
Android push   FCM              driver is outside
SMS            SMS provider     same arrival, no push token
email          email provider   weekly deals, or a receipt
caps           2 promotional/week, 20 transactional/day
```

![Push Notification System](/content/09_System_Design_Interview/21_Real_Time_and_Notification_Systems/diagrams/notifications-1-push-notification-system.png)

*Source: [`diagrams/notifications.drawio`](/content/09_System_Design_Interview/21_Real_Time_and_Notification_Systems/diagrams/notifications.drawio), page 1.*

## Device Tokens

A device token is the opaque address APNs or FCM assigns to one install of your app. The address book maps one rider to many rows. Each row is a channel, an address, and the install it belongs to. A rider can have the app on a phone and a tablet, and push has to reach the install that registered. The SMS row is the mobile number on the account and the email row is the account email. Those are addresses in the same book but not device tokens, and a push provider will not accept a phone number in the token field.

When the rider allows alerts, APNs or FCM returns a token, and the app posts it to the backend with a stable install id. The book stores one row per install, so the phone and the tablet are two rows. A later token for the same install replaces that row and leaves the tablet row alone, so a refresh does not leave the old phone token beside the new one. When a send comes back unregistered, as APNs HTTP 410 `Unregistered` or FCM `UNREGISTERED`, only that row is deleted, and the next send uses what remains. A dead token left in the book comes back as another reject, and the queue fills with work the provider has already refused.

Keeping every historical token for an install makes a debug log and keeps an address the provider will keep rejecting. Deleting every row for the rider when one token dies would also drop the tablet, the SMS number and the email. Not every error means the install is gone. APNs `BadDeviceToken` means the token string is malformed. FCM `INVALID_ARGUMENT` can mean a bad token or a bad payload, so delete for it only when the payload is valid.

```text
register    one push row per install id
refresh     replace that install's row, keep the others
410 / UNREGISTERED   delete that row only
book        push tokens + SMS number + email for one rider
```

![Device Tokens](/content/09_System_Design_Interview/21_Real_Time_and_Notification_Systems/diagrams/notifications-2-device-tokens.png)

*Source: [`diagrams/notifications.drawio`](/content/09_System_Design_Interview/21_Real_Time_and_Notification_Systems/diagrams/notifications.drawio), page 2.*

## Notification Preferences

Notification preferences are the rider's switches: one set for channels and one set for notice types. The service reads both on every notice. A rider can want trip alerts and refuse weekly deals, or want email and refuse SMS. Sending first and filtering later spends a template render, a queue write and sometimes a paid SMS on a message the rider has already declined.

The channels in this design are push, SMS and email. The types are trip alerts, which are transactional, and deals, which are promotional. Take a rider with push on, SMS off, email on, deals off and trip alerts on. A deals push stops because the type is off. A trip text stops because SMS is off. A trip push passes both switches. The gate runs before a template is rendered and before a message is written to a queue, so a notice that fails it leaves nothing behind: no rendered body, no queued message, no provider call. A notice that passes still has to fit the caps on Push Notification System, counted by the Rate Limiter in [Rate Limiting and Throttling](../17_Rate_Limiting_and_Throttling/).

One master "notifications off" switch is smaller to build and coarser than the settings screen riders already expect. Checking the switches inside the provider call is late, because the body is rendered and the message queued by then. A second check when the worker actually sends is the stricter option when a message can sit in the queue for minutes after the rider flips a switch. The required gate is the early one.

```text
deals via push        deals off           stop, nothing rendered or queued
trip alert via SMS    SMS off             stop, nothing rendered or queued
trip alert via push   trip on, push on    pass, then face the daily cap
```

![Notification Preferences](/content/09_System_Design_Interview/21_Real_Time_and_Notification_Systems/diagrams/notifications-3-notification-preferences.png)

*Source: [`diagrams/notifications.drawio`](/content/09_System_Design_Interview/21_Real_Time_and_Notification_Systems/diagrams/notifications.drawio), page 3.*

## Notification Service Architecture

The notification service turns one product event into one queued message for each channel the rider still allows. The trip service should return as soon as "driver arrived" is recorded. Rendering a template and calling APNs, FCM or an SMS provider are slower than that write, and they fail independently.

A trip event, or a call from an operations console, enters the service, which applies Notification Preferences first. It fills one template for the notice type, such as "Your driver is outside until 18:00." The wording lives in the template, so a deals notice and a trip notice share the rest of the path. The service then writes one message for each channel that passed. Those buffers are a Message Queue in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/), and the reason the provider call leaves the request is When to Queue in that topic. One worker per channel calls the provider, and the API returns once the event is on the queue. A status on the notice id moves from queued to accepted by the provider to opened, which is recorded when the app reports a tap.

One shared queue with a channel field is simpler to operate, and then a slow SMS provider sits in front of push messages. A queue per channel isolates that stall, and that split is what the figure shows. Calling the provider inside the trip request is a reasonable first version at low volume, and it ties the trip write to APNs latency. A worker that falls behind shows up as queue depth, which is Backpressure in the queue topic. A product that charts that depth is Metrics Monitoring System in [Classic Design Problems](../24_Classic_Design_Problems/).

```text
event -> preferences -> one template -> one message per allowed channel
worker per channel -> provider
status   queued -> provider-accepted -> opened
lag      queue depth
```

![Notification Service Architecture](/content/09_System_Design_Interview/21_Real_Time_and_Notification_Systems/diagrams/notifications-4-notification-service-architecture.png)

*Source: [`diagrams/notifications.drawio`](/content/09_System_Design_Interview/21_Real_Time_and_Notification_Systems/diagrams/notifications.drawio), page 4.*

## Presence

Presence is the record of who is online right now. A Slack-style chat uses it for the active and away dot next to a teammate. The roster should survive a subway blip and update when someone actually leaves. Marking offline on every dropped packet makes the dot flicker, and publishing every heartbeat to every teammate wakes the whole company every 20 seconds.

There are two ways to hold the mark. With a heartbeat, the app sends a beat every 20 seconds and each beat refreshes a key that lives 50 seconds. A single missed beat still finds the key. In the worked timeline, beats land at 0, 20 and 40 seconds. If the beat due at 60 never arrives, the key set at 40 expires at 90, and the person is offline then. With a socket, the open connection is the mark, held as described in WebSockets and SSE in [Networking and Communication](../10_Networking_and_Communication/). When it closes, a 12-second grace starts. A reconnect at 8 seconds keeps the person online and nobody is told. A drop still open at 20 seconds is past the grace, so the mark becomes offline. An explicit logout skips the grace and is offline immediately.

A change is published only when the mark actually moves, and only to subscribers who are online now. An offline subscriber reads the mark on their next open. A heartbeat alone fits a mobile client that cannot hold a socket. Using both fits a Slack-style client, where the socket is the live signal and the heartbeat covers an unreliable socket. A TTL equal to the beat interval drops people on one lost beat, and a much longer one hides real departures. A user watched by a huge list is a choice on Fan-Out Strategies, and the screen that paints the dot is Chat System in [Classic Design Problems](../24_Classic_Design_Problems/).

```text
heartbeat     every 20 s, key TTL 50 s     last beat at 40 s -> offline at 90 s
reconnect     8 s, inside the 12 s grace   stays online, nobody told
still down    20 s, past the grace         offline
logout        immediate                    offline, no grace
who hears     subscribed and online
```

![Presence](/content/09_System_Design_Interview/21_Real_Time_and_Notification_Systems/diagrams/notifications-5-presence.png)

*Source: [`diagrams/notifications.drawio`](/content/09_System_Design_Interview/21_Real_Time_and_Notification_Systems/diagrams/notifications.drawio), page 5.*

## Fan-Out Strategies

Fan-out is how one event becomes a notice for many people. The choice is write, read, or hybrid, and it follows the size of the recipient set. Six people in a trip chat and 18,000 riders in a city-wide outage cannot share a write path. Copying a row into every inbox makes the open cheap and the publish expensive. Storing the notice once makes the publish a single row and makes every open do more work.

This design draws two lines: at or under 500 recipients, fan out on write, and at or over 5,000, fan out on read. A trip chat of six becomes six inbox rows, and opening the list is one read of that person's rows. A city outage naming 18,000 riders is stored once, and each rider pulls recent shared alerts on open and keeps the ones that name them. A safety notice naming 900 drivers sits between the lines. Copying 900 rows is already an expensive write, and a pure pull makes all 900 opens assemble the notice. The service writes a row for each on-duty dispatcher inside the 900 and stores one notice for the rest to pull. That split is the hybrid.

Write favors the reader and punishes a huge recipient set, since one blast becomes one insert per person. Read favors the writer and makes every open heavier. Hybrid spends inserts on the people who must see the notice immediately. The lines are a product choice, and 500 and 5,000 are this design's numbers, so ask for the recipient count before you pick a shape. Placing the written rows beside the pulled notice, ranking that screen and caching it are News Feed in [Classic Design Problems](../24_Classic_Design_Problems/).

```text
6        at or under 500    write    one inbox row per recipient
900      between the lines  hybrid   rows for on-duty dispatchers, others pull
18,000   at or over 5,000   read     one stored notice, pulled on open
```

![Fan-Out Strategies](/content/09_System_Design_Interview/21_Real_Time_and_Notification_Systems/diagrams/notifications-6-fan-out-strategies.png)

*Source: [`diagrams/notifications.drawio`](/content/09_System_Design_Interview/21_Real_Time_and_Notification_Systems/diagrams/notifications.drawio), page 6.*

## In-App or Push

After preferences allow a notice, this choice picks the pipe: the connection the app already holds, a platform push, email, or SMS. A rider staring at the trip screen already has a live connection, and a platform push to that phone is a second banner for news the screen is about to show. A rider who locked the phone has no connection to write on. A weekly deals mail can wait in either case.

The decision is made per notice, after Notification Preferences pass it. A rider in the app watching the trip gets the notice on the connection the app already holds. How that connection is kept, including a poll or a long poll, is Polling and Long-Polling and WebSockets and SSE in [Networking and Communication](../10_Networking_and_Communication/). A rider who is away, with a push row still on Device Tokens, gets the same trip notice as a platform push on Push Notification System. Weekly deals go by email even while the rider is online. A driver-arrived alert with no push row, while SMS is still allowed, goes by text. The test that the rider entered the pickup polygon is Geofencing in [Geospatial and Location-Based Services](../20_Geospatial_and_Location_Based_Services/), and the notice that follows it takes this same path.

Always pushing is one code path, and it double-notifies people who are already looking at the trip. Always waiting for the app to poll misses the locked phone. Email for an arrival hides a driver standing at the curb. SMS for every trip update is expensive and ignores a working push token. So the order is: an open screen uses the open connection, an absent rider with a token gets a push, mail carries what can wait, and SMS is the urgent fallback.

```text
in the app, watching the trip         the connection the app holds
away, push token on file              APNs or FCM
weekly deals, even while online       email
urgent, no push token, SMS allowed    SMS
```

![In-App or Push](/content/09_System_Design_Interview/21_Real_Time_and_Notification_Systems/diagrams/notifications-7-in-app-or-push.png)

*Source: [`diagrams/notifications.drawio`](/content/09_System_Design_Interview/21_Real_Time_and_Notification_Systems/diagrams/notifications.drawio), page 7.*

## Delivery Guarantees for Notifications

Delivery to the provider is at-least-once. The phone makes a duplicate harmless by showing each notice id once. The channel worker retries when a call fails. The awkward case is a call that succeeded and whose success response was lost, so the worker sends the same notice again. Exactly-once would need the provider's accept and the phone's display to commit together, and those two sides have no shared commit.

The worker calls the provider until it accepts, so a lost accept produces a second send of the same id. The broker makes the same class of promise about the queued message, which is Message Delivery Guarantees in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/). The phone keeps the ids it has shown, so a second copy of `n-18` is the same notice. Notices for one trip also carry a sequence, so when `n-19` arrives before a retry of `n-18`, the phone still renders them in trip order. A rider who was away can have a pile waiting. Nine trip updates become one summary once the pile passes 3, naming the count and the latest update, and the nine rows stay on the server. Three waiting reminders sit at the line, so each one is still sent.

A single attempt avoids duplicates and drops any notice whose response was lost. Retrying until accept keeps the arrival alert and requires the phone to dedupe. Providers also coalesce banners. APNs merges banners that share an `apns-collapse-id` of at most 64 bytes. An FCM collapse key keeps the latest message per key while the device is offline, with at most four distinct keys per device. That merges the visible banner, not the stored rows, and it is separate from the summary. A rejected token is deleted on Device Tokens. The pause between tries is Timeouts and Retries in [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/). A message that spends its retry budget goes to a Dead Letter Queue in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/).

```text
provider   at-least-once, retry until accept
phone      show each notice id once, order one trip by sequence
pile       more than 3 waiting -> one summary, rows stay stored
spent      retry budget exhausted -> dead letter queue
```

![Delivery Guarantees for Notifications](/content/09_System_Design_Interview/21_Real_Time_and_Notification_Systems/diagrams/notifications-8-delivery-guarantees-for-notifications.png)

*Source: [`diagrams/notifications.drawio`](/content/09_System_Design_Interview/21_Real_Time_and_Notification_Systems/diagrams/notifications.drawio), page 8.*
