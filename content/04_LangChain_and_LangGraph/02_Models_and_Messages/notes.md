# Models and Messages

How LangChain wraps the chat-style LLM APIs that every modern provider exposes. Everything else in the framework — prompts, chains, agents, graphs — composes over `BaseChatModel`.

## Key Points

- **Chat, not completion** — modern LLMs take a list of typed messages; the legacy single-string `LLM` interface is deprecated.
- **Message types** — `SystemMessage`, `HumanMessage`, `AIMessage`, `ToolMessage` map directly to provider chat APIs.
- **Provider abstraction** — `ChatOpenAI`, `ChatAnthropic`, etc. share the same `invoke`/`batch`/`stream` API and the same message classes.
- **Configuration** — set `temperature=0` explicitly for reproducibility; cap `max_tokens` and `timeout` to control cost.
- **Streaming** — `.stream()` yields `AIMessageChunk` objects; concat them to recover the full message.
- **Token usage** — `response_metadata` and `usage_metadata` on every `AIMessage`; LangSmith aggregates across traces.
- **Multimodal** — image/audio/document inputs ride on `HumanMessage` as a list of content parts.
- **Caching** — LangChain's LLM cache eliminates duplicate calls; provider-side prompt caching (OpenAI, Anthropic) is cheaper and should be used first.

## Example

Same code, two providers, streaming output, with token usage logged. Swap one import + one model line and the rest of the program is unchanged.

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI


def run(model, prompt: str) -> None:
    messages = [
        SystemMessage("You are a senior software engineer. Be concise."),
        HumanMessage(prompt),
    ]

    # Stream the response token by token
    chunks = []
    for chunk in model.stream(messages):
        chunks.append(chunk)
        print(chunk.content, end="", flush=True)
    print()

    # Concatenate streaming chunks to recover the full message
    full = chunks[0]
    for c in chunks[1:]:
        full = full + c
    print(f"  usage: {full.usage_metadata}")


if __name__ == "__main__":
    gpt = ChatOpenAI(model="gpt-4o-mini", temperature=0, max_tokens=256)
    claude = ChatAnthropic(model="claude-3-5-haiku-latest", temperature=0, max_tokens=256)

    for label, model in [("openai", gpt), ("anthropic", claude)]:
        print(f"--- {label} ---")
        run(model, "Name three things to look for in a code review of a 500-line PR.")
```

Run it and you get two streaming responses with their token counts. To switch providers permanently, replace `gpt` with `claude` (or vice versa) at the bottom — no other code changes. That portability is the value the model abstraction is buying you; the cost is that provider-specific features (vision, JSON mode, prompt caching) still need their own code paths.
