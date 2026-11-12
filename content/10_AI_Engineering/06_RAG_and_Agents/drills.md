# RAG and Agents — Drills

Practice for the retrieval and agent decisions in this chapter. Each card is one exercise: commit to an answer, then check it. The products are real. Ranks, prices, latencies, token counts, and scores are assumptions for the arithmetic. A launch uses a measured index, the current rate card, and the eval you actually run.

## SKU or Description

A Shopify catalog search box receives two kinds of queries. Some are product codes, such as `SKU-1042`. Some are descriptions, such as "warm wool socks." On an exercise set of 20 code queries and 20 description queries, which is not a published Shopify metric, the number of queries whose intended product appears in the top 5 is below. Pure vector search, pure BM25, and a hybrid of the two are the three systems.

Which system do you ship for a box that receives both kinds of query, and when would you skip the vector index?

```python
CODE = 20
DESC = 20
# Exercise top-5 hits, not a Shopify metric.
HITS = {
    "vector": {"code": 8, "desc": 16},
    "bm25": {"code": 17, "desc": 11},
    "hybrid": {"code": 18, "desc": 17},
}
```

**Answer:** Ship the hybrid. On codes it hits 18 of 20, recall 0.90, against the vector index's 8 of 20, recall 0.40. On descriptions it hits 17 of 20, recall 0.85, against BM25's 11 of 20, recall 0.55. Pure vector search is the wrong system for a product code, because nearby descriptions outrank the exact token. Pure BM25 is the wrong system for "warm wool socks," because the catalog does not share those words. The hybrid's extra code hit over BM25, 18 against 17, is small. The description gap is not. If the box received only product codes, BM25 at 17 of 20 would be enough and the vector index would be an update path you could skip. This box receives both, so you pay for both lists. These counts are not the rank fusion on the concept card, and they are not a Shopify dashboard. Recompute them on your own queries before you buy the second index.

```python
CODE = 20
DESC = 20
HITS = {
    "vector": {"code": 8, "desc": 16},
    "bm25": {"code": 17, "desc": 11},
    "hybrid": {"code": 18, "desc": 17},
}


def recall(system: str, kind: str, n: int) -> float:
    return HITS[system][kind] / n


print(f"{recall('vector', 'code', CODE):.2f} {recall('hybrid', 'code', CODE):.2f}")
print(f"{recall('bm25', 'desc', DESC):.2f} {recall('hybrid', 'desc', DESC):.2f}")
print(HITS["hybrid"]["code"] - HITS["bm25"]["code"])
# 0.40 0.90
# 0.55 0.85
# 1
```

## Fork Secrets

A bot over GitHub's Actions documentation is asked whether a pull request from a fork receives repository secrets. The relevant section is two sentences that a fixed splitter put in different chunks. The retriever returned the event sentence and an unrelated sentence about installing dependencies. It did not return the secrets sentence. The draft says the workflow runs and does not mention the secrets restriction.

What do you change in the index, and why is pasting the Actions manual into the prompt the wrong repair?

```python
EVENT = "The pull_request event runs this workflow."
SECRETS = "Pull requests from forks do not receive repository secrets."
SECTION = EVENT + " " + SECRETS
RETRIEVED = (EVENT, "Workflows can install dependencies.")


def contains(chunks: tuple[str, ...] | list[str], fact: str) -> bool:
    return any(fact in chunk for chunk in chunks)
```

**Answer:** Index the section as one chunk, so a single hit contains both the event and the restriction. The retrieved set supports "pull_request" and does not support "do not receive repository secrets," which is why the draft can sound confident and still be incomplete. Overlap of a few tokens does not repair this cut. The two sentences share no token that would carry the restriction into the event chunk. Raising the number of retrieved chunks might have included the secrets sentence, and it also might have included more install instructions. The log shows the second hit was already the wrong neighbor. A parent-section fetch, match the sentence and generate from the section, is the same repair. Pasting the Actions manual spends the context window and puts the restriction in the middle of a long paste, which is the context-efficiency problem in Prompt Engineering. The section is short. It belongs in one chunk. Score recall of that chunk. A fluent draft that never saw the secrets sentence is not a retrieval success.

```python
EVENT = "The pull_request event runs this workflow."
SECRETS = "Pull requests from forks do not receive repository secrets."
SECTION = EVENT + " " + SECRETS
RETRIEVED = (EVENT, "Workflows can install dependencies.")


def contains(chunks: tuple[str, ...] | list[str], fact: str) -> bool:
    return any(fact in chunk for chunk in chunks)


print(contains(RETRIEVED, "pull_request"), contains(RETRIEVED, "do not receive repository secrets"))
print(contains([SECTION], "pull_request"), contains([SECTION], "do not receive repository secrets"))
# True False
# True True
```

## Two Hundred Milliseconds

Notion Q&A has an exercise budget of 200 milliseconds for retrieval before the model starts generating. The first-stage search takes 40 milliseconds and returns up to 80 candidates. A cross-encoder then reranks a prefix of that list. The times and the recall-at-5 figures below are exercise measurements, not a published Notion benchmark.

Which option do you ship?

```python
BUDGET_MS = 200
RETRIEVE_MS = 40
# Exercise latency and recall@5, not a Notion benchmark.
OPTIONS = (
    ("no rerank", 0, 0.61),
    ("rerank 20", 90, 0.73),
    ("rerank 40", 150, 0.77),
    ("rerank 80", 280, 0.79),
)
```

**Answer:** Ship the rerank of 40 candidates. It finishes in 190 milliseconds and has exercise recall at 5 of 0.77. The rerank of 20 also fits, at 130 milliseconds and 0.73, and it leaves recall on the table inside the budget. The rerank of 80 reaches 0.79 and takes 320 milliseconds, which misses the budget by 120. No rerank fits and scores 0.61. The step from 40 to 80 buys 0.02 recall and breaks the wait the user actually has. If the budget were 100 milliseconds, only the list with no rerank would fit, and you would ship that and argue for a faster reranker rather than silently exceeding 100. A reranker still cannot recover a gold chunk the first stage never returned. These recalls are not Cohere's and not Notion's. Time your own candidate counts.

```python
BUDGET_MS = 200
RETRIEVE_MS = 40
OPTIONS = (
    ("no rerank", 0, 0.61),
    ("rerank 20", 90, 0.73),
    ("rerank 40", 150, 0.77),
    ("rerank 80", 280, 0.79),
)


def fits(extra_ms: int) -> tuple[int, bool]:
    total = RETRIEVE_MS + extra_ms
    return total, total <= BUDGET_MS


legal = [(name, *fits(extra), recall) for name, extra, recall in OPTIONS if fits(extra)[1]]
best = max(legal, key=lambda row: row[3])
miss = [(name, fits(extra)[0]) for name, extra, _ in OPTIONS if not fits(extra)[1]]
print(best[0], best[1], f"{best[3]:.2f}")
print(miss)
# rerank 40 190 0.77
# [('rerank 80', 320)]
```

## Refunded Cents

A text-to-SQL assistant sits on a sales warehouse. The question, asked on 12 November 2026, is how many cents were refunded in the seven days ending that day, 5 November through 12 November inclusive. The model proposes two statements. The first filters `orders.refunded_at`. The second sums `orders.total_cents` for rows whose status is `refunded`. The schema and the fixture below are an exercise, not a Shopify export.

What do you run, what do you answer, and which statement never reaches the warehouse?

```python
from datetime import date

AS_OF = date(2026, 11, 12)
START = date(2026, 11, 5)
SCHEMA = {
    "orders": {"id", "created_at", "status", "total_cents"},
    "refunds": {"id", "order_id", "refunded_at", "amount_cents"},
}
ORDERS = (
    {"id": 1001, "created_at": date(2026, 11, 1), "status": "paid", "total_cents": 8000},
    {"id": 1002, "created_at": date(2026, 11, 10), "status": "paid", "total_cents": 4000},
)
REFUNDS = (
    {"id": 1, "order_id": 1001, "refunded_at": date(2026, 11, 8), "amount_cents": 1000},
    {"id": 2, "order_id": 1001, "refunded_at": date(2026, 11, 11), "amount_cents": 1500},
)
```

**Answer:** `orders.refunded_at` is not in the schema, so that statement is rejected before it runs. The status filter is legal SQL and answers a different question. No order has status `refunded`, so the sum is 0, while the refund table holds 2,500 cents in the window, both rows on order 1001. The answer is 2,500 cents. Counting refund rows would say 2, and summing the order total would say 8,000. Neither is what was asked. Execution on the fixture catches the status query. A string match against one gold query would also reject another statement that sums `refunds.amount_cents` with a different alias and the same rows. The functional-correctness card is why the result, not the spelling, is the score, and why the statement still has to be one read. Show the 2,500 with the query that produced it. Do not let the model say "no refunds" because a bad filter returned empty.

```python
from datetime import date

AS_OF = date(2026, 11, 12)
START = date(2026, 11, 5)
SCHEMA = {
    "orders": {"id", "created_at", "status", "total_cents"},
    "refunds": {"id", "order_id", "refunded_at", "amount_cents"},
}
ORDERS = (
    {"id": 1001, "created_at": date(2026, 11, 1), "status": "paid", "total_cents": 8000},
    {"id": 1002, "created_at": date(2026, 11, 10), "status": "paid", "total_cents": 4000},
)
REFUNDS = (
    {"id": 1, "order_id": 1001, "refunded_at": date(2026, 11, 8), "amount_cents": 1000},
    {"id": 2, "order_id": 1001, "refunded_at": date(2026, 11, 11), "amount_cents": 1500},
)


def known(table: str, column: str) -> bool:
    return column in SCHEMA.get(table, set())


def refunded_cents() -> int:
    return sum(row["amount_cents"] for row in REFUNDS if START <= row["refunded_at"] <= AS_OF)


def status_total() -> int:
    return sum(
        row["total_cents"]
        for row in ORDERS
        if row["status"] == "refunded" and START <= row["created_at"] <= AS_OF
    )


print(known("orders", "refunded_at"), known("refunds", "amount_cents"))
print(refunded_cents(), status_total(), len(REFUNDS))
# False True
# 2500 0 2
```

## The Same Search

A coding agent on a GitHub repository is trying to find retry handling. The trace proposes `search_code` with the query `retry` on three steps in a row. Each observation is the same three paths. A later step would have read `retry.py`. The host's step cap is 6. The observations did not change between the calls.

Which calls should have run, and what does the step cap fail to stop?

```python
TRACE = (
    ("search_code", "retry"),
    ("search_code", "retry"),
    ("search_code", "retry"),
    ("read_file", "retry.py"),
)
REPEATS = (("search_code", "retry"),) * 8
CAP = 6
```

**Answer:** Run the search once. The second proposal is the same tool and the same argument, and the observation is unchanged, so it does not run. The read of `retry.py` never starts, because the loop is already stopped and the model has not been given a turn to choose a different tool. The host should append a trusted note that this search already ran, then let one more step choose something else, such as the read. A trace of eight identical searches, with only the step cap and no repeat check, runs six of them and then stops. The cap bounds the bill. It does not notice that step 2 cannot add information. This is a different stop from the repair on the reflection card, where the argument changed after an error. Here the argument did not change. Stopping is the host's job. A reflection that says "I should search again" does not override it.

```python
TRACE = (
    ("search_code", "retry"),
    ("search_code", "retry"),
    ("search_code", "retry"),
    ("read_file", "retry.py"),
)
REPEATS = (("search_code", "retry"),) * 8
CAP = 6


def run(trace: tuple[tuple[str, str], ...], cap: int, stop_repeats: bool) -> tuple[list[tuple[str, str]], str]:
    seen: set[tuple[str, str]] = set()
    executed: list[tuple[str, str]] = []
    for call in trace:
        if len(executed) >= cap:
            return executed, "step cap"
        if stop_repeats and call in seen:
            return executed, "repeated call"
        seen.add(call)
        executed.append(call)
    return executed, "finished"


print(run(TRACE, CAP, True))
print(len(run(REPEATS, CAP, False)[0]), run(REPEATS, CAP, False)[1])
# ([('search_code', 'retry')], 'repeated call')
# 6 step cap
```

## Who Confirms the Trip

A travel-booking agent has six tools: search flights, search hotels, hold a fare, charge the card, email the itinerary, and cancel the booking. In this exercise the hold expires on its own and does not charge. The charge, the email, and the cancellation do not expire into safety. The user typed "book it" in the chat. Nobody has pressed a confirm button.

Which tools may run now, and which wait?

```python
TOOLS = {
    "search_flights": "read",
    "search_hotels": "read",
    "hold_fare": "hold",
    "charge_card": "money",
    "email_itinerary": "send",
    "cancel_booking": "cancel",
}
NEEDS_PERSON = {"money", "send", "cancel"}
```

**Answer:** Search and the expiring hold may run. The charge, the email, and the cancellation wait for a person. "Book it" in the chat does not set that confirmation. The button does, and the person who presses it has to see the amount and the itinerary your program computed, not the amount the model echoed. The hold is allowed only because its contract, enforced in code, is that it expires and does not capture funds. A hold that turns into a charge if you forget to cancel is a money tool and waits with the others. Reads stay on the call. Writes that leave the building wait. This is the system-level gate from Prompt Engineering applied to a booking, and it is a different product from the refund-window drill in that chapter. Log every hold even when no person is required.

```python
TOOLS = {
    "search_flights": "read",
    "search_hotels": "read",
    "hold_fare": "hold",
    "charge_card": "money",
    "email_itinerary": "send",
    "cancel_booking": "cancel",
}
NEEDS_PERSON = {"money", "send", "cancel"}


def gate(name: str, person_confirmed: bool) -> str:
    if TOOLS[name] in NEEDS_PERSON and not person_confirmed:
        return "wait"
    return "run"


chat_said_book_it = False
decisions = {name: gate(name, chat_said_book_it) for name in TOOLS}
print(sorted(name for name, choice in decisions.items() if choice == "run"))
print(sorted(name for name, choice in decisions.items() if choice == "wait"))
print(gate("charge_card", True))
# ['hold_fare', 'search_flights', 'search_hotels']
# ['cancel_booking', 'charge_card', 'email_itinerary']
# run
```

## Four Tools or Twenty-Four

A Shopify support agent on the "where is my package" page can be given 4 tools or 24. On an exercise set of 20 tracking questions, which is not a Shopify metric, the 4-tool list calls the tracking tool on 18 questions. The 24-tool list calls it on 11. Of the 9 misses, 6 call the refund tool. The refund tool is the right tool on a different page, where the customer is asking for money back.

What do you offer on the tracking page, and what do you do with the refund tool?

```python
QUESTIONS = 20
# Exercise tool-selection hits, not a Shopify metric.
HITS = {"four": 18, "twenty_four": 11}
REFUND_MISROUTES = 6
```

**Answer:** Offer the four tracking tools on this page. Exact tool match is 0.90 against 0.55. Six of the nine misses are the refund tool, which means the extra tools are not a harmless menu. They are a way to move money on a question about a package. Keep the refund tool on the refund flow, behind the write-tool checks, and off this list. Ablation is this comparison: removing the other twenty tools raised tracking selection from 11 to 18 and removed the refund misroutes on this page. It does not tell you to delete refund from the product. On a general inbox where both tools must be available, the descriptions have to say when not to use each one, and you measure the misroutes again. The concept card argued for a short list. These counts are the measurement, and they are exercise counts. A different model can mis-route a different tool. Run the ablation on the model you serve.

```python
QUESTIONS = 20
HITS = {"four": 18, "twenty_four": 11}
REFUND_MISROUTES = 6


def rate(hits: int) -> float:
    return hits / QUESTIONS


misses = QUESTIONS - HITS["twenty_four"]
print(f"{rate(HITS['four']):.2f} {rate(HITS['twenty_four']):.2f}")
print(misses, REFUND_MISROUTES, misses - REFUND_MISROUTES)
# 0.90 0.55
# 9 6 3
```

## Berlin or Lisbon

A personal assistant in the style of ChatGPT memory has three saved notes. On 10 January 2026 the user lived in Berlin and had a shellfish allergy. On 2 August 2026 a note says the user moved to Lisbon. Nothing has updated the allergy. The user asks the assistant to book a seafood dinner "in my city."

What may the assistant assume, what must it still avoid, and which tool waits?

```python
from datetime import date

MEMORIES = (
    (date(2026, 1, 10), "city", "Berlin"),
    (date(2026, 8, 2), "city", "Lisbon"),
    (date(2026, 1, 10), "allergy", "shellfish"),
)
```

**Answer:** The city key conflicts. The latest value is Lisbon, dated 2 August, and the earlier value is Berlin, dated 10 January. A suggestion can show both dates. A reservation tool does not run until the user confirms the city. Newest-wins is not an authorization to book. The allergy key has one value, shellfish, and it still constrains the dinner. Resolving the city must not drop it, and a seafood restaurant contradicts it even in the confirmed city. The eviction exercise on the concept card was about which fact to delete under a token budget. This exercise is about two live values of one key, plus a second key that is not in conflict. Store the fields with dates. Do not collapse them into a summary that says "lives in Lisbon and likes seafood."

```python
from datetime import date

MEMORIES = (
    (date(2026, 1, 10), "city", "Berlin"),
    (date(2026, 8, 2), "city", "Lisbon"),
    (date(2026, 1, 10), "allergy", "shellfish"),
)


def resolve(memories: tuple[tuple[date, str, str], ...]) -> tuple[dict[str, tuple[date, str]], list[str]]:
    latest: dict[str, tuple[date, str]] = {}
    conflicts: list[str] = []
    for when, key, value in sorted(memories):
        if key in latest and latest[key][1] != value:
            conflicts.append(key)
        latest[key] = (when, value)
    return latest, conflicts


latest, conflicts = resolve(MEMORIES)
print(conflicts, latest["city"][1], latest["allergy"][1])
print("book" if not conflicts else "wait")
# ['city'] Lisbon shellfish
# wait
```
