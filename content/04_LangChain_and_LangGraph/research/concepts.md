# LangChain and LangGraph Concepts

A distilled concept reference for a student of LangChain and LangGraph, synthesized from the five course outlines in [course_outlines.md](course_outlines.md). Each item names a concept worth being able to explain, recognize in code, and apply in practice. Generic Python / API basics and course-specific project names are excluded — the focus is on durable LLM-orchestration knowledge.

---

## 1. LLM Application Stack

- **Why a framework at all** — wiring an LLM into a real application means prompt management, output parsing, memory, retrieval, tool use, branching, observability, and deployment. LangChain and LangGraph give you primitives for each instead of leaving you to glue them together.
- **LangChain vs LangGraph vs LangSmith** — LangChain is the primitives library (models, prompts, retrievers, tools); LangGraph is the orchestration layer (stateful graphs, agents); LangSmith is the observability layer (tracing, evaluation, monitoring). Same vendor, distinct concerns.
- **The ecosystem split (v1+)** — LangChain v1 reorganized into smaller packages: `langchain-core` (interfaces), `langchain` (the standard library), `langchain-community` (third-party integrations), `langchain-openai` / `langchain-anthropic` / etc. (provider-specific). Pin them coherently.
- **When LangChain isn't the answer** — for a single LLM call with a fixed prompt, the provider's SDK is simpler. Reach for LangChain when you have composition, retrieval, or tool use; reach for LangGraph when you have branching, loops, or human-in-the-loop.

## 2. Models and Messages

- **Chat models vs completion models** — modern LLMs are chat models that take a list of typed messages (`SystemMessage`, `HumanMessage`, `AIMessage`, `ToolMessage`). LangChain's `BaseChatModel` is the common interface.
- **Provider abstraction** — `ChatOpenAI`, `ChatAnthropic`, `ChatGoogleGenerativeAI`, `ChatOllama`, etc. expose the same interface, so you can swap providers without rewriting the application.
- **Streaming** — every chat model supports `.stream()` and `.astream()`; intermediate tokens arrive as `AIMessageChunk` objects you can concatenate or forward to the client.
- **Token usage and cost** — track `response_metadata["token_usage"]` per call; LangSmith aggregates it across a trace. Cost discipline starts at the model layer.

## 3. Prompts

- **Prompt templates** — `PromptTemplate` and `ChatPromptTemplate` declare a prompt with named variables that get filled at runtime. Keep prompts out of f-strings scattered through your code.
- **Few-shot prompting** — `FewShotPromptTemplate` injects example input/output pairs into the prompt; effective when the task is hard to describe but easy to demonstrate.
- **Prompt hub** — LangSmith hosts a public prompt registry (`prompts.langchain.com`); pull a versioned, community-vetted prompt instead of writing your own from scratch.
- **System vs user prompts** — system prompts set the role and rules ("You are a helpful assistant…"); user prompts carry the task. Many failures are prompts in the wrong slot.

## 4. Output Parsing and Structured Output

- **Output parsers** — `StrOutputParser`, `JsonOutputParser`, `PydanticOutputParser`. Coerce LLM text into the shape your code wants, with retry logic when parsing fails.
- **`with_structured_output()`** — the modern, model-native way to get typed responses. Pass a Pydantic class or JSON schema; the model returns a validated instance via its function-calling primitive. Prefer this over text parsers when the provider supports it.
- **Pydantic schemas as the contract** — defining the shape of LLM output as a Pydantic model gives you validation, IDE autocomplete, and a JSON schema that flows into prompts and tool definitions.

## 5. LangChain Expression Language (LCEL)

- **`Runnable` interface** — every LangChain primitive (model, prompt, parser, retriever, tool) implements `Runnable`, which means it has `.invoke()`, `.batch()`, `.stream()`, and their async counterparts.
- **Composition with `|`** — the pipe operator composes runnables into a chain: `prompt | model | parser`. The output type of each stage must match the input type of the next.
- **`RunnablePassthrough` and `RunnableParallel`** — pass inputs through unchanged or fan out to multiple parallel runnables. The building blocks for non-linear chains.
- **`RunnableLambda`** — wrap any function in the Runnable interface so it can participate in a pipeline.
- **Async, batch, and streaming for free** — building blocks expose `.ainvoke`, `.abatch`, `.astream`; any composed chain inherits them. You don't write the concurrency.

## 6. Memory

- **Why memory** — LLMs are stateless between calls. To carry a conversation forward, you reinject prior turns into the prompt — that's what "memory" means here.
- **Buffer memory** — stores the full transcript; simple, but the prompt grows unboundedly with the conversation.
- **Window memory** — keeps the last N turns; constant prompt size, loses old context.
- **Summary memory** — periodically summarizes older turns into a single message; preserves gist, loses detail.
- **Vector-store memory** — embeds past turns and retrieves the relevant ones per query; scales to long conversations at the cost of complexity.
- **LangGraph short-term vs long-term memory** — short-term memory is per-thread state in the graph; long-term memory is shared across threads via the `LangGraph Store`.

## 7. Retrieval-Augmented Generation (RAG)

- **The RAG pipeline** — load → split → embed → store → retrieve → augment → generate. Each stage has a named LangChain primitive.
- **Document loaders** — `WebBaseLoader`, `PyPDFLoader`, `DirectoryLoader`, `NotionDBLoader`, etc.; produce `Document` objects with `page_content` and `metadata`.
- **Text splitters** — `RecursiveCharacterTextSplitter` is the default; respects paragraph/sentence boundaries. Chunk size and overlap are tuning knobs.
- **Embeddings** — `OpenAIEmbeddings`, `CohereEmbeddings`, `HuggingFaceEmbeddings`. Two documents with similar meaning produce similar vectors.
- **Vector stores** — `Chroma`, `Pinecone`, `Weaviate`, `FAISS`, `pgvector`. The persistence layer for embeddings + retrieval.
- **Retrievers** — wrap a vector store with retrieval logic. Variants: similarity, MMR (max marginal relevance), self-querying (LLM rewrites the query), contextual compression.
- **Retrieval chains** — `create_retrieval_chain`, `RetrievalQA`. The standard composition: retrieve → stuff into prompt → generate.
- **Agentic RAG** — RAG embedded in an agent loop with query rewriting, relevance grading, and hallucination grading; the agent retries when retrieval is bad.

## 8. Tools and Tool Calling

- **What a "tool" is** — a callable with a name, description, and JSON schema for its arguments. The LLM picks a tool by emitting a structured tool call; your code executes it; the result feeds back as a `ToolMessage`.
- **`@tool` decorator** — wraps a Python function as a `BaseTool`. The function signature and docstring become the tool's schema and description.
- **Built-in toolkits** — search (Tavily, SerpAPI), web scraping, SQL, code interpreters, file system, calendar, email. Bundles of related tools mounted as a unit.
- **Function calling vs JSON mode vs ReAct text parsing** — modern providers expose native function/tool calling; older approaches parse tool calls out of the model's text (ReAct). Prefer native when available.

## 9. The ReAct Loop

- **Reason + Act, alternating** — the classic agent loop: think (LLM emits a reasoning trace), act (LLM picks a tool), observe (run the tool, feed the result back), repeat until the model emits a final answer.
- **`create_react_agent`** — the canonical helper for building a ReAct agent over a list of tools. Hides the loop; exposes the agent as a `Runnable`.
- **When ReAct fails** — infinite loops, tool-call hallucinations, premature finalization. Most production agents need explicit guardrails on the loop: max iterations, validation of tool outputs, fallbacks.

## 10. Agents

- **Agent vs chain** — a chain runs a fixed sequence; an agent decides the sequence at runtime by picking among tools. Use a chain when the steps are known; use an agent when they aren't.
- **Agent prompt structure** — the system prompt describes the role, lists the tools, and gives instructions; the user prompt is the task. The agent loops until it produces a final answer.
- **AgentExecutor (legacy)** — the v0.x API for running an agent loop. Largely superseded by LangGraph's `create_react_agent` in v1+.
- **Cost and latency reality** — agents call the LLM many times per task. A 5-step agent is 5× the cost and latency of a one-shot call. Choose agents deliberately.

## 11. LangGraph Fundamentals

- **Stateful graph model** — LangGraph models an application as a graph of nodes that read from and write to a shared state object. Cyclic graphs are first-class, which is what makes agent loops natural to express.
- **`StateGraph` and `MessageGraph`** — the two main graph classes. `StateGraph` works with arbitrary typed state (Pydantic, TypedDict); `MessageGraph` is a shortcut for conversational state.
- **Nodes** — pure functions (or `Runnable`s) from `State → State`. A node's signature is `def node(state: State) -> dict`; the returned dict is merged into state via reducers.
- **Edges** — connect nodes. **Regular edges** always traverse from A to B; **conditional edges** call a function on state to pick the next node dynamically.
- **`START` and `END`** — sentinel nodes that mark graph entry and exit. Every graph has at least one edge from `START` and at least one to `END`.

## 12. State and Reducers

- **State schema** — a `TypedDict` or Pydantic class describing the keys carried through the graph. Each node returns updates that get merged into this schema.
- **Reducers** — functions that combine the existing value of a key with the node's update. Default is "replace"; `add_messages` appends to a message list; you can write custom reducers for sets, counters, etc.
- **Annotated types for reducers** — declare reducers in the schema: `messages: Annotated[list, add_messages]`. The graph picks them up automatically.
- **Multiple schemas** — input state, output state, and internal state can differ. Hide intermediate fields from the API surface this way.

## 13. Control Flow

- **Conditional edges** — `add_conditional_edges(node, router_fn, mapping)`. The router function returns a key from the mapping, picking the next node based on state.
- **Loops** — conditional edges that point back to an earlier node give you a loop. The classic ReAct loop is two nodes (agent ↔ tools) with a conditional edge that exits when the agent emits a final answer.
- **Parallelization** — multiple edges from a single node fan out; the named nodes execute concurrently and their results merge back into state. The standard pattern for "run these N retrievers in parallel."
- **Sub-graphs** — compile a `StateGraph` and use it as a node inside another graph. Encapsulation for complex sub-workflows.
- **Map-reduce** — fan out one input to many parallel calls (map), then collapse the results into a single output (reduce). LangGraph expresses this with `Send` objects.

## 14. Persistence and Checkpointers

- **Why persistence** — without it, a graph forgets everything between invocations; conversations and long-running workflows can't survive a restart.
- **Checkpointers** — save the full graph state after each step under a `thread_id`. Resuming with the same thread ID continues from where you left off.
- **In-memory, SQLite, Postgres checkpointers** — `MemorySaver` for dev/tests, `SqliteSaver` for single-machine, `PostgresSaver` for production multi-instance.
- **Threads** — a thread ID groups together a conversation (or a long-running task) across multiple invocations. Same thread = same memory; different thread = fresh start.

## 15. Streaming

- **What streams from a graph** — three things: token-level streams from the LLM, intermediate step events (which node ran, what it returned), and state updates. Different consumers want different streams.
- **`.stream()` modes** — `"updates"` (state diffs per step), `"values"` (full state per step), `"messages"` (LLM token stream). Pick based on what the UI needs.
- **Astream events** — `astream_events(version="v2")` emits a fine-grained event stream useful for instrumenting any LangGraph application without modifying its nodes.

## 16. Human-in-the-Loop

- **Why HITL** — agentic systems make mistakes; for high-stakes actions (sending email, executing trades, modifying production data) a human review step is the difference between a useful agent and a dangerous one.
- **Breakpoints** — pause the graph before a specific node. The graph's state is checkpointed and a human can inspect, approve, or modify before resumption.
- **Editing state** — between breakpoint and resumption, the human can change state values; the resumed run sees the edited state.
- **Dynamic breakpoints** — pause conditionally based on state (e.g., "only ask for approval if the transaction exceeds $1000").
- **Time travel** — rewind to an earlier checkpoint and resume from there with different state or different tool outputs; lets you debug interactively.

## 17. Self-Improving Agent Patterns

- **Reflection** — a generator node produces output; a separate reflector node critiques it; the generator revises. Two-node loop in LangGraph.
- **Reflexion** — reflection plus structured external knowledge; the agent records what went wrong and uses it on the next attempt. Often grounded in citations.
- **ReAct** — Reason + Act, the canonical "think then act" loop. The simplest self-improving pattern; later approaches build on it.
- **When self-improvement helps** — open-ended generation (essays, code), retrieval where the first attempt might miss, multi-step reasoning. Less useful for one-shot factual queries.

## 18. Multi-Agent Systems

- **Why multiple agents** — one prompt and one tool list can't handle every domain. Splitting concerns (researcher, writer, reviewer) is the same logic that motivates microservices: smaller surfaces, clearer responsibilities.
- **Supervisor pattern** — a top-level agent routes work to specialist sub-agents and aggregates their results. The most common multi-agent topology.
- **Hierarchical teams** — supervisors all the way down; each sub-agent can itself be a supervisor of finer-grained agents.
- **Swarm / peer-to-peer** — agents talk to each other without a supervisor; harder to control, occasionally appropriate for collaborative or adversarial scenarios.
- **Risks** — autonomous multi-agent systems amplify single-agent failure modes (hallucination, loops, prompt injection) by every agent added. Match the topology to actual coordination needs, not to the demo.

## 19. LangSmith Observability

- **Tracing** — every LangChain/LangGraph invocation produces a hierarchical trace: which prompts, which models, which tools, in which order, with which latency. Enabled by `LANGSMITH_TRACING=true`.
- **Datasets** — collections of input/output pairs used as test fixtures. Promote real production traces into datasets to grow your evaluation suite.
- **Evaluators** — run a function against every dataset row to grade output. LLM-as-judge evaluators score generation quality; deterministic evaluators score structured-output correctness.
- **Experiments** — run a chain over a dataset with different prompts/models/parameters; LangSmith diffs the results so you can pick the winning variant.
- **Production monitoring** — latency, cost, error rate, and custom evaluator scores in a dashboard; alerts on regression.

## 20. Deployment

- **LangGraph Cloud / LangGraph Platform** — LangChain's managed deployment for graphs; handles persistence, scaling, the API surface, and Assistants out of the box.
- **Self-host** — wrap the graph in a FastAPI endpoint, run on your own infrastructure. More work; full control.
- **Assistants** — versioned configurations of a deployed graph (different prompts, different tools, different models) addressable by ID. The platform pattern for parameterizing one graph across many use cases.
- **Double-texting** — what to do when a new message arrives while the graph is still processing the previous one. Options: queue, interrupt and replace, run in parallel, reject. The deployment layer handles the policy.

## 21. Security and Safety

- **Prompt injection** — untrusted content (search results, documents, tool outputs) reaching the LLM can override your system prompt. Treat all retrieved/external text as adversarial; isolate it with delimiters and instructions.
- **Tool sandboxing** — code-execution tools (Python REPL, shell, filesystem) need real sandboxes (containers, restricted execution environments), not just prompt-level guardrails.
- **Output validation** — LLMs lie; never trust their output for high-stakes decisions without external verification (a database lookup, a deterministic checker, a human).
- **Secrets handling** — model API keys, vector store credentials, tool integrations all need the same hygiene as any other secret. Same rules as in [Configuration Management](../../01_FastAPI/12_Configuration_Management/) — env vars, no commits.

---

## How to use this list

This isn't a syllabus — it's a self-check. Pick any concept and ask:

1. Can I explain what it is in two sentences without looking it up?
2. Can I recognize it in unfamiliar LangChain/LangGraph code?
3. Can I write a small example that uses it correctly?

A "no" on any of those three is a topic to study next.
