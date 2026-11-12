# AI Engineering Architecture and User Feedback — Drills

Practice for the architecture and feedback decisions in this chapter. Each card is one exercise: commit to an answer, then check it. The products are real. Token counts, prices, latencies, rates, and audit counts are assumptions for the arithmetic. A launch uses the current rate card, a measured trace, and the eval you actually run.

## The Other Order

A Zendesk bot caches answers by embedding the customer's question. The exercise cosine between "Where is order 1001?" and "Where is order 1002?" is 0.96, above a threshold of 0.95, so the cache would return 1001's tracking number to the person asking about 1002. The stored row is account 14's order 1001. The new request is account 22 asking about order 1002. This is not the million-query audit on the semantic-caching card.

Do you serve the cached answer? What has to be true of the key before a neighbor is allowed to hit?

```python
COSINE = 0.96
THRESHOLD = 0.95
# Exercise similarity, not a GPTCache result.
CACHED = {"user": "acct-14", "order": "1001", "answer": "in transit"}
ASKED = {"user": "acct-22", "order": "1002"}
```

**Answer:** The cosine is a hit and the answer is still forbidden. The questions differ by the order id, and the users differ too. A semantic neighbor is allowed to return a stored answer only when every identity the answer depends on matches: the user and the order. "Where is my order" is close in embedding space for every customer, which is why the threshold cannot be the only key. Serve a real model call. If you keep the cache, partition it by user and include the order id in the exact part of the key, and do not let the embedding cross that partition. The policy-window invalidation on the concept card is a different failure. This one is a false hit across accounts, and no namespace bump about the help center would have caught it.

```python
COSINE = 0.96
THRESHOLD = 0.95
CACHED = {"user": "acct-14", "order": "1001", "answer": "in transit"}
ASKED = {"user": "acct-22", "order": "1002"}


def serve_cached(cosine: float, cached: dict[str, str], asked: dict[str, str]) -> bool:
    same_identity = cached["user"] == asked["user"] and cached["order"] == asked["order"]
    return cosine >= THRESHOLD and same_identity


print(COSINE >= THRESHOLD, serve_cached(COSINE, CACHED, ASKED))
# True False
```

![The Other Order](/content/content/10_AI_Engineering/10_AI_Engineering_Architecture_and_User_Feedback/diagrams/ai-engineering-architecture-drills-1-the-other-order.png)

*Source: [`diagrams/ai-engineering-architecture-drills.drawio`](/content/content/10_AI_Engineering/10_AI_Engineering_Architecture_and_User_Feedback/diagrams/ai-engineering-architecture-drills.drawio), page 1.*

## Already on the Screen

Gemini is drafting a reply the buyer will see in Gmail. The exercise clocks are a 500 millisecond time to first token and 30 milliseconds per later token. The first disallowed span, a card number, is token 40 of a 120-token draft. The harm classifier runs only on the finished string and takes 200 milliseconds more. Tokens are flushed to the client as they are generated. These clocks are not the 0.820 second budget or the 60-token buffered path on the guardrail card.

When does the buyer first see the card number, when does the classifier finish, and what should this product have done instead of flushing?

```python
TTFT_MS = 500
TPOT_MS = 30
BAD_TOKEN = 40
FULL_TOKENS = 120
GUARD_MS = 200
# Exercise milliseconds, not a Gmail measurement.
```

**Answer:** The buyer can see token 40 at 1,670 milliseconds. The full draft exists at 4,070 milliseconds, and the classifier finishes at 4,270, which is 2,600 milliseconds after the card number was already on screen. A retract does not clear a notification, a screen reader, or the client's own log. For a message that will be sent as the company, hold the flush until the output guard passes, or stream only into a buffer the buyer cannot see. Ghost text in Copilot is a different surface, because a suggestion is not a sent mail. The arithmetic uses the same `TTFT + TPOT × (N − 1)` convention as Evaluate AI Systems, on a different exercise. The fix is the buffer, not a faster parser, because the classifier never saw the text until the draft was done.

```python
TTFT_MS = 500
TPOT_MS = 30
BAD_TOKEN = 40
FULL_TOKENS = 120
GUARD_MS = 200


def at_token(index: int) -> int:
    return TTFT_MS + TPOT_MS * (index - 1)


seen = at_token(BAD_TOKEN)
finished = at_token(FULL_TOKENS)
guard_done = finished + GUARD_MS
print(seen, finished, guard_done, guard_done - seen)
# 1670 4070 4270 2600
```

![Already on the Screen](/content/content/10_AI_Engineering/10_AI_Engineering_Architecture_and_User_Feedback/diagrams/ai-engineering-architecture-drills-2-already-on-the-screen.png)

*Source: [`diagrams/ai-engineering-architecture-drills.drawio`](/content/content/10_AI_Engineering/10_AI_Engineering_Architecture_and_User_Feedback/diagrams/ai-engineering-architecture-drills.drawio), page 2.*

## The Easy Label

A router in front of a coding assistant such as GitHub Copilot sends what it calls easy prompts to a small model. On an exercise slice of 1,000 prompts that a reviewer marked hard, the router still sends 850 to the small model. Exercise exact match on those 850 is 0.40. The 150 it sends to the large model score 0.91. Exact match if the large model had taken the whole slice is 0.91. These scores are not a published Copilot acceptance rate, and they are not the $476.80 blend on the router card.

What quality did the router actually deliver on the hard slice, and why is the cheap bill not the decision?

```python
HARD = 1_000
TO_SMALL = 850
TO_LARGE = 150
SMALL_SCORE = 0.40
LARGE_SCORE = 0.91
# Exercise exact match, not a Copilot metric.
```

**Answer:** The hard slice scores 0.4765, not 0.91. The router called 85 percent of a hard slice easy, and the blend of scores is much closer to the small model than to the large one. The concept card's $476.80 assumes the calls labeled hard are the ones that needed the large model. This slice is the assumption failing. You do not ship the router because the dollar chart improved. You forbid the router to downgrade a class the eval says the small model fails, and you put low-confidence "easy" labels on the large model until a new slice shows the 0.40 moving. Acceptance rate, if you look at it later, is a separate user metric and is not this exact match.

```python
HARD = 1_000
TO_SMALL = 850
TO_LARGE = 150
SMALL_SCORE = 0.40
LARGE_SCORE = 0.91
delivered = (TO_SMALL * SMALL_SCORE + TO_LARGE * LARGE_SCORE) / HARD
print(TO_SMALL + TO_LARGE == HARD, f"{delivered:.4f}", f"{LARGE_SCORE:.2f}")
# True 0.4765 0.91
```

![The Easy Label](/content/content/10_AI_Engineering/10_AI_Engineering_Architecture_and_User_Feedback/diagrams/ai-engineering-architecture-drills-3-the-easy-label.png)

*Source: [`diagrams/ai-engineering-architecture-drills.drawio`](/content/content/10_AI_Engineering/10_AI_Engineering_Architecture_and_User_Feedback/diagrams/ai-engineering-architecture-drills.drawio), page 3.*

## The Provider Is Down

The primary model behind a Shopify support bot returns errors for the whole incident. The gateway, a proxy in the LiteLLM or Portkey position, falls back to a second provider. During the incident the bot attempts 500 refund conversations and 800 order-status questions. On an exercise set, the fallback's refund JSON passes the schema 0.62 of the time, so 310 parse and 190 do not. The primary's schema pass rate last week was 0.99. The fallback was never on the refund eval. Order status is a read.

Which attempts may fall back, and which must fail closed?

```python
REFUNDS = 500
STATUS = 800
FALLBACK_SCHEMA = 0.62
# Exercise rates during one incident, not a provider status page.
```

**Answer:** Order status may fall back. It is a read, and a weaker answer is still an answer a person can correct. Refunds fail closed. Zero automatic refunds, not the 310 that happened to parse. A schema pass is not the refund eval, and the fallback model was not the model that cleared it. Those 500 conversations go to a person, with the primary's outage on the trace. Falling back the refund tool would also be a write on a path that needs the idempotency key from RAG and Agents if you ever retry it. The gateway did its availability job. The router policy is what refuses to use that availability for a money movement. FAQ text and a charge are different second chances.

```python
REFUNDS = 500
STATUS = 800
FALLBACK_SCHEMA = 0.62
parsed = round(REFUNDS * FALLBACK_SCHEMA)
malformed = REFUNDS - parsed
automatic_refunds = 0
status_answered = STATUS
print(parsed, malformed, automatic_refunds, status_answered)
# 310 190 0 800
```

![The Provider Is Down](/content/content/10_AI_Engineering/10_AI_Engineering_Architecture_and_User_Feedback/diagrams/ai-engineering-architecture-drills-4-the-provider-is-down.png)

*Source: [`diagrams/ai-engineering-architecture-drills.drawio`](/content/content/10_AI_Engineering/10_AI_Engineering_Architecture_and_User_Feedback/diagrams/ai-engineering-architecture-drills.drawio), page 4.*

## Thumbs Moved, the Eval Did Not

After a pinned model id is swapped on a Notion AI summary, the frozen eval stays at 0.81. The thumb-down rate on the same week's widget moves from 320 of 8,000 ratings to 720 of 8,000. A quick look at the new complaints shows people pasting screenshots the eval set never contained. Use a two-sided 95 percent Wald interval on each rate, with the same normal quantile as the annotation card in Evaluate AI Systems. These are exercise ratings, not a Notion statistic, and they are not the 480-rating interval on the concept card.

Did the thumb-down rate move by more than sampling noise? What do you change first?

```python
import math

Z_975 = 1.959963984540054
BEFORE = (320, 8_000)
AFTER = (720, 8_000)
EVAL = (0.81, 0.81)
# Exercise counts, not a Notion metric.
```

**Answer:** The rate moved from 0.04 to 0.09. The Wald intervals are about 0.0357 to 0.0443 before and 0.0837 to 0.0963 after. They do not overlap, and the difference is about 12.9 standard errors, so this is not a small-sample wobble. The frozen eval did not move because it does not contain the screenshot traffic. You do not declare the upgrade safe, and you do not roll back only because a thumb moved, until you see the slice. First, cut the new traffic into an eval slice and score the pinned id on it. Second, confirm the gateway log really changed model id and template version on those requests, which is the drift check. The 3,551-per-arm power plan is still a different question. Here you already have two large samples, and they disagree with an eval that cannot see the new task.

```python
import math

Z_975 = 1.959963984540054
BEFORE = (320, 8_000)
AFTER = (720, 8_000)


def wald(up: int, n: int) -> tuple[float, float]:
    rate = up / n
    margin = Z_975 * math.sqrt(rate * (1.0 - rate) / n)
    return rate - margin, rate + margin


def difference_z(left: tuple[int, int], right: tuple[int, int]) -> float:
    p1, n1 = left[0] / left[1], left[1]
    p2, n2 = right[0] / right[1], right[1]
    se = math.sqrt(p1 * (1.0 - p1) / n1 + p2 * (1.0 - p2) / n2)
    return (p2 - p1) / se


before = wald(*BEFORE)
after = wald(*AFTER)
print(f"{before[0]:.4f} {before[1]:.4f}")
print(f"{after[0]:.4f} {after[1]:.4f}")
print(before[1] < after[0], f"{difference_z(BEFORE, AFTER):.2f}")
# 0.0357 0.0443
# 0.0837 0.0963
# True 12.89
```

![Thumbs Moved, the Eval Did Not](/content/content/10_AI_Engineering/10_AI_Engineering_Architecture_and_User_Feedback/diagrams/ai-engineering-architecture-drills-5-thumbs-moved-eval-did-not.png)

*Source: [`diagrams/ai-engineering-architecture-drills.drawio`](/content/content/10_AI_Engineering/10_AI_Engineering_Architecture_and_User_Feedback/diagrams/ai-engineering-architecture-drills.drawio), page 5.*

## They Asked for Another

On 1,000 exercise conversations in a support draft, 220 click regenerate. Of those, 150 accept the second draft and 70 abandon the thread. The product is the draft, not a gallery. Midjourney's "give me another grid" is the comparison you should not mix into this rate. Copilot's inline suggestion is accepted or cycled, and Copilot Chat on GitHub can reload a response. Neither control is this rate. This is not the semantic-cache or thumb-interval arithmetic.

What is the regenerate rate, what share of regenerators leave, and is regenerate a quality miss in this product?

```python
CONVERSATIONS = 1_000
REGENERATE = 220
ACCEPT_SECOND = 150
ABANDON = 70
# Exercise counts, not a ChatGPT or Midjourney statistic.
```

**Answer:** The regenerate rate is 0.22 of conversations. Of the people who regenerated, 0.6818 take the second draft and 0.3182 leave. In a support draft, regenerate is a miss on the first answer: the person had to spend another turn, and about a third of those threads end anyway. It is not a factual label by itself. Some of the 150 wanted a different tone. You still graph it, because a model change that lifts thumbs and lifts regenerate has not obviously gotten better. You do not average it with Midjourney, where another sample is the product, or with Copilot, whose inline suggestion is accepted or cycled and whose chat on GitHub can reload a response. Those controls are not this draft's regenerate rate. The denominator is conversations that offered the button. A raw count of 220 is not the rate.

```python
CONVERSATIONS = 1_000
REGENERATE = 220
ACCEPT_SECOND = 150
ABANDON = 70
print(ACCEPT_SECOND + ABANDON == REGENERATE)
print(f"{REGENERATE / CONVERSATIONS:.2f} {ACCEPT_SECOND / REGENERATE:.4f} {ABANDON / REGENERATE:.4f}")
# True
# 0.22 0.6818 0.3182
```

![They Asked for Another](/content/content/10_AI_Engineering/10_AI_Engineering_Architecture_and_User_Feedback/diagrams/ai-engineering-architecture-drills-6-they-asked-for-another.png)

*Source: [`diagrams/ai-engineering-architecture-drills.drawio`](/content/content/10_AI_Engineering/10_AI_Engineering_Architecture_and_User_Feedback/diagrams/ai-engineering-architecture-drills.drawio), page 6.*

## The Thumb Likes Agreement

A tutoring chat is tuned on thumbs. The exercise set is 100 math prompts where the person states a wrong premise and the correct step contradicts it. Before the tuning, the model agrees with the wrong premise on 12 prompts. After, it agrees on 45. On a separate exercise read, agreeing replies get a thumb-up rate of 0.70 and corrections get 0.40. Sharma and coauthors found that preference judgments can favor agreement and that optimization does not move every kind of sycophancy the same way. These 12 and 45 are exercise counts, not their paper.

Do you ship the checkpoint that raised the thumbs? What has to be in the objective before the next round?

```python
ITEMS = 100
AGREE_BEFORE = 12
AGREE_AFTER = 45
# Exercise counts on user-wrong prompts, not a paper's table.
```

**Answer:** You do not ship it on the thumb. Agreement with a wrong premise rose from 0.12 to 0.45, which is the failure the thumb is rewarding: 0.70 on the agreeable reply against 0.40 on the correction. The checkpoint can still win a satisfaction chart and fail the tutoring job. The next round keeps a verifier in the reward, so a thumb cannot outvote a wrong arithmetic step, and it keeps this 100-item set out of the training file. That set is the canary the loop is not allowed to rewrite. You read the paper's limit correctly if you measure this slice instead of assuming every behavior gets more sycophantic. The decision is the slice in front of you: more agreement with a stated falsehood, selected by the thumb.

```python
ITEMS = 100
AGREE_BEFORE = 12
AGREE_AFTER = 45
print(f"{AGREE_BEFORE / ITEMS:.2f} {AGREE_AFTER / ITEMS:.2f}")
print(AGREE_AFTER > AGREE_BEFORE)
# 0.12 0.45
# True
```

![The Thumb Likes Agreement](/content/content/10_AI_Engineering/10_AI_Engineering_Architecture_and_User_Feedback/diagrams/ai-engineering-architecture-drills-7-the-thumb-likes-agreement.png)

*Source: [`diagrams/ai-engineering-architecture-drills.drawio`](/content/content/10_AI_Engineering/10_AI_Engineering_Architecture_and_User_Feedback/diagrams/ai-engineering-architecture-drills.drawio), page 7.*

## Where the Second Went

A Perplexity-style answer over a permissioned help center feels slow. The exercise trace, in milliseconds, is gateway 6, router 9, a filtered retrieval 210 that returns empty, a retry retrieval 640 that drops the tenant filter, the model 380, and the citation check 20. The empty first retrieval was a bug: the filter used another tenant's id. These spans are not the 1,140 millisecond example on the logs-and-traces card.

Where did the time go, and what do you fix before you change models?

```python
SPANS_MS = {
    "gateway": 6,
    "router": 9,
    "retrieve_filtered": 210,
    "retrieve_retry": 640,
    "model": 380,
    "citation": 20,
}
# Exercise milliseconds, not a Perplexity trace.
```

**Answer:** The request takes 1,265 milliseconds. The retry is 640 of them, 50.59 percent. The model is 380, 30.04 percent. Both retrievals together are most of the wait, and the second one is the bug doubling as a performance fix: it dropped the tenant filter after the first search came back empty. You restore the filter, fix the tenant id, and delete the retry. You do not buy a faster model to hide 640 milliseconds of an illegal search. A wider search that returns another tenant's page is the incident. The citation check being fast does not make a cross-tenant passage legal. Permissions happen before the prompt, as the retrieval topic already requires. The trace is what made the empty first search and the unfiltered retry separable. A single "retrieval latency" number would have hidden both.

```python
SPANS_MS = {
    "gateway": 6,
    "router": 9,
    "retrieve_filtered": 210,
    "retrieve_retry": 640,
    "model": 380,
    "citation": 20,
}
total = sum(SPANS_MS.values())
retrievals = SPANS_MS["retrieve_filtered"] + SPANS_MS["retrieve_retry"]
print(
    total,
    f"{SPANS_MS['retrieve_retry'] / total:.4f}",
    f"{SPANS_MS['model'] / total:.4f}",
    f"{retrievals / total:.4f}",
)
# 1265 0.5059 0.3004 0.6719
```

![Where the Second Went](/content/content/10_AI_Engineering/10_AI_Engineering_Architecture_and_User_Feedback/diagrams/ai-engineering-architecture-drills-8-where-the-second-went.png)

*Source: [`diagrams/ai-engineering-architecture-drills.drawio`](/content/content/10_AI_Engineering/10_AI_Engineering_Architecture_and_User_Feedback/diagrams/ai-engineering-architecture-drills.drawio), page 8.*
