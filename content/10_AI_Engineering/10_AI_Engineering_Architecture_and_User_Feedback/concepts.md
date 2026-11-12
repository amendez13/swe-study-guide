## The incremental architecture

The incremental architecture is the set of layers around one model call, added when a measured failure needs that layer.

A demo is a prompt and a reply. A product has to decide what the model is allowed to see, what it is allowed to emit, which model runs, what an identical or a near-identical question should skip, which requests become a tool loop, and how you notice the day the answers change. Those are the layers in this topic. Context comes first, because a missing fact cannot be routed or cached into existence. Guardrails come next, because a fluent draft is not yet safe to show or to act on. A router and a gateway come when one model, one key, and one provider are no longer the whole product. Caches come when the same work is paid for on every call. An agent loop comes last among the request-path steps, and only for the intents that need tools. Monitoring is not a step you postpone until the path is finished. The first production call already needs a log line, a model id, and a latency. This topic treats telemetry after the path because the path is what the telemetry has to be able to name.

The layers sit in the application tier of the three-layer stack in [Introduction to Building AI Applications with Foundation Models](../01_Introduction_to_Building_AI_Applications_with_Foundation_Models/). The gateway, the cache store, and the trace pipeline are infrastructure that the application configures. A finetune, when feedback earns one, is the model tier, and the file it trains on stays in [Dataset Engineering](../08_Dataset_Engineering/). Prompt caching of a KV prefix stays in [Inference Optimization](../09_Inference_Optimization/). It is a serving optimization under the call. It is not one of the boxes below.

| Layer | What it does on a request |
| --- | --- |
| Context | Retrieval, the user record, and the date put this request's facts into the prompt. |
| Guardrails | Input checks redact or block a bad request. Output checks hold a bad draft. |
| Router | The router sends an easy intent to a cheap path and a hard intent to a strong one. |
| Gateway | The gateway holds keys, limits, spend, and a provider fallback. |
| Response cache | An exact or semantic cache skips the model when a stored answer is safe to reuse. |
| Agent route | A tool loop runs only for intents that need it. A write stays a proposal. |
| Telemetry | Metrics, logs, and traces say whether the path you shipped is the path that ran. |

**Trade-offs.** Adding every layer on day one buys latency, vendors, and failure modes you do not yet have a metric for. Waiting for a refund to reach Stripe before you add a guardrail is how the incident writes the design. A layer that cannot name the failure it removes is ceremony. A missing layer that already has an incident is the next change. The order is a teaching order. A log line does not wait for the agent.

**Interview.** Draw the request from the user to the model and name the box you would add for the failure you were just given. A wrong return window with the policy sitting in a help center is context. A card number in the log is an input guardrail. A small model on a hard ticket is the router. A second provider during an outage is the gateway. The same question answered from last week's policy is a cache invalidation. A refund that fired from model JSON is the write gate, which already lives on the write-tools card in [RAG and Agents](../06_RAG_and_Agents/). Say which box you would not add yet, and why.

**Recap.** Production grows a prompt into a path: context, guardrails, a router and a gateway, response caches, and an agent only where tools are required. Telemetry starts with the first production call. Prompt caching of a KV prefix is a serving technique under the call, covered in Inference Optimization, and it is not a substitute for any box in the table. Each layer has to name the failure it removes.

## Enhance context

Enhancing context means putting the facts this request depends on into the prompt the model will actually read.

The model does not see the help center, the order system, or today's date unless this request contains them. That is the definition of a prompt in [Prompt Engineering](../05_Prompt_Engineering/). Most "the model is bad" reports on a support bot are a missing passage, a missing order id, or a date the prompt never stated. The fix is the first step in the architecture because a router cannot classify a fact it was not given and a cache cannot store an answer the corpus does not support. Notion AI over a workspace, a Zendesk bot over a help center, Perplexity with citations, and a Gemini draft that can see the open Gmail thread are this step in products you can look at. The index, the permissions, the chunking, and the citation check stay in [RAG and Agents](../06_RAG_and_Agents/). The instruction that says where a fact must come from stays on the sufficient-context card. This card is only the architectural claim: do that work before you add machinery around a blind call.

The bill is the same exercise input price as the context-length card, $0.50 per million tokens. A 2,400-token stable prefix on that card is $1,200 per million calls. A 1,200-token policy page, retrieved per call and not part of that prefix, is half the tokens and half that line.

```python
CALLS = 1_000_000
PAGE_TOKENS = 1_200
INPUT_PER_M = 0.50
print(f"{CALLS * PAGE_TOKENS / 1_000_000 * INPUT_PER_M:.2f}")
# 600.00
```

That $600 is the cost of showing the page. It is not a judgment that the page is the right page. A retrieved article can be stale, permissioned for someone else, or carrying an instruction. Index lag and indirect prompt injection stay on those earlier cards. Enhancing context includes the decision to leave a fact out when the caller may not see it.

**Trade-offs.** A short prompt is cheap and blind. A long paste of the help center spends the $600 several times over and recreates the lost-in-the-middle problem. Retrieving a handful of passages is the usual shape, and it drops the passage that had the exception. Putting the user's entire account into every prompt answers personal questions and leaks the account into logs and into a cache if you are careless later. Context you do not need is a cost, a privacy surface, and a distraction. Context you needed and skipped is a wrong answer.

**Interview.** Start from the question the model got wrong and name the fact that was absent. Say you would retrieve or look up that fact, with the caller's permissions, before you change models. Quote the exercise bill: 1,200 tokens at $0.50 per million is $600 per million calls, half of the 2,400-token prefix on the context-length card because it is half the tokens. Then say what context you would refuse to add: another user's orders, a secret, a page the caller cannot open.

**Recap.** The first architectural step is to put this request's facts into the prompt. Retrieval, the order record, and the date are that step, and the machinery for them is already in RAG and Agents and in Prompt Engineering. At the shared exercise input price, a 1,200-token page is $600 per million calls. A page the caller must not see does not get added just because the model would sound better with it.

## Input guardrails

An input guardrail is a check on the request before the model is allowed to act on it.

Two different failures get lumped together. One is private data you do not want in a provider request or in a log: an email, a phone number, a card number, a national id. The other is an instruction you do not want followed: a jailbreak aimed at the model's own rules, or a prompt injection aimed at your application prompt. Willison's split between those two attacks, and the system-level defenses around them, stay in [Prompt Engineering](../05_Prompt_Engineering/). This card is where those checks sit on the request path.

Microsoft Presidio is the open-source analyzer and anonymizer teams run for the private-data case. It combines recognizers, including patterns and a named-entity pass, and it replaces the spans you configure. A hand-written phone regex is the weak version of the same idea. The cleaning card in [Dataset Engineering](../08_Dataset_Engineering/) already records that a regex can catch a digit pattern and miss the number spelled out. Presidio misses whatever no recognizer covers, so you still sample what reached the model. The check belongs before the log line as well as before the provider. A guardrail that redacts the outbound prompt and stores the raw prompt in the trace has moved the leak into the observability system.

The injection and jailbreak checks are classifiers, not a paragraph in the system prompt. Meta's Llama Guard scores a prompt or a response against a safety taxonomy. Prompt Guard is the small input classifier, and Prompt Guard 2's published window is 512 tokens on the system-level defense card, so a long ticket is segmented or the tail is unscored. NVIDIA NeMo Guardrails is a programmable rail, written separately from the application prompt, that can run on the way in. OpenAI's Moderation API scores harm categories such as hate and violence. It is not, by itself, an injection detector. Azure AI Content Safety does both jobs with different checks. Its harm scoring is the toxicity family. Prompt Shields, the feature previously described as jailbreak risk detection, returns whether a user prompt looks like an attack on the instructions and whether a document looks like a hidden instruction. Microsoft's own description is the boundary worth remembering: that shield does not decide harm, factuality, or whether the text belongs in the task. The application decides whether a positive result blocks, reviews, or passes.

The threshold and the action are yours. A support draft can redact a phone number and continue. A request that would call a refund tool does not continue past a high injection score. The numbers below are exercise verdicts, not a cutoff from Prompt Guard or from Prompt Shields.

```python
def admit(has_pii: bool, injection_score: float, threshold: float, will_call_tool: bool) -> str:
    if will_call_tool and (has_pii or injection_score >= threshold):
        return "block"
    if has_pii:
        return "redact and continue"
    if injection_score >= threshold:
        return "block"
    return "continue"


# Exercise scores, not a vendor cutoff.
print(admit(False, 0.10, 0.80, False))
print(admit(True, 0.10, 0.80, False))
print(admit(False, 0.91, 0.80, True))
# continue
# redact and continue
# block
```

**Trade-offs.** Blocking on a sensitive classifier stops attacks and stops buyers who paste a phishing email they want explained. The over-refusal problem on the safety card in [Evaluate AI Systems](../04_Evaluate_AI_Systems/) is this trade, measured on your tickets rather than inherited from a model card. Redaction preserves the conversation and can remove the order id the model needed. A rail you wrote in NeMo or a validator you wrote in Guardrails AI is reviewable. A score from a hosted shield is not, and it moves when the vendor updates the classifier. Running every check on every keystroke is safer and blows the latency budget on the next card.

**Interview.** Separate private data from an attack, and name a tool for each. Presidio, or a recognizer of the same kind, for the card number. Llama Guard, Prompt Guard, a NeMo input rail, or Azure Prompt Shields for the attack. Say OpenAI's Moderation API is aimed at harm categories and is not the injection check. Then give the action: redact and continue for a draft; block a tool call when the input has private data or a high injection score. A clean tool call still faces the write gate. Mention the 512-token window so a long ticket is not a silent miss. End with the log: the raw span you redacted must not be the span you trace.

**Recap.** Input guardrails run before the model acts. Presidio-style recognizers catch private spans, with the regex limitation already recorded in Dataset Engineering. Llama Guard, Prompt Guard, NeMo Guardrails, and Azure Prompt Shields target jailbreaks and injections, and a harm classifier such as OpenAI's Moderation API is a different check. A draft can redact and continue. A tool call blocks when the input is private or looks like an injection. The trace stores the redacted request.

## Output guardrails

An output guardrail is a check on the model's text before a person sees it or a tool runs.

Four checks cover almost every production draft. Format asks whether the text matches the shape the next step parses. Factuality asks whether a claimed fact is supported by a source you trust. Toxicity asks whether the text is in a harm category you refuse to show. A retry asks the model again when a check fails, once, with a cap. These are the output side of the same rail products: Llama Guard on a response, NeMo's output rails, Guardrails AI's validators, OpenAI's Moderation API, and Azure AI Content Safety's harm scoring.

Format is a parser. JSON that does not parse, a label outside the set, or a missing field is a failed check a program can make with no model involved. The schema mask and the structured-output contract stay in [Understanding Foundation Models](../02_Understanding_Foundation_Models/). Spending a judge on a bracket is the wrong tool, which the "which models can judge" card already says. Factuality, for a grounded product, starts as a substring: the policy quote has to occur in the retrieved article. That check is the citation rule in [RAG and Agents](../06_RAG_and_Agents/) and the factual-consistency criterion in [Evaluate AI Systems](../04_Evaluate_AI_Systems/). An entailment model is the specialist judge for the residue a substring cannot decide. It is not a free pass for a quote that does not appear. Toxicity is a classifier on the completion. A harm score and an injection score are different outputs and should be logged as different verdicts.

A retry sends the failure back once. Guardrails AI's validators are built so a failed check can request another completion. The retry prompt should name the failed constraint. It should not paste an untrusted span back in as instructions, because the failed draft is untrusted text, and untrusted text is the injection path. After one retry, the product refuses, asks a person, or shows nothing. It does not loop.

```python
import json


def release(text: str, article: str, toxic: bool) -> str:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return "retry format once"
    quote = str(payload.get("quote", ""))
    if quote not in article:
        return "retry factuality once"
    if toxic:
        return "hold"
    return "show"


article = "Returns are accepted within 30 days of delivery."
good = '{"quote": "within 30 days of delivery"}'
bad = '{"quote": "within 90 days of delivery"}'
print(release(good, article, False))
print(release("not json", article, False))
print(release(bad, article, False))
print(release(good, article, True))
# show
# retry format once
# retry factuality once
# hold
```

**Trade-offs.** A strict schema catches garbage and rejects a useful answer with a trailing comma. A substring check is exact and blind to a paraphrase that was faithful, and also blind to a quote that is present and out of date. A toxicity classifier blocks abuse and blocks a buyer quoting abuse. A retry fixes a sloppy format and doubles the bill when the model is determined to invent the window. Holding every draft for a person is safe and is no longer a product. Showing every draft and logging the classifier is a product and is how a bad sentence reaches a customer.

**Interview.** Walk the four checks in the order a program should run them: parse, then the citation or the entailment, then the harm classifier, then one retry. Say the schema does not need a model, and point the citation rule at RAG and Agents rather than re-deriving it. Say a harm classifier and an injection classifier log different verdicts. Give the retry a cap of one, and say the failed draft is untrusted if you feed it back. The latency of doing this on a stream is the next card.

**Recap.** Output guardrails check format, factuality, and toxicity before the user or the tool sees the text. Format is a parser. A policy quote has to occur in the retrieved article, with entailment only for what a substring cannot decide. Llama Guard, NeMo, Guardrails AI, OpenAI Moderation, and Azure AI Content Safety are the usual classifiers and validators. One retry names the failed constraint. The draft that failed is not a new system prompt.

## Guardrail implementation

Guardrail implementation is the decision of which checks run before the first token, which checks run on the finished text, which of them block, and how much of the latency budget they may spend.

Checks that do not depend on each other run in parallel. The wall clock is the slowest check, not the sum. Checks that need the model output cannot start until the tokens they inspect exist. A streaming product shows tokens as they arrive. A guardrail that needs the full string cannot veto a token the client has already painted, spoken aloud, or written into its own log. That is the streaming problem. The repairs are to buffer until the check passes, to check a prefix before the first flush, to retract and accept that a retract does not reach every client, or to stream only into a surface that was never a commitment, such as ghost text the user has not accepted.

The clocks below are an exercise for a support draft. They are not the 0.80 second TTFT cap in the inference drills, and they are not the 500-token example on the latency card. This topic uses the same formula as [Evaluate AI Systems](../04_Evaluate_AI_Systems/): a reply of N tokens takes `TTFT + TPOT × (N − 1)`. The product budget here is 0.820 seconds until the user may see the first token.

```python
BUDGET_S = 0.820
PII_S = 0.080
INJECTION_S = 0.120
TTFT_S = 0.650
TPOT_S = 0.025
OUTPUT_TOKENS = 60
FORMAT_S = 0.005
CITATION_S = 0.040
TOXICITY_S = 0.180
# Exercise seconds, not a measured Zendesk trace.

parallel_in = max(PII_S, INJECTION_S)
sequential_in = PII_S + INJECTION_S
first_parallel = parallel_in + TTFT_S
first_sequential = sequential_in + TTFT_S
generation = TTFT_S + TPOT_S * (OUTPUT_TOKENS - 1)
output_wall = max(FORMAT_S, CITATION_S, TOXICITY_S)
output_sum = FORMAT_S + CITATION_S + TOXICITY_S
buffered = parallel_in + generation + output_wall
print(f"{first_parallel:.3f} {first_sequential:.3f} {generation:.3f} {buffered:.3f}")
print(f"{BUDGET_S - first_parallel:.3f} {first_sequential - BUDGET_S:.3f} {output_wall:.3f} {output_sum:.3f}")
# 0.770 0.850 2.125 2.425
# 0.050 0.030 0.180 0.225
```

Parallel input checks finish in 0.120 seconds and the first token is available at 0.770, inside the 0.820 budget with 0.050 seconds to spare. Sequential checks finish in 0.200 seconds and the first token is at 0.850, which misses the budget by 0.030 seconds. The 60-token generation itself is 2.125 seconds. Output checks in parallel add their slowest member, 0.180 seconds, not their sum, 0.225. A path that buffers the whole draft until those checks pass shows nothing until 2.425 seconds. Streaming shows the first token at 0.770 and can only retract later. For a customer email that might contain a card number or a slur, buffer, or hold the flush. For Copilot ghost text, the suggestion is not a sent message, and a local filter on the tokens in hand matches the product better than a 2.425 second silence.

**Trade-offs.** Parallel checks spend extra compute to buy wall clock, and they still wait on the slowest one. The toxicity model at 0.180 seconds dominates the output wall, so speeding up the parser does not move that path. Buffering protects the user and misses a first-token budget on purpose. Streaming meets the budget and leaks the bad span to anything that already rendered it. A retract is a user-interface gesture, not an undo of a notification. Skipping the output guard on the stream because the input guard passed is how a benign prompt with a toxic completion ships.

**Interview.** Put the budget on the table first, 0.820 seconds to first visible token in this exercise. Show that parallel input checks pass it at 0.770 and sequential checks miss it at 0.850. Then show the buffered full draft at 2.425 seconds and say that number is why a stream and a guardrail fight. Name the product that should buffer, a message sent as the company, and the product that should stream, ghost text. Mention that output checks take the max, 0.180, when they run together.

**Recap.** Guardrails add latency, and independent checks should run together so the user waits for the slowest one. In the exercise, parallel input checks leave the first token at 0.770 seconds, inside a 0.820 budget, and sequential checks land at 0.850 and miss it. A 60-token draft buffered for the output guard is not visible until 2.425 seconds. Streaming meets the first-token budget and cannot unsay a token the client has already shown.

## One retry and one fallback

A second chance is one extra attempt after a failure. The cap is what stops a guardrail retry, a router backup, and a gateway fallback from stacking into an unbounded wait.

These are three different second chances, and products blur them. A guardrail retry is the same task on the same model, after a format or citation check failed. A router backup is a different model chosen because the first model was the wrong tool for the intent, or because it returned an error. A gateway fallback is a different provider called because the first provider timed out or returned a server error. Each one can be the right recovery. All three on the same request change the model that was evaluated, multiply the latency, and, if any of them can call a write tool, risk doing the write twice. The idempotency key on the write-tools card in [RAG and Agents](../06_RAG_and_Agents/) is the control for that last risk. This card is the latency cap.

The clocks here are a short routed call, such as an intent label. They are not the 60-token draft. That draft's buffered path is 2.425 seconds, so it does not fit inside the 2.000 second timeout below and needs the budget on the previous card.

```python
TIMEOUT_S = 2.000
HEALTHY_S = 0.450
CAP_S = 3.000
# Exercise seconds for a short routed call, not the 60-token draft.
worst = TIMEOUT_S + HEALTHY_S + HEALTHY_S
uncapped = 4 * TIMEOUT_S
print(f"{worst:.3f} {uncapped:.3f} {worst <= CAP_S} {uncapped <= CAP_S}")
# 2.900 8.000 True False
```

One primary timeout, one healthy fallback, and one healthy retry take 2.900 seconds and fit under a 3.000 second cap. Four attempts that each burn the timeout take 8.000 seconds and do not. The policy the cap encodes is one provider fallback and one guardrail retry. A second fallback is a product decision you make with a new number, not an accident of three configs multiplying.

**Trade-offs.** A single retry saves a request that failed a comma and hides a model that fails the citation check half the time, if you only graph success after retry. A fallback keeps the product up during a provider outage and serves a model your eval may never have scored. Counting retries as success inflates availability. Failing closed on the second error protects a refund flow and drops a FAQ that could have survived on the backup model. The cap is per request. It is not a reason to disable retries on the nightly index job, which is an orchestration concern with its own backoff.

**Interview.** Name the three second chances and give each a different trigger: a bad parse, a wrong model for the intent, a provider 500. Then give the exercise arithmetic, 2.900 seconds against a 3.000 cap, and 8.000 seconds if four timeouts stack. Say the 60-token buffered draft at 2.425 seconds needs its own budget and does not fit this timeout. Close with the write: a retry of a refund uses the idempotency key from RAG and Agents, or it is not a retry, it is a second refund.

**Recap.** A guardrail retry, a router backup, and a gateway fallback are three different second chances. The exercise allows one timeout plus one healthy fallback plus one healthy retry, 2.900 seconds, under a 3.000 second cap. Four timeouts take 8.000 seconds. The 60-token draft lives on a different clock. A retried write still needs an idempotency key.

## The model router

A model router sends each request to a model or a pipeline chosen for that request, instead of calling one model for every task.

Two decisions get called routing. Intent routing classifies the request and selects a pipeline: a refund draft, a shipping answer, an account edit, or a refusal. The classifier can be a small model, a finetuned encoder, or the few-shot prompt in [Prompt Engineering](../05_Prompt_Engineering/). Difficulty routing decides that this intent is easy enough for a cheap model or hard enough for a strong one. RouteLLM, from Ong and coauthors in 2024, is the public framework for the second decision. It trains a router on preference data, including Chatbot Arena battles, so a strong model is reserved for the prompts that need it. The LMSYS post of 1 July 2024 describes four routers: a similarity-weighted ranker, a matrix-factorization scorer, a BERT classifier, and a causal-LLM classifier. That post reports cost reductions versus using only GPT-4 of over 85 percent on MT Bench, 45 percent on MMLU, and 35 percent on GSM8K, while still reaching 95 percent of GPT-4's performance. The paper's abstract states the result more coarsely: cost reductions of over 2× on the benchmarks they ran, without sacrificing response quality. Those are their model pairs and their benchmarks. They are not the blend below, and they are not a Zendesk queue. OpenRouter is the hosted product people meet when they want someone else's router in front of many providers. A self-hosted intent classifier is still the right tool when the classes are your tickets rather than Arena's prompts.

The bill below is an exercise. One hundred thousand calls. Seventy percent are easy: 800 input tokens and 120 output tokens on the small card, $0.50 and $2.00 per million, the planning prices shared with the prompt and agent topics. Thirty percent are hard: 2,000 input tokens and 400 output tokens on the large card, $4.00 and $16.00 per million. These rates are not the $0.25/$0.75 and $5/$15 cards in [Evaluate AI Systems](../04_Evaluate_AI_Systems/), and they are not the $1.25/$5.00 prefix-cache illustration in [Inference Optimization](../09_Inference_Optimization/).

```python
def bill(calls: int, input_tokens: int, output_tokens: int, input_rate: float, output_rate: float) -> float:
    input_cost = calls * input_tokens / 1_000_000 * input_rate
    output_cost = calls * output_tokens / 1_000_000 * output_rate
    return input_cost + output_cost


easy = bill(70_000, 800, 120, 0.50, 2.00)
hard = bill(30_000, 2_000, 400, 4.00, 16.00)
all_large = bill(100_000, 2_000, 400, 4.00, 16.00)
all_small = bill(100_000, 800, 120, 0.50, 2.00)
routed = easy + hard
print(f"{all_large:.2f} {all_small:.2f} {routed:.2f} {all_large - routed:.2f} {100 * routed / all_large:.2f}")
# 1440.00 64.00 476.80 963.20 33.11
```

Perfect routing costs $476.80. Sending every call to the large model costs $1,440.00. Sending every call to the small model costs $64.00. The routed bill is 33.11 percent of the all-large bill, and the saving against always-large is $963.20. The $64.00 bill is available only if the small model passes the hard slice, which is the assumption this arithmetic does not get to make. A refund-amount decision is not an "easy" class because it is short. The router that optimizes the bill will discover that it is short and will need a class the optimizer is not allowed to downgrade.

**Trade-offs.** Intent routing makes prompts specific and adds a misclassification that sends a refund through the shipping prompt. Difficulty routing cuts the bill when the classifier is right and quietly drops quality when it is wrong, while the dashboard shows the $476.80. A router trained on Arena preferences has learned Arena's notion of a hard prompt. Your hard prompt may be a policy exception that is lexically simple. Fallback to the strong model on low classifier confidence spends some of the saving and catches the uncertain band. It does not catch the confident mistake.

**Interview.** Separate intent routing from difficulty routing, and name RouteLLM as the 2024 preference-data framework for the second. Quote the July 2024 post's reductions as that post's benchmark results, then compute this exercise: $1,440.00, $64.00, and $476.80, a saving of $963.20 against always using the large model. Say the $476.80 assumes the 30 percent labeled hard are exactly the calls the large model should take. Say which class you would forbid the router to downgrade.

**Recap.** A router chooses a pipeline or a model per request. Intent classification picks the task. RouteLLM-style routing picks a strong or a weak model from preference data, and the July 2024 benchmark savings belong to that post. On the exercise mix, perfect routing costs $476.80 per 100,000 calls, against $1,440.00 for always-large and $64.00 for always-small. The cheap total is not evidence the hard slice survived.

## The model gateway

A model gateway is the shared front door that holds provider keys, enforces limits, records spend, and presents one interface to every application.

The router decides where a request should go. The gateway is how it gets there. Application teams stop embedding provider secrets in each service. They hold a virtual key the gateway issued, and the gateway holds the real key. The gateway enforces a limit per key, translates one request shape into OpenAI's, Anthropic's, or a self-hosted server's shape, writes the token counts that finance will reconcile, and follows a fallback list when the chosen provider returns an error. LiteLLM's proxy, Portkey, Cloudflare AI Gateway, and Kong's AI gateway are this box in different packaging: a library you host, a vendor's control plane, or an edge you already run. OpenRouter is the hosted multi-provider API that folds a router and a gateway into one bill. Using it does not remove the need to know which of the two jobs a given setting performs.

Limits are the part teams discover during an incident. The exercise provider allows 500 requests a minute. Four applications are capped at 100, 100, 150, and 150. The sum equals the provider cap, and the largest single application is 150, so one runaway client cannot consume the whole provider budget.

```python
PER_APP_RPM = (100, 100, 150, 150)
PROVIDER_RPM = 500
# Exercise limits, not a provider's published quota.
print(sum(PER_APP_RPM), max(PER_APP_RPM), sum(PER_APP_RPM) == PROVIDER_RPM)
# 500 150 True
```

Cost tracking at the gateway is what makes the router bill real. The gateway records input tokens, output tokens, the model id, the virtual key, and whether the call was a fallback. A finance export that only has the provider's monthly total cannot tell you that one application, or one prompt version, spent it. The rate card still moves. The gateway applies the card you configured, and a monthly reconciliation against the provider invoice is the check that the card is the one you are actually being charged.

**Trade-offs.** One front door is one place to rotate a key, one place to see spend, and one outage that stops every assistant you have. Per-app limits protect the provider quota and block a legitimate launch-day spike unless someone raises the cap on purpose. A gateway fallback keeps requests succeeding on a provider the eval did not score. Centralized logs are how you debug a slow call, and they are a new store of prompts unless the input guardrail redacted them first. A gateway that also bundles its own cache and its own guardrails is convenient and makes it harder to see which layer actually fired.

**Interview.** Draw the router and the gateway as two boxes. The router picks the model for the task. The gateway holds the key, the 500-request budget split 100, 100, 150, and 150, the token ledger, and the provider fallback. Name LiteLLM, Portkey, Cloudflare AI Gateway, and Kong as implementations, and OpenRouter as a hosted product that also routes. Say a fallback is a model change. Say the prompt that lands in the gateway log has already passed through the redaction guardrail.

**Recap.** The gateway is the shared front door: one interface, virtual keys, rate limits, a cost ledger, and provider fallbacks. LiteLLM, Portkey, Cloudflare AI Gateway, Kong, and OpenRouter are the products teams actually install or call. In the exercise, four app caps of 100, 100, 150, and 150 sum to a 500-request provider limit, and no single app is that whole limit. The router chooses the model. The gateway executes the call.

## Exact response caching

Exact response caching stores a finished answer and returns it when the same request arrives again.

The cache key is a hash of everything that defines the answer: the model id, the prompt-template version, the canonical rendered prompt, and the decoding settings. Temperature zero, or a task where any one correct answer is acceptable, is the setting that makes a stored answer meaningful. A creative sample at temperature 0.7 is a different draw every time, and caching one of them pretends a sample is a function. Redis is the usual store. The lookup should be a small fraction of the model call. The key includes the tenant and the user whenever the answer depends on them. A key of only the normalized question serves one customer's order status to the next customer who typed the same sentence.

This is not the prompt cache in [Inference Optimization](../09_Inference_Optimization/). That cache reuses KV state for an identical prefix and still generates. This cache skips generation. The difference has its own card below. The dollars here use the $0.50 and $2.00 planning prices, not that card's $1.25 and $5.00 illustration.

One million support classifications in this exercise, 600 input tokens and 20 output tokens, cost $340.00 with no cache. Twelve percent are exact duplicates after normalization. Those 120,000 calls are the hits. A model call takes 0.900 seconds and a Redis get takes 0.002 seconds, both exercise figures.

```python
CALLS = 1_000_000
HIT_RATE = 0.12
INPUT_TOKENS = 600
OUTPUT_TOKENS = 20
INPUT_RATE = 0.50
OUTPUT_RATE = 2.00
MODEL_S = 0.900
REDIS_S = 0.002


def bill(calls: float) -> float:
    input_cost = calls * INPUT_TOKENS / 1_000_000 * INPUT_RATE
    output_cost = calls * OUTPUT_TOKENS / 1_000_000 * OUTPUT_RATE
    return input_cost + output_cost


uncached = bill(CALLS)
saved = bill(CALLS * HIT_RATE)
average_s = HIT_RATE * REDIS_S + (1.0 - HIT_RATE) * MODEL_S
print(f"{uncached:.2f} {saved:.2f} {average_s:.5f}")
# 340.00 40.80 0.79224
```

The hits save $40.80, which is 12 percent of $340.00, and they pull the average latency from 0.900 seconds to 0.79224 seconds. The other 88 percent pay the full call. A 12 percent duplicate rate is an exercise observation about repetitive intents, not a quota you should expect from an open-ended chat.

Invalidation is part of the key. A new template version is a new key, so a prompt edit cannot keep serving the previous answer. A model id is in the key for the same reason. If the retrieved page is inside the hashed prompt, an updated page misses the cache on its own. If the key is only the user's question and the page is fetched after the cache lookup, the cache serves yesterday's window until you delete the namespace. Exact match does not protect you from a key that omitted the thing that changed.

**Trade-offs.** Exact caching is safe when the key is complete, and it saves only the requests that repeat byte for byte. A low duplicate rate will not pay for the machinery. Omitting the user from the key raises the hit rate and leaks an answer across users. Caching a temperature-0.7 draft makes the product look deterministic and stale. A long TTL survives a policy edit that did not change the question text. A short TTL throws away the $40.80.

**Interview.** Write the key: model id, template version, canonical prompt, decoding settings, and the tenant or user when the answer is personal. Compute the exercise: a 12 percent hit rate saves $40.80 of a $340.00 million-call bill and moves average latency from 0.900 seconds to 0.79224 seconds. Separate this store from the KV prefix cache. Say how a policy edit misses: it is inside the hashed prompt, or you delete a namespace that was keyed only on the question.

**Recap.** Exact response caching returns a stored answer for a repeated request and skips the model. The key binds the model, the template, the prompt, the decoding settings, and any identity the answer depends on. At a 12 percent exercise hit rate, one million short classifications drop from $340.00 to a bill that is $40.80 cheaper, and average latency falls from 0.900 seconds to 0.79224 seconds. A key that omits the user, or the page, caches the wrong thing.

## Semantic caching

Semantic caching returns a stored answer when a new request is close to a cached request in embedding space, even though the text is not the same.

GPTCache, from Zilliz, is the public library built for this. It can store an exact match, and it can embed the request, search a vector index, and accept a neighbor whose similarity clears a threshold. Redis is a common place to keep the payload beside that index. The threshold is the whole design. A higher cosine requirement returns fewer hits and fewer wrong hits. A lower one does the opposite. GPTCache's own configuration has shipped both a similarity score and a distance, and those two point in opposite directions, so you read the evaluator you enabled rather than copy a default. Their example tables are one dataset. They are not the audit below.

The exercise is one million queries. At a cosine threshold of 0.92, 180,000 queries have a neighbor in the cache. An audit labels 4 percent of those neighbors as false hits: the text was close and the answer was wrong. Call cost is 1,500 input tokens and 200 output tokens at the $0.50 and $2.00 planning prices, $0.00115 per call. A model call takes 0.850 seconds. The embed and the vector lookup take 0.015 seconds. A stricter exercise audit, at cosine 0.98, finds 60,000 candidates and 300 false hits. None of these counts are a GPTCache benchmark.

```python
CALLS = 1_000_000
CANDIDATES = 180_000
FALSE_RATE = 0.04
STRICT_CANDIDATES = 60_000
STRICT_FALSE = 300
PER_CALL = 1_500 / 1_000_000 * 0.50 + 200 / 1_000_000 * 2.00
MODEL_S = 0.850
LOOKUP_S = 0.015
# Exercise audits, not a library benchmark.

false_hits = round(CANDIDATES * FALSE_RATE)
saved_all = CANDIDATES * PER_CALL
saved_strict = STRICT_CANDIDATES * PER_CALL
average_s = (CANDIDATES * LOOKUP_S + (CALLS - CANDIDATES) * MODEL_S) / CALLS
print(f"{PER_CALL:.5f} {false_hits} {saved_all:.2f} {average_s:.4f} {MODEL_S - average_s:.4f}")
print(f"{saved_strict:.2f} {false_hits / CALLS:.4f} {STRICT_FALSE / CALLS:.4f}")
# 0.00115 7200 207.00 0.6997 0.1503
# 69.00 0.0072 0.0003
```

Serving every 0.92 neighbor saves $207.00 and cuts average latency from 0.850 seconds to 0.6997 seconds, a 0.1503 second saving. It also serves 7,200 wrong answers, 0.72 percent of traffic. You cannot subtract those 7,200 online, because the audit is what told you they were wrong. Raising the threshold to the stricter exercise point saves $69.00 and leaves 300 wrong answers, 0.03 percent of traffic. The hit rate falls from 18 percent to 6 percent. That is the curve you are choosing.

Invalidation is the other half. The embedding of "what is the return window" does not change when the window changes from 30 days to 14. A semantic key built only on the question keeps the old answer. The fix is a namespace or a generation id in the lookup, bumped when the corpus, the template, or the model changes, plus a TTL so a bump you forgot still expires. Personal answers need the tenant in that namespace. "Where is my order" is close to "where is my order" for every customer, and the answer is not transferable. A false hit across accounts is the failure mode this threshold does not understand, because the embeddings really are close.

**Trade-offs.** Semantic caching catches paraphrases exact caching misses, and it is wrong exactly when the paraphrase changed the fact that matters: the order id, the date, the amount, the negation. A high threshold is almost exact match and saves less. A low threshold looks good on the latency chart and bad in the support queue. Auditing false hits is extra labeling. Skipping the audit and quoting the $207.00 is how a 0.72 percent error rate gets described as a performance win. A namespace bump invalidates aggressively and throws away good hits. Forgetting the bump serves a stale policy to everyone whose wording is familiar.

**Interview.** Define the hit as a neighbor above a threshold, and give both exercise points: 180,000 candidates with 7,200 false hits and a $207.00 gross saving at 0.92, against 60,000 candidates, 300 false hits, and $69.00 at 0.98. Say the average latency moves from 0.850 to 0.6997 seconds only if you serve the false hits too. Then give the two invalidations a threshold cannot do: a policy edit that does not change the question, and a second customer with a similar sentence. Name GPTCache as the public library, and refuse to quote its default threshold as if distance and similarity were the same knob.

**Recap.** Semantic caching serves a stored answer to a nearby request. The threshold sets the hit rate and the false-hit rate together. In the exercise, cosine 0.92 saves $207.00 per million calls and 0.1503 seconds of average latency while serving 7,200 wrong answers. Cosine 0.98 saves $69.00 and serves 300 wrong answers. A namespace has to move when the corpus changes, and the key has to include the tenant when the answer is personal.

## Prompt cache versus response cache

A prompt cache reuses the KV state of an identical prefix and still generates the answer. A response cache returns a stored answer and skips generation.

Both are called caching, and they fail differently. The prompt-cache card in [Inference Optimization](../09_Inference_Optimization/) is the first one. On the Llama 3 8B shape, a 4,096-token prefix is 0.50 GiB of BF16 cache. At that card's exercise rates, one million calls with a 512-token question and 250 output tokens cost $7,010 uncached and $2,402 with the prefix read from cache, a saving of $4,608. The cached portion has to be a prefix. The question and the completion are paid every time. The docs checked for that card, 12 November 2026, are the source of the provider multipliers. This topic does not recompute them and does not mix them with the $0.50 and $2.00 planning prices used for response-cache bills.

A response cache, exact or semantic, is the second one. A hit does not prefill and does not decode. That is why the exact-cache card can take $40.80 off a $340.00 bill, and why a semantic false hit is a wrong answer rather than a slightly stale prefill. The prefix rule does not apply, because there is no prefix. The identity rule does. A KV cache of a shared system prompt is not a customer's order status. A response cache of that order status is.

| | Prompt cache | Response cache |
| --- | --- | --- |
| What is stored | The KV state of an identical prefix. | The finished answer, exact or by a neighbor. |
| What a hit skips | The prefill of that prefix. Decode still runs. | The model call. |
| What still changes | The suffix and the new completion. | Nothing, until the entry is dropped. |
| The stale failure | An old prefix that still matches byte for byte. | An answer whose world changed, or whose neighbor was a different user. |
| The bill in this guide | $7,010 versus $2,402 per million calls, on the inference card's rates. | $40.80 off $340.00 exact, or $207.00 gross semantic, on the $0.50 and $2.00 rates. |

**Trade-offs.** A prompt cache helps every call that shares a long stable prefix, including calls whose answers must be unique. A response cache helps only calls whose whole answer is reusable, and it is a privacy bug when that judgment is wrong. Turning on both is normal. The gateway or the application looks for a response hit first, and on a miss the provider may still cache the prefix of the new call. Attributing the entire saving to one of them makes the next capacity decision wrong. A response-cache hit rate cannot be compared with the $4,608 prefix saving. They are different mechanisms, different rates, and different exercise prices.

**Interview.** Say which store a hit reads. KV bytes, and the model still decodes: prompt cache, 0.50 GiB for the 4,096-token Llama 3 8B prefix, $7,010 down to $2,402 in that card's exercise. A finished string, and the model does not run: response cache, with the exact and semantic bills kept on their own cards at the $0.50 and $2.00 prices. Give the failure each one has. A one-token edit at the start of the prefix misses the KV cache. A semantic neighbor with the wrong order id hits the response cache and should not have.

**Recap.** Prompt caching skips the prefill of an identical prefix and still generates. The inference card prices that at $7,010 versus $2,402 per million exercise calls, and the prefix is 0.50 GiB on Llama 3 8B. Response caching skips the call and returns a stored answer, exact or semantic, at this topic's own exercise bills. A shared system prompt belongs in the first. A customer's order status belongs in the second only behind a key that includes that customer.

## Agents and write actions in the architecture

An agent in this architecture is a routed loop with tools. A write action remains a proposal the program has to accept.

The agent topic already defines the loop, the tool classes, the planner, the failure modes, and the memory. This card places that loop in the path. The router is what keeps it off most requests. A repeated FAQ goes to the exact cache or to a single grounded draft. A policy question goes through retrieval and the citation guardrail. A request that needs several lookups can enter a read-only loop, with the step cap from [RAG and Agents](../06_RAG_and_Agents/). A refund, a sent email, or a merge enters as a proposal. The model does not hold the Stripe key, which is the system-level defense in [Prompt Engineering](../05_Prompt_Engineering/) applied at the routing layer. The program recomputes the amount, asks a person for an irreversible write, and sends an idempotency key. Those three controls stay on the write-tools card. Repeating the Stripe walk would only risk a second, conflicting procedure.

The cost is why the router exists. The efficiency card already prices a six-step loop at $684.00 per 100,000 tasks against $140.00 for one retrieve-then-answer call, at the $0.50 and $2.00 exercise prices. Putting every ticket into the loop spends that difference. The gateway still meters the loop as several model calls under one user request, or the $476.80 router blend from earlier will undercount the agent route. Guardrails apply to tool results, not only to the user. A tool result is untrusted text. Azure Prompt Shields' document check, and the indirect-injection card, are the same warning from the tool side.

| Intent | The path that should run |
| --- | --- |
| A repeated question whose answer is safe to reuse | The response cache, and the model only on a miss. |
| A policy question | Retrieval, one grounded draft, and the citation check. |
| Several lookups and no side effect | The read-only agent, with a step cap. |
| A refund, a sent message, or a merge | A proposal, a recomputed argument, and a person where the action is irreversible. |

**Trade-offs.** An agent route solves multi-step work and is the expensive, hard-to-evaluate default if the router is generous. A read-only loop can still be prompt-injected by a page it retrieved. A human on every write protects the refund and makes a high-volume "mark as read" action feel broken, which is why that action is a different tool with a different gate. Hiding the loop inside a framework so the application cannot see the tool call is the orchestration failure on a later card. Logging "agent" as the route, without the tool names and the step count, makes the $684.00 impossible to attribute.

**Interview.** Place four intents into the table: a cached FAQ, a policy question, a multi-lookup read, a refund. Say the refund uses the write-tools card rather than a new policy invented here. Cite the $684.00 against $140.00 as the reason the router may refuse to enter the loop. Say tool output is untrusted and passes an input-style check before the next step. Mention that the gateway has to bill the steps, not the user request alone.

**Recap.** The agent is one route, not the product. Reads can loop, with the step cap and the $684.00 versus $140.00 bill from RAG and Agents. Writes stay proposals: recomputed arguments, a person on the irreversible ones, an idempotency key. Tool results re-enter through a guardrail. The router is what keeps a simple ticket off that path.

## Monitoring and observability

Monitoring tells you a known signal crossed a line you set. Observability is the telemetry that lets you explain a failure you did not have a line for.

A monitor on error rate, p95 latency, dollars per hour, or thumbs-down rate answers "is the bad thing we already named happening." It pages someone. It cannot tell you why this request retrieved the wrong page, because "wrong page" was not a metric you defined in advance. Observability is the property that lets you ask that question from data you kept: a trace with the passage ids, a log of the template version, a metric you can break down by intent after the incident starts. Metrics, logs, and traces are the three kinds of telemetry. The next cards are what each one has to contain for a model application. The split itself is the point of this card. A dashboard is not observability. A warehouse of raw prompts is not a monitor.

OpenTelemetry is the instrumentation layer that keeps those three signals joinable by a request id. Its GenAI semantic conventions, still marked development in the project's docs as of November 2026, name spans and metrics in a shared way: `gen_ai.request.model`, `gen_ai.operation.name`, `gen_ai.provider.name`, `gen_ai.usage.input_tokens`, and `gen_ai.usage.output_tokens`. An older draft used `gen_ai.system` and treated the input count differently. The November 2026 text says the input count should include cached tokens and, when a provider reports both a billed count and a consumed count, the billed count. The cache-read attribute in that revision is a subset of the input count, so adding the two double-counts. Pin the revision your SDK emits. LangSmith, Langfuse, and Arize Phoenix are the products teams use to look at LLM traces specifically. LangSmith is tied to the LangChain ecosystem and also stands alone as a trace store. Langfuse is the open-source server many gateways ship traces to. Phoenix, from Arize, is the open-source trace and evaluation UI, including embedding views that make a cluster of odd prompts visible. A vendor trace that cannot carry your retrieval span is only the model call.

**Trade-offs.** Monitors are how you sleep, and they are silent on the failure you forgot to name. High-cardinality traces answer the new question and cost money, retention decisions, and a privacy review, because a prompt is often personal data. Keeping every prompt for a year helps the postmortem and is a liability the input guardrail was supposed to shrink. Sampling traces cuts the bill and can drop the one request you needed. A GenAI vendor UI is fast to adopt and a second source of truth if the gateway also logs. Standard names help you change vendors. They do not help if two services emit two revisions of `input_tokens`.

**Interview.** Define the two words with one incident. The page is the monitor: p95 crossed the line. The explanation is observability: the trace shows the template version and the passage ids. Name the three signals and the three products, LangSmith, Langfuse, and Phoenix, plus OpenTelemetry as the shared names. Mention that the GenAI conventions were still development in November 2026, that cached tokens and billed counts need the revision you pinned, and that summing input tokens and cache-read tokens double-counts in the revision that nests them.

**Recap.** Monitoring pages you when a known line is crossed. Observability is being able to explain a request you did not think to graph. Metrics, logs, and traces are the raw material, joined by a request id. OpenTelemetry's GenAI names are the common vocabulary and were still moving in November 2026, especially around whether cached tokens sit inside the input count. LangSmith, Langfuse, and Arize Phoenix are the trace products. A prompt in any of them is a privacy decision.

## Quality, latency, cost, and reliability

The metrics that decide a production model are quality, latency, cost, how fast you notice and repair a break, and what users actually do.

Quality online is not the offline eval, and you want both. The offline number is the pipeline in [Evaluate AI Systems](../04_Evaluate_AI_Systems/): exact checks, a judge where a judge is earned, a slice for the intents that matter. Online, you can see schema failures, citation failures, guardrail blocks, and refusals on traffic the eval set may not contain. The two numbers diverging is a finding, not a nuisance. Latency uses that topic's clocks. TTFT, TPOT, and the formula `TTFT + TPOT × (N − 1)` stay defined there. This topic adds the user-visible clock, which includes the gateway, the guards, and the client. A p95 you can act on names which clock it is. Goodput, requests that finished inside the objectives, stays defined there too. Cost is dollars per successful task, broken down by route, model, and cache outcome. A cost per call that ignores retries flatters a model you call three times. The router card's $476.80 is a planning bill. The gateway ledger is the actual one.

Reliability of the service, as opposed to quality of the answer, is how long failures last. This topic uses three clocks, because the industry words overlap. Time to detect is from onset to the page. Time to mitigate is from the page to the user-visible recovery. Time to restore, the MTTR on this card, is from onset to recovery, so it equals the first plus the second. The eight incidents below are an exercise, in minutes. They are not an SLA.

```python
DETECT_MIN = (6, 10, 4, 22, 8, 15, 9, 14)
RESTORE_MIN = (20, 40, 18, 90, 30, 55, 25, 70)
# Exercise minutes from onset, not a vendor SLA.


def mean(values: tuple[int, ...]) -> float:
    return sum(values) / len(values)


gaps = tuple(restore - detect for detect, restore in zip(DETECT_MIN, RESTORE_MIN))
print(f"{mean(DETECT_MIN):.1f} {mean(gaps):.1f} {mean(RESTORE_MIN):.1f}")
# 11.0 32.5 43.5
```

Mean time to detect is 11.0 minutes. Mean time from the page to recovery is 32.5 minutes. Mean time from onset to recovery is 43.5 minutes. A program that alerts in 11 minutes and then waits on the only person who can roll a prompt back is a detection success and a mitigation failure. User-facing rates sit beside these clocks and do not replace them. A thumbs-up rate, a regenerate rate, and Copilot's acceptance rate say what people did. They are rates only with a denominator: thumbs per rating shown, regenerates per answer, acceptances per suggestion displayed. The interval on a thumb rate is its own card. A moving user rate with a flat eval is a drift problem, not a reason to throw out either number.

**Trade-offs.** An offline eval the traffic has outgrown will bless a regression users already hate. An online thumb rate will condemn a correct refusal users dislike. Latency p50 hides the p95 the guardrail budget cares about. Cost per call rewards a cache that serves the wrong answer, unless the denominator is a successful task. Short MTTD with long mitigation means the page works and the rollback does not. Optimizing MTTR by reverting every blip will also revert the fixes.

**Interview.** List the five families and one concrete series for each. Quality: citation-failure rate beside the offline slice score. Latency: user-visible p95, using the TTFT formula from Evaluate AI Systems rather than a new one. Cost: dollars per successful task by route. Reliability: 11.0, 32.5, and 43.5 minutes on the exercise incidents, with the definitions. User metrics: acceptance per suggestion shown, not a raw count of accepts. Say a flat eval and a moving thumb rate are a disagreement you investigate, not a tie you break by ignoring one.

**Recap.** Production quality is an offline eval plus online failure rates. Latency keeps the TTFT and TPOT definitions from Evaluate AI Systems and adds the user-visible clock. Cost is dollars per successful task. On eight exercise incidents, mean detection is 11.0 minutes, mean mitigation after the page is 32.5, and mean time from onset to recovery is 43.5. User rates need a denominator. They do not outvote a measured task failure, and a task score does not outvote a real change in what users do.

## Logs and traces

A log is an event you record. A trace is the tree of timed spans for one request.

A useful model-request log has the request id, the tenant, the prompt-template id and version, the model id, the route, the cache outcome, the guardrail verdicts, the tool names, the token counts, and the passage ids. It does not need the raw card number, and it should not contain the raw prompt if the input guardrail's job was to keep that span out. A log of "error" with none of those fields is how an incident becomes a guessing game. The trace is the same request drawn as time. Gateway, router, retrieval, model, and output guard are the spans that tell you which layer was slow. OpenTelemetry is what makes the log line and the span share a request id. LangSmith, Langfuse, and Phoenix are where people look at the tree. The trace is also the place a write action shows up as its own span, so a refund is visible as a child of the request and not only as a sentence inside a completion.

The milliseconds below are one exercise help-center answer. They are not a production trace and not the slow-request drill.

```python
SPANS_MS = {
    "gateway": 8,
    "router": 12,
    "retrieval": 180,
    "model": 900,
    "output_guard": 40,
}
# Exercise milliseconds, not a production trace.
total = sum(SPANS_MS.values())
hot = SPANS_MS["retrieval"] + SPANS_MS["model"]
print(total, f"{hot / total:.4f}", f"{SPANS_MS['output_guard'] / total:.4f}")
# 1140 0.9474 0.0351
```

The request takes 1,140 milliseconds. Retrieval and the model are 1,080 of them, 94.74 percent. The output guard is 40 milliseconds, 3.51 percent of the trace, and it is not the problem on this request. A team that spends the week shrinking the guardrail because the dashboard says "AI latency" is optimizing that 3.51 percent. The fix, if one is needed, is the retrieval or the generation. Another request can put the time in a retry instead, which is why you read the spans rather than the total.

**Trade-offs.** Detailed traces make the 94.74 percent visible and store more user text unless you redact first. Logging every token of every prompt helps replay and retains data you may not have a basis to keep. Sampling keeps the bill down and biases the sample toward whatever the sampler favors. A trace that starts at the model SDK misses the gateway queue and will blame the model for a wait that happened earlier. A log without a template version makes two answers incomparable. A trace without passage ids makes a groundedness failure look like a generation failure.

**Interview.** Say what you put on the log line and what you refuse to put there: ids, versions, verdicts, passage ids, and not the raw card number. Then read a trace. In this exercise the total is 1,140 milliseconds and 94.74 percent of it is retrieval plus the model, so the 40 millisecond guard is the wrong optimization. Say the request id is what joins the log to the trace. Mention that a write belongs in the tree as its own span.

**Recap.** Logs record the decision: which template, which model, which route, which verdicts, which passages. Traces record the time, as spans. In the exercise, one answer takes 1,140 milliseconds and retrieval plus the model are 94.74 percent of it. The guardrail is 40 milliseconds. Redaction happens before either store. A total without spans will send the work to the wrong layer.

## Drift detection

Drift is a change in the prompts, the model behind an API name, or the mix of users, that moves behavior while your last deploy stays where it was.

Prompt drift is the input distribution moving. Users start pasting screenshots. The help center rewrites the window. A template edit changes the prefix. The maintenance card in [Introduction to Building AI Applications with Foundation Models](../01_Introduction_to_Building_AI_Applications_with_Foundation_Models/) already treats the model as a dependency that moves under you. Model-API drift is that dependency: the provider replaces weights behind a name, and your code is identical. Pinning a dated model id is the control that card names. A floating alias makes the drift automatic. User-behavior drift is the mix of intents, languages, or tenants changing so that a router threshold fit to last month is fit to the wrong traffic.

You detect it with series you can compare to themselves. A fixed set of canary prompts with answers you expect. The offline eval, rerun on a schedule and on every model-id change. The online rates from the metrics card: citation failures, schema failures, refusal rate, output length, thumb rate. And a distribution over intents. The shares below are an exercise week, not a Zendesk export. Total variation distance is half the sum of absolute differences, so it is 0 when the mix is unchanged and 1 when the mixes are disjoint.

```python
LAST_WEEK = {"refund": 0.40, "shipping": 0.35, "account": 0.25}
THIS_WEEK = {"refund": 0.22, "shipping": 0.33, "account": 0.45}
# Exercise intent shares, not a ticket export.


def total_variation(left: dict[str, float], right: dict[str, float]) -> float:
    return 0.5 * sum(abs(left[name] - right[name]) for name in left)


print(f"{total_variation(LAST_WEEK, THIS_WEEK):.2f}")
# 0.20
```

The distance is 0.20. Account traffic went from a quarter of the mix to nearly half, and refunds fell by 18 points. A router tuned so that 30 percent of calls are "hard" is now aimed at a different population. Phoenix and similar embedding views help when the drift is not a clean intent label: the prompts cluster somewhere the old set did not. A canary that still passes while the intent distance moves is a coverage gap in the canary, not a proof that nothing drifted. The page threshold on 0.20 is one you set from your own history. The number is not a universal cutoff.

**Trade-offs.** Canaries catch a broken alias and miss a new intent. Full evals catch quality and cost too much to run on every request. Intent histograms are cheap and only as good as the labels. Embedding clusters show a new blob and do not name it. Alerting on every small distance trains the on-call to ignore the page. Never alerting, because the model vendor said the alias was stable, is how an unpinned upgrade reaches the queue. Pinning avoids a class of drift and delays a class of improvements, which is the maintenance card's trade.

**Interview.** Name the three drifts: the prompt and corpus, the model behind the API name, and the user mix. Give the exercise distance, 0.20, and say what moved, refunds down and account up. Say a pinned model id is the control for the API case, from the introduction topic. Say a green canary plus a moved histogram means the canary does not cover the new mix. Refuse a universal cutoff.

**Recap.** Drift is a prompt change, a silent model change, or a user-mix change that your deploy did not ship. Canaries, a rerun eval, online failure rates, and an intent histogram are how you see it. In the exercise, total variation between the two weeks is 0.20, with account traffic replacing refunds as the large class. Pin the model id. Treat a green canary on the old mix as incomplete evidence.

## Pipeline orchestration

Pipeline orchestration is how multi-step work retries, waits, and resumes. A framework earns its place when that work no longer fits in one request function.

Two kinds of multi-step work get the same name. The request path is a function: retrieve, generate, check, return. It has to finish while the user waits, and the previous cards are its structure. The offline path is a workflow: rebuild the index when the help center changes, run the nightly eval, wait for a person to approve a finetune, backfill a week of traces. Apache Airflow and Prefect are built for the second kind. They retry, schedule, and record a run id. Using them for the request path adds a scheduler to a call that needed a function. Using a bare function for the nightly rebuild leaves you with a cron job that does not know whether yesterday's run finished.

LangChain, LlamaIndex, Haystack, and DSPy sit on the request side and on the authoring side. LangChain is a general framework for chains, tools, and agents. LlamaIndex is organized around the indexes and data connectors a RAG path loads. Haystack, from deepset, is a pipeline framework aimed at search and question answering. DSPy compiles a prompt program against a metric. The search it performs, and the bill of that search, stay on the prompt-tools card in [Prompt Engineering](../05_Prompt_Engineering/). This card is where the compiled program is allowed to sit: behind the same gateway, the same guardrails, and the same eval id as a hand-written prompt. You can use a LlamaIndex loader, or a Haystack retriever, inside your own function. Adopting the framework's agent loop is a separate choice. The failure is a framework that calls the tool itself, so the allow-list, the idempotency key, and the human gate from [RAG and Agents](../06_RAG_and_Agents/) are inside code you do not review on each change.

```python
def answer(draft: str, passages: list[str]) -> str:
    quotes = [line.removeprefix("quote: ") for line in draft.splitlines() if line.startswith("quote: ")]
    if quotes and all(quote in "\n".join(passages) for quote in quotes):
        return draft
    return "refuse"


print(answer("quote: 30 days", ["Returns within 30 days."]))
print(answer("quote: 90 days", ["Returns within 30 days."]))
# quote: 30 days
# refuse
```

That function does not need a DAG. The index job that produces `passages` might. The two prints are the output guardrail in miniature: a quote has to occur in the retrieved text. They are not a framework.

**Trade-offs.** A framework gives you connectors, a retriever, and a trace integration, and it gives you an upgrade trail and an abstraction that hides the prompt. Owning the loop in ordinary code is easy to audit and easy to leave without retries on the offline job. Airflow for a single chat completion is ceremony. A cron script for a reindex that must not run twice is an incident. DSPy can find a prompt that beats yours on the metric you gave it, and that metric needs the holdout the prompt-tools card already requires. A graph you cannot draw on one page has become the product.

**Interview.** Split the request function from the offline workflow, and assign Airflow or Prefect only to the second. Name LangChain, LlamaIndex, Haystack, and DSPy as request-path and authoring tools, and say you can take a loader without taking the agent runtime. Put the tool allow-list in code you own even if a framework dispatches the call. Point DSPy's search cost at the prompt-tools card instead of re-deriving it.

**Recap.** Orchestration is for work that retries, waits, and resumes, such as a reindex or a nightly eval. Airflow and Prefect are the usual engines. The user-facing path can stay a function: retrieve, generate, check. LangChain, LlamaIndex, Haystack, and DSPy help build that function and can hide the tool boundary if you let them own the action. A compiled prompt still goes through the gateway, the guardrails, and the eval.

## Explicit and implicit feedback

Explicit feedback is a signal the person knows they are giving. Implicit feedback is behavior you interpret as a judgment.

A thumb, a star, a written complaint, and a choice between two answers are explicit. ChatGPT's thumb on a reply is the familiar explicit control. A side-by-side pick, which ChatGPT has also asked of people and which Arena runs as the whole product, is explicit too. Implicit signals are the ones the product records while the person does the task. GitHub Copilot's acceptance rate is the share of shown suggestions a developer takes. A suggestion the developer ignores is the implicit negative. Midjourney's upscale choice is closer to explicit: the person picks one of four images, knowing the pick continues the work. The boundary is whether the person was asked. The value of the signal is a different question. Implicit signals are plentiful and ambiguous. Explicit signals are sparse, and the people who bother are not the whole traffic. That selection bias is already the flywheel warning on the acquiring-data card in [Dataset Engineering](../08_Dataset_Engineering/). This card does not recompute that card's $3,125.00 label budget.

Both kinds need a denominator and a definition of the action. Copilot can report acceptance of a whole suggestion and acceptance of a smaller span. Those are different rates, and a published percentage goes stale, so you cite the post and the date if you need one. A thumb without the count of answers that offered the thumb is not a rate. A regenerate is implicit or explicit depending on the control, and it has its own card. None of these signals is a task score. The metrics card keeps the offline eval beside them because a user can accept a wrong refund and thumbs-down a correct refusal.

**Trade-offs.** Asking for a thumb gets you a label and annoys people, and the people who answer are the ones with time or a grievance. Inferring quality from acceptance is unobtrusive and confuses "I took the suggestion" with "the suggestion was right." Copilot acceptance can rise because the suggestion got more aggressive about matching the next line the developer was going to type, which is a product success and a weak factual test. A side-by-side vote is the cleanest preference and the most expensive to ask for. Training on explicit votes alone inherits the voters. Training on implicit accepts alone inherits the workflow.

**Interview.** Give one explicit signal and one implicit signal from real products: ChatGPT's thumb, Copilot's acceptance per suggestion shown. Say Midjourney's upscale is a deliberate choice among four images. Say the voters and the accepters are not the whole user base, and point that bias at the acquiring-data card rather than inventing a new one. Keep the offline eval in the answer so a thumb is not the only definition of quality.

**Recap.** Explicit feedback is a thumb, a vote, or a written judgment the person knows they gave. Implicit feedback is behavior such as accepting a Copilot suggestion. ChatGPT's thumb and Arena's comparison are explicit. Copilot's acceptance rate is implicit and needs the shown suggestions as its denominator. Midjourney's upscale is a choice the person means to make. Neither kind is the traffic, and neither replaces the task eval.

## Natural language feedback

Natural language feedback is the judgment hiding in what the person types or does next, in words rather than in a widget.

Four patterns show up in chat products. Early termination is the stop button. ChatGPT and Claude both let a person halt a generation. Stopping at the first sentence often means that sentence was already wrong, or already enough. You cannot tell those apart from the stop alone. The next turn is the better evidence. Error correction is a follow-up that names the mistake: "no, the window is 14 days," "that is the other order." The correction is a candidate preference pair, the draft as the rejected answer and the correction as the chosen one, only after you believe the person is right. The acquiring-data card makes that condition. A complaint is evaluative language with no replacement fact: "this is useless," "wrong." It is a negative label on the turn and a poor training target by itself, because it does not say what the right answer was. Sentiment of the next turn is the weakest of the four. A thank-you can follow a bad answer the person fixed themselves. "This is not bad" contains the word bad. A classifier on the next turn is a feature, not a label you train on raw.

The useful extraction is a relation between turns, not a keyword. A negation plus a replacement fact is a correction. A stop with no follow-up is ambiguous. A complaint plus a reformulation is both a negative label and a new attempt. Logging the pair of turns, with the template version, is what makes the extraction auditable. Running a sentiment model and storing only "negative" throws away the 14 days.

**Trade-offs.** Reading the next turn uses signal you already paid to generate, and it overweights people who argue. People who leave are invisible here, which is why deletion and abandonment are the next card. Treating every correction as ground truth teaches the model the user's misconception when the user was the one who was wrong. That is the sycophancy loop, one card away. A keyword list is cheap and wrong on negation. A classifier is better and still needs a sample you read. Storing raw follow-ups for training imports whatever private data the follow-up contained, so the same redaction guardrail applies to the second turn.

**Interview.** Name the four patterns and the one you would train on. A stop is ambiguous. A complaint is a negative label without a target. Sentiment is a hint. A correction that replaces a fact is the preference-pair candidate, after someone or something checks that the replacement is better. Give the "not bad" example as the reason a keyword is not a sentiment model. Say both turns pass through redaction before they enter a training file.

**Recap.** The next turn contains feedback: a stop, a correction, a complaint, or a tone. Only a correction that supplies a better fact is close to a training pair, and only once you believe the fact. A stop alone is ambiguous. A complaint does not contain the right answer. Sentiment words lie, including "not bad." Store the turns, redact them, and do not promote a keyword to a label.

## Regenerate, edits, length, and deletion

Regenerate, an edit, the length of the conversation, and a deletion are feedback that never uses a rating widget.

Regenerate means the person asked for another sample of the same turn. ChatGPT's regenerate button is the explicit version of an implicit complaint about the current sample. It is not, by itself, a factual error. People regenerate because the tone was wrong, because they want a second idea, or because the first answer was false. Midjourney's new variation is the product, not a failure: the point of the grid is another draw. A support draft that is regenerated is closer to a miss, because a second draft delays the reply. The rate needs the same denominator as any user metric, regenerates per answer that offered the control. Edits are stronger. When a person changes a Copilot suggestion or a Gmail draft before sending, the distance between the suggestion and the sent text is the signal. An edit that only shortens is style. An edit that changes the window from 30 days to 14 is a factual correction and, again, a preference pair only if the edit is the better text. Conversation length is the trap. A long thread can be engagement or a stuck user repeating the question. Split it by whether the task completed. A resolved ticket with a long thread and a refund that matches the policy is a different series from five turns of "that is not what I asked." Deletion is the weakest negative. ChatGPT lets a person delete a conversation. They also delete to tidy up, or to remove a sensitive paste. A deletion policy that treats every delete as a thumbs-down will chase privacy behavior as if it were quality.

None of these should be averaged into one "user unhappiness" score across products. Copilot has no regenerate button. Midjourney wants another image. A Zendesk draft wants the first answer to be sendable. The metric follows the job.

**Trade-offs.** Regenerate is dense and ambiguous. Edits are closer to a label and cost more to interpret, because you have to know whether the fact changed. Length is free and points both ways. Deletion is rare and confounded with privacy. Ignoring all four leaves you with thumbs, which are sparse. Feeding all four into one reward trains the model to avoid long conversations and second samples even when the product exists to produce them. Keeping the raw before-and-after text lets a later reviewer relabel. Keeping only a distance throws away that chance.

**Interview.** Give the four signals and one product where each one means something different. Regenerate in a support draft is a miss. Another grid in Midjourney is the product. An edit that changes a fact is a candidate pair. Length needs a completed-task split. Deletion is privacy as often as it is quality. Say you would not ship one blended unhappiness score across Copilot, Midjourney, and a help-center bot.

**Recap.** Regenerate, edit distance, conversation length, and deletion are feedback without a star rating. A regenerate is a failed first answer in a draft product and a requested extra sample in Midjourney. An edit that changes a fact is the useful pair. A long conversation is either engagement or a loop, depending on whether the task finished. A deletion is too confounded with privacy to train on alone.

## When to collect feedback

When to collect feedback is the moment the person can judge the thing you will actually change, and not a moment sooner.

Copilot asks for nothing. It records acceptance when the suggestion is on screen, which is the only moment acceptance is defined. A thumb on a ChatGPT answer belongs after the answer exists, not on the first token, because the person cannot judge a prefix you might still retract. A support bot can ask at two honest times, and they answer different questions. A rating on the draft says whether the draft was usable. A rating after the ticket resolves says whether the outcome was right. Collecting the second and calling it a draft score, or the reverse, is how a metric drifts away from the decision. You ask when you will use the answer. A survey nobody reads is a cost imposed on the user. You do not ask on every turn. Interruption has its own failure mode: people click the nearest star to make the widget leave.

Irreversible actions are the exception that is not a feedback question. The confirmation before a refund is the write gate in [RAG and Agents](../06_RAG_and_Agents/). A thumb after the refund has already moved the money is an evaluation of a mistake, not a prevention. Collect that thumb if you want the eval slice. Do not describe it as the control that stops the next bad refund. The control is the gate you already had.

Sampling is part of timing. A small random fraction of completed answers gets the explicit question, so the widget stays rare and the sample stays interpretable. Triggering the question only after a regenerate oversamples angry turns, which can be what you want for a hard-case review and is not what you want for a base rate. The interval card says how wide a rate is at a given sample. This card says whose answers enter the sample.

**Trade-offs.** Asking at the moment of use gets a relevant judgment and interrupts the task. Asking later gets a calmer user and a memory of a different event than the one you logged. Sampling keeps the product quiet and widens the interval. Asking everyone narrows the interval and trains people to dismiss the widget. A post-resolution survey measures the outcome and misses the draft you could have fixed. A draft survey does the opposite. Collecting both and adding them is a number with no meaning.

**Interview.** Tie the moment to the decision. Copilot records acceptance when the suggestion is visible. A chat thumb waits until the answer is complete. A refund asks a person before the money moves, and that dialog is the write gate, not a satisfaction survey. Say you sample explicit questions so the widget stays rare, and that sampling only the regenerates will not give you the base rate. Mention that a draft rating and an outcome rating are different series.

**Recap.** Collect feedback when the person can see the thing you might change, and when you will use what they tell you. Acceptance is recorded at the suggestion. A thumb waits for a finished answer. A refund is confirmed before it happens. Sample explicit questions. Do not add a draft score to an outcome score and call the sum quality.

## How to collect feedback

How to collect feedback is the design of the control: easy to ignore, specific enough to learn from, and ordered so the slot does not pick the winner.

Unobtrusive means the person can finish the task without the widget. A thumb at the corner of a ChatGPT answer, a keyboard accept in Copilot, an upscale button that is already the way Midjourney continues: the control is on the path of the work. A modal survey in the middle of a draft is the opposite. The comment box, if you need one, opens after a negative thumb, so the happy path stays one click and the unhappy path can carry the reason. A required essay on every answer collects essays from people who wanted the essay gone.

Comparisons are the higher-quality explicit signal. Two drafts, a person picks one. ChatGPT has collected that side-by-side preference as well as the single-answer thumb. Arena is the public product that is only that comparison, and the ranking cards in [Evaluation Methodology](../03_Evaluation_Methodology/) are how those votes become a rating. The UI rule that matters here is order. People and model judges both favor a slot. On the bias card there, GPT-4 kept the same verdict after a swap on 65.0 percent of the similar-answer probe, and the other judges in that table did worse. That 65.0 percent is a model-judge measurement on that probe. It is not a human click rate you can paste onto your UI. The direction is the part to copy: randomize which answer is on the left, or swap and keep the win only when the same answer wins both ways. A comparison that always puts the new model on the right measures the right-hand slot.

The control has to name the unit. A thumb on the whole conversation is not a thumb on the last turn. A preference between two answers that used different tools is not a clean model comparison. Hide the model name if you want the text judged, which is the same warning the comparative-evaluation card makes about brand preference.

**Trade-offs.** A single thumb is easy and thin. A comparison is informative and costs a second generation plus the person's time. Randomizing order removes a slot bias and complicates the analysis if you forget to log the order you showed. An optional comment is gold when it exists and missing most of the time. Forcing the comment reduces response and fills the box with periods. A delightful widget that takes over the screen measures obedience. A control so quiet that nobody finds it measures nothing.

**Interview.** Specify the control before the model. One thumb, optional reason only on the negative, or a pairwise pick with the side randomized and the side logged. Cite the 65.0 percent figure as the judge-probe result it is, and say you still randomize for people because the direction of slot bias does not depend on that percentage being theirs. Say you hide model names. Say the unit is the turn or the suggestion, and you log that unit's id with the vote.

**Recap.** The control sits on the path of the work and can be ignored. A thumb plus an optional reason on the negative is the small version. A side-by-side pick is the stronger one, with the order randomized or swapped, because slot bias is real for people and measured for judges. ChatGPT has used both patterns. Arena is the public comparison product. Log the unit, the order, and the template version with the vote.

## Feedback biases

A feedback bias is a systematic tilt in the signal, separate from the noise of one careless click.

Leniency is rating higher than behavior. People give a thumb up and then edit the draft heavily, or accept a Copilot suggestion and immediately delete it. The rating described a mood or a courtesy. The edit described the work. If you train on the thumb and ignore the edit, you train on the courtesy. Randomness is the click that is not a judgment: a mis-tap, a tired rater, a person clearing a widget. It widens the interval on the next card. It does not, by itself, move the average in one direction. The fix for noise is more independent judgments. The fix for bias is a change in the instrument, because more of a biased sample is a more precise biased sample.

Position is a preference for a slot. The left answer, the first image, the suggestion at the top of a list. The how-to-collect card randomizes order for this reason. Preference, in the narrower sense, is a taste the rater brings: longer answers, agreeable answers, answers in a familiar dialect, answers that match what the rater just said. Verbosity bias on the judge card is the model-shaped version of the length taste, and Arena's style control is the public regression that tries to partial it out. Human raters have the same taste. A reward that follows it will produce longer, warmer answers. That may be what the product wants. It is not evidence the window got more accurate.

The selection problem sits under all four. The people who rate are not the traffic. The acquiring-data card states that for thumbs and edits, and it is the reason a training file built from ratings needs a slice of silent sessions read on purpose. A bias you do not name becomes the objective.

**Trade-offs.** Correcting for leniency by ignoring thumbs throws away the only explicit signal some products have. Keeping thumbs and also logging the subsequent edit lets you see the gap. Randomizing order fixes position and does nothing for agreement bias. Style control on a public leaderboard is the right tool for a ranking and the wrong tool if your users truly want the longer answer: you then report both, which is the ranking card's advice. Dropping "noisy" raters can remove the minority who dislike a fluent wrong answer. An audit sample of people who did not click is expensive and is the only way to see the silent sessions.

**Interview.** Name the four tilts: leniency, randomness, position, and preference for length or agreement. Give the fix that matches each one. Behavior beside the thumb. More data for noise, and no hope that more data fixes a tilt. Randomize the slot. A factual check beside the preference, plus the style-control warning from the ranking cards. Say the raters are not the traffic, and point at Dataset Engineering for that selection bias rather than restating the label budget.

**Recap.** Leniency inflates ratings relative to later edits. Randomness adds noise and does not pick a direction. Position favors a slot, so the order has to move. Preference favors answers that are long, warm, or agreeable, which is a product choice only when you meant it. More ratings make a bias more precise. The people who respond are not the whole user base.

## A confidence interval on a thumb rate

A confidence interval on a thumb rate is the range the clicks you already collected can support, under a stated approximation.

It is not a plan for how many labels to buy before you look. That plan, for detecting 70 percent versus 73 percent accuracy with a two-sided 5 percent Wald test at 80 percent power, is 3,551 examples per independent arm on the unpooled formula and 3,554 when the significance term uses the pooled rate. Those two numbers stay on the annotation card in [Evaluate AI Systems](../04_Evaluate_AI_Systems/). They compare two rates. This card describes one rate you already have.

The exercise is 336 thumbs up out of 480 ratings. The rate is 0.70. The interval is a two-sided 95 percent Wald interval, the normal approximation, with no continuity correction. The standard-normal quantile is the same 1.959963984540054 the annotation card uses. The standard error is the square root of `p (1 − p) / n`. The annotation card says the normal approximation is the wrong picture when the miss count is a handful. Here there are 336 ups and 144 downs, which is past a handful and still far from a rate near 0 or 1, where a Wald interval can fall outside `[0, 1]` and should be replaced. It is also far smaller than that card's powered sample, which is a different formula.

```python
import math

Z_975 = 1.959963984540054
RATINGS = 480
THUMBS_UP = 336
# Exercise ratings, not a ChatGPT statistic.
rate = THUMBS_UP / RATINGS
standard_error = math.sqrt(rate * (1.0 - rate) / RATINGS)
margin = Z_975 * standard_error
# Ratings so a rate of 0.70 has a Wald margin of 0.03, rounded up.
needed = math.ceil(rate * (1.0 - rate) / (0.03 / Z_975) ** 2)
print(f"{rate:.2f} {margin:.4f} {rate - margin:.4f} {rate + margin:.4f} {needed}")
# 0.70 0.0410 0.6590 0.7410 897
```

The interval is 0.6590 to 0.7410. The margin is 0.0410, about four points. A week of 480 ratings cannot support a claim finer than that. Getting the margin down to 0.03 at this same rate takes 897 ratings. That 897 is still not 3,551. One is the sample that makes a single Wald interval ±3 points wide. The other is the sample that gives 80 percent power to detect a 3-point gap between two independent arms. A gap between two noisy rates is a harder question than the width of one rate, and the formulas are not interchangeable.

**Trade-offs.** Publishing the interval stops a one-point move from becoming a launch decision, and it invites a false sense of security when the 480 raters are a biased slice. The interval says how large the sampling noise is. It does not say the sample is the traffic. A Wald interval is easy to explain and poor near 0 and 1. Collecting 897 ratings narrows the margin and does nothing about leniency. Comparing this week to last week needs an interval on the difference, or the annotation card's test, not two overlapping glances.

**Interview.** Compute 336 out of 480 as 0.70, with a 95 percent Wald interval from 0.6590 to 0.7410 using the annotation card's quantile. Say 897 ratings are what a ±0.03 margin takes at this rate. Then refuse to equate 897 with 3,551. One is an interval width on a single rate. The other is power for a 3-point difference between two independent accuracy arms. Close with the bias: the interval assumes the 480 are the process you care about.

**Recap.** On 336 thumbs up out of 480 exercise ratings, the rate is 0.70 and the 95 percent Wald interval is 0.6590 to 0.7410, a margin of 0.0410. A ±0.03 margin at this rate needs 897 ratings. The annotation card's 3,551 per arm answers a different question, a powered comparison of 0.70 against 0.73. The interval measures noise. It does not repair a biased sample.

## Degenerate feedback loops

A degenerate feedback loop is a system that trains on behavior its own outputs created, and then produces more of that behavior.

Sycophancy is the loop in a chat product. People prefer answers that agree with them. A model tuned on that preference agrees more. The next round of thumbs rewards the agreement. Sharma and coauthors, in work published at ICLR 2024, studied this directly. Across five assistant models and four free-form tasks, the assistants echoed the user's stated view. In the preference data they examined, a response that matched the user's views was more likely to be chosen, and both people and preference models sometimes preferred a fluent sycophantic answer over a correct one. Optimizing against the preference model sometimes traded away truthfulness. Their own optimization sweeps did not raise every form of sycophancy, so "thumbs always make this worse on every axis" is stronger than the paper. The part to keep is the mechanism. A thumb that rewards agreement is a reward for agreement. A factual check has to sit in the objective if correctness is what you wanted.

Popularity bias is the same loop in a recommender. YouTube's homepage and Spotify's playlists show items. People play what is shown. The play becomes evidence the item should be shown again. The long tail, which was never shown, cannot collect the play that would have promoted it. The ranking looks confirmed by the data it created. Position feeds the loop: the first slot gets the click, the click justifies the first slot. Randomizing a slice of traffic, logging what was shown and not only what was clicked, and holding out items or prompts the loop cannot touch are the breaks. The eval set that training must not swallow, from [Dataset Engineering](../08_Dataset_Engineering/), is the holdout for the model. A canary set of user-wrong questions is the holdout for sycophancy. If those questions never enter the training file, the loop cannot grade itself on them.

**Trade-offs.** Training on real preferences makes the product feel better and can make it less truthful. Refusing to train on any user signal leaves a model that never learns your queue's actual requests. Exploration, showing a random slice, reduces popularity bias and spends impressions on worse items. A non-sycophantic reward that always contradicts the user is a product people abandon, which the paper's mixed sweeps already hint at: agreement is not the only feature in a preference. Logging exposure lets you debias and retains a record of what you showed. The degenerate failure is to notice the thumb rate rising and ship the checkpoint that caused it.

**Interview.** Explain the loop in both products. Chat: thumbs reward agreement, the next model agrees more, Sharma and coauthors showed preference data already leans that way and that optimization can cost truthfulness. Recommender: exposure creates the clicks that justify the exposure. Then give the breaks: a factual verifier in the reward, a canary of user-wrong items the training file cannot touch, logged exposure, and a random slice. Say you would not select the checkpoint by the thumb rate alone.

**Recap.** A degenerate loop trains on the behavior it just induced. Sycophancy is that loop for agreement: Sharma and coauthors found preference judgments favoring answers that match the user, and optimization that can trade away truth. Popularity bias is the loop for recommenders: shown items collect the clicks that keep them shown. Log exposure, keep a random slice, and keep an eval the feedback cannot rewrite. A rising thumb rate is not, by itself, a better model.

## Feedback and the data flywheel

The data flywheel is the path from a shipped product's feedback to the next prompt or the next model, closed by an eval the feedback is not allowed to rewrite.

The loop has a shape. Serve a pinned template and a pinned model. Collect a signal you defined: a comparison, an edit that changed a fact, an acceptance with the suggestion stored beside the final text. Redact it. Drop the cases the biases card says you cannot interpret, or label them so a later stage can. Turn the survivors into rows the trainer can read. The acquiring-data card in [Dataset Engineering](../08_Dataset_Engineering/) is that file: an edit is a preference pair when the edit is better, with the draft rejected and the edit chosen, and thumbs are not the traffic. The $3,125.00 exercise budget on that card is what a careful labeling pass costs. This card does not reprice it. Train or rewrite the prompt. Score the result on a frozen eval the new rows are not in. Ship only if that eval, the latency, and the cost still clear the bars on the maintenance card. A thumb rate whose 95 percent interval still runs from 0.6590 to 0.7410 is not that gate.

Consent and purpose bind the loop before any row is written. A suggestion a developer accepted is not a training example just because the product logged it. The terms, the retention, and the redaction have to allow the use. The model-collapse warning on the synthetic-data card is the other bound. A flywheel that trains only on its own outputs, with no remaining human text and no factual check, is the replacement regime that paper describes. A checked slice of edits mixed into data you still trust is a different mixture. The flywheel is useful because the traffic is real. It is dangerous because the traffic is also the model's previous mistakes, the user's misconceptions, and the positions you chose to show.

The product decision is which signals may enter. A pairwise comparison with logged order may enter, after the order bias is handled. An edit that changed a checked fact may enter. A bare thumb may enter a dashboard and may not enter the trainer alone. A deletion may not. Copilot acceptance may enter when you stored both the suggestion and the text the developer kept, and still only as a weak pair, because acceptance is lenient. The eval set stays out, which is the contamination rule you already have.

**Trade-offs.** A fast flywheel ships the queue's real requests and ships yesterday's sycophancy. A slow one, with a human on the slice, stays honest and arrives late. Training on edits improves the cases people bother to fix and ignores the silent wrong answers. Keeping the frozen eval stops a self-graded improvement and goes stale if you never add new canaries. Adding this week's incidents to the eval, and not to the training file, is how the eval keeps up without contaminating itself. Skipping the gateway's cost check lets a slightly better model double the bill. The flywheel is a production process with an owner, not a notebook that happened to fit.

**Interview.** Walk the loop in order: serve a pinned id, collect a defined signal, redact, filter, write the file Dataset Engineering already specifies, train or change the prompt, pass the eval the file cannot touch, then look at latency and cost. Say which signals may enter: a debiased comparison, a checked edit, a stored accept with its suggestion. Say a bare thumb, a deletion, and anything in the eval set may not. Mention consent, and mention model collapse as the bound on training from your own outputs alone. End with the gate. The thumb rate is not the gate.

**Recap.** The flywheel turns feedback into the next prompt or model only through redaction, a filter, a training file, and an eval that file cannot touch. Dataset Engineering owns the file, the bias that thumbs are not traffic, and the collapse warning. This topic owns which signals may enter: checked edits, debiased comparisons, and stored acceptances, not bare thumbs, deletions, or the eval set. A moved thumb rate is not a ship decision. The pinned eval, the latency, and the cost are.
