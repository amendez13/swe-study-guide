# Prompts

Prompts are the contract with the model. LangChain's prompt classes turn scattered f-strings into typed, versioned, composable artifacts.

## Key Points

- **Prompts as code** — don't sprinkle f-strings across handlers; declare prompts once with named variables.
- **`ChatPromptTemplate`** — the standard class; declares `(role, content)` pairs with `{variable}` placeholders.
- **`PromptTemplate`** — the flat-string equivalent for the rare non-chat case.
- **`MessagesPlaceholder`** — a slot that takes a full message list at runtime, used for history and few-shot examples.
- **Few-shot prompting** — `FewShotChatMessagePromptTemplate` formats input/output examples; pair with an `ExampleSelector` to pick relevant ones per query.
- **Partial application** — fill some variables at construction, the rest at invoke time.
- **LangSmith Prompt Hub** — pull community-maintained, versioned prompts by name.
- **System vs user content** — authoritative rules go in the system prompt; the task goes in the user prompt. Wrong slot = inconsistent behavior.
- **Versioning** — every prompt change is a code change; run evals before shipping.

## Example

A customer-support prompt that demonstrates a partial-applied system message, a `MessagesPlaceholder` for conversation history, and few-shot examples for tone calibration:

```python
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_openai import ChatOpenAI

# Few-shot examples for tone — formal but friendly
example_prompt = ChatPromptTemplate.from_messages([
    ("user", "{input}"),
    ("assistant", "{output}"),
])

tone_examples = FewShotChatMessagePromptTemplate(
    example_prompt=example_prompt,
    examples=[
        {
            "input": "When will my package arrive?",
            "output": "Your package is scheduled to arrive on Tuesday. I'll send an update if anything changes.",
        },
        {
            "input": "I'm so angry, this is broken!",
            "output": "I'm sorry you're having trouble — let's sort this out. Can you tell me what's broken so I can help?",
        },
    ],
)

# Master template with a slot for conversation history and a slot for the current question
base = ChatPromptTemplate.from_messages([
    ("system",
     "You are a {role} support agent for {company}. "
     "Be helpful, concise, and never invent policies you don't know about."),
    tone_examples,
    MessagesPlaceholder("history"),
    ("user", "{question}"),
])

# At app startup — company is known once and for all
support_prompt = base.partial(company="Acme Corp")

model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
chain = support_prompt | model | StrOutputParser()


def reply(role: str, history: list, question: str) -> str:
    return chain.invoke({
        "role": role,
        "history": history,
        "question": question,
    })


if __name__ == "__main__":
    history = [
        HumanMessage("Hi, I bought a widget last week."),
        AIMessage("Hello! Thanks for getting in touch. How can I help with your widget?"),
    ]
    print(reply(role="billing", history=history, question="Can I get a refund?"))
```

Every prompt piece is named and reusable: `company` is fixed at construction, `role` switches per chain instance, `history` carries the conversation, `question` is the per-call input, and the few-shot examples are tone-calibrated separately from the system instructions. Edit one piece without breaking the others.
