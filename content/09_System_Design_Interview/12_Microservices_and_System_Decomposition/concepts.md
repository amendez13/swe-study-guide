## Monolith or Microservices

### What it is

A monolith is one process you build and ship as a unit. Microservices are separate processes: each one deploys on its own, and the call that used to be a function is a network hop.

### Why it exists

An online store is catalog, cart, orders, payments, and inventory. While they share a process, a Friday release ships all five, and a crash in payments restarts the process that also serves the product page. Splitting exists so one part can ship, or grow, without the others. Amazon's retail site and Netflix's streaming product both ended up as many services for that reason: a team had to change one part of the product without redeploying the rest. A small store hits the same choice as soon as one part blocks the others.

### How it works

Start with one process and one database.

1. Cart calls inventory in memory. One database transaction can reserve 2 units of SKU 18 and insert order 1842. Both changes commit, or neither does.
2. A bug in the payments page restarts that process. Catalog and checkout go down with it. You run one pipeline, and one person is on call.
3. The week before a holiday sale, catalog search uses about 70% of that process's CPU, and the checkout page slows with it. Adding a second copy of the whole process copies the quiet payments code onto the extra machine. That is horizontal scale of one deployable.
4. Moving catalog into its own process is a different move. Catalog can then run 4 instances while payments stays at 1, and catalog can ship on Tuesday while payments stays on last week's build.
5. The call from checkout to catalog is now a network hop. Give it a timeout, for example 100 ms. The hop can return a price from a few seconds ago, or fail while catalog restarts.

Splitting by function is the Y-axis of The Scale Cube in [Scalability Fundamentals](../02_Scalability_Fundamentals/). Cloning identical copies is the X-axis there, and splitting a dataset is the Z-axis. This card is the decision to leave one process.

### Trade-offs

One process keeps calls in memory and lets one transaction cover the order and the stock reservation. The shared fate is the cost: one bug, one release train, and one scale knob. Each service you add brings a pipeline, a config set, and someone who notices when it is down. A box per noun on a whiteboard still has to earn that cost. Name the part that must ship or scale alone before you draw the hop.

### In an interview

Say you would start with one deployable for the store. Name the part that blocks the rest, and call that split the Y-axis. If you cannot name that part, leave the boxes in one process.

### Recap

| | One process | Separate services |
| --- | --- | --- |
| What ships | Catalog, cart, orders, payments, and inventory deploy together. | Catalog can ship on Tuesday while payments stays on last week's build. |
| A failure | A payments crash takes the catalog page down too. | Catalog can stay up while payments restarts. |
| A call | In memory. One transaction can cover the stock reservation and the order. | A network hop. It can time out, come back stale, or fail during a restart. |
| What you operate | One pipeline and one on-call rotation. | A pipeline, a config set, and an alert for each service. |

![Monolith or Microservices](/content/09_System_Design_Interview/12_Microservices_and_System_Decomposition/diagrams/microservices-1-monolith-or-microservices.png)

*Source: [`diagrams/microservices.drawio`](/content/09_System_Design_Interview/12_Microservices_and_System_Decomposition/diagrams/microservices.drawio), page 1.*

## When to Decompose

### What it is

Decomposition is moving one part of the monolith into a process of its own. A piece leaves when it is the hot path, or when a team must release it alone. A piece that still changes with its neighbor stays. A drawing with more boxes is not one of these checks.

### Why it exists

Splitting too early buys a network hop for code that still ships as one change. Splitting too late forces every feature to scale and deploy with the hottest path. The checks exist so the hop shows up only where independence is already real.

### How it works

Walk the store with the three checks.

1. One domain is hot. The week before the holiday sale, catalog search saturates the process and the checkout page slows with it. Cloning the whole process copies the quiet admin screens onto every extra machine. Moving catalog search out lets that service add instances on its own. That is the Y-axis split from The Scale Cube in [Scalability Fundamentals](../02_Scalability_Fundamentals/), applied to a measured hotspot.
2. Two areas always change together. Every cart change still edits the order code, and every order change still edits the cart. They are one change. A network boundary between them adds two deploys and a version dance, and the teams still release together.
3. A team needs its own release. The payments group ships fraud-rule fixes on Tuesday. Waiting for Friday's storefront train makes a two-line fix a store-wide release, and a bad payments build takes the product page down. That is a real deploy boundary.

A modular monolith sits between one pile of code and a network hop. Catalog, orders, and payments are separate packages with separate owners, still one process, and still one database transaction where they share a database. A call between packages is a function call. Stop there until one package is the thing you must deploy or scale alone.

### Trade-offs

A hot path wants its own scale knob. A team with its own train wants its own deploy. Code that still lands in one pull request wants to stay one service. The modular monolith gives you the package boundary, the owners, and the local transaction, and it postpones timeouts and partial failure. Take the hop when a package's deploy or its CPU is the thing blocking the rest.

### In an interview

Name which of the three checks fired, and which piece moves first. Say that a tidier diagram is not a check. Offer the modular monolith when the pain is ownership and the process is still fine.

### Recap

- A hot domain moves out so you can add instances of that domain alone.
- Two areas that always change together stay one service.
- A team that must ship on its own train, and whose failures already take the rest down, gets a deploy boundary.
- A whiteboard with a box per noun leaves the code where it is.
- A modular monolith keeps the boundary inside one process until a deploy or a scale limit needs a hop.

![When to Decompose](/content/09_System_Design_Interview/12_Microservices_and_System_Decomposition/diagrams/microservices-2-when-to-decompose.png)

*Source: [`diagrams/microservices.drawio`](/content/09_System_Design_Interview/12_Microservices_and_System_Decomposition/diagrams/microservices.drawio), page 2.*

## Service Boundaries

### What it is

A service boundary wraps one business capability, a bounded context: one owner, and one meaning for the words that owner uses. The cut follows the capability a shopper or a team asks for.

### Why it exists

A cut along a technical layer puts every feature through one shared service. That service becomes the place every change has to touch, which is the coupling a split was supposed to remove. A boundary around a capability lets one team change its rules while the others keep their own.

### How it works

Use the store's words.

1. In the catalog, "available" means the product is listed for sale: SKU 18 is a blue mug at $21. Catalog owns products, titles, and list prices.
2. In inventory, "available" means a warehouse has units on hand: warehouse B has 14 units of SKU 18. Inventory owns counts, reservations, and warehouses.
3. The cart owns the line items a shopper has picked and has not paid for. Orders owns the purchase the shopper committed to. Payments owns the charge, the capture, and the refund.
4. An order stores `product_id` 18 and a quantity. It asks catalog when it needs the title. A price change in catalog does not require an orders schema change.
5. A proposed "database service" that reads and writes every table has to learn every feature, and every team edits it. A "validation service" that checks every form has to learn the coupon rule and the address rule. The rule belongs next to the rows it judges, inside the service that owns those rows.
6. Two proposed services that always land in the same pull request are one service. Put them back together until a change can ship on one side only.

The cut that holds has high cohesion inside the service, meaning the code that changes together lives together, and a narrow call between services, meaning the caller passes an id and a request rather than reaching into the other service's tables.

### Trade-offs

A capability boundary is stable because the business capability outlives a particular database or framework. A technical-layer boundary feels tidy on a diagram and couples every team to one service. Smaller boundaries mean more hops. Larger boundaries mean a change in one rule still redeploys unrelated rules. When two capabilities still change as one pull request, the larger boundary is the honest one.

### In an interview

Draw the line where the vocabulary changes. Catalog owns what a product is. Inventory owns how many units exist. Say that a shared database service or a shared validation service is a layer every team would have to edit, so the rule stays with the rows.

### Recap

| Proposed cut | What it owns | Decision |
| --- | --- | --- |
| Catalog | Products, titles, list prices. "Available" means listed for sale. | Keep. An order stores `product_id`. |
| Inventory | Counts and reservations. "Available" means units on hand. | Keep. Same word as catalog, different meaning, different owner. |
| Cart and orders, when every change ships both | One purchase flow that still changes together. | One service, until a change can ship on one side only. |
| A database service or a validation service | Every table, or every form rule. | Reject. The rule sits apart from the rows it judges. |

![Service Boundaries](/content/09_System_Design_Interview/12_Microservices_and_System_Decomposition/diagrams/microservices-3-service-boundaries.png)

*Source: [`diagrams/microservices.drawio`](/content/09_System_Design_Interview/12_Microservices_and_System_Decomposition/diagrams/microservices.drawio), page 3.*

## Data Ownership

### What it is

The service that decides a fact is the only service that writes the row. Everyone else stores an id and asks, or applies a fact the owner already published.

### Why it exists

A shared table couples two deploys through one schema, with the network left off the diagram. The services can ship on different days and still break each other, because there is no API version between a writer and a column.

### How it works

Catalog decides the product. It is the only writer of the product row, including the list price.

1. Inventory needs the price of SKU 18. It stores `product_id` 18. It calls catalog, or it applies a price-changed fact catalog already published. It does not run `UPDATE products SET price = ...`.
2. An unknown id is a normal answer. The product was withdrawn. The caller handles that the same way it handles any other missing product.
3. Suppose inventory also writes `products.price`. Catalog renames `price` to `price_cents` on Tuesday and ships. Inventory, still on Friday's build, writes the old column. Both deploys look healthy. The write fails, or it writes a column nobody reads. A shared table has no version header to negotiate that change.
4. A report that needs orders and categories reads each owner, or reads a copy built for that report. The copy can lag the owners by seconds. The lag is visible in the report, and the owners remain the place a correction is written.
5. One writer is the repair. Asking two databases to prepare and then commit together is Two-Phase Commit in [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/). That protocol coordinates a commit across databases. It does not turn a shared table into a service boundary.

The usual name for this rule is database-per-service: each service owns the tables it writes.

### Trade-offs

One writer makes the schema safe to change and makes the source of a fact obvious. The cost is that a question spanning two owners is either two calls or a read copy that can lag. A shared table looks simpler on a small team and couples the next two deploys. Two-phase commit can commit two databases together, and it holds locks while it does. It is a different tool, for a case where both sides must commit or both must abort. The ownership rule still stands when you choose it.

### In an interview

Say catalog is the only writer of the product row, and inventory stores `product_id`. Walk through the Tuesday rename: two deploys, one column, no API in between. If a report needs both sides, say where the read copy lives and that it can lag.

### Recap

- The owner is the only service allowed to write the row.
- Callers store an id such as `product_id`, then ask or apply a published fact.
- An unknown id means the product was withdrawn, and the caller handles it.
- A shared table lets one deploy's column rename break the other deploy's write.
- A cross-service report reads each owner, or a copy that can lag.
- Two-phase commit is a cross-database commit protocol. One writer is the ownership repair.

![Data Ownership](/content/09_System_Design_Interview/12_Microservices_and_System_Decomposition/diagrams/microservices-4-data-ownership.png)

*Source: [`diagrams/microservices.drawio`](/content/09_System_Design_Interview/12_Microservices_and_System_Decomposition/diagrams/microservices.drawio), page 4.*

## Multi-Tier Architecture

### What it is

Tiers are layers inside one deployable. Presentation is the page a shopper uses. Application is the rule, such as whether 2 units of SKU 18 can be reserved. Data is that deployable's database, plus a cache or a queue if it has one.

### Why it exists

People use "three-tier" and "microservices" as if they were the same diagram. They answer different questions. Tiers say who may call whom inside this program. Services say what ships separately. Mixing them produces a design that has three layers and still one release train, or several services and no story for what sits inside each one.

### How it works

1. A monolith can have all three tiers and still be one deploy. The shopper's page calls the reservation rule, and the rule reads that process's database.
2. A microservice can have all three tiers. Inventory's page, inventory's reservation rule, and inventory's database ship together, apart from catalog.
3. A service can also be a single process that is only the rule and its database, with no page of its own. Payments can be that shape: other services call it, and it has no shopper-facing screen.
4. Several services with no internal layering are still several network boundaries. Describe the tiers when you are explaining the inside of a deployable. Describe services when you are explaining what ships on its own.
5. The application tier is the one you clone, so a shopper's session stays out of the process. Any instance can then handle the next request. That rule is Stateless vs. Stateful Services in [Scalability Fundamentals](../02_Scalability_Fundamentals/), and a session moved to a store every instance can read is the Shared Session Store there.
6. A process that holds a shopper's order-status socket open is stateful: the connection lives in that process. The connection itself is WebSockets and SSE in [Networking and Communication](../10_Networking_and_Communication/).

### Trade-offs

Layers inside a deploy keep the page, the rule, and the database from tangling, and they leave you with one thing to ship. Service boundaries let those things ship on different days, and they add a hop at each cut. You can have three tiers and one service. You can have six services whose internals are each a small stack. Pick the word that matches the question you were asked: inside a deploy, or across deploys.

### In an interview

When the prompt says "three-tier," describe presentation, application, and data inside one deployable, and say that this is still one deploy. When the prompt says "split the store," name the services. Mention that the application tier stays stateless so you can clone it, and that an open order-status socket is state in one process.

### Recap

| Question you were asked | What you describe |
| --- | --- |
| What is inside this deployable? | Presentation (the shopper's page), application (the rule), and data (that service's database). |
| What ships on its own? | The services: catalog, cart, orders, payments, inventory. |
| Can one box be both? | Yes. A three-tier monolith is one deploy. One service can contain all three tiers. |
| What do you clone? | The application tier, with the session out of the process. A socket held open is stateful. |

![Multi-Tier Architecture](/content/09_System_Design_Interview/12_Microservices_and_System_Decomposition/diagrams/microservices-5-multi-tier-architecture.png)

*Source: [`diagrams/microservices.drawio`](/content/09_System_Design_Interview/12_Microservices_and_System_Decomposition/diagrams/microservices.drawio), page 5.*

## Event-Driven Architecture

### What it is

A service records a fact, publishes it, and returns. Other services react to that fact on their own. A synchronous call is the other shape: the caller waits, and the response is the answer.

### Why it exists

A checkout page that waits for every follower makes the shopper pay for work they already finished. A page that guesses a fact it needed, such as whether the units exist, confirms an order the warehouse cannot fill. The choice is which facts the response depends on.

### How it works

Order 1842 is 2 units of SKU 18.

1. The page asks inventory whether those 2 units exist, and it asks catalog for the current price. The HTTP response is that answer. Put the call on the request when the page would be a guess without it. Here the shopper is looking at a yes or a no.
2. Those two calls are 40 ms and 30 ms. A third synchronous call, payments at 180 ms, makes the page wait about 250 ms before it can answer. If payments is down, the whole chain fails. A chain waits on its slowest hop, and one dead process fails the chain.
3. Orders writes "order 1842 placed, SKU 18, quantity 2" and returns. The product page's stock count catches up when inventory applies the fact. The receipt email goes out. Monday's sales tally counts the order. None of those steps sit inside the shopper's request. The receipt can take 1.2 seconds and the shopper has already left. A reserve that must succeed before the charge, and a charge that must be undone if it fails, belong on the saga card. The event here is a follower that can lag.
4. The subscribers do not agree at the same instant. The order row can be committed while the product page still shows the old stock count, until inventory applies the event. That window is the lag you accepted.
5. Carry a request id on the event so a log search can follow it across services. The search is Centralized Logs in [Observability](../25_Observability/). A trace view across services is a later question in that topic.

Writing the order row and publishing the event are two steps. One can succeed while the other fails. The bus those events travel on, the test for what may leave the request, and the transactional outbox that keeps the order row and the first event from diverging are When to Queue and Transactional Outbox in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/). This card is the decision to publish.

### Trade-offs

A call gives the page a fresh answer and couples the page's success to every hop in the chain. An event lets the shopper leave and lets each subscriber fail and retry on its own. The subscribers are briefly stale, and you need a way to see the request in their logs. Use the call for a fact the response would be wrong without. Use the event for work that can finish after the shopper has an answer.

### In an interview

Point at each hop and say which kind it is. The stock check and the price stay on the request. The receipt and the Monday tally are events. Mention the request id, and say the bus and the outbox live in the message-queue topic.

### Recap

| Hop | Shape | Why |
| --- | --- | --- |
| Does SKU 18 have 2 units? | Call. About 40 ms, on the request. | The page is that answer. |
| What is the price? | Call. About 30 ms, on the request. | A missing price makes the page a failure. |
| Send the receipt. | Event, after the order is saved. | The shopper already has the confirmation. 1.2 s stays off the page. |
| Monday's sales tally. | Event. A later reader. | March, or Monday, can wait. |
| A chain of calls | The page waits on the sum, and one down process fails the chain. | Three hops at 40, 30, and 180 ms are about 250 ms, and a payments outage fails checkout. |

![Event-Driven Architecture](/content/09_System_Design_Interview/12_Microservices_and_System_Decomposition/diagrams/microservices-6-event-driven-architecture.png)

*Source: [`diagrams/microservices.drawio`](/content/09_System_Design_Interview/12_Microservices_and_System_Decomposition/diagrams/microservices.drawio), page 6.*

## Service Discovery

### What it is

Discovery is how a caller learns a current address. Instances start, stop, and move, so orders cannot keep a fixed host for inventory in a config file.

### Why it exists

Eight inventory instances today can be seven after a crash and nine after a scale-out. A caller that stores yesterday's IP connects to a machine that is gone, or it never sees the new one. Something has to hand out a live address.

### How it works

Inventory runs 8 instances. One crashes. The registry can still list it for about 30 seconds, until the missed heartbeat expires. Three styles deal with that list.

1. Client-side discovery. Orders reads the registry and connects to an instance it picked. There is no proxy hop. Orders has to speak the registry's protocol, and it has to skip an instance that is already gone while the registry still lists it: the connect fails, and orders tries the next address. This fits when you ship both sides and an extra hop is budget you do not have. Netflix published one version of this: services registered with Eureka, and the caller picked an instance.
2. Server-side discovery. Orders uses one stable address, such as `inventory.internal`. A load balancer or a proxy reads the registry and forwards. Callers stay simple, which is what you want when the callers are written in several languages and you will not put a registry client in each. You pay the extra hop, about 1 ms in the same zone. A Kubernetes Service is this shape: callers use one address, and the platform picks the pod. Which instance the balancer picks is Load Balancing Algorithms in [Load Balancing](../04_Load_Balancing/). This card stops at "a balancer is the lookup."
3. A mesh puts a sidecar proxy next to each instance. The process calls localhost. The sidecar learns the peer and can require a certificate on every hop, so the handlers do not contain that handshake. You operate the proxies as well as the services. Use it when every hop must look the same, including mutual TLS, and the application code should stay free of that handshake.

The address a shopper's browser uses is the API Gateway in [Networking and Communication](../10_Networking_and_Communication/). That host is the public front door. It checks the caller and routes by path. Netflix's Zuul gateway was that door, separate from Eureka. The gateway is the browser's entry. The registry is how orders and inventory find each other.

### Trade-offs

Client-side discovery spends no extra hop and puts registry logic, plus stale-instance handling, in every caller. Server-side discovery keeps callers simple and adds a proxy you now have to run. A mesh makes every hop look the same, certificates included, and it adds a proxy fleet beside the services. Pick from the constraint you were given: hop budget, number of languages, or a certificate on every call.

### In an interview

Say which style matches the constraint. Both sides are code you ship and the path has no room for a proxy: the caller reads the registry. Four languages and one stable address: a balancer reads the registry. Every hop must present a certificate and the handlers must stay free of that code: a sidecar. Then say the shopper's browser stops at the gateway.

### Recap

| Style | Who picks the instance | What you take on |
| --- | --- | --- |
| Client-side | The caller reads the registry and connects. | No proxy hop. The caller skips an instance the registry still lists, for example for 30 seconds after a crash. |
| Server-side | One stable address. A balancer picks the instance. | Simple callers, including several languages. About 1 ms extra in the same zone. |
| Mesh | A sidecar on each instance does the lookup and the certificate. | The process calls localhost. You operate the proxies too. |
| The public front door | The API gateway, for browsers. | Path routing and the shopper's identity. Peer discovery stays on the registry. |

![Service Discovery](/content/09_System_Design_Interview/12_Microservices_and_System_Decomposition/diagrams/microservices-7-service-discovery.png)

*Source: [`diagrams/microservices.drawio`](/content/09_System_Design_Interview/12_Microservices_and_System_Decomposition/diagrams/microservices.drawio), page 7.*

## Third-Party Integration

### What it is

A vendor is a process you do not deploy and cannot change. An adapter the store owns is the only code that speaks that vendor. The rest of the store calls the adapter.

### Why it exists

A carrier's shipping-quote API has its own URL, its own field names, and status codes that mean something odd. If orders calls that URL directly, a renamed field is a change in orders, in checkout, and in every other caller. The adapter keeps that churn in one place. It also keeps the vendor's latency off a page that cannot afford it.

### How it works

The carrier's slow tail is 8 seconds, and it was down this morning. The page budget for placing an order is 300 ms.

1. Orders says "quote shipping for cart 18, to zip 94107." That sentence is the store's contract.
2. The adapter is the only code that knows the carrier's URL, which status codes may be retried, and the timeout. Interviewers sometimes call this adapter an anti-corruption layer: it translates the vendor's names into yours, so the vendor's model stops at the adapter.
3. When the carrier renames a field, the adapter changes. Orders keeps the same request.
4. If the shopper needs a live quote before placing the order, the page waits on the adapter. The timeout is short enough that the page fails inside the 300 ms budget and shows a clear error. An 8 second tail does not fit on that page.
5. If the order is already placed and a refreshed quote can arrive later, the refresh goes on a queue. The shopper leaves with the order confirmed, and the page shows the last quote the adapter stored. A carrier outage then fails the refresh. The order stays placed. That split is When to Queue in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/).

The store owns the adapter's contract with orders. The carrier's URL and status codes stay inside the adapter. Charging a card is a different boundary: the payment intent, the signed webhook, and the poll live in [Payment and Financial Systems](../23_Payment_and_Financial_Systems/).

### Trade-offs

One adapter is another service to run, and it is the only place a vendor change hurts. Calling the vendor from each service avoids that hop and spreads the vendor's URL through the store. A short timeout protects the page and turns a slow vendor into a clear failure. A queue protects the page and accepts a stale quote until the refresh lands. Use the queue once the shopper can leave. Wait on the adapter when the page would be wrong without a fresh answer, and keep the timeout inside the page budget.

### In an interview

Name the adapter as the only code that knows the vendor URL. Put the 8 second tail next to the 300 ms budget and say the place-order request reads the last stored quote. The refresh is queued. Say that a card charge is the payments topic, and this card is the boundary around a vendor you do not deploy.

### Recap

| Piece | Where it sits |
| --- | --- |
| The carrier's URL, odd status codes, and timeout | Inside the adapter. A renamed field changes the adapter only. |
| "Quote shipping for cart 18" | The store's contract, from orders to the adapter. |
| A live quote the page needs before the shopper can finish | On the request, with a timeout inside the 300 ms budget. |
| A refresh after the order is already placed | On a queue. The page shows the last stored quote. A vendor outage fails the refresh. |
| An 8 second p99 against a 300 ms page | The vendor call stays off the place-order request. |

![Third-Party Integration](/content/09_System_Design_Interview/12_Microservices_and_System_Decomposition/diagrams/microservices-8-third-party-integration.png)

*Source: [`diagrams/microservices.drawio`](/content/09_System_Design_Interview/12_Microservices_and_System_Decomposition/diagrams/microservices.drawio), page 8.*

## Saga Pattern

### What it is

A saga is a chain of local commits, one per service, each with a compensating action. It is how work finishes across services that do not share a transaction.

### Why it exists

Order 1842 needs an order row, a stock reservation, and a charge. Each of those lives in a database its own service writes. There is no transaction that can commit all three. A later step can fail after an earlier step has already committed. The saga is the plan for undoing the steps that succeeded.

### How it works

The forward steps, each a commit in its own database:

1. Orders writes order 1842 as pending.
2. Inventory reserves 2 units of SKU 18 for that order.
3. Payments charges $42.

The charge is declined, and no money moves, so payments has nothing to undo. The two earlier commits are already durable. Compensations are new writes, run in reverse order of the steps that succeeded:

1. Inventory releases the 2 units.
2. Orders marks 1842 cancelled.

```python
def compensate(done: list[str]) -> list[str]:
    undo = {"open-order": "cancel-order", "reserve-stock": "release-stock"}
    return [undo[step] for step in reversed(done)]


print(compensate(["open-order", "reserve-stock"]))
# ['release-stock', 'cancel-order']
```

Nothing holds a lock across the three databases while this is in progress. Another shopper sees the available count fall by 2 and then rise again. That window is the consistency you accepted by giving each service its own rows. A compensation has to be safe to run twice: a second release finds no reservation and changes nothing, because the message may be delivered again.

Orchestration puts one coordinator on the chain. It calls open, then reserve, then charge, and it calls the compensations if the charge fails. It records which step completed, so a restart continues from the failed step. The path is easy to read back to a shopper. The coordinator is another process that has to be up, and a new step is a change to it.

Choreography has no coordinator. Orders publishes that 1842 is pending. Inventory reserves the units and publishes that. Payments fails the charge and publishes that. The earlier services compensate from the events. The flow is the events. Reading "what happens if the charge is declined" means reading three services. Choreography rides the bus in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/). The first event, the one that must not exist unless the local row committed, may need the Transactional Outbox there.

Two-phase commit would ask the three databases to prepare and then commit, holding locks until the decision. That protocol stays in [Transactions and Concurrency Control](../16_Transactions_and_Concurrency_Control/). A saga lets a step commit, then undoes it later with a compensating write if a later step fails.

### Trade-offs

A saga accepts a visible in-between state and needs a compensating action for every step that can succeed. A step you cannot undo, such as an email already sent, belongs after the saga, as an event, once the order is real. Orchestration makes the failure path one piece of code and adds a process to operate. Choreography leaves each team with its own handler and spreads the story across those handlers. Use orchestration while one team has to explain the path. Use choreography when each step is already an event those teams own.

### In an interview

List the local commits and the compensating write for each one, in reverse order. Say another shopper can see the 2 units reserved and then free, because no lock spans the databases. Pick an orchestrator when one team has to read the failure path back. Say two-phase commit is the prepare-and-commit protocol, and this design compensates after a local commit.

### Recap

| | What happens for order 1842 |
| --- | --- |
| Forward | Orders commits the pending order. Inventory commits a reservation of 2 units. Payments tries to charge $42. |
| Charge declined | Release the 2 units, then cancel the order. Those are new writes, in reverse order. |
| What a shopper can see | The available count falls by 2, then rises again. No lock spans the three databases. |
| Orchestration | One coordinator calls each step and the compensations, and it remembers the step so a restart can continue. |
| Choreography | Each service reacts to the previous event. The failure story is spread across the services. The bus and the outbox stay in the queue topic. |
| Two-phase commit | The databases prepare and then commit together. A saga commits locally, then compensates. |

![Saga Pattern](/content/09_System_Design_Interview/12_Microservices_and_System_Decomposition/diagrams/microservices-9-saga-pattern.png)

*Source: [`diagrams/microservices.drawio`](/content/09_System_Design_Interview/12_Microservices_and_System_Decomposition/diagrams/microservices.drawio), page 9.*
