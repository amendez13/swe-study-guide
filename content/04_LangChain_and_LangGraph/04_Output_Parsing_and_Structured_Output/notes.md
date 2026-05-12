# Output Parsing and Structured Output

The model emits a string; your code wants typed data. How to bridge that without trusting f-string-shaped JSON parsing in production.

## Key Points

- **Three approaches, ranked** — text parsing (don't), `OutputParser` (acceptable), `with_structured_output()` (the modern default).
- **`StrOutputParser`** — collapses `AIMessage` to `str`; almost every text chain ends with this.
- **`JsonOutputParser`** — text-based JSON parsing with format-instruction injection; handles markdown fences and prose.
- **`PydanticOutputParser`** — same idea, returns a validated Pydantic instance instead of a dict.
- **`with_structured_output()`** — wraps the model with function calling so the response is a validated Pydantic instance natively; no parsing failures, no format instructions.
- **Pydantic as the shared schema** — the same model class serves as output shape, tool argument schema, API response model, and DB mapping.
- **`OutputFixingParser` / `RetryWithErrorOutputParser`** — recovery wrappers for parser-based flows; mostly unneeded once you're on `with_structured_output()`.
- **When NOT to use structured output** — streaming text to a user, open-ended generation, plain-text outputs like translation.

## Example

A single extraction task implemented three ways — text parsing, `JsonOutputParser`, and `with_structured_output()` — so you can compare them side by side.

```python
import json
from typing import Literal

from langchain_core.output_parsers import JsonOutputParser, PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

# Shared schema
class Entity(BaseModel):
    name: str = Field(description="The entity's name")
    type: Literal["person", "org", "place"]


class Extraction(BaseModel):
    entities: list[Entity]


model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
TEXT = "Alice works at Acme Corp in Berlin alongside Bob."


# --- 1. Raw text + manual parsing (don't ship this) ---
def extract_manual() -> Extraction:
    prompt = (
        f"Extract entities from: {TEXT}. "
        f"Respond with JSON: {{'entities': [{{'name': ..., 'type': person|org|place}}]}}"
    )
    raw = model.invoke(prompt).content
    # ... strip markdown fences ... handle prose ... pray
    return Extraction.model_validate(json.loads(raw))


# --- 2. JsonOutputParser — better but still text-based ---
def extract_json_parser() -> Extraction:
    parser = PydanticOutputParser(pydantic_object=Extraction)
    prompt = ChatPromptTemplate.from_template(
        "Extract entities: {text}\n\n{format_instructions}"
    ).partial(format_instructions=parser.get_format_instructions())
    chain = prompt | model | parser
    return chain.invoke({"text": TEXT})


# --- 3. with_structured_output — the modern default ---
def extract_structured() -> Extraction:
    extractor = model.with_structured_output(Extraction)
    return extractor.invoke(
        f"Extract entities from: {TEXT}"
    )


if __name__ == "__main__":
    for name, fn in [
        ("manual",     extract_manual),
        ("json_parser", extract_json_parser),
        ("structured", extract_structured),
    ]:
        try:
            result = fn()
            print(f"{name:12} → {[e.name for e in result.entities]}")
        except Exception as exc:
            print(f"{name:12} → FAILED: {exc}")
```

All three approaches produce the same `Extraction` object when they succeed. The difference is failure modes: option 1 fails roughly 5–15% of the time depending on the model and prompt; option 2 cuts that to ~1–3% with format instructions; option 3 essentially can't fail at the parsing layer because the provider enforces the schema before the response is returned.

In new code, default to option 3. Use option 2 when the provider doesn't support function calling (some local models, some less mainstream APIs). Never ship option 1.
