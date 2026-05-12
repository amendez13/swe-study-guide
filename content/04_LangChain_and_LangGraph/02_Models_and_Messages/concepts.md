## Chat models vs completion models

Modern LLM APIs are **chat models** — they take a list of typed messages, not a single prompt string. Completion-style APIs (one string in, one string out) are legacy; every current frontier provider exposes chat. LangChain mirrors this distinction with `BaseChatModel` (the modern interface) and the now-deprecated `LLM` interface.

The chat shape matters because every interesting feature — system instructions, multi-turn conversations, tool calling, multimodal input — needs message metadata that a single string can't carry.

## Message types

LangChain's typed message classes mirror the chat-API standard:

- **`SystemMessage`** — role and instructions ("You are a helpful assistant…"). Usually first; usually one per conversation.
- **`HumanMessage`** — what the user said.
- **`AIMessage`** — what the model said. Carries `content`, optional `tool_calls`, and `usage_metadata` (token counts).
- **`ToolMessage`** — the output of a tool the model invoked, replied to a specific `tool_call_id`.
- **`AIMessageChunk`** — the streaming variant of `AIMessage`; chunks concatenate.

```python
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

response = model.invoke([
    SystemMessage("You translate English to French."),
    HumanMessage("Hello, world!"),
])
# response is an AIMessage
print(response.content)
```

## Provider abstraction

`ChatOpenAI`, `ChatAnthropic`, `ChatGoogleGenerativeAI`, `ChatOllama`, `ChatMistralAI`, etc. all subclass `BaseChatModel`. Same `.invoke()`, `.stream()`, `.batch()` API; same message classes; same response shape. This is the layer that lets you swap models without rewriting the rest of your code.

```python
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

# Identical interface, different provider
gpt = ChatOpenAI(model="gpt-4o-mini")
claude = ChatAnthropic(model="claude-3-5-haiku-latest")

for model in (gpt, claude):
    print(model.invoke("In one word, what's Python?"))
```

Provider-specific quirks (vision support, JSON mode, prompt caching, max tokens) still need provider-specific code; the abstraction covers the common surface, not every feature.

## Model configuration

Every chat model accepts the standard LLM knobs at construction:

- **`model`** — the model ID (`gpt-4o-mini`, `claude-3-5-sonnet-latest`). Required.
- **`temperature`** — randomness (0 = deterministic, 1 = creative). Lower for extraction/classification, higher for brainstorming.
- **`max_tokens`** — cap the response length. Defends against runaway costs.
- **`timeout`** — per-call timeout in seconds.
- **`max_retries`** — automatic retry count on transient failures.

```python
model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
    max_tokens=512,
    timeout=30,
    max_retries=2,
)
```

Don't leave temperature unset; the default varies by provider and a non-zero default is a source of flakiness in tests.

## Streaming

Every chat model supports `.stream()` (sync) and `.astream()` (async). They yield `AIMessageChunk` objects whose `.content` is a fragment of the final response; concatenating them recovers the full message.

```python
for chunk in model.stream("Write a haiku about Python."):
    print(chunk.content, end="", flush=True)
```

Streaming matters for UX (the user sees text appear word by word) and for cancellation (you can stop the stream as soon as you have what you need).

## Token usage and cost

Every `AIMessage` carries `response_metadata` with the model name, finish reason, and provider-specific details, plus `usage_metadata` with `input_tokens`, `output_tokens`, and `total_tokens`.

```python
r = model.invoke("Hi")
print(r.usage_metadata)
# {'input_tokens': 8, 'output_tokens': 6, 'total_tokens': 14}
```

Multiply by the provider's per-token price to get the cost of the call. LangSmith aggregates this across an entire trace so you can see what a request actually cost end-to-end.

Cost discipline starts here: a chain with three model calls costs three times as much as one call, and an agent loop with ten iterations costs ten times. Pick smaller/cheaper models where they suffice.

## Multimodal input

Frontier models accept images, audio, and PDFs alongside text. In LangChain, multimodal content rides on `HumanMessage` as a list of content parts instead of a string:

```python
from langchain_core.messages import HumanMessage

response = model.invoke([
    HumanMessage(content=[
        {"type": "text", "text": "What's in this image?"},
        {"type": "image_url", "image_url": {"url": "https://example.com/cat.jpg"}},
    ]),
])
```

Provider support varies — check the model's docs for what `type` values it accepts (`image_url`, `image`, `input_audio`, `document`). The interface is uniform; the capabilities aren't.

## Caching

Repeated identical calls are the easiest cost to eliminate. LangChain ships an LLM cache (`InMemoryCache`, `SQLiteCache`, `RedisCache`) that short-circuits matching prompts.

```python
from langchain_community.cache import SQLiteCache
from langchain_core.globals import set_llm_cache

set_llm_cache(SQLiteCache(database_path=".langchain.db"))

# Identical .invoke() calls hit the cache after the first
```

Two caveats: temperature must be 0 for caching to be safe (else you're returning yesterday's "random" answer), and a cache hit is only as good as your key — small prompt edits invalidate it. Also: most modern providers (OpenAI, Anthropic) ship **prompt caching** of their own that you should use first; it caches the prefix at the provider's side and is cheaper.
