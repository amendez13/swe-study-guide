# Introduction to Building AI Applications with Foundation Models

This chapter introduces the shift from training narrow machine learning models to building products on top of reusable foundation models. AI engineering is distinct not because it uses trendier tools, but because it changes the center of gravity: less effort goes into training bespoke models, and more goes into choosing the right use case, adapting the model, shaping the user workflow, and evaluating failure modes in production.

## Key Points

- **AI engineering** — building applications on top of foundation models has become practical because model capability rose while access barriers fell through APIs and tooling.
- **Language models** — many AI tasks can be reframed as next-token completion, which explains both their power and their probabilistic behavior.
- **Masked vs. autoregressive models** — masked models fill in missing text using both left and right context, while autoregressive models generate one token at a time from prior context; modern generative AI products are mostly built on the autoregressive side.
- **Self-supervision** — LLM scaling became possible because language models can learn from raw text without manual labels for every example.
- **Foundation models** — the big shift is from narrow, task-specific models to reusable, general-purpose models that can be adapted to many tasks.
- **Adaptation levers** — prompt engineering changes instructions, RAG changes available context, and finetuning changes model weights.
- **Use-case selection** — evaluate fit at the task level: foundation models work best on unstructured inputs, open-ended outputs, and reviewable outcomes; in the OpenAI exposure study, a task counts as exposed when AI can cut completion time by at least 50%.
- **Human role** — define the application along four axes: critical or complementary, reactive or proactive, dynamic or static, and human review versus direct automation; these choices determine the quality bar, latency bar, and guardrail design.
- **Planning matters** — a flashy demo is not the same as a production-ready system; evaluation, maintenance, latency, and cost have to be planned early.
- **Three-layer stack** — application development, model development, and infrastructure are distinct layers with different responsibilities.
- **Role shift** — compared with ML engineering, AI engineering is more adaptation- and evaluation-heavy; compared with full-stack work, it deals with probabilistic systems and model trade-offs.

## Example

```python
from dataclasses import dataclass


@dataclass
class AIUseCase:
    name: str
    language_heavy: bool
    needs_hard_guarantees: bool
    requires_fresh_context: bool


def recommend_strategy(use_case: AIUseCase) -> str:
    if use_case.needs_hard_guarantees and not use_case.language_heavy:
        return f"{use_case.name}: prefer conventional software first."
    if use_case.requires_fresh_context:
        return f"{use_case.name}: start with prompting + RAG."
    return f"{use_case.name}: start with prompting, then evaluate whether finetuning is worth it."


cases = [
    AIUseCase("Internal knowledge assistant", True, False, True),
    AIUseCase("Fraud rule engine", False, True, False),
    AIUseCase("Product description generator", True, False, False),
]

for case in cases:
    print(recommend_strategy(case))
```

This example is intentionally simple, but it captures the chapter’s planning mindset: begin by classifying the task, then choose an adaptation strategy instead of assuming every problem needs the same AI architecture.
