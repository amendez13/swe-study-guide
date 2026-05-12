## Deployment shapes

A LangChain/LangGraph application can be deployed in one of three broad shapes:

1. **Self-hosted FastAPI** — wrap the chain/graph in a FastAPI endpoint, run on your own infrastructure. Maximum control, most ops work.
2. **LangGraph Platform** — LangChain's managed deployment for graphs. Handles persistence, scaling, API surface, streaming.
3. **Container orchestration** — Cloud Run, ECS/Fargate, Kubernetes. Same code as self-hosted FastAPI, hosted by a platform.

Pick by where you already deploy other services. Don't adopt LangGraph Platform just because it exists; don't roll your own infrastructure just because you can.

## Wrapping a chain or graph in FastAPI

The simplest deployment: one FastAPI endpoint that invokes your chain. Streaming is what makes the response feel fast.

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from my_app.chain import chain    # any compiled chain or graph

app = FastAPI()


class AskBody(BaseModel):
    question: str


@app.post("/ask")
async def ask(body: AskBody):
    """Non-streaming: simple but the user waits for the full response."""
    answer = await chain.ainvoke({"question": body.question})
    return {"answer": answer}


@app.post("/ask/stream")
async def ask_stream(body: AskBody):
    """Streaming: token-by-token over an SSE-style response."""
    async def gen():
        async for chunk in chain.astream({"question": body.question}):
            yield chunk

    return StreamingResponse(gen(), media_type="text/event-stream")
```

Production hardening looks the same as any FastAPI service: see [Deployment and Production](../../01_FastAPI/19_Deployment_and_Production/) for workers, reverse proxy, TLS, and managed databases.

## LangGraph Platform

LangChain's managed runtime specifically for compiled `StateGraph`s. You define the graph; the platform handles:

- **Persistence** — `PostgresSaver` checkpointer, managed.
- **API surface** — auto-generated REST endpoints for invoke/stream/get_state/update_state.
- **Streaming** — server-sent events over the API.
- **Assistants** — versioned configurations of the same graph (different prompts, different tools per use case).
- **Scheduling** — cron triggers for scheduled graph runs.

The deal: you write a `langgraph.json` declaring which graph to expose, and the platform handles the rest.

```json
{
  "dependencies": ["."],
  "graphs": {
    "main_agent": "./my_app/graph.py:app"
  },
  "env": ".env"
}
```

Use it when the graph is the product and you don't want to operate a separate FastAPI service.

## Assistants

A LangGraph Platform feature, but useful to understand even if you self-host: an **assistant** is a versioned configuration of a deployed graph. Different prompts, different tools, different models, all addressable by an ID.

```python
# One graph, many assistants
client.assistants.create(
    graph_id="main_agent",
    config={"configurable": {"system_prompt": "You are a billing assistant."}},
    name="billing-v1",
)
client.assistants.create(
    graph_id="main_agent",
    config={"configurable": {"system_prompt": "You are a technical support assistant."}},
    name="tech-v1",
)
```

The graph is the code; the assistant is a particular configuration of that code, versioned independently. This is the LangGraph way to A/B test prompt changes without redeploying the application.

## Streaming over HTTP

Streaming a graph through an HTTP endpoint requires both ends to cooperate:

- **Server** — emit Server-Sent Events (`text/event-stream`) or chunked HTTP responses; flush on every chunk.
- **Client** — read the stream and render chunks as they arrive.

FastAPI's `StreamingResponse` handles the server side cleanly. For the client, the EventSource API in browsers and `httpx` streaming in Python both work.

A common pitfall: a buffering reverse proxy (default nginx behavior) collects the whole response before forwarding, defeating streaming. Set `proxy_buffering off` for the streaming endpoint or use a proxy that's stream-aware (Caddy is by default).

## Connection management

LLM calls and tool calls are I/O-bound. The right runtime model for a LangChain/LangGraph server is async — `async def` endpoints calling `await chain.ainvoke(...)`, with Uvicorn workers.

```bash
uvicorn my_app.api:app --host 0.0.0.0 --port 8000 --workers 4
```

Workers > 1 gives you parallelism across CPU cores. The math is the same as any async Python service: each worker handles many concurrent connections cooperatively; multiple workers handle CPU-bound work in parallel.

## Background graph execution

When a graph might run for minutes (multi-step research, long agent loops), don't make the user wait on the HTTP request. Two patterns:

1. **Background task** — accept the request, return a task ID, run the graph asynchronously. The client polls or reconnects for the result.
2. **Webhook** — accept the request, return immediately, call back to the client when the graph finishes.

LangGraph Platform exposes this as **background runs** — the API has a "start a run, get a thread ID, fetch the result later" mode. With self-hosted FastAPI, you implement it yourself with a task queue (see [Background Tasks](../../01_FastAPI/15_Background_Tasks/)).

## Cost controls

LLM cost discipline is part of deployment, not a separate concern:

- **Per-request budget** — track tokens; abort the graph if cumulative cost exceeds a cap.
- **Per-user rate limits** — protect against abuse and runaway agents.
- **Model fallback** — try the cheap model first; fall back to the expensive one only when needed.
- **Caching** — `set_llm_cache()` for exact-match prompt caching; provider prompt caching for partial reuse.

A single deployed agent can burn through a daily budget in minutes if misconfigured. Bake the controls in at deploy time, not in response to the first surprising bill.

## Secrets handling

Same rules as any production service:

- API keys (OpenAI, Anthropic, LangSmith, Tavily) come from the platform's secret store, not committed `.env` files.
- Don't log secrets — and remember that LangSmith traces capture inputs, so anything you pass through state is in the trace. Redact PII and credentials before they flow into LangSmith.

```python
class Settings(BaseSettings):
    openai_api_key: str          # required at startup
    anthropic_api_key: str
    langsmith_api_key: str
    tavily_api_key: str
```

See [Configuration Management](../../01_FastAPI/12_Configuration_Management/) for the Pydantic-Settings pattern.

## Health endpoints and warm starts

A LangChain/LangGraph service needs the same operational scaffolding as any FastAPI service:

- **`/health`** — cheap liveness check (just returns `{"ok": true}`).
- **`/ready`** — readiness check that exercises one dependency (e.g., a trivial LLM call) — proves the service can serve before the load balancer routes to it.
- **Lifespan startup** — eagerly initialize connection pools, load embeddings models, connect to LangSmith. Otherwise the first request pays the full warm-up cost.

```python
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Warm up at startup
    await chain.ainvoke({"question": "hi"})
    yield
    # Cleanup if needed
```

The first request to a cold container can be 5–10 seconds slower than steady-state; lifespan warm-up amortizes that into deploy time instead of user wait time.
