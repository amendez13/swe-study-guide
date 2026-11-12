# Dataset Engineering — Drills

Practice for the dataset decisions in this chapter. Each card is one exercise: commit to an answer, then check it. The products are real. Prices, accuracies, corpus sizes, and label counts that are not derived from a public paper are assumptions for the arithmetic. A launch uses the contract you signed, the tokenizer you will serve, and the eval you actually hold out.

## Labels for the rare intent

A Zendesk intent classifier has six labels. The definitions were frozen for the quarter. The traffic shares below are an exercise, not a Zendesk statistic. So is the $0.40 label price. You want at least 200 labeled examples of every intent before the first finetune, including `legal`. A uniform draw from production is one plan. Labeling 200 of each intent on purpose is the other. You also have only 400 production tickets on hand today.

How many labels do you buy for the first set, and how do you score it?

```python
SHARES = {
    "order_status": 0.46,
    "refund": 0.22,
    "shipping": 0.16,
    "account": 0.10,
    "product": 0.04,
    "legal": 0.02,
}
MIN_PER_CLASS = 200
ON_HAND = 400
# Exercise dollars per label, not a vendor rate.
RATE = 0.40
DOUBLE = 0.20
```

**Answer:** Buy the stratified 1,200, then double-label 20 percent of them, and do not start with a uniform 10,000. A uniform draw needs 10,000 labels before the 2 percent `legal` slice is expected to reach 200, which is $4,000.00 at the exercise rate, and a short draw can still miss 200. The 400 tickets on hand contain about 8 legal tickets, so most of the 200 legal rows have to be written by someone who knows the guideline. Those expert rows are not 2 percent of traffic, and they must not be scored as if they were. The training file can be balanced so the rare class has a gradient. The number you ship on is a traffic-weighted slice. Double-labeling 20 percent adds 240 labels and brings the exercise bill to $576.00. Agreement on that slice is Cohen's kappa from [Evaluation Methodology](../03_Evaluation_Methodology/). The 3,551-example plan in [Evaluate AI Systems](../04_Evaluate_AI_Systems/) answers a different question, whether you can detect a rise from 70 percent to 73 percent. It is not the size of this first training buy.

```python
import math

SHARES = {
    "order_status": 0.46,
    "refund": 0.22,
    "shipping": 0.16,
    "account": 0.10,
    "product": 0.04,
    "legal": 0.02,
}
MIN_PER_CLASS = 200
ON_HAND = 400
RATE = 0.40
DOUBLE = 0.20
uniform = math.ceil(MIN_PER_CLASS / SHARES["legal"])
stratified = MIN_PER_CLASS * len(SHARES)
second = round(stratified * DOUBLE)
print(uniform, stratified, f"{ON_HAND * SHARES['legal']:.0f}")
print(f"{uniform * RATE:.2f} {stratified * RATE:.2f} {(stratified + second) * RATE:.2f}")
# 10000 1200 8
# 4000.00 480.00 576.00
```

## SQL that has to run

You are synthesizing text-to-SQL pairs for a Shopify support analyst. The schema and the four rows below are an exercise written for this drill. Three candidate pairs came back from the generator. A pair is kept only when executing its SQL returns the result the question asked for.

Which pairs do you keep?

```python
QUESTIONS = (
    "How many orders were refunded, and what is their total in cents?",
    "How many orders were refunded, and what is their total in cents?",
    "How many orders are there, and what is their total in cents?",
)
SQL = (
    "SELECT COUNT(*), COALESCE(SUM(total_cents), 0) FROM orders WHERE status = 'refunded'",
    "SELECT COUNT(*), COALESCE(SUM(total_cents), 0) FROM orders",
    "SELECT COUNT(*), COALESCE(SUM(total_cents), 0) FROM orders",
)
```

**Answer:** Keep the first and the third. Drop the second. The first question asks for refunded orders, and its SQL returns `(2, 6000)`, which is the two refunded rows, 4800 and 1200 cents. The second candidate asks the same question and returns `(4, 17500)`, every order, so it is a fluent query for a different question. The third candidate asks for every order, and `(4, 17500)` is the right result, so the same SQL is kept under the question it actually answers. A query that parses is not a training row. The result has to match the question in the pair. A status value of `refund`, which is not in the table, returns `(0, 0)` and would be dropped against the first question as well.

```python
import sqlite3

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE orders (id INTEGER, status TEXT, total_cents INTEGER)")
con.executemany(
    "INSERT INTO orders VALUES (?, ?, ?)",
    (
        (1001, "refunded", 4800),
        (1002, "shipped", 2500),
        (1003, "refunded", 1200),
        (1004, "delivered", 9000),
    ),
)
QUESTIONS = (
    "How many orders were refunded, and what is their total in cents?",
    "How many orders were refunded, and what is their total in cents?",
    "How many orders are there, and what is their total in cents?",
)
SQL = (
    "SELECT COUNT(*), COALESCE(SUM(total_cents), 0) FROM orders WHERE status = 'refunded'",
    "SELECT COUNT(*), COALESCE(SUM(total_cents), 0) FROM orders",
    "SELECT COUNT(*), COALESCE(SUM(total_cents), 0) FROM orders",
)
# One gold result per candidate, in the same order as QUESTIONS.
GOLD = ((2, 6000), (2, 6000), (4, 17500))
kept = []
for statement, gold in zip(SQL, GOLD):
    got = con.execute(statement).fetchone()
    kept.append(got == gold)
    print(got)
print(kept)
miss = con.execute(
    "SELECT COUNT(*), COALESCE(SUM(total_cents), 0) FROM orders WHERE status = 'refund'"
).fetchone()
print(miss)
# (2, 6000)
# (4, 17500)
# (4, 17500)
# [True, False, True]
# (0, 0)
```

## The same complaint twice

A Gmail-to-Zendesk export will be the training file for a tone finetune. Exact hashing has already run. The two emails below survived it. The counts after that are an exercise result from the export, not a published corpus: 12,000 emails, 1,200 removed as exact copies, 2,700 more removed by a near-duplicate pass at Jaccard 0.8, and 3,600 of the original 12,000 belonging to this one crushed-box wording. Held-out macro-F1 on other complaint types is an exercise 0.61. Training accuracy on the un-deduped file is an exercise 0.97.

Do you keep both emails, and what do you change before the run?

```python
FIRST = "Hi, my order 1001 arrived damaged and I want a refund. The box was crushed. Thanks."
SECOND = "Hi, my order 1001 arrived damaged and I want a refund. The box was crushed. Thank you."
EMAILS = 12_000
EXACT_REMOVED = 1_200
NEAR_REMOVED = 2_700
FAMILY = 3_600
# Exercise scores, not a Zendesk metric.
TRAIN_ACCURACY = 0.97
HELD_OUT_F1 = 0.61
THRESHOLD = 0.8
```

**Answer:** Keep one of the two emails. Their 3-gram Jaccard is 0.8125, which is over the 0.8 threshold, so the near-duplicate pass drops the second. Exact hash kept both because `Thanks.` and `Thank you.` do not normalize to the same string. After both passes the exercise file has 8,100 emails, 0.675 of the export. The crushed-box family was 0.30 of the raw file, so a finetune on the raw export was mostly learning one complaint. That is why an exercise training accuracy of 0.97 can sit next to a held-out macro-F1 of 0.61 on other complaints. The repair is the near-duplicate pass, then a cap on any one family, then the held-out number. Copying the family into the eval would manufacture a high score. That failure is the next drill. This held-out set is a different complaint, so the gap here is duplication inside the training file.

```python
def shingles(text: str, n: int = 3) -> set[tuple[str, ...]]:
    tokens = " ".join(text.lower().split()).split()
    return {tuple(tokens[i : i + n]) for i in range(len(tokens) - n + 1)}


FIRST = "Hi, my order 1001 arrived damaged and I want a refund. The box was crushed. Thanks."
SECOND = "Hi, my order 1001 arrived damaged and I want a refund. The box was crushed. Thank you."
left, right = shingles(FIRST), shingles(SECOND)
overlap = len(left & right) / len(left | right)
EMAILS = 12_000
EXACT_REMOVED = 1_200
NEAR_REMOVED = 2_700
FAMILY = 3_600
remain = EMAILS - EXACT_REMOVED - NEAR_REMOVED
print(len(left & right), len(left | right), f"{overlap:.4f}", overlap >= 0.8)
print(remain, f"{remain / EMAILS:.3f}", f"{FAMILY / EMAILS:.2f}")
# 13 16 0.8125 True
# 8100 0.675 0.30
```

## The leaked eval

A private support eval has 250 prompts. After you normalize the training file, 70 of those prompts are present verbatim and a long n-gram screen flags 30 more. The exercise assumption is that the contaminated model answered all 100 leaked prompts correctly and answered 90 of the other 150 correctly. The n-gram length and the GPT-3 13-word filter stay on the contamination card in [Evaluate AI Systems](../04_Evaluate_AI_Systems/).

Which file do you edit, and which number do you ship?

```python
EVAL_N = 250
EXACT = 70
NGRAM = 30
CLEAN_CORRECT = 90
```

**Answer:** Delete the 100 overlapping rows from the training file, keep all 250 in the eval, and retrain before you quote a score. Under the exercise assumption the full eval scores 190/250, which is 0.76, and the 150-item clean slice scores 90/150, which is 0.60. The 0.16 gap is the leak showing up, and it is a diagnosis about the model that already saw the 100. It is not the score of a repaired model. Deleting the 100 from the eval and leaving them in the training file makes the next headline easier and leaves the memorization in the weights. A clean-slice score computed before the retrain is the evidence you needed to spend the retrain. The number you ship is the full eval, scored on a model whose training file no longer contains those rows. A restatement the n-gram missed can still be in the file, so you also read a sample of unflagged neighbors. You do not lower the gram until it flags ordinary phrasing. That trade-off is the earlier card.

```python
EVAL_N = 250
EXACT = 70
NGRAM = 30
CLEAN_CORRECT = 90
leaked = EXACT + NGRAM
clean = EVAL_N - leaked
full_correct = CLEAN_CORRECT + leaked
print(leaked, clean, full_correct)
print(f"{full_correct / EVAL_N:.2f} {CLEAN_CORRECT / clean:.2f}")
# 100 150 190
# 0.76 0.60
```

## Outputs you do not get to train on

You want a support assistant you will host and sell. The plan is to call the OpenAI API for 50,000 demonstrations, then finetune a Llama student on that file. The clause in front of you assigns ownership of the output to the customer. The public wording in front of you is the consumer Terms of Use effective January 1, 2026, and the business terms effective May 1, 2025. The account you would actually call may be on a later page. The 50,000 is the size of this plan, not a public dataset.

Does ownership of the output make the Llama finetune allowed, and what would be allowed instead?

```python
PLAN = "hosted Llama support assistant trained on 50000 OpenAI outputs"
OWN_THE_TEXT = True
WILL_DISTRIBUTE = True
PURPOSE = "general support assistant"
```

**Answer:** Ownership does not make the finetune allowed. The consumer terms prohibit using Output to develop models that compete with OpenAI. They also prohibit automatically or programmatically extracting Output, which is a second problem if the rows are harvested from the consumer product rather than generated under an API agreement. The business terms prohibit using Output to develop models that compete with OpenAI's products and services, except a permitted exception. The exception covers a model whose purpose is to categorize, classify, or organize data, such as a classifier or an embedding model, when that model is not distributed, and it covers fine-tuning through OpenAI's own services. A Llama you host and sell as a support assistant is the competing-model case. An internal refund classifier you never ship is the classification exception, and only against the contract on that account. Fine-tuning inside OpenAI's service is the other exception, and it does not give you weights to host. The remaining clean paths are demonstrations people write, and a teacher whose license allows the training. The license on the Llama student is a second document, on the open-weights card in [Evaluate AI Systems](../04_Evaluate_AI_Systems/). Read the page the account is actually on before you generate the file. These two effective dates are the public pages, and they move.

```python
def allowed(purpose: str, distribute: bool, openai_hosted_tune: bool) -> bool:
    internal_classifier = purpose == "classifier" and not distribute
    return internal_classifier or openai_hosted_tune


print(allowed("general support assistant", True, False))
print(allowed("classifier", False, False))
print(allowed("general support assistant", True, True))
# False
# True
# True
```

## The chat log and the template

A Zendesk transcript has to become Llama 3 supervised rows. The base is Llama 3 Instruct. Someone has already wrapped the same turns in ChatML, and someone else rendered Llama 3 headers with a single newline instead of the blank line Meta's encoder inserts. The loss, in a third experiment, was applied to every content word, user and assistant. The header tokens themselves are specified on the chat-template card in [Prompt Engineering](../05_Prompt_Engineering/). The 100-token and 20-token mask arithmetic stays on the prompt-loss card in [Finetuning](../07_Finetuning/).

Which rendering do you train, and which words are in the loss?

```python
TURNS = (
    ("user", "I placed order 7781 on Monday. The tracking page still says label created, and I need the delivery date before Friday."),
    ("assistant", "Order 7781 shipped on Tuesday."),
    ("user", "Can I change the address before the carrier scans it?"),
    ("assistant", "The address can be changed before the carrier scans the package."),
)
```

**Answer:** Train the Llama 3 rendering with the blank line, and put the loss on the assistant contents only. ChatML is a different string from that rendering. A single newline after the header is a different string from the blank line. Both can produce a falling loss on a task the server will not send. Of the content words, 16 are assistant and 31 are user, so an unmasked loss has the answer at 0.340 of the content words. The mask makes the assistant text the whole loss. The user turns stay in the context. Special tokens such as `<|eot_id|>` have to be one tokenizer id, which is the formatting card's 9-versus-18 stand-in. Apply one function in the trainer and on the server, the function that shipped with the weights.

```python
def llama3(messages: list[tuple[str, str]], blank: str = "\n\n") -> str:
    parts = ["<|begin_of_text|>"]
    for role, content in messages:
        parts.append("<|start_header_id|>" + role + "<|end_header_id|>" + blank + content + "<|eot_id|>")
    return "".join(parts)


def chatml(messages: list[tuple[str, str]]) -> str:
    return "".join(f"<|im_start|>{role}\n{content}<|im_end|>\n" for role, content in messages)


TURNS = (
    ("user", "I placed order 7781 on Monday. The tracking page still says label created, and I need the delivery date before Friday."),
    ("assistant", "Order 7781 shipped on Tuesday."),
    ("user", "Can I change the address before the carrier scans it?"),
    ("assistant", "The address can be changed before the carrier scans the package."),
)
official = llama3(TURNS)
user_words = sum(len(content.split()) for role, content in TURNS if role == "user")
assistant_words = sum(len(content.split()) for role, content in TURNS if role == "assistant")
print(official == chatml(TURNS), official == llama3(TURNS, blank="\n"))
print(user_words, assistant_words, f"{assistant_words / (user_words + assistant_words):.3f}")
# False False
# 31 16 0.340
```

## The fluent wrong amount

A frontier teacher wrote refund demonstrations for a smaller student. The damaged-item rule is half the order total. Order 7781 totals 4800 cents, so the refund is 2400 cents. In an exercise batch of 200 rows, a program finds 36 wrong amounts. A style judge, asked only whether the reply sounds like the teacher, accepts 34 of those 36 and accepts all 164 correct rows. The judge's biases stay on the judge cards in [Evaluation Methodology](../03_Evaluation_Methodology/).

Which rows enter the student file?

```python
ROWS = 200
WRONG_AMOUNT = 36
JUDGE_KEEPS_WRONG = 34
ORDER_TOTAL = 4800
# Damaged items refund half the total.
POLICY = 0.5
```

**Answer:** Keep the 164 rows the program accepts, and drop all 36 wrong amounts, including the 34 the style judge liked. The correct amount is 2400 cents. A paragraph that opens the way the teacher opens and then says 4800 has copied the style and missed the rule. That is superficial imitation, not a successful distillation. If you follow the judge, you keep 198 rows, and 34/198 of the file, 0.172, is a wrong amount the student will imitate. The judge can still grade tone on the rows the program kept. It does not get a vote on the amount. The choosing-evaluation-methods card is this order, applied to training data: the program first, the judge on the residue.

```python
ROWS = 200
WRONG_AMOUNT = 36
JUDGE_KEEPS_WRONG = 34
correct = ROWS - WRONG_AMOUNT
judge_kept = correct + JUDGE_KEEPS_WRONG
print(int(4800 * 0.5))
print(correct, judge_kept, f"{JUDGE_KEEPS_WRONG / WRONG_AMOUNT:.3f}", f"{JUDGE_KEEPS_WRONG / judge_kept:.3f}")
# 2400
# 164 198 0.944 0.172
```

## The number left in the ticket

A finetune file was exported from real Zendesk tickets. A regex pass is proposed as the privacy filter before training. The three rows below are the sample you were handed. `4242-4242-4242-4242` is Stripe's published test card number. `555-010-0199` is in the fictional North American number range. `case@example.com` is a reserved example address. None of these is a customer. The pattern is what you are checking.

Do you train on the file after this regex pass?

```python
ROWS = (
    "Email case@example.com or call 555-010-0199 about order 7781.",
    "The note says to call five five five zero one zero zero one nine nine.",
    "The tester typed 4242-4242-4242-4242 and it must not be learned.",
)
```

**Answer:** Do not train on the file after this pass alone. The email pattern and the digit-phone pattern catch the first row. A grouped card pattern catches the test PAN in the third row. The second row is the same phone number in words, and none of the three patterns sees it. Order 7781 is not a secret and should survive, because a filter that redacts every integer erases the task. Replace the hits with placeholders when the model should learn to skip them, or drop the row when the private value is the content. Then read a sample, and add a pass for number words once a sample finds one, which this sample already did. Scrubbing at inference, after the number was in the optimizer, does not take it out of the weights. Presidio-style detectors and the pretraining scrub on the training-data card are the same problem at two scales. This file is the one you are about to finetune.

```python
import re

EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE = re.compile(r"\b\d{3}-\d{3}-\d{4}\b")
CARD = re.compile(r"\b(?:\d{4}-){3}\d{4}\b")
ROWS = (
    "Email case@example.com or call 555-010-0199 about order 7781.",
    "The note says to call five five five zero one zero zero one nine nine.",
    "The tester typed 4242-4242-4242-4242 and it must not be learned.",
)
for row in ROWS:
    print(bool(EMAIL.search(row)), bool(PHONE.search(row)), bool(CARD.search(row)))
print("7781" in ROWS[0])
# True True False
# False False False
# False False True
# True
```
