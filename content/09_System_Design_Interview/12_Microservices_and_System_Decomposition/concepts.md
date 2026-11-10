## Monolith or Microservices

A monolith is one process you ship as a unit. At a ceramics guild, the shelf list, the kiln calendar, and the glaze batches live in that process. A firing-week change and a shelf change ride the same deploy. A bug in the glaze page takes the kiln calendar down with it. Calls between those parts stay in memory, and one database transaction can cover a shelf and a week.

Microservices are separate processes, each with its own deploy. The kiln calendar can ship on Tuesday while the shelf code stays on last week's build, and a holiday rush can add kiln instances without copying the glaze process. The call that used to be a function is now a network hop. It can time out, return a stale shelf, or fail while that process restarts. Each service also brings a pipeline, a config set, and someone who notices when it is down.

Start with the one process. Splitting by function is the Y-axis of The Scale Cube in [Scalability Fundamentals](../02_Scalability_Fundamentals/). Use that axis when one part is the reason the rest cannot ship or scale. A diagram that opens with a box per noun has not earned those hops.

```text
one process     shelf, kiln, and glaze deploy together
split           a service ships and scales on its own
first move      one process, until a measured reason appears
```

## When to Decompose

Three checks decide whether a piece leaves the monolith. A drawing with more boxes is not one of them.

One domain is hot. The week before the holiday sale, kiln scheduling saturates the process and the shelf page slows with it. Cloning the whole process copies the quiet glaze code on every extra machine. Moving the kiln calendar out lets that service scale on its own. That is the Y-axis split, not a new kind of scale.

Two areas always change together. If every shelf change still edits the kiln calendar, and the reverse, they are one change. A network boundary between them adds a deploy dance and no independence.

A team needs its own release. The clay buyer ships supplier fixes on Tuesday and should not wait for the Friday guild train, and a bad clay release should not take the kiln page down. That is a real reason. A whiteboard that would look tidier with more boxes is not.

A modular monolith sits between one process and a network hop. Separate packages, separate owners, still one process and still one database transaction where the modules share a database. Stop there until one module is the thing you must deploy or scale alone.

```text
hot path        that part needs its own scale
same release    keep the pieces in one service
own train       a team ships without the rest
not a reason    a drawing with more boxes
```

## Service Boundaries

Draw a service around a business capability, a bounded context. Inside the shelf service, "ready" means the piece can go in a kiln. Inside the kiln service, "ready" means the week has room. Same word, two meanings, two owners. The shelf service knows pieces and shelves. The kiln service knows cones, kilns, and weeks. The glaze service knows batches the guild mixed. Each one is a reason a member calls the guild.

A cut along a technical layer piles every feature onto one shared service. A "database service" that reads and writes every table becomes the place every change has to touch. A "validation service" that checks every form has to learn the kiln rule and the glaze rule, and both teams edit it. The rule belongs next to the rows it judges.

Two proposed services that always land in the same pull request are one service. Put them back together until a change can ship on one side only. The cut that holds is high cohesion inside the service and a narrow call between services.

```text
shelf      pieces and which shelf they sit on
kiln       which kiln, which week, which cone
glaze      batches the guild mixed
reject     "the database" or "validation" as a service
```

## Data Ownership

The service that decides a fact is the service that writes the row. The shelf service owns the piece row, including the condition. The kiln service does not update that condition. It stores `piece_id`. When it needs the condition, it asks the shelf service, or it applies a fact the shelf service already published. An unknown id is a normal answer: the piece was withdrawn, and the caller handles that.

A shared table is coupling with the network left off the diagram. The kiln service and the shelf service both writing `pieces.condition` can deploy on different days and still break each other. One renames the column. The other ships a write that expected the old name. There is no API version between them. A report that needs both reads from each owner, or from a copy built for reading. That copy can lag the owner.

One writer is the repair. Asking two databases to prepare and then commit together is Two-Phase Commit (2PC) in [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/). That protocol is a different problem. It does not make a shared table into a boundary.

```text
owner         the only service allowed to write the row
piece_id      a reference, not a shared row
shared table  two deploys, one schema
```

## Multi-Tier Architecture

Tiers are layers inside a deployable. Presentation is the page a member uses. Application is the rule, such as whether kiln 2 has room in week 12. Data is that service's database, and a cache or a queue if it has one. A monolith can have all three. A microservice can have all three, or a single process that is only the rule and its database.

The tiers say who may call whom inside this program. The service cut says what ships separately. A three-tier monolith is still one deploy. Several services with no internal layering are still several network boundaries. Describe the tiers when you are explaining the inside of a deployable. Describe services when you are explaining what ships on its own.

The application tier is the one you clone, so it should not keep a member's session in the process. That rule is Stateless vs. Stateful Services in [Scalability Fundamentals](../02_Scalability_Fundamentals/), and a session moved out of the process is the Shared Session Store there. A kiln monitor that holds a socket open is a stateful process. The connection itself is WebSockets and SSE in [Networking and Communication](../10_Networking_and_Communication/).

```text
presentation   the member's page
application    the kiln-week rule
data           that service's database
orthogonal     tiers sit inside a deploy; services are the deploys
```

## Event-Driven Architecture

A service records a fact and publishes it. Others react. The kiln service writes "kiln 2, week 12, piece 18" and returns. The shelf service marks the piece as scheduled. The glaze service stages a batch. The holiday tally counts the firing. None of those steps sit inside the member's request.

A synchronous call is the other shape. The page asks the kiln service whether week 12 has room, and the HTTP status is that answer. Put the call on the request when the response would be a guess without it. Leave it off the request when the member can go back to the shelf with the week already confirmed. A chain of synchronous calls makes the page wait on the slowest hop, and one down process fails the whole chain.

The subscribers do not agree at the same instant. The week can be booked in the kiln database while the shelf page still shows the piece as free, until the event is applied. Carry a request id on the event so a log search can follow it. The search is Centralized Logs in [Observability](../25_Observability/). A trace view across services is a later question in that topic.

The bus those events travel on, the test for what may leave the request, and the transactional outbox that keeps the kiln row and the first event from diverging are When to Queue and Transactional Outbox in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/). This card is the decision to publish.

```text
publish     the kiln service states the week and returns
react       shelf, glaze, and the tally each apply it
call        the page needs a yes or no before it can answer
```

## Service Discovery

Instances start, stop, and move. The kiln service cannot keep a fixed host for the shelf service. Discovery is how a caller learns a current address.

Client-side discovery means the caller reads a registry and connects to an instance it picked. There is no proxy hop. The caller has to speak the registry, and it has to skip an instance that is already gone while the registry still lists it. That fits when you ship both sides and an extra hop is the budget you do not have.

Server-side discovery means the caller uses one stable address. A load balancer or a proxy reads the registry and forwards. Callers stay simple, which is what you want when the callers are written in several languages and you will not put a registry client in each. You pay the extra hop. Which instance the balancer picks is Load Balancing Algorithms in [Load Balancing](../04_Load_Balancing/). This card stops at "a balancer is the lookup."

A mesh puts a sidecar proxy next to each instance. The process calls localhost. The sidecar learns the peer, and it can require a certificate on every hop, so the handlers do not contain that handshake. You operate the proxies as well as the services. Use it when every hop must look the same, including mutual TLS, and the application code should not know.

The address a member's browser uses is the API Gateway in [Networking and Communication](../10_Networking_and_Communication/). That host is the public front door. It checks the caller and routes by path. It is not the registry the kiln service and the shelf service use between themselves.

```text
client-side    the caller reads the registry and connects
server-side    one address; a balancer picks the instance
mesh           a sidecar does the lookup and the certificate
front door     the gateway, for browsers, not for peers
```

## Third-Party Integration

A vendor is a process you do not deploy and cannot change. The clay supplier is one. Wrap it behind a boundary the guild owns. An adapter service is the only code that knows the supplier's URL, the odd status codes, and which errors may be retried. The kiln service says "deliver two bags of stoneware before week 12." When the supplier renames a field, the adapter changes. The kiln service does not.

Put a timeout on the call, and keep the supplier's latency off the member's request. A supplier whose slow responses run to several seconds cannot sit inside the page that confirms week 12. If the member needs a price before confirming, the page waits on the adapter, and the timeout is short enough that the page fails clearly. If the week is already confirmed and the clay can arrive later, the refresh goes on a queue. The member leaves. A supplier outage then fails the refresh, not the confirmation. That split is When to Queue in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/).

The guild owns the adapter's contract with the kiln service. The supplier's URL and status codes stay inside the adapter.

```text
adapter    the only code that speaks the supplier
timeout    the confirm page does not inherit the supplier's latency
queue      the week is already saved, and the clay can follow
```

## Saga Pattern

A saga is a chain of local commits, each with a compensating action, for work that spans services that do not share a transaction. The shelf service holds piece 18. The kiln service writes week 12. The glaze service reserves a batch. Each step commits in its own database. If the glaze batch is short, the kiln service cancels week 12 and the shelf service releases piece 18. Those compensations are new writes. They run in reverse order of the steps that succeeded. They are not a rollback of someone else's database.

Nothing holds a lock across the three databases while this is in progress. Another member can see piece 18 as held and then see it free again. That window is the consistency you accepted by giving each service its own rows.

Orchestration puts one coordinator on the chain. It calls hold, then book, then reserve, and it calls the compensations if reserve fails. The path is easy to read back to a member. The coordinator is another process that has to be up, and a new step is a change to it.

Choreography has no coordinator. The shelf service publishes that piece 18 is held. The kiln service books the week and publishes that. The glaze service fails the reserve and publishes that. The earlier services compensate. The flow is the events. Reading "what happens if the batch is short" means reading three services. Choreography rides the bus in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/). The first event, the one that must not exist unless the local row committed, may need the Transactional Outbox there.

A saga is not Two-Phase Commit (2PC). That protocol would ask the three databases to prepare and then commit, and it stays in [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/). A saga lets a step commit, then undoes it later with a compensating action if a later step fails.

```text
hold shelf → book week → reserve glaze
glaze fails → cancel the week → release the shelf
orchestrate    one coordinator calls each step
choreograph    each service reacts to the previous event
```
