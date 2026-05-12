## Prompts as code, not strings

The simplest mistake in LLM applications is scattering prompt strings across the codebase as f-strings. Prompts are the contract with the model — they deserve the same treatment as SQL queries or API schemas: declared once, parameterized, versioned.

LangChain's `PromptTemplate` and `ChatPromptTemplate` are the declarative layer. They name the variables, separate role from content, validate that the inputs match, and produce typed message lists ready to pass to a model.

## `ChatPromptTemplate`

The standard prompt class for chat models. Declares a list of `(role, content)` pairs with `{variable}` placeholders that get filled at invoke time.

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a {style} writing assistant."),
    ("user", "Rewrite this sentence: {sentence}"),
])

messages = prompt.format_messages(style="concise", sentence="The quick brown fox jumps.")
```

`format_messages()` returns a `list[BaseMessage]` ready to invoke. In a chain, you don't call it directly — the `|` operator passes the dict downstream and the template fills itself.

## `PromptTemplate`

The flat-string equivalent for the rare cases where you're calling a completion-style endpoint or building a sub-prompt that will be embedded in another message.

```python
from langchain_core.prompts import PromptTemplate

template = PromptTemplate.from_template("Translate {text} into {language}.")
filled = template.format(text="hello", language="French")
```

You'll reach for `ChatPromptTemplate` 95% of the time; this exists for the other 5%.

## `MessagesPlaceholder`

A slot in a chat prompt that gets filled with **an entire list of messages** at runtime, not a string. This is how you splice in conversation history or few-shot examples:

```python
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder("history"),     # ← conversation so far
    ("user", "{question}"),
])

prompt.invoke({
    "history": [HumanMessage("What's 2+2?"), AIMessage("4.")],
    "question": "What's 2+3?",
})
```

`MessagesPlaceholder` is what makes multi-turn chat and memory possible without string-concatenating the conversation by hand.

## Few-shot prompting

When a task is hard to describe but easy to demonstrate, give the model examples. `FewShotChatMessagePromptTemplate` formats a list of input/output pairs into the prompt automatically.

```python
from langchain_core.prompts import (
    ChatPromptTemplate, FewShotChatMessagePromptTemplate,
)

example_prompt = ChatPromptTemplate.from_messages([
    ("user", "{input}"),
    ("assistant", "{output}"),
])

few_shot = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    examples=[
        {"input": "happy", "output": "😀"},
        {"input": "sad", "output": "😢"},
        {"input": "confused", "output": "😕"},
    ],
)

final = ChatPromptTemplate.from_messages([
    ("system", "Map words to a single emoji."),
    few_shot,
    ("user", "{word}"),
])
```

For large example pools, use `ExampleSelector` (semantic, length-based, n-gram similarity) to pick the most relevant examples per query instead of always sending all of them.

## Partial prompts

When some variables are known at construction time and others at invoke time, "partial" the template to fill in the constants:

```python
base = ChatPromptTemplate.from_messages([
    ("system", "You are a {role} assistant for {company}."),
    ("user", "{question}"),
])

# At app startup — company is known, role and question aren't
support_prompt = base.partial(company="Acme Corp")

# At invoke time
support_prompt.invoke({"role": "billing", "question": "Where's my invoice?"})
```

Partial application keeps the template definition complete (the system prompt names everything it needs) without forcing callers to pass values they shouldn't have to think about.

## LangSmith Prompt Hub

LangSmith hosts a public registry of versioned prompts at [prompts.langchain.com](https://smith.langchain.com/hub). You can pull a community-maintained prompt by name, version it like code, and roll back if a new revision regresses.

```python
from langchain import hub

prompt = hub.pull("hwchase17/react")    # the canonical ReAct prompt
```

Useful for well-known patterns (ReAct, structured-output extraction, SQL agents) where someone has already done the prompt-engineering work. Less useful for domain-specific prompts — those should live in your repo so they ship with the code that depends on them.

## System vs user prompts: where things go

A surprising fraction of prompt failures are content in the wrong message slot. The convention that works:

- **System prompt** — role, rules, constraints, output format, persistent context. Stable across the conversation. Things the model should treat as authoritative.
- **User prompt** — the task itself. Things that change per request.
- **Tool messages** — outputs the model asked for. Strictly model-machine; not user-authored.

Putting "please respond in JSON" in a user message and forgetting it in the system prompt is the #1 cause of "it works sometimes." Authoritative rules go in `SystemMessage`.

## Prompts are versioned artifacts

Treat prompts the way you treat database migrations: every change is a code change, reviewed, tested, and traceable. A "small tweak" to the system prompt can silently regress accuracy by 10%; the only way to know is to run an eval suite (covered in [LangSmith Observability](../19_LangSmith_Observability/)) on both the old and new version before shipping.

The minimum hygiene: keep prompts in code (not in a config UI that lets non-engineers edit them blindly), give them docstrings explaining intent, and grep for callers before editing.
