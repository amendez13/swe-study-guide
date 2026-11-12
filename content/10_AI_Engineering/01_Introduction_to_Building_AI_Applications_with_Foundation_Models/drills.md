# Introduction to Building AI Applications — Drills

Practice for the planning decisions in this chapter. Each card is one exercise: commit to an answer, then check it. The products are real. The token prices, the error rates, and the monthly volumes are assumptions for the arithmetic, and a real launch uses the provider's current rate card and your own measured rates.

## Compose or Refund

Gmail Smart Compose shows gray text ahead of the cursor. Gmail still sends mail when the feature is off, and the person did not press a button to request the suggestion. ChatGPT has nothing else to show when the model is down, and the person sent the message. A help-desk bot on Intercom or Zendesk answers a customer who opened a ticket. Agents still work the queue when the bot is off. One of the bot's tools calls Stripe to refund a charge.

For each product, is the model critical or complementary, is the interaction reactive or proactive, and what does the human still do?

```python
PRODUCTS = (
    ("gmail-smart-compose", True, False, False),
    ("chatgpt", False, True, False),
    ("support-refund", True, True, True),
)
```

**Answer:** Smart Compose is complementary and proactive, and the person can ignore the gray text. The product survives an outage, and an unasked suggestion has to be precise or people learn to look past it. ChatGPT is critical and reactive, and the person can ignore a bad answer and try again. An outage is the product being down, so the quality bar and the uptime bar are the product's bars. The refund bot is complementary and reactive, and a person confirms the money movement. The desk still runs without the bot, and the customer did ask for help, so this is not ghost text. Complementary does not relax the rule on a side effect. The refund stays behind a confirmation because it moves money, which is the human-role axis and not the criticality axis.

```python
PRODUCTS = (
    ("gmail-smart-compose", True, False, False),
    ("chatgpt", False, True, False),
    ("support-refund", True, True, True),
)

def placement(works_without_model: bool, user_invoked: bool, moves_money: bool) -> tuple[str, str, str]:
    criticality = "complementary" if works_without_model else "critical"
    timing = "reactive" if user_invoked else "proactive"
    human = "person confirms" if moves_money else "person can ignore"
    return (criticality, timing, human)

for name, works, invoked, money in PRODUCTS:
    print(name, placement(works, invoked, money))
# gmail-smart-compose ('complementary', 'proactive', 'person can ignore')
# chatgpt ('critical', 'reactive', 'person can ignore')
# support-refund ('complementary', 'reactive', 'person confirms')
```

## Use or Skip

Four tasks are on the table. Duolingo conversation practice is language, a learner can try again, and one turn does not change a credential. A Gusto or ADP payroll-tax filing must be exact, and submitting the wrong figure is a filing you then have to amend. An Expensify-style receipt read fills vendor, date, and total for a person who still compares them to the photo before anyone is paid. Google Maps driving time already comes from a routing algorithm.

Which tasks can the model take, which should it only draft, and which should stay ordinary software?

```python
TASKS = (
    ("duolingo-practice", True, True, False, False, False),
    ("payroll-filing", False, False, True, True, False),
    ("receipt-fields", True, True, True, False, False),
    ("maps-route", False, True, True, False, True),
)
```

**Answer:** Duolingo practice is a task the model can take: language in, a low-stakes turn out, and a retry. Payroll filing stays off the model because the number has to be exact and the submission is painful to undo. Receipt fields are a draft: the output is a schema a person checks against the photo, and the payment waits for that check. The Maps route stays ordinary software because a routing algorithm already produces it. A model that narrates the route is a different, optional writing task. It is not a reason to replace the router.

```python
TASKS = (
    ("duolingo-practice", True, True, False, False, False),
    ("payroll-filing", False, False, True, True, False),
    ("receipt-fields", True, True, True, False, False),
    ("maps-route", False, True, True, False, True),
)

def verdict(
    language_heavy: bool,
    reviewable: bool,
    needs_exact: bool,
    irreversible: bool,
    known_algorithm: bool,
) -> str:
    if known_algorithm:
        return "ordinary software"
    if needs_exact and irreversible:
        return "keep the model off this decision"
    if needs_exact and reviewable:
        return "model drafts, a person commits"
    if language_heavy and reviewable:
        return "model can take the task"
    return "ordinary software"

for name, language, reviewable, exact, irreversible, algorithm in TASKS:
    print(name, verdict(language, reviewable, exact, irreversible, algorithm))
# duolingo-practice model can take the task
# payroll-filing keep the model off this decision
# receipt-fields model drafts, a person commits
# maps-route ordinary software
```

## Which Lever

Three features need an adaptation plan. Gmail summarizes a thread that is already in the request. Notion answers questions over a company wiki that editors change every day. A Shopify catalog needs thousands of product blurbs in a house voice, the facts of each product are passed in the request, and a prompt with a few examples will not hold the voice.

Which levers do you use? Prices and model names are irrelevant here. The question is what is missing.

```python
CASES = {
    "gmail-thread-summary": {
        "facts_change_outside": False,
        "prompt_cannot_hold_behavior": False,
    },
    "notion-wiki-qa": {
        "facts_change_outside": True,
        "prompt_cannot_hold_behavior": False,
    },
    "shopify-house-style": {
        "facts_change_outside": False,
        "prompt_cannot_hold_behavior": True,
    },
}
```

**Answer:** The Gmail summary is a prompt. The thread is the context, and there is nothing to retrieve or train. Notion is a prompt plus retrieval. The wiki is private and it changes after you ship, so baking pages into weights would freeze yesterday's edits. The Shopify voice is a prompt plus a finetune, and only after the prompt actually failed to hold the voice, with a set of good blurbs to train on. The product facts still ride along in the prompt. A finetune does not replace retrieval: if those blurbs also had to quote a returns policy that changes monthly, you would add retrieval and could keep the finetune for the voice.

```python
CASES = {
    "gmail-thread-summary": {
        "facts_change_outside": False,
        "prompt_cannot_hold_behavior": False,
    },
    "notion-wiki-qa": {
        "facts_change_outside": True,
        "prompt_cannot_hold_behavior": False,
    },
    "shopify-house-style": {
        "facts_change_outside": False,
        "prompt_cannot_hold_behavior": True,
    },
}

def levers(facts_change_outside: bool, prompt_cannot_hold_behavior: bool) -> tuple[str, ...]:
    chosen = ["prompt"]
    if facts_change_outside:
        chosen.append("rag")
    if prompt_cannot_hold_behavior:
        chosen.append("finetune")
    return tuple(chosen)

for name, case in CASES.items():
    print(name, levers(case["facts_change_outside"], case["prompt_cannot_hold_behavior"]))
# gmail-thread-summary ('prompt',)
# notion-wiki-qa ('prompt', 'rag')
# shopify-house-style ('prompt', 'finetune')
```

## Repo or File

A Copilot Chat or Cursor feature answers "explain this code." One design pastes 80,000 tokens of the repository on every question. The other pastes the open file, the question, and a short instruction, 3,500 tokens. Both designs generate 400 output tokens. The team expects 50,000 questions a day.

Use these planning prices, which are exercise assumptions and not a vendor's current rate card: $0.50 per million input tokens and $2.00 per million output tokens. What does each design cost per day, and which lever moved the bill?

```python
QUESTIONS_PER_DAY = 50_000
OUTPUT_TOKENS = 400
INPUT_USD_PER_MILLION = 0.50
OUTPUT_USD_PER_MILLION = 2.00
WHOLE_REPO = 80_000
OPEN_FILE = 3_500
```

**Answer:** The whole-repo prompt costs $2,040 a day. The open-file prompt costs $127.50 a day. Output is $40 either way, so almost all of the gap is input context. The lever is the application decision of what enters the prompt, which you take before you finetune, quantize, or rent a GPU cluster. Rejected answers are still billed. A real rate card replaces these prices, and the comparison stands as long as input tokens dominate a stuffed context.

```python
QUESTIONS_PER_DAY = 50_000
OUTPUT_TOKENS = 400
INPUT_USD_PER_MILLION = 0.50
OUTPUT_USD_PER_MILLION = 2.00
WHOLE_REPO = 80_000
OPEN_FILE = 3_500

def daily_usd(input_tokens: int) -> float:
    input_cost = QUESTIONS_PER_DAY * input_tokens / 1_000_000 * INPUT_USD_PER_MILLION
    output_cost = QUESTIONS_PER_DAY * OUTPUT_TOKENS / 1_000_000 * OUTPUT_USD_PER_MILLION
    return input_cost + output_cost

print(daily_usd(WHOLE_REPO), daily_usd(OPEN_FILE))
# 2040.0 127.5
```

## Demo Milestone

A support bot was shown on 20 tickets a product manager picked. The room liked it. There is no written rubric and no set of real tickets scored in advance. Leadership wants customer-visible replies next week. Separately, imagine the team later builds a set, runs shadow mode, and measures a 5 percent policy-error rate against a 1 percent bar.

What is the next milestone for the demo they actually have? What is the next milestone after that measured 5 percent?

```python
POLICY_BAR = 0.01
DEMO = {"has_eval": False, "shadow_ran": False, "policy_error": 0.0}
MEASURED = {"has_eval": True, "shadow_ran": True, "policy_error": 0.05}
```

**Answer:** The demo's next milestone is an eval set. A room's reaction is not a rate, and 20 chosen tickets will not include the tail. After a real set shows 5 percent policy errors, the next milestone is to keep a person on policy-bearing replies. Shadow mode taught you the rate. It does not authorize unattended sending while the rate is over the bar. Limited send is for the intents that are under the bar, with a kill switch. The last mile is this sequence. The meeting skipped it.

```python
POLICY_BAR = 0.01
DEMO = {"has_eval": False, "shadow_ran": False, "policy_error": 0.0}
MEASURED = {"has_eval": True, "shadow_ran": True, "policy_error": 0.05}

def next_milestone(has_eval: bool, shadow_ran: bool, policy_error: float, policy_bar: float) -> str:
    if not has_eval:
        return "eval set"
    if not shadow_ran:
        return "shadow"
    if policy_error > policy_bar:
        return "human on policy replies"
    return "limited send"

print(next_milestone(**DEMO, policy_bar=POLICY_BAR))
print(next_milestone(**MEASURED, policy_bar=POLICY_BAR))
# eval set
# human on policy replies
```

## Eighty Percent

The same support bot's demo of 25 curated tickets was described as "about 80 percent." A later random sample is more specific: 80 percent of drafts are sendable with a light edit, 15 percent need a full rewrite, and 5 percent invent a policy such as a refund the help center does not offer. The desk handles 10,000 tickets a day.

How many policy inventions is that per day, and how many full rewrites? Why is the demo's 80 percent not a launch number?

```python
DAILY_TICKETS = 10_000
DEMO_TICKETS = 25
SENDABLE_PCT = 80
POLICY_PCT = 5
```

**Answer:** The random sample implies 500 policy inventions and 1,500 full rewrites a day. The other 8,000 drafts are the ones an agent can lightly edit. The demo's 80 percent cannot authorize a launch for three reasons. The 25 tickets were chosen, so they over-represent the easy path, and the number you can quote is the one on the random sample. One accuracy figure adds a stiff sentence to a made-up refund, and only the 5 percent decides whether the bot may send. The demo also never measured latency against a person waiting in chat, dollars per resolved ticket, or the day the provider ships a new snapshot. If agents spend longer repairing the 15 percent than writing those replies, the draft misses its usefulness threshold even while the slide says 80 percent.

```python
DAILY_TICKETS = 10_000
DEMO_TICKETS = 25
SENDABLE_PCT = 80
POLICY_PCT = 5

policy_per_day = DAILY_TICKETS * POLICY_PCT // 100
rewrite_per_day = DAILY_TICKETS * (100 - SENDABLE_PCT - POLICY_PCT) // 100
print(DEMO_TICKETS, policy_per_day, rewrite_per_day)
# 25 500 1500
```

## Stack Map

A Perplexity-style product answers a question and shows sources. Place each responsibility in the application, model, or infrastructure layer. The embedding index is the one people file in the wrong layer.

```python
WORK = (
    "sources list in the answer UI",
    "which passages go into the prompt",
    "faithfulness eval on a fixed question set",
    "finetune on downvoted answers",
    "quantize the model to cut latency",
    "GPU fleet and the autoscaler",
    "latency and dollars-per-query dashboard",
    "the process that stores the embedding index",
)
```

**Answer:** The sources list, the choice of passages, and the faithfulness eval are application work. The eval asks a product question, whether the answer stayed on the retrieved pages, which is different from a training loss. The finetune and the quantization change the model artifact, so they are model development. The GPU fleet, the dashboard, and the process that stores the embedding index are infrastructure. The index is a database. The policy that decides which rows to put in the prompt stays in the application. You start in the application layer. You finetune, quantize, or take on the fleet when a measurement says prompting and retrieval cannot hit the bar.

```python
WORK = {
    "sources list in the answer UI": "application",
    "which passages go into the prompt": "application",
    "faithfulness eval on a fixed question set": "application",
    "finetune on downvoted answers": "model",
    "quantize the model to cut latency": "model",
    "GPU fleet and the autoscaler": "infrastructure",
    "latency and dollars-per-query dashboard": "infrastructure",
    "the process that stores the embedding index": "infrastructure",
}

for name, layer in WORK.items():
    print(f"{layer}: {name}")
# application: sources list in the answer UI
# application: which passages go into the prompt
# application: faithfulness eval on a fixed question set
# model: finetune on downvoted answers
# model: quantize the model to cut latency
# infrastructure: GPU fleet and the autoscaler
# infrastructure: latency and dollars-per-query dashboard
# infrastructure: the process that stores the embedding index
```

## Pinned Snapshot

A Notion-style summarizer calls a floating "latest" model. The previous snapshot, `model-2026-03-01`, scores 0.93 faithfulness on your regression set. The new snapshot scores 0.81. Your bar is 0.90. Input price falls from $5.00 to $0.50 per million tokens. Output stays $15.00 per million. You run 1,000,000 summaries. Each summary sends 2,000 input tokens. The old snapshot writes 200 output tokens. The new one writes 1,200.

Do you move production to the new snapshot? What happens to the bill?

```python
CALLS = 1_000_000
INPUT_TOKENS = 2_000
OUT_USD_PER_MILLION = 15.00
BAR = 0.90
OLD = {"faithfulness": 0.93, "output_tokens": 200, "input_usd_per_million": 5.00}
NEW = {"faithfulness": 0.81, "output_tokens": 1_200, "input_usd_per_million": 0.50}
```

**Answer:** Keep `model-2026-03-01` pinned. Faithfulness 0.81 is under the 0.90 bar, so the price cut is unused until a prompt change or a later snapshot passes the same set. The bill would also rise, from $13,000 to $19,000, because the cheaper input is smaller than the extra output. A headline price cut is not a cost win until you recompute input and output together. Re-run this check on every alias move. A finetune built on the old base does not come along automatically.

```python
CALLS = 1_000_000
INPUT_TOKENS = 2_000
OUT_USD_PER_MILLION = 15.00
BAR = 0.90
OLD = {"faithfulness": 0.93, "output_tokens": 200, "input_usd_per_million": 5.00}
NEW = {"faithfulness": 0.81, "output_tokens": 1_200, "input_usd_per_million": 0.50}

def bill(output_tokens: int, input_usd_per_million: float) -> float:
    input_cost = CALLS * INPUT_TOKENS / 1_000_000 * input_usd_per_million
    output_cost = CALLS * output_tokens / 1_000_000 * OUT_USD_PER_MILLION
    return input_cost + output_cost

def choice(faithfulness: float, bar: float) -> str:
    if faithfulness < bar:
        return "pin model-2026-03-01"
    return "move to the new snapshot"

old_bill = bill(OLD["output_tokens"], OLD["input_usd_per_million"])
new_bill = bill(NEW["output_tokens"], NEW["input_usd_per_million"])
print(choice(NEW["faithfulness"], BAR), old_bill, new_bill, new_bill > old_bill)
# pin model-2026-03-01 13000.0 19000.0 True
```
