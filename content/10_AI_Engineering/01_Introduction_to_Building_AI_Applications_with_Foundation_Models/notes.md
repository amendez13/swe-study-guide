# Introduction to Building AI Applications with Foundation Models

AI engineering is the discipline of shipping products on foundation models that already exist. This topic covers why that became practical, which real products those models show up in, how to decide whether a task should use one and in what role, how to plan the path from a demo to a pinned production model, and how the work sits in a three-layer stack next to ML engineering and full-stack engineering. Language-model internals stay short on purpose. Architecture, sampling, and training live in the next topic.

## Key Points

- **AI engineering** — build the product on a foundation model you adapt, evaluate, and operate. Training a base model from scratch is a separate project most teams buy as an API.
- **Language models in product terms** — a product model finishes a prompt. Masked models such as BERT fill a gap from both sides. Autoregressive models write ChatGPT, Copilot, and Gmail drafts. Tokens are the unit of context, latency, and price.
- **Self-supervision** — the next piece of the document is the label, which is why training could scale without a human mark on every row. Private facts and your quality bar are not in that signal.
- **Foundation models** — a broad base you adapt to many tasks. Text is one modality. CLIP, from Radford and coauthors in 2021, trains image and text embeddings on captions that were already next to the pictures. Midjourney, Firefly, Runway, Sora, and the image inputs on GPT-4o, Gemini, and Claude are the same pattern with different cost and review.
- **Why this became practical** — useful models, hosted APIs, and the investment that followed visible products such as ChatGPT and GitHub Copilot arrived together. A measured productivity win or a capability users will leave for is a reason to build. A demo driven by everyone else shipping one is not. Buy the API for a public task. Own retrieval when the corpus is yours. Pretrain only when a hosted model cannot meet the constraint and you have the data.
- **Prompting, RAG, and finetuning** — prompt when the task is in the request, retrieve when facts are private or changing, finetune when a behavior will not stick and you have examples. Earlier levers stay when you add the next. Pretraining built the base. Post-training taught it to follow instructions. Prompting is not training.
- **Coding and writing** — Copilot, Cursor, Notion AI, and Gmail drafts generate a version a person accepts. Tests catch some bad code. Prose usually has only the sender.
- **Image, video, and tutoring** — stills fit a person choosing variations, video adds a watch-before-publish review, and Duolingo or Khanmigo fit low-stakes practice on material you supply. Grades and answer keys need a source outside the sample.
- **Bots and aggregation** — ChatGPT can be the whole product. Intercom and Zendesk bots sit on a desk with articles and agents. Perplexity, NotebookLM, and Gmail summaries work when each claim is a step away from its source.
- **Extraction and automation** — receipt and invoice tools should emit fields that code can check. Zapier-style agents start with drafts and read-only tools. Money movement and sending as the company wait for a person.
- **Task-level fit** — judge the task. The Eloundou, Manning, Mishkin, and Rock paper marks a task exposed when a model could cut its time by at least half. About 80 percent of U.S. workers are in occupations with at least a tenth of tasks exposed, and about 19 percent are in occupations with more than half exposed. The figures measure time that could be saved on tasks. The job can remain.
- **Roles** — critical or complementary, reactive or proactive, static or dynamic, and what the human still decides. The axes are independent. A complementary refund bot still needs a person on the charge. Adoption guides, including Microsoft's, use crawl, walk, and run for rollout scope. On this card those names are the human role: crawl is a suggestion the person can ignore, walk is a draft they still commit, and run is action on a slice whose error rate you have measured.
- **Expectations** — set a quality threshold against the user's real alternative, a latency threshold for the interaction, and a cost per successful task. An average of 80 percent hides a harmful tail.
- **Milestones** — demo, eval set, shadow, limited send, pinned production. A meeting that liked 20 tickets is still the demo.
- **Maintenance** — pin a model id, re-run the regression set, and recompute the bill from input and output tokens. A cheaper rate card can raise spend when answers get longer.
- **Three-layer stack** — application (prompt, context, UI, product eval), model (train, finetune, datasets, quantization), infrastructure (GPUs, serving, storage, monitoring). Start at the top.
- **Versus ML engineering** — the default moves from training a labeled task model to adapting a general one and judging open-ended output. Dataset engineering replaces feature engineering: dedup, tokenization, and quality control. Inference optimization is on the request path from the first call. Latency and token cost show up then. Finetunes and rerankers are ML work inside this job.
- **Versus full-stack engineering** — the app around the model is ordinary product engineering. Build the product, then the data, then a model change the failures justify. The model adds a slow, metered call that can return a wrong answer with a success status. Prompts are reviewed like code. Faithfulness belongs on an eval set.
- **AI product defensibility** — technology, data, and distribution are what remain after a competitor can call the same model. A prompt on a rented API is a feature a platform can absorb. The data flywheel is the Feedback and the data flywheel card in the architecture topic.

## Example

A practice conversation can go to the model. A payroll filing cannot. A wiki that changes wants retrieval. A thread that is already on screen wants a prompt. Two million Gmail-style summaries, each with 1,900 input tokens and 200 output tokens, cost $2,700 a month at the exercise prices of $0.50 per million input tokens and $2.00 per million output tokens.

```python
def fit(language_heavy: bool, needs_exact: bool, irreversible: bool) -> str:
    if needs_exact and irreversible:
        return "skip"
    if language_heavy and needs_exact:
        return "draft"
    if language_heavy:
        return "use"
    return "skip"


def lever(facts_change_outside: bool) -> str:
    if facts_change_outside:
        return "rag"
    return "prompt"


def month_usd(calls: int, input_tokens: int, output_tokens: int) -> float:
    input_cost = calls * input_tokens / 1_000_000 * 0.50
    output_cost = calls * output_tokens / 1_000_000 * 2.00
    return input_cost + output_cost


print(
    fit(True, False, False),
    fit(False, True, True),
    lever(True),
    lever(False),
    round(month_usd(2_000_000, 1_900, 200)),
)
# use skip rag prompt 2700
```

`use` is the Duolingo-style practice turn. `skip` is the payroll filing. `rag` is the wiki. `prompt` is the thread summary. The $2,700 figure is an assumption at those rates, and it counts every call, including summaries nobody reads. The drills work the role axes, the last mile, the stack, and a price cut that still fails the quality bar.

## Source Chapter

- **Book chapter**: Chapter 1
- **Title**: Introduction to Building AI Applications with Foundation Models

## Book Outline

- The Rise of AI Engineering
- From Language Models to Large Language Models
- From Large Language Models to Foundation Models
- From Foundation Models to AI Engineering
- Foundation Model Use Cases
- Coding
- Image and Video Production
- Writing
- Education
- Conversational Bots
- Information Aggregation
- Data Organization
- Workflow Automation
- Planning AI Applications
- Use Case Evaluation
- Setting Expectations
- Milestone Planning
- Maintenance
- The AI Engineering Stack
- Three Layers of the AI Stack
- AI Engineering Versus ML Engineering
- AI Engineering Versus Full-Stack Engineering
- Summary

## Status

- `concepts.md` is a study set of 19 cards: the rise from language models to AI engineering, the use-case landscape, task fit and the four product roles, expectations, milestones, maintenance, the three-layer stack, the comparisons with ML engineering and full-stack engineering, and AI product defensibility.
- `drills.md` has eight worked drills. The site sets `hasDrills` from the file, so this topic shows a Drills tab.
- Language-model architecture, sampling, and training stay brief here. They belong to Understanding Foundation Models.
- Each of the first 18 concept cards and each of the 8 drill cards embeds a PNG exported from draw.io. The AI product defensibility card has no image yet. Concept pages are in `diagrams/ai-engineering-intro.drawio`. Drill pages are in `diagrams/ai-engineering-intro-drills.drawio`.

## See also

- [Understanding Foundation Models](../02_Understanding_Foundation_Models/) — architecture, training, sampling, and why outputs are probabilistic.
- [Evaluation Methodology](../03_Evaluation_Methodology/) — how to score open-ended output once a task has a threshold.
- [Prompt Engineering](../05_Prompt_Engineering/) — the first adaptation lever, in detail.
- [RAG and Agents](../06_RAG_and_Agents/) — retrieval, tools, and workflows that take actions.
- [Finetuning](../07_Finetuning/) — when a behavior has to live in the weights.
- [AI Engineering Architecture and User Feedback](../10_AI_Engineering_Architecture_and_User_Feedback/) — guardrails, monitoring, and feedback after the feature is live.
