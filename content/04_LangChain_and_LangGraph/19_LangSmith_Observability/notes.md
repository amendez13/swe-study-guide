# LangSmith Observability

The dashboard, dataset, evaluator, and experiment platform purpose-built for LangChain/LangGraph apps. Skip it and you're debugging blind.

## Key Points

- **Why** — LLM apps are non-deterministic; every call is potentially the source of the bug. You need to see every prompt and every response.
- **Tracing** — hierarchical record of one invocation: every Runnable, prompt, response, tool call, retrieval, with timing and tokens.
- **Opt-in via env vars** — `LANGSMITH_TRACING=true` + `LANGSMITH_API_KEY` + `LANGSMITH_PROJECT`; no code change.
- **Tag and name runs** — `run_name`, `tags`, `metadata` make traces findable.
- **Datasets** — eval fixtures, built from real production traces or hand-curated.
- **Evaluators** — deterministic for checkable answers, LLM-as-judge for qualitative properties.
- **Experiments** — run a chain over a dataset with evaluators; the only honest way to know a change helped.
- **Production monitoring** — latency, cost, error rate, evaluator scores over time; alerts on regression.
- **`@traceable`** — wrap non-LangChain code for unified observability.
- **Cost discipline** — traces show real token usage; review them when shipping new chains.

## Example

A retrieval chain instrumented with LangSmith: tagged runs, a small eval dataset, two evaluators (deterministic + LLM-as-judge), and an experiment that compares two prompt variants.

```python
import os
from typing import Any

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_openai import ChatOpenAI
from langsmith import Client
from langsmith.evaluation import evaluate

# 1. Tracing is enabled via env vars (no code change needed):
#    LANGSMITH_TRACING=true
#    LANGSMITH_API_KEY=lsv2_...
#    LANGSMITH_PROJECT=retrieval-experiments

# 2. The chain we're testing — two prompt variants
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# Fake retrieval for the example — real code would use a vector store
def retrieve(query: str) -> list[Document]:
    return [
        Document(page_content="Acme's refund policy is 30 days, no questions asked."),
        Document(page_content="Acme ships internationally to 80 countries."),
    ]


def format_docs(docs: list[Document]) -> str:
    return "\n\n".join(d.page_content for d in docs)


def build_chain(system_prompt: str):
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("user", "Context:\n{context}\n\nQuestion: {question}"),
    ])
    return (
        {
            "context": RunnableLambda(retrieve) | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | model
        | StrOutputParser()
    )


chain_v1 = build_chain("Answer using only the context below.")
chain_v2 = build_chain(
    "Answer using only the context below. If the context doesn't contain the "
    "answer, reply 'I don't know based on the provided information.'"
)


# 3. Tag invocations so they're findable in the LangSmith UI
def ask(chain, question: str, variant: str) -> str:
    return chain.invoke(
        question,
        config={
            "run_name": "retrieval_qa",
            "tags": [variant],
            "metadata": {"variant": variant, "user": "demo"},
        },
    )


# 4. Build an eval dataset
client = Client()


def ensure_dataset() -> str:
    name = "refund-policy-eval"
    existing = list(client.list_datasets(dataset_name=name))
    if existing:
        return existing[0].id
    ds = client.create_dataset(name)
    client.create_examples(
        dataset_id=ds.id,
        inputs=[
            {"question": "What's the refund policy?"},
            {"question": "Do you ship to Brazil?"},
            {"question": "What's the CEO's middle name?"},     # not in context
        ],
        outputs=[
            {"expected": "30 days"},
            {"expected": "yes"},                                # 80 countries includes Brazil
            {"expected": "i don't know"},                       # should refuse
        ],
    )
    return ds.id


# 5. Evaluators
def contains_expected(run, example) -> dict:
    expected: str = example.outputs["expected"].lower()
    actual: str = (run.outputs.get("output") or "").lower()
    return {
        "key": "contains_expected",
        "score": 1.0 if expected in actual else 0.0,
    }


# LLM-as-judge for "is the answer faithful to context"
judge = ChatOpenAI(model="gpt-4o-mini", temperature=0)


def faithfulness(run, example) -> dict:
    question = example.inputs["question"]
    answer = run.outputs.get("output", "")
    verdict = judge.invoke(
        f"Given the question {question!r} and the answer {answer!r}, "
        f"is the answer well-grounded in the context provided by the retrieval system? "
        f"Reply only 'yes' or 'no'."
    ).content.lower().strip()
    return {"key": "faithful", "score": 1.0 if "yes" in verdict else 0.0}


# 6. Run experiments — one per variant
def run_experiment(chain, variant: str) -> Any:
    dataset_id = ensure_dataset()
    return evaluate(
        lambda inputs: {"output": chain.invoke(inputs["question"])},
        data=dataset_id,
        evaluators=[contains_expected, faithfulness],
        experiment_prefix=f"variant-{variant}",
    )


if __name__ == "__main__":
    # Quick interactive checks (these traces show up in LangSmith)
    print("v1:", ask(chain_v1, "What's the refund policy?", "v1"))
    print("v2:", ask(chain_v2, "What's the CEO's middle name?", "v2"))

    # Systematic comparison
    if os.environ.get("RUN_EVALS") == "1":
        run_experiment(chain_v1, "v1")
        run_experiment(chain_v2, "v2")
        # Open the experiments page in LangSmith to compare side by side
```

What's worth noticing:

- **Tagging matters.** Without `tags=["v1"]` and `tags=["v2"]`, you can't find the runs you want in a list of 10,000. With them, one filter shows you the comparison.
- **The dataset is the eval contract.** Three examples is plenty to get started; grow it from production traces over time. The third example (asking about the CEO's middle name) is the kind of failure mode that's easy to miss with vibes-based testing.
- **Two evaluators, two purposes.** `contains_expected` is deterministic — checks for a specific substring. `faithfulness` is LLM-as-judge — grades a qualitative property. They check different things; both run on every example.
- **Experiments compare variants.** Run v1 and v2 against the same dataset; the LangSmith UI shows scores side by side per example. You see exactly which questions improved or regressed.
- **The `RUN_EVALS` gate.** Evals cost real money; gate them behind an env var so casual runs of the file don't burn budget.

The shape of mature LLM engineering looks like this: every interesting change has a dataset associated with it, every change runs as an experiment, every release is gated on evaluator scores not regressing. Without this loop, you're shipping prompts based on what feels right — and feels-right doesn't survive contact with real users.
