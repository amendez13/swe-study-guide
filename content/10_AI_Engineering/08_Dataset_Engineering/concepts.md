## What dataset engineering is

Dataset engineering is the work of building the examples a model will learn from: which rows exist, what they are allowed to teach, and which encoding the trainer will actually see.

The architecture is often already chosen. An application team calls a hosted model or finetunes a checkpoint such as Llama, and the demonstrations set the ceiling the supervised-finetuning card in [Understanding Foundation Models](../02_Understanding_Foundation_Models/) states. Data-centric AI, the phrase Andrew Ng popularized, means spending the next unit of effort on examples instead of a new network: hold the model still and fix labels, coverage, and duplicates. Pretraining corpora such as C4, RefinedWeb, and FineWeb apply the same discipline at crawl scale; the training-data card covers what a base model inherited. This topic covers the set you build for a finetune, classifier, reward model, or your own crawl, and the processing between raw export and trainer.

The order is the rest of the topic. Decide what behavior the rows should teach and judge quality, coverage, and quantity. Acquire rows from people, your product, or a generator, verify what a generator wrote, then inspect, deduplicate, filter, and format. [Finetuning](../07_Finetuning/) consumes the file. [Evaluate AI Systems](../04_Evaluate_AI_Systems/) owns the held-out set, which never goes in the file. A better set can move a frozen model further than another week of architecture search, but it is slow to specify, label, and read. Synthetic volume is cheap and copies the generator, while a human set matches the shipped distribution only within budget. Treating a file named `train.jsonl` as done is how a finetune memorizes duplicates and a leaked eval.

```text
goal -> quality / coverage / quantity -> acquire (people, product, generator)
-> verify synthetic -> inspect -> dedup -> filter -> format -> trainer
held-out eval: never in the file
```

![What dataset engineering is](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering-1-what-dataset-engineering-is.png)

*Source: [`diagrams/dataset-engineering.drawio`](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering.drawio), page 1.*

## What the data teaches

A curation goal is the behavior you want at inference, named tightly enough that you can look at a row and say whether the row teaches it.

A base model continues text, and supervised finetuning teaches it to answer by imitating demonstrations, specifically. If every target is a short final answer, the model learns short final answers, so chain-of-thought must be in the target when you want the trace. Orca (Mukherjee et al., 2023) trained smaller models on GPT-4's step-by-step explanations rather than final answers; DeepSeek-R1's students (the reasoning-trace card) needed traces as training text at larger scale. Tool calling is the same: with no row containing a parser-accepted tool name and arguments, the finetune has no example of the action the agent ([RAG and Agents](../06_RAG_and_Agents/)) will take.

Multi-turn is a behavior too. LIMA (Zhou et al.), a 65B Llama finetuned on 1,000 single-turn demonstrations, could still hold a conversation, and adding 30 hand-crafted dialogue chains improved that sharply. A file of isolated questions never contains a user who changes the address on the second turn. Preference data teaches a ranking rather than a demonstration (the Reward models card), and a row added because it was easy to export, such as a long system prompt pasted onto an unrelated answer, teaches the paste. Putting traces, tool calls, and second turns in targets makes rows longer and harder to check; training only on final answers is cheaper and leaves out the step you meant to serve. Mixing many goals in one file teaches a compromise, while a set per behavior means more files to keep on one chat template. Ask what the product must do on Tuesday, then which field of the row contains it.

```text
want the trace     -> trace in the target (Orca)
want tool use      -> parseable tool calls in the target
want multi-turn    -> dialogues in the file (LIMA's 30 chains)
want a ranking     -> preference pairs
```

![What the data teaches](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering-2-what-the-data-teaches.png)

*Source: [`diagrams/dataset-engineering.drawio`](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering.drawio), page 2.*

## Data quality

Data quality is the set of properties that make a row worth training on: it is about the task, the label agrees with the task, a second careful person would accept it, the format parses, the row is not a copy, and you are allowed to use it.

The six checks fail in different places, and one "looks fine" hides which failed. The consistency fix is a written guideline (the annotation-guidelines card, with the evaluation-guideline card in [Evaluate AI Systems](../04_Evaluate_AI_Systems/) as the pattern). Format failures become a schema on the formatting card, uniqueness is measured on the deduplication card, and compliance covers a card number in the text or a corpus license forbidding training. The base model's license is the Open weights and licenses card, and the teacher's output license is the distillation card.

| Check | The question the row has to answer | What a failure looks like in a support set |
| --- | --- | --- |
| Relevance | The row is about the task you will serve. | A marketing email sits in the refund file. |
| Alignment with the task | The target does the thing the prompt asked for. | The prompt says to refuse, and the answer refunds the order. |
| Consistency | A second careful person, using the guideline, would keep the same label. | One rater marks a delay "late" and another marks that same delay as a different class. |
| Format | The trainer can parse the row into the fields the loss expects. | The assistant role is missing, or the tool call is prose instead of JSON. |
| Uniqueness | The row adds a case the file does not already contain many times. | The same ticket was pasted in forty times and will dominate the gradient. |
| Compliance | You have the right to train on the text, and the text is safe to put in weights. | The row contains a card number, or the corpus license forbids the training use. |

Quality is not polish. A short, blunt, correct refund decision is a high-quality row; a long, warm, wrong one is not, which is the failure the verification card and distillation drill target. People still read a sample, because a "quality" classifier learned someone else's definition (the filter card). Six checks catch six bugs at six passes, while one overall grade is fast and un-debuggable when the finetune fails. Rejecting every inconsistent row can erase the ambiguous cases the product receives; keeping them without a rule teaches both labels. Compliance discovered after training means the private string was already in the optimizer. Match the repair to the failure: a guideline, a parser, a dedup pass, or a drop.

![Data quality](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering-3-data-quality.png)

*Source: [`diagrams/dataset-engineering.drawio`](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering.drawio), page 3.*

## Data coverage

Data coverage is how much of the traffic you will serve is actually represented in the training rows: the task types, the lengths, the languages, and the topics.

Margins lie. An exercise support file can be 70% short English billing tickets, 10% long English threads, 5% Spanish, 10% tool calls, and 5% refusals, yet contain no long Spanish thread where the assistant calls a tool and then refuses. Every margin looks covered, but Tuesday's cell is empty, and the model will answer from pretraining, which you meant to override. Pretraining has a mix too (Llama 3's blend on the training-data card); a finetune's is small enough to count empty cells yourself. Ten thousand rows at those shares give 500 Spanish, 1,000 long, and 1,000 tool-call rows, and nothing in that arithmetic builds the intersection. Sample it on purpose or accept that it is missing.

Length is the cell teams forget because the mean looks fine (the inspection card). Language is the cell English-only review misses, and the multilingual card in [Understanding Foundation Models](../02_Understanding_Foundation_Models/) explains why it is also a tokenizer and cost problem. Topics work the same way: a refund set that never mentions a damaged shipment has no evidence for that case. Upsampling a rare slice raises its gradient share and can make the model treat it as typical, so weight the eval by traffic. Covering the full grid multiplies labeling cost by the number of cells, while natural traffic starves rare cells. For an empty cell, collect it, synthesize and verify it, or tell the product owner the model has no evidence there.

```python
ROWS = 10_000
# Exercise shares for a support finetune, not a published corpus.
MIX = {
    "english_short": 0.70,
    "english_long": 0.10,
    "spanish": 0.05,
    "tool_calls": 0.10,
    "refusals": 0.05,
}
print(f"{sum(MIX.values()):.1f}")
print(int(ROWS * MIX["spanish"]), int(ROWS * MIX["english_long"]), int(ROWS * MIX["tool_calls"]))
# 1.0
# 500 1000 1000
```

![Data coverage](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering-4-data-coverage.png)

*Source: [`diagrams/dataset-engineering.drawio`](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering.drawio), page 4.*

## Data quantity

Data quantity is how many rows you have. It helps when the next row is a new, correct case, and it stops helping when the next row repeats a prompt you already covered.

Five factors decide whether another thousand rows pay. A hard task needs more cases before rare branches appear. A strong base model mostly needs a small set to select a format pretraining already made possible. Noisy labels repeated do not converge on the right rule, and copies add no diversity. Technique matters: a full update (Training memory card in [Finetuning](../07_Finetuning/)) can memorize a small file and erode untrained skills, so it needs far more diverse rows than LoRA, which fits formats from less data but still overfits fifty noisy copies. Quote technique with count. LIMA (Zhou et al., 2023) finetuned a 65B Llama with ordinary supervised loss on 1,000 curated prompts and responses, about 750,000 tokens and no preference stage: 750 prompts from Stack Exchange, wikiHow, and similar forums, plus 250 written by the authors. Its superficial alignment hypothesis says capability comes from pretraining and alignment mostly teaches response format. In its preference study, LIMA was equivalent or strictly preferred against GPT-4 in 43% of cases (ties included, not a win rate), Bard 58%, and DaVinci003 65%. Its ablation showed more quantity without new prompt kinds gave sharply diminishing returns. That is evidence about a strong base and a small consistent set, not a law, and Llama 3's post-training used far more rows because its behaviors were more than a format layer.

The exercise curve (not LIMA's table) is what you should run on your task. Diverse rows gain 0.22 in win rate from 100 to 1,000 (0.244 per thousand) and only 0.03 from 1,000 to 16,000 (0.002 per thousand). Copies of the first 100 gain 0.03 total and flatten after 500. If the copies and diverse curves match, you are not in the LIMA regime and more careful rows are the lever. If both are flat and low, the base lacks the skill and quantity will not install it. Start with a pilot around fifty examples, a planning size: small enough to read every row and large enough to see whether fifty of a new ticket kind move a held-out number. If they do not, a thousand more of the same will not either. Staged finetuning spends expensive rows last: unlabeled domain text before supervised labels (continued pretraining on the Finetuning objectives card), plentiful less-relevant rows before production-matched ones, and synthetic rows before person-checked real ones. A model that only saw the synthetic stage sounds like the teacher. Buying 16,000 paraphrases moves the invoice, not the curve.

```python
# Exercise win rates against a frozen prompt baseline, not the LIMA study.
N = (100, 250, 500, 1_000, 4_000, 16_000)
DIVERSE = (0.62, 0.71, 0.78, 0.84, 0.86, 0.87)
COPIES = (0.62, 0.64, 0.65, 0.65, 0.65, 0.65)
early = DIVERSE[3] - DIVERSE[0]
late = DIVERSE[-1] - DIVERSE[3]
print(f"{early:.2f} {N[3] - N[0]}")
print(f"{late:.2f} {N[-1] - N[3]}")
print(f"{early / (N[3] - N[0]) * 1000:.3f}")
print(f"{late / (N[-1] - N[3]) * 1000:.3f}")
print(f"{COPIES[-1] - COPIES[0]:.2f}")
# 0.22 900
# 0.03 15000
# 0.244
# 0.002
# 0.03
```

![Data quantity](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering-5-data-quantity.png)

*Source: [`diagrams/dataset-engineering.drawio`](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering.drawio), page 5.*

## Acquiring data

Data acquisition is where a training row comes from: a public set, your own traffic, a vendor, or a generator.

A Hugging Face set is usable after you read the license and datasheet, including any research-only clause that excludes products. Your own traffic is the distribution you serve, once consent and a privacy filter allow export. The flywheel uses that export on purpose. ChatGPT-style thumbs and user edits are its public shape: an edit becomes a preference pair (draft rejected, edit chosen) when it is actually better. Clickers are not traffic. Thumbs-down over-represents angry failures and misses silent wrong answers a user abandoned, so training on that slice teaches complaint avoidance, not correctness, and can train on your model's own mistakes unless filtered. A vendor such as Scale AI staffs raters against your guideline. Label Studio (HumanSignal) is the open-source queue you host when data cannot leave. The generator is this topic's synthesis half. The eval set comes from none of these: the annotating-evaluation-data card in [Evaluate AI Systems](../04_Evaluate_AI_Systems/) builds it and forbids training on it.

The exercise budget (not a Scale AI rate) is 2,000 prompts with one comparison each, a 15% second read, and a 10% redraw for guideline breaks: 300 second reads, 200 redraws, 2,500 labels, $3,125.00 at $1.25. Cut the second rater last, because it is what tells you whether the guideline is one guideline (next card; Cohen's kappa stays in [Evaluation Methodology](../03_Evaluation_Methodology/)). A senior reviewer on disagreements costs more and changes the guideline rather than silently correcting rows. The eval card's 3,551 figure is measurement power, while $3,125.00 buys training labels. A vendor scales and imports whatever the guideline omitted, and a public dataset was finished for someone else's task.

```python
PROMPTS = 2_000
# Exercise dollars per comparison, not a vendor rate.
RATE = 1.25
second = round(PROMPTS * 0.15)
redraw = round(PROMPTS * 0.10)
labels = PROMPTS + second + redraw
print(second, redraw, labels, f"{labels * RATE:.2f}")
# 300 200 2500 3125.00
```

![Acquiring data](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering-6-acquiring-data.png)

*Source: [`diagrams/dataset-engineering.drawio`](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering.drawio), page 6.*

## Annotation guidelines and agreement

An annotation guideline is the written rule a rater applies. Inter-annotator agreement is the check that two careful raters, using that rule, make the same decision.

The document has the evaluation-guideline card's shape ([Evaluate AI Systems](../04_Evaluate_AI_Systems/)): the decision, one example per label, and the edge case you already argued about. "Refund if it feels right" is two datasets under one name. A written window, a worked ticket, and a rule for a photo showing the box rather than the item make one dataset. Raters drift when the document is a slogan, and drift again when you change it but keep old labels under the new name, mixing two policies. Scale AI or a Label Studio queue can apply only the document you give them.

Agreement shows the rule is one rule. Double-label a slice. Percent agreement looks strong when nearly every ticket is the common class, which is why the how-to-use-an-AI-judge card in [Evaluation Methodology](../03_Evaluation_Methodology/) reports chance-corrected Cohen's kappa; its worked example is not recomputed here. In this exercise slice (not that topic's 40-draft example), 64 of 80 agree (0.80). The sixteen disagreements reveal a missing edge, a vague level, or a rater who missed the revision. Fix the document, then relabel rows the old wording touched. A second rater on every row buys what a slice already shows and spends the quantity card's budget for new cases, which is why acquisition double-labels a fraction and protects it. A tight guideline raises agreement and can erase the ambiguous ticket the product actually receives.

```python
# Exercise slice, not the 40-draft kappa example in Evaluation Methodology.
LABELED = 80
AGREED = 64
print(AGREED, LABELED - AGREED, f"{AGREED / LABELED:.2f}")
# 64 16 0.80
```

![Annotation guidelines and agreement](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering-7-annotation-guidelines.png)

*Source: [`diagrams/dataset-engineering.drawio`](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering.drawio), page 7.*

## Why synthesize data

Synthesis is the creation of training rows by a procedure, a simulator, or a model, when you cannot collect enough real rows that teach the behavior.

There are five reasons. Quantity is Alpaca: Taori et al. took Self-Instruct's 175 human seed tasks, had `text-davinci-003` write 52,000 demonstrations for under $500, and finetuned Llama 7B in about three hours on eight 80 GB A100s for under $100, under $600 total. Coverage fills the coverage card's empty cell, such as a language, a tool, or a long document. Quality is Phi-1 (Gunasekar et al., "Textbooks Are All You Need"), a 1.3B code model trained on about 6 billion tokens of textbook-quality code filtered from The Stack and StackOverflow, plus GPT-3.5 synthetic data. The abstract says about 1 billion synthetic tokens; the body splits them into textbooks under 1 billion and an exercise finetune under 200 million. It reports 50.6% HumanEval pass@1 and 55.5% on MBPP. Its 13-gram check found four HumanEval overlaps in the exercises, judged false positives, and retrained after pruning similar exercises. That is the paper's argument, not a waiver for your contamination check. Privacy uses a synthetic ticket to stand in for a pattern, though the teacher may have memorized a private string, so the filter still runs. Distillation moves a stronger model's behavior into one you can serve, and the teacher's terms decide whether the row may exist (distillation card).

Llama 3 uses synthesis inside post-training, not as a corpus substitute. For code, Llama 3 and a code expert generated over 2.7 million synthetic SFT examples. Rejection sampling draws about 10 to 30 candidates per prompt and keeps the reward model's top choice. NVIDIA's Nemotron-4 340B is the public generate-then-filter loop: the Instruct model writes, and the Reward model scores HelpSteer2's helpfulness, correctness, coherence, complexity, and verbosity. HelpSteer2 is a CC-BY-4.0 set of about ten thousand English response pairs. The synthetic set can be large because the filter, not the generator, decides what remains. Textbook-style data can beat a larger pile of average web text, as Phi-1 argued, and can also be narrow, wrong, and forbidden by the teacher's contract. Skipping synthesis leaves the cell empty; trusting it unverified fills the cell with fluent errors.

```text
quantity      Alpaca (175 seeds -> 52,000 rows, < $500 generation)
coverage      the empty cell
quality       Phi-1 (1.3B, 50.6% HumanEval pass@1)
privacy       stand-in tickets (still filtered)
distillation  teacher -> student (license permitting)
production    Llama 3 rejection sampling, Nemotron-4 generate -> reward filter
```

![Why synthesize data](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering-8-why-synthesize.png)

*Source: [`diagrams/dataset-engineering.drawio`](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering.drawio), page 8.*

## Rule-based synthesis

Rule-based synthesis builds a row from a template or a small perturbation you can write down, without asking a model to invent the text.

A template is a sentence with holes filled from a table you trust, such as a reason code, posted window, or checked city, and the label is a function of those holes, not a string copied from a neighbor. A perturbation changes a row you already accepted. Wei and Zou's 2019 easy data augmentation (synonym replacement, random insertion, swap, deletion) is the commonly cited text version. A new row is legitimate only if the label survives the edit. Deleting a "not" or shortening a 30-day window to 14 is a different task, so the old label is a bug you generated on purpose.

In the code, the paraphrase keeps `review`, the 14-day row is `refuse`, and copying the original label onto the shortened window produces a row the function rejects. That check is the method. Templates print many rows from a large table and a narrow distribution, because the table is the distribution, including its rhythm, and they under-represent how customers write. They suit regular language such as amounts, dates, entity swaps, and behavior-preserving identifier renames, and fit poorly for judgments you cannot write as functions. Once the function exists, running it is the verification, with no judge needed. Mixing a small templated slice into real tickets adds regular cases without replacing the distribution.

```python
def row(reason: str, window: int) -> dict[str, str]:
    label = "review" if window >= 30 else "refuse"
    prompt = f"The order {reason}. The posted window is {window} days."
    return {"prompt": prompt, "label": label}


base = [row(reason, 30) for reason in ("arrived damaged", "arrived late")]
paraphrase = row("showed up damaged", 30)
flipped = row("arrived damaged", 14)
copied = {"prompt": flipped["prompt"], "label": base[0]["label"]}
print(len(base), paraphrase["label"], flipped["label"])
print(copied["label"] == flipped["label"])
# 2 review refuse
# False
```

![Rule-based synthesis](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering-9-rule-based-synthesis.png)

*Source: [`diagrams/dataset-engineering.drawio`](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering.drawio), page 9.*

## Simulation

Simulation builds training rows by running a process whose rules you control, then keeping the trace the process actually produced.

The process depends on the domain. Robots need contact, friction, and camera images, so teams use simulators such as NVIDIA Isaac Sim rather than breaking hardware. Driving models need rare collisions and odd weather; CARLA is a public driving simulator, and Waymo has described simulation as part of its testing. A scene is data because the simulator stepped the physics, not because a model wrote about a crash. Tool-using assistants need a sandbox that executes calls: WebArena for websites, and SWE-bench for GitHub issues, where a patch is kept if tests pass. In the refund example, a trace is training data only if the sandbox ran `get_order` and `refund` and returned `result` fields. The good trace refunds the 4,800 cents the lookup returned. The 99,999-cent refund and the result-less story are rejected; fluency does not legitimize an amount the sandbox would refuse.

Simulation creates the row and verification admits it; here one function does both, which is the nice case. A driving scene still needs a check that actor labels are what you think. Domain randomization (varying lighting and textures) widens coverage and can train a policy to rely on cues the real camera lacks. Simulation supplies rare, dangerous cases you should not collect in production, with whatever is wrong in the simulator. That sim-to-real gap is a policy perfect in CARLA and wrong on a road, or a tool policy that passes a stub and fails on a real Stripe error, so a passing sandbox does not retire the production eval. Executed traces are slower than stories and the ones worth training on; stories teach that tools succeed when the prose says so.

```python
ALLOWED = {"get_order", "refund"}


def accept(trace: list[dict], order_total: int) -> bool:
    seen_lookup = False
    for step in trace:
        if step["tool"] not in ALLOWED or "result" not in step:
            return False
        if step["tool"] == "get_order":
            seen_lookup = True
        if step["tool"] == "refund":
            amount = step["arguments"]["amount_cents"]
            if not seen_lookup or amount != order_total:
                return False
    return True


good = [
    {"tool": "get_order", "arguments": {"order_id": "1001"}, "result": {"total_cents": 4800}},
    {"tool": "refund", "arguments": {"order_id": "1001", "amount_cents": 4800}, "result": {"ok": True}},
]
over = [
    {"tool": "get_order", "arguments": {"order_id": "1001"}, "result": {"total_cents": 4800}},
    {"tool": "refund", "arguments": {"order_id": "1001", "amount_cents": 99999}, "result": {"ok": True}},
]
story = [{"tool": "refund", "arguments": {"order_id": "1001", "amount_cents": 4800}}]
print(accept(good, 4800), accept(over, 4800), accept(story, 4800))
# True False False
```

![Simulation](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering-10-simulation.png)

*Source: [`diagrams/dataset-engineering.drawio`](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering.drawio), page 10.*

## AI-powered synthesis

AI-powered synthesis uses a model to create or rewrite training rows. The model is not, by itself, a reason to trust the row.

Self-play has the model generate both sides of an interaction, and it works only when something outside the model scores the result. AlphaZero has game rules; a language model talking to itself needs a unit test, sandbox, or written principle. Constitutional AI (the Reward models card in [Understanding Foundation Models](../02_Understanding_Foundation_Models/)) is the public language version: the model critiques and revises against a constitution, and revisions become preference pairs. Two copies chatting without a constitution or checker converge on what both already say, and self-play optimizes only what its score sees. Paraphrase restates an accepted row. It helps only when it changes the surface and preserves the label; otherwise it is a duplicate, which the deduplication card's Jaccard check detects. Back-translation in Sennrich, Haddow, and Birch's sense keeps a real sentence on one side and is a different procedure from a round trip (next card).

Translation as augmentation covers a language you are short on, with the same failure. Names, order ids, and code often should not be translated, and a Spanish ticket translated to English, answered, and translated back can train a fluent answer to a question the customer did not ask. The multilingual card is why you still want real text in that language; synthetic translation is a bridge, not the cell. Every model-written row inherits the model's mistakes and contract. A second model as the only judge of the first is circular when the two share a failure (the verification card). Separate "a model wrote it" from "a check accepted it."

```text
self-play     needs an external score (rules, sandbox, constitution)
paraphrase    new surface + same label, or it's a duplicate (Jaccard)
translation   a bridge for a missing language; recheck the label
```

![AI-powered synthesis](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering-11-ai-powered-synthesis.png)

*Source: [`diagrams/dataset-engineering.drawio`](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering.drawio), page 11.*

## Back-translation

Back-translation, in the machine-translation sense, creates a training pair by translating real monolingual text with a model in the reverse direction. The human sentence stays human. Only the other side is synthetic.

Sennrich, Haddow, and Birch (ACL 2016) used a target-to-source model to turn real target sentences into synthetic sources, adding parallel pairs of synthetic source plus real target. It is one translation, not out and back. Instruction backtranslation (instruction-synthesis card) has that shape for prompts: a human document is the response and a model writes the instruction; Li et al. describe it that way and cite Sennrich. Augmentation papers use the same name for a round trip, translating a labeled sentence into another language and back in hope of a paraphrase. Xie et al.'s 2020 unsupervised data augmentation uses it as noising for classification. It is useful when meaning survives, a corrupted label when the trip drops a negation or condition, and a near-duplicate when the surface barely changes (Jaccard catches that). A keyword search for "not" cannot catch the first failure: "leave the charge in place" is a faithful refusal without "not," while "refund the order" flips the label. Re-decide the label from the guideline or drop the row. Names, order ids, and code often should not be translated.

For a language the model barely writes, Sennrich's direction is the synthesis path and native generation is the one to refuse. A thousand model-authored support replies in a language scarce in pretraining yield fluent-looking text with the wrong policy and morphology. Keep the scarce-language human sentence, if you have it, and let the model propose the other side. A round trip from trusted English back to English is augmentation, but "now write the training set in the low-resource language" invents the side you cannot check. Translate with a system you can spot-check, or keep the human sentence on the side users read. The Multilingual models card explains why a tokenizer that splits the language into many pieces shrinks a small native set further, and more synthetic native text rehearses errors rather than fixing the tokenizer. Treating every round trip as a new row fills the file with near-copies MinHash should collapse.

```python
def keeps_refusal(text: str) -> bool:
    tokens = set(text.lower().split())
    return bool(tokens & {"not", "don't", "never"}) or "leave the charge" in text.lower()


original = "do not refund the order"
paraphrase = "leave the charge in place"
flipped = "refund the order"
print(keeps_refusal(original), keeps_refusal(paraphrase), keeps_refusal(flipped))
# True True False
```

![Back-translation](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering-12-back-translation.png)

*Source: [`diagrams/dataset-engineering.drawio`](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering.drawio), page 12.*

## Instruction data synthesis

Instruction data synthesis is the loop that creates the prompts and the answers for supervised finetuning, starting from a small seed or from unlabeled text.

Self-Instruct (Wang et al., 2022) bootstraps from 175 human-written seed tasks. A model proposes instructions and input-output instances, heuristics drop malformed and near-duplicate instructions, and survivors rejoin the pool. On GPT-3 it produced 52,445 instructions and 82,439 instances for about $600 at the cited December 2022 davinci price of $0.02 per 1,000 tokens. Alpaca applies the idea with a stronger teacher and simpler pipeline: the same seeds, `text-davinci-003`, 52,000 demonstrations, under $500. The student learns the teacher's instruction-following and habits, a recognizable accent, and the loop plateaus when new instructions are paraphrases the filter missed. Evol-Instruct (Xu et al., 2023; WizardLM) rewrites existing instructions. In-depth evolution makes them harder by adding constraints, deepening, making them more concrete, adding reasoning steps, or complicating inputs; in-breadth evolution creates a more long-tailed new instruction. An elimination pass drops failed evolutions, then the teacher writes answers. Difficulty rises only if answers are checked; a harder instruction with a wrong answer is a harder way to teach a mistake.

Reverse instruction starts from the answer. Li et al.'s 2023 instruction backtranslation treats a human web document as the response and has a model write the instruction, which is Sennrich's shape, not a round trip. Raw pairs trained poorly; a curation pass keeping only model-scored high-quality pairs was the method. The document's facts are real, but the instruction can still ask something it does not answer. UltraChat (Ding et al., 2023) has the generator play user and assistant across turns, and Zephyr's recipe trains on a filtered slice. Synthetic multi-turn data teaches conversation only when someone checked that the second turn follows from the first; unfiltered turns are conversations in form and contradictions in content. Long-context synthesis is the next card.

```text
Self-Instruct      175 seeds -> generate -> filter -> repeat (52,445 instructions)
Alpaca             same seeds, stronger teacher (52,000 rows)
Evol-Instruct      rewrite toward difficulty; check the answer
backtranslation    human document + generated prompt; curation is the method
UltraChat          model-written multi-turn; turns must follow
```

![Instruction data synthesis](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering-13-instruction-synthesis.png)

*Source: [`diagrams/dataset-engineering.drawio`](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering.drawio), page 13.*

## Long-context synthesis

Long-context synthesis builds a training pair whose source is a real long document, and whose question is kept only when the answer is a span of that document or the result of a check you can run.

People will not read a long contract to write a thousand questions. Llama 3's report says short-context SFT data made long-context ability regress and human annotation at those lengths was impractical. Earlier Llama 3 checkpoints therefore wrote synthetic question-answering, summarization, and repository-reasoning rows, and the ablation that preserved short and long benchmarks mixed them in at 0.1% of the supervised set. That is one report's mixture, not a quota; measure the fraction on your task. The question must still be answerable from the packed source. One whose answer is neither a span nor a check output teaches a fact the document lacks. Packing two unrelated contracts and asking for a buried number teaches the failure the Context length and context efficiency card in [Prompt Engineering](../05_Prompt_Engineering/) measured, where the model answers from the ends. A summary that adds a refund the contract does not offer is a fluent insertion, and hierarchical summarization still needs a person or check on a sample because a summary of a summary can drop the exception.

In the code, "30 days from delivery" is a span and survives; "there is no restocking fee" is not, so the pair is dropped even if a teacher wrote it confidently. A span check misses correct paraphrases, which go to a person or the verification card instead of being trusted for sounding like the source. It can also accept a copied sentence that answers a different question. Synthetic long-context rows are a practical way to keep behavior humans will not label at that length, and only as true as the check.

```python
CONTRACT = "the return window is 30 days from delivery. damaged items are refunded at half the order total."


def grounded(source: str, answer: str) -> bool:
    return answer.lower() in source.lower()


print(grounded(CONTRACT, "30 days from delivery"))
print(grounded(CONTRACT, "there is no restocking fee"))
# True
# False
```

![Long-context synthesis](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering-14-long-context-synthesis.png)

*Source: [`diagrams/dataset-engineering.drawio`](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering.drawio), page 14.*

## Verifying synthetic data

Verification is the decision to keep a synthetic row. A row a model wrote is a candidate until a check that does not depend on the model's fluency accepts it.

Run the cheapest check that can see the failure first (the choosing-evaluation-methods card in [Evaluate AI Systems](../04_Evaluate_AI_Systems/), applied to the training file). Functional checks execute: a tool call parses with a served name and typed arguments, code runs, SQL returns the requested result, and math equals the reference. The simulation sandbox is one. Heuristics are cheap patterns: too short or long, repeated n-grams, wrong language, a refusal template in a set meant to answer, or high Jaccard to a kept row. "Looks long" is not a check. An AI judge handles the residue under the judge cards in [Evaluation Methodology](../03_Evaluation_Methodology/): pinned model, anchored rubric, human slice, and swaps for pairwise verdicts. The teacher as sole judge of its own rows repeats its taste. Nemotron-4 340B's reward model and Llama 3's rejection sampler, which picks among 10 to 30 candidates, are judges after a functional check, not substitutes. Llama 3 also keeps a row when either its reward model or a separate Llama quality score marks it high quality, because they often disagree and the union had better recall internally. Read the rows only one score accepts.

In the code, the parsed call with a numeric order id is kept, while `abc` and never-JSON prose are dropped. Repeated "please wait" trips the heuristic; the ordinary sentence does not. Neither check knows whether the refund amount was right, so that needs another functional rule, and a judge cannot overrule a failed execution. If a row passes the parser and fails a person on a sampled slice, the check has a spec bug; fix it before the next batch. Heuristics are foolish in the ways you wrote them, dropping a poem you meant to keep and missing a paraphrase of a bad answer. Running only the judge because it is one API call lets a wrong amount with a warm paragraph in. Running every check on every row wastes judge money on JSON the parser already rejected.

```python
import json


def tool_ok(raw: str) -> bool:
    try:
        call = json.loads(raw)
    except json.JSONDecodeError:
        return False
    arguments = call.get("arguments", {})
    order_id = arguments.get("order_id")
    known = call.get("name") in {"get_order", "refund"}
    return known and isinstance(order_id, str) and order_id.isdigit()


def repeated(text: str, n: int = 4) -> bool:
    words = text.lower().split()
    span = range(len(words) - 2 * n + 1)
    return any(words[i : i + n] == words[i + n : i + 2 * n] for i in span)


good = '{"name":"get_order","arguments":{"order_id":"1001"}}'
bad_id = '{"name":"get_order","arguments":{"order_id":"abc"}}'
prose = "sure, looking now"
loop = "please wait please wait please wait please wait"
plain = "the package left the warehouse on Tuesday"
print(tool_ok(good), tool_ok(bad_id), tool_ok(prose))
print(repeated(loop), repeated(plain))
# True False False
# True False
```

![Verifying synthetic data](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering-15-verifying-synthetic-data.png)

*Source: [`diagrams/dataset-engineering.drawio`](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering.drawio), page 15.*

## Limits of AI-generated data

The limits of AI-generated data are the ways a large synthetic set still makes the next model worse, or makes it something you are not allowed to ship.

Quality control is the first limit. Unchecked wrong rows become demonstrations, training the student to produce errors the teacher only sampled occasionally. Superficial imitation is the second: the student copies the teacher's length, stock opening, and tone, including on cases the teacher gets wrong. That differs from LIMA's superficial alignment hypothesis, where a strong pretrained model already has the capability and a small set selects the format. Superficial imitation means the targets were surface, so the student learned surface; check answers, not style. Model collapse is the third. Shumailov et al. (Nature, 2024) show that indiscriminate training on a previous generative model's output makes the original distribution's tails disappear, in Gaussian mixtures, VAEs, and language models. The warning concerns recursive replacement, each generation trained on the previous model's output instead of the original human distribution. A checked synthetic slice mixed into human data you still hold is a different regime and not collapse. Their practical consequence matches the flywheel: human data and real-interaction data become more valuable as the web fills with model text. Do not finetune today's model only on yesterday's answers and repeat.

Lineage is the fourth limit (next card): a synthetic row's facts come from a teacher corpus you usually cannot list, possibly including benchmarks, and the record of teacher, filter, and license makes it auditable. Licensing is the fifth: a high-quality row can still violate a contract (the distillation card). Synthetic data is the only way to fill some cells, and unchecked synthetic data narrows the distribution toward what the teacher says. Aggressive filtering drops rare cases that look odd to heuristics; light filtering keeps both the rare cases and the mistakes.

```text
1 quality control      a check, not a hope
2 superficial imitation style without the right answer (not LIMA's hypothesis)
3 model collapse       recursive replacement erases tails (Shumailov et al., 2024)
4 lineage              unknown teacher corpus -> record it
5 licensing            the teacher's contract
```

![Limits of AI-generated data](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering-16-limits-of-ai-data.png)

*Source: [`diagrams/dataset-engineering.drawio`](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering.drawio), page 16.*

## Data lineage

Data lineage is the record of where a row came from, what produced it, and which filters let it through, so a later audit can tell a human ticket from a teacher's invention.

A raw export records its source system, time window, and consent note. A synthetic row records teacher, version, date, seed, prompt, and filter. Without that, the next person treats the file as a measurement of customers. Phi-1's paper releases the model while omitting some synthetic-generation details for proprietary reasons, a legitimate limit that means you cannot list the teacher's inputs. A benchmark in the teacher's data can ride inside a new-looking textbook, so run the contamination screen from [Evaluate AI Systems](../04_Evaluate_AI_Systems/) on the student file. Datasheets (Gebru et al.) are the written record: source, filters, known gaps, license. The inspection card computes the distributions that belong there; this card is why the note names the teacher and the filter version, without which you cannot explain why a language cell disappeared.

The license is part of lineage, not a footer. A factually correct row can violate a contract (distillation card), and a customer message you may store may not be trainable. The record goes to the reviewer. A `train.jsonl` with no note gets reused for a task it does not cover, discovering the coverage card's empty cell a quarter late. Storing prompts and seeds makes the set reproducible and stores any private string in the prompt, so the privacy filter runs on the record too. A lineage record is cheap beside a poisoned run, though it does not make a row true.

```text
human row:      source system, time window, consent
synthetic row:  teacher, version, date, seed, prompt, filter, license
datasheet:      source, filters, known gaps, license
```

![Data lineage](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering-17-data-lineage.png)

*Source: [`diagrams/dataset-engineering.drawio`](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering.drawio), page 17.*

## Model distillation

Model distillation trains a student on a teacher's outputs so the student picks up behavior the teacher already has, at a cost you can serve.

Hinton, Vinyals, and Dean (2015) defined distillation with the teacher's full distribution. A hard label names the answer; a soft target, the teacher's probabilities, also shows how much it believed wrong classes. Temperature-scaling the logits before the softmax flattens the distribution so small probabilities are learnable, the "dark knowledge." In the illustrative logits, the top class falls from 0.8668 at temperature 1 to 0.5065 at temperature 4, and the third rises from 0.0159 to 0.1863, which an argmax-only student cannot see. DistilBERT (Sanh et al., 2019) reports 40% fewer parameters than BERT-base, 60% faster, and 97% of BERT's GLUE score (77.0 vs 79.5 macro). An API teacher usually withholds the full distribution, and a few top-token logprobs are not Hinton's soft target. What you can run is sequence-level distillation: save the teacher's text and train with ordinary supervised loss, as Alpaca did from `text-davinci-003` (the teacher you cannot afford on the request path, from the reasons-to-finetune card in [Finetuning](../07_Finetuning/)). The student learns the demonstrations, not the teacher's behavior on unasked questions. Reasoning traces are the next card, and a trace is still output under the same contract.

The contract is independent of the loss. OpenAI's consumer Terms of Use (effective January 1, 2026) prohibit using Output to develop models that compete with OpenAI and prohibit automated or programmatic extraction of data or Output. The Services Agreement (also January 1, 2026) prohibits using Output to develop competing AI models except under a two-part exception, the same exception as the May 1, 2025 business terms, which are the previous page rather than the current citation. The exception covers models primarily intended to categorize, classify, or organize data, such as embeddings or classifiers, when not distributed or commercially available to third parties, and fine-tuning or customizing models through OpenAI's own listed services. Owning the output, which both pages assign to the customer, is not a training right. A hosted, sold Llama student is the competing-model case. An internal, undistributed classifier is the exception, still read against your account's current contract because pages move and order forms differ. The student checkpoint's license is a second document (Open weights and licenses in [Evaluate AI Systems](../04_Evaluate_AI_Systems/)). Distilling a teacher you may not train from produces a capable model you cannot ship.

```python
import math


def softmax(logits: list[float], temperature: float) -> list[float]:
    scaled = [logit / temperature for logit in logits]
    peak = max(scaled)
    exponents = [math.exp(value - peak) for value in scaled]
    total = sum(exponents)
    return [value / total for value in exponents]


logits = [4.0, 2.0, 0.0]
for temperature in (1, 4):
    probs = softmax(logits, temperature)
    print(temperature, " ".join(f"{prob:.4f}" for prob in probs))
# 1 0.8668 0.1173 0.0159
# 4 0.5065 0.3072 0.1863
```

![Model distillation](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering-18-model-distillation.png)

*Source: [`diagrams/dataset-engineering.drawio`](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering.drawio), page 18.*

## Reasoning-trace distillation

Reasoning-trace distillation is sequence-level distillation in which the training text includes the intermediate steps, not only the final answer.

If the trace is not in the target, the student learns to emit the final line. Orca (Mukherjee et al., 2023) trained smaller models on GPT-4's step-by-step explanations. DeepSeek-R1's students are the larger-scale version: Qwen2.5 bases, including a 1.5B math model, and Llama 3 bases, including Llama 3.3 70B Instruct, finetuned with supervised loss only on about 800,000 curated samples. About 600,000 are reasoning trajectories and about 200,000 non-reasoning samples such as writing and translation, so calling all 800,000 "traces" overstates it. The published head-to-head against reinforcement learning is on a 32B Qwen base, where distillation beat the paper's large-scale RL run; it is not shown for every size from 1.5B to 70B. The students received no RL stage, and the report says one could still help. Distillation can also copy teacher habits on questions you never checked.

A correct final line does not make the steps true. The report notes wrong explanations with correct answers, more often when only a small fraction of samples were correct, so those questions were dropped rather than claiming every step was checked. In the bad trace, 48 × 2 is written as 100, and the product check drops it. A student copying the teacher's opening and keeping the bad product imitates style, the superficial-imitation limit, and the verification card's functional check removes the row first. A reasoning trace is output, so the distillation card's contract applies.

```python
def steps_ok(steps: list[tuple[int, int, int]]) -> bool:
    return all(left * right == claimed for left, right, claimed in steps)


good = [(12, 4, 48), (48, 2, 96)]
bad = [(12, 4, 48), (48, 2, 100)]
print(steps_ok(good), steps_ok(bad))
# True False
```

![Reasoning-trace distillation](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering-19-reasoning-trace-distillation.png)

*Source: [`diagrams/dataset-engineering.drawio`](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering.drawio), page 19.*

## Inspecting a dataset

Inspecting a dataset is computing the distribution of the file and reading rows until the statistics and the text tell the same story.

The decision-changing statistics are few: row count, length distribution (not only mean), label balance, language mix, duplicate rate (next card), and parser rejection rate. A mean length hides the two threads that dominate a batch and training time. In the exercise sample, the mean is 191.7 while the median is 40.5 and the longest row is 1,200 tokens. A plan reserving "about 200 tokens" read the mean, though eight of ten rows are around 40. The two long rows are either your intended long-context cell or an unnoticed paste, and only opening them tells you which. Read four samples: random rows, the longest, each rare label, and rows the quality filter nearly dropped. Datasheets (Gebru et al.) record source, filters, known gaps, and license. The coverage card's empty cell appears in a handful of group-bys and vanishes in a random ten. Using the teacher that wrote the rows to automate reading repeats its standard; noticing that every "excellent" row starts with the same sentence takes a person.

Hygiene is part of inspection. Run the trainer on a slice first so a broken template or a label always set to the first class fails in minutes. Never modify the canonical file in place. A filter that overwrites `train.jsonl` destroys the rows you just judged wrong and makes the decision impossible to diff. Write a new versioned artifact and keep the previous one until the eval confirms the deletion. A trial run that inspects the whole file and "cleans it up" in the same path is how a bad threshold becomes the dataset. Skipping inspection because the loss curve will reveal problems finds them after the GPU bill.

```python
lengths = [38, 41, 36, 44, 40, 39, 1200, 42, 37, 400]
ordered = sorted(lengths)
median = (ordered[4] + ordered[5]) / 2
print(f"{sum(lengths) / len(lengths):.1f} {median:.1f} {max(lengths)}")
# 191.7 40.5 1200
```

![Inspecting a dataset](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering-20-inspecting-a-dataset.png)

*Source: [`diagrams/dataset-engineering.drawio`](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering.drawio), page 20.*

## Deduplicating data

Deduplication removes repeated training rows so the optimizer does not spend its steps memorizing one complaint. Decontamination removes training rows that would teach the eval set.

Exact dedup hashes a normalized document and keeps one copy per hash, so normalization is part of the decision. This pass lowercases and collapses whitespace but keeps punctuation, so a trailing exclamation mark changes the hash; stricter normalization catches more copies and merges more distinct rows. Lee et al. (2022) dedup exact substrings with a suffix array, removing paragraphs copied across non-identical pages, and report less memorization. Near-duplicate detection handles a changed word. Jaccard similarity of shingles is intersection over union. MinHash (Broder, 1997) estimates it without comparing sets: each hash contributes the minimum over the shingles, and the fraction of matching minima is an unbiased Jaccard estimate. Locality-sensitive hashing cuts signatures into bands and compares only documents sharing one; with `r` rows per band and `b` bands, a pair of similarity `s` collides with probability `1 - (1 - s^r)^b`.

The refund sentences share 5 of 7 shingles (Jaccard 0.7143). This run estimates 0.3750 with 8 hashes, 0.7109 with 128, and 0.7012 with 512: right in expectation, noisy in small runs, and a longer run is not guaranteed closer. With 5 rows and 20 bands, this pair collides with probability 0.9837 and a Jaccard-0.1 pair with 0.0002; confirm candidates with real Jaccard at a chosen threshold. At 0.8, these sentences both stay, which is correct because "delivery" and "shipment" are different facts; the threshold is a product decision. In the computed toy reduction (not crawl statistics), exact hashing removes three case or repetition copies (8 → 5). A 0.65 near pass drops "settings screen" (2/3 overlap with "settings page") and keeps the order-1001/1002 pair (1/2), leaving 4. Paraphrases sharing few shingles need semantic dedup (next card).

Contamination is dedup against a set you measure. The contamination card in [Evaluate AI Systems](../04_Evaluate_AI_Systems/) owns the screen: long n-grams, GPT-3's partial 13-word filter, why 4-grams flag ordinary phrasing, and the defensible clean slice when you cannot retrain. When you own the finetune, drop the overlapping row from training and keep it in the eval. The copied return policy shares three 8-grams with the eval wording; the restatement shares none, which is not proof of cleanliness, only something this gram cannot see. Retrain after deletion, because a clean-slice score from a model trained on the leak is a diagnosis, not the repaired model's score. Deleting the eval item instead of the training copy produces a flattering next score. Aggressive thresholds can shrink a small task set until the coverage card's rare cell is gone.

```python
import hashlib


def norm(text: str) -> str:
    return " ".join(text.lower().split())


def shingles(text: str, n: int = 3) -> set[tuple[str, ...]]:
    tokens = norm(text).split()
    return {tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}


def jaccard(left: set[tuple[str, ...]], right: set[tuple[str, ...]]) -> float:
    return len(left & right) / len(left | right)


def minhash(grams: set[tuple[str, ...]], seeds: range) -> list[int]:
    signature = []
    for seed in seeds:
        best = None
        for gram in grams:
            digest = hashlib.sha256(f"{seed}:{gram}".encode()).hexdigest()
            value = int(digest[:16], 16)
            best = value if best is None or value < best else best
        signature.append(best)
    return signature


def band_hit(similarity: float, rows: int, bands: int) -> float:
    return 1 - (1 - similarity**rows) ** bands


left = shingles("the refund window is thirty days from delivery")
right = shingles("the refund window is thirty days from shipment")
exact = jaccard(left, right)
print(len(left & right), len(left | right), f"{exact:.4f}")
estimates = []
for count in (8, 128, 512):
    a = minhash(left, range(count))
    b = minhash(right, range(count))
    estimates.append(f"{sum(x == y for x, y in zip(a, b)) / count:.4f}")
print(" ".join(estimates))
print(f"{band_hit(exact, 5, 20):.4f} {band_hit(0.1, 5, 20):.4f}")
# 5 7 0.7143
# 0.3750 0.7109 0.7012
# 0.9837 0.0002
```

```python
import hashlib


def norm(text: str) -> str:
    return " ".join(text.lower().split())


def shingles(text: str, n: int = 3) -> set[tuple[str, ...]]:
    tokens = norm(text).split()
    return {tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}


def jaccard(left: set[tuple[str, ...]], right: set[tuple[str, ...]]) -> float:
    return len(left & right) / len(left | right)


def overlap(a: str, b: str) -> tuple[int, int]:
    left, right = shingles(a), shingles(b)
    return len(left & right), len(left | right)


docs = [
    "Reset your password from the settings page.",
    "Reset your password from the settings page.",
    "reset your password from the settings page.",
    "Reset your password from the settings screen.",
    "Where is my order 1001?",
    "Where is my order 1002?",
    "Where is my order 1001?",
    "The capital of France is Paris.",
]
seen: set[str] = set()
exact_kept = []
for doc in docs:
    digest = hashlib.sha256(norm(doc).encode()).hexdigest()
    if digest not in seen:
        seen.add(digest)
        exact_kept.append(doc)
near_kept = []
for doc in exact_kept:
    grams = shingles(doc)
    if all(jaccard(grams, shingles(kept)) < 0.65 for kept in near_kept):
        near_kept.append(doc)
print(*overlap(docs[0], docs[3]))
print(*overlap("Where is my order 1001?", "Where is my order 1002?"))
print(len(docs), len(exact_kept), len(near_kept))
# 4 6
# 2 4
# 8 5 4
```

```python
def ngrams(tokens: list[str], size: int) -> set[tuple[str, ...]]:
    return {tuple(tokens[i : i + size]) for i in range(len(tokens) - size + 1)}


def shared(a: str, b: str, size: int) -> int:
    return len(ngrams(a.split(), size) & ngrams(b.split(), size))


train = "customers may return an item within thirty days of delivery for a full refund"
leaked = "customers may return an item within thirty days of delivery if they kept the receipt"
fresh = "a shopper can send an item back for thirty days after it arrives"
print(shared(train, leaked, 8), shared(train, fresh, 8))
# 3 0
```

![Deduplicating data](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering-21-deduplicating-data.png)

*Source: [`diagrams/dataset-engineering.drawio`](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering.drawio), page 21.*

## Semantic deduplication

Semantic deduplication removes rows that mean the same thing even when they share few shingles, so a paraphrase does not survive the MinHash pass and then dominate the gradient.

MinHash estimates word overlap, so a restatement sharing no 3-grams is invisible. SemDeDup (Abbas et al., 2023) embeds examples (CLIP for images, a 125M OPT model for text), clusters them with k-means, and within each cluster keeps one of any neighbors above a cosine threshold. On a LAION subset, removing 50% of the data cost little performance, a result for that image set and threshold, not a deletion quota for tickets. Same-product or same-topic documents sit close without being duplicates, and a threshold set too low deletes a topic you had only twice, the coverage card's rare cell. Read borderline pairs. Clustering makes comparison tractable and can miss a pair split across clusters.

Llama 3's post-training applies the idea to dialogues and cites SemDeDup. It clusters with RoBERTa, sorts each cluster by quality × difficulty, and greedily keeps dialogues whose cosine to already-kept ones stays under a threshold. The score chooses which copy survives, not whether two complaints are the same, and it trusts an unaudited quality score, though it beats keeping whichever row arrived first. The exercise vectors are not encoder output, only the comparison you would run after one. At a 0.9 threshold, the screen vector (0.9600) drops and the order vector (0.0000) stays; a real encoder can rank a real pair the other way. This threshold is a product decision like Jaccard 0.65, in another space. Exact hashing and MinHash run first because they are cheaper; this pass catches the paraphrases they miss.

```python
def cosine(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    dot = sum(x * y for x, y in zip(left, right))
    left_norm = sum(x * x for x in left) ** 0.5
    right_norm = sum(y * y for y in right) ** 0.5
    return dot / (left_norm * right_norm)


# Exercise embeddings, not an encoder's output.
page = (1.0, 0.0)
screen = (0.96, 0.28)
order = (0.0, 1.0)
threshold = 0.9
print(f"{cosine(page, screen):.4f} {cosine(page, order):.4f}")
print(cosine(page, screen) >= threshold, cosine(page, order) >= threshold)
# 0.9600 0.0000
# True False
```

![Semantic deduplication](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering-22-semantic-deduplication.png)

*Source: [`diagrams/dataset-engineering.drawio`](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering.drawio), page 22.*

## Cleaning and filtering

Cleaning and filtering removes rows that are junk, toxic in a way you can define, private, or the wrong language, after duplicates are gone and before you spend a label on what remains.

Heuristics are one-line rules. Raffel's C4 pipeline, as Dodge et al. restate it, drops lines lacking terminal punctuation or with fewer than three words, documents with fewer than five sentences, lorem ipsum, or a bad-word-list term, keeps English only at language-detector probability ≥ 0.99, and deduplicates repeated three-sentence spans. Gopher's rules (length, average word length, symbol ratio, stop-word presence) are the same family, retested on Common Crawl by Hugging Face's FineWeb. FineWeb-Edu adds a classifier trained on educational-quality judgments. Dodge et al. showed C4's bad-word list removed science, medicine, health, and legal text, disproportionately removed sexual-orientation mentions (including non-offensive ones), and removed African American English and Hispanic-aligned English much more than white-aligned English. CCNet (Wenzek et al.) tags language with fastText, then scores pages with a 5-gram KenLM model trained on Wikipedia; low perplexity means Wikipedia-like, and fastText is not the quality score. Perplexity filters remove gibberish and also technical pages and dialects the small model never saw. Llama 3 keeps a post-training row when either its reward score or Llama quality score is high, a recall choice that also keeps rows either alone would reject, so read the disputed band. Toxicity filters fail like C4 even as models: a blocklist or Jigsaw's Perspective API can delete reclaimed terms or quoted abuse, and in a moderation dataset that deletes the positive class. Filter toward the safety taxonomy in [Evaluate AI Systems](../04_Evaluate_AI_Systems/), not a generic "be nice" score.

Personal data is a different delete. Emails, phone numbers, national IDs, and payment numbers do not belong in a finetune file. Microsoft Presidio combines patterns with a named-entity model. Llama 3 handled personal data in pretraining cleanup, including dropping domains likely to hold much of it, a coarser pass than a regex on one ticket. The digit pattern finds `555-010-0142` and the email but misses the spelled-out number, so a person reads a sample of kept rows. Replace a match with a placeholder such as `[PHONE]` when the model should learn to abstain or emit it; drop the row when the private value is the sentence's point. Order ids are task entities, not secrets, and a redact-every-number filter erases them. Low-quality removal also covers SEO boilerplate, keyword pages, and parser rejects. Filtering can unlearn behavior too: to stop unrequested suggestions, delete or relabel rows demonstrating them, because "do not suggest" beside a hundred suggesting rows is a weaker gradient. A strict privacy filter drops some legitimate rows; a loose one leaks a phone number into weights you cannot easily delete from. Sample every automatic drop, because a filter that silently removes the Spanish cell is a coverage bug with a clean mean.

```python
import re

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"\b\d{3}-\d{3}-\d{4}\b")
rows = (
    "Reach the customer at user@example.com or 555-010-0142.",
    "The note says five five five, zero one zero, zero one four two.",
)
for row in rows:
    print(bool(EMAIL.search(row)), bool(PHONE.search(row)))
# True True
# False False
```

![Cleaning and filtering](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering-23-cleaning-and-filtering.png)

*Source: [`diagrams/dataset-engineering.drawio`](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering.drawio), page 23.*

## Selecting which rows to keep

Selection decides which surviving rows earn a person or a training slot. Filtering has already removed junk. Selection spends a limited budget on the rows that will change the model.

Active learning puts a model in the loop: label a seed, train or prompt a model, and send people rows it is unsure about rather than random rows it would get right. Cap the unsure pile, because if it is mostly one pattern you buy that pattern repeatedly (the quantity card's copies curve). Keep a random floor, because batches of only today's errors never reveal confident mistakes and drift away from traffic. In the exercise round, 5,000 unlabeled tickets have 700 below the confidence cutoff, 650 of them one pattern. You label 100 of that pattern, all 50 other unsure rows, and 150 confident random rows, for 300 labels, leaving 550 dominant-pattern copies for the next retrain. The acquisition card supplies the guideline and price; this card chooses the queue. Capping can miss a real subtype folded into the pattern.

Distribution matching selects without model uncertainty. DSIR (Xie et al.) resamples a large raw pool to resemble a small trusted target, useful when you have crawl text and want more of a corpus's style, though it copies the target's biases. Uncertainty sampling fits a label budget and a model that already answers some tickets. Ranking every row by a quality classifier and keeping the top quartile is a filter with a quota, like Llama 3's reward-model or Llama-scorer cut, and becomes active learning only when a person labels the next round. One selection round without a second read spends the budget on a drifted guideline.

```python
UNLABELED = 5_000
UNSURE = 700
SAME_PATTERN = 650
CAP = 100
RANDOM_FLOOR = 150
other_unsure = UNSURE - SAME_PATTERN
to_label = CAP + other_unsure + RANDOM_FLOOR
print(UNLABELED, to_label, other_unsure, SAME_PATTERN - CAP)
# 5000 300 50 550
```

![Selecting which rows to keep](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering-24-selecting-rows.png)

*Source: [`diagrams/dataset-engineering.drawio`](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering.drawio), page 24.*

## Formatting training data

Formatting training data is encoding each example in the schema the loss expects and in the chat template the checkpoint was trained with, so the string the trainer scores is the string the server will send.

A supervised row is a conversation, usually a list of role/content messages accepted by OpenAI's fine-tuning API and Hugging Face TRL. A preference row is a prompt plus chosen and rejected responses, and the preference loss (RLHF and DPO card in [Understanding Foundation Models](../02_Understanding_Foundation_Models/)) trains on both. The supervised loss trains assistant tokens and skips the prompt; the mask and its 100/20-token arithmetic are on the Finetuning hyperparameters card in [Finetuning](../07_Finetuning/). The chat template is the encoding around those tokens. The System prompt, user prompt, and chat templates card in [Prompt Engineering](../05_Prompt_Engineering/) specifies Llama 3's headers, Meta's blank line, and `<|eot_id|>`. Apply the template shipped with the weights in trainer and server. ChatML or a missing blank line is a different string, and loss can still fall on it for a task you will not serve. The instruction skeleton is part of the format too. Converting a four-example few-shot prompt into four rows of short instruction, ticket, and answer is the finetune's point. If training saw "Label the ticket" without examples, production must send exactly that; training on one shape and serving the other debugs as a quality drop.

Special tokens must be registered as single tokenizer tokens. If `<|eot_id|>` is ordinary text, the boundary dissolves into characters. The stand-in counter, not Llama 3's tokenizer, shows the bug's size: `Tuesday.<|eot_id|>` is 9 pieces with the token registered and 18 without. Registering tokens changes vocabulary and embeddings, so register exactly the checkpoint's set. Tool-call rows need one schema across the training file, parser, and served model. Render chosen and rejected answers with the same function, or the preference pair trains a ranking of templates. Sharing one template function between training and serving adds a dependency and is the only way they stay aligned. A strict schema rejects rows early, while a lenient loader trains corrupted turns.

```python
def llama3(messages: list[dict[str, str]], blank: str = "\n\n") -> str:
    parts = ["<|begin_of_text|>"]
    for message in messages:
        parts.append(
            "<|start_header_id|>"
            + message["role"]
            + "<|end_header_id|>"
            + blank
            + message["content"]
            + "<|eot_id|>"
        )
    return "".join(parts)


def chatml(messages: list[dict[str, str]]) -> str:
    return "".join(f"<|im_start|>{m['role']}\n{m['content']}<|im_end|>\n" for m in messages)


messages = [
    {"role": "user", "content": "What is the status of order 2048?"},
    {"role": "assistant", "content": "Order 2048 is out for delivery."},
]
official = llama3(messages)
print(official == chatml(messages), official == llama3(messages, blank="\n"))
# False False
```

```python
def tokenize(text: str, specials: tuple[str, ...]) -> list[str]:
    pieces: list[str] = []
    index = 0
    ordered = tuple(sorted(specials, key=len, reverse=True))
    while index < len(text):
        match = next((token for token in ordered if text.startswith(token, index)), None)
        if match is None:
            pieces.append(text[index])
            index += 1
        else:
            pieces.append(match)
            index += len(match)
    return pieces


boundary = "Tuesday.<|eot_id|>"
print(len(tokenize(boundary, ("<|eot_id|>",))), len(tokenize(boundary, ())))
# 9 18
```

![Formatting training data](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering-25-formatting-training-data.png)

*Source: [`diagrams/dataset-engineering.drawio`](/content/10_AI_Engineering/08_Dataset_Engineering/diagrams/dataset-engineering.drawio), page 25.*
