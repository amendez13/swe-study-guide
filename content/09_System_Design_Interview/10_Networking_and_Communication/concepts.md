## TCP and UDP

TCP gives the application an ordered byte stream. The two sides handshake, then each byte is numbered. The stack resends a segment that was not acknowledged, and the receiver does not hand the application a later byte while an earlier one is missing. A font file, an HTTP request, and a job body want that stream. A hole in the middle would change the message.

UDP gives the application datagrams. Each send is one packet. The network may drop it, delay it, or deliver it ahead of a packet sent earlier. There is no handshake and no resend. A press-temperature sample once a second can skip a lost packet, because the next sample replaces it. Anything else the application still needs, it adds itself. A sequence number or a timestamp lets the receiver ignore a sample that arrived late. An authentication tag is the application's when the packet must be trusted. A resend, when a lost datagram cannot be skipped, is the application's too. The timeout that decides a packet is missing, and the backoff before a retry, are Unreliable Networks in [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/).

```text
TCP     handshake, ordered bytes, the stack repairs loss
UDP     one datagram, loss and reorder stay visible
on UDP  the application adds order, a resend, or an auth tag when it needs them
```

## HTTP Connections

HTTP/1.0 opened a TCP connection, carried one request, and closed it. The next request paid for another handshake. HTTP/1.1 keep-alive leaves the connection open, so a following request skips that handshake. Responses on that connection still come back one at a time, in order. A slow response holds every later response on the same connection. That wait is head-of-line blocking. A client that wants six responses in flight opens six connections.

HTTP/2 keeps one connection and splits it into streams. Frames from different streams interleave, so one slow response does not block the others. gRPC wants HTTP/2 for that reason: many calls, and a stream that stays open, share a connection without lining up behind one response. The call still looks like a local function, which is RPC. The bytes and the rules for adding a field are Protocol Buffers and Schema Evolution in [Encoding Serialization and Schema Evolution](../14_Encoding_Serialization_and_Schema_Evolution/).

```text
HTTP/1.0    open, one request, close
HTTP/1.1    keep-alive, one response at a time on the connection
HTTP/2      many streams on one connection
gRPC        uses that multiplex so calls do not queue behind one response
```

## REST

REST names each resource with a URL and uses the HTTP method as the operation. GET reads the resource. POST creates one, or starts an action that is not a replacement of one URL. PUT replaces the resource with the body. PATCH changes part of it. DELETE removes it. A redirect in the 3xx range carries the next URL in Location, and the client requests that URL. A shortener's redirect table is a different design.

Each request stands alone. It carries the credential and the identifiers the handler needs. The server does not keep a conversational session for that client between calls. That is the web-tier case of Stateless vs. Stateful Services in [Scalability Fundamentals](../02_Scalability_Fundamentals/). A response may declare a cache lifetime with Cache-Control, and a validator with ETag, so an intermediary that understands HTTP can reuse a stable GET. The tier that stores the response is [Caching](../05_Caching/). A public object served from the edge of the network is [Content Distribution and Media](../22_Content_Distribution_and_Media/).

Browsers, proxies, and gateways already understand these methods and URL shapes. A public CRUD API in an interview takes this form. A call that should look like a function in the caller's source is RPC.

```text
GET     /jobs/42     read job 42
POST    /jobs        create a job
PUT     /jobs/42     replace job 42
PATCH   /jobs/42     change one field
DELETE  /jobs/42     remove job 42
3xx                  Location names the next URL
```

## RPC

A remote procedure call is written as a function call. The client calls a stub, the stub sends the arguments, and the return value comes back as if the function had run in the same process. The network is still on the path. The call can time out, and a retry can run the handler again. The name that makes a retried write one write is Idempotency. The lost reply is Unreliable Networks in [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/).

The usual interview form is gRPC. One call can carry a stream of messages in one direction or in both, so a long transfer stays a single call. The messages ride HTTP/2, so other calls share the connection. That sharing is HTTP Connections. The payload is often Protocol Buffers. Field numbers, generated clients, and adding a field an old reader can skip are Protocol Buffers and Schema Evolution in [Encoding Serialization and Schema Evolution](../14_Encoding_Serialization_and_Schema_Evolution/).

A browser does not speak that stub. A public caller you do not ship already knows how to send HTTP. A service you do ship, on a private network, can take the stub and keep one contract for every language you generate.

```text
reply = press.StartRun(job_id=42)    the call site looks local
stream = press.Watch(job_id=42)      messages until the run ends
schema and field numbers             Encoding Serialization and Schema Evolution
```

## REST or RPC

REST fits a caller outside your deploy, a CRUD operation on a resource, and a response a cache or a browser can use. RPC fits a service you ship, a high call rate, and a stream. Many systems use both. The public edge speaks REST. Services behind that edge call each other with RPC.

A catalog of open press times, read with curl and cacheable for a minute, is REST. The job service telling a press to start, then reading a stream of temperatures, is RPC. Both ends of that stream are code you deploy, and the contract lives in one definition. Offering only the stub as the public API drops the caller who will not generate a client.

```text
public, CRUD, cacheable          REST
internal, low latency, a stream  RPC
the usual system                 REST at the edge, RPC behind it
```

## Forward and Reverse Proxy

A forward proxy sits with the clients. The print shop's laptops send outbound traffic through it, and the vendor they reach sees the proxy's address. The shop uses that hop to filter destinations and to keep laptop addresses off the public network.

A reverse proxy sits with the servers. Clients use its address, and it forwards to a machine the client never addresses. It hides which server is up. It can terminate TLS, hold a cacheable response, or absorb traffic the origin should not take directly. The box in front of a web tier faces this direction. Choosing a server inside one pool, checking health, and terminating TLS as a balancer feature are [Load Balancing](../04_Load_Balancing/). Publishing several addresses for one name is DNS-Level Load Balancing in that same topic.

An API gateway is a reverse proxy whose extra job is the API: route by path, check a credential, and apply a request budget. The budget's algorithm is [Rate Limiting and Throttling](../17_Rate_Limiting_and_Throttling/). A load balancer can be the same binary and a different job, spreading one pool of identical workers. A gateway fronts different services. Draw the box for the job this design actually has. Those gateway duties are the next card.

```text
forward proxy    laptops → office proxy → vendor     the vendor sees the proxy
reverse proxy    customer → shop address → a server  the customer does not address the server
load balancer    spreads one pool                    the pick stays in Load Balancing
API gateway      path, credential, and budget        a reverse proxy with API duties
```

## API Gateway

The gateway is the one host a client calls when several services sit behind it. The client learns the gateway's address and the paths, not the address of each service. The gateway matches the path, checks the credential, and forwards.

```text
customer → gateway
             /jobs    → job service
             /presses → press service
```

Routing is that match. Authentication rejects a missing or invalid token before a service runs. TLS termination decrypts at this hop so the path can be read. Where the certificate lives, and when the hop behind the gateway stays encrypted, is TLS Termination in [Load Balancing](../04_Load_Balancing/). A request budget fits this edge when one limit should cover every service. The token bucket, the window, and the headers on a refusal are the Rate Limiter in [Rate Limiting and Throttling](../17_Rate_Limiting_and_Throttling/). The gateway applies the result of that limit.

The service keeps the work that needs its own data. Whether a job slot is free, and the insert of the job row, run on the job service. A page that needs both a job and a press can call the gateway twice, or once if the gateway asks both services and combines the answers. The combined call hides the split, and it finishes when the slower service finishes. Where that split belongs is Service Boundaries in [Microservices and System Decomposition](../12_Microservices_and_System_Decomposition/). How one service finds another service's current address is Service Discovery in that topic. The gateway is the client's front door. It is not the registry those services use among themselves.

```text
gateway    route, authenticate, terminate TLS, apply the budget
service    the job row and the rule that decides it
peers      Service Discovery
```

## Polling and Long-Polling

Short polling asks on a timer. The client sends a request, the server answers with the current value, and the connection closes. A job page that can be fifteen seconds stale sends `GET /jobs/42` every fifteen seconds. The handler is an ordinary read. Most answers say the job has not changed. The change can arrive as late as one full interval, and the client pays for a request on every interval.

Long-polling holds one request open. The client sends the GET. The server writes the response when the job changes, or when a timeout fires, whichever comes first. The client reads the body and sends the next GET immediately. A change leaves during the hold, so the wait is the open request. Each delivery is still a full HTTP request, and a quiet timeout still ends so the client can open the next hold. A proxy that already allows a request and a response allows this, because the path does not have to learn a second protocol.

The choice is an interval or a held request. Short polling keeps the server to a normal read and spends requests. Long-polling spends an open request to shorten the wait. A stream the server writes without a new request per event, and a connection both sides can write, are WebSockets and SSE.

```text
short poll    request, answer now, wait out the interval, request again
long poll     the request stays open until a change or a timeout
lateness      up to one interval, or as long as the hold
```

## WebSockets and SSE

A WebSocket starts as HTTP, with a request to upgrade. After the upgrade, either side writes a frame at any time on that connection. The press operator can send a pause and receive temperatures without opening a second channel. The process that accepted the socket is the process that can read and write it. Another process has no socket for that client. Holding the conversation in the process is the stateful case of Stateless vs. Stateful Services in [Scalability Fundamentals](../02_Scalability_Fundamentals/).

The TCP connection stays on the server that accepted it for the life of the socket. A reconnect is a new connection. It reaches a process that can continue the conversation when the balancer pins the client, or when any process can load a shared record and resume. The pin is Sticky Sessions in [Load Balancing](../04_Load_Balancing/). The shared record is the Shared Session Store in [Scalability Fundamentals](../02_Scalability_Fundamentals/). The algorithm that picks a server for a fresh connection stays in Load Balancing.

Server-Sent Events (SSE) are an HTTP response the server keeps writing. The body is a sequence of events, and the client reads. The client does not write events back on that response. A page that only watches temperature uses SSE, and a separate POST carries a command. Intermediaries that pass a response body can pass the stream, because it is still HTTP. An event can carry an id. On reconnect the client sends the last id it applied, and the server continues after that id. Who counts as present, and how a closed app receives a vendor push, are Presence and Real-Time Delivery Patterns in [Real-Time and Notification Systems](../21_Real_Time_and_Notification_Systems/).

```text
WebSocket    upgrade, then either side writes frames
SSE          the server writes events, the client reads
reconnect    a new connection; SSE can send the last event id
the socket   stays on the process that accepted it
```

## Idempotency

An operation is idempotent when repeating it leaves the outcome the first accepted call already produced. GET reads. PUT with the same body replaces the resource with that body again. DELETE leaves the resource absent, and a second DELETE leaves it absent. POST accepts a new job on each call, so two accepted POSTs are two jobs.

A client that hits its deadline does not know whether the handler committed. The response may be what was lost. The client sends the POST again. With no shared name for that attempt, the server treats the second call as a new job. The client sends an idempotency key it chose for this one attempt. The server stores the key with the response. The first call creates the job and saves the pair. A retry with the same key returns the saved response and does not insert again. A second call that arrives while the first is still running waits for that result, or gets a conflict, so two workers do not both insert. A different key is a different attempt, and it creates a job on purpose.

```text
POST /jobs
Idempotency-Key: 7c1e
{ "cards": 500, "stock": "cream" }

first call with 7c1e    creates job 18 and stores the response
retry with 7c1e         returns job 18
POST with 9af0          creates a different job
```

A charge has this same shape: the key names the attempt, and the handler returns the stored result on a retry. The ledger under that charge is Idempotency in Payments in [Payment and Financial Systems](../23_Payment_and_Financial_Systems/). Lost replies, duplicate packets, and the wait before a retry are Unreliable Networks in [Distributed System Failure Modes](../15_Distributed_System_Failure_Modes/). A consumer that can see the same queued message twice is Message Delivery Guarantees in [Message Queues and Async Processing](../11_Message_Queues_and_Async_Processing/). A notification that must not surface twice as a product rule is Delivery Guarantees for Notifications in [Real-Time and Notification Systems](../21_Real_Time_and_Notification_Systems/).
