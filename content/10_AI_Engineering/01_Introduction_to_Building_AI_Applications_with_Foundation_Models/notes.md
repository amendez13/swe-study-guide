# Introduction to Building AI Applications with Foundation Models

This chapter introduces the shift from training narrow machine learning models to building products on top of reusable foundation models. The key idea is that AI engineering is not just "ML, but newer" — it is a different development posture that emphasizes model adaptation, evaluation, interfaces, and fast iteration.

## Key Points

- **AI engineering** — building applications on top of foundation models has become practical because model capability rose while access barriers fell through APIs and tooling.
- **Language models** — many AI tasks can be reframed as next-token completion, which explains both their power and their probabilistic behavior.
- **Self-supervision** — LLM scaling became possible because language models can learn from raw text without manual labels for every example.
- **Foundation models** — the big shift is from narrow, task-specific models to reusable, general-purpose models that can be adapted to many tasks.
- **Adaptation levers** — prompt engineering changes instructions, RAG changes available context, and finetuning changes model weights.
- **Use-case selection** — AI is strongest on language-heavy, pattern-rich work and weaker when the task requires hard guarantees or low error tolerance.
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
