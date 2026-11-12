# Finetuning — Drills

Practice for the finetuning decisions in this chapter. Each card is one exercise: commit to an answer, then check it. The products are real. Accuracies, prices, loss curves, and activation peaks that are not derived from a public model shape are assumptions for the arithmetic. A launch uses the checkpoint you trained, the current rate card, and the eval you actually run.

## Indemnity or liability

Harvey is asked to label a clause a lawyer has highlighted. Counsel has signed off on six labels: indemnity, limitation of liability, termination, governing law, confidentiality, and other. The definitions were frozen last quarter and are not expected to move this half. The volume below is an exercise, not a Harvey traffic figure. So are the accuracies and the two prices. The general model is the one you call with a long prompt. The small model is one you would finetune and host.

Which lever do you ship for the steady state, and what do you leave in the prompt?

```python
CLAUSES = 500_000
# Exercise accuracies, not a Harvey benchmark.
ACCURACY = {"zero_shot": 0.84, "few_shot": 0.91, "playbook_rag": 0.92, "finetune": 0.96}
# Exercise dollars per million tokens, not a rate card.
GENERAL_IN, GENERAL_OUT = 0.50, 2.00
SMALL_IN, SMALL_OUT = 0.15, 0.60
# Input tokens, then output tokens.
SHAPES = {"few_shot": (700, 6), "playbook_rag": (900, 6), "finetune": (140, 6)}
```

**Answer:** Ship the finetune, and keep a short instruction that names the six labels. The clause text is already in the request, so there is no corpus to retrieve. The gap that remains after the few-shot prompt is a boundary between labels, indemnity against limitation of liability, which is a behavior. A playbook paste scores 0.92 against the few-shot 0.91 and spends more tokens to do it. The finetune scores 0.96. At the exercise prices, half a million clauses cost $181.00 few-shot, $231.00 with the playbook paste, and $12.30 to run the small finetuned model. Those three numbers are inference only. The training job is not in the $12.30. The inference gap against few-shot is $168.70 on this volume, so a modest training run is paid for, and this exercise does not price that run. Retrieval over case law would answer a different question, what a jurisdiction has held, and it would not pick the label. If counsel rewrote the definitions every week, the definitions would go back in the prompt and the weights would not be the store for that text. They are not rewriting them. The held-out clauses are an eval set, not more training data.

```python
CLAUSES = 500_000
ACCURACY = {"zero_shot": 0.84, "few_shot": 0.91, "playbook_rag": 0.92, "finetune": 0.96}
GENERAL_IN, GENERAL_OUT = 0.50, 2.00
SMALL_IN, SMALL_OUT = 0.15, 0.60
SHAPES = {"few_shot": (700, 6), "playbook_rag": (900, 6), "finetune": (140, 6)}


def bill(tokens_in: int, tokens_out: int, rate_in: float, rate_out: float) -> float:
    return CLAUSES * tokens_in / 1_000_000 * rate_in + CLAUSES * tokens_out / 1_000_000 * rate_out


few = bill(*SHAPES["few_shot"], GENERAL_IN, GENERAL_OUT)
rag = bill(*SHAPES["playbook_rag"], GENERAL_IN, GENERAL_OUT)
tuned = bill(*SHAPES["finetune"], SMALL_IN, SMALL_OUT)
print(f"{few:.2f} {rag:.2f} {tuned:.2f}")
print(ACCURACY["finetune"] > ACCURACY["few_shot"] > ACCURACY["zero_shot"])
# 181.00 231.00 12.30
# True
```

## The 4090

You will QLoRA-finetune the Llama 2 13B shape on one RTX 4090, sold as 24 GB. The layout is the public one: 40 layers, hidden size 5,120, intermediate size 13,824, vocabulary 32,000, untied embeddings, no biases. The adapters are rank 16 on every linear layer of the block, and they use the 16-byte AdamW accounting: BF16 weight, BF16 gradient, FP32 master, and two FP32 moments. The base is packed at the QLoRA paper's double-quantized width, 4.126953 bits for every parameter, including the embeddings. Two activation peaks below are exercise measurements from a profiler, not a published 4090 benchmark. The budget used here is 24 GiB.

Which launch configuration fits, and why is a full AdamW finetune not the alternative?

```python
def llama2_params(layers: int, hidden: int, intermediate: int, vocab: int = 32_000) -> int:
    per_layer = 4 * hidden * hidden + 3 * intermediate * hidden + 2 * hidden
    return layers * per_layer + hidden + 2 * vocab * hidden


PARAMS = llama2_params(40, 5120, 13824)
BITS = 4 + 8 / 64 + 32 / (64 * 256)
LORA = 40 * (4 * 16 * (5120 + 5120) + 3 * 16 * (13824 + 5120))
# Exercise activation peaks, in GiB, not a profiler log from a 4090.
PEAKS = (("batch 1, seq 2048, checkpointed", 5.5), ("batch 4, seq 4096", 18.0))
BUDGET_GIB = 24
```

**Answer:** Ship the checkpointed batch of 1 at sequence 2,048. The Llama 2 13B layout is 13,015,864,320 parameters. A full 16-byte AdamW state is 194.0 GiB, so it does not fit this card no matter how you set the batch. The FP32-gradient variant, 18 bytes, is 218.2 GiB and does not fit either. A second 24 GB card is 48 GiB and still does not hold the 16-byte state. The QLoRA static state under this drill's assumption, every parameter packed at 4.126953 bits plus 16 bytes on the adapters, is 7.19 GiB. Adding the exercise peak of 5.5 GiB lands at 12.69 GiB, inside 24. Adding the 18.0 GiB peak lands at 25.19 GiB and misses. The miss is activations, not the 13B weights. The repair is the smaller microbatch, the shorter sequence, and checkpointing. Leave headroom for fragmentation. 12.69 GiB of a 24 GiB budget has it. 25.19 does not. bitsandbytes would also leave the embedding and the output projection in BF16, so the static floor on a real load is a bit higher than 7.19 GiB and still has to be profiled. Re-profile on the card you will train on. These peaks are exercise numbers.

```python
def llama2_params(layers: int, hidden: int, intermediate: int, vocab: int = 32_000) -> int:
    per_layer = 4 * hidden * hidden + 3 * intermediate * hidden + 2 * hidden
    return layers * per_layer + hidden + 2 * vocab * hidden


PARAMS = llama2_params(40, 5120, 13824)
BITS = 4 + 8 / 64 + 32 / (64 * 256)
LORA = 40 * (4 * 16 * (5120 + 5120) + 3 * 16 * (13824 + 5120))
PEAKS = (("batch 1, seq 2048, checkpointed", 5.5), ("batch 4, seq 4096", 18.0))
BUDGET_GIB = 24
BYTES = 16
STATIC = PARAMS * BITS / 8 + LORA * BYTES
print(PARAMS)
print(f"{PARAMS * BYTES / 1024**3:.1f} {PARAMS * (BYTES + 2) / 1024**3:.1f}")
print(f"{STATIC / 1024**3:.2f}")
for name, peak in PEAKS:
    total = STATIC / 1024**3 + peak
    print(f"{total:.2f} {total <= BUDGET_GIB}")
# 13015864320
# 194.0 218.2
# 7.19
# 12.69 True
# 25.19 False
```

## Rank against coverage

A GitHub issue triager labels an issue bug, feature, or question. You are choosing a LoRA on the Llama 2 13B shape: 40 layers, hidden size 5,120, intermediate size 13,824. The three candidate adapters are below. The macro-F1 figures are exercise scores on your held-out issues, not a GitHub metric and not the QLoRA paper's table.

Which adapter do you train?

```python
# Exercise macro-F1, not a published score.
CANDIDATES = (
    ("rank 8, query and value", 0.71),
    ("rank 64, query and value", 0.74),
    ("rank 8, all linear layers", 0.86),
)
```

**Answer:** Train rank 8 on all seven linear layers of the block. It has 31,293,440 trainable parameters and an exercise macro-F1 of 0.86. Rank 64 on query and value has more parameters, 52,428,800, and scores 0.74. Rank 8 on query and value has 6,553,600 parameters and scores 0.71. The extra rank bought 0.03 on the pair of attention matrices and spent 45.9 million parameters to do it. Covering the MLP projections, the gate, the up projection, and the down projection, is where the exercise score moves. That lines up with the direction of the QLoRA paper's finding, that the set of adapted layers mattered more than the rank in their run. It is not their number. If a later eval showed the all-linear adapter memorizing issues, you would drop rank or add data, not go back to query and value on the evidence here. Embeddings and the output head stay frozen. Recompute the F1 on your own issues before you lock the config.

```python
def lora_params(layers: int, hidden: int, intermediate: int, rank: int, all_linear: bool) -> int:
    matrices = 2 if not all_linear else 4
    attention = matrices * rank * (hidden + hidden)
    feed_forward = 0
    if all_linear:
        feed_forward = 3 * rank * (intermediate + hidden)
    return layers * (attention + feed_forward)


COUNTS = (
    lora_params(40, 5120, 13824, 8, False),
    lora_params(40, 5120, 13824, 64, False),
    lora_params(40, 5120, 13824, 8, True),
)
SCORES = (0.71, 0.74, 0.86)
best = max(range(3), key=lambda index: SCORES[index])
print(*COUNTS)
print(best, COUNTS[1] > COUNTS[2], SCORES[1] < SCORES[2])
# 6553600 52428800 31293440
# 2 True True
```

## Fifty customers

A support platform serves one Llama 2 7B base and one LoRA per customer, the serving pattern vLLM's multi-LoRA support and S-LoRA are built for. Each adapter is rank 8 on all seven linear layers. The base is the untied Llama 2 7B layout in BF16, 32 layers, hidden size 4,096, intermediate size 11,008. Fifty customers are the exercise tenancy, not a published vLLM limit. You also have to hold the KV cache for the live requests. A 2,048-token request on this shape is the cache you should compute. The card is sold as 24 GB, and the budget used here is 24 GiB.

Do the fifty adapters fit, and what actually pushes the card over?

```python
CUSTOMERS = 50
CONCURRENCY = (8, 16)
TOKENS = 2048
BUDGET_GIB = 24
```

**Answer:** The adapters fit. The base is 12.55 GiB in BF16, the same weights the inference card rounds to 12.6 GiB. One all-linear rank-8 adapter is 19,988,480 parameters, 38.125 MiB in BF16, and fifty of them are 1.86 GiB. Base plus adapters is 14.41 GiB. Fifty full BF16 copies of the base would be 627.56 GiB, which is the number that makes the adapter design the one to serve. The cache is the other term. One 2,048-token request is 1 GiB on this 32-head shape, half of the 2 GiB a 4,096-token context costs. Eight concurrent requests add 8 GiB and the total is 22.41 GiB, inside the budget with little room. Sixteen concurrent requests add 16 GiB and the total is 30.41 GiB, over. You ship the fifty adapters on one base and you cap concurrency. Merging the fifty into a single weight would destroy the per-customer behavior. The server's current rules decide which ranks can share a batch. The cache does not shrink because the adapter files are small.

```python
def llama2_params(layers: int, hidden: int, intermediate: int, vocab: int = 32_000) -> int:
    per_layer = 4 * hidden * hidden + 3 * intermediate * hidden + 2 * hidden
    return layers * per_layer + hidden + 2 * vocab * hidden


PARAMS = llama2_params(32, 4096, 11008)
LORA = 32 * (4 * 8 * (4096 + 4096) + 3 * 8 * (11008 + 4096))
BASE = PARAMS * 2
ADAPTERS = 50 * LORA * 2
PER_TOKEN = 2 * 32 * 32 * 128 * 2
print(LORA)
print(f"{BASE / 1024**3:.2f} {ADAPTERS / 1024**3:.2f} {(BASE + ADAPTERS) / 1024**3:.2f}")
print(f"{50 * BASE / 1024**3:.2f}")
for live in (8, 16):
    total = (BASE + ADAPTERS + live * PER_TOKEN * 2048) / 1024**3
    print(f"{total:.2f} {total <= 24}")
# 19988480
# 12.55 1.86 14.41
# 627.56
# 22.41 True
# 30.41 False
```

## A wrong total

You serve Llama 2 13B in vLLM with GPTQ INT4 weights, for practice problems of the kind a tutoring product such as Khanmigo has to get right. The prose looks fine. On an exercise slice of 200 arithmetic items, the BF16 checkpoint answers 156 correctly and the INT4 checkpoint answers 97. An exercise chat rating stays at 0.90 for both. Neither figure is a Khanmigo score or a published GPTQ table.

What do you change, and why did the chat rating miss it?

```python
ITEMS = 200
BF16_CORRECT = 156
INT4_CORRECT = 97
CHAT_RATING = 0.90
```

**Answer:** Keep INT4 off the arithmetic path. The BF16 model gets 0.780 of the exercise items and the INT4 model gets 0.485, so this is a quantization failure, not proof that the base cannot do the step. INT4 has 16 codes in the group, and a chat rating of 0.90 on both checkpoints will never see a dropped digit. The repairs, in the order you would try them, are a calculator tool for the arithmetic, the capability-tool pattern, and a higher-precision copy on this route. INT8, or BF16, on the requests that contain a quantity. A finer group size and a calibration set that includes worked arithmetic are the quantizer-side experiments if you must stay in 4 bits. Leaving the output projection in BF16 is the matrix to protect first, because a rounding error there changes the token. Do not wait for the chat rating to fall. Score the arithmetic slice the way the eval pipeline scores a domain task separately from a preference.

```python
ITEMS = 200
print(f"{156 / ITEMS:.3f} {97 / ITEMS:.3f}")
print(round(156 / ITEMS - 97 / ITEMS, 3))
print(0.90 == 0.90)
# 0.780 0.485
# 0.295
# True
```

## Code plus chat

You trained two finetunes from the same Llama 2 7B base. One saw code demonstrations. One saw support-chat demonstrations. They do not share their training data anymore. The product wants both skills. The scores below are exercise scores on your coding set and your chat set, not HumanEval and not a published merge paper. A single weight file is optional. vLLM can load both adapters.

Do you sum the task vectors, run TIES, or serve both adapters?

```python
# Exercise scores as (coding, chat), not a leaderboard.
SCORES = {
    "code specialist": (0.48, 0.31),
    "chat specialist": (0.22, 0.61),
    "sum at lambda 1": (0.30, 0.40),
    "TIES": (0.41, 0.55),
}
```

**Answer:** Serve the two adapters on the shared base. The requests are separable, a completion against a support reply, and one file is not required. The code specialist's 0.48 and the chat specialist's 0.61 both survive, because nothing is added. The equal-weight sum is the failure: coding falls from 0.48 to 0.30 and chat falls from 0.61 to 0.40, which is the coordinate cancellation you get when both finetunes edited the same weights. TIES keeps more of each, 0.41 and 0.55, and it still gives up 0.07 of coding and 0.06 of chat against the specialists. You would ship TIES only if a phone or a single model id forced one checkpoint, and you would say so with both numbers, not with their average. The average of the TIES pair is 0.48, which flatters a model that lost coding skill. The two finetunes share a base, so a task vector is legal. A merge onto a different family would not be. Joint multi-task training is the path if, later, one request needs both skills in the same forward pass and the data can sit in one job.

```python
SCORES = {
    "code specialist": (0.48, 0.31),
    "chat specialist": (0.22, 0.61),
    "sum at lambda 1": (0.30, 0.40),
    "TIES": (0.41, 0.55),
}


def average(pair: tuple[float, float]) -> float:
    return (pair[0] + pair[1]) / 2


print(f"{average(SCORES['TIES']):.2f}")
print(SCORES["TIES"][0] < SCORES["code specialist"][0])
print(SCORES["sum at lambda 1"][0] < SCORES["TIES"][0])
# 0.48
# True
# True
```

## NaN and a third epoch

An Axolotl QLoRA run is training Llama 2 7B to draft replies to GitHub issues. Two exercise loss curves are below. They are not an Axolotl log. Run A records train and eval loss at the end of three epochs. Run B's training loss is NaN at step 80.

Which checkpoint do you keep, and what do you change on the run you discard?

```python
# Exercise losses, not a training log.
RUN_A_TRAIN = (2.40, 1.10, 0.35)
RUN_A_EVAL = (2.45, 2.05, 2.70)
RUN_B_TRAIN_STEP_80 = float("nan")
```

**Answer:** Keep the checkpoint after epoch 2, eval loss 2.05, and do not promote epoch 3. The three recorded points are the ends of epochs 1, 2, and 3. Training loss fell from 2.40 to 0.35 across those epochs while eval fell from 2.45 to 2.05 and then rose to 2.70. That rise is overfitting. More epochs will copy the issue replies, not generalize them. The repairs are the earlier checkpoint, fewer passes, and more issue pairs if you still need the training loss to mean something. Run B is a different fault. A NaN at step 80 is a step size or a numeric range problem. If the run is in FP16, switch it to BF16 and keep the learning rate, because FP16 overflows at 65,504 and BF16 has the range. If the run is already in BF16, cut the learning rate by 10 and start again. Change one of those, not both, or you will not know which one fixed the NaN. Do not average the two runs and do not keep training B to see if the NaN heals. Read a generated reply from the epoch-2 checkpoint before you ship it. The eval set that produced 2.05 stays out of the training file.

```python
RUN_A_TRAIN = (2.40, 1.10, 0.35)
RUN_A_EVAL = (2.45, 2.05, 2.70)
best = min(range(3), key=lambda epoch: RUN_A_EVAL[epoch]) + 1
print(best, RUN_A_EVAL[best - 1], RUN_A_TRAIN[2] < RUN_A_TRAIN[0])
print(RUN_A_EVAL[2] > RUN_A_EVAL[1])
run_b_step_80 = float("nan")
print(run_b_step_80 != run_b_step_80)
# 2 2.05 True
# True
# True
```

## The size that fits

A Zendesk intent classifier has to train and then serve on one RTX 4090, sold as 24 GB. The launch bar is an exercise accuracy of 0.90. The three candidates are a whiteboard 1 billion parameters, the Llama 2 7B layout, and the Llama 2 13B layout. Accuracies are exercise scores, not a Zendesk benchmark. Serving is BF16 weights plus a 1,024-token KV cache for one request. The budget is 24 GiB.

Which base do you finetune?

```python
# Exercise accuracy, not a published classifier score.
ACCURACY = {"1B": 0.84, "7B": 0.93, "13B": 0.94}
BAR = 0.90
TOKENS = 1024
BUDGET_GIB = 24
```

**Answer:** Finetune the Llama 2 7B. It scores 0.93, over the bar, and one request at 1,024 tokens is 13.05 GiB of BF16 weights plus cache, inside 24. The whiteboard 1B is 1.86 GiB of weights and scores 0.84, under the bar. A model that fits and misses the label bar is the wrong save. The 13B scores 0.94, a gain of 0.01 over the 7B, and its BF16 weights alone are 24.24 GiB. With a 1,024-token cache the request is 25.03 GiB, over the card before a batch. You would be training a base you cannot serve in the precision you just measured. Full 16-byte AdamW of the 7B is the 100.4 GiB training state from the training-memory card, so the training method on this card is QLoRA, not a full update. The 113.0 GiB figure is the same layout with FP32 gradients, and it does not fit either. INT4 serving of the 13B might fit and is a different accuracy experiment. It is not justified by 0.01 on an exercise score. Pin the 7B, and keep the intent eval off the training set.

```python
def llama2_params(layers: int, hidden: int, intermediate: int, vocab: int = 32_000) -> int:
    per_layer = 4 * hidden * hidden + 3 * intermediate * hidden + 2 * hidden
    return layers * per_layer + hidden + 2 * vocab * hidden


def kv_bytes(layers: int, kv_heads: int, head_dim: int, tokens: int) -> int:
    return 2 * layers * kv_heads * head_dim * 2 * tokens


P7 = llama2_params(32, 4096, 11008)
P13 = llama2_params(40, 5120, 13824)
GIB = 1024**3
serve_7 = (P7 * 2 + kv_bytes(32, 32, 128, 1024)) / GIB
serve_13 = (P13 * 2 + kv_bytes(40, 40, 128, 1024)) / GIB
print(f"{1_000_000_000 * 2 / GIB:.2f}")
print(f"{P13 * 2 / GIB:.2f}")
print(f"{serve_7:.2f} {serve_13:.2f}")
print(0.93 >= 0.90, serve_7 <= 24, serve_13 <= 24, 0.84 >= 0.90)
# 1.86
# 24.24
# 13.05 25.03
# True True False False
```
