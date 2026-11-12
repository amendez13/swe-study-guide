# Inference Optimization — Drills

Practice for the serving decisions in this chapter. Each card is one exercise: commit to an answer, then check it. The products are real. Prices, acceptance rates, profiler snapshots, and activation peaks that are not derived from a public model shape or a named datasheet are assumptions for the arithmetic. A launch uses the current rate card, the GPU you actually have, and the eval you run.

## The Stall in the Stream

The chat pane of a product such as ChatGPT or Claude.ai is missing its latency caps whenever traffic rises. The exercise measurements below are not a vendor status page. Quiet and loaded are the two hours you captured. TTFT already includes the first token, so a 40-token reply takes `TTFT + TPOT × (N − 1)`, the same convention as Evaluate AI Systems. The caps are TTFT at or under 0.80 seconds, average TPOT at or under 0.040 seconds, and p99 inter-token latency at or under 0.050 seconds.

Which clocks actually fail under load, and what do you change first?

```python
N = 40
SLO_TTFT, SLO_TPOT, SLO_P99_ITL = 0.80, 0.040, 0.050
# Exercise clocks, in seconds, not a ChatGPT or Claude measurement.
QUIET = {"ttft": 0.35, "tpot": 0.018, "p99_itl": 0.022}
LOADED = {"ttft": 1.40, "tpot": 0.024, "p99_itl": 0.160}
```

**Answer:** Under load, TTFT and the p99 gap fail, and the average TPOT still passes. A 40-token reply moves from 1.052 seconds quiet to 2.336 seconds loaded. The loaded decode rate implied by the average TPOT is 41.7 tokens a second, inside a 0.040 second cap, so a dashboard that only plots average TPOT stays green. The p99 gap of 0.160 seconds is the prefill of a new request running on the same GPUs as the streams already in flight. Continuous batching does not prevent that. Quantizing the weights does not remove a 160 ms scheduling stall. The first change is to stop running the whole prefill inline: chunk it, or move prefill to its own pool the way DistServe and Splitwise do, and add capacity if the 1.40 second TTFT is the queue rather than the prompt. Then reread p99 ITL. The average is the clock that was hiding the miss.

```python
N = 40
SLO_TTFT, SLO_TPOT, SLO_P99_ITL = 0.80, 0.040, 0.050
QUIET = {"ttft": 0.35, "tpot": 0.018, "p99_itl": 0.022}
LOADED = {"ttft": 1.40, "tpot": 0.024, "p99_itl": 0.160}


def wait(sample: dict) -> float:
    return sample["ttft"] + sample["tpot"] * (N - 1)


for name, sample in (("quiet", QUIET), ("loaded", LOADED)):
    print(
        f"{wait(sample):.3f} {1 / sample['tpot']:.1f} "
        f"{sample['ttft'] <= SLO_TTFT} {sample['tpot'] <= SLO_TPOT} "
        f"{sample['p99_itl'] <= SLO_P99_ITL}"
    )
# 1.052 55.6 True True True
# 2.336 41.7 False True False
```

## Thirty-Two Thousand Tokens

You have one H100 SXM5, sold as 80 GB, and this topic treats that label as 80 GiB. You want a 32,768-token context. The 8B candidate is the untied Llama 3 8B shape: 8,030,261,248 parameters, 32 layers, 8 key-value heads, head dimension 128, BF16 weights at 2 bytes. The 70B candidate uses the figures from Understanding Foundation Models: 131.4 GiB of BF16 weights, 65.7 GiB at INT8, and 320 KiB of BF16 cache per token. Two activation peaks below are exercise profiler readings for the INT8 70B prefill, not a published H100 trace.

Which launches fit on the one GPU?

```python
BUDGET_GIB = 80
# Exercise activation peaks, in GiB, not a profiler log.
PEAKS = (3.0, 8.0)
```

**Answer:** The 8B in BF16 fits. Its weights are 14.96 GiB and a 32,768-token cache is exactly 4 GiB, so the sum is 18.96 GiB, with room for activations. The 70B in BF16 does not fit: 131.4 GiB of weights misses an 80 GiB GPU before the cache is added, and the cache at this length is another 10 GiB. The 70B in INT8 is 65.7 GiB of weights plus that 10 GiB of cache, 75.7 GiB before activations. Adding the 3.0 GiB exercise peak lands at 78.7 GiB, inside the budget with almost no room for fragmentation. Adding the 8.0 GiB peak lands at 83.7 GiB and misses. You can defend the 8B on this GPU today. You can defend the INT8 70B only after a profile on this SKU shows a peak near the smaller exercise number, and after the task slice still passes at INT8. A sum of 78.7 GiB is not leftover headroom. If the product needs the 70B and the larger peak is real, the weights have to be split across GPUs. That is a parallelism decision, not a hope that 83.7 will fit.

```python
PARAMS_8B = 8_030_261_248
PER_TOKEN_8B = 2 * 32 * 8 * 128 * 2
WEIGHTS_8B = PARAMS_8B * 2 / 1024**3
CACHE_8B = PER_TOKEN_8B * 32_768 / 1024**3
CACHE_70B = 327_680 * 32_768 / 1024**3
BUDGET_GIB = 80
PEAKS = (3.0, 8.0)
print(f"{WEIGHTS_8B:.2f} {CACHE_8B:.2f} {WEIGHTS_8B + CACHE_8B:.2f}")
print(f"{131.4 + CACHE_70B:.1f} {131.4 <= BUDGET_GIB}")
static_70b = 65.7 + CACHE_70B
print(f"{CACHE_70B:.1f} {static_70b:.1f}")
for peak in PEAKS:
    total = static_70b + peak
    print(f"{total:.1f} {total <= BUDGET_GIB}")
# 14.96 4.00 18.96
# 141.4 False
# 10.0 75.7
# 78.7 True
# 83.7 False
```

## The Overnight Queue

A support desk in the class of Zendesk summarizes tickets that nobody is waiting on, and it also summarizes the ticket an agent has open. The exercise volume is 250,000 overnight tickets and 4,000 tickets that are open right now. Each ticket is 2,200 input tokens and 180 output tokens. The exercise synchronous rates are $0.80 per million input tokens and $3.20 per million output tokens. The batch path is half of those rates, the 50 percent shape both OpenAI's Batch API and Anthropic's Message Batches documented on 12 November 2026, not a contract you skip rereading. The overnight job can land the next morning. The open ticket cannot.

What do you send to the batch API, and what is the bill?

```python
OVERNIGHT, URGENT = 250_000, 4_000
INPUT_TOKENS, OUTPUT_TOKENS = 2_200, 180
INPUT_RATE, OUTPUT_RATE = 0.80, 3.20
```

**Answer:** Send the 250,000 overnight tickets to the batch API and leave the 4,000 open tickets on the synchronous API. The overnight pile is $584.00 synchronous and $292.00 at half off. The open tickets are $9.34 either way, because a person is blocked on them and the batch window does not apply. The mixed bill is $301.34. Running everything synchronously is $593.34. Running the open tickets through the batch API would keep the $292.00 overnight saving and make the agent wait with the digest. The half is the published discount shape used for this exercise. The current price page replaces it, and a ticket that becomes urgent moves back to the synchronous rate for that one call.

```python
OVERNIGHT, URGENT = 250_000, 4_000
INPUT_TOKENS, OUTPUT_TOKENS = 2_200, 180
INPUT_RATE, OUTPUT_RATE = 0.80, 3.20


def bill(calls: int, scale: float = 1.0) -> float:
    input_cost = calls * INPUT_TOKENS / 1_000_000 * INPUT_RATE * scale
    output_cost = calls * OUTPUT_TOKENS / 1_000_000 * OUTPUT_RATE * scale
    return input_cost + output_cost


mixed = bill(OVERNIGHT, 0.5) + bill(URGENT)
print(f"{bill(OVERNIGHT):.2f} {bill(OVERNIGHT, 0.5):.2f} {bill(URGENT):.2f}")
print(f"{bill(OVERNIGHT + URGENT):.2f} {mixed:.2f}")
# 584.00 292.00 9.34
# 593.34 301.34
```

## One Hundred Forty Tokens

An internal code assistant, the latency class of inline completion, has to match an exercise decode rate of 140 tokens a second per stream at batch 1. That is a TPOT of 7.1 ms under this chapter's definition, the gap after the first token. The box is one A100 80GB SXM, whose datasheet bandwidth is 2,039 GB/s. The model is the untied Llama 3 8B, 8,030,261,248 parameters. BF16 weights are 2 bytes. The INT8 candidate is 1 byte. The INT4 candidate in this drill is a raw 0.5 byte packing, scales ignored, so its ceiling is an optimistic roof. The measured tokens per second and the exact-match counts are exercise results on 400 held-out lines, not an A100 benchmark and not a published score. The quality bar is 0.75 exact match. This A100 has no FP8 tensor cores.

Which checkpoint do you serve?

```python
SLO_TPS = 140
ITEMS = 400
# Exercise measurements, not an A100 profile and not a model-card score.
MEASURED_TPS = {"bf16": 105, "int8": 160, "int4": 220}
CORRECT = {"bf16": 332, "int8": 316, "int4": 244}
```

**Answer:** Serve the INT8 checkpoint. The A100 80GB SXM roofs are 127.0 tokens a second in BF16, 253.9 in INT8, and 507.8 for the raw INT4 packing. The BF16 roof itself is under 140, so a better kernel cannot get BF16 across this SLO. Its exercise measurement of 105 is inside that roof and still short. INT8's measurement of 160 clears 140 and is under its roof of 253.9. INT4's measurement of 220 also clears 140. The exact-match rates are 0.830, 0.790, and 0.610. The bar is 0.75, so INT4 fails the lines and INT8 passes. FP8 is not a candidate on this GPU. A group scale would lower the INT4 roof from 507.8 and would not fix 244 correct out of 400. Recompute the roofs if you move the job to an H100 SXM5, because that SKU's bandwidth is not 2,039 GB/s, and rerun the 400 lines on the checkpoint you pin.

```python
PARAMS = 8_030_261_248
BANDWIDTH = 2_039 * 10**9
SLO_TPS = 140
ITEMS = 400
MEASURED_TPS = {"bf16": 105, "int8": 160, "int4": 220}
CORRECT = {"bf16": 332, "int8": 316, "int4": 244}
BYTES = {"bf16": 2, "int8": 1, "int4": 0.5}
for name, width in BYTES.items():
    ceiling = BANDWIDTH / (PARAMS * width)
    accuracy = CORRECT[name] / ITEMS
    print(
        f"{ceiling:.1f} {MEASURED_TPS[name] >= SLO_TPS} "
        f"{accuracy:.3f} {accuracy >= 0.75} {MEASURED_TPS[name] <= ceiling}"
    )
print(f"{1 / SLO_TPS * 1e3:.1f}")
# 127.0 False 0.830 True True
# 253.9 True 0.790 True True
# 507.8 True 0.610 False True
# 7.1
```

## Which Draft

A self-hosted completion server can attach one of three drafts to a target it already serves. The acceptance rates, draft lengths, and cost coefficients are exercise values for this traffic, not a number from Leviathan and coauthors. Their formula is the one the speculative-decoding card uses. A draft of γ tokens at acceptance rate α and cost c has expected speedup `(1 − α^(γ+1)) / ((1 − α)(γc + 1))`. Draft B is also being offered at γ = 8 with the same α and c. The tokenizer is already shared. A speedup below 1 is a slowdown.

Which draft do you run, and do you lengthen B?

```python
# Exercise acceptance and cost, not a paper's speedup table.
# Name, alpha, gamma, cost coefficient.
DRAFTS = (
    ("A", 0.90, 3, 0.25),
    ("B", 0.60, 5, 0.02),
    ("C", 0.30, 5, 0.15),
)
LONGER_B = ("B8", 0.60, 8, 0.02)
```

**Answer:** Run draft B at γ = 5, and do not lengthen it to 8. A is a closer model and a slower one. It yields 3.44 tokens per target step and a speedup of 1.97× because each of its three draft steps costs a quarter of a target step. B yields 2.38 tokens and a speedup of 2.17×, because the draft is cheap. C yields 1.43 tokens and a speedup of 0.82×, which is slower than decoding the target alone. The weak match is the failure, not the size. Lengthening B to γ = 8 raises the expected tokens only to 2.47 and drops the speedup to 2.13×. The extra draft tokens are not accepted often enough to pay for themselves at α = 0.60. You would rerun this arithmetic on a measured acceptance rate from your own completion logs before you pinned the pair. A brainstorming traffic mix with a lower α can push B under 1 even though this exercise does not.

```python
def speedup(alpha: float, gamma: int, cost: float) -> tuple[float, float]:
    expected = (1 - alpha ** (gamma + 1)) / (1 - alpha)
    return expected, expected / (gamma * cost + 1)


for name, alpha, gamma, cost in (
    ("A", 0.90, 3, 0.25),
    ("B", 0.60, 5, 0.02),
    ("C", 0.30, 5, 0.15),
    ("B8", 0.60, 8, 0.02),
):
    expected, factor = speedup(alpha, gamma, cost)
    print(f"{expected:.2f} {factor:.2f} {factor > 1}")
# 3.44 1.97 True
# 2.38 2.17 True
# 1.43 0.82 False
# 2.47 2.13 True
```

## The Tool List First

A support assistant in the class of Intercom Fin sends a long stable instruction and tool list, then the ticket, on every call. The exercise prompt is 12,000 tokens of instructions and 2,000 tokens of ticket, with 150 tokens of output. The exercise rates are $3.00 per million input tokens, $12.00 per million output tokens, a cache-read price of $0.30, and a cache-write price of $3.75, which is 1.25 times the input rate. Those four numbers are not a price page. The cached portion has to be a prefix. One million calls is the volume for the steady-state bill. You also need the cost of a prefix that is used once and the cost of a prefix that is used twice, write on the first call and read on the second.

Where does the ticket go, and when is the cache worth marking?

```python
CALLS = 1_000_000
PREFIX, TICKET, OUTPUT = 12_000, 2_000, 150
INPUT_RATE, OUTPUT_RATE = 3.00, 12.00
READ_RATE, WRITE_RATE = 0.30, 3.75
```

**Answer:** Put the 12,000-token instruction first and the ticket after it. Mark the instruction for caching. At one million calls the uncached bill is $43,800 and the cached bill is $11,400, a saving of $32,400. The ticket and the output are paid in full every time. If the ticket is placed first, the prefix changes on every call and the cache misses, so you pay $43,800 and you also pay the write premium on a prefix that never hits. A prefix used once costs $0.0450 to write against $0.0360 to send uncached, which is $0.0090 more, so you do not mark a one-shot prompt. A prefix used twice costs $0.0486 against $0.0720 uncached, a saving of $0.0234, so the second use is what pays for the write. The instruction qualifies. The ticket does not. The rates are an exercise. The prefix rule is not.

```python
CALLS = 1_000_000
PREFIX, TICKET, OUTPUT = 12_000, 2_000, 150
INPUT_RATE, OUTPUT_RATE = 3.00, 12.00
READ_RATE, WRITE_RATE = 0.30, 3.75


def million(prefix_rate: float) -> float:
    return (
        CALLS * PREFIX / 1_000_000 * prefix_rate
        + CALLS * TICKET / 1_000_000 * INPUT_RATE
        + CALLS * OUTPUT / 1_000_000 * OUTPUT_RATE
    )


once_plain = PREFIX / 1_000_000 * INPUT_RATE
once_write = PREFIX / 1_000_000 * WRITE_RATE
twice_plain = 2 * once_plain
twice_cached = once_write + PREFIX / 1_000_000 * READ_RATE
print(f"{million(INPUT_RATE):.0f} {million(READ_RATE):.0f}")
print(f"{million(INPUT_RATE) - million(READ_RATE):.0f}")
print(f"{once_plain:.4f} {once_write:.4f} {once_write - once_plain:.4f}")
print(f"{twice_plain:.4f} {twice_cached:.4f} {twice_plain - twice_cached:.4f}")
# 43800 11400
# 32400
# 0.0360 0.0450 0.0090
# 0.0720 0.0486 0.0234
```

## Four GPUs, One Suggestion

You have four H100 SXM5 GPUs and the Llama 3 70B checkpoint from Understanding Foundation Models, 70,553,706,496 parameters, 131.4 GiB in BF16. Inline suggestions, the latency class of Copilot, need a TPOT at or under 25 ms for a single request. Ignore the KV cache in the step time. This drill's question is the bandwidth roof, not a profile. Pipeline parallelism runs the stages one after another, so one request takes the full weight bytes divided by 3.35 TB/s. Tensor parallelism splits the weights four ways and adds an exercise collective tax of 25 percent on that shorter step. The tax stands in for collective latency. The 0.018-microsecond NVLink payload on the parallelism card is not this tax. A 32,768-token cache on this shape is part of the fit check only.

Which split meets the cap, and do both splits fit?

```python
PARAMS = 70_553_706_496
SLO_MS = 25
TAX = 1.25  # Exercise collective latency, not an NVLink measurement.
```

**Answer:** Tensor parallelism meets the cap. Pipeline parallelism does not. The BF16 weights are 131.4 GiB. One request through four pipeline stages takes 42.1 ms at the H100 SXM5's 3.35 TB/s, 23.7 tokens a second, which misses 25 ms. The same request with the weights split four ways, plus the 25 percent exercise tax, takes 13.2 ms, 76.0 tokens a second, which clears the cap. Both splits fit the memory. Each GPU holds a quarter of the weights, 32.85 GiB, and a quarter of the 10 GiB cache for 32,768 tokens if the cache is sharded with the layers or the heads, 2.50 GiB. The sum on one GPU is 35.35 GiB of an 80 GiB card. Fit is not the question. A single inline suggestion cannot fill a four-stage pipe, so pipeline parallelism waits out the full model. The overnight batch, where you can keep 32 microbatches in flight, is the case where that pipe stops being the latency path. The 25 percent tax is an exercise. The split without that tax is 10.5 ms, and the step reaches the 25 ms cap only if the collective multiplies the split by 2.37. Measure the collective on these four GPUs before you call the cap met.

```python
PARAMS = 70_553_706_496
BANDWIDTH = 3.35e12
SLO_MS = 25
TAX = 1.25
WEIGHTS = PARAMS * 2
per_gpu = WEIGHTS / 4 / 1024**3
cache = 327_680 * 32_768 / 1024**3
pp_ms = WEIGHTS / BANDWIDTH * 1e3
untaxed_ms = (WEIGHTS / 4) / BANDWIDTH * 1e3
tp_ms = untaxed_ms * TAX
print(f"{WEIGHTS / 1024**3:.1f} {per_gpu:.2f} {cache:.2f} {per_gpu + cache / 4:.2f}")
print(f"{pp_ms:.1f} {1 / (pp_ms / 1e3):.1f} {pp_ms <= SLO_MS}")
print(f"{tp_ms:.1f} {1 / (tp_ms / 1e3):.1f} {tp_ms <= SLO_MS}")
print(f"{untaxed_ms:.1f} {SLO_MS / untaxed_ms:.2f}")
# 131.4 32.85 10.00 35.35
# 42.1 23.7 False
# 13.2 76.0 True
# 10.5 2.37
```

## Four Tokens a Second

A vLLM process on one H100 SXM5 is serving the untied Llama 3 8B in BF16, 8,030,261,248 parameters. An exercise snapshot, not a vLLM benchmark, shows 3.6 tokens a second and 4.0 GiB resident on the GPU. The HBM ceiling is the weight-only roof from the memory card, using the datasheet's 3.35 TB/s. The other ceiling is the one-way reading of that datasheet's PCIe Gen5 line. The line prints 128 GB/s next to NVLink, and that total is bidirectional, so the planning ceiling is 64 GB/s. Someone on the review wants a new fused kernel.

What is the bottleneck, and what do you change?

```python
MEASURED_TPS = 3.6  # Exercise rate, not a vLLM benchmark.
RESIDENT_GIB = 4.0  # Exercise residency, not a memory profile.
```

**Answer:** The weights are not on the GPU, and a fused kernel will not fix that. The BF16 weights are 14.96 GiB. The snapshot shows 4.0 GiB resident, so the checkpoint is streaming from the host. The HBM roof is 208.6 tokens a second. The one-way PCIe ceiling, at 64 GB/s, is 4.0 tokens a second. Dividing the same weights by the printed 128 GB/s produces 8.0, and that reading treats both directions as if they carried the weights. The measured 3.6 is 0.90 of the one-way ceiling and 0.017 of the HBM roof. You are close to saturating the bus you are actually using. Dividing 3.6 by 208.6 and calling it a bad matmul sends you into a kernel project that cannot move bytes across PCIe any faster. Load the weights into HBM, confirm residency near 14.96 GiB plus runtime, and only then remeasure model bandwidth utilization against the 208.6 roof. If that second measurement is still far below the roof, the kernel and the launch overhead become the question. They are not the question in this snapshot.

```python
PARAMS = 8_030_261_248
WEIGHTS = PARAMS * 2
HBM = 3.35e12
PCIE_ONE_WAY = 64 * 10**9
MEASURED_TPS = 3.6
RESIDENT_GIB = 4.0
hbm_ceiling = HBM / WEIGHTS
pcie_ceiling = PCIE_ONE_WAY / WEIGHTS
printed_both_ways = (128 * 10**9) / WEIGHTS
print(f"{WEIGHTS / 1024**3:.2f}")
print(f"{hbm_ceiling:.1f} {pcie_ceiling:.1f} {printed_both_ways:.1f}")
print(f"{MEASURED_TPS / hbm_ceiling:.3f} {MEASURED_TPS / pcie_ceiling:.2f}")
print(RESIDENT_GIB < WEIGHTS / 1024**3)
# 14.96
# 208.6 4.0 8.0
# 0.017 0.90
# True
```
