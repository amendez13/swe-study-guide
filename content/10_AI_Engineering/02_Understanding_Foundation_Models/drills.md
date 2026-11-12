# Understanding Foundation Models — Drills

Practice for the model decisions in this chapter. Each card is one exercise: commit to an answer, then check it. The products are real. Token prices, pass rates, latencies, and GPU peaks are assumptions for the arithmetic. A launch uses the current rate card, a measured tokenizer, and the GPU you actually have.

## Sharp or Loose

GitHub Copilot shows ghost text while someone types. The exercise budget is 300 milliseconds, and a surprising token is inserted into the file. A ChatGPT or Claude brainstorm was asked for ten titles, and the user can wait a few seconds. An Expensify-style receipt reader must return a total the rest of the program can parse.

What temperature and top_p do you set on each, and what does the receipt need besides a low temperature?

```python
CASES = {
    "copilot-ghost-text": {"latency_ms": 300, "wants_variety": False, "must_parse": False},
    "chatgpt-brainstorm": {"latency_ms": 5000, "wants_variety": True, "must_parse": False},
    "receipt-total": {"latency_ms": 2000, "wants_variety": False, "must_parse": True},
}
```

**Answer:** Ghost text gets temperature 0 and top_p 1. The suggestion has to be the mode, because the user did not ask for a surprise, and 300 milliseconds leaves no room for a second sample. The brainstorm gets temperature 0.9 and top_p left at 1, so only one knob moves. A nucleus of 0.95 at temperature 1 is the other coherent choice. Stacking 0.9 on top of 0.95 makes the sample hard to explain, which is why OpenAI's temperature documentation says to change one of the two. The receipt gets temperature 0, top_p 1, and a JSON schema. Temperature 0 repeats the leading token. It does not make the string valid JSON. The schema mask does that, and a parser still checks the total against the receipt.

```python
CASES = {
    "copilot-ghost-text": {"latency_ms": 300, "wants_variety": False, "must_parse": False},
    "chatgpt-brainstorm": {"latency_ms": 5000, "wants_variety": True, "must_parse": False},
    "receipt-total": {"latency_ms": 2000, "wants_variety": False, "must_parse": True},
}


def settings(latency_ms: int, wants_variety: bool, must_parse: bool) -> tuple[float, float, str]:
    extra = "greedy"
    temperature = 0.0
    if must_parse:
        extra = "json schema"
    elif wants_variety and latency_ms >= 1000:
        temperature = 0.9
        extra = "one knob"
    return (temperature, 1.0, extra)


for name, case in CASES.items():
    print(name, settings(**case))
# copilot-ghost-text (0.0, 1.0, 'greedy')
# chatgpt-brainstorm (0.9, 1.0, 'one knob')
# receipt-total (0.0, 1.0, 'json schema')
```

## Seventy Billion

You are placing a 70-billion-parameter model on an A100 or H100 that reports 81920 MiB, which is 80 GiB. BF16 and FP16 store 2 bytes per parameter. INT8 stores 1 byte. A 4,096-token KV cache on the Llama 70B attention shape, computed in the attention card, is 1.25 GiB. A 131,072-token cache on that shape is 40 GiB.

How much memory do the weights take in each precision? What fits on one GPU, and how many 4,096-token caches fit in the INT8 spare if that spare were entirely cache?

```python
PARAMS = 70_000_000_000
GPU_GIB = 80
CACHE_4K_GIB = 1.25
CACHE_128K_GIB = 40.0
GIB = 1024**3
```

**Answer:** BF16 or FP16 weights are 130.4 GiB and do not fit on one 80 GiB GPU. INT8 weights are 65.2 GiB and fit, with 14.8 GiB spare. That spare holds eleven 1.25 GiB caches only if the runtime takes none of it, so "about ten short contexts" is the planning sentence, and a single 40 GiB long-context cache does not fit beside the INT8 weights on that GPU. A whiteboard that says "140 GB versus 80 GB" reaches the same conclusion for BF16, because 70 billion times 2 bytes is 140 decimal GB. It reaches a different spare at INT8, 10 decimal GB rather than 14.8 GiB. Name the unit. Quantization scales add a little on top of the 1-byte estimate. Training with Adam is a different budget, on the order of 18 bytes per parameter, and it is not this serving question.

```python
PARAMS = 70_000_000_000
GPU_GIB = 80
CACHE_4K_GIB = 1.25
CACHE_128K_GIB = 40.0
GIB = 1024**3


def weight_gib(bytes_per_param: int) -> float:
    return PARAMS * bytes_per_param / GIB


bf16_gib = weight_gib(2)
int8_gib = weight_gib(1)
spare_gib = GPU_GIB - int8_gib
short_caches = int(spare_gib // CACHE_4K_GIB)
print(round(bf16_gib, 1), round(int8_gib, 1), round(spare_gib, 1))
print(bf16_gib <= GPU_GIB, int8_gib <= GPU_GIB, short_caches, spare_gib >= CACHE_128K_GIB)
# 130.4 65.2 14.8
# False True 11 False
```

## Twenty per Parameter

A pretraining plan has to pick a token count. Use the Chinchilla rule of thumb of about 20 tokens per parameter, which is the training-compute split, not a law about the best model to serve. Separately, treat 15 trillion tokens as the exercise stand-in for the scale Meta reported for Llama 3 pretraining.

How many tokens does the rule suggest for a 7-billion-parameter model and for a 70-billion-parameter model? If an 8-billion-parameter model trains on those 15 trillion tokens, how many tokens per parameter is that, and why would a team do it on purpose?

```python
TOKENS_PER_PARAM = 20
SEVEN_B = 7_000_000_000
SEVENTY_B = 70_000_000_000
EIGHT_B = 8_000_000_000
LLAMA3_TOKENS = 15_000_000_000_000
```

**Answer:** The rule suggests 140 billion tokens for the 7B model and 1.4 trillion tokens for the 70B model. The 1.4 trillion figure is Chinchilla's own training length for a 70B model. Fifteen trillion tokens on an 8B model is 1,875 tokens per parameter, which is 93.75 times the rule, so the run is far past the training-compute optimum. The reason to pass that optimum is inference. The training FLOPs are paid once. Every Copilot suggestion and every chat turn pays the inference cost of the model you kept. A smaller model that has seen more tokens can be the better checkpoint to serve. The ratio is still the check on the opposite mistake: a 70B model trained on a few tens of billions of tokens is the undertrained shape Chinchilla was written to retire.

```python
TOKENS_PER_PARAM = 20
SEVEN_B = 7_000_000_000
SEVENTY_B = 70_000_000_000
EIGHT_B = 8_000_000_000
LLAMA3_TOKENS = 15_000_000_000_000


def per_parameter(tokens: int, params: int) -> float:
    return tokens / params


seen = per_parameter(LLAMA3_TOKENS, EIGHT_B)
print(TOKENS_PER_PARAM * SEVEN_B, TOKENS_PER_PARAM * SEVENTY_B)
print(seen, seen / TOKENS_PER_PARAM)
# 140000000000 1400000000000
# 1875.0 93.75
```

## Broken JSON

A receipt extractor returns a preamble, then a markdown fence, then `{"total": 12.50,}` with a trailing comma. The receipt total is 12.50.

Which of the four structured-output methods removes this failure, and why is a finetune the wrong first purchase? The salvage below is the post-processing you could ship this afternoon.

```python
import json
import re

FENCE = "`" * 3
RAW = "Here is the object:\n" + FENCE + "json\n" + '{"total": 12.50,}\n' + FENCE
WRONG_BUT_VALID = '{"total": 999.0}'
```

**Answer:** Constrained decoding removes this class of failure. A JSON schema mask will not sample the preamble, the fence, or the trailing comma, because those tokens leave the grammar. A stricter prompt reduces how often they appear and still leaks. The salvage parses this sample to 12.5, and it also parses `{"total": 999.0}`, which is legal JSON and the wrong total. Post-processing stays in the stack as a parser that checks types and ranges. It is a bad place to stop. Finetuning is the purchase you make when valid objects keep holding the wrong fields, the schema is stable, the volume is high, and you have examples of the right fields. It is an expensive way to forbid a trailing comma. The grammar has not seen the receipt, so the total is still checked against the document.

```python
import json
import re

FENCE = "`" * 3
RAW = "Here is the object:\n" + FENCE + "json\n" + '{"total": 12.50,}\n' + FENCE
WRONG_BUT_VALID = '{"total": 999.0}'


def salvage(raw: str) -> dict[str, float]:
    start = raw.find("{")
    end = raw.rfind("}")
    body = re.sub(r",\s*}", "}", raw[start : end + 1])
    parsed = json.loads(body)
    return {key: float(value) for key, value in parsed.items()}


print(salvage(RAW), salvage(WRONG_BUT_VALID))
# {'total': 12.5} {'total': 999.0}
```

## Wrong Twice

A Zendesk or Intercom bot answers from a help-center article. The article says the return window is 30 days, through the returns portal. You draw two samples on the same prompt, at the temperature the bot is actually using.

Four outcomes show up in the logs. Both samples say 30 days. Both samples say 30 days and describe the portal in different words. One sample says 30 days and the other says 60. Both samples say 60 days.

Which outcomes are inconsistency, which are hallucination, and which knob can fix which outcome?

```python
CASES = (
    ("both-say-30", True, True),
    ("two-wordings-of-30", False, True),
    ("30-and-60", False, False),
    ("both-say-60", True, False),
)
```

**Answer:** Both samples saying 30 days is a stable, supported answer. Different wordings that both match the article are inconsistency of phrasing, and a string compare will call it a failure when the fact survived. One sample at 30 and one at 60 is inconsistency and a hallucination together: the 60-day sample adds a window the article does not support. Lowering the temperature, or taking a vote, helps this cell when 30 is the mode, and the article check still has to reject a 60 that slips through. Both samples saying 60 is a consistent hallucination. The mode is wrong, so a lower temperature repeats 60 more reliably. That one wants the article in the prompt, an abstention when the draft disagrees with the retrieved page, or a field checked against the article. Sampling knobs are for the cell where the samples disagree. They are the wrong tool for the cell where the samples agree on a false window.

```python
CASES = (
    ("both-say-30", True, True),
    ("two-wordings-of-30", False, True),
    ("30-and-60", False, False),
    ("both-say-60", True, False),
)


def diagnose(agree: bool, supported: bool) -> str:
    if supported and agree:
        return "stable"
    if supported:
        return "wording only"
    if agree:
        return "consistent hallucination"
    return "mixed hallucination"


for name, agree, supported in CASES:
    print(name, diagnose(agree, supported))
# both-say-30 stable
# two-wordings-of-30 wording only
# 30-and-60 mixed hallucination
# both-say-60 consistent hallucination
```

## Best of Eight

A background coding agent may draw several patches and keep one that passes the unit tests. One sample passes those tests 40 percent of the time. The exercise prices are $0.50 per million input tokens and $2.00 per million output tokens. Each sample sends 2,000 input tokens and writes 400 output tokens. The team runs 10,000 tasks a day. One sample takes 250 milliseconds of model time, and the test suite takes 2,000 milliseconds after the samples return. Copilot-style ghost text in this exercise has a 300 millisecond budget and no test suite in the loop.

What does best-of-8 do to the pass rate and to the bill, and which product can spend it?

```python
TASKS = 10_000
N = 8
P_PASS = 0.4
SAMPLE_MS = 250
TEST_MS = 2_000
INLINE_BUDGET_MS = 300
INPUT_TOKENS = 2_000
OUTPUT_TOKENS = 400
INPUT_USD_PER_MILLION = 0.50
OUTPUT_USD_PER_MILLION = 2.00
```

**Answer:** Under an independence assumption, the chance that at least one of eight samples passes is 98.3 percent, because `1 − 0.6^8` is about 0.983. Shared bugs break that assumption, so eight copies of the same mistake stay near 40 percent. Measure pass@8 on the repository. The formula is a ceiling. Without a prompt cache, the day goes from $18 to $144. With the prompt cached so the input is billed once, the day is $74, because the eight generations are still billed. Ghost text cannot spend this. One sample fits in 300 milliseconds, and a sample plus the suite does not. The background agent can. Parallel samples keep the model wait near 250 milliseconds and still pay for eight outputs. The suite, not the sampling temperature, is what makes the extra samples a search.

```python
TASKS = 10_000
N = 8
P_PASS = 0.4
SAMPLE_MS = 250
TEST_MS = 2_000
INLINE_BUDGET_MS = 300
INPUT_TOKENS = 2_000
OUTPUT_TOKENS = 400
INPUT_USD_PER_MILLION = 0.50
OUTPUT_USD_PER_MILLION = 2.00


def day_usd(input_bills: int, output_bills: int) -> float:
    input_cost = TASKS * input_bills * INPUT_TOKENS / 1_000_000 * INPUT_USD_PER_MILLION
    output_cost = TASKS * output_bills * OUTPUT_TOKENS / 1_000_000 * OUTPUT_USD_PER_MILLION
    return input_cost + output_cost


ceiling = 1 - (1 - P_PASS) ** N
one_fits = SAMPLE_MS <= INLINE_BUDGET_MS
with_tests_fits = SAMPLE_MS + TEST_MS <= INLINE_BUDGET_MS
print(round(100 * ceiling, 1), day_usd(1, 1), day_usd(N, N), day_usd(1, N))
print(one_fits, with_tests_fits)
# 98.3 18.0 144.0 74.0
# True False
```

## Show or Prefer

Three checkpoints are on the table, and each one has a different gap.

A raw Llama base model is given "Classify this ticket:" and writes another ticket. You have several thousand replies that agents actually sent. A Llama 3 Instruct checkpoint already produces both a two-sentence reply and a long one. Another supervised pass on the short replies did not stop the long ones, and you have preference pairs. A third Instruct checkpoint has the format and the tone the raters prefer, and it still quotes a return window the help center changed yesterday.

Which lever do you pull?

```python
CASES = {
    "base-continues-the-prompt": {
        "emits_behavior": False,
        "pairs_still_needed": False,
        "facts_changed": False,
    },
    "instruct-ranks-the-long-reply": {
        "emits_behavior": True,
        "pairs_still_needed": True,
        "facts_changed": False,
    },
    "yesterday-policy": {
        "emits_behavior": True,
        "pairs_still_needed": False,
        "facts_changed": True,
    },
}
```

**Answer:** The base model gets supervised finetuning. The preferred behavior is absent, so a preference loss has nothing nearby to reinforce. DPO in particular is weak when the winning answer is far from the reference model. The Instruct model that already emits both lengths, and that a further supervised pass did not fix, gets preference finetuning: DPO on the pairs, or a reward model and RLHF if you also want that scorer for best-of-N. The stale window gets retrieval. The policy changed after training, and neither supervised finetuning nor a preference update is a place to store a fact that will change again. The prompt still carries the instruction in all three cases.

```python
CASES = {
    "base-continues-the-prompt": {
        "emits_behavior": False,
        "pairs_still_needed": False,
        "facts_changed": False,
    },
    "instruct-ranks-the-long-reply": {
        "emits_behavior": True,
        "pairs_still_needed": True,
        "facts_changed": False,
    },
    "yesterday-policy": {
        "emits_behavior": True,
        "pairs_still_needed": False,
        "facts_changed": True,
    },
}


def lever(emits_behavior: bool, pairs_still_needed: bool, facts_changed: bool) -> str:
    if facts_changed:
        return "retrieval"
    if not emits_behavior:
        return "sft"
    if pairs_still_needed:
        return "preference"
    return "prompt"


for name, case in CASES.items():
    print(name, lever(**case))
# base-continues-the-prompt sft
# instruct-ranks-the-long-reply preference
# yesterday-policy retrieval
```

## One Long Paste

A service holds Llama 70B weights in BF16, 130.4 GiB, across 80 GiB GPUs. The attention shape is the public Llama 70B configuration: 80 layers, 8 key-value heads, head dimension 128, keys and values in BF16. A user pastes 131,072 tokens. Another request is only 4,096 tokens. Full multi-head attention on this model would be 64 key-value heads.

How big is the KV cache for one request at each length, how many GPUs hold the weights plus that cache, and what did grouped-query attention change?

```python
import math

LAYERS = 80
KV_HEADS = 8
FULL_HEADS = 64
HEAD_DIM = 128
BYTES = 2
WEIGHT_GIB = 130.4
GPU_GIB = 80
SHORT = 4_096
LONG = 131_072
```

**Answer:** One token adds 327,680 bytes. A 4,096-token request is 1.25 GiB of cache. A 131,072-token request is 40 GiB. Weights plus the short cache are 131.7 GiB, so two 80 GiB GPUs hold them. Weights plus the long cache are 170.4 GiB, so two GPUs miss and three are the minimum. With 64 key-value heads the long cache is 320 GiB, and the weights plus that cache need six GPUs. Grouped-query attention is the difference between those two long-context bills. The count is weights plus one request's cache, before activations, fragmentation, and a second concurrent paste. Four concurrent 131,072-token requests would be 160 GiB of cache on top of the 130.4 GiB of weights.

```python
import math

LAYERS = 80
KV_HEADS = 8
FULL_HEADS = 64
HEAD_DIM = 128
BYTES = 2
WEIGHT_GIB = 130.4
GPU_GIB = 80
SHORT = 4_096
LONG = 131_072


def cache_gib(tokens: int, kv_heads: int) -> float:
    byte_count = 2 * LAYERS * kv_heads * HEAD_DIM * BYTES * tokens
    return byte_count / 1024**3


def gpus(cache: float) -> int:
    return math.ceil((WEIGHT_GIB + cache) / GPU_GIB)


short = cache_gib(SHORT, KV_HEADS)
long = cache_gib(LONG, KV_HEADS)
full = cache_gib(LONG, FULL_HEADS)
print(short, long, full)
print(gpus(short), gpus(long), gpus(full))
# 1.25 40.0 320.0
# 2 3 6
```
