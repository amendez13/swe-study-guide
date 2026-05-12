# Deployment

The shape of a production LangChain/LangGraph service. The LLM-specific parts are streaming, cost controls, and long-running graphs; everything else is normal FastAPI deployment.

## Key Points

- **Three deployment shapes** — self-hosted FastAPI, LangGraph Platform, container orchestration.
- **FastAPI wrapping** — one endpoint for sync `/ask`, one streaming endpoint for token output.
- **LangGraph Platform** — managed runtime with persistence, API, streaming, assistants, scheduling baked in.
- **Assistants** — versioned configurations of one deployed graph (different prompts, models, tools).
- **Streaming over HTTP** — Server-Sent Events; turn off proxy buffering for stream-aware proxies.
- **Async + workers** — `async def` endpoints, Uvicorn with multiple workers.
- **Background runs** — for long-running graphs, return a task ID and let the client poll/webhook.
- **Cost controls** — per-request budget, rate limits, model fallback, caching.
- **Secrets and tracing** — LangSmith traces capture state; redact PII before it flows in.
- **Health and warm-up** — `/health`, `/ready`, lifespan warm-up to avoid cold-start surprises.

## Example

A production-shaped FastAPI service that exposes a LangGraph agent with both blocking and streaming endpoints, a background-run pattern for long tasks, structured cost limits, and proper warm-up.

```python
import asyncio
import uuid
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Annotated, TypedDict


# --- Settings ---
class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="APP_")
    openai_api_key: str
    langsmith_api_key: str | None = None
    langsmith_project: str = "production"
    cost_cap_tokens: int = 50_000        # per-task budget


settings = Settings()


# --- Graph ---
class State(TypedDict):
    messages: Annotated[list, add_messages]


model = ChatOpenAI(model="gpt-4o-mini", temperature=0, openai_api_key=settings.openai_api_key)


def chat_node(state: State) -> dict:
    return {"messages": [model.invoke(state["messages"])]}


graph = StateGraph(State)
graph.add_node("chat", chat_node)
graph.add_edge(START, "chat")
graph.add_edge("chat", END)

checkpointer = MemorySaver()        # production: PostgresSaver(DATABASE_URL)
agent = graph.compile(checkpointer=checkpointer)


# --- Background-run store ---
# In production this is a database table; in-memory dict is for the example.
class RunStatus(BaseModel):
    status: str             # "running" | "done" | "error"
    result: Any | None = None
    error: str | None = None


runs: dict[str, RunStatus] = {}


# --- Lifespan: warm up the chain at startup ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # First call pays the cold-start cost; subsequent requests are fast.
    print("Warming up the agent...")
    await agent.ainvoke(
        {"messages": [HumanMessage("hi")]},
        config={"configurable": {"thread_id": "__warmup__"}},
    )
    print("Ready.")
    yield


app = FastAPI(lifespan=lifespan)


# --- Schemas ---
class AskBody(BaseModel):
    question: str
    thread_id: str | None = None


# --- Endpoints ---
@app.get("/health")
async def health():
    return {"ok": True}


@app.get("/ready")
async def ready():
    """Exercise the agent so the load balancer only routes here when it works."""
    try:
        await agent.ainvoke(
            {"messages": [HumanMessage("ping")]},
            config={"configurable": {"thread_id": "__ready__"}},
        )
    except Exception as e:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, str(e))
    return {"ok": True}


@app.post("/ask")
async def ask(body: AskBody):
    """Blocking; for short prompts where streaming UX isn't needed."""
    config = {"configurable": {"thread_id": body.thread_id or str(uuid.uuid4())}}
    result = await agent.ainvoke({"messages": [HumanMessage(body.question)]}, config=config)
    return {"answer": result["messages"][-1].content, "thread_id": config["configurable"]["thread_id"]}


@app.post("/ask/stream")
async def ask_stream(body: AskBody):
    """Stream tokens as they're generated."""
    config = {"configurable": {"thread_id": body.thread_id or str(uuid.uuid4())}}

    async def gen():
        async for mode, payload in agent.astream(
            {"messages": [HumanMessage(body.question)]},
            config=config,
            stream_mode=["messages"],
        ):
            chunk, metadata = payload
            if metadata.get("langgraph_node") == "chat":
                content = chunk.content or ""
                if content:
                    yield f"data: {content}\n\n"

    return StreamingResponse(gen(), media_type="text/event-stream")


# --- Background run pattern (for long-running graphs) ---
async def _run_in_background(run_id: str, body: AskBody) -> None:
    try:
        config = {"configurable": {"thread_id": body.thread_id or run_id}}
        result = await agent.ainvoke({"messages": [HumanMessage(body.question)]}, config=config)
        runs[run_id] = RunStatus(status="done", result=result["messages"][-1].content)
    except Exception as e:
        runs[run_id] = RunStatus(status="error", error=str(e))


@app.post("/ask/background")
async def ask_background(body: AskBody):
    """For long graphs — return a run_id, client polls /runs/{run_id}."""
    run_id = str(uuid.uuid4())
    runs[run_id] = RunStatus(status="running")
    asyncio.create_task(_run_in_background(run_id, body))
    return {"run_id": run_id}


@app.get("/runs/{run_id}")
async def get_run(run_id: str):
    run = runs.get(run_id)
    if run is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "no such run")
    return run
```

Running it:

```bash
# Dev
uvicorn my_app.api:app --reload

# Production
uvicorn my_app.api:app --host 0.0.0.0 --port 8000 --workers 4 --proxy-headers
```

Behavior:

- **`GET /health`** — instant, no LLM call. Use for load balancer liveness checks.
- **`GET /ready`** — exercises the agent. Use for readiness/canary checks before routing traffic.
- **`POST /ask`** — blocking; the client waits for the full response. Fine for short prompts.
- **`POST /ask/stream`** — Server-Sent Events with token-level output. What chat UIs use.
- **`POST /ask/background`** — for graphs that might take a minute or longer; returns immediately with a `run_id`. The client polls `/runs/{run_id}` until status is `done`.
- **Lifespan warm-up** — runs once at startup so the first user request isn't 5 seconds slower than the rest.

For real production, swap `MemorySaver` for `PostgresSaver`, swap the in-memory `runs` dict for a database table, and put a reverse proxy (Caddy or nginx with `proxy_buffering off` for the stream endpoint) in front. The shape of the application code doesn't change.
