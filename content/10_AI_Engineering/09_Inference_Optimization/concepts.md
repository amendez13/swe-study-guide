## What inference optimization is

Inference optimization is the work of serving a trained model inside a latency, throughput, and cost budget while keeping the quality you measured.

A training job pays the forward and backward passes once, or once per experiment. Serving pays a forward pass on every ChatGPT turn, every Claude reply, every Copilot suggestion, and every nightly summary. The autoregressive loop from the transformer card in [Understanding Foundation Models](../02_Understanding_Foundation_Models/) writes one token at a time, and the KV cache from that same card grows with the prompt. Those two facts are why a checkpoint that fit in a demo can miss a product. The latency and cost criteria in [Evaluate AI Systems](../04_Evaluate_AI_Systems/) decide whether the wait and the bill are acceptable. This topic is how those numbers move: by changing the checkpoint, or by changing the server around it.

The model half compresses weights, drafts extra tokens, shrinks attention state, and fuses kernels. The service half batches requests, separates prompt reading from token writing, reuses a repeated prefix, and spreads one model across accelerators. None of that is a license to skip the eval. A faster wrong total is a regression. The quantization and distillation cards in [Finetuning](../07_Finetuning/) and [Dataset Engineering](../08_Dataset_Engineering/) own the accuracy and the training contract. The cards here own the bytes, the bandwidth, and the schedule.

**Trade-offs.** Chasing tokens per second fills the GPU and can push time to first token past the point where a person is still waiting. Chasing the first token leaves the GPU underfilled and raises the cost of every request. A technique that changes the output distribution has to be scored again. A technique that only changes the schedule can still fail the same score if it times out and returns an error. The budget you write down is part of the optimization. A number you did not write down will be the one the technique spends.

**Interview.** Separate the model from the service before you name a library. Say which phase is slow, the prompt or the generated tokens, and which budget moved: latency, throughput under a latency cap, or dollars. Then say you would remeasure the task slice, not the demo. If the question is "how do we make the 70B faster," the first answer is the phase and the byte count, not a kernel name.

**Recap.** Inference optimization makes a trained model serve tokens inside a latency, throughput, and cost budget without giving up measured quality. Training pays the backward pass. Serving pays a forward pass on every request. The model half changes weights, drafts, attention state, and kernels. The service half changes batching, phase placement, prefix reuse, and how many accelerators hold the model. A faster answer that fails the eval is not the goal.

## Prefill and decode

Prefill and decode are the two phases of one generated reply. Prefill reads the prompt and writes the KV cache. Decode appends one new token at a time and reads that cache back.

The split is the serving form of the causal transformer. The model cannot emit token 40 until it has a key and a value for token 39, so the generated half of the request is a loop. The prompt is different. Every prompt token is already known, so the server can run those positions together. That parallel pass is the prefill. It is why a long paste in Claude or ChatGPT sits on "thinking" before the first word, and why the same model then streams words at a steadier pace. The attention card in [Understanding Foundation Models](../02_Understanding_Foundation_Models/) names the two phases and the cache they share. The roofline card is why they feel different: prefill does a lot of arithmetic per byte, and decode moves the weights again to produce one token.

vLLM, TensorRT-LLM, and the hosted APIs all schedule these phases, whether or not the dashboard shows the names. A request's time to first token includes the queue and the prefill. The gaps after that are decode. A long retrieved document makes the first clock worse even when the decode kernel is unchanged. A huge model makes the second clock worse even when the prompt is short. Optimizing the wrong phase is how a team quantizes weights to fix a stall that was a 20,000-token prefill.

**Trade-offs.** Spending the design on decode leaves a long-context product waiting on the first token. Spending it on prefill leaves a chat that starts quickly and then crawls. The two phases also contend when they share a GPU: a new prefill can pause every decode already in flight, which is the disaggregation card. Splitting them removes that pause and adds a pool you have to size. Short prompts and long answers are a decode problem. Long prompts and short answers are a prefill problem. Copilot inline suggestions and a book-length summary are not the same phase.

**Interview.** Define the two phases from the causal mask, not from a profiler screenshot. Prefill consumes the prompt in parallel and writes keys and values. Decode is serial in the generated tokens and reads those keys and values. Say which product symptom maps to which phase. Then say the next question is arithmetic intensity, because "the GPU is at 100 percent" does not tell you which ceiling you hit.

**Recap.** Prefill reads the whole prompt and builds the KV cache. Decode walks the generation one token at a time because each token depends on the one before it. Time to first token is mostly queue plus prefill. The later gaps are decode. A long prompt and a long answer stress different ceilings, and a fix for one phase does not move the other.

## Arithmetic intensity and the roofline

Arithmetic intensity is the floating-point work a kernel does per byte it moves. The roofline is the pair of ceilings that intensity runs into: peak compute, and peak memory bandwidth.

Williams, Waterman, and Patterson published the model in 2009. A chip can issue only so many operations per second, and it can move only so many bytes per second. The ridge point is peak FLOPs divided by peak bandwidth, in FLOPs per byte. A kernel whose intensity is below the ridge is memory-bandwidth-bound. It finishes when the bytes arrive, with arithmetic units waiting. A kernel above the ridge is compute-bound. It finishes when the arithmetic units are done, with bandwidth to spare. Buying a faster ALU does nothing for a kernel below the ridge. Buying faster memory does nothing for a kernel above it.

The H100 SXM5 is the worked chip. Its dense BF16 tensor-core peak is 989.4 TFLOPS, the figure in [Understanding Foundation Models](../02_Understanding_Foundation_Models/), and the datasheet lists its HBM bandwidth at 3.35 TB/s. This topic treats that 3.35 as `3.35 × 10^12` bytes per second. The ridge is 295.3 FLOPs per byte. One square BF16 projection of hidden size 4,096, the Llama 3 8B width, shows the two regimes. The FLOP count is `2 × sequence × 4096 × 4096`, a multiply and an add. The bytes are the input, the weight, and the output at 2 bytes each. At one token the intensity is 1.00 FLOP per byte, far below the ridge, so that step is bandwidth-bound. At 4,096 tokens the intensity is 1,365.3 FLOPs per byte, above the ridge, so that step is compute-bound. The crossover for this single projection is about 345 tokens. The A100 80GB SXM ridge, 312 TFLOPS over its datasheet 2,039 GB/s, is 153.0 FLOPs per byte. H100's tensor-core peak grew by more than its memory bandwidth, so a layer that sat nearer the ridge on A100 is more clearly bandwidth-bound on H100.

```python
HIDDEN = 4096
H100_RIDGE = 989.4e12 / 3.35e12
A100_RIDGE = 312e12 / 2.039e12


def intensity(seq: int) -> float:
    flops = 2 * seq * HIDDEN * HIDDEN
    nbytes = 2 * (seq * HIDDEN + HIDDEN * HIDDEN + seq * HIDDEN)
    return flops / nbytes


crossover = H100_RIDGE * HIDDEN / (HIDDEN - 2 * H100_RIDGE)
print(f"{H100_RIDGE:.1f} {A100_RIDGE:.1f}")
print(f"{intensity(1):.2f} {intensity(4096):.1f}")
print(f"{crossover:.0f}")
print(intensity(1) < H100_RIDGE < intensity(4096))
# 295.3 153.0
# 1.00 1365.3
# 345
# True
```

This is one linear layer, with its input, weight, and output counted, and with no KV cache. Attention and the cache add bytes, so a real decode stays bandwidth-bound even further out. A real prefill of a long prompt stays compute-bound. That is the computational bottleneck behind the two phases. The `6ND` training estimate in Understanding Foundation Models is a cousin: about `2N` FLOPs for a forward token, ignoring attention until the sequence is long. The intensity above is that forward arithmetic divided by the bytes the layer touches.

**Trade-offs.** A compute optimization on a bandwidth-bound decode burns a week and leaves tokens per second where they were. A bandwidth optimization on a compute-bound prefill does the same in the other direction. Raising the batch raises intensity, because the weights are loaded once and reused, and it also raises the wait for the request that arrived first. The ridge moves when you change chips or dtypes. An INT8 tensor-core peak and a 1-byte weight are a different ridge than BF16.

**Interview.** Draw the ridge as peak FLOPs over peak bandwidth and put a number on it for a named SKU: 295.3 FLOPs per byte on the H100 SXM5 at the dense BF16 peak and 3.35 TB/s. Then put one token and a 4,096-token prefill on either side of it for a 4,096-wide BF16 projection, 1.00 against 1,365.3. Say the crossover for that layer is about 345 tokens, and that the KV cache pushes decode further toward bandwidth. Close with the decision rule: name the bound before you pick the optimization.

**Recap.** Arithmetic intensity is FLOPs per byte moved. The roofline's ridge is peak FLOPs divided by peak bandwidth. On an H100 SXM5 that ridge is 295.3 FLOPs per byte for dense BF16 and the datasheet's 3.35 TB/s. A 4,096-wide BF16 projection at one token has intensity 1.00 and is bandwidth-bound. At 4,096 tokens it has intensity 1,365.3 and is compute-bound. The crossover is about 345 tokens for that layer alone. Prefill of a long prompt is the compute side. Decode of one token is the bandwidth side.

## Online and batch inference APIs

An online inference API returns tokens inside an interactive wait. A batch inference API accepts a pile of requests and returns them later, at a lower price per token.

The online path is ChatGPT, Claude.ai, Copilot, and any call your own service makes while a person or a downstream tool is blocked. The clocks on the next cards are the contract: time to first token, the gap between later tokens, and a timeout. The batch path is the overnight job. OpenAI's Batch API documents a 24-hour completion window. Anthropic's Message Batches API is the same shape of asynchronous job, and the current docs have its window. Both have been offered at about half the synchronous token price. The window and the discount move. The price page you would actually sign is the one that counts. The half below is that published shape, applied to exercise rates, not a quote.

Take 100,000 documents, 6,000 input tokens and 500 output tokens each, at exercise rates of $1.50 per million input tokens and $6.00 per million output tokens. The synchronous bill is $1,200. At half off, the batch bill is $600. The $600 buys a result that can land hours later. It does not buy a chat turn. A support agent looking at one ticket still needs the online API. The digest of the whole queue can wait. [Evaluate AI Systems](../04_Evaluate_AI_Systems/) prices a single call. This card is the discount you get for giving the provider a deadline instead of a latency SLO.

```python
DOCS = 100_000
INPUT_TOKENS, OUTPUT_TOKENS = 6_000, 500
INPUT_RATE, OUTPUT_RATE = 1.50, 6.00


def bill(scale: float) -> float:
    input_cost = DOCS * INPUT_TOKENS / 1_000_000 * INPUT_RATE * scale
    output_cost = DOCS * OUTPUT_TOKENS / 1_000_000 * OUTPUT_RATE * scale
    return input_cost + output_cost


print(f"{bill(1):.0f}")
print(f"{bill(0.5):.0f}")
# 1200
# 600
```

The provider can run that pile when the interactive fleet has room, on hardware that would otherwise sit idle between peaks. That is why the discount exists. Your own GPUs have the same shape if you run the job yourself: the batch window lets you fill a GPU with a large, throughput-oriented configuration, including a degree of parallelism that would be too slow for a single chat. The online tier keeps the configuration that protects the first token.

**Trade-offs.** The batch discount is real money on a large, delay-tolerant job, and it is useless for a person watching a cursor. A 24-hour window is a deadline, not a promise that every line finishes in minutes. Mixing the urgent ticket into the batch makes that ticket late. Running the whole digest on the online rate pays double, at these exercise prices, for a latency nobody needed. Prices and windows move, so a budget that hard-codes half off has to be recomputed when the page changes.

**Interview.** Split the traffic before you mention the discount. Interactive calls stay on the online API. Delay-tolerant calls go to the batch API and pick up about half off, which you re-read on the current page. Compute a bill both ways. Here, 100,000 documents at the exercise rates are $1,200 synchronous and $600 in batch. Say what you refuse to batch: anything whose caller is blocked on the answer.

**Recap.** Online APIs answer inside an interactive latency budget. Batch APIs, including OpenAI's Batch API and Anthropic's Message Batches, answer later and have been priced at about half the synchronous token rate. On the exercise rates, 100,000 documents of 6,000 input tokens and 500 output tokens cost $1,200 online and $600 in batch. The discount is payment for a loose deadline. A chat turn does not have that deadline. The current price page replaces the half when it changes.

## TTFT, TPOT, and inter-token latency

Time to first token, time per output token, and inter-token latency are three clocks on one generation.

Time to first token, TTFT, is the wait from the request until the first output token is available at the server. It includes queueing and prefill. Time per output token, TPOT, is the average gap between later tokens. Inter-token latency, ITL, is one of those gaps, and the tail of ITL is the stall a stream actually hit. [Evaluate AI Systems](../04_Evaluate_AI_Systems/) fixes the formula this topic uses: TTFT already includes the first token, so N output tokens take `TTFT + TPOT × (N − 1)`. A vendor that divides total generation time by N, first token included, is using a different TPOT. Reconcile the definitions before you compare dashboards. The token a user sees can be later still, after the network and the client buffer it. The objective has to name which clock it means.

A worked stream, not the 0.400 and 0.020 second example in that topic, makes the arithmetic local. TTFT of 1.20 seconds and TPOT of 0.040 seconds put an 80-token reply at 4.36 seconds. The decode rate on that stream is 25 tokens a second. The end-to-end rate is 18.35, because the 1.20 seconds produce the first token and then sit in the denominator. Three later gaps of 0.030, 0.035, and 0.090 seconds average to 0.052. A TPOT near 0.040 can hide the 0.090 stall. A voice reply and a streamed chat care about that stall. A batch job that only stores the finished string cares about the 4.36 seconds, and often not even that.

```python
TTFT = 1.20
TPOT = 0.040
OUTPUT_TOKENS = 80
GAPS = (0.030, 0.035, 0.090)
wait = TTFT + TPOT * (OUTPUT_TOKENS - 1)
print(f"{wait:.2f}")
print(f"{1 / TPOT:.1f} {OUTPUT_TOKENS / wait:.2f}")
print(f"{sum(GAPS) / len(GAPS):.3f} {max(GAPS):.3f}")
# 4.36
# 25.0 18.35
# 0.052 0.090
```

Sampling settings from the temperature card do not appear in this formula, and they still change the clocks. A longer reasoning trace, the test-time compute pattern, adds tokens and therefore adds `TPOT × (extra tokens)`. A stop that fires early shortens N. The formula is the wait once N and the two clocks are known. It is not a way to avoid measuring them.

**Trade-offs.** Optimizing the average TPOT can leave the tail ITL, and the user, untouched. Optimizing TTFT can leave a long answer slow after a snappy first word. Quoting the 25 token-per-second decode rate as if it were the user's wait ignores the 1.20 seconds. Quoting 4.36 seconds as if every consumer waited that long ignores a chat UI that streams. A server clock and the token on the screen are different measurements, and a launch that mixes them accepts a setup the user experiences as late.

**Interview.** Write `TTFT + TPOT × (N − 1)` and state that it is the same convention as Evaluate AI Systems. Compute the 80-token reply at 1.20 and 0.040 seconds: 4.36 seconds, a 25 token-per-second decode, and an 18.35 token-per-second end-to-end rate. Then explain ITL. The average of 0.030, 0.035, and 0.090 is 0.052, and the 0.090 is what a streaming UI hit. Ask which clock the product promised before you compare two serving stacks.

**Recap.** TTFT waits for the first server token, including queue and prefill. TPOT is the average gap after that, and ITL is a single gap, including the bad one. An 80-token reply at 1.20 seconds and 0.040 seconds takes 4.36 seconds, which is a 25 token-per-second decode and an 18.35 token-per-second end-to-end rate. Gaps of 0.030, 0.035, and 0.090 seconds average to 0.052 and still contain a 0.090 stall. The formula matches Evaluate AI Systems. A different vendor definition of TPOT has to be converted before the numbers are compared.

## Throughput and goodput

Throughput counts finished requests. Goodput counts the finished requests that met every latency objective you wrote down.

[Evaluate AI Systems](../04_Evaluate_AI_Systems/) uses that definition and calls the fraction of finished requests that met the objectives the attainment. Some dashboards use the word goodput for the fraction. DistServe, from Zhong and coauthors, uses goodput for a capacity: the highest request rate at which a stated percentile still meets the TTFT and TPOT caps. Same word, two readings. Name which dashboard you are looking at. Both readings agree on the failure that matters. A change that finishes more requests by missing the caps is not a win.

Over one minute, finishing 1,200 requests with 900 inside both caps is throughput 1,200 and goodput 900, attainment 0.75. Finishing 1,800 and keeping 720 inside the caps raises throughput and drops goodput to 720, attainment 0.40. The larger batch won a completion chart and lost the interaction. Errors and timeouts do not count as goodput in the first definition, because they did not meet the objective. DistServe's point is that a serving stack should be sized for the rate it can hold while the caps still hold, not for the rate it can hold with the caps removed. A chatbot, a code completion, and a summarizer do not share those caps, so they do not share a goodput.

```python
def report(finished: int, met: int) -> None:
    print(finished, met, f"{met / finished:.2f}")


report(1_200, 900)
report(1_800, 720)
# 1200 900 0.75
# 1800 720 0.40
```

The minute above is a worked window, not a DistServe table and not the one-second window in Evaluate AI Systems. The pattern is the same one that topic already computed with different counts. Throughput without the caps is how a colocated prefill looks good on a token counter while every in-flight decode misses its gap. The disaggregation card is that failure in hardware. This card is the metric that catches it.

**Trade-offs.** Reporting throughput is cheap and it rewards the configuration that breaks the product. Reporting goodput requires you to have written the caps down, and a vague cap makes the metric vague. A tight cap lowers the number and can force you to buy GPUs a looser product would not need. Attainment without the request rate hides whether you kept the caps by refusing traffic. The rate without attainment hides whether anyone got a timely answer.

**Interview.** Define throughput as finished requests and goodput as the finished requests that met every written latency cap. Give the minute: 1,200 finished and 900 inside is attainment 0.75, and 1,800 finished and 720 inside is attainment 0.40. Mention DistServe's variant, the maximum rate at which a percentile still meets TTFT and TPOT, and say you would name which definition the page uses. The 10-and-16 example in Evaluate AI Systems is the same idea on a one-second window. Do not mix the two windows.

**Recap.** Throughput counts every finished request. Goodput counts the ones that met every latency objective, and attainment is that count divided by throughput. In the worked minute, 900 of 1,200 is attainment 0.75, and 720 of 1,800 is attainment 0.40. The busier configuration finished more and satisfied fewer. DistServe uses goodput for the highest rate that still holds a TTFT and TPOT percentile. Say which definition you are quoting.

## Model FLOPs utilization

Model FLOPs utilization, MFU, is the fraction of a chip's peak arithmetic that the model's own FLOPs actually occupied.

The PaLM paper, Chowdhery and coauthors, defined it so training runs could be compared across chips. The numerator is the analytical FLOPs for the forward and backward passes, the model math, counted from the observed tokens per second. Rematerialization is left out. The denominator is the chip's published peak. Hardware FLOPs utilization, HFU, puts the rematerialization FLOPs back in the numerator, so the same run scores higher and the number depends on how much you chose to recompute. PaLM 540B, on 6,144 TPU v4 chips, is the paper's headline: 46.2 percent MFU with self-attention counted, 45.7 percent without it, and 57.8 percent HFU. They report an average training throughput of 238.3 thousand tokens a second. The same table puts GPT-3 175B at 21.3 percent MFU on V100, Gopher 280B at 32.5 percent on 4,096 TPU v3 chips, and Megatron-Turing NLG 530B at 30.2 percent on 2,240 A100s. Those are training numbers. The 40 percent figure in [Understanding Foundation Models](../02_Understanding_Foundation_Models/) is a planning utilization for a different sketch, not a measurement of any of these runs.

Decode on one GPU is a different regime, and the low MFU is the point rather than a failure. Use the untied Llama 3 8B count from the KV-cache card, 8,030,261,248 parameters, and the `2N` forward approximation, which ignores attention. A step that moves every BF16 weight once, at the H100 SXM5 datasheet bandwidth of 3.35 TB/s, produces 208.6 tokens a second. The FLOPs that step performs per second are exactly that bandwidth, because both the FLOP count and the byte count are `2N`. Divided by the 989.4 TFLOPS dense BF16 peak, MFU is 0.339 percent. The matmul is not broken. The step is waiting on HBM, which the roofline card already showed for a single token. Quoting 0.339 percent next to PaLM's 46.2 percent without saying "decode" and "training" is how a review panics.

```python
PARAMS = 8_030_261_248
BANDWIDTH = 3.35e12
PEAK = 989.4e12
TOKENS_PER_SEC = BANDWIDTH / (PARAMS * 2)
ACHIEVED = TOKENS_PER_SEC * (2 * PARAMS)
print(f"{TOKENS_PER_SEC:.1f}")
print(f"{ACHIEVED:.3e}")
print(f"{100 * ACHIEVED / PEAK:.3f}")
# 208.6
# 3.350e+12
# 0.339
```

Raising the batch raises intensity and can raise MFU, until the step crosses the ridge and the tensor cores are the ceiling. Quantizing weights raises the token rate of a bandwidth-bound decode and therefore raises this MFU, because you still do about `2N` FLOPs and you do them more often per second. The compression card puts the group-128 4-bit case at 1.31 percent. That is still a bandwidth-bound decode, not PaLM's training number. MFU is a useful alarm when a compute-bound prefill or a training step is far below the peak you paid for. It is a bad alarm for batch-1 decode.

**Trade-offs.** MFU lets you compare a training stack across GPU and TPU peaks, and it hides rematerialization that HFU would have counted. Optimizing decode for MFU pushes you toward huge batches and higher FLOP formats that can miss the latency caps. Ignoring MFU on a prefill cluster lets a compiler regression sit at a third of the FLOPs you provisioned. The metric is only as honest as the FLOP formula. Leaving attention out undercounts a long-context prefill. Putting the sparse tensor-core peak in the denominator understates utilization for a dense matmul.

**Interview.** Define MFU as model FLOPs per second divided by the chip's published peak, with rematerialization excluded. Cite PaLM 540B at 46.2 percent MFU on 6,144 TPU v4 chips, and say 57.8 percent is the HFU that includes rematerialization. Then compute the decode contrast: a bandwidth-saturated BF16 Llama 3 8B step on an H100 SXM5 uses 0.339 percent of the dense BF16 peak. The low number means the step is bandwidth-bound. It does not mean the kernel forgot how to multiply.

**Recap.** MFU divides the model's analytical FLOPs per second by the accelerator's peak. PaLM 540B reached 46.2 percent MFU on 6,144 TPU v4 chips, against 57.8 percent hardware FLOPs utilization once rematerialization is counted. A BF16 Llama 3 8B decode that saturates the H100 SXM5's 3.35 TB/s moves 208.6 tokens a second and uses 0.339 percent of the 989.4 TFLOPS dense peak. That decode figure is low because the chip is waiting on memory. PaLM's figure is a training run. They are not a before-and-after on the same job.

## Model bandwidth utilization

Model bandwidth utilization, MBU, is the fraction of an accelerator's peak memory bandwidth that the model actually used.

It is the bandwidth twin of MFU. Achieved bandwidth is the bytes the step had to move, multiplied by the steps per second. Peak bandwidth is the HBM figure on the datasheet of the SKU you are holding. For a BF16 decode whose traffic is the weights, MBU is the measured tokens per second divided by the tokens per second the bandwidth roof allows. On the Llama 3 8B shape and an H100 SXM5, that roof is 208.6 tokens a second if every weight byte moves and nothing else does. At that roof, MBU is 1. A measured  rate below the roof is an MBU below 1. The memory card derives the roof. This card is what a gap under the roof means.

```python
PARAMS = 8_030_261_248
WEIGHTS = PARAMS * 2
BANDWIDTH = 3.35e12
CEILING = BANDWIDTH / WEIGHTS
print(f"{CEILING:.1f}")
print(f"{CEILING * WEIGHTS / BANDWIDTH:.2f}")
# 208.6
# 1.00
```

A low MBU with a low MFU means the chip is waiting on something other than HBM. Typical causes are weights that never left host memory and are streaming over PCIe, a launch overhead larger than the kernel, a synchronous CPU step between tokens, or an access pattern that does not stream. A high MBU with a low MFU is the healthy batch-1 decode from the MFU card: the HBM pipe is full and the tensor cores are not the limit. A rising batch can hold MBU up while MFU climbs, until the roofline's ridge. Past the ridge, MBU falls because the arithmetic units finish before they have demanded the full pipe. That fall is not a memory bug.

The KV cache belongs in the byte count once the sequence is long. The memory card's second ceiling, 195.5 tokens a second at 8,192 tokens of cache, is the same MBU idea with a larger numerator of bytes per token. Using the weight-only 208.6 as the denominator when the cache is huge makes MBU look worse than the HBM pipe actually is. Write down which bytes you counted.

**Trade-offs.** MBU tells you whether a bandwidth-bound step is close to the HBM you paid for, and it says nothing about whether the latency SLO was met. Driving MBU to 1 with a giant batch can fill the pipe and miss every TTFT cap. Treating a low MFU as proof of a bad kernel, when MBU is already high, sends you into a fusion project that cannot add tokens. Treating a low MBU as "the model is too big" sends you into quantization when the weights were on the CPU. The metric is a placement of the bottleneck. It is not a leaderboard.

**Interview.** Define MBU as achieved bytes per second over the SKU's peak HBM bandwidth. For weight-only BF16 decode, that is measured tokens per second over the bandwidth roof, 208.6 on this 8B and H100 SXM5 pair, and the roof itself has MBU 1. Contrast it with MFU: high MBU and tiny MFU is a healthy decode, and low MBU is the case you debug. Name two causes you would check before you rewrite a kernel: weights resident in HBM, and the byte formula including the KV cache when the prompt is long.

**Recap.** MBU is the fraction of peak HBM bandwidth the model used. On a weight-only BF16 Llama 3 8B decode, the H100 SXM5 roof is 208.6 tokens a second, and that roof is MBU 1. A lower measured rate is unused bandwidth. High MBU with low MFU means the step is honestly bandwidth-bound. Low MBU means the bytes are not coming from HBM at the rate the datasheet allows, which is a residency, launch, or accounting problem before it is a math problem.

## What an accelerator is

An accelerator is a chip built to apply the same numeric operation to a large grid of values at once, which is what a neural-network layer does.

A CPU core is built to run a branchy program with a little data on the side. A GPU, such as NVIDIA's H100 or A100, puts thousands of lanes on one chip and adds tensor cores that run a small matrix multiply as a single instruction. A TPU, Google's accelerator, puts the matrix multiply in a systolic array: weights stay in place and activations stream past them. TPU v4's chip, in Google's documentation and in the Jouppi and coauthors system paper, holds two TensorCores, peaks at 275 TFLOPS of BF16 or INT8, and is the chip PaLM's 6,144-chip run trained on. You do not point CUDA or TensorRT-LLM at a TPU. The compiler on that side is XLA. The roofline still applies. Peak FLOPs over the TPU v4's 1,200 GB/s of HBM is 229 FLOPs per byte, the same kind of ridge the H100 card computes at 295.3.

```python
print(f"{275 / 1.2:.0f}")
# 229
```

The product consequence is which software and which number format you are allowed to assume. An A100 80GB SXM has BF16, FP16, TF32, and INT8 tensor cores, and it does not have FP8. An H100 SXM5 does have FP8 tensor cores. A TPU v4's peak is quoted for BF16 and INT8. A kernel written for one of those paths is not a kernel for the others. MIG, NVIDIA's multi-instance GPU, can slice one H100 into as many as seven 10 GB instances. That is useful for small models with small traffic. It also slices the HBM. A large model that needed the whole 80 GB does not become seven large models.

**Trade-offs.** A GPU is the flexible default and the one most serving stacks target. A TPU can be the better training machine inside Google's stack and a poor choice for a CUDA-only server. A CPU still runs the tokenizer, the scheduler, the web server, and small models, and it is the wrong place for a 70B decode if you had a choice. Slicing a GPU with MIG raises isolation and cuts the memory each slice can use. Assuming every accelerator has FP8, NVLink, or a CUDA graph is how a portable-looking config fails on the machine you actually rented.

**Interview.** Define an accelerator as a chip that spends its area on parallel numeric work rather than on branchy control. Contrast a GPU's tensor cores with a TPU's systolic array, and name the software: CUDA and TensorRT-LLM on one side, XLA on the other. Give one published peak with the chip attached, such as 275 TFLOPS for a TPU v4 or 989.4 TFLOPS dense BF16 for an H100 SXM5. Say the ridge is peak FLOPs over bandwidth on whichever chip you picked. The TPU v4's is 229 FLOPs per byte.

**Recap.** An accelerator is a parallel numeric chip. NVIDIA GPUs use tensor cores. Google TPUs use systolic arrays, and a TPU v4 chip peaks at 275 TFLOPS of BF16 or INT8 with a ridge of 229 FLOPs per byte. PaLM trained on TPU v4. vLLM and TensorRT-LLM target GPUs. FP8 is a Hopper feature, not an A100 feature. The roofline is the same picture on all of these chips. The datasheet you read has to be the chip you are holding.

## FLOPs and number formats

A published FLOP rate is the peak arithmetic of one number format on one SKU, and the datasheet's sparsity footnote is a different peak from the dense one.

[Finetuning](../07_Finetuning/) owns what BF16, FP16, FP8, and INT8 mean as formats: range, mantissa, and scales. [Understanding Foundation Models](../02_Understanding_Foundation_Models/) owns the dense-versus-sparse distinction for the H100 and uses 989.4 TFLOPS as the dense BF16 tensor-core peak. This card is the serving table those facts plug into. The H100 SXM datasheet row, the SXM5 module, lists BF16 and FP16 tensor-core performance at 1,979 TFLOPS with the sparsity footnote, FP8 and INT8 at 3,958 with the same footnote, 80 GB of HBM3 at 3.35 TB/s, and a TDP up to 700 W. The starred numbers assume 2:4 structured sparsity, two zeros in every four weights. A dense matmul gets half of the starred line. This guide uses 989.4 TFLOPS for dense BF16, the figure in Understanding Foundation Models, which is half of 1,979 within a tenth of a TFLOP. Half of the starred 3,958 FP8 and INT8 line is 1,979. The A100 80GB SXM datasheet lists 312 TFLOPS of dense BF16 tensor core, 624 with sparsity, 80 GB of HBM2e at 2,039 GB/s, and a 400 W standard TDP. It has no FP8 tensor core.

| SKU | Dense BF16 tensor core | 2:4 sparse line | Memory | Bandwidth | Power |
| --- | --- | --- | --- | --- | --- |
| H100 SXM5, datasheet row "H100 SXM" | 989.4 TFLOPS | 1,979 TFLOPS | 80 GB HBM3 | 3.35 TB/s | Up to 700 W, configurable |
| A100 80GB SXM | 312 TFLOPS | 624 TFLOPS | 80 GB HBM2e | 2,039 GB/s | 400 W standard |
| TPU v4 chip | 275 TFLOPS BF16 or INT8 | Not an NVIDIA sparse tensor core | 32 GiB HBM2 | 1,200 GB/s | Measured mean 170 W, max 192 W |

The H100's dense BF16 peak is 3.17 times the A100 80GB SXM's. Its bandwidth is 1.64 times, 3.35 TB/s against 2,039 GB/s. Compute peak grew faster than memory bandwidth, which is why the ridge rose from 153.0 to 295.3 FLOPs per byte on the roofline card. A decode that was already short of FLOPs to hide the bytes is shorter still. FP8 on Hopper cuts weight bytes and raises the tensor-core ceiling together. That is a different lever from weight-only INT4, which cuts bytes and still does the matmul in a wider type after a dequant. The A100 can do the INT8 and INT4 path. It cannot do the FP8 tensor-core path.

```python
print(f"{989.4 / 312:.2f}")
print(f"{3.35e12 / 2.039e12:.2f}")
# 3.17
# 1.64
```

The PCIe H100 is not this table. The architecture brief describes that module as 80 GB of HBM2e at over 2 TB/s, and the datasheet lists a configurable TDP of 300 to 350 W. Quoting 3.35 TB/s for a PCIe board overstates the pipe the decode will actually see.

**Trade-offs.** The sparse peak is a real datasheet line and a misleading denominator for a dense model. FP8 buys Hopper throughput and adds a scaling problem the finetuning format card already names. Staying on BF16 keeps the serving stack simpler and spends bandwidth you may not have. Comparing an H100 SXM5 with an A100 PCIe card, or a TPU v4 with a GPU, without naming the SKU, produces a fake speedup. The TPU's 275 TFLOPS is not a worse H100. It is a different chip with a different compiler and a different memory system.

**Interview.** Refuse a FLOP number that has no SKU, no dtype, and no dense-or-sparse flag. Give the H100 SXM5 as 989.4 TFLOPS dense BF16, 1,979 with 2:4 sparsity, 3.35 TB/s, up to 700 W. Give the A100 80GB SXM as 312 TFLOPS dense BF16, 2,039 GB/s, 400 W, and no FP8. Say the 3.17× compute gap against the 1.64× bandwidth gap is why the ridge moved. Put the sparse peak in the denominator only when the weights are actually 2:4 sparse and the kernel uses the sparse tensor cores.

**Recap.** FLOP peaks are per format and per SKU. The H100 SXM5 datasheet's starred BF16 line is 1,979 TFLOPS with 2:4 sparsity, and the dense peak is 989.4 TFLOPS. The same footnote puts FP8 and INT8 at 3,958, so the dense reading is half of that. The A100 80GB SXM is 312 TFLOPS dense BF16, 2,039 GB/s, 400 W, and has no FP8 tensor core. H100's dense BF16 peak is 3.17 times the A100's, and its bandwidth is 1.64 times, which is why decode stays bandwidth-bound. The PCIe H100 does not have the SXM5's 3.35 TB/s.

## Memory size and bandwidth

Memory size is how much state stays on the accelerator. Memory bandwidth is how many bytes per second can move between that memory and the compute units.

The hierarchy, from the math outward, is registers and shared memory on the streaming multiprocessor, then a cache, then HBM, then the host over PCIe, with NVLink beside that for GPU-to-GPU copies. NVIDIA's H100 architecture brief describes a 50 MB L2. That cache can hold a tile. It cannot hold a model. The Llama 3 8B BF16 weights on the KV-cache card are 14.96 GiB. They live in HBM, and a decode step reads them from HBM again because they do not fit in the L2. The H100 SXM5 datasheet lists that HBM as 80 GB at 3.35 TB/s. As [Understanding Foundation Models](../02_Understanding_Foundation_Models/) states for this label, an "80 GB" device reports 81920 MiB, so the capacity this topic uses is 80 GiB. The bandwidth figure stays in the datasheet's decimal terabytes per second.

The weight-only decode roof is that bandwidth divided by the weight bytes. At 3.35 TB/s and 14.96 GiB of BF16 weights, the roof is 208.6 tokens a second, one token every 4.79 ms, and only if the kernel moves nothing else and hits the full pipe. An 8,192-token KV cache on this shape is exactly 1 GiB. Adding that read drops the roof to 195.5 tokens a second. A real kernel also writes activations and does not hit MBU 1, so a measured rate is lower. This ceiling is an upper bound you use to see whether a goal is possible. It is not a benchmark of vLLM.

```python
PARAMS = 8_030_261_248
WEIGHTS = PARAMS * 2
BANDWIDTH = 3.35e12
PER_TOKEN = 2 * 32 * 8 * 128 * 2
print(f"{WEIGHTS / 1024**3:.2f}")
print(f"{BANDWIDTH / WEIGHTS:.1f}")
print(f"{BANDWIDTH / (WEIGHTS + PER_TOKEN * 8192):.1f}")
print(f"{WEIGHTS / BANDWIDTH * 1e3:.2f}")
print(f"{128e9 / WEIGHTS:.1f}")
# 14.96
# 208.6
# 195.5
# 4.79
# 8.0
```

The datasheet lists PCIe Gen5 at 128 GB/s next to NVLink at 900 GB/s on this SXM module. Streaming the same weights from the host on every token, at that 128 GB/s figure, is a roof of 8.0 tokens a second. That is the offload case. NVLink is the path a tensor-parallel collective uses, and the parallelism card counts how small that payload is. Neither number is HBM. A capacity plan that adds "80 GB" and forgets 3.35 TB/s will buy a card the weights fit on and then miss the token rate. A plan that quotes 208.6 and forgets the cache will miss it once the prompts get long.

**Trade-offs.** More HBM fits a longer cache and a larger batch, and it costs money and power even when the batch is empty. More bandwidth raises the decode roof and does not, by itself, speed a compute-bound prefill. Offloading weights to host memory fits a model the HBM cannot hold and replaces the HBM roof with the PCIe roof. Quantizing weights raises the HBM roof by shrinking the denominator, which is the compression card, and it does not raise the roof if the kernel dequantizes by first materializing a full BF16 copy in a way that moves the wide bytes anyway. You read the kernel, not only the checkpoint dtype.

**Interview.** Separate capacity from bandwidth and name the SKU. H100 SXM5: 80 GB of HBM3, which this guide treats as 80 GiB, at 3.35 TB/s. Then compute the Llama 3 8B BF16 roof, 208.6 tokens a second, and the 195.5 once an 8,192-token cache is in the byte count. Mention the PCIe line on the same datasheet, 128 GB/s, as the roof you fall to if the weights are not resident. Say the 50 MB L2 is why the weights are reread from HBM on every token.

**Recap.** HBM capacity holds the weights and the KV cache. HBM bandwidth sets the decode roof. On an H100 SXM5, 3.35 TB/s over the Llama 3 8B's 14.96 GiB of BF16 weights is 208.6 tokens a second, or 4.79 ms a token, and 195.5 tokens a second once an 8,192-token cache is also read. The on-chip cache is tens of megabytes, so it does not keep the model. The datasheet's PCIe Gen5 figure of 128 GB/s is the pipe you get if the weights stay on the host. A measured rate above these roofs is an accounting error. A measured rate far below them is the MBU card.

## Power

Power is the watts an accelerator is allowed to draw, and it is the constraint that turns a FLOP peak into a facilities problem.

TDP is a cap, not a measured average, which is the same reading [Understanding Foundation Models](../02_Understanding_Foundation_Models/) uses for the H100's 700 W. The H100 SXM datasheet lists a maximum TDP up to 700 W, configurable. The A100 80GB SXM datasheet lists 400 W for the standard configuration, and a custom thermal SKU up to 500 W that this card does not use. At those nameplate caps, dense BF16 tensor-core peak per watt is 1.41 TFLOPS on the H100 SXM5 and 0.78 TFLOPS on the A100 80GB SXM, a ratio of 1.81. HBM bandwidth per watt runs the other way: 4.79 GB/s per watt against 5.10. Absolute bandwidth still favors the H100, 1.64 times the A100's, and the nameplate watts rose 1.75 times. A decode fleet, which is bandwidth-bound, buys bytes per second first and bytes per watt second. A prefill fleet, which is compute-bound, buys the 1.81× arithmetic per nameplate watt more directly.

```python
print(f"{989.4 / 700:.2f} {312 / 400:.2f}")
print(f"{(989.4 / 700) / (312 / 400):.2f}")
print(f"{3.35e12 / 700 / 1e9:.2f} {2.039e12 / 400 / 1e9:.2f}")
print(f"{3.35 / 2.039:.2f} {700 / 400:.2f}")
# 1.41 0.78
# 1.81
# 4.79 5.10
# 1.64 1.75
```

Google's TPU v4 documentation lists measured power of 90 W minimum, 170 W mean, and 192 W maximum for the chip, and the system paper marks TDP as not applicable. Do not divide 275 TFLOPS by 170 W and call it a TDP efficiency. Peak FLOPs over a measured mean is a different ratio from peak FLOPs over a nameplate cap, and the two should not be ranked against the H100's 1.41. The facilities number in Understanding Foundation Models stays the training example: up to 16,384 H100 GPUs at a 700 W TDP is 11.5 megawatts of accelerator nameplate before CPUs, network, and cooling. An inference fleet is the same kind of sum on however many GPUs you leave powered overnight. Idle watts are why a spiky product often prefers an API, which is the self-hosting card in Evaluate AI Systems. This card is the per-GPU cap inside that choice.

**Trade-offs.** Provisioning the nameplate keeps the SLO when the chip boosts, and it overstates the average bill if the decode rarely hits 700 W. Provisioning the average trips the breaker at the peak or throttles the clock, which moves both FLOPs and bandwidth. A chip with better FLOPs per watt can be the wrong buy for a bandwidth-bound decode if its HBM per watt is worse and the absolute bandwidth does not clear the token roof. Cooling and the network are outside the TDP and outside the 11.5 megawatt figure. Leaving them out understates the room.

**Interview.** Call TDP a cap. Give the H100 SXM5 as up to 700 W and the A100 80GB SXM standard configuration as 400 W. Compute dense BF16 per watt, 1.41 against 0.78, and HBM per watt, 4.79 GB/s against 5.10. Say which one a decode buys. Point at the 11.5 megawatt Llama 3 training nameplate as the cluster form of the same cap, and say it excludes cooling. Refuse a TPU comparison that divides peak FLOPs by the 170 W measured mean and ranks it against a TDP ratio.

**Recap.** Power is the cap under the peaks. The H100 SXM5 is up to 700 W. The standard A100 80GB SXM is 400 W. Dense BF16 peak per nameplate watt is 1.41 TFLOPS against 0.78, a ratio of 1.81. HBM bandwidth per watt is 4.79 GB/s against 5.10, because bandwidth grew 1.64 times while nameplate watts grew 1.75 times. Decode buys bandwidth. Prefill buys the arithmetic per watt. TDP is not an average draw, and a TPU v4's measured 170 W mean is not a TDP you can rank against these ratios. The 11.5 megawatt figure in Understanding Foundation Models is this cap times a training cluster, before cooling.

## Quantization, pruning, and distillation

Model compression rewrites a checkpoint so serving moves fewer bytes or does less arithmetic. The three rewrites you will actually choose among are quantization, pruning, and distillation.

[Finetuning](../07_Finetuning/) owns the accuracy side of quantization: post-training weight-only methods such as GPTQ and AWQ, activation quantization such as LLM.int8() and SmoothQuant, the group of 128, and the warning that INT4 moves arithmetic and exact tokens first. This card owns the serving math, and it keeps that topic's rule that a BF16 weight is 2 bytes. A raw 4-bit packing is 0.5 bytes. GPTQ and AWQ store a scale per group. At a group of 128 and one FP16 scale, the scale adds `2 / 128` bytes, so a parameter costs 0.515625 bytes. A zero-point adds another 2 bytes per group and moves the cost to 0.53125 bytes. On the Llama 3 8B count, the scale-only packing is 3.86 GiB of weights against 14.96 GiB in BF16. If decode stays bandwidth-bound and the kernel truly moves the packed bytes, the H100 SXM5 roof rises from 208.6 tokens a second to 809.1, a factor of 3.88. The zero-point packing is a factor of 3.76 instead. The same step's MFU rises from 0.339 percent to 1.31 percent, because the `2N` FLOPs happen more often per second. That is still a bandwidth-bound decode. Prefill, which is compute-bound, may not speed up, and a dequant kernel can spend the arithmetic the smaller checkpoint saved. The A100 80GB SXM can run INT8 and INT4. FP8 tensor cores are the Hopper row on the FLOPs card, not a reason to expect FP8 on that A100.

```python
PARAMS = 8_030_261_248
BANDWIDTH = 3.35e12
PEAK = 989.4e12
SCALE = 0.5 + 2 / 128
ZERO = 0.5 + 4 / 128
bf16_tokens = BANDWIDTH / (PARAMS * 2)
int4_tokens = BANDWIDTH / (PARAMS * SCALE)
print(f"{SCALE:.6f} {ZERO:.5f}")
print(f"{PARAMS * SCALE / 1024**3:.2f}")
print(f"{bf16_tokens:.1f} {int4_tokens:.1f} {int4_tokens / bf16_tokens:.2f}")
print(f"{2 / SCALE:.2f} {2 / ZERO:.2f}")
print(f"{100 * bf16_tokens * (2 * PARAMS) / PEAK:.3f}")
print(f"{100 * int4_tokens * (2 * PARAMS) / PEAK:.2f}")
# 0.515625 0.53125
# 3.86
# 208.6 809.1 3.88
# 3.88 3.76
# 0.339
# 1.31
```

Pruning deletes weights. Unstructured pruning, as in SparseGPT from Frantar and Alistarh and Wanda from Sun and coauthors, can zero many values and still leave a kernel that loads the dense tensor and skips the zeros only in the ALU. You then pay the BF16 traffic anyway. NVIDIA's 2:4 structured sparsity is the pattern the starred tensor-core peaks assume, two zeros in every four weights, and it doubles the datasheet peak only when the kernel uses that path. A 50 percent sparse checkpoint that is not in that pattern does not get the 1,979 TFLOPS line.

Distillation trains a smaller student. [Dataset Engineering](../08_Dataset_Engineering/) owns the method: Hinton's soft targets, sequence-level text when the teacher is an API, DistilBERT's published summary, and the license limit on training from a provider's outputs. The serving consequence is a smaller N. Weight bytes fall with N, so the bandwidth-bound token roof rises in proportion, and the KV cache falls only if the student also has fewer layers or fewer key-value heads. A student that keeps the teacher's attention shape and only shrinks the feed-forward still moves almost the same cache. You remeasure the task. A cheaper model that misses the slice is the finetuning topic's reason not to ship a checkpoint, applied to a student.

**Trade-offs.** INT4's 3.88× byte reduction is the decode win and the accuracy risk Finetuning already names. Finer groups and a skipped output projection give some of the accuracy back and spend some of the bytes. Pruning looks like a free FLOP peak until you check whether HBM still carries the zeros. Distillation can clear a latency SLO a quantized large model still misses, and it caps quality at the questions you asked the teacher, under that teacher's license. Stacking all three makes a failure undebuggable. Change one, then score the slice that previously failed.

**Interview.** Keep 2 bytes per BF16 parameter. Show the group-128 FP16 scale turning 0.5 bytes into 0.515625, and the H100 SXM5 roof moving from 208.6 to 809.1 tokens a second, MFU from 0.339 percent to 1.31 percent. Say prefill may not move. Separate unstructured pruning from 2:4 sparsity, and say the starred FLOP peak requires the structured pattern and a kernel that uses it. Point distillation's training and license at Dataset Engineering, and say the serving win is fewer weight bytes, with the cache unchanged unless the attention shape shrank.

**Recap.** Compression cuts bytes or arithmetic. Weight-only 4-bit with a group-128 FP16 scale is 0.515625 bytes per parameter, 3.86 GiB for Llama 3 8B, and an H100 SXM5 decode roof of 809.1 tokens a second against 208.6 in BF16, which is 3.88×. MFU moves from 0.339 percent to 1.31 percent and the step is still bandwidth-bound. A zero-point makes the factor 3.76×. Unstructured pruning does not earn the 2:4 sparse tensor-core peak. Distillation's serving effect is a smaller model, and the way that student is trained is the distillation card in Dataset Engineering.

## Speculative decoding

Speculative decoding drafts several future tokens with a cheap model and then checks them with the model you serve, so one expensive step can accept more than one token.

The reason it exists is the decode roof. A target as large as Llama 3 70B is bandwidth-bound at batch 1, and each token rereads the weights. A smaller draft model proposes γ tokens. The target then scores those positions together, which is a short prefill rather than γ sequential decode steps, and keeps the longest prefix that agrees with its own distribution. Leviathan, Kalman, and Matias, in 2023, and Chen and coauthors, in 2023, both give a rejection rule that leaves the target distribution unchanged. On a rejection you draw from the residual between the target and the draft, not from the draft. Greedy decoding is the special case where you keep a draft token only when it is the target's argmax, which preserves the greedy string. Naively keeping the draft whenever it "looks close" does not.

If each draft token is accepted independently with probability α, the expected number of tokens per target step is `(1 − α^(γ+1)) / (1 − α)`. That count includes the bonus token the target can emit when every draft token is accepted, and it includes the one token you still emit when the first draft token is rejected. Leviathan and coauthors define c as the time for one draft step divided by the time for one target step, and they assume the target scores the drafted positions in about one target step. The expected speedup is then `(1 − α^(γ+1)) / ((1 − α)(γc + 1))`. In their experiments c stayed under 0.05. The values below are a worked acceptance rate of 0.7, a draft of 4 tokens, and a cost coefficient of 0.05 at that reported bound. They are not a cell from the paper's speedup table.

```python
def speedup(alpha: float, gamma: int, cost: float) -> tuple[float, float]:
    expected = (1 - alpha ** (gamma + 1)) / (1 - alpha)
    return expected, expected / (gamma * cost + 1)


free = speedup(0.7, 4, 0.0)
paid = speedup(0.7, 4, 0.05)
print(f"{free[0]:.2f} {free[1]:.2f}")
print(f"{paid[0]:.2f} {paid[1]:.2f}")
# 2.77 2.77
# 2.77 2.31
```

The worked case accepts 2.77 tokens per target step. If the draft were free, that would be a 2.77× wall-time speedup under the paper's assumptions. At c = 0.05 the speedup is 2.31×. A draft that is large, slow, or a poor match makes the denominator grow faster than the numerator, and speculative decoding becomes slower than ordinary decode. The draft and the target also have to share a tokenizer, or you need an explicit map between their ids. A draft that proposes tokens the target cannot line up is not a plug-in. vLLM and TensorRT-LLM both implement this path. The acceptance rate is a property of the pair and of the task. Code that repeats a local pattern accepts more than open-ended chat. You measure α on your traffic. You do not borrow it from a worked example.

**Trade-offs.** A well-matched draft multiplies decode tokens per target step and preserves the distribution when the rejection rule is the real one. A poorly matched draft spends the target step rejecting, and you would have been faster without it. Longer γ helps only while the extra draft tokens still get accepted often enough to pay for c. Greedy verification is simpler and is the wrong rule for a sampled chat if you promised the temperature setting from the sampling cards. Speculative decoding does not shrink the prefill of a long prompt. The prompt is still a prefill.

**Interview.** Explain the draft, the parallel verify, and the residual sample that keeps the target distribution. Write the expected-token formula and evaluate it at a labeled α. Here, α = 0.7 and γ = 4 give 2.77 tokens, and c = 0.05 cuts the speedup from 2.77× to 2.31×. Say c stayed under 0.05 in the Leviathan experiments and that this 0.05 is a worked coefficient at that bound, not their table. Name the failure: a slow or inaccurate draft, or a tokenizer mismatch, makes the feature a slowdown. Point at Chen and coauthors as the other 2023 paper with a distribution-preserving rule.

**Recap.** Speculative decoding lets a small draft propose tokens that the target verifies in one step. Leviathan and coauthors and Chen and coauthors give rejection rules that preserve the target distribution. With an independent acceptance rate α, one target step yields `(1 − α^(γ+1)) / (1 − α)` tokens. At a worked α of 0.7 and γ of 4, that is 2.77 tokens. With their cost model at a worked c of 0.05, the speedup is 2.31× rather than 2.77×. A draft that is too slow or too wrong makes decoding slower. The tokenizer has to match.

## Medusa, lookahead, and prompt lookup

Medusa, lookahead decoding, and prompt lookup propose several future tokens without a second full language model.

They exist because a draft model is an extra checkpoint to load, version, and keep on the same tokenizer. Medusa, from Cai and coauthors in 2024, adds small heads on the target's last hidden state. Each head predicts a further token. A tree of those predictions is checked in one verification pass, which is why the extra heads can share the target's weights instead of rereading a second model. The acceptance rule decides whether the samples still match ordinary decoding. Speculative sampling's residual draw is built to leave the distribution unchanged. A Medusa setup that accepts a token when it looks typical can take a higher acceptance rate and a small shift in the distribution. Read the rule before you promise bitwise or distributional identity with the baseline.

Lookahead decoding, from Fu and coauthors in 2024, does not add heads. It keeps n-grams from the model's own Jacobi-style trajectory, proposes several of them, and verifies the candidates with the target. For a greedy decode, a candidate that survives verification is the greedy token, so the string does not drift. Prompt lookup does not train anything. It searches the prompt, and sometimes the text generated so far, for a span that ends with the current tokens, and it proposes the tokens that followed that span last time. The target verifies them the way it would verify any other draft. Hugging Face Transformers and vLLM both ship a prompt-lookup or n-gram path. It pays off when the answer quotes the source: a RAG snippet, a code edit that repeats the buffer, a template with a long fixed middle. On an open-ended chat there is often nothing to copy, the proposals miss, and you paid a verification step for one ordinary token.

| Method | Where the proposal comes from | What you add at serve time | Distribution |
| --- | --- | --- | --- |
| Speculative decoding | A smaller model with the same tokenizer | The draft weights, and one verification step | Preserved when the residual rejection rule is used |
| Medusa | Extra heads on the target | Those heads, and a tree verification | Depends on the acceptance rule |
| Lookahead decoding | n-grams from the same model's trajectory | A small n-gram pool, no second model | Greedy verification keeps the greedy string |
| Prompt lookup | A matching span in the prompt or the output so far | A string search, no extra weights | The target still verifies the proposal |

The speculative-decoding card's formula still describes the verify step. What changes is c and α. Prompt lookup has a tiny c, because the proposal is a memory lookup, and a terrible α when the prompt contains no repeated span. Medusa's c is the cost of the extra heads, which is small next to a 70B target and is not zero. None of these remove the prefill, and none of them shrink the KV cache.

**Trade-offs.** Dropping the draft model removes a second checkpoint and removes a source of tokenizer bugs. You then depend on heads you have to train, on n-grams the trajectory has actually produced, or on literal overlap with the prompt. Medusa's looser acceptance can be faster and can change answers you already evaluated. Lookahead and prompt lookup are only as good as their proposals. A RAG product that quotes sources is the favorable case for prompt lookup. A brainstorm is the unfavorable one. Running two of these at once makes the trace of which token came from where hard to debug.

**Interview.** Name the four proposal sources: a draft model, extra heads, a Jacobi n-gram pool, and a span copied from the prompt. Say which ones preserve the baseline. Residual rejection sampling does. Greedy verification keeps the greedy string. A typical-acceptance rule needs a measurement. Give the product fit. Prompt lookup for a quoting RAG bot, speculative decoding when you have a matched small model, Medusa when you can train heads and you have checked the acceptance rule. Say that a miss still costs a verification step.

**Recap.** Medusa, lookahead decoding, and prompt lookup draft tokens without a second full model. Medusa uses extra heads and a tree of candidates. Lookahead uses n-grams from the same model. Prompt lookup copies a span from the prompt and is useful when the answer repeats the source. The target still verifies. Residual rejection sampling preserves the distribution. A looser acceptance rule can move it. A proposal that always misses makes the decode slower, just as a bad draft model does.

## KV cache size

The KV cache is the stored keys and values for the tokens a request has already processed, and its size is fixed once you name the attention shape, the dtype, and the length.

The attention card in [Understanding Foundation Models](../02_Understanding_Foundation_Models/) derives the formula. Two tensors, times layers, times key-value heads, times head dimension, times bytes per number, times tokens. Tokens means the prompt plus the tokens generated so far. The inference-memory card in [Finetuning](../07_Finetuning/) applies it to Llama 2 7B, which has 32 key-value heads, and gets 512 KiB a token. This card applies it to the released Llama 3 8B shape, which the 70B cards do not: 32 layers, hidden size 4,096, intermediate size 14,336, 32 query heads, 8 key-value heads, head dimension 128, vocabulary 128,256, and untied input and output embeddings. That count is 8,030,261,248 parameters, 14.96 GiB in BF16 at 2 bytes per parameter.

Each new token adds `2 × 32 × 8 × 128 × 2 = 131,072` bytes, which is 128 KiB. The quarter of Llama 2 7B's 512 KiB is the quarter as many key-value heads. An 8,192-token sequence, Llama 3's original context, is exactly 1 GiB of cache. A 131,072-token sequence, the 128k context in the sense of 128 × 1024 that Understanding Foundation Models uses for Llama 3.1, is exactly 16 GiB. One such request plus the BF16 weights is 30.96 GiB, which fits an 80 GiB H100 SXM5 before activations. Four concurrent 131,072-token requests are 78.96 GiB of weights plus cache, with almost no room for activations or fragmentation. Five are 94.96 GiB and do not fit. The weights are paid once. The cache is paid per live request. Llama 3.1 keeps this 8B attention shape and extends the length you are allowed to allocate. The per-token price does not change when the maximum context does.

```python
def llama3_8b_params() -> int:
    layers, hidden, intermediate, vocab = 32, 4096, 14336, 128_256
    kv_width = 8 * 128
    per_layer = (
        hidden * hidden
        + hidden * kv_width
        + hidden * kv_width
        + hidden * hidden
        + 3 * hidden * intermediate
        + 2 * hidden
    )
    return layers * per_layer + hidden + 2 * vocab * hidden


PARAMS = llama3_8b_params()
PER_TOKEN = 2 * 32 * 8 * 128 * 2
print(PARAMS)
print(PER_TOKEN, PER_TOKEN // 1024)
print(8192, PER_TOKEN * 8192 // 1024**3)
print(131_072, PER_TOKEN * 131_072 // 1024**3)
weights = PARAMS * 2 / 1024**3
print(f"{weights:.2f}")
print(f"{weights + 16:.2f}")
print(f"{weights + 4 * 16:.2f}")
print(f"{weights + 5 * 16:.2f}")
# 8030261248
# 131072 128
# 8192 1
# 131072 16
# 14.96
# 30.96
# 78.96
# 94.96
```

The 70B shape in Understanding Foundation Models is the other worked point: 320 KiB a token, 1.25 GiB at 4,096 tokens, and 40 GiB at 131,072 tokens, with BF16 weights of 131.4 GiB that do not fit one 80 GiB GPU. Quantizing the cache halves these bytes again if you store it in 1 byte, and it adds a numerical error you measure. Grouped-query attention is why the 8B's 16 GiB figure is the one to plan with. Full multi-head attention at 32 key-value heads would be 64 GiB at the same long context, which is the next card.

**Trade-offs.** A longer context lets a user paste the thread, and it raises cache memory linearly. Concurrency multiplies the cache and does not multiply the weights. Quantizing the cache saves bytes and can move the token the model would have produced. Paging, on the FlashAttention card, removes the waste of reserving the maximum length. It does not make a live 16 GiB cache smaller. Forgetting the cache and planning from the 14.96 GiB of weights is how a single demo fits and four long sessions do not.

**Interview.** Write the formula and pick the model whose config you can defend. For Llama 3 8B in BF16, 128 KiB a token, 1 GiB at 8,192, 16 GiB at 131,072, weights 14.96 GiB, one long request 30.96 GiB, four of them 78.96 GiB, five of them 94.96 GiB. Mention Llama 2 7B's 512 KiB only to show the key-value head ratio, and point the 70B's 40 GiB at Understanding Foundation Models rather than rederiving it. Say activations sit on top, so 78.96 GiB is not a comfortable fit on an 80 GiB GPU.

**Recap.** KV-cache bytes are two tensors times layers times key-value heads times head dimension times bytes times tokens. The untied Llama 3 8B shape is 8,030,261,248 parameters and 14.96 GiB in BF16. Its cache is 128 KiB a token, 1 GiB at 8,192 tokens, and 16 GiB at 131,072 tokens. One 128k request is 30.96 GiB with the weights. Four are 78.96 GiB before activations. Five are 94.96 GiB and miss an 80 GiB GPU. The 70B cache figures stay in Understanding Foundation Models. The weights are paid once, and the cache is paid per live request.

## Multi-query, grouped-query, and sliding-window attention

Multi-query, grouped-query, and sliding-window attention shrink the keys and values a new token has to read.

Multi-head attention gives every query head its own key and value. Multi-query attention, from Shazeer in 2019, keeps a single key-value head for all of the query heads. Grouped-query attention, from Ainslie and coauthors in 2023, is the middle: several query heads share one key-value head. PaLM used multi-query attention. Llama 2 uses grouped-query attention at 70B and ordinary multi-head attention at 7B and 13B. Llama 3 uses 8 key-value heads at the 8B, 70B, and 405B sizes. The attention card in [Understanding Foundation Models](../02_Understanding_Foundation_Models/) records the 70B consequence: 8 key-value heads rather than 64 makes the 40 GiB cache at 131,072 tokens discussable, where the full key-value head count would be 320 GiB. The 8B shape is the factor of four you can see next to the KV-cache card. Thirty-two key-value heads would be 512 KiB a token. Eight are 128 KiB. At 131,072 tokens that is 64 GiB against 16 GiB.

```python
FULL = 2 * 32 * 32 * 128 * 2
GROUPED = 2 * 32 * 8 * 128 * 2
print(FULL // 1024, GROUPED // 1024, FULL // GROUPED)
print(f"{131_072 * FULL / 1024**3:.0f}")
print(f"{131_072 * GROUPED / 1024**3:.0f}")
# 512 128 4
# 64
# 16
```

A sliding window changes which of those keys are live. Mistral 7B uses a window of 4,096 tokens and the same 32 layers, 8 key-value heads, and head dimension of 128, so the same 128 KiB a token if you stored the whole sequence. A rolling cache that stores only the window is 0.5 GiB. At a sequence length of 8,192 the full cache would be 1 GiB, and the rolling cache is half of that. Understanding Foundation Models reports that comparison as about half. At 32,768 tokens the full cache would be 4 GiB and the rolling cache is still 0.5 GiB. The score computation at each layer looks at the window. Information can still move further, because each layer can carry a summary forward by one window, so 32 layers have a longer reach than 4,096 tokens. A token outside the window is not a key you can quote from that layer directly.

```python
PER_TOKEN = 128 * 1024
print(f"{4096 * PER_TOKEN / 1024**3:.1f}")
print(f"{8192 * PER_TOKEN / 1024**3:.1f}")
print(f"{32768 * PER_TOKEN / 1024**3:.1f}")
# 0.5
# 1.0
# 4.0
```

**Trade-offs.** Fewer key-value heads cut cache bytes and cut the distinct key-value patterns the model can keep. Multi-query is the smallest cache and the largest quality question. Grouped-query is the compromise Llama 3 ships. A sliding window bounds the cache and drops a direct lookup of an older token, which is the failure mode of pasting a long contract and asking for a clause that fell out of the window. Keeping full attention quotes the clause and pays the 16 GiB, or the 40 GiB on the 70B shape. Quantizing an already grouped cache is a further cut, with a further measurement.

**Interview.** Tie the byte formula to the key-value head count. Llama 3 8B at 8 heads is 128 KiB a token, and 32 heads would be 512 KiB, four times more, 64 GiB against 16 GiB at 131,072 tokens. Point at the 70B's 8-versus-64 comparison in Understanding Foundation Models instead of recomputing 40 GiB. Define the sliding window with Mistral's 4,096, and say a rolling cache at sequence length 8,192 is half the full cache, 0.5 GiB against 1 GiB. Mention that earlier tokens can still influence the output through the stack of windows.

**Recap.** Multi-query attention uses one key-value head. Grouped-query attention shares one key-value head across a group of query heads. On Llama 3 8B, 8 heads instead of 32 cut the cache from 512 KiB a token to 128 KiB, and from 64 GiB to 16 GiB at 131,072 tokens. Mistral 7B's window of 4,096 keeps a rolling cache at 0.5 GiB, which is half of the full 8,192-token cache and an eighth of a full 32,768-token cache. The 70B version of the same head-count argument stays in Understanding Foundation Models. You give up key-value diversity, or a direct lookup of older tokens, in exchange for those bytes.

## PagedAttention and FlashAttention

PagedAttention and FlashAttention fix two different memory problems in attention. Paging stops wasted KV-cache reservations. FlashAttention stops the score matrix from being written out to HBM.

FlashAttention, from Dao and coauthors in 2022, with FlashAttention-2 in 2023 and FlashAttention-3 aimed at Hopper, computes the weighted sum in tiles that stay in on-chip memory. The attention card in [Understanding Foundation Models](../02_Understanding_Foundation_Models/) already says the important limit: it speeds the math, up to small numerical differences, and it does not delete the cache you keep for decode. The byte reason is the score matrix. For one head at 8,192 tokens, stored in BF16, the scores are `8192 × 8192 × 2` bytes, which is 128 MiB. The Q, K, and V for that head are 6 MiB, so the scores are 21.3 times the vectors they came from. Thirty-two heads in one layer would be 4 GiB of score matrices if you materialized them together. A naive kernel writes the scores, rereads them for the softmax, and rereads them for the values. FlashAttention keeps a tile, updates the softmax statistics, and never stores that matrix. The 1 GiB KV cache for the whole Llama 3 8B model at this length is still allocated. FlashAttention changed the prefill's traffic. It did not change the decode's resident state.

```python
SEQ = 8192
HEAD = 128
scores = SEQ * SEQ * 2
qkv = 3 * SEQ * HEAD * 2
print(scores // 1024**2, qkv // 1024**2)
print(f"{scores / qkv:.1f}")
print(32 * scores // 1024**3)
# 128 6
# 21.3
# 4
```

PagedAttention, from Kwon and coauthors in 2023, is the allocator behind vLLM. A server that reserves each request's maximum context up front fragments HBM the way an operating system would if it gave every process its peak heap. On the Llama 3 8B shape, ten requests reserved at 8,192 tokens and actually using 1,024 hold 10.00 GiB of reservations and 1.25 GiB of real tokens. The other 8.75 GiB cannot be given to an eleventh request even though it is empty. Paging the cache in blocks, a block of 16 tokens is a common page size, makes those empty regions reusable. The live tokens still cost 128 KiB each. Paging recovers fragmentation. It is not quantization, and it is not a smaller attention head count.

```python
PER_TOKEN = 131_072
print(f"{10 * 8192 * PER_TOKEN / 1024**3:.2f}")
print(f"{10 * 1024 * PER_TOKEN / 1024**3:.2f}")
# 10.00
# 1.25
```

The two techniques stack. FlashAttention is the kernel you want during prefill. PagedAttention is the allocator you want while many decodes of different lengths share a GPU. Neither one raises the HBM datasheet bandwidth. A step that is already at the weight-moving roof stays there.

**Trade-offs.** FlashAttention speeds the prefill and still leaves you holding the cache, so a memory plan that deletes the 16 GiB because "we enabled FlashAttention" is wrong. Paging raises concurrency and adds a block table and some internal fragmentation of the last partial block. A page size of one token is a lot of bookkeeping. A huge page brings back the waste paging was meant to remove. Numerical differences in FlashAttention are small and are still a reason to remeasure a strict exact-match slice after you change kernels. Serving without paging wastes HBM on reserved tails. Serving without a tiled attention kernel writes score matrices you do not need.

**Interview.** Separate the two papers. FlashAttention tiles the score computation so the `S × S` matrix is not written to HBM. At 8,192 tokens one BF16 head is 128 MiB of scores against 6 MiB of QKV, 21.3 times, and 32 heads are 4 GiB. The KV cache remains. PagedAttention is vLLM's block allocator. Ten requests reserved at 8,192 and used at 1,024 are 10.00 GiB reserved and 1.25 GiB live. Say what each one does not do, because that is the usual mix-up.

**Recap.** FlashAttention computes attention in on-chip tiles and does not write the score matrix to HBM. One head at 8,192 tokens would otherwise write 128 MiB of BF16 scores against 6 MiB of Q, K, and V. The KV cache stays. PagedAttention stores that cache in reusable blocks so a request does not reserve its maximum length up front. Ten Llama 3 8B requests reserved at 8,192 tokens and using 1,024 cost 10.00 GiB of reservations and 1.25 GiB of real cache. Paging recovers the waste. It does not shrink a token that is actually live.

## Kernels and compilers

A kernel is the program that runs one operation on the accelerator. A compiler chooses kernels and fuses them so intermediate values stay on chip instead of taking a trip to HBM.

The reason fusion matters is the hierarchy on the memory card. Every separate kernel that writes an activation pays HBM bandwidth and a launch. A Llama-style feed-forward applies two projections and then a SiLU gate. Unfused, each projection reads the 4,096-wide hidden state and writes a 14,336-wide activation, and the epilogue reads both activations and writes the product. That activation traffic is 159,744 bytes. A fused kernel reads the hidden state once and writes the product, 36,864 bytes. The unfused epilogue moves 4.33 times the fused traffic, and the difference is 120 KiB. The gate weight alone, at BF16, is 112 MiB. At batch 1 the weight traffic dwarfs the 120 KiB. Fusion does not move the 208.6 token roof. It matters when launch overhead dominates a chain of tiny kernels, and when the batch is large enough that activation traffic is no longer a rounding error. A profile that shows the GPU waiting between kernels is the case for fusion. A profile that shows HBM already full of weight reads is the case for a smaller checkpoint or a larger batch, not for another epilogue fuse.

```python
HIDDEN = 4096
INTERMEDIATE = 14336
unfused = 2 * (2 * HIDDEN + 2 * INTERMEDIATE)
unfused += 2 * INTERMEDIATE + 2 * INTERMEDIATE + 2 * INTERMEDIATE
fused = 2 * HIDDEN + 2 * INTERMEDIATE
print(unfused, fused, f"{unfused / fused:.2f}")
print((unfused - fused) // 1024)
print(HIDDEN * INTERMEDIATE * 2 // 1024**2)
# 159744 36864 4.33
# 120
# 112
```

PyTorch's `torch.compile` traces the model and, by default, hands the graph to Inductor, which emits fused kernels, often through Triton. Triton, from OpenAI, is the language those kernels are written in when you need a custom tile and do not want a raw CUDA file. TensorRT-LLM is NVIDIA's serving stack of fused attention and GEMM kernels, plus the runtime that schedules them. CUTLASS is the template library underneath a lot of those GEMMs. vLLM ships its own CUDA and Triton kernels, including paged attention and FlashAttention. A compiler wins when the graph is ordinary. A hand-written kernel wins when the profile shows a fusion the compiler missed, or a layout, such as paged KV blocks, that the general graph does not know about. Changing the compiler changes numerics slightly. The exact-match slice is the check, the same one you run after FlashAttention.

**Trade-offs.** `torch.compile` is the cheapest fusion and it can fail or slow down on graphs full of data-dependent Python. TensorRT-LLM is fast on the models it supports and is another engine to version, with its own kernels and its own gaps. A hand-written Triton kernel can beat both on the one op you measured and can be slower, or wrong, on the shapes you did not test. Fusing everything makes a one-kernel binary that is hard to attribute in a profile. Leaving everything unfused makes a decode that is launch-bound and still moves the weights. You fuse what the profile says is waiting, and you keep the weight-byte roof in view so you do not expect 4.33× end to end.

**Interview.** Define a kernel as the code for one accelerator op, and fusion as keeping intermediates out of HBM. Walk the SiLU numbers: 159,744 bytes unfused, 36,864 fused, 120 KiB saved, against a 112 MiB gate weight, so batch-1 decode does not become 4.33× faster. Name `torch.compile`, Triton, and TensorRT-LLM, and say a custom kernel is justified by a profile. Mention that paged KV and FlashAttention are kernels a generic graph may not invent. The numerics can move, so the task slice is rerun.

**Recap.** Kernels are the accelerator programs behind each layer, and compilers fuse them so activations are not written to HBM between every op. An unfused Llama feed-forward epilogue moves 159,744 activation bytes against 36,864 for a fused one, a 4.33× difference and a 120 KiB saving, while one gate weight is 112 MiB. Batch-1 decode is still dominated by the weights. `torch.compile`, Triton, and TensorRT-LLM are the tools. A handwritten kernel is for the fusion or the layout the compiler missed. The weight-byte roof does not move just because the epilogue got shorter.

## Static, dynamic, and continuous batching

Batching groups requests so the weights loaded for one step are reused across several of them.

A single decode is the roofline's low-intensity corner: the HBM pipe moves the whole model to produce one token. A batch of B tokens reuses those weights, so aggregate tokens per second climb until the step becomes compute-bound. The cost is latency. Someone's token waits on the other requests in the step. The three schedulers differ in how long a request is stuck with that company.

Static batching waits until a fixed number of requests is available, pads them to a common length, and runs the whole batch until the longest one finishes. Four decode lengths of 40, 80, 120, and 400 tokens occupy `400 × 4 = 1,600` slots and do 640 tokens of useful work, a useful fraction of 0.40. Four prefill lengths of 128, 256, 1,024, and 4,096, padded to 4,096, do 5,504 tokens of useful work out of 16,384 padded positions, a useful fraction of 0.336. The short requests sit in the batch until the long one ends. Throughput graphs love this. TTFT and the tail ITL do not. It is a reasonable scheduler for the overnight batch API, where nobody is waiting on the first token of one row, and a poor one for chat.

```python
DECODE = (40, 80, 120, 400)
PREFILL = (128, 256, 1024, 4096)
print(sum(DECODE), max(DECODE) * len(DECODE), f"{sum(DECODE) / (max(DECODE) * len(DECODE)):.2f}")
print(sum(PREFILL), max(PREFILL) * len(PREFILL), f"{sum(PREFILL) / (max(PREFILL) * len(PREFILL)):.3f}")
# 640 1600 0.40
# 5504 16384 0.336
```

Dynamic batching launches when the batch is full or a timeout fires. The timeout caps how long the first request waits, and it will launch a small batch when traffic is thin. You pick the timeout from the TTFT budget. A long timeout fills the GPU and spends the budget. A short timeout protects TTFT and returns you to the one-request roof.

Continuous batching, which Orca, from Yu and coauthors at OSDI 2022, introduced as iteration-level scheduling, admits and retires requests between tokens. A 40-token request leaves at token 40. The slot takes new work instead of padding out to 400. vLLM and TensorRT-LLM, which calls the same idea in-flight batching, schedule this way, and vLLM combines it with paged KV blocks so the new arrival does not need a contiguous reservation. The remaining problem is the prefill. A new request's prefill is a long compute-bound chunk dropped into a step that decode requests expected to be short. Continuous batching does not, by itself, stop that chunk from stalling every ITL in the batch. Chunked prefill breaks the prompt into pieces that fit a gap budget. Disaggregation moves the prompt to another pool. Those are the next card.

**Trade-offs.** Static batching is simple and wasteful, and the waste grows with the spread of lengths, 0.40 useful in the decode example. Dynamic batching is the practical offline-or-online compromise and it has a timeout you can set wrong in either direction. Continuous batching recovers the idle slots and can still miss a TPOT cap when prefills share the GPU. Larger batches raise aggregate tokens and raise the wait. A batch size chosen for MFU rather than for the latency SLO is the goodput failure. Padding to a round number makes kernels happy and bills you for positions that are not tokens.

**Interview.** Define the three schedulers by what a finished short request does. In a static batch it waits for the long one, and the worked decode is 640 useful slots out of 1,600. In a dynamic batch it waits until the timeout or the fill. In a continuous batch it leaves at the next token boundary, which is Orca's iteration-level schedule. Then say continuous batching does not solve prefill interference. Ask for the TTFT and TPOT caps before you praise a throughput number.

**Recap.** Batching reuses a weight load across requests. Static batching pads and waits for the longest request. Four decode lengths of 40, 80, 120, and 400 use 0.40 of their slots, and four prefills padded to 4,096 use 0.336 of their positions. Dynamic batching adds a timeout so TTFT stays bounded. Continuous batching, from Orca, joins and leaves at token boundaries, which is what vLLM and TensorRT-LLM schedule. The short request no longer waits for the long one. A prefill that lands in the same step can still stall every decode, which batching alone does not fix.

## Disaggregated prefill and decode

Disaggregated prefill and decode run the two phases on separate accelerator pools so a long prompt does not stall token generation.

Colocation is the default. One GPU, or one tensor-parallel group, prefills a new request and then decodes it, and continuous batching mixes those steps. The phases want different machines. Prefill is compute-bound and likes a high FLOP peak. Decode is bandwidth-bound and likes HBM bandwidth, and it likes a batch of many short steps. A prefill dropped into a decode step is a long compute job in a line of short ones. On the Llama 3 8B shape, the `2N` forward model at the H100 SXM5's 989.4 TFLOPS dense BF16 peak spends 33.2 ms to prefill 2,048 tokens. A weight-only decode step at the 3.35 TB/s roof is 4.79 ms. If the scheduler runs that prefill inline, every colocated decode sees a gap on the order of the prefill, not on the order of 4.79 ms. A TPOT or ITL cap of 20 ms fails while the average over a quiet period, when no prefill arrived, still looks fine. A real prefill is slower than this roof, because MFU is not 100 percent and attention is extra work. The 33.2 ms is the best case for the linear layers, and it is already over a 20 ms cap.

```python
PARAMS = 8_030_261_248
PREFILL_MS = 2048 * 2 * PARAMS / 989.4e12 * 1e3
DECODE_MS = (PARAMS * 2) / 3.35e12 * 1e3
SLO_MS = 20
print(f"{PREFILL_MS:.1f}")
print(f"{DECODE_MS:.2f}")
print(PREFILL_MS > SLO_MS > DECODE_MS)
# 33.2
# 4.79
# True
```

DistServe, from Zhong and coauthors, puts prefill and decode on separate GPUs and sizes the two pools for goodput under TTFT and TPOT caps. Splitwise, from Patel and coauthors, splits the same two phases and can place them on different GPU types, so the compute-heavy phase and the bandwidth-heavy phase do not have to rent the same SKU. Chunked prefill is the same-GPU alternative: the prompt is cut into pieces small enough that a decode gets the GPU back inside its gap budget. You pay scheduling complexity instead of a second pool. The transfer between a prefill worker and a decode worker is the KV cache for that prompt. On this 8B shape, a 2,048-token cache is 0.25 GiB. That transfer has to be faster than the stall you removed, or you traded a prefill stall for a network stall. Inside one node, NVLink is the comfortable path. Across a slow Ethernet link, the cache movement can dominate.

**Trade-offs.** Disaggregation protects ITL and lets each pool use the parallelism and batch size its phase wants. It leaves a pool idle when the mix shifts. A prefill-heavy hour wastes the decode GPUs. A decode-heavy hour wastes the prefill GPUs. Chunked prefill keeps one pool and can only shrink the stall, not remove the shared GPU. Colocation is the simplest scheduler and the one whose tail ITL moves with whatever prompt just arrived. Goodput is the metric that notices. Throughput is the metric that hides it. The 33.2 ms figure is a roof for one model and one length, not a DistServe result you can quote as a speedup.

**Interview.** Explain the interference with the two roofs: a 2,048-token Llama 3 8B prefill is 33.2 ms at the H100 SXM5 dense BF16 peak, and a decode step is 4.79 ms at the bandwidth roof, so an inline prefill blows a 20 ms gap. Name DistServe and Splitwise as the systems that split the pools, and chunked prefill as the option that stays on one pool. Say the KV cache has to move to the decode workers. Then say you would size the pools for goodput under the product's TTFT and TPOT caps, not for aggregate tokens.

**Recap.** Prefill and decode contend when they share a GPU, because a compute-bound prompt lands in a bandwidth-bound token loop. At the H100 SXM5 roofs, a 2,048-token Llama 3 8B prefill is 33.2 ms and a weight-only decode step is 4.79 ms, so a 20 ms gap fails if the prefill runs inline. DistServe and Splitwise put the phases on separate pools and optimize goodput under TTFT and TPOT caps. Chunked prefill keeps one pool and limits how long the prompt may hold the GPU. The cache has to be transferred, and a slow link can replace the stall you just removed.

## Prompt caching

Prompt caching stores the KV cache of a repeated prefix and reuses it on the next request that begins with that same prefix.

The prefill is the expensive read of a long system prompt, a tool list, or a book you are asking several questions about. If the next request starts with the same tokens, the keys and values are already on the server and the prefill can skip them. The product rules are on the context-length card in [Prompt Engineering](../05_Prompt_Engineering/). The cached portion is a prefix. Edit the first token and the rest misses. OpenAI caches a long enough identical prefix automatically. Anthropic caches at breakpoints you mark. A cache write costs more than a normal input token, a cache read costs less, the default lifetime is short unless a longer one is sold, and the discount moves. This card is the serving reason the discount exists, plus a bill at exercise rates.

On the Llama 3 8B shape, a 4,096-token prefix is exactly 0.50 GiB of BF16 cache. That is the state you reuse. The dollar side, at exercise rates of $1.25 per million input tokens, $5.00 per million output tokens, and a cache-read price of $0.125, is a worked illustration of a read priced at one tenth of input. It is not a quote. One million calls with that 4,096-token prefix, a 512-token question, and 250 output tokens cost $7,010 with no cache and $2,402 with the prefix read from cache. The saving is $4,608, which is the prefix tokens times the gap between the input rate and the read rate. The 512-token question and the output are paid in full every time. Putting the question in front of the system prompt, or editing the system prompt's first line, makes every call a miss and returns you to $7,010.

```python
CALLS = 1_000_000
PREFIX, FRESH, OUTPUT = 4_096, 512, 250
INPUT_RATE, OUTPUT_RATE, READ_RATE = 1.25, 5.00, 0.125
PER_TOKEN = 2 * 32 * 8 * 128 * 2


def dollars(prefix_rate: float) -> float:
    prefix_cost = CALLS * PREFIX / 1_000_000 * prefix_rate
    fresh_cost = CALLS * FRESH / 1_000_000 * INPUT_RATE
    output_cost = CALLS * OUTPUT / 1_000_000 * OUTPUT_RATE
    return prefix_cost + fresh_cost + output_cost


print(f"{dollars(INPUT_RATE):.0f}")
print(f"{dollars(READ_RATE):.0f}")
print(f"{dollars(INPUT_RATE) - dollars(READ_RATE):.0f}")
print(f"{PREFIX * PER_TOKEN / 1024**3:.2f}")
# 7010
# 2402
# 4608
# 0.50
```

A write that costs more than a normal input token is a loss when the prefix is used once. The provider still had to prefill it. The discount appears on the later hits, inside the cache's lifetime. A prefix that changes every call, including a prefix that only changes in the first token, should not be marked for caching. A stable tool list in front of a changing user message should. Self-hosted vLLM and TensorRT-LLM can reuse a prefix too, as a KV block that stays resident. You then pay HBM for that 0.50 GiB, times the number of distinct prefixes you keep, instead of paying the provider's write premium. A cache of a thousand different system prompts is a thousand copies of the cache, not one.

**Trade-offs.** Caching a stable prefix cuts prefill time and, on a hosted API, cuts the input line. It constrains order, and it does nothing for the question or the completion. A write premium on a one-shot prefix spends money to store state you never reread. A long TTL keeps a stale policy prompt in front of the model after you thought you had shipped a new one. Automatic caching, the OpenAI behavior, is easy and can miss when a middleware script rewrites the first tokens. Explicit breakpoints, the Anthropic behavior, are precise and are easy to leave off the one prompt that most needed them. The rates move. The prefix rule does not.

**Interview.** Explain the mechanism as a reused KV cache, and give the 0.50 GiB for a 4,096-token Llama 3 8B prefix. Then give the product rules from Prompt Engineering: prefix only, OpenAI automatic, Anthropic breakpoints, write above the input price, read below it. Compute the exercise million calls, $7,010 uncached and $2,402 cached, saving $4,608. Say a one-shot prefix loses money if the write costs more than a normal read of those tokens. Say you put the stable instructions first and the changing ticket last.

**Recap.** Prompt caching reuses the KV cache of an identical prefix so the server does not prefill it again. A 4,096-token prefix on Llama 3 8B is 0.50 GiB. At the exercise rates, one million calls with a 512-token question and 250 output tokens cost $7,010 uncached and $2,402 with the prefix cached, a saving of $4,608. The cached portion has to be a prefix. OpenAI applies this when the prefix matches. Anthropic applies it at breakpoints you mark. A write costs more than a normal input token, so a prefix used once is the wrong thing to cache. The discount itself is whatever the current price page says.

## Parallelism

Parallelism is how one model uses more than one accelerator, either because the weights and cache do not fit in one, or because one accelerator cannot meet the latency or the throughput on its own.

Data parallelism and replica parallelism share a memory shape and differ in the traffic. A data-parallel training step puts a full copy of the weights on each GPU and all-reduces gradients. A replica at inference time is also a full copy, and it does not synchronize. A router sends each request to one replica. Throughput scales with the number of copies. The latency of a single request does not improve, and the bill scales with the idle copies. Replicas are the right tool when the model fits and the queue is the problem.

Tensor parallelism, the Megatron pattern, splits each layer's matrices across GPUs. Every token uses every GPU in the group, and each layer ends in a collective. The bytes of that collective, for one token, are the hidden state. Llama 3 70B's hidden size is 8,192, so a BF16 activation is 16,384 bytes. At the H100 SXM datasheet's 900 GB/s NVLink, the bandwidth term is 0.018 microseconds. The time you pay is the latency of the collective, which this division does not show. Pipeline parallelism splits the layers into stages. A token visits the stages in order. With one request there is nothing to overlap, so the latency is the sum of the stages plus the sends between them, and the other GPUs are idle during another stage's work. With P stages and M microbatches, the fraction of pipeline slots that sit idle is `(P − 1) / (M + P − 1)`. Four stages and one wave of four microbatches idle 0.43 of the slots. Four stages and 32 microbatches idle 0.086. A chat request you cannot split into 32 independent microbatches pays the bubble. A saturated batch job can hide it.

```python
print(8192 * 2)
print(f"{8192 * 2 / 900e9 * 1e6:.3f}")
print(f"{(4 - 1) / (4 + 4 - 1):.2f}")
print(f"{(4 - 1) / (32 + 4 - 1):.3f}")
# 16384
# 0.018
# 0.43
# 0.086
```

The fit constraint is the 70B checkpoint from [Understanding Foundation Models](../02_Understanding_Foundation_Models/): 131.4 GiB of BF16 weights, which misses one 80 GiB GPU. Two H100 SXM5 GPUs hold 160 GiB. The spare after the weights is 28.6 GiB, before runtime and fragmentation. If that spare were entirely KV cache, at this shape's 320 KiB a token, it would hold 93,716 tokens. It is not entirely cache. One 131,072-token request is 40 GiB of cache on this 70B shape, the figure in Understanding Foundation Models, and 40 GiB does not fit in the 28.6 GiB spare. The INT8 weights in that topic are 65.7 GiB and leave 14.3 GiB on one GPU, a short-context spare, not a 40 GiB one. Tensor parallelism across two GPUs is how the BF16 weights get a home. It does not create a 40 GiB hole next to them.

```python
WEIGHT_GIB = 131.4
PER_TOKEN = 327_680
spare = 160 - WEIGHT_GIB
print(f"{spare:.1f}")
print(round(spare * 1024**3 / PER_TOKEN))
print(f"{131_072 * PER_TOKEN / 1024**3:.0f}")
# 28.6
# 93716
# 40
```

Two more splits are easy to swap because their names are close. Context parallelism shards a long sequence so the attention itself is split. Ring attention, from Liu, Zaharia, and Abbeel, is one way to pass the blocks. Megatron's sequence parallelism is a different device: once tensor parallelism is on, it shards the sequence dimension of the ops that are not already split, so activations are not replicated on every GPU. Context parallelism is about a long prompt fitting. Sequence parallelism is about activation memory next to a tensor-parallel layer. Replica parallelism remains the "another full copy" tool when the unit of scale is requests, not layers.

**Trade-offs.** Tensor parallelism cuts single-request latency when the collective latency is smaller than the benefit of splitting the weights, and it wants NVLink. Across a slow link the 0.018-microsecond bandwidth term is irrelevant and the latency term dominates. Pipeline parallelism raises throughput once the pipe is full and adds a bubble and a stage delay to every lonely request. Replicas scale throughput with no collective and no help for a model that does not fit. Context parallelism fits a long cache and adds a pass over the sequence. Using pipeline parallelism for Copilot-style inline suggestions pays the bubble on a batch of one. Using tensor parallelism across a network boundary pays the collective on every layer. A 70B that you quantized to INT8 to avoid a second GPU is the compression card's trade, and the 14.3 GiB spare still has to hold the cache.

**Interview.** Start from fit. Llama 3 70B in BF16 is 131.4 GiB, two 80 GiB GPUs leave 28.6 GiB, and a 131,072-token cache is 40 GiB, so it does not fit in the spare. Then pick the split from the latency shape. Tensor parallelism cooperates on each token and pays a collective whose payload is 16 KiB, 0.018 microseconds of NVLink bandwidth, plus a latency the bandwidth does not capture. Pipeline parallelism visits stages in order, and four stages with four microbatches idle 0.43 of the slots. Replicas copy the whole model and do not talk. Separate context parallelism from Megatron sequence parallelism in one sentence each. The inline-suggestion product wants tensor parallelism. The full overnight batch can fill a pipeline.

**Recap.** Parallelism splits work that one accelerator cannot hold or cannot finish in time. Replicas are full copies with no gradient sync, and they scale throughput. Tensor parallelism splits each layer and all-reduces a 16 KiB activation, 0.018 microseconds of H100 SXM NVLink bandwidth, plus the collective's latency. Pipeline parallelism splits layers, and the idle fraction of slots is `(P − 1) / (M + P − 1)`, which is 0.43 for four stages and four microbatches and 0.086 for 32 microbatches. Two H100 SXM5 GPUs hold the 131.4 GiB Llama 3 70B weights with 28.6 GiB spare, and a 40 GiB cache at 131,072 tokens does not fit in that spare. Context parallelism shards a long sequence. Megatron sequence parallelism shards activations beside tensor parallelism. They are not the same split.
