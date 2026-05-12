## Why structured output

The model returns a string. Your code wants typed data — a `bool`, a list of records, a Pydantic instance. Bridging that gap is the difference between "demo that works on the slides" and a production system.

Three approaches, in increasing order of preference:

1. **Text parsing** — ask the model for JSON in the prompt, parse the response yourself. Brittle.
2. **`OutputParser`** — LangChain's parser layer, with format-instruction injection and retry logic. Better, but still text-based.
3. **`with_structured_output()`** — the modern, native approach using the provider's function-calling primitive. Validated by Pydantic; no parsing failure modes. Use this when the provider supports it.

## `StrOutputParser`

Turns an `AIMessage` into a plain `str`. Almost every chain ends with this when you want text out; without it the chain yields an `AIMessage` and callers have to remember to access `.content`.

```python
from langchain_core.output_parsers import StrOutputParser

chain = prompt | model | StrOutputParser()
text: str = chain.invoke({"topic": "Python"})
```

It's a trivial transformation, but it's the right boundary — once you're past the parser, downstream code doesn't need to know it's talking to an LLM.

## `JsonOutputParser`

Asks the model to produce JSON, then parses it. The parser supplies "format instructions" you splice into the prompt so the model knows what shape you want.

```python
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate

parser = JsonOutputParser()
prompt = ChatPromptTemplate.from_template(
    "Extract entities from: {text}\n\n{format_instructions}"
).partial(format_instructions=parser.get_format_instructions())

chain = prompt | model | parser
result: dict = chain.invoke({"text": "Alice works at Acme in Berlin."})
```

Strictly better than asking for JSON in the prompt by hand — the format instructions are battle-tested and `JsonOutputParser` handles common failure modes (markdown code fences, trailing prose).

## `PydanticOutputParser`

The same idea, but the output shape is a Pydantic model and the parser returns an instance — validated, typed, IDE-friendly.

```python
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser

class Entity(BaseModel):
    name: str
    type: str = Field(description="person, org, or place")

class Extraction(BaseModel):
    entities: list[Entity]

parser = PydanticOutputParser(pydantic_object=Extraction)
prompt = ChatPromptTemplate.from_template(
    "Extract entities: {text}\n\n{format_instructions}"
).partial(format_instructions=parser.get_format_instructions())

chain = prompt | model | parser
result: Extraction = chain.invoke({"text": "Alice works at Acme in Berlin."})
```

The Pydantic schema flows into the prompt as a JSON Schema; the parser validates the response against it; you get type errors at parse time, not at the call site.

## `with_structured_output()` — the modern approach

Skip the text-parsing dance entirely. Modern providers expose **function calling**, which forces the model to emit a JSON object matching a declared schema. `with_structured_output()` wraps the model call with this and returns a validated Pydantic instance directly.

```python
from pydantic import BaseModel
from langchain_openai import ChatOpenAI

class Extraction(BaseModel):
    entities: list[Entity]

model = ChatOpenAI(model="gpt-4o-mini").with_structured_output(Extraction)

result: Extraction = model.invoke("Extract entities from: Alice works at Acme in Berlin.")
```

No format instructions in the prompt, no parser failures, no markdown fences to strip. This is the default for any new code; reach for parsers only when the provider doesn't support structured output.

## Pydantic schemas as the contract

The same Pydantic class can serve as: the model's output schema (`with_structured_output`), a tool's input schema (`@tool`), the API response model (a FastAPI `response_model`), the database row mapping, and the in-code type.

```python
class Entity(BaseModel):
    name: str = Field(description="The entity's name")
    type: Literal["person", "org", "place"]
    confidence: float = Field(ge=0, le=1)
```

`description` and `Field(...)` constraints flow into the JSON Schema the model sees, so it's documentation and validation in one place. Get the schema right once and every consumer benefits.

## Retry and error handling

When parsing fails (the model emits invalid JSON, omits a required field), there are two clean recovery patterns:

- **`OutputFixingParser`** wraps another parser; on failure it calls the LLM again with the original output and the error, asking it to fix the format. Cheap and effective.
- **`RetryWithErrorOutputParser`** retries the original prompt with the error feedback. More expensive (re-runs the whole call) but catches deeper failures.

```python
from langchain.output_parsers import OutputFixingParser

base = PydanticOutputParser(pydantic_object=Extraction)
parser = OutputFixingParser.from_llm(parser=base, llm=model)
```

With `with_structured_output()` you mostly don't need these — function calling can't emit a malformed schema. They're a safety net for the parser-based path.

## When structured output isn't what you want

Three cases where a plain string is the right answer:

1. **Streaming text to a user** — chat UIs, generated prose; you want tokens, not a final object.
2. **Open-ended generation** — summarization, ideation; forcing a schema constrains creativity.
3. **The output IS unstructured text** — translations, rephrasings.

For everything else (extraction, classification, decisions, tool argument generation, routing), structured output is the right default.
