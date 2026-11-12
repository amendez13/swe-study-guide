## Evaluation criteria

Evaluation criteria are the properties a system has to have before you let a foundation model serve users. They answer what "good" means for this product, which is a different question from how you score one sample.

[Evaluation Methodology](../03_Evaluation_Methodology/) is the scoring toolkit: a program, a comparison to a reference, a model used as a judge, and a pairwise ranking. This topic is the list of properties those tools get pointed at, and the pipeline that turns the list into a launch gate. Four families cover a foundation-model product. Domain-specific capability asks whether the model can do this kind of work at all, the way a medical exam, a graduate science question, or a code change is a kind of work. Generation capability asks whether the text it just produced is acceptable: factually consistent with the source or with the world, and inside a written safety policy. Instruction-following asks whether it obeyed the request, including a role it was supposed to keep across many turns. Cost and latency ask whether the answer arrives at a price and a delay the interaction can stand.

The split matters because a model can pass one family and fail the product. GitHub Copilot can be a strong coder and still be the wrong model if the suggestion arrives after the developer has typed past it. A ChatGPT, Claude, or Gemini reply can be cheap and fluent and still be unusable if it invents a refund rule or complies with a request the product forbids. A Zendesk or Intercom bot is not the foundation model alone. It is a retriever, a prompt, a model, a safety filter, and a send button. A domain score on the model does not measure that pipeline. Public benchmarks, later in this topic, are evidence about a family. They are not a substitute for writing the four criteria down before you open a leaderboard. A board will always offer a number. The criteria decide which number you are allowed to care about.

| Family | The question it answers | Where a public number shows up |
| --- | --- | --- |
| Domain-specific capability | Can it do this kind of work, such as a graduate science question or a code change that has to pass tests? | MMLU and GPQA for knowledge. HumanEval and SWE-bench for code, scored the way the previous topic describes. |
| Generation capability | Is this text factually consistent, and is it inside the safety policy? | Factuality checks such as FActScore, and safety classifiers such as Llama Guard. |
| Instruction-following | Did it obey the constraints, including a role held across a conversation? | IFEval for constraints a program can check. A persona eval for a role. |
| Cost and latency | Does the answer arrive at a price and a delay this interaction can stand? | Time to first token, time per output token, and the provider's rate card. |

**Trade-offs.** A short criteria list keeps the launch review readable and misses the failure users actually write in about. A long list turns every model change into a month of labeling. Scoring only the model is cheap and blind to retrieval, tools, and the filter in front of the model. Scoring the whole product on one "helpfulness" grade hides which family failed. The useful list is the smallest set of properties a user would notice, each owned by one of the four families, each with a tool from the previous topic.

**Interview.** Name the four families and give a product that can pass three and still fail the fourth. A Copilot suggestion that is correct and late fails the latency budget. A support draft that is fast and polite and wrong about the return window fails generation quality. Then separate this list from the previous topic's tools: criteria say what you measure, and exact checks, judges, and pairwise votes say how. Close by refusing a leaderboard as the criteria. The board is an input to model selection after the criteria exist.

**Recap.** Evaluation criteria are the properties a system must have before it serves users. The four families are domain-specific capability, generation capability, instruction-following, and cost and latency. The previous topic is how you score a sample. This topic is which properties you score, on the system the user touches, before a public number is allowed to matter.

## Domain-specific capability

Domain-specific capability is how well a model does the work of one field, such as code, graduate science, medicine, or law, as opposed to how well it chats in general.

A general leaderboard mixes fields on purpose. That average is a poor guide to a product that lives in one field. MMLU, from Hendrycks and coauthors, is the multiple-choice exam people cite: 57 subjects spanning STEM, humanities, social sciences, and everyday knowledge. It became a standard, then a saturated one for frontier models, and later critiques found noisy and unanswerable items in it. MMLU-Pro keeps the multi-subject idea and makes the question harder, including by offering ten choices instead of four. GPQA, from Rein and coauthors, is a different bet: 448 expert-written questions in biology, physics, and chemistry, built so a quick web search does not hand the answer to a non-expert. Leaderboards usually quote the harder diamond subset, and the dataset is gated, which is a contamination control as well as a quality control. Neither exam is your support queue. A model that leads MMLU can still misread a Shopify returns article, and a model that is mediocre on GPQA can still be the right one for a help center.

Code is the domain where the previous topic already gave you a real oracle. HumanEval's 164 handwritten problems and SWE-bench's fail-to-pass patches are domain capability measured by execution, not by a multiple-choice letter. LiveCodeBench dates contest problems so you can drop anything released before a model's training cutoff, which is the contamination problem applied to this domain. A domain-specific model is the other way to chase the same gap. Codex, Code Llama, StarCoder, BloombergGPT, and Med-PaLM are the examples in [Understanding Foundation Models](../02_Understanding_Foundation_Models/). You only learn whether the specialized checkpoint was worth it by scoring it against a general model on your tasks, with the field's own failure mode. A fabricated drug dose and a fabricated citation are domain failures a generic helpfulness grade describes badly.

Multiple choice is the trap inside this family. MMLU and GPQA ask the model to pick a letter. Your product asks it to write the answer, call a tool, or edit a repository. A strong letter grade can sit next to a weak free-form answer, because the choices leaked hints and the grader never saw the prose. Use the public exam to throw out models that cannot do the field at all. Use a set drawn from your own work, graded by the method that field actually requires, before you treat the model as capable.

**Trade-offs.** A public exam is cheap, comparable, and increasingly saturated or contaminated. A private domain set matches the product and costs experts, which is painful in medicine, law, and finance where the rater is expensive. A specialized checkpoint can beat a general model of similar size on the field's distribution and then lose the moment the fact has to come from a document you supply. Retrieval, not a domain pretrain, owns the fact that changed on Monday.

**Interview.** Separate a public knowledge exam from the product task. Name MMLU as the 57-subject multiple-choice set that frontier models have saturated, GPQA as gated graduate science written to resist a quick search, and HumanEval or SWE-bench as domain tests with an execution oracle. Say a letter grade is not a written answer. Then say how you would actually decide: screen with the public exam, ship on a private set graded the way the field fails.

**Recap.** Domain-specific capability is performance on one field's work. MMLU and MMLU-Pro measure broad multiple-choice knowledge, GPQA measures graduate science that search does not trivially solve, and HumanEval, SWE-bench, and LiveCodeBench measure code by running it. A public exam can reject a model that cannot do the field. The launch number is a private set, graded in the form the product actually produces.

## Factual consistency

Factual consistency means the claims in a generation are supported. Local consistency means the source you provided supports them. Global consistency means the world does.

The two checks exist because products promise different things. Perplexity and NotebookLM promise that a statement is tied to material they retrieved or that you uploaded. Gmail's summary of a thread and Notion AI's summary of a page promise the same thing about a document the user can see. A bare ChatGPT answer to "what is the capital of France" has no document in the prompt. It promises the world, not a paragraph. Literature also calls the local check faithfulness and the global check factuality. The names differ. The split does not. A claim can pass one and fail the other. If the retrieved help-center page is out of date and the model repeats it, the answer is locally consistent and globally wrong. If the model adds a true fact that the page never stated, a "use only the article" bot is locally unfaithful even though the fact is true. The product promise picks which failure counts.

Local checking is an entailment problem. Split the answer into claims. For each claim, the source is the premise and the claim is the hypothesis. An NLI model, a small entailment classifier or the judge pattern from the previous topic pointed at one claim and the source, returns entailed, contradicted, or unsupported. Entailed passes. Contradicted fails. Unsupported fails when the product promised to stay inside the source, and it is a separate decision when the product allows the model to add common knowledge. Numbers and dates stay on an exact check even if an entailment model likes the sentence. A claim that needs two sentences of the source can look unsupported to a checker that only reads one sentence, so the unit of the premise is part of the metric.

Global checking needs a source outside the prompt. Three public patterns cover the usual budgets. SelfCheckGPT, from Manakul, Liusie, and Gales, samples several answers and treats a claim that changes across samples as a hallucination candidate. It needs no retrieval. It fails when the model is confidently wrong, because a memorized falsehood is stable, and it fails when the sampler is deterministic, because nothing varies. FActScore, from Min and coauthors, splits a long biography into atomic facts and scores the fraction a knowledge source supports. The paper used Wikipedia. The same split-and-check idea is how you score other long-form answers, and the published number is about that biography setup. SAFE, the search-augmented factuality evaluator from Wei and coauthors, has the model propose searches, read the results, and judge support. It can check claims the prompt never contained. It spends extra model calls, and the pages it finds can be stale or wrong. A stable SelfCheckGPT claim still gets a FActScore or SAFE pass only if the product promised the world.

```python
SOURCE = "the package ships on 12 May and the refund cap is 40 dollars"
CLAIMS = (
    ("the package ships on 12 May", "entailed"),
    ("the package ships on 12 June", "contradicted"),
    ("the carrier is a national parcel service", "unsupported"),
)


def local_verdict(label: str, must_stay_in_source: bool) -> str:
    if label == "entailed":
        return "pass"
    if label == "contradicted":
        return "fail"
    if must_stay_in_source:
        return "fail"
    return "needs a world check"


print([local_verdict(label, True) for _, label in CLAIMS])
print([local_verdict(label, False) for _, label in CLAIMS])
# ['pass', 'fail', 'fail']
# ['pass', 'fail', 'needs a world check']
```

The third claim is the whole distinction. A grounded Gmail summary fails it, because the thread never named a carrier. A general assistant does not fail it yet. That claim goes to a world check, and the date goes to an exact comparison with the thread either way. Hallucination, in the previous topic's sampling card, is the generation behavior. This card is how you detect it after the fact.

**Trade-offs.** Entailment against a source is the right gate for retrieval products and says nothing about a claim the source itself got wrong. Self-consistency is cheap and blind to confident errors. Search-augmented checking reaches the open web and inherits the web's mistakes, plus a larger bill. Atomic-fact scoring punishes a harmless paraphrase less than a sentence-level grade does, and it over-penalizes when the split produces a fragment that was never a claim. Checking every claim of every production answer is the thorough pipeline and often costs more than generating the answer.

**Interview.** Define local and global with one sentence each, then give a claim that is locally faithful and globally false, and a claim that is globally true and locally unfaithful. Name the three tools: NLI or a source-bound judge, SelfCheckGPT's sample agreement, and a search or encyclopedia check in the FActScore and SAFE line. Say a zero-temperature sample has no SelfCheckGPT signal, and that a date still wants an exact match. The previous topic's judge is the mechanism. This card is which question you ask it.

**Recap.** Factual consistency asks whether claims are supported. Local consistency checks the source you provided, usually with an entailment judgment, and global consistency checks the world with sample agreement or with retrieval against Wikipedia or the web. A grounded product fails unsupported claims. A general assistant sends those claims to a world check. A wrong date fails both, on an exact comparison.

## Safety

Safety, as an evaluation criterion, means the system refuses the harms its policy forbids and still answers the requests that policy allows.

Generation capability includes this next to factual consistency because both are properties of the text, not of a domain exam. The lists people actually ship are taxonomies. Llama Guard, from Meta, is a classifier model: it reads a prompt, a response, or both, and labels the text as safe or as one hazard. Later Llama Guard checkpoints follow the MLCommons hazard taxonomy, so the label set is a published list rather than a private vibe. The OpenAI moderation endpoint is the hosted version of the same idea, a separate classifier in front of or behind the generator. Typical hazard families in these taxonomies are violent crime, non-violent crime, sexual content, child sexual exploitation, hate, self-harm, and privacy violations such as leaking or inferring personal data. Naming the category is the evaluation. The evaluation does not need an example of the harm.

A taxonomy is not your policy. A patient-portal assistant has to be able to discuss hopelessness far enough to route someone to help, and a children's product has to refuse more than a developer tool does. Gemma's prohibited-use policy and Llama's acceptable-use policy are license constraints on the model. The product policy is the document your reviewers hold. Where they disagree, the stricter rule that actually applies to you wins, and you write that down so the raters are not guessing. Over-refusal is the other failure. XSTest is a public check for exaggerated safety: benign requests that merely look adjacent to a hazard, which a nervous model refuses. A support bot that refuses "how do I cancel" because the word sits near a policy keyword is a product bug, measured on a set of allowed prompts, not only on a set of disallowed ones.

The system under test includes the filter. A safe generator behind a filter that never fires, and an unsafe generator behind a filter that catches it, are different systems with the same final text on the cases you remembered to try. Log the classifier's label and the model's raw reply. Adversarial sets such as HarmBench exist because a sample of ordinary prompts underestimates a user who is trying to get past the policy. You cite the benchmark and you do not need to paste an attack into the study notes. TruthfulQA, from Lin, Hilton, and Evans, is adjacent and easy to misfile here. It measures whether models repeat common human misconceptions. That is imitative falsehood, a factuality problem, not a hazard taxonomy. It belonged on the old Open LLM Leaderboard for that reason. It is not a safety gate.

**Trade-offs.** A dedicated classifier is cheaper and more stable than asking a frontier model "is this safe?" on every turn, and it only knows the hazards it was trained on. A frontier judge catches odd cases and drifts, and it is the judge from the previous topic with a safety rubric. Blocking on the classifier reduces harm and creates the refusal tail XSTest is about. Letting the generator answer and reviewing later is how a consumer chat learns, and it is a poor fit for a product that cannot show the harm even once. Evaluating only benign traffic reports a flattering safety rate.

**Interview.** Separate the hazard taxonomy, the license's acceptable-use rules, and the product policy. Name Llama Guard and a hosted moderation endpoint as classifiers, and say you score both the raw model and the filter. Pair a harm set with an over-refusal set, and name XSTest as the public form of the second. Put TruthfulQA on the factuality side of the line. Say an adversarial benchmark is part of the number you quote, without describing an attack.

**Recap.** Safety evaluation checks that the system refuses the harms its policy forbids and still answers what that policy allows. Llama Guard and hosted moderation classifiers label text against a hazard taxonomy such as MLCommons. The product policy can be stricter or more permissive than the license, and over-refusal is its own set. Score the filter and the generator, on ordinary prompts and on adversarial ones.

## Instruction following

Instruction following is the model's obedience to constraints that were stated in the request: a format, a length, a required phrase, a forbidden topic, an order of sections.

The criterion exists because a capable model still skips the one constraint the product needed. A Shopify support macro that must mention the refund window, stay under a length the SMS gateway will accept, and avoid promising a replacement is three instructions. Domain knowledge does not grade them. IFEval, from Zhou and coauthors at Google, is the public benchmark that grades this with a program. The paper identifies 25 types of verifiable instruction, things like "use more than this many words," "mention this keyword at least this many times," or "end with this sentence," and builds around 500 prompts, some with several instructions at once. A program decides each one. There is no judge in the headline number.

IFEval reports four accuracies, and the differences are the design. Prompt-level accuracy counts a prompt as passed only when every instruction in it passed. Instruction-level accuracy counts each instruction on its own, so a prompt that hits two constraints out of three still contributes. Strict scoring runs the check on the raw text. Loose scoring tries the check again after a few surface cleanups. The paper uses eight variants, built from leaving the text alone, stripping markdown emphasis, dropping the first line, dropping the last line, and combining those. Loose scoring rescues a reply that followed the instruction and wrapped it in "Sure, here it is" or in bold. It can also create a false pass, for example when dropping the first line is what brings a word-count instruction under the limit. Quote the level. A prompt-level strict number is the one that matches a product where any missed constraint is a broken message. An instruction-level loose number is a friendlier diagnostic and a weaker gate.

Your own macros are the same shape and a different set. IFEval's keyword and length checks are synthetic. "Do not promise a refund the article refuses" is verifiable once the article is in the grader, and it will not appear in IFEval. Constrained decoding changes who deserves the credit. The structured-output card in [Understanding Foundation Models](../02_Understanding_Foundation_Models/) is the mechanism: a schema mask can force JSON no matter how weak the model's instruction following is. When the decoder enforces the format, the format metric moves onto the decoder, and the model is graded on the values inside it. Grading the model on "output JSON" after you masked the grammar measures your parser.

```python
def word_count_at_most(text: str, limit: int) -> bool:
    return len(text.split()) <= limit


def contains_keyword(text: str, keyword: str) -> bool:
    return keyword.lower() in text.lower()


def prompt_and_instruction(text: str) -> tuple[bool, float]:
    checks = (
        word_count_at_most(text, 12),
        contains_keyword(text, "refund"),
    )
    return all(checks), sum(checks) / len(checks)


long_reply = (
    "We can refund the shipping charge. Please reply with the order number "
    "so we can look it up today and confirm the amount."
)
short_reply = "Yes, we can refund shipping today."
print(len(long_reply.split()), prompt_and_instruction(long_reply))
print(len(short_reply.split()), prompt_and_instruction(short_reply))
# 23 (False, 0.5)
# 6 (True, 1.0)
```

The long reply contains the keyword and runs past the length, so instruction-level accuracy is one half and prompt-level accuracy is a fail. The short reply passes both instructions, so both levels pass. That is the whole IFEval distinction, on a support macro instead of the public set.

**Trade-offs.** Verifiable instructions are repeatable and they ignore tone, truth, and whether the constraint was a good idea. A judge can grade "sound like our help center" and reintroduces every bias in the previous topic. Prompt-level scoring matches a product that needs all the constraints and looks harsher than instruction-level scoring on the same outputs. Loose scoring reduces silly failures and hides real ones. Synthetic IFEval success can coexist with failure on the messy instruction your prompt actually uses.

**Interview.** Define prompt-level versus instruction-level, and strict versus loose, and say which one you would gate on when any missed constraint breaks the message. Mention IFEval's scale, about 500 prompts and 25 verifiable types, without quoting a model score from the paper as if it were this year's board. Then say where you stop using it: a schema mask owns the JSON check, and a policy constraint owns a grader you wrote against the article.

**Recap.** Instruction following measures obedience to stated constraints. IFEval grades about 500 prompts across 25 verifiable instruction types with a program, at prompt level or instruction level, strict or loose. Prompt-level strict is the gate when every constraint matters. A format that your decoder already enforces is the decoder's metric, and the model's remaining job is the values and the constraints IFEval does not contain.

## Roleplaying

Roleplaying evaluation measures whether a model holds a stated persona, brand voice, or role across a conversation, rather than only in a single reply.

Instruction following grades constraints a program can usually see in one message. A role is a constraint that has to survive turn twelve. Character.AI is the consumer product built on that survival. A custom GPT is the same idea with a shorter instruction card. A brand voice on an Intercom bot is the same idea again, with a narrower character: the shop's assistant, not a general chatbot, even when the user asks it to be one. The failures are specific. The persona drifts into a generic assistant. It contradicts a preference the user set on the first turn, or a fact the persona card committed to. It reveals the hidden instruction text. It refuses a request the role should have handled, or it accepts one the role forbids. None of those shows up in a one-turn IFEval prompt about word count.

You score the session. A turn-level average flatters a conversation that was in character for five replies and then leaked the system prompt on the sixth. The leak is an exact check: the hidden text, or a distinctive substring of it, appeared in the user-visible reply. That check does not need a judge, and a single leak is a product and security failure rather than a style quibble. Prompt injection, the later topic, is how a user pushes for that leak. This card only needs the detection. Voice and drift are judgments. The judge from the previous topic can grade "still the shop assistant, still not a general chatbot" against the persona card, on a full transcript, after you have calibrated it on a human slice. The persona card itself has to be concrete enough that two raters can agree. "Be helpful and fun" is not a role. "You are the shop assistant. You do not invent a discount. You do not discuss a competitor's price" is a role, and the discount ban is verifiable on top of the voice judgment.

Multi-turn also changes the data you store. A single exported reply cannot show that turn one forbade a topic and turn four raised it. The transcript, including the persona card and the tool outputs the model saw, is the example. A conversation passes when every exact check passed and the voice judgment passed. Averaging turns is a diagnostic for where it drifted. It is not the launch number for a companion or a brand bot, because the user experienced the session.

**Trade-offs.** Session-level grading matches the product and costs more labels per example than a single-turn benchmark. A harsh exact check on leaks and forbidden topics is the part you can automate. A voice judge covers the residue and needs the same calibration as any other judge. Freezing a persona card makes scores comparable across model changes and falls behind when the brand voice is edited. Grading one golden reply misses the drift that shows up only after the user pushes.

**Interview.** Separate a verifiable instruction from a role that has to hold for a session. Name Character.AI, a custom GPT, and a brand-voice support bot as the same evaluation shape with different cards. Say the system-prompt leak is an exact fail, and the voice is a judge you calibrate. Give the metric as the fraction of conversations that stayed inside the card, not the fraction of turns that sounded fine. A turn average is how you debug a session that failed.

**Recap.** Roleplaying evaluation checks that a persona, brand voice, or role survives the whole conversation. Character.AI, custom GPTs, and brand-voice support bots are the products. Leaks of hidden instructions and violations of explicit bans are exact checks. Voice and drift are judged on the transcript. The launch number is the session, because one broken turn is the conversation the user had.

## Cost and latency

Cost and latency are the price and the delay of producing an answer. They are evaluation criteria because a correct answer that arrives too late, or at a price the product cannot pay, does not ship.

Two clocks describe a streamed generation. Time to first token, TTFT, is the wait from the request until the first output token is available. It includes queueing and the prefill that reads the prompt, so a long RAG context makes it worse even when the model is fixed. Time per output token, TPOT, is the average gap between later tokens, also called inter-token latency. This topic uses the convention that TTFT already includes the first token, so a reply of N output tokens takes `TTFT + TPOT × (N − 1)`. A vendor that defines TPOT as total decode time divided by N, first token included, is using a different formula. Reconcile the definitions before you compare two dashboards. Throughput is a third number and it is not the reciprocal of TPOT. One stream at 50 tokens a second is that user's decode rate. A server batching many requests can produce more aggregate tokens per second while each user's TPOT gets worse. vLLM and the public latency boards report these separately because they move differently. Artificial Analysis and the vendors' own dashboards are useful and they move, so you cite the date.

The bill is the rate card times the tokens. Input and output are usually different prices, and both prices move, so every dollar below is an exercise rate for the arithmetic, not a quote you would sign. Take a RAG-shaped call with 3,000 input tokens and 500 output tokens. A smaller hosted model at $0.25 per million input tokens and $0.75 per million output tokens costs $1.125 per 1,000 requests. A frontier hosted model at $5 and $15 on the same units costs $22.50 per 1,000 requests. On both cards the 3,000-token prompt is the larger line, $0.75 versus $0.375 on the small card and $15 versus $7.50 on the frontier card, because the prompt is six times longer and the output price is only three times the input price. A shorter prompt or a much wider output gap would flip which line dominates. Recompute from the current card before either total enters a budget.

```python
TTFT_SECONDS = 0.400
TPOT_SECONDS = 0.020
OUTPUT_TOKENS = 500
INPUT_TOKENS = 3_000


def latency_seconds(tokens: int) -> float:
    return TTFT_SECONDS + TPOT_SECONDS * (tokens - 1)


def cost_per_thousand(input_rate: float, output_rate: float) -> tuple[float, float, float]:
    input_cost = 1_000 * INPUT_TOKENS / 1_000_000 * input_rate
    output_cost = 1_000 * OUTPUT_TOKENS / 1_000_000 * output_rate
    return input_cost, output_cost, input_cost + output_cost


wait = latency_seconds(OUTPUT_TOKENS)
small = cost_per_thousand(0.25, 0.75)
frontier = cost_per_thousand(5.00, 15.00)
print(f"{wait:.2f} {1 / TPOT_SECONDS:.1f} {OUTPUT_TOKENS / wait:.2f}")
print(f"{small[0]:.3f} {small[1]:.3f} {small[2]:.3f}")
print(f"{frontier[0]:.3f} {frontier[1]:.3f} {frontier[2]:.3f}")
# 10.38 50.0 48.17
# 0.750 0.375 1.125
# 15.000 7.500 22.500
```

The 500-token answer takes 10.38 seconds. The decode rate on that stream is 50 tokens a second, and the end-to-end rate is 48.17, because the 0.400 seconds of TTFT sit in the denominator and produce no extra tokens. A chat UI that streams can show the first token at 0.4 seconds and let the user read along. A tool call, a voice utterance, or a grading script that waits for the full string waits 10.38 seconds. Those are different product metrics on the same generation. Quality trades against both clocks. The test-time compute card in the previous topic, the o1 and DeepSeek-R1 pattern, spends extra tokens and extra seconds when a verifier can reject a bad answer. Inline ghost text in Copilot cannot spend them. A nightly batch classification can. [Inference Optimization](../09_Inference_Optimization/) is where batching, quantization, and the kernels that move TTFT and TPOT actually get built. Here you only need the numbers that decide whether a model is eligible.

**Trade-offs.** Streaming optimizes TTFT and TPOT and does nothing for a consumer that cannot act until the last token. Chasing throughput with a large batch helps the cluster's token count and hurts the interactive tail. A frontier model can be worth $22.50 per 1,000 calls on the hard slice and a waste on the easy slice a $1.125 model already passes. Quoting decode tokens per second as if it were the user's wait ignores TTFT. Quoting a rate card without the token mix ignores the line that actually dominates.

**Interview.** Write `TTFT + TPOT × (N − 1)` and compute a 500-token answer at 0.400 and 0.020 seconds, which is 10.38 seconds. Distinguish that wait from the 50 token-per-second decode rate, and from cluster throughput. Then price 1,000 RAG-shaped calls on two exercise cards, $1.125 against $22.50, and say which line is larger and why. Finish with the product: ghost text, a streamed chat, a voice reply, and a batch job do not share a latency budget, so they do not share a winner.

**Recap.** Cost and latency decide whether a correct answer is usable. TTFT waits for the first token and TPOT spaces out the rest, so 500 tokens at 0.400 seconds and 0.020 seconds take 10.38 seconds. Per 1,000 requests of 3,000 input tokens and 500 output tokens, the exercise cards cost $1.125 and $22.50, and the long prompt is the larger line on both. Prices, dashboards, and which model is fastest all move. The formula and the token mix are what you recompute.

## Model selection workflow

A model selection workflow turns the criteria into a shortlist and then into a choice. It filters on hard attributes, ranks what remains on soft ones, and repeats when a measurement proves an attribute was mislabeled.

Hard attributes are pass or fail, and a failure removes the model no matter how strong its demo was. The context window has to hold the prompt you actually send. The license has to allow the product. The data-handling terms have to match the regulation you are under. The model has to support the modality and the tool calls you will invoke. It has to serve the languages you launch in. It has to meet the latency budget of the interaction, which is a hard attribute for inline code and a soft one for an overnight report. Soft attributes are the ones you rank: quality on your eval, dollar cost, how hard the API is to operate, how often you want to ride a vendor's upgrades. Mixing the two is how a leaderboard picks a model you are not allowed to deploy.

The order is the method. Write the hard attributes from the product before you look at scores. Drop every candidate that fails one. Use public benchmarks only inside the survivors, and only the benchmarks that match a criterion you wrote down, to cut the survivors to a handful. Run the private eval on that handful. Then iterate. A winner that fails Spanish, when Spanish is a launch language, does not get a waiver. Spanish moves from an unspoken hope into the hard filter and you rerun the filter. A winner that is excellent and three times the latency budget for Copilot-style ghost text is the same shape of mistake. The latency budget was hard, and a coding-benchmark lead does not relax it. The private eval can also show that a soft attribute should have been hard, or that a hard attribute was superstition. Change the list explicitly. Do not keep the chart and quietly ignore a row.

GitHub Copilot's inline suggestions are the worked shape, as a workflow rather than a claim about which model GitHub serves. Hard: the suggestion must start inside the pause a developer will wait, the license must allow the product, and the context must hold the file and the cursor. Soft: acceptance rate on your snippets, cost per suggestion, and how painful the model is to host. A frontier chat model that leads a code leaderboard and misses the pause is out before its score is discussed. Two models that both return a suggestion in time are then compared on acceptance rate, not on a general chat ranking. The next card's build-versus-buy decision sits inside the same filter. "Must stay in our VPC" is a hard attribute that removes every multi-tenant API, however strong.

**Trade-offs.** A strict hard filter avoids models you are not allowed to ship, and models that cannot serve the interaction, and it can leave you with a weak survivor set. Loosening a constraint to admit a better model is legitimate when you change the constraint in writing. A public benchmark as a soft rank is a cheap shortlist and a bad final exam. Skipping the private eval because the shortlist has an obvious leader is how a contaminated or off-domain score becomes the launch. Iterating the attribute list makes the decision honest and makes an old spreadsheet incomparable, so you version the list with the result.

**Interview.** Define a hard attribute as a pass or fail that removes a model, and a soft attribute as a rank among the models that remain. Walk the order: write the constraints, filter, narrow with a relevant public number, run your eval, and move an attribute between the two lists only on purpose. Use inline code as the latency example. If the interviewer offers you a model that leads MMLU and fails a constraint, the answer is that it is out.

**Recap.** Model selection filters on hard attributes, ranks the survivors on soft ones, and checks the ranking with a private eval. Context, license, data handling, modality, language, and sometimes latency are hard. Quality and cost are usually soft. A failed constraint removes a model before its leaderboard score is allowed to argue. When a measurement shows the list was wrong, you change the list and run the filter again.

## Build versus buy

Build versus buy is the choice of who produces the checkpoint you call: a lab you run, or a provider you pay.

For almost every application team the checkpoint is bought. Buying an API from OpenAI, Anthropic, or Google buys a frontier model, elastic capacity, and a vendor that can change behavior under a name you thought you had pinned. Buying a hosted open-weight model from a serving company, or from a cloud such as Amazon Bedrock, buys a checkpoint you can name and a vendor who runs the GPUs. Building, in this chapter, means pretraining or continuing a base model yourself. BloombergGPT is the public example of a domain pretrain from scratch, and Med-PaLM is the public example of adapting a general model instead. The sizes and the mixes live in the foundation-model topic. The decision here is whether your team should be in that business. Almost always, no. You do not have the corpus, the GPU pool, or a quality gap that a prompt and a retrieved document leave on the table.

What you do build is the product around a checkpoint you bought. The introduction topic's levers stay in force and this card does not restate them. You prompt when the task is in the request, you retrieve when the fact is private or changing, and you finetune when a behavior will not stick and you have the examples. A finetune is a hybrid: you bought the base and you built a behavior on top. [Finetuning](../07_Finetuning/) is the training stack. A finetune does not replace retrieval for a policy that changed this morning, and a pretrain does not either. The eval in the rest of this topic is also something you build. Buying the model and borrowing the vendor's blog-post score is how the selection workflow fails.

The reversible line is the practical one. Swapping an API model, or a hosted checkpoint, is a selection rerun. Pretraining a 70-billion-parameter model because last quarter's API bill was annoying is not reversible on the timescale of a product change. Start from the hard attributes. If one of them is "no prompt can leave our network," you are not buying a multi-tenant API, and the next card is the hosting choice among models you can actually run. If none of them forces you to own the weights, buy the call and spend the effort on the private eval.

**Trade-offs.** An API is the fastest way to a strong model and the weakest way to control data, lineage, and price at high volume. A hosted open checkpoint sits in between and still sends text to someone else's fleet unless the contract says otherwise. Pretraining buys a model shaped to a corpus you believe is an advantage, and it buys a permanent training and serving organization. Finetuning is the narrow build that application teams actually finish. Skipping it when the behavior will not stick leaves quality on the table. Doing it when the gap was a missing document bakes today's document into the weights.

**Interview.** Put pretraining on the far side of the line and name BloombergGPT as the rare from-scratch domain model, without reciting its parameter count from memory unless you have the paper's table in front of you. Put the application team's job on the near side: choose, adapt, evaluate, and operate a checkpoint someone else trained. Say a finetune is build-on-a-purchase, and that a daily-changing fact stays in retrieval. If the hard attribute is data residency, the buy is a checkpoint you can run, not a multi-tenant API.

**Recap.** Build versus buy asks who produces the checkpoint. Application teams buy an API or a hosted open model, and they build the prompts, the retrieval, the tools, and the evaluation. Pretraining a base model is a separate project, and BloombergGPT is the kind of exception that proves how rare it is. A finetune builds a behavior on weights you bought. It does not replace a document that changes.

## Open weights and licenses

Open weights, open source, and a model license are three different claims about what you are allowed to do with a checkpoint. The file next to the weights is the claim that counts.

Open weights means you can download the parameters. Open source, for software, means an OSI-approved license that lets you use, study, modify, and share the work without a field-of-use restriction. In October 2024 the Open Source Initiative adopted version 1.0 of the Open Source AI Definition. For a machine-learning system, the preferred form of the work includes three pieces: data information detailed enough that a skilled person could build a substantially equivalent system, the code used to train and run it, and the parameters. The definition also says that "open source weights" in that sense include the data information and the code those weights came from. A weight file with a custom license is not that artifact. Weights can be public and still forbid uses, require a separate commercial grant, or withhold the training data. Calling every downloadable checkpoint open source is how a legal review starts from the wrong document.

The licenses you actually meet divide the shortlist. Apache 2.0 is a permissive OSI license with an explicit patent grant, attribution, and a NOTICE duty. MIT is a shorter permissive license. It allows commercial use and modification, and it does not carry Apache's patent grant. Mistral 7B is a widely cited Apache 2.0 weight release. Later checkpoints from the same lab have shipped under different terms, so the license is a property of the checkpoint, not of the brand. Allen AI's OLMo releases are the public example of publishing training data and training code along with weights, which is the direction the OSI definition is pointing, without this card certifying any particular release against that definition. The Llama community license is the well-known middle case. The Llama 3 community license grants use, modification, and redistribution, and then adds terms an OSI license does not. One of them is the 700 million monthly-active-user clause. It is a snapshot, not a meter: if, on that version's release date, the licensee's products or affiliates already had more than 700 million monthly active users in the preceding calendar month, the grant does not apply until Meta agrees to a separate license. A company that is small on that date does not lose the grant by growing later. The same Llama 3 text also restricts using the materials or their outputs to improve a non-Llama language model, and it incorporates an acceptable-use policy. Later Meta licenses have revised wording, so you read the file that shipped with the weights you will run. Gemma's weights are downloadable under the Gemma Terms of Use. Those terms are not Apache 2.0. They incorporate a prohibited-use policy and require the restrictions to travel with derivatives. A prohibited-use list is exactly the kind of field restriction an OSI-approved license does not impose.

| What you downloaded | What you can honestly call it | The check before you ship |
| --- | --- | --- |
| Weights, training code, and data information under OSI-approved terms, matching the Open Source AI Definition. | Open source, in the OSI's sense for an AI system. | Confirm the data information is actually sufficient, and that no extra terms ban a field of use. |
| An Apache 2.0 or MIT weight file, without the training data. | Open-weight under a permissive software license. | Attribution, NOTICE, and the patent terms. The missing data means it is not the OSI AI definition by weights alone. |
| Llama weights under the community license. | Open-weight under a custom license. | The 700 million MAU snapshot, the acceptable-use policy, and any restriction on training other models. Read the version you pin. |
| Gemma weights under Google's terms. | Open-weight under custom terms. | The prohibited-use policy and the duty to pass it downstream. |
| An API with no weights. | A service. | The contract: retention, training on your prompts, regions, and whether the model id stays put. |

A selection workflow treats the license as a hard attribute. An ordinary company's product can use Llama weights and never approach the user-count gate. A product that needs to train a different model on Llama outputs cannot, under the Llama 3 wording. A product that needs an OSI-approved license in the procurement spreadsheet cannot clear that spreadsheet with Gemma terms or the Llama community license, however good the checkpoint is.

**Trade-offs.** Permissive licenses are the easiest procurement and they do not magically include the training data. Custom open-weight licenses get you strong models and a review every time the vendor revises the file. Refusing anything that is not Apache 2.0 shrinks the shortlist and simplifies legal review. Treating "the weights are on Hugging Face" as a license skips the only document that matters. The OSI definition is a precise bar and it is stricter than the way most model cards use the word open.

**Interview.** Define open weights as downloadable parameters and open source as the OSI freedoms plus, for the 2024 AI definition, data information and code as well as weights. State the Llama 3 700 million MAU clause as a snapshot on the release date, not as a counter that trips when a startup later grows. Contrast Apache 2.0, which is a permissive OSI license with a patent grant, with Gemma's terms, which carry a prohibited-use policy. End with the process: the license file on the pinned checkpoint is a hard filter, read before the benchmark score.

**Recap.** Open weights means the parameters are downloadable. Open source, under the OSI's October 2024 AI definition, also means enough data information and code for a skilled person to rebuild a substantially equivalent system, under terms that do not ban a field of use. Apache 2.0 and MIT are permissive licenses. The Llama 3 community license adds a 700 million monthly-active-user snapshot and other restrictions. Gemma ships under its own terms and prohibited-use policy. The license on the checkpoint you will run is a hard attribute.

## Self-hosting and model APIs

Self-hosting means you run the weights on infrastructure you control. A model API means a provider runs a model and you send it requests. The choice is how the hard attributes of privacy, lineage, and control trade against performance, features, and cost.

Data privacy is the first split. A multi-tenant API receives the prompt. An enterprise contract can add no-training and a retention limit, which is a promise about a copy someone else holds. Self-hosting keeps the prompt in your VPC, which is the attribute a bank or a hospital often writes down as hard. On-device models go one step further. Gemini Nano runs on phones. Apple Intelligence runs some models on the device and sends some requests to Private Cloud Compute. The device path works offline and keeps those prompts off your server as well as off a model vendor's. The model is smaller, the context is shorter, and shipping weights inside an app binary requires a license that allows redistribution.

Lineage is whether tomorrow's call is the model you evaluated. An API product name can move underneath you. The maintenance card in the introduction topic is the pin: a dated model id, and a regression run when it changes. Chatbot Arena split GPT-4-0314 from GPT-4-0613 because the name was not the checkpoint. A self-hosted weight file has a hash. The hash does not move unless you move it. Hosted open-weight services sit in between. You can pin a public checkpoint only when the host actually serves that hash and says so.

Performance and functionality do not fall out of the privacy choice. A large vendor fleet is often faster, on TTFT and on aggregate throughput, than a GPU you stood up for a popular model. It can also be slower for your region, your batch window, or a latency SLO the shared tier will not sign. Measure both. Features land on APIs early: vision, tool calling, JSON mode, prompt caching, batch endpoints. Open weights catch up unevenly, and you can finetune and quantize them, which a closed API allows only to the extent the vendor's finetune program allows. Control is the same axis. On your GPUs you pick the sampler, the log retention, the filter, and the day you upgrade. On an API you pick among the switches the vendor exposes, and an upgrade can arrive as a quality change you did not schedule.

Cost is a shape, not a winner. API cost scales with tokens and is near zero when traffic is near zero. Self-hosting cost is mostly a floor: the GPUs bill overnight whether or not a request arrives. Low or spiky traffic favors the API. High, steady traffic can favor the GPUs once utilization is real. A load test has to show the GPUs survive the peak, because a dollar crossover computed on average traffic is not a capacity plan. The arithmetic belongs to a measured rate card and a measured GPU hour, and both move. On-device cost looks different again. You pay in binary size, battery, and a weaker model, and you stop paying a per-token invoice.

**Trade-offs.** The API is the better performance and feature default and the weaker privacy and lineage default. Self-hosting reverses that and adds an operations burden the API had included. A no-train contract narrows the privacy gap and does not erase it. On-device maximizes privacy for the requests that stay on the device and loses the tasks that need a frontier model. Pinning a hash freezes quality on purpose, including the bugs you have not patched. Riding a vendor's moving alias gets their fixes and their regressions on the same morning.

**Interview.** Walk the seven axes without picking a universal winner: privacy, lineage, performance, functionality, cost, control, and on-device as the extreme of privacy and control. Say the API bills per token and the GPUs bill while idle, so the crossover depends on utilization and on a peak load test. Say a contract is not a hash. If the prompt cannot leave the VPC, the API is out, and the question becomes which open-weight checkpoint you can serve inside the latency budget.

**Recap.** Self-hosting runs weights you control. A model API sends prompts to a provider. Privacy, lineage, and control favor self-hosting or on-device models such as Gemini Nano and the on-device part of Apple Intelligence. Performance and new features often favor the API. Cost favors the API when traffic is low or spiky and can favor your GPUs when steady traffic fills them, which a peak load test has to confirm. The hard attributes pick the side before quality does.

## Public benchmarks

A public benchmark is a shared task, with a shared grader, that many models have been scored on. Navigating one means reading the number as a measurement with a date, a harness, and a task mix, not as a ranking of products.

HELM, Holistic Evaluation of Language Models, from Liang and coauthors at Stanford CRFM, is the argument for a matrix. The original HELM reports accuracy and also calibration, robustness, fairness, bias, toxicity, and efficiency, across scenarios. A model is a column of numbers. The paper's point is that a single accuracy hides the column that would have changed your decision. Chatbot Arena, later LMArena and now Arena, is a different public instrument: pairwise preferences from people chatting, turned into a rating. The previous topic owns Elo, Bradley-Terry, and style control. A public rank from that board is context about preference on that crowd's prompts. It is not an accuracy, and it is not your queue.

Hugging Face's Open LLM Leaderboard is the cautionary history of a single average. The first version, archived in June 2024, averaged six tasks: ARC, HellaSwag, MMLU, TruthfulQA, WinoGrande, and GSM8K. Those tasks saturated and mixed knowledge, common sense, truthfulness, and grade-school math into one scalar. The second version, launched that June, replaced them with a harder six: IFEval, BBH, MATH level 5, GPQA, MuSR, and MMLU-Pro. In March 2025 the maintainers retired the leaderboard rather than let the field keep optimizing a mix that was going stale as reasoning models and assistants changed what was worth measuring. The archived numbers remain useful as history. They are not a live gate. The task list is the lesson. A model that leads an average of those six can be the wrong model for a support bot, and a later board with a different six would reorder the table.

Reading any of these numbers has a checklist. The model id has to be the checkpoint you would call, not a sibling with the same marketing name. The prompt template and the few-shot count have to be the ones in the harness, because a paper's "MMLU" and a leaderboard's "MMLU" can differ by the wrapper. The date has to travel with the score, because boards are revised and retired. The metric has to match the criterion: a preference win is not a factuality rate, and TruthfulQA is not a hazard taxonomy. Contamination, the card after the next one, can inflate a public set the training crawl already contained. Use the board to drop models that fall over on a criterion you already named. Do not use it as the eval you forgot to build.

**Trade-offs.** A shared harness is the only way to compare a number from someone else's paper to a number you measure, and the harness is almost never your product distribution. HELM's matrix is harder to game with one saturated task and harder to explain in a meeting than an average. Arena tracks human preference and tracks the crowd that showed up. A retired leaderboard is an honest ending and a trap for slide decks that still quote it. Running every public set is thorough and mostly irrelevant. Running none leaves you with a demo.

**Interview.** Explain HELM as a matrix of metrics, Arena as a preference rating whose statistics live in the previous topic, and the Open LLM Leaderboard as a six-task average that was replaced in 2024 and retired in March 2025. List either task mix only if you can list it accurately, and say the mix is the reason a leader can still be the wrong model. Then give the reading checklist: model id, harness and template, date, metric, and whether the set could have been in the training data. The board narrows a shortlist. The private eval makes the decision.

**Recap.** Public benchmarks are shared tasks with shared graders. HELM reports a matrix of quality, risk, and efficiency metrics. Arena ranks preference, under the rules in the previous topic. The Open LLM Leaderboard averaged ARC, HellaSwag, MMLU, TruthfulQA, WinoGrande, and GSM8K, then a harder six led by IFEval, GPQA, and MMLU-Pro, and the maintainers retired it in March 2025. Read the model id, the harness, the date, and the metric. Use the number to filter, not to launch.

## Benchmark selection and aggregation

Benchmark selection is choosing the public tasks that match your criteria. Aggregation is how you combine those tasks when they disagree, which they will.

Select by the failure a user would notice. Code that must run points at HumanEval, SWE-bench, and a dated set such as LiveCodeBench, with execution as the grader from the previous topic. Crisp constraints point at IFEval. Broad knowledge points at MMLU or, once that saturates, MMLU-Pro. Graduate science that should resist a quick search points at GPQA. Factuality of a long answer points at a grounded check, not at a multiple-choice exam. Safety points at a hazard set plus an over-refusal set. A chat preference points at Arena with the style and date attached. A task that matches none of your criteria is a distraction, including a task your team happens to be good at explaining. The Open LLM Leaderboard's retirement is what it looks like when the selected mix stops matching the models people are actually choosing between.

Aggregation is where a careful selection gets thrown away. A mean of accuracies treats every task as the same kind of point, on the same scale, with the same chance level. GPQA's four choices and MMLU-Pro's ten choices do not share a chance level. An Elo and an accuracy do not share a unit, so they never go into one average. Ranks are the comparable object: on each task, rank the candidates, then average the ranks. A floor is a hard attribute applied to a score: anything under the floor is out, and the mean is computed only for the survivors. The worksheet below is not a leaderboard. The three columns are an exercise so the arithmetic is visible. Domain, instructions, and science stand in for three tasks you already decided you care about.

```python
SCORES = {
    "A": (86, 90, 35),
    "B": (84, 60, 70),
    "C": (80, 75, 55),
}
FLOOR = 50


def mean(values: tuple[int, ...]) -> float:
    return sum(values) / len(values)


def ranks_for(index: int) -> dict[str, int]:
    ordered = sorted(SCORES, key=lambda name: SCORES[name][index], reverse=True)
    return {name: place for place, name in enumerate(ordered, start=1)}


rank_rows = [ranks_for(index) for index in range(3)]
survivors = [name for name, values in SCORES.items() if min(values) >= FLOOR]
print(survivors)
for name in ("A", "B", "C"):
    mean_rank = sum(row[name] for row in rank_rows) / 3
    print(name, f"{mean(SCORES[name]):.2f}", f"{mean_rank:.3f}")
# ['B', 'C']
# A 70.33 1.667
# B 71.33 2.000
# C 70.00 2.333
```

The mean picks B, at 71.33 against A's 70.33 and C's 70.00. The mean rank picks A, at 1.667 against B's 2.000 and C's 2.333, because A is first on domain and first on instructions and last on science. A floor of 50 removes A for a science score of 35, before either aggregate is allowed to crown it. Among the survivors, the column still decides. B leads science, 70 against 55. C leads instructions, 75 against 60. A science assistant and an instruction-heavy macro bot do not share a winner, and the mean of 71.33 pretends they do. Report the columns, the floor, and the aggregate you said you would use. A meeting that sees only the mean has not seen the evaluation.

**Trade-offs.** One headline number is easy to track and wrong when tasks disagree. A full matrix is honest and easy to cherry-pick in the other direction, by starring the column your favorite model won. Ranks throw away the size of a gap: a 1-point lead and a 30-point lead are both one rank. A floor keeps a catastrophic column from hiding inside a healthy mean, and a badly chosen floor eliminates a model that was acceptable. Averaging every public task you can find dilutes the two that match the product.

**Interview.** Show a case where the mean and the mean rank pick different models, using a gap like A's last-place science score against its two firsts. Then apply a floor and let the product pick the column among the survivors. Say you do not average an Arena Elo with an accuracy. Finish with the selection rule: a benchmark earns a column only by matching a criterion you wrote down before you saw who won it.

**Recap.** Select public benchmarks by the failure the product has, not by what is easy to quote. Aggregate with the rule you declared. On the worksheet, the mean picks B at 71.33, the mean rank picks A at 1.667, and a floor of 50 removes A. The surviving decision is the column the product actually feels. A single average is a summary you add after that choice, not the choice itself.

## Data contamination

Data contamination means evaluation items were in the training data, so a score can reward memorization of the test rather than the capability the test was supposed to measure.

Public benchmarks leak because models train on web crawls and the web contains the benchmarks. The training-data card in the foundation-model topic is where decontamination belongs in the pipeline, before the run. The check itself is usually n-gram overlap. You flag a test item when a long n-gram also appears in the training text. The n-gram has to be long because ordinary language shares short phrases. The GPT-3 report's training filter searched for 13-word overlaps, counting a word as a lowercase whitespace-separated token, and its clean-subset analysis used a window between 8 and 13 words depending on the benchmark. A shorter window collides with ordinary phrases. Overlap is a flag, not yet a verdict. That paper found overlaps on many benchmarks and, for most of them, little change when the flagged items were removed, so a flagged item still has to be scored both ways. After training, you often no longer have the crawl. A paraphrase test is the check you can still run: rewrite the item, keep the answer, and compare scores. A model that knew the skill should barely move. A model that memorized the wording drops. Perplexity is the other after-the-fact smell, and the previous topic owns how to read it. A contaminated item is often much more predictable than a matched control or a paraphrase, and a low perplexity on easy text is not, by itself, proof.

```python
def ngrams(tokens: list[str], size: int) -> set[tuple[str, ...]]:
    return {tuple(tokens[index : index + size]) for index in range(len(tokens) - size + 1)}


def overlap(left: list[str], right: list[str], size: int) -> int:
    return len(ngrams(left, size) & ngrams(right, size))


train = "the capital of france is paris and it sits on the seine".split()
leaked = "the capital of france is paris and it sits on the seine what is the capital".split()
paraphrase = "which city serves as the capital of france".split()
print(overlap(leaked, train, 8), overlap(paraphrase, train, 8))
print(overlap(leaked, train, 4), overlap(paraphrase, train, 4))
# 5 0
# 9 1
```

The leaked wording shares five 8-grams with the training text. The paraphrase shares none. At 4-grams the paraphrase still shares "the capital of france," which is the fact, not a copied question. A decontamination pass that used 4-grams would have flagged a legitimate rewording. The flag still has to be checked against the score. If the clean items score like the full set, the overlap was probably boilerplate or a shared fact, which is what the GPT-3 analysis found on many of its benchmarks. If the clean items collapse, the headline was inflated, and the clean number is the one you can defend. BIG-bench publishes a canary string so a later crawl can be filtered on purpose. GPQA's gated distribution is the same idea at the dataset door. Neither helps once a paper, a blog, or a training scrape has quoted the items. A cutoff helps when you know it. LiveCodeBench can restrict code problems to contests dated after the model's training cutoff. A score on problems the model could not have seen is the score you can defend. A score on a famous set, with no overlap check and no rewrite, is a hypothesis.

What you do with a flagged set is score the clean slice beside the full set. When the clean slice drops, it carries the launch and the full set does not. When the two match, the overlap was not evidence of memorization. A private set drawn from production, and kept out of the next finetune, is the durable fix. The previous topic's closing card already said a public set you do not rotate will flatter a model that trained on it, and that a private set has the same fate if its prompts are pasted into training. Contamination is why the model-selection workflow treats a public number as a filter. The private eval is the measurement.

**Trade-offs.** N-gram decontamination needs the training text and misses a paraphrase that preserved the answer without preserving the wording. A rewrite test needs no crawl and confuses a genuinely hard rewording with memorization. Perplexity needs a matched control and a shared tokenizer, which is why the previous topic refuses a raw threshold. Dropping every suspicious item shrinks the set and can throw out the easy problems a fair model should have found easy. Keeping them can inflate the number you are about to ship on, which is why the clean slice is reported next to the full set.

**Interview.** Define contamination as the test appearing in training, so the score can be recall. Give n-gram overlap as the pretraining screen, with a long n, and the 8-versus-4 example as the reason the n is long. Give a paraphrase drop, a perplexity comparison against a control, a canary, and a time cutoff as the checks you can explain. Say you defend the clean slice when it drops, and a clean slice that matches the full set is evidence the overlap was not memorization.

**Recap.** Data contamination can inflate a benchmark when the items were in the training data. Long n-gram overlap is the screen while you still have the crawl. An 8-gram flags a copied sentence and misses a paraphrase, while a 4-gram flags both. After training, a rewrite test, a perplexity comparison, a canary, or a problem dated after the cutoff is the evidence. The launch number is the uncontaminated slice, or a private set that has not been trained on.

## Evaluate every component

Evaluating every component means scoring each stage of the system on its own output, and scoring the task the user actually had, because those two numbers answer different questions.

A foundation-model product is a pipeline. A NotebookLM or Notion answer over a workspace is a retrieval query, a set of pages, a prompt, a generation, and a citation check. An Intercom bot that can refund through Stripe adds a tool call with arguments. If you store only the final message, a bad answer is an undifferentiated failure and you will edit the prompt when the index was empty. Step 1 of an evaluation pipeline is to log every stage's inputs and outputs so each stage can be graded with the tool that stage requires. Retrieval is a hit at k against the page that contains the answer. A tool argument is an exact check. A grounded sentence is the local-consistency check. Tone is a judge. The previous topic's rule, that each field uses the tool that can actually mark it wrong, is the rule you apply per stage.

Turn-level and task-level are the other cut, and they show up as soon as the product has more than one step. A turn-level metric scores this reply, this retrieval, or this tool call. A task-level metric scores whether the user got what they came for: the summary matched the page, the ticket resolved, the refund that arrived was the refund they were owed. A task can succeed despite a bad turn when a later turn or a human repairs it. A task can fail despite fluent turns when the order id was wrong from the start. Both numbers are real. A Stripe refund flow makes the gap concrete. The bot asks for an order id, which is a good turn. It then calls the refund tool with the right id and the wrong amount. A person catches it and the customer is made whole. Task-level resolution says the case ended correctly. The tool-call metric says the system attempted the wrong amount. If you only track resolution, you will ship the bad call until the person stops catching it. If you only track the tool call, you will reject a multi-turn recovery that is part of the design. Log the attempted amount and the final amount.

The retrieval version of the same gap is why a correct final answer is not a retrieval score. When the right page was missing and the model answered from pretraining anyway, the task can pass today and fail the morning the workspace disagrees with the weights. Grounded accuracy, correct and supported by a retrieved page, is the task metric a "this workspace" product promised. Raw accuracy is the task metric a general assistant promised. Naming which product you are in is part of step 1. Component scores tell you where to spend the next week. Task scores tell you whether users are getting the outcome. A launch that reports only the prettier of the two has picked the prettier definition of the product.

**Trade-offs.** Logging every stage is cheap compared with being unable to diagnose a regression, and the logs can contain customer data you now have to retain on purpose. A full component matrix slows a team that needed one task number to make a decision. A single task number is the business outcome and a blunt instrument for a five-stage pipeline. Grading turns without the task rewards locally polite steps that do not add up. Grading the task without the turns hides a dangerous tool call that a human happened to catch.

**Interview.** Draw the pipeline and attach a metric to each box: recall at k, exact tool arguments, entailment against the retrieved page, a judge only for the residue. Then define turn-level versus task-level with the refund amount: the tool call was wrong, the case still closed, and both facts stay in the report. Say a correct answer on a retrieval miss does not clear the retriever, if the product promised the document.

**Recap.** An evaluation pipeline starts by scoring every component and scoring the task. Retrieval, tool arguments, grounding, and tone use different tools, and you can only compute them if you logged the stage. Turn-level metrics catch a bad refund amount or a bad retrieval. Task-level metrics catch whether the user actually got the outcome. A product that promises grounding reports the grounded number, not the lucky correct answer.

## An evaluation guideline

An evaluation guideline is the written definition of how raters, and any judge you prompt, decide a score. It is step 2 of the pipeline. It states the criteria, shows a rubric with an example of each level, and says which business metric the score is supposed to track.

Criteria in the guideline are the product's criteria, cut into decisions a rater can make. "Be helpful" is not a decision. For a Notion or Google Docs meeting summary, a rater can decide three things: every decision and date in the summary appears in the transcript, every owner matches the transcript, and the summary adds no decision the transcript does not contain. Those are local-consistency and exact-match criteria from earlier in this topic. Tone can be on the list. It is not the gate unless you have evidence it changes an outcome you care about. The previous topic's failure mode, a vague criterion that makes a judge look arbitrary, is what this document prevents.

A rubric without examples is still vague, because "partial" means a different thing to every rater. Each level needs a description and a short example of an answer that belongs there. Pass: the summary says the launch review is Tuesday and the editor owns the checklist, and the transcript says that and nothing contradictory. Partial: the date and the decision match, and the owner is missing. Fail: the summary adds a budget decision the transcript never made, or moves Tuesday to Wednesday. The example can be a fragment. It has to be concrete enough that two raters, and the judge prompt, classify it the same way. Edge cases you have already argued about go in the guideline. They are the future disagreements.

The business tie is a hypothesis you then measure. A meeting-summary rubric is supposed to predict something the product already logs, such as whether the user edits the summary or accepts the extracted action items. You check the hypothesis by slicing that log on the rubric level. If edit rates are the same for passes and fails, the rubric is reliable theater and you do not gate a launch on it. If fails are edited far more often than passes, the rubric is earning its keep as a proxy you can run before the edit exists. Support tools have a sharper logged outcome, a reopen or an escalation, and the same test applies. The tie is not a hope you write in the rubric header. It is a comparison you recompute when the rubric or the product changes. A metric that does not move a business number can stay as a diagnostic. It does not get to block a launch by itself.

**Trade-offs.** A tight guideline makes raters interchangeable and makes the judge promptable, and it is slower to write than a one-line "is this good?" A worked example at every level prevents drift and goes stale when the product voice changes, so the examples are versioned with the rubric. Tying every criterion to revenue sounds serious and pushes teams to drop harms that are rare and expensive. Leaving the business tie implicit lets a polished rubric optimize a score customers do not feel.

**Interview.** Take a real feature and turn "helpfulness" into two or three decisions a program or a rater can apply. Put a pass, a partial, and a fail example next to them, including one wrong fact. Then name the logged outcome you would slice on, edits or reopens or escalations, and say what you do if the slice is flat: the rubric does not gate the launch. Mention that the judge prompt is this document, not a fresh adjective.

**Recap.** An evaluation guideline defines the decisions, shows an example of each score, and names the business outcome the score should track. A meeting summary passes when decisions, dates, and owners match the transcript and nothing was added. The tie to user edits or to ticket reopens is measured by slicing the log, not assumed in the header. A rubric that does not move that outcome stays a diagnostic.

## Choosing evaluation methods

Choosing an evaluation method means assigning each criterion to the cheapest tool that can actually mark a failure. That assignment is the start of step 3. It uses the toolkit from the previous topic rather than re-deriving it.

The assignment is the step. Exact programs take everything they can see: dates, amounts, tool arguments, schema validation, keyword and length constraints, n-gram leaks of a hidden prompt, and unit tests. Retrieval metrics take the logged page ids. Local consistency takes an NLI model or a judge bound to the source, one claim at a time. Global factuality takes a search-augmented or encyclopedia check on a sample, not on every token of every request. Safety takes a hazard classifier, a set of allowed prompts for over-refusal, and a human read of the severe tail. Voice, persona, and "is this summary fair" take a judge with the guideline in the prompt, calibrated the way the previous topic describes. Choosing among a few surviving models or prompts can start with pairwise votes, and the launch still requires an absolute pass line. A method that cannot see the failure is the wrong assignment even if it is cheaper. BLEU on a refund window is the previous topic's example of that mistake. You do not repeat it here. You refuse the assignment.

| Criterion | Method | Why this tool |
| --- | --- | --- |
| A date, an amount, a tool argument, a JSON schema, an IFEval-style constraint, a leaked instruction string. | A program. | The rule is executable, so a judge would be a slower copy of it. |
| Retrieval. | Recall or a hit at k against the page that contains the answer. | The stage either returned the page or it did not. |
| Local consistency of a prose claim. | An NLI model or a source-bound judge. | The source is the premise. Numbers inside the claim still go to the program. |
| Global factuality of a long answer. | An atomic-fact check against a knowledge source, on a sample. | There is no single document unless you retrieve one. |
| Safety and over-refusal. | A classifier plus an allowed-prompt set, with humans on the severe tail. | The taxonomy is stable, and the tail is where a classifier's miss matters. |
| Tone, role voice, usefulness beyond the checks above. | A calibrated judge, using the guideline. | No program has the rule, so the rubric and the rater are part of the metric. |
| Which of two close variants people prefer. | Pairwise votes, then an absolute gate. | Preference ranks the candidates. It does not issue a pass. |

Cost orders the methods inside that table, not instead of it. A program runs on every build. A classifier can run on every build. A frontier judge runs on the residue and on a schedule you can afford. People run where the judge's calibration is due, and on the severe slice the classifier is not allowed to decide alone. The nightly bill in the previous topic is the reason a judge of open quality and a program for the amount can share a pipeline without sharing a budget.

**Trade-offs.** One judge for every criterion is simple to build and spends frontier-model money to approximate checks a program already makes. A program for every criterion is cheap and blind to voice and fairness of a summary. Pairwise preference is how people are reliable, and it has no unit for correct. Matching the method to the criterion is more moving parts and is the only assignment that fails in the right place.

**Interview.** Given a feature, draw the table for it rather than naming a favorite metric. A support bot gets an exact window check, a grounding check, a safety classifier, and a judge only for tone if tone earned a place in the guideline. Say the previous topic is why the judge needs a swap test and a human slice, and this step is only the assignment. If a method cannot mark the failure, it is out, however cheap it is.

**Recap.** Each criterion gets the cheapest method that can see its failure. Programs take dates, amounts, tools, schemas, and leaks. Retrieval metrics take page ids. Entailment or a source-bound judge takes grounded claims. Classifiers take safety. A calibrated judge takes the residue, and pairwise votes only rank variants that still have to pass an absolute bar. The previous topic is how those tools behave. This step is which tool is allowed to grade which row.

## Annotating evaluation data

Annotating evaluation data means building the set you score, deciding which slices must stay visible, and collecting enough labels that the comparison you care about can show up. It is the data half of step 3.

The rows should look like the traffic you serve. Production logs, with consent and with personal data removed or replaced, are that distribution. Expert-written rows cover severe cases traffic has not produced often enough: a refund above a threshold, a self-harm disclosure your policy routes to a person, a tool call with a dangerous argument. Synthetic rows from a model are a draft. A person accepts them into the set, or they are a generator grading its own homework. A frozen regression set stays byte-identical so this week's score compares to last week's. A rotating slice of fresh logs catches the new failure mode a frozen set will miss. You want both, and you do not train on either. A finetune that swallows the regression set contaminates the one number you trusted, which is the previous card's lesson applied to your own data.

Slices are how an average hides a broken product. Language, intent, plan tier, long context, and the incident from last week are the usual cuts. An English help center at a high overall accuracy can still be failing the Spanish refund intent. The introduction topic's warning, that an average near 80 percent hides a harmful tail, is this chart. Report the slice next to the overall number. A slice with a handful of rows is a place you need more labels, not a precise rate.

Sample size is the arithmetic of that honesty. To detect a change from 70 percent to 73 percent accuracy, with a two-sided 5 percent test at 80 percent power, under a normal approximation for two independent proportions and no continuity correction, the unpooled plan needs 3,551 examples per model. The standard normal quantiles are about 1.960 and 0.842. Three points against a base rate of 70 percent is a small gap next to the noise of a proportion, so the set is large. If both models are scored on the same items, positive correlation reduces the variance of the difference and you can get away with fewer. The independent formula ignores that covariance, so it is a conservative plan for a shared set. It is also one comparison. Twenty independent slices at a 5 percent test are expected to produce about one spurious flag when nothing actually changed. A few hundred labels cannot resolve a 3-point gap near 70 percent, however clean the rubric is. An interval on the labels you already have is the sibling calculation: it tells you what those labels can support, and the power formula tells you how many to collect before you look.

```python
import math

Z_975 = 1.959963984540054
Z_80 = 0.841621233572914


def examples_per_arm(baseline: float, target: float) -> float:
    variance = baseline * (1.0 - baseline) + target * (1.0 - target)
    z_sum = Z_975 + Z_80
    return z_sum * z_sum * variance / (target - baseline) ** 2


def examples_pooled(baseline: float, target: float) -> float:
    pooled = (baseline + target) / 2.0
    null_se = math.sqrt(2.0 * pooled * (1.0 - pooled))
    alt_se = math.sqrt(baseline * (1.0 - baseline) + target * (1.0 - target))
    return ((Z_975 * null_se + Z_80 * alt_se) / (target - baseline)) ** 2


needed = examples_per_arm(0.70, 0.73)
pooled = examples_pooled(0.70, 0.73)
print(f"{needed:.1f} {math.ceil(needed)} {pooled:.1f} {math.ceil(pooled)}")
# 3550.3 3551 3553.1 3554
```

The code's first number uses the unpooled variance for both the significance term and the power term. The usual two-proportion sample-size formula puts the pooled rate on the significance term and the unpooled rates on the power term, and that version rounds up to 3,554 for the same 70 percent and 73 percent. A few labels either way do not change the decision. A few hundred labels cannot resolve the gap.

Double-label a slice of the same set. Agreement is not a reason to skip the next card's reliability check, and the labels are the raw material for it. The annotators see the guideline, including the examples, not a fresh interpretation of "helpfulness." When the guideline changes, old labels are a different metric. Keep them under the version they were collected with.

**Trade-offs.** Production logs match the distribution and under-represent rare harms, so an expert slice has to be added on purpose and then not mistaken for the base rate. Large sets detect small gaps and cost labeling. Small sets are affordable and can only see large gaps, which is acceptable when the failure you care about is large. A frozen set makes a trend line and goes blind. A set you rewrite every week makes every gain uninterpretable. Synthetic data scales and flatters the model family that wrote it.

**Interview.** Say where the rows come from: production with redaction, experts for the severe tail, synthetic only after a person accepts it. Then compute the 70-versus-73 sample size, about 3,551 per arm under the assumptions above, and say a shared-item comparison can be smaller because errors correlate. Mention slices, and that a handful of rows is not a rate. Close with the ban on training on the eval set.

**Recap.** Evaluation data should look like traffic, with an expert slice for rare harms and both a frozen regression set and a rotating fresh slice. Neither set is training data. Slices stop an average from hiding a broken intent or language. Detecting 70 percent versus 73 percent, at 80 percent power and a two-sided 5 percent test, needs 3,551 examples per model on the unpooled plan and 3,554 when the significance term uses the pooled rate. Fewer labels can only support coarser claims.

## Evaluating the evaluation

Evaluating the evaluation means testing the metric itself for signal, reliability, correlation with the business outcome, and cost, before you let the metric gate a launch. That audit is part of step 3.

Signal is whether the number moves when the product moves. Break a stage you understand and watch the metric. Swap the retrieved page for a paragraph that contradicts the answer. Grounded accuracy should fall. If it stays put, the grader is ignoring the source and scoring the model's fluency. Shorten a good reply with irrelevant padding and a verbosity-biased judge moves for the wrong reason, which is a failure mode the previous topic already measured. A metric with no signal will smile through a regression. You discover that with a deliberate break, not with a production incident.

Reliability is whether the metric agrees with itself. A program agrees with itself. A judge and a pool of raters need a chance-corrected agreement on a double-labeled slice, which is the previous topic's calibration, not a new formula. A judge that flips when you swap two equivalent answers, or when you ask it tomorrow, is not a launch gate. The fix is the guideline: tighter levels, an example, a smaller question. You do not lower the bar until the flip goes away.

Correlation is whether a reliable metric tracks the outcome the business feels. Raters can agree perfectly on warmth while ticket reopens ignore warmth and track whether the policy was stated correctly. Reliability without correlation is a precise measurement of the wrong thing. The guideline card made the tie a hypothesis. This card is the test. Slice the logged outcome on the rubric level, on rows that were not used to write the rubric. A flat slice demotes the criterion to a diagnostic. A steep slice promotes it. Do the test again when either the rubric or the product changes, because the correlation is not a property of the rubric text alone.

Cost is whether you can run the metric often enough to catch the regression you care about. A frontier judge on every production conversation can cost more than the feature. A human pass on every build will not happen, so it will not be the weekly gate. The affordable pattern is a program and a classifier on every change, a pinned judge on a schedule, and people on the slice that keeps the judge honest. A perfect eval you can run once a quarter is a research report. The Tuesday model swap needs the cheap checks the same day, plus a date for the expensive ones.

**Trade-offs.** A deliberate break test takes engineering time and saves you from a metric that cannot see the outage. Double-labeling is the reliability bill, and skipping it leaves you with a percent agreement that chance could explain. Insisting on a business correlation drops vanity metrics and can drop a real harm that is too rare to show up in reopens. Spending until the eval is flawless delays the launch. Shipping on an untested rubric launches the rubric's bugs.

**Interview.** Name the four tests and the failure each one catches. Signal: the score does not move when you poison the retrieved page. Reliability: the judge flips, or kappa on the double-labeled slice is what chance would do. Correlation: raters agree on a criterion the reopen log ignores. Cost: the only honest eval is too expensive to run when the model changes. Say the previous topic supplies kappa, the swap, and the judge biases. This card supplies the decision to trust the pipeline or change it.

**Recap.** A metric has to earn its place as a gate. Signal means it moves when you break the stage it claims to measure. Reliability means a second rater or a second run agrees beyond chance. Correlation means the score tracks a business outcome such as edits or reopens. Cost means you can run it often enough to catch the change you are making. A metric that fails one of those stays a diagnostic.

## Iterate and version

Iterating and versioning an evaluation means changing the guideline, the data, and the methods on purpose, and never comparing a score to a number that was produced under a different version. It is the last part of step 3, and it closes the pipeline.

A score is reproducible only as a tuple. The generator's model id or weight hash, the eval set's hash, the guideline's version, the judge's model id and prompt, the harness, and the date are part of the result. Drop any of them and a two-point movement is a story. The common story is a gain. The other story is a rubric edit that made the same outputs score higher. Plot a new guideline on a new series. Keep the old series if you still need to explain an old launch. Mixing them is how a team congratulates itself for rewriting a document.

Iteration is the loop that makes the guideline true. Ship a small version. Read the disagreements between raters, between the judge and the raters, and between the metric and the business outcome. Each disagreement is a candidate edit: a level that needs an example, a criterion that should become a program, a slice that needs more rows, a component you were not logging. The production incident from last week becomes a row in the rotating slice and, if it can recur, a row in the frozen set. Then you version the set and rerun. A frozen set that never grows will miss the next incident. A set that grows without a version will make the trend line a lie. Both mistakes are the iteration done halfway.

Public benchmarks stay outside this series. They can change who enters the shortlist, under the reading rules earlier in this topic, and they do not get appended to the private chart. When a vendor ships a new model id, the hard filters run first, then this versioned eval, then a decision. The previous topic's tools, used under this topic's criteria, are the gate. A public rank is a dated input. The launch is a versioned private result: component and task, exact where a program can decide, judged where it cannot, correlated with an outcome you measured, and cheap enough to repeat when the model id moves.

**Trade-offs.** Versioning everything makes a two-point claim defensible and adds process a small team will be tempted to skip. A living guideline gets more accurate and breaks the chart on purpose. Freezing the guideline forever keeps the chart pretty and keeps last year's blind spots. Reading every disagreement does not scale, so you read the disagreements that changed a pass into a fail and a sample of the rest. Waiting to iterate until the eval is perfect is a way to ship with no eval.

**Interview.** List the tuple that has to travel with a score: model id, set hash, guideline version, judge id, harness, date. Say a rubric edit starts a new series rather than a jump on the old one. Describe the loop as disagreements becoming edits, and incidents becoming rows, under a new version. Then place public benchmarks outside the series. They filter the shortlist. The versioned private eval is the launch gate.

**Recap.** A score is comparable only within a version of the model, the set, the guideline, the judge, and the harness. Iteration turns disagreements and production incidents into edits and new rows, and each edit bumps the version. The frozen set keeps the trend honest. The rotating set keeps it relevant. Public leaderboards can change the shortlist. The launch number is the versioned private evaluation.
