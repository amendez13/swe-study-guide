## AI engineering

AI engineering is the discipline of building applications on top of already-available foundation models instead of training every model from scratch. The chapter frames it as the convergence of rising model capability and falling barriers to using those models through APIs and developer tooling.

What makes the term useful is the shift in emphasis. Traditional ML engineering spends much more effort on collecting labeled data, training task-specific models, and operating those models. AI engineering shifts more of the work toward model adaptation, application design, evaluation, and product iteration.

```text
Traditional ML flow:
  data -> model training -> model serving -> product

AI engineering flow:
  model API -> prompting / RAG / finetuning -> product -> evaluation -> iteration
```

## Language models as completion systems

A language model predicts likely tokens from context. In practical product terms, the chapter treats a language model as a completion machine: give it a prompt, and it predicts what should come next based on patterns learned from training data.

That framing matters because many seemingly different tasks can be reduced to completion. Translation, summarization, classification, and code generation all become special cases of "continue this text in the right way." It also explains why model outputs are probabilistic rather than guaranteed to be correct.

```text
Prompt:
  Question: Is this email likely spam?
  Email: "Claim your free prize now..."
  Answer:

Possible completion:
  Likely spam
```

## Masked language models

A masked language model predicts missing tokens by looking at context on both sides of the blank. Instead of only asking "what comes next?", it asks "what best fits here given the surrounding text?" This makes it strong at tasks where understanding the full context matters more than generating long free-form outputs.

The chapter uses masked language models to contrast older bidirectional text-understanding systems such as BERT with today’s generative chat systems. In practice, they are often a better conceptual fit for classification, tagging, and code-understanding tasks than for open-ended assistants.

```text
Input:
  "My favorite [MASK] is blue."

Prediction:
  color
```

## Autoregressive language models

An autoregressive language model predicts the next token using only the tokens that came before it. This left-to-right prediction loop is what makes modern chatbots, coding assistants, and text generators feel generative: the model can keep extending its own output one token at a time.

This is the family that matters most for the rest of the course because foundation-model applications are usually built on autoregressive systems. Their open-endedness gives them broad capability, but it also makes them harder to evaluate and easier to push off track with ambiguity, poor prompts, or missing context.

```text
Context:
  "To be or not to be"

Possible next tokens:
  ",", " that", " is", " the", " question"
```

## Tokens and tokenization

Foundation-model interfaces work on tokens, not raw words. A token may be a character, a word, or a word fragment, and tokenization is the process that breaks text into those pieces before a model processes it.

This matters operationally because token counts affect context limits, latency, and cost. It also matters conceptually because tokenization explains why models can generalize to unfamiliar words by composing them out of known subparts instead of requiring every whole word to exist in the vocabulary.

```text
"I can't wait to build AI applications"
-> ["I", "can", "'t", "wait", "to", "build", "AI", "application", "s"]
```

## Self-supervision and scaling to LLMs

The chapter’s core explanation for the rise of LLMs is self-supervision. Instead of requiring humans to label every example, language modeling can derive its own labels from the text stream itself by predicting the next token from prior context.

That is what makes internet-scale training possible. If the model can learn from books, articles, comments, and documentation without expensive manual labeling, then the bottleneck shifts from annotation to compute, data curation, and architecture. That shift is one of the main reasons language models scaled so much faster than many older supervised systems.

```text
Training sample from "I love street food."

Input:  <BOS>, I, love, street
Output: food
```

## Foundation models and multimodality

A foundation model is broader than a text-only large language model. The chapter uses the term for large general-purpose models that can serve as a base for many downstream applications, including multimodal systems that work with text plus images or other modalities.

The important transition is from narrow, task-specific models to reusable general-purpose models. A team can now start with a strong base model and adapt it, rather than building a separate model family for every task such as translation, image classification, or retrieval.

## Model adaptation: prompt engineering, RAG, and finetuning

The chapter introduces three recurring ways to adapt a foundation model to an application: prompt engineering, retrieval-augmented generation (RAG), and finetuning. These are not random techniques; they are the main levers for changing model behavior without always creating a new model.

Prompting changes instructions, RAG changes the context available at generation time, and finetuning changes the model weights themselves. This is a useful mental model for the rest of the course because many downstream architecture decisions reduce to deciding which of these levers to pull first.

```mermaid
flowchart LR
    A[Base model] --> B[Prompt engineering]
    A --> C[RAG]
    A --> D[Finetuning]
    B --> E[Behavior adapted by instructions]
    C --> F[Behavior adapted by retrieved context]
    D --> G[Behavior adapted by updated weights]
```

## Why AI engineering emerged now

The chapter argues that AI engineering took off because three forces aligned: foundation models gained broad capabilities, investment surged after visible product successes like ChatGPT, and model-as-a-service lowered the implementation barrier for developers.

This is a better explanation than "AI suddenly got popular." It ties the field’s growth to concrete engineering conditions: stronger base models, cheaper experimentation, and the ability to ship useful products through APIs instead of owning the full model-training stack.

## Use case fit and exposure to AI

Use-case fit should be evaluated at the **task** level, not the job-title level. A foundation model is a strong fit when the task mainly involves interpreting messy inputs, generating or transforming language, retrieving and synthesizing information, or producing a first draft that a human or downstream system can refine. It is a weak fit when the task requires hard guarantees, exact arithmetic, deterministic policy execution, precise physical control, or irreversible actions with low tolerance for error.

In the 2023 OpenAI study *GPTs are GPTs*, a task is considered **exposed** if AI or AI-powered software can reduce the time needed to complete it by at least **50%**. An occupation with 80% exposure means roughly 80% of its tasks cross that threshold. High-exposure occupations include interpreters and translators, survey researchers, writers and authors, tax preparers, and web designers. Near-zero-exposure occupations include cooks, stonemasons, and athletes. Exposure is therefore about **time leverage on tasks**, not a claim that the whole occupation disappears.

The most useful first-pass screen is to ask whether the task is language-heavy, whether approximate output is acceptable, whether the result can be reviewed or reversed, and whether the system can cheaply learn from feedback. That is why AI works well for coding assistance, product-copy generation, customer-support drafting, information aggregation, and workflow triage, but is much less appropriate for brake control, medication dosing, payroll finalization, or unrestricted financial authorization.

```text
Strong fit signals
  - unstructured input: docs, tickets, emails, chats, screenshots
  - open-ended output: summaries, drafts, classifications, plans
  - reversible or reviewable outcome
  - feedback arrives quickly
  - tool use or retrieval can close knowledge gaps

Weak fit signals
  - exactness is mandatory
  - output triggers irreversible side effects
  - correctness is hard to verify
  - physical execution is the hard part
  - failure cost is high even for rare mistakes
```

This is also why many successful enterprise deployments start with **internal copilots** rather than full automation. The task can still have excellent AI fit even when the model is imperfect, as long as the output is advisory, reviewable, and tied to a workflow that already has human accountability.

## Role of AI and humans in the application

An AI feature should be designed across four separate axes. First, **critical or complementary**: if the product stops working without AI, the model is critical, and the reliability bar is much higher. Face ID is critical. Smart Compose is complementary. Second, **reactive or proactive**: reactive features answer a user request, so latency matters more; proactive features appear without being asked, so the quality bar is higher because low-quality suggestions feel intrusive. Third, **dynamic or static**: dynamic features adapt continually through user feedback or personalization, while static features update only when the shared model or rules are refreshed. Fourth, **human role**: AI may assist a human, handle only low-risk cases, or act directly without review.

Those axes determine both product behavior and system design. A critical, proactive, dynamic system is much harder to build than a complementary, reactive, static one. It needs better observability, safer rollback paths, stricter evaluation, and tighter controls around feedback loops because bad behavior can affect many users quickly.

For human involvement, a practical progression is: AI drafts for humans, AI handles simple cases and routes harder cases to humans, then AI acts directly once the acceptance rate and failure profile are well understood. That is a better mental model than asking whether the system is merely "human in the loop" or "fully automated." The real question is which decisions remain human, which are delegated, and how the boundary changes over time.

```mermaid
flowchart TD
    A[AI role is complementary or critical]
    B[AI interaction is reactive or proactive]
    C[Model behavior is static or dynamic]
    D[Human role: review, route, or delegate]
    A --> E[Required reliability bar]
    B --> E
    C --> F[Feedback and update design]
    D --> G[Automation boundary]
```

## Planning an AI application

The chapter treats planning as part of the engineering work, not just product management overhead. Before building, you need to ask whether the use case is necessary, whether AI is the right mechanism, what performance level is actually required, and how the project should be staged.

This is especially important in AI because the demo quality of a system can be very different from its production quality. Good planning turns "the model did something impressive once" into milestones around evaluation, failure modes, maintenance, cost, and user expectations.

```python
def should_build_ai_app(task_is_language_heavy: bool, error_tolerance: str, roi_clear: bool) -> str:
    if not roi_clear:
        return "Do more scoping before building."
    if not task_is_language_heavy:
        return "AI may not be the first tool to reach for."
    if error_tolerance == "low":
        return "Use AI carefully with strong evaluation and guardrails."
    return "Good candidate for an AI-assisted application."


print(should_build_ai_app(True, "medium", True))
```

## The three-layer AI stack

The chapter organizes AI systems into three layers: application development, model development, and infrastructure. This is a useful abstraction because it separates product behavior, model adaptation, and platform concerns instead of flattening everything into "just call the API."

Application development is where prompts, context, interfaces, and evaluation meet users. Model development covers tuning, datasets, and inference optimization. Infrastructure handles serving, compute, monitoring, and the systems needed to keep the application operational.

```mermaid
flowchart TD
    A[Application development] --> B[Model development]
    B --> C[Infrastructure]
    A1[UX, prompts, context, evaluation] --- A
    B1[finetuning, datasets, optimization] --- B
    C1[serving, compute, monitoring] --- C
```

## AI engineering versus ML engineering and full-stack engineering

The chapter positions AI engineering between two familiar worlds. Compared with traditional ML engineering, it is less centered on training task-specific models and more centered on adapting, evaluating, and productizing large general-purpose ones. Compared with classic full-stack engineering, it inherits more probabilistic behavior, model latency, and evaluation complexity.

This is why strong AI engineers often need a hybrid mindset. They need enough ML understanding to reason about model behavior and enough product and software engineering skill to build interfaces, iterate quickly, and decide when a system should rely on prompting, retrieval, weight updates, or non-AI code.
