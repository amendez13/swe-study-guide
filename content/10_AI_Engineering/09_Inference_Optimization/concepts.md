## What inference optimization is

Inference optimization is the work of serving a trained model inside a latency, throughput, and cost budget while keeping the quality you measured.

A training job pays the forward and backward passes once, or once per experiment. Serving pays a forward pass on every ChatGPT turn, every Claude reply, every Copilot suggestion, and every nightly summary. The autoregressive loop on The transformer card in [Understanding Foundation Models](../02_Understanding_Foundation_Models/) writes one token at a time. The KV cache on the Attention, the KV cache, and context card in that topic grows with the prompt. Those two facts are why a checkpoint that fit in a demo can miss a product. The latency and cost criteria in [Evaluate AI Systems](../04_Evaluate_AI_Systems/) decide whether the wait and the bill are acceptable. This topic is how those numbers move: by changing the checkpoint, or by changing the server around it.

The model half compresses weights, drafts extra tokens, shrinks attention state, and fuses kernels. The service half batches requests, separates prompt reading from token writing, reuses a repeated prefix, and spreads one model across accelerators. None of that is a license to skip the eval. A faster wrong total is a regression. The Inference quantization and Training quantization cards in [Finetuning](../07_Finetuning/), and the Model distillation card in [Dataset Engineering](../08_Dataset_Engineering/), own the accuracy and the training contract. The cards here own the bytes, the bandwidth, and the schedule.

**Trade-offs.** Chasing tokens per second fills the GPU and can push time to first token past the point where a person is still waiting. Chasing the first token leaves the GPU underfilled and raises the cost of every request. A technique that changes the output distribution has to be scored again. A technique that only changes the schedule can still fail the same score if it times out and returns an error. The budget you write down is part of the optimization. A number you did not write down will be the one the technique spends.

**Interview.** Separate the model from the service before you name a library. Say which phase is slow, the prompt or the generated tokens, and which budget moved: latency, throughput under a latency cap, or dollars. Then say you would remeasure the task slice, not the demo. If the question is "how do we make the 70B faster," the first answer is the phase and the byte count, not a kernel name.

**Recap.** Inference optimization makes a trained model serve tokens inside a latency, throughput, and cost budget without giving up measured quality. Training pays the backward pass. Serving pays a forward pass on every request. The model half changes weights, drafts, attention state, and kernels. The service half changes batching, phase placement, prefix reuse, and how many accelerators hold the model. A faster answer that fails the eval is not the goal.

## Prefill and decode

Prefill and decode are the two phases of one generated reply. Prefill reads the prompt and writes the KV cache. Decode appends one new token at a time and reads that cache back.

The split is the serving form of the causal transformer. The model cannot emit token 40 until it has a key and a value for token 39, so the generated half of the request is a loop. The prompt is different. Every prompt token is already known, so the server can run those positions together. That parallel pass is the prefill. It is why a long paste in Claude or ChatGPT sits on "thinking" before the first word, and why the same model then streams words at a steadier pace. The Attention, the KV cache, and context card in [Understanding Foundation Models](../02_Understanding_Foundation_Models/) names the two phases and the cache they share. The roofline card is why they feel different: prefill does a lot of arithmetic per byte, and decode moves the weights again to produce one token.

vLLM, TensorRT-LLM, and the hosted APIs all schedule these phases, whether or not the dashboard shows the names. A request's time to first token includes the queue and the prefill. The gaps after that are decode. A long retrieved document makes the first clock worse even when the decode kernel is unchanged. A huge model makes the second clock worse even when the prompt is short. Optimizing the wrong phase is how a team quantizes weights to fix a stall that was a 20,000-token prefill.

**Trade-offs.** Spending the design on decode leaves a long-context product waiting on the first token. Spending it on prefill leaves a chat that starts quickly and then crawls. The two phases also contend when they share a GPU: a new prefill can pause every decode already in flight, which is the disaggregation card. Splitting them removes that pause and adds a pool you have to size. Short prompts and long answers are a decode problem. Long prompts and short answers are a prefill problem. Copilot inline suggestions and a book-length summary are not the same phase.

**Interview.** Define the two phases from the causal mask, not from a profiler screenshot. Prefill consumes the prompt in parallel and writes keys and values. Decode is serial in the generated tokens and reads those keys and values. Say which product symptom maps to which phase. Then say the next question is arithmetic intensity, because "the GPU is at 100 percent" does not tell you which ceiling you hit.

**Recap.** Prefill reads the whole prompt and builds the KV cache. Decode walks the generation one token at a time because each token depends on the one before it. Time to first token is mostly queue plus prefill. The later gaps are decode. A long prompt and a long answer stress different ceilings, and a fix for one phase does not move the other.

## Arithmetic intensity and the roofline

Arithmetic intensity is the floating-point work a kernel does per byte it moves. The roofline is the pair of ceilings that intensity runs into: peak compute, and peak memory bandwidth.

Williams, Waterman, and Patterson published the model in 2009. A chip can issue only so many operations per second, and it can move only so many bytes per second. The ridge point is peak FLOPs divided by peak bandwidth, in FLOPs per byte. A kernel whose intensity is below the ridge is memory-bandwidth-bound. It finishes when the bytes arrive, with arithmetic units waiting. A kernel above the ridge is compute-bound. It finishes when the arithmetic units are done, with bandwidth to spare. Buying a faster ALU does nothing for a kernel below the ridge. Buying faster memory does nothing for a kernel above it.

The H100 SXM5 is the worked chip. Its dense BF16 tensor-core peak is 989.4 TFLOPS, the figure in [Understanding Foundation Models](../02_Understanding_Foundation_Models/), and the datasheet lists its HBM bandwidth at 3.35 TB/s. This topic treats that 3.35 as `3.35 × 10^12` bytes per second. The ridge is 295.3 FLOPs per byte. One square BF16 projection of hidden size 4,096, the Llama 3 8B width, shows the two regimes. The FLOP count is `2 × sequence × 4096 × 4096`, a multiply and an add. The bytes are the input, the weight, and the output at 2 bytes each. At one token the intensity is 1.00 FLOP per byte, far below the ridge, so that step is bandwidth-bound. At 4,096 tokens the intensity is 1,365.3 FLOPs per byte, above the ridge, so that step is compute-bound. The crossover for this single projection is about 345 tokens. The A100 80GB SXM ridge, 312 TFLOPS over its datasheet 2,039 GB/s, is 153.0 FLOPs per byte. H100's tensor-core peak grew by more than its memory bandwidth, so a layer that sat nearer the ridge on A100 is more clearly bandwidth-bound on H100. An H200 SXM does the opposite of that step. The FLOPs card keeps the H100 SXM's sparse BF16 line and raises bandwidth to 4.8 TB/s, so the dense ridge falls to 206.1 FLOPs per byte. Same arithmetic peak, more bytes per second, and decode has an easier time hiding behind the bandwidth.

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

"Memory-bound" is two complaints, and the fixes are different. Bandwidth-bound is the ridge above: the weights fit, and the step waits on bytes per second. Capacity-bound means they do not fit. The checkpoint, the KV cache, or the batch exceeds HBM, so the kernel spills, offloads, or does not launch. Quantizing, shortening the context, cutting concurrency, or adding a GPU answers a capacity miss. A faster HBM pipe answers a bandwidth miss and does nothing for a model that does not load. Saying "the GPU is memory-bound" without saying which one sends the team to buy bandwidth for a problem that was 12.6 GiB of weights plus a cache on a card that had 24. The memory-size card is the capacity arithmetic. This card is the bandwidth arithmetic. Name the one you measured.

**Trade-offs.** A compute optimization on a bandwidth-bound decode burns a week and leaves tokens per second where they were. A bandwidth optimization on a compute-bound prefill does the same in the other direction. Raising the batch raises intensity, because the weights are loaded once and reused, and it also raises the wait for the request that arrived first. The ridge moves when you change chips or dtypes. An INT8 tensor-core peak and a 1-byte weight are a different ridge than BF16.

**Interview.** Draw the ridge as peak FLOPs over peak bandwidth and put a number on it for a named SKU: 295.3 FLOPs per byte on the H100 SXM5 at the dense BF16 peak and 3.35 TB/s. Then put one token and a 4,096-token prefill on either side of it for a 4,096-wide BF16 projection, 1.00 against 1,365.3. Say the crossover for that layer is about 345 tokens, and that the KV cache pushes decode further toward bandwidth. Close with the decision rule: name the bound before you pick the optimization.

**Recap.** Arithmetic intensity is FLOPs per byte moved. The roofline's ridge is peak FLOPs divided by peak bandwidth. On an H100 SXM5 that ridge is 295.3 FLOPs per byte for dense BF16 and the datasheet's 3.35 TB/s. A 4,096-wide BF16 projection at one token has intensity 1.00 and is bandwidth-bound. At 4,096 tokens it has intensity 1,365.3 and is compute-bound. The crossover is about 345 tokens for that layer alone. The H200 SXM ridge is 206.1, because the bandwidth rose and the sparse BF16 line did not. Prefill of a long prompt is the compute side. Decode of one token is the bandwidth side.

## Online and batch inference APIs

An online inference API returns tokens inside an interactive wait. A batch inference API accepts a pile of requests and returns them later, at a lower price per token.

The online path is ChatGPT, Claude.ai, Copilot, and any call your own service makes while a person or a downstream tool is blocked. The clocks on the next cards are the contract: time to first token, the gap between later tokens, and a timeout. The batch path is the overnight job. On the docs checked 12 November 2026, OpenAI's Batch API is a 50 percent discount against the synchronous APIs, and `24h` is the only completion window it documents. Batches often finish sooner, and a batch that misses the window expires. Anthropic's Message Batches API charges 50 percent of the standard API prices. The same page says most batches finish within an hour, that you can read results when the batch finishes or at 24 hours, and that unfinished requests expire at 24 hours. The one-hour sentence is not a latency SLO. The window and the discount can move. The page you would actually sign is the one that counts. The half below is that 50 percent shape, applied to exercise rates, not a quote.

A foundation-model batch API is not the batch inference a classical model has used for years. The classical job precomputes predictions before anyone asks. A recommender writes scores for the catalog overnight, and the request reads a row that already exists. The OpenAI and Anthropic batch APIs queue the same request you would have sent online, the same prompt, the same generation, and they run it later for a discount. They do not score a user who has not shown up. If the product needs an answer for every customer before the customer arrives, that is a precompute, and a language-model batch window is the wrong tool unless you are willing to generate those answers in advance and store them. If the product can wait until after the request exists, the batch API is the discount. Do not describe the second as the first in a design review. The storage, the staleness, and the failure mode are different. A precomputed score can be a day old. A batch-API completion is late, and it is about the prompt you submitted.

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

**Trade-offs.** The batch discount is real money on a large, delay-tolerant job, and it is useless for a person watching a cursor. A 24-hour window is a deadline, not a promise that every line finishes in minutes. Anthropic's "most batches finish within an hour" is an observation on their page, not an SLO you can page someone for. Mixing the urgent ticket into the batch makes that ticket late. Running the whole digest on the online rate pays double, at these exercise prices, for a latency nobody needed. Prices and windows move, so a budget that hard-codes 50 percent has to be recomputed when the page changes.

**Interview.** Split the traffic before you mention the discount. Interactive calls stay on the online API. Delay-tolerant calls go to the batch API. As of 12 November 2026 both OpenAI and Anthropic document 50 percent off, OpenAI's only window is 24 hours, and Anthropic expires unfinished requests at 24 hours while saying most batches finish sooner. Re-read the page. Compute a bill both ways. Here, 100,000 documents at the exercise rates are $1,200 synchronous and $600 in batch. Say what you refuse to batch: anything whose caller is blocked on the answer.

**Recap.** Online APIs answer inside an interactive latency budget. On the docs checked 12 November 2026, OpenAI's Batch API and Anthropic's Message Batches both charge 50 percent of the synchronous price. OpenAI documents a 24-hour completion window. Anthropic expires unfinished work at 24 hours and says most batches finish within an hour, which is not an SLO. On the exercise rates, 100,000 documents of 6,000 input tokens and 500 output tokens cost $1,200 online and $600 in batch. The discount is payment for a loose deadline. A chat turn does not have that deadline. A later price page replaces the 50 percent.

## TTFT, TPOT, and inter-token latency

Time to first token, time per output token, and inter-token latency are three clocks on one generation.

Time to first token, TTFT, is the wait from the request until the first output token is available at the server. It includes queueing and prefill. Time per output token, TPOT, is the average gap between later tokens. Inter-token latency, ITL, is one of those gaps, and the tail of ITL is the stall a stream actually hit. [Evaluate AI Systems](../04_Evaluate_AI_Systems/) fixes the formula this topic uses: TTFT already includes the first token, so N output tokens take `TTFT + TPOT × (N − 1)`. A vendor that divides total generation time by N, first token included, is using a different TPOT. Reconcile the definitions before you compare dashboards. The token a user sees can be later still, after the network and the client buffer it. The objective has to name which clock it means.

A worked stream, not the 0.400 and 0.020 second example in that topic, makes the arithmetic local. TTFT of 1.20 seconds and TPOT of 0.040 seconds put an 80-token reply at 4.36 seconds. The decode rate on that stream is 25 tokens a second. The end-to-end rate is 18.35, because the 1.20 seconds produce the first token and then sit in the denominator. Three later gaps of 0.030, 0.035, and 0.090 seconds average to 0.052. A TPOT near 0.040 can hide the 0.090 stall. A voice reply and a streamed chat care about that stall. A batch job that only stores the finished string cares about the 4.36 seconds, and often not even that.

For a streamed document the person will read, TPOT only has to beat reading speed. A planning figure, not a measured reading study: a few words a second of English is on the order of 10 tokens a second when a word is one or two tokens. The 25 tokens a second above is already ahead of that reader, so shaving TPOT from 0.040 seconds to 0.020 seconds spends decode budget the person cannot take in. TTFT is still the wait before anything appears. Voice, and a caption the ear has to keep up with, are the products where each gap is perceived. A chat transcript the person scrolls is not. Set the TPOT budget from the interaction, not from the smallest number the kernel can print.

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

`nvidia-smi` will not show you that 0.339. Its utilization is the fraction of time at least one kernel was resident on the GPU, a busy percentage. A decode kernel that is launched back to back and then waits on HBM can sit at 100 percent busy while MFU is a fraction of a percent and model bandwidth utilization, the next card, is the number that is actually high. The busy percentage answers "did we forget to launch work." MFU answers "what fraction of peak arithmetic did the model's FLOPs occupy." MBU answers "what fraction of the HBM pipe did we move." A capacity problem, the weights did not fit, shows up as the process failing or spilling before any of the three is interesting. Read the busy percentage to see that the GPU was scheduled. Read MFU and MBU to see what it was busy doing.

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

Raising the batch raises intensity and can raise MFU, until the step crosses the ridge and the tensor cores are the ceiling. Quantizing weights raises the token rate of a bandwidth-bound decode and therefore raises this MFU, because you still do about `2N` FLOPs and you do them more often per second. The quantization card puts the group-128 4-bit case at 1.31 percent. That is still a bandwidth-bound decode, not PaLM's training number. MFU is a useful alarm when a compute-bound prefill or a training step is far below the peak you paid for. It is a bad alarm for batch-1 decode.

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

The product consequence is which software and which number format you are allowed to assume. An A100 80GB SXM has BF16, FP16, TF32, INT8, and INT4 tensor cores, and it does not have FP8. An H100 SXM5 does have FP8 tensor cores. An H200 SXM is still that Hopper programming model. The FLOPs card is where its memory differs. A TPU v4's peak is quoted for BF16 and INT8. A kernel written for one of those paths is not a kernel for the others. MIG, NVIDIA's multi-instance GPU, can slice one H100 into as many as seven 10 GB instances. That is useful for small models with small traffic. It also slices the HBM. A large model that needed the whole 80 GB does not become seven large models.

Training chips and inference chips spend that area differently. A training part wants high-precision or BF16 throughput, a fast interconnect for the collective, and enough memory to hold optimizer state. An inference part can spend the budget on low precision and on memory bandwidth, because decode is the bandwidth side of the roofline and the weights are not being updated. AWS splits the two on purpose: Trainium for training, Inferentia for inference. NVIDIA's L4 and L40S are sold into inference and graphics servers where an H100's training interconnect is wasted. Groq's language-processing unit is a public inference accelerator aimed at deterministic token latency rather than at a training collective. A transformer-specific chip hard-wires the matmul and attention pattern and gives up the general CUDA program a GPU still runs. The three questions before you pick any of them are the same. Can it run this model: does the memory hold the weights and the cache, does the dtype exist, does the software stack load the checkpoint. How fast: TTFT, TPOT, and tokens per second at the batch you will actually serve. How much: dollars per million tokens, and the power, against the card you are comparing. A chip that wins peak FLOPs and fails the first question does not run. A chip that runs and misses the reading-speed TPOT on a chat stream, or blows the power budget, is not the cheap one.

**Trade-offs.** A GPU is the flexible default and the one most serving stacks target. A TPU can be the better training machine inside Google's stack and a poor choice for a CUDA-only server. A CPU still runs the tokenizer, the scheduler, the web server, and small models, and it is the wrong place for a 70B decode if you had a choice. Slicing a GPU with MIG raises isolation and cuts the memory each slice can use. Assuming every accelerator has FP8, NVLink, or a CUDA graph is how a portable-looking config fails on the machine you actually rented.

**Interview.** Define an accelerator as a chip that spends its area on parallel numeric work rather than on branchy control. Contrast a GPU's tensor cores with a TPU's systolic array, and name the software: CUDA and TensorRT-LLM on one side, XLA on the other. Give one published peak with the chip attached, such as 275 TFLOPS for a TPU v4 or 989.4 TFLOPS dense BF16 for an H100 SXM5. Say the ridge is peak FLOPs over bandwidth on whichever chip you picked. The TPU v4's is 229 FLOPs per byte.

**Recap.** An accelerator is a parallel numeric chip. NVIDIA GPUs use tensor cores. Google TPUs use systolic arrays, and a TPU v4 chip peaks at 275 TFLOPS of BF16 or INT8 with a ridge of 229 FLOPs per byte. PaLM trained on TPU v4. vLLM and TensorRT-LLM target GPUs. FP8 is a Hopper feature, not an A100 feature. The roofline is the same picture on all of these chips. The datasheet you read has to be the chip you are holding.

## FLOPs and number formats

A published FLOP rate is the peak arithmetic of one number format on one SKU, and the datasheet's sparsity footnote is a different peak from the dense one.

[Finetuning](../07_Finetuning/) owns what BF16, FP16, FP8, and INT8 mean as formats: range, mantissa, and scales. [Understanding Foundation Models](../02_Understanding_Foundation_Models/) owns the dense-versus-sparse distinction for the H100 and uses 989.4 TFLOPS as the dense BF16 tensor-core peak. This card is the serving table those facts plug into. The Hopper architecture paper lists the H100 SXM5 at 989.4 TFLOPS of dense BF16 tensor core and 1,978.9 TFLOPS with 2:4 sparsity. The product datasheet's row "H100 SXM" rounds that sparse line to 1,979 TFLOPS and says the specification is half without sparsity, which is 989.5. This guide keeps 989.4, the architecture-paper dense peak and the figure in Understanding Foundation Models. The same datasheet row puts FP8 and INT8 at 3,958 with the sparsity footnote, so the dense reading of that line is half, 1,979. Memory on that row is 80 GB of HBM3 at 3.35 TB/s, and TDP is up to 700 W, configurable. The starred numbers assume 2:4 structured sparsity, two zeros in every four weights. A dense matmul does not get the starred line.

The product datasheet's H100 PCIe row is a different chip. It lists BF16 and FP16 at 1,513 TFLOPS with sparsity, so the dense reading is 756.5, and the architecture paper prints 756 dense and 1,513 with sparsity. Memory is 80 GB of HBM2e at 2 TB/s. TDP is 300 to 350 W, configurable. The architecture paper's earlier table printed 2,039 GB/s for that module and marked the bandwidth as not finalized. The shipping datasheet is the 2 TB/s line. Quoting the SXM5's 989.4 TFLOPS or 3.35 TB/s for a PCIe board overstates both the arithmetic and the pipe.

NVIDIA's H200 SXM table reprints the H100 SXM sparse tensor-core lines, including 1,979 TFLOPS of BF16, and lists 141 GB of HBM3e at 4.8 TB/s with a TDP up to 700 W, configurable. The page still marks that table preliminary. The arithmetic peak does not move. The memory does. Half of the printed 1,979 is 989.5, and 989.5 over 4.8 TB/s is a ridge of 206.1 FLOPs per byte, against the H100 SXM5's 295.3. Do not read 141 GB as 141 GiB, and do not assume the 131.4 GiB Llama 3 70B weights fit until the device reports its MiB.

The A100 80GB SXM datasheet lists 312 TFLOPS of dense BF16 tensor core and 624 with sparsity, 80 GB of HBM2e at 2,039 GB/s, and a 400 W standard TDP. The HGX custom-thermal SKU can go to 500 W. This card uses 400 W. The A100 has INT8 and INT4 tensor cores and no FP8 tensor core. A TPU v4 chip peaks at 275 TFLOPS of BF16 or INT8. That is not a sparse-tensor-core footnote.

| SKU | Dense BF16 tensor core | 2:4 sparse line | Memory | Bandwidth | Power |
| --- | --- | --- | --- | --- | --- |
| H100 SXM5, datasheet row "H100 SXM" | 989.4 TFLOPS | 1,979 TFLOPS on the datasheet, 1,978.9 in the architecture paper | 80 GB HBM3 | 3.35 TB/s | Up to 700 W, configurable |
| H100 PCIe | 756 TFLOPS in the architecture paper | 1,513 TFLOPS | 80 GB HBM2e | 2 TB/s on the product datasheet | 300 to 350 W, configurable |
| H200 SXM, table still marked preliminary | Half of the printed sparse line, 989.5 | 1,979 TFLOPS | 141 GB HBM3e | 4.8 TB/s | Up to 700 W, configurable |
| A100 80GB SXM | 312 TFLOPS | 624 TFLOPS | 80 GB HBM2e | 2,039 GB/s | 400 W standard |
| TPU v4 chip | 275 TFLOPS BF16 or INT8 | Not an NVIDIA sparse tensor core | 32 GiB HBM2 | 1,200 GB/s | Running mean 170 W, max 192 W. TDP is not applicable |

The H100 SXM5's dense BF16 peak is 3.17 times the A100 80GB SXM's. Its bandwidth is 1.64 times, 3.35 TB/s against 2,039 GB/s. Compute peak grew faster than memory bandwidth, which is why the ridge rose from 153.0 to 295.3 FLOPs per byte on the roofline card. The H100 PCIe card does not inherit that gap. Its architecture-paper dense peak is 2.42 times the A100 80GB SXM's, and its 2 TB/s is 0.98 times that A100's bandwidth. An H200 SXM keeps the H100 SXM's sparse line and offers 1.43 times the H100 SXM's bandwidth, which is why its ridge falls to 206.1. FP8 on Hopper cuts weight bytes and raises the tensor-core ceiling together. That is a different lever from weight-only INT4, which cuts bytes and still does the matmul in a wider type after a dequant.

```python
print(f"{989.4 / 312:.2f}")
print(f"{3.35e12 / 2.039e12:.2f}")
print(f"{756 / 312:.2f}")
print(f"{2e12 / 2.039e12:.2f}")
print(f"{4.8 / 3.35:.2f}")
print(f"{(1979 / 2) / 4.8:.1f}")
# 3.17
# 1.64
# 2.42
# 0.98
# 1.43
# 206.1
```

**Trade-offs.** The sparse peak is a real datasheet line and a misleading denominator for a dense model. FP8 buys Hopper throughput and adds a scaling problem the finetuning format card already names. Staying on BF16 keeps the serving stack simpler and spends bandwidth you may not have. Comparing an H100 SXM5 with an A100 PCIe card, or a TPU v4 with a GPU, without naming the SKU, produces a fake speedup. The TPU's 275 TFLOPS is not a worse H100. It is a different chip with a different compiler and a different memory system.

**Interview.** Refuse a FLOP number that has no SKU, no dtype, and no dense-or-sparse flag. Give the H100 SXM5 as 989.4 TFLOPS dense BF16, 1,979 with 2:4 sparsity on the datasheet, 3.35 TB/s, up to 700 W. Give the H100 PCIe as 756 TFLOPS dense BF16 in the architecture paper, 2 TB/s, and 300 to 350 W. Give the H200 SXM as the same 1,979 sparse BF16 line, 141 GB at 4.8 TB/s, and a ridge of 206.1, and say the table is still marked preliminary. Give the A100 80GB SXM as 312 TFLOPS dense BF16, 2,039 GB/s, 400 W, and no FP8. Say the 3.17× compute gap against the 1.64× bandwidth gap is the SXM5-versus-A100-SXM comparison, not the PCIe card. Put the sparse peak in the denominator only when the weights are actually 2:4 sparse and the kernel uses the sparse tensor cores.

**Recap.** FLOP peaks are per format and per SKU. The H100 SXM5 architecture paper lists 989.4 TFLOPS dense BF16 and 1,978.9 with 2:4 sparsity. The product datasheet rounds the sparse line to 1,979 and halves it when sparsity is off. The H100 PCIe card is 756 TFLOPS dense BF16 in that paper, 2 TB/s, and 300 to 350 W. The H200 SXM table keeps the 1,979 sparse line, lists 141 GB of HBM3e at 4.8 TB/s, and is still marked preliminary. Half of 1,979 over 4.8 TB/s is a ridge of 206.1 FLOPs per byte. The A100 80GB SXM is 312 TFLOPS dense BF16, 2,039 GB/s, 400 W, and has no FP8 tensor core. The SXM5's dense BF16 peak is 3.17 times that A100's, and its bandwidth is 1.64 times. The PCIe H100's bandwidth is 0.98 times that A100's.

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
# 14.96
# 208.6
# 195.5
# 4.79
```

The same datasheet prints PCIe Gen5 at 128 GB/s beside NVLink at 900 GB/s. Both printed totals are bidirectional aggregates. A host-to-GPU copy of the weights uses one direction. Half of 128 GB/s is 64 GB/s before protocol overhead, and a measured copy is lower. At `64 × 10^9` bytes per second the same BF16 weights move at 4.0 tokens a second. Treating the printed 128 GB/s as one-way traffic produces 8.0 and overstates the offload roof by about two. The H100 PCIe module's own HBM, 2 TB/s on the product datasheet, is a different and higher roof, 124.5 tokens a second for these weights, and it is still not the SXM5's 208.6. The H200 SXM's 4.8 TB/s, on a table the page still marks preliminary, raises this weight-only roof to 298.9 tokens a second if the checkpoint is resident and the kernel hits the pipe. NVLink is the path a tensor-parallel collective uses, and the tensor-parallelism card counts how small that payload is. None of these links is HBM. A capacity plan that adds "80 GB" and forgets 3.35 TB/s will buy a card the weights fit on and then miss the token rate. A plan that quotes 208.6 and forgets the cache will miss it once the prompts get long.

```python
WEIGHTS = 8_030_261_248 * 2
print(f"{128e9 / WEIGHTS:.1f}")
print(f"{64e9 / WEIGHTS:.1f}")
print(f"{2e12 / WEIGHTS:.1f}")
print(f"{4.8e12 / WEIGHTS:.1f}")
# 8.0
# 4.0
# 124.5
# 298.9
```

**Trade-offs.** More HBM fits a longer cache and a larger batch, and it costs money and power even when the batch is empty. More bandwidth raises the decode roof and does not, by itself, speed a compute-bound prefill. Offloading weights to host memory fits a model the HBM cannot hold and replaces the HBM roof with the one-way PCIe ceiling, 4.0 tokens a second here, not the bidirectional 128 GB/s line. Quantizing weights raises the HBM roof by shrinking the denominator, which is the quantization card, and it does not raise the roof if the kernel dequantizes by first materializing a full BF16 copy in a way that moves the wide bytes anyway. You read the kernel, not only the checkpoint dtype.

**Interview.** Separate capacity from bandwidth and name the SKU. H100 SXM5: 80 GB of HBM3, which this guide treats as 80 GiB, at 3.35 TB/s. Then compute the Llama 3 8B BF16 roof, 208.6 tokens a second, and the 195.5 once an 8,192-token cache is in the byte count. Say the datasheet's 128 GB/s PCIe line is bidirectional, so the one-way planning ceiling is 64 GB/s and 4.0 tokens a second for these weights, not 8.0. Mention 124.5 on an H100 PCIe card's 2 TB/s HBM and 298.9 on the H200 SXM's 4.8 TB/s only with the SKU attached. Say the 50 MB L2 is why the weights are reread from HBM on every token.

**Recap.** HBM capacity holds the weights and the KV cache. HBM bandwidth sets the decode roof. On an H100 SXM5, 3.35 TB/s over the Llama 3 8B's 14.96 GiB of BF16 weights is 208.6 tokens a second, or 4.79 ms a token, and 195.5 tokens a second once an 8,192-token cache is also read. The on-chip cache is tens of megabytes, so it does not keep the model. The datasheet's PCIe Gen5 line of 128 GB/s is bidirectional. A one-way host-to-GPU stream at half of that, 64 GB/s, is 4.0 tokens a second for these weights. The H100 PCIe module's 2 TB/s HBM is 124.5, and the H200 SXM's 4.8 TB/s is 298.9, on a table still marked preliminary. A measured rate above the roof of the link you are actually using is an accounting error. A measured rate far below it is the MBU card.

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

Google Cloud's TPU v4 page lists measured power as 90 W minimum, 170 W mean, and 192 W maximum. The Jouppi and coauthors system paper splits that into an idle of 90 W and a running minimum, mean, and maximum of 121 W, 170 W, and 192 W, and it marks TDP as not applicable. Do not divide 275 TFLOPS by 170 W and call it a TDP efficiency. Peak FLOPs over a measured mean is a different ratio from peak FLOPs over a nameplate cap, and the two should not be ranked against the H100's 1.41. The facilities number in Understanding Foundation Models stays the training example: up to 16,384 H100 GPUs at a 700 W TDP is 11.5 megawatts of accelerator nameplate before CPUs, network, and cooling. An inference fleet is the same kind of sum on however many GPUs you leave powered overnight. Idle watts are why a spiky product often prefers an API, which is the self-hosting card in Evaluate AI Systems. This card is the per-GPU cap inside that choice.

**Trade-offs.** Provisioning the nameplate keeps the SLO when the chip boosts, and it overstates the average bill if the decode rarely hits 700 W. Provisioning the average trips the breaker at the peak or throttles the clock, which moves both FLOPs and bandwidth. A chip with better FLOPs per watt can be the wrong buy for a bandwidth-bound decode if its HBM per watt is worse and the absolute bandwidth does not clear the token roof. Cooling and the network are outside the TDP and outside the 11.5 megawatt figure. Leaving them out understates the room.

**Interview.** Call TDP a cap. Give the H100 SXM5 as up to 700 W and the A100 80GB SXM standard configuration as 400 W. Compute dense BF16 per watt, 1.41 against 0.78, and HBM per watt, 4.79 GB/s against 5.10. Say which one a decode buys. Point at the 11.5 megawatt Llama 3 training nameplate as the cluster form of the same cap, and say it excludes cooling. Refuse a TPU comparison that divides peak FLOPs by the 170 W measured mean and ranks it against a TDP ratio.

**Recap.** Power is the cap under the peaks. The H100 SXM5 is up to 700 W. The standard A100 80GB SXM is 400 W. Dense BF16 peak per nameplate watt is 1.41 TFLOPS against 0.78, a ratio of 1.81. HBM bandwidth per watt is 4.79 GB/s against 5.10, because bandwidth grew 1.64 times while nameplate watts grew 1.75 times. Decode buys bandwidth. Prefill buys the arithmetic per watt. TDP is not an average draw, and a TPU v4's measured 170 W mean is not a TDP you can rank against these ratios. The 11.5 megawatt figure in Understanding Foundation Models is this cap times a training cluster, before cooling.

## Quantization

Quantization stores the weights in fewer bits so a bandwidth-bound decode moves fewer bytes per token.

[Finetuning](../07_Finetuning/) owns the accuracy side: post-training weight-only methods such as GPTQ and AWQ, activation quantization such as LLM.int8() and SmoothQuant, the group of 128, and the warning that INT4 moves arithmetic and exact tokens first. This card owns the serving math, and it keeps that topic's rule that a BF16 weight is 2 bytes. A raw 4-bit packing is 0.5 bytes. GPTQ and AWQ store a scale per group. At a group of 128 and one FP16 scale, the scale adds `2 / 128` bytes, so a parameter costs 0.515625 bytes. A zero-point stored as another 2 bytes per group moves the cost to 0.53125 bytes. That zero-point width is an assumption for this packing, not a claim that every file uses an FP16 zero. On the Llama 3 8B count, the scale-only packing is 3.86 GiB of weights against 14.96 GiB in BF16. If decode stays bandwidth-bound and the kernel truly moves the packed bytes, the H100 SXM5 roof rises from 208.6 tokens a second to 809.1, a factor of 3.88. The zero-point packing is a factor of 3.76 instead. The same step's MFU rises from 0.339 percent to 1.31 percent, because the `2N` FLOPs happen more often per second. That is still a bandwidth-bound decode. Prefill, which is compute-bound, may not speed up, and a dequant kernel can spend the arithmetic the smaller checkpoint saved. The A100 80GB SXM can run INT8 and INT4 tensor cores. FP8 tensor cores are the Hopper row on the FLOPs card, not a reason to expect FP8 on that A100. Weight-only INT4 often dequantizes back to BF16 for the matmul, so the A100's INT4 tensor cores are not automatically the kernel you get.

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

FP8 on an H100 is the other cut. The weights are 1 byte and the tensor cores run FP8, so both the byte count and the arithmetic ceiling change. Weight-only INT4 changes the bytes and leaves the matmul in a wider type after the dequant. A kernel that first materializes a full BF16 copy moves the wide bytes anyway, and the roof does not rise. You read the kernel, not only the checkpoint dtype. The KV-cache card is a different tensor. Quantizing weights does not quantize keys and values.

**Trade-offs.** INT4's 3.88× byte reduction, at this group-128 scale and on this H100 SXM5 roof, is the decode win and the accuracy risk Finetuning already names. Finer groups and a skipped output projection give some of the accuracy back and spend some of the bytes. FP8 needs Hopper. Staying on BF16 keeps the stack simpler and spends bandwidth you may not have. A prefill that was compute-bound can stay compute-bound after the weights shrink. Stacking quantization with pruning and distillation in one checkpoint makes a failure undebuggable. Change one, then score the slice that previously failed.

**Interview.** Keep 2 bytes per BF16 parameter. Show the group-128 FP16 scale turning 0.5 bytes into 0.515625, and the H100 SXM5 roof moving from 208.6 to 809.1 tokens a second, MFU from 0.339 percent to 1.31 percent. Say the zero-point factor of 3.76× assumes 2 extra bytes per group. Say prefill may not move, and that a dequant which rewrites BF16 weights into HBM cancels the roof. Point GPTQ, AWQ, and the accuracy slice at Finetuning. Pruning and distillation are the next two cards, not a second name for this one.

**Recap.** Quantization stores weights in fewer bits. Weight-only 4-bit with a group-128 FP16 scale is 0.515625 bytes per parameter, 3.86 GiB for Llama 3 8B, and an H100 SXM5 decode roof of 809.1 tokens a second against 208.6 in BF16, which is 3.88×. MFU moves from 0.339 percent to 1.31 percent and the step is still bandwidth-bound. A 2-byte zero-point per group makes the factor 3.76×. FP8 on Hopper changes bytes and the tensor-core peak together. A kernel that materializes BF16 weights moves the wide bytes anyway. The accuracy decision stays in Finetuning.

## Pruning

Pruning deletes weights so the checkpoint contains zeros, and it speeds serving only when the kernel stops loading those zeros.

Unstructured pruning, as in SparseGPT from Frantar and Alistarh and Wanda from Sun and coauthors, can zero many values and still leave a kernel that loads the dense tensor and skips the zeros only in the ALU. You then pay the BF16 traffic anyway, and the H100 SXM5 decode roof stays 208.6 tokens a second for the Llama 3 8B weights. NVIDIA's 2:4 structured sparsity is the pattern the starred tensor-core peaks assume, two zeros in every four weights. The FLOPs card's 1,979 TFLOPS line is twice the 989.4 dense peak only when the weights are in that pattern and the kernel uses the sparse tensor cores. A 50 percent sparse checkpoint that is not in that pattern does not get the 1,979 line. It also does not get a smaller HBM read. The zeros are still bytes on the bus.

```python
print(f"{1979 / 989.4:.2f}")
# 2.00
```

The product consequence is which peak you are allowed to put in an MFU denominator. A dense Llama matmul on an H100 SXM5 is divided by 989.4 TFLOPS. Dividing it by 1,979 reports half the utilization the chip could have delivered for that matmul, which is the MFU card's warning about a sparse denominator. Pruning is not quantization. Quantization changes the width of every stored value. Pruning changes which values exist, and only a matching kernel changes the bytes that move.

**Trade-offs.** A 2:4 pattern can use the sparse tensor cores and raises the arithmetic peak, and it constrains which weights you are allowed to keep. Unstructured sparsity is easier to get to a high zero count and often leaves the HBM traffic unchanged. Combining it with INT4 makes two accuracy hits and two kernel requirements. If the profile still shows a dense weight read, the zeros were free in the paper and not free on the GPU.

**Interview.** Separate unstructured pruning from 2:4 sparsity. Name SparseGPT and Wanda as unstructured methods that can zero weights without shrinking the load. Say the starred 1,979 TFLOPS line requires the structured pattern and a kernel that uses it, and that 1,979 / 989.4 is 2.00 only in that case. Refuse a sparse peak in the denominator of a dense matmul. Quantization is the byte-width card. This card is whether the zeros move.

**Recap.** Pruning deletes weights. Unstructured sparsity, including SparseGPT and Wanda, can leave a kernel that still loads the dense tensor, so the BF16 decode roof does not move. NVIDIA's 2:4 pattern is what the starred tensor-core peak assumes, and 1,979 is 2.00 times the 989.4 dense BF16 peak only when that kernel runs. A 50 percent sparse checkpoint in any other pattern does not get the line. The zeros have to disappear from the HBM read before the token rate changes.

## Distillation at serving time

Distillation, at serving time, is the decision to run a smaller student instead of the teacher, after the student has been trained on the teacher's outputs.

[Dataset Engineering](../08_Dataset_Engineering/) owns the method: Hinton's soft targets, sequence-level text when the teacher is an API, DistilBERT's published summary, and the license limit on training from a provider's outputs. This card owns the bytes that change when you serve the student. Weight bytes fall with the parameter count, so a bandwidth-bound token roof rises in proportion. The KV cache falls only if the student also has fewer layers or fewer key-value heads. A student that keeps the teacher's attention shape and only shrinks the feed-forward still moves almost the same cache. The public comparison already on the other cards is Llama 3 8B against Llama 3 70B. The 8B is 14.96 GiB of BF16 weights and 128 KiB of cache per token. The 70B, in Understanding Foundation Models, is 131.4 GiB and 320 KiB per token. Serving the 8B in place of the 70B is an 8.78× cut in weight bytes and a 2.50× cut in cache bytes per token. Distillation is one way to get a checkpoint you are willing to serve in the smaller shape. Quantization is a different checkpoint of the same shape. They are not substitutes you can skip measuring.

```python
print(f"{131.4 / 14.96:.2f}")
print(f"{320 / 128:.2f}")
# 8.78
# 2.50
```

You remeasure the task. A cheaper model that misses the slice is the finetuning topic's reason not to ship a checkpoint, applied to a student. The license travels with the teacher's outputs. A student that is fast and not allowed to ship is not a serving win.

**Trade-offs.** A smaller student can clear a latency SLO a quantized large model still misses, because both the weights and, when the attention shape shrinks, the cache get smaller. It caps quality at the questions you asked the teacher, under that teacher's license. Quantizing the teacher keeps the teacher's weights, rounded, and keeps the teacher's cache shape. Pruning the teacher keeps the shape too. Picking the student because the parameter count looks like the latency budget, without the cache formula, is how a long-context 8B still misses an HBM plan the weight ratio seemed to solve.

**Interview.** Point the training and the license at Dataset Engineering, including DistilBERT's published summary, and do not rederive them. Then give the serving ratio you can defend: Llama 3 8B against Llama 3 70B is 131.4 / 14.96 = 8.78× fewer weight bytes and 320 / 128 = 2.50× fewer cache bytes per token. Say the cache ratio is the attention shape, not an automatic consequence of "smaller." Say you would score the task slice on the student you intend to serve.

**Recap.** Distillation's serving effect is a smaller model. The training contract, DistilBERT's summary, and the license stay in Dataset Engineering. Weight bytes fall with the parameter count. Cache bytes fall only when layers or key-value heads fall. Llama 3 8B against Llama 3 70B is 8.78× fewer BF16 weight bytes and 2.50× fewer cache bytes per token. That is a different checkpoint from a quantized 70B. The task slice still has to pass.

## Speculative decoding

Speculative decoding drafts several future tokens with a cheap model and then checks them with the model you serve, so one expensive step can accept more than one token.

The reason it exists is the decode roof. A target as large as Llama 3 70B is bandwidth-bound at batch 1, and each token rereads the weights. A smaller draft model proposes γ tokens. The target then scores those positions together, which is a short prefill rather than γ sequential decode steps, and keeps the longest prefix that agrees with its own distribution. Leviathan, Kalman, and Matias, in 2023, and Chen and coauthors, in 2023, both give a rejection rule that leaves the target distribution unchanged. On a rejection you draw from the residual between the target and the draft, not from the draft. Greedy decoding is the special case where you keep a draft token only when it is the target's argmax, which preserves the greedy string. Naively keeping the draft whenever it "looks close" does not.

If each draft token is accepted independently with probability α, which is Leviathan and coauthors' i.i.d. assumption, the expected number of tokens per target step is `(1 − α^(γ+1)) / (1 − α)`. That count includes the bonus token the target can emit when every draft token is accepted, and it includes the one token you still emit when the first draft token is rejected. They define c as the time for one draft forward divided by the time for one target forward. Their wall-time theorem also assumes the target can score the γ drafted positions, plus the bonus position, in about one target step. That assumption fits a bandwidth-bound decode, where a short verification still reads the weights once. It does not fit a batch that is already compute-bound. Under those assumptions the expected speedup is `(1 − α^(γ+1)) / ((1 − α)(γc + 1))`. In their experiments c was always under 0.05 and often close to zero. The values below are a worked acceptance rate of 0.7, a draft of 4 tokens, and a cost coefficient of 0.05 at that reported bound. They are not a cell from the paper's speedup table.

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

**Interview.** Explain the draft, the parallel verify, and the residual sample that keeps the target distribution. Write the expected-token formula and evaluate it at a labeled α. Here, α = 0.7 and γ = 4 give 2.77 tokens, and c = 0.05 cuts the speedup from 2.77× to 2.31×. Say c was always under 0.05, and often near zero, in the Leviathan experiments, and that this 0.05 is a worked coefficient at that bound, not their table. Name the two assumptions in the speedup: independent acceptance, and a verification that fits in one target step. Name the failure: a slow or inaccurate draft, or a tokenizer mismatch, makes the feature a slowdown. Point at Chen and coauthors as the other 2023 paper with a distribution-preserving rule.

**Recap.** Speculative decoding lets a small draft propose tokens that the target verifies in one step. Leviathan and coauthors and Chen and coauthors give rejection rules that preserve the target distribution. With their independent-acceptance assumption, one target step yields `(1 − α^(γ+1)) / (1 − α)` tokens. At a worked α of 0.7 and γ of 4, that is 2.77 tokens. With their cost model at a worked c of 0.05, and with verification counted as one target step, the speedup is 2.31× rather than 2.77×. A draft that is too slow or too wrong makes decoding slower. The tokenizer has to match.

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

The Attention, the KV cache, and context card in [Understanding Foundation Models](../02_Understanding_Foundation_Models/) derives the formula. Two tensors, times layers, times key-value heads, times head dimension, times bytes per number, times tokens. Tokens means the prompt plus the tokens generated so far. The Inference memory card in [Finetuning](../07_Finetuning/) applies it to Llama 2 7B, which has 32 key-value heads, and gets 512 KiB a token. This card applies it to the released Llama 3 8B shape, which the 70B cards do not: 32 layers, hidden size 4,096, intermediate size 14,336, 32 query heads, 8 key-value heads, head dimension 128, vocabulary 128,256, and untied input and output embeddings. That count is 8,030,261,248 parameters, 14.96 GiB in BF16 at 2 bytes per parameter.

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

The 70B shape in Understanding Foundation Models is the other worked point: 320 KiB a token, 1.25 GiB at 4,096 tokens, and 40 GiB at 131,072 tokens, with BF16 weights of 131.4 GiB that do not fit one 80 GiB GPU. Storing the cache in 1 byte halves these bytes before scales, and it adds a numerical error you measure. That packing, and the choice to leave the cache on the host, is the next card. Grouped-query attention is why the 8B's 16 GiB figure is the one to plan with. Full multi-head attention at 32 key-value heads would be 64 GiB at the same long context, which is the card after that.

**Trade-offs.** A longer context lets a user paste the thread, and it raises cache memory linearly. Concurrency multiplies the cache and does not multiply the weights. Quantizing the cache saves bytes and can move the token the model would have produced. Paging, on the PagedAttention card, removes the waste of reserving the maximum length. It does not make a live 16 GiB cache smaller. Forgetting the cache and planning from the 14.96 GiB of weights is how a single demo fits and four long sessions do not.

**Interview.** Write the formula and pick the model whose config you can defend. For Llama 3 8B in BF16, 128 KiB a token, 1 GiB at 8,192, 16 GiB at 131,072, weights 14.96 GiB, one long request 30.96 GiB, four of them 78.96 GiB, five of them 94.96 GiB. Mention Llama 2 7B's 512 KiB only to show the key-value head ratio, and point the 70B's 40 GiB at Understanding Foundation Models rather than rederiving it. Say activations sit on top, so 78.96 GiB is not a comfortable fit on an 80 GiB GPU.

**Recap.** KV-cache bytes are two tensors times layers times key-value heads times head dimension times bytes times tokens. The untied Llama 3 8B shape is 8,030,261,248 parameters and 14.96 GiB in BF16. Its cache is 128 KiB a token, 1 GiB at 8,192 tokens, and 16 GiB at 131,072 tokens. One 128k request is 30.96 GiB with the weights. Four are 78.96 GiB before activations. Five are 94.96 GiB and miss an 80 GiB GPU. The 70B cache figures stay in Understanding Foundation Models. The weights are paid once, and the cache is paid per live request.

## KV cache quantization and offloading

KV cache quantization stores keys and values in fewer bytes. KV cache offloading keeps those bytes in host memory and reads them back over the bus for each new token.

The KV-cache card's 128 KiB is BF16, 2 bytes per number. A 1-byte storage of the same layout, before scales, is 64 KiB a token. At 131,072 tokens that is 8 GiB instead of 16 GiB, so five of those requests are 40 GiB of cache instead of 80 GiB, and the four-request plan that was 78.96 GiB with BF16 weights becomes 14.96 plus 32 GiB of cache, 46.96 GiB, before activations. A scale per tensor or per channel adds a little on top of the half. vLLM and TensorRT-LLM both have an FP8 cache path. KIVI is a published 2-bit cache method. KVQuant is a published low-bit cache method. The quality hit is a measurement on the task slice, the same rule Finetuning uses for INT4 weights. Keys and values are not weights. A recipe that was fine for the checkpoint can move the token when it is applied to the cache.

Offloading is a different lever. The cache stays at full width and lives on the host, and every decode step pulls the live keys and values across PCIe. On this 8B shape an 8,192-token BF16 cache is 1 GiB. At the memory card's one-way planning ceiling of 64 GB/s, that read is 16.8 ms, before the weights. A 131,072-token cache is 16 GiB and the same ceiling is 268.4 ms a token. The weight-offload roof on that card is 4.0 tokens a second however long the prompt is, because the weight bytes do not grow with the prompt. The cache-offload cost does. FlexGen, from Sheng and coauthors, is the published system that offloads weights and cache to CPU and disk. vLLM can offload the cache to CPU memory as well. Both are how a model that does not fit still answers. Neither is an interactive token rate once the cache is long.

```python
PER_TOKEN_BF16 = 2 * 32 * 8 * 128 * 2
PER_TOKEN_BYTE = PER_TOKEN_BF16 // 2
ONE_WAY = 64e9
print(PER_TOKEN_BF16 // 1024, PER_TOKEN_BYTE // 1024)
print(f"{131_072 * PER_TOKEN_BF16 / 1024**3:.0f}")
print(f"{131_072 * PER_TOKEN_BYTE / 1024**3:.0f}")
print(f"{14.96 + 4 * 8:.2f}")
print(f"{PER_TOKEN_BF16 * 8192 / ONE_WAY * 1e3:.1f}")
print(f"{16 * 1024**3 / ONE_WAY * 1e3:.1f}")
# 128 64
# 16
# 8
# 46.96
# 16.8
# 268.4
```

**Trade-offs.** A 1-byte cache doubles the number of long requests that fit in HBM and can change the next token. A 2-bit cache saves more and is a larger quality question, which is why KIVI and KVQuant exist as papers rather than as a default flag. Offloading fits a context the GPU cannot hold and replaces the HBM read with a PCIe read that grows with length. Quantizing and then offloading stacks the error and the bus. Leaving the cache in HBM and shortening the context is the option that keeps the 4.79 ms weight roof in view. Paging, on the PagedAttention card, does not shrink a live token and does not move it to the host.

**Interview.** Separate three byte cuts. Quantizing weights is the quantization card. Quantizing the cache halves the 128 KiB to 64 KiB before scales, and 131,072 tokens fall from 16 GiB to 8 GiB. Offloading the cache at the one-way 64 GB/s ceiling costs 16.8 ms for an 8,192-token BF16 cache and 268.4 ms for 16 GiB. Say weight offload is a fixed 4.0 tokens a second on the memory card, and cache offload gets worse as the prompt grows. Name FP8 in vLLM or TensorRT-LLM as the common 1-byte path, KIVI as a 2-bit method, and KVQuant as a low-bit method. Then say you would remeasure the slice.

**Recap.** KV cache quantization stores keys and values in fewer bits. A 1-byte packing of the Llama 3 8B layout is 64 KiB a token, 8 GiB at 131,072 tokens, before scales. Four such caches plus the BF16 weights are 46.96 GiB. FP8 in vLLM and TensorRT-LLM is the usual 1-byte path. KIVI is a 2-bit method and KVQuant is a low-bit method, and the quality hit is measured. Offloading keeps the full cache on the host. At 64 GB/s one way, an 8,192-token cache takes 16.8 ms to read and a 16 GiB cache takes 268.4 ms. Weight offload does not grow with the prompt. Cache offload does.

## Multi-query, grouped-query, and sliding-window attention

Multi-query, grouped-query, and sliding-window attention shrink the keys and values a new token has to read.

Multi-head attention gives every query head its own key and value. Multi-query attention, from Shazeer in 2019, keeps a single key-value head for all of the query heads. Grouped-query attention, from Ainslie and coauthors in 2023, is the middle: several query heads share one key-value head. PaLM used multi-query attention. Llama 2 uses grouped-query attention at 70B and ordinary multi-head attention at 7B and 13B. Llama 3 uses 8 key-value heads at the 8B, 70B, and 405B sizes. The Attention, the KV cache, and context card in [Understanding Foundation Models](../02_Understanding_Foundation_Models/) records the 70B consequence: 8 key-value heads rather than 64 makes the 40 GiB cache at 131,072 tokens discussable, where the full key-value head count would be 320 GiB. The 8B shape is the factor of four you can see next to the KV-cache card. Thirty-two key-value heads would be 512 KiB a token. Eight are 128 KiB. At 131,072 tokens that is 64 GiB against 16 GiB.

Cross-layer attention shares keys and values across layers, which grouped-query attention does not. Brandon and coauthors, at NeurIPS 2024, compute the key and value projections in only some layers and let the neighboring layers reuse those activations. A sharing factor of two, their CLA2, stores about half the KV cache of the same model without that reuse. It stacks with multi-query or grouped-query attention, because one choice shares heads inside a layer and the other shares layers. Their 1B and 3B trains from scratch found the pair-of-layers version the robust one, with a small perplexity cost next to the cache cut. That is a training-time architecture choice. You do not turn it on in a Llama checkpoint that computed a fresh key and value in every layer. The quality trade is the reused key: a layer that needed its own view of the tokens is now reading a neighbor's. Score the long-context task after the cache math, the same way you score grouped-query attention after you enjoy the smaller cache.

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

## FlashAttention

FlashAttention is an attention kernel that computes the weighted sum in on-chip tiles and does not write the score matrix out to HBM.

Dao and coauthors published it in 2022. Dao's FlashAttention-2 followed in 2023. FlashAttention-3, from Shah and coauthors in 2024, targets Hopper, including its FP8 tensor cores and asynchronous copies. The Attention, the KV cache, and context card in [Understanding Foundation Models](../02_Understanding_Foundation_Models/) already says the important limit: it speeds the math, up to small numerical differences, and it does not delete the cache you keep for decode. The byte reason is the score matrix. For one head at 8,192 tokens, stored in BF16, the scores are `8192 × 8192 × 2` bytes, which is 128 MiB. The Q, K, and V for that head are 6 MiB, so the scores are 21.3 times the vectors they came from. Thirty-two heads in one layer would be 4 GiB of score matrices if you materialized them together. A naive kernel writes the scores, rereads them for the softmax, and rereads them for the values. FlashAttention keeps a tile, updates the softmax statistics, and never stores that matrix. The 1 GiB KV cache for the whole Llama 3 8B model at this length is still allocated. FlashAttention changed the prefill's traffic. It did not change the decode's resident state. PagedAttention, the next card, is the allocator for that resident state. It is not this kernel.

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

The prefill of a long prompt is where the score matrix would have dominated. A batch-1 decode attends with one new query against the stored keys, so the score row is short and the weight read is still the roof on the memory card. Enabling FlashAttention does not move 208.6 tokens a second. It also does not make two prefills numerically identical. The exact-match slice is the check after you change the kernel.

**Trade-offs.** FlashAttention speeds the prefill and still leaves you holding the cache, so a memory plan that deletes the 16 GiB because "we enabled FlashAttention" is wrong. The numerical differences are small and are still a reason to remeasure a strict exact-match slice. FlashAttention-3's FP8 path is a Hopper kernel, not a flag on an A100. A fused kernel that the compiler did not emit is the kernels card. This card is specifically the score matrix.

**Interview.** Define it as tiling so the `S × S` matrix is not written to HBM. At 8,192 tokens one BF16 head is 128 MiB of scores against 6 MiB of QKV, 21.3 times, and 32 heads materialized together are 4 GiB. Say the KV cache remains, and point paging at the next card rather than treating the two papers as one feature. Name the versions: 2022, FlashAttention-2 in 2023, FlashAttention-3 for Hopper in 2024. Say a decode that is already at the weight roof does not speed up.

**Recap.** FlashAttention computes attention in on-chip tiles and does not write the score matrix to HBM. One head at 8,192 tokens would otherwise write 128 MiB of BF16 scores against 6 MiB of Q, K, and V, which is 21.3 times, and 32 heads together would be 4 GiB. The 1 GiB Llama 3 8B KV cache at that length stays. FlashAttention-2 and the Hopper-oriented FlashAttention-3 are later kernels with the same limit. Paging the cache is a different paper.

## PagedAttention

PagedAttention is a KV-cache allocator that stores each request's keys and values in fixed-size blocks so a request does not reserve its maximum length up front.

Kwon and coauthors published it in 2023, and it is the allocator behind vLLM. A server that reserves each request's maximum context up front fragments HBM the way an operating system would if it gave every process its peak heap. On the Llama 3 8B shape, ten requests reserved at 8,192 tokens and actually using 1,024 hold 10.00 GiB of reservations and 1.25 GiB of real tokens. The other 8.75 GiB cannot be given to an eleventh request even though it is empty. Paging the cache in blocks, a block of 16 tokens is a common page size in vLLM, makes those empty regions reusable. The live tokens still cost 128 KiB each in BF16. The last partial block wastes up to 15 tokens of that page. Paging recovers fragmentation. It is not quantization, it is not FlashAttention, and it is not a smaller attention head count.

```python
PER_TOKEN = 131_072
print(f"{10 * 8192 * PER_TOKEN / 1024**3:.2f}")
print(f"{10 * 1024 * PER_TOKEN / 1024**3:.2f}")
print(f"{(10 * 8192 - 10 * 1024) * PER_TOKEN / 1024**3:.2f}")
# 10.00
# 1.25
# 8.75
```

FlashAttention is the kernel you want during prefill, so the score matrix stays on chip. PagedAttention is the allocator you want while many decodes of different lengths share a GPU. The two stack. Neither one raises the HBM datasheet bandwidth. A step that is already at the weight-moving roof stays there. A live 16 GiB cache at 131,072 tokens is still 16 GiB after you page it.

**Trade-offs.** Paging raises concurrency and adds a block table and some internal fragmentation of the last partial block. A page size of one token is a lot of bookkeeping. A huge page brings back the waste paging was meant to remove. Serving without paging wastes HBM on reserved tails, 8.75 GiB in the example. Serving without a tiled attention kernel writes score matrices you do not need, which is the previous card. Offloading the cache to the host is the KV-cache quantization card, not a page size.

**Interview.** Define PagedAttention as vLLM's block allocator, from Kwon and coauthors in 2023. Ten Llama 3 8B requests reserved at 8,192 and used at 1,024 are 10.00 GiB reserved and 1.25 GiB live, so 8.75 GiB is empty and stuck. Say a block of 16 is a common page and the live token is still 128 KiB. Say what it does not do: it does not delete the score-matrix problem, and it does not shrink a token that is actually live.

**Recap.** PagedAttention stores the KV cache in reusable blocks so a request does not reserve its maximum length. Ten Llama 3 8B requests reserved at 8,192 tokens and using 1,024 cost 10.00 GiB of reservations and 1.25 GiB of real cache, which leaves 8.75 GiB unusable until you page. A block of 16 tokens is a common page. The live token still costs 128 KiB in BF16. Paging recovers fragmentation. FlashAttention is the kernel that avoids writing scores. This card is the allocator.

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

## The cost of structured outputs

The serving cost of a structured output is the extra work that keeps each token inside a schema, on top of the ordinary prefill and decode.

[Understanding Foundation Models](../02_Understanding_Foundation_Models/) owns the four ways to get a parseable object and the three contracts people mix up. JSON mode, as OpenAI documents it, promises a JSON string and not your schema. A schema mask refuses illegal tokens. A tool call returns a function name and arguments your code may still refuse to run. This card is what that mask costs in time. Outlines, XGrammar from Dong and coauthors in 2024, and llguidance compile a grammar or a JSON schema into a mask over the tokenizer. vLLM can apply that mask while it decodes. Every new token, the sampler rejects ids the automaton forbids. That work sits on the decode loop. A slow mask can dominate a step whose weight roof, on the Llama 3 8B and an H100 SXM5, is 4.79 ms. Compiling the grammar is a time-to-first-token cost, paid before or beside the prefill, and a large schema makes it larger. Speculative decoding still has to obey the mask. A draft token the grammar rejects is a rejection even when the target model would have accepted it, so the acceptance rate α on the speculative-decoding card falls for reasons that have nothing to do with the draft's match to the target. XGrammar's paper argues the mask can be applied with much less CPU work than a naive scan of the vocabulary. Quote a speedup from a measurement on your engine, not from that paper's table as if it were your server.

Providers that bill output tokens do not add a second meter for the mask unless the current rate card says so. You pay in TTFT when the grammar is compiled, in TPOT when the mask is slow, and in a lower speculative speedup when drafts fall outside the grammar. A receipt reader that returns `{"total": 12.50}` and a tool call in ChatGPT, Claude, or Gemini are the same serving problem once the schema is enforced in the sampler. The parser that checks the total against the receipt stays, because a schema-valid object can still be the wrong total. That check is the Structured outputs card in Understanding Foundation Models. It is not free either, but it is ordinary CPU after the last token.

**Trade-offs.** A mask removes illegal syntax and can force a valid empty object when the model was trying to refuse, which is the quality point on that earlier card. A huge schema raises compile time and per-token mask time. Turning speculation off avoids illegal drafts and gives up the speculative speedup. JSON mode without a schema is cheaper on the sampler and still needs a parser. Finetuning the shape, the fourth rung on that card, spends training instead of a per-token mask and still does not guarantee the schema after the next change. There is no token-price discount for being constrained. The bill is the tokens you generated, at the latency the mask allowed.

**Interview.** Point at Understanding Foundation Models for JSON mode versus a schema mask versus a tool call. Then put the cost on the clocks. Compilation sits in TTFT. The per-token mask sits in TPOT, next to a 4.79 ms weight roof that a slow mask can exceed. Speculation and the grammar share one acceptance rule, so a draft the schema forbids does not count. Say you would measure the same prompt with and without the schema before you blame the model. Say the output token price does not grow just because the sampler wore a mask, and that you would re-read the rate card anyway.

**Recap.** Structured output costs serving time because each token has to stay inside a grammar. Outlines, XGrammar, and llguidance build that mask, and vLLM can apply it. The compile shows up in time to first token. A slow mask shows up in the gap between tokens, which on this 8B and an H100 SXM5 is otherwise a 4.79 ms weight roof. Speculative drafts that the grammar rejects lower the acceptance rate. The token price is still the token price unless the rate card says otherwise. A valid object can still hold the wrong total, so the parser from Understanding Foundation Models stays.

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

DistServe, from Zhong and coauthors, puts prefill and decode on separate GPUs and sizes the two pools for goodput under TTFT and TPOT caps. Splitwise, from Patel and coauthors, splits the same two phases and can place them on different GPU types, so the compute-heavy phase and the bandwidth-heavy phase do not have to rent the same SKU. Chunked prefill is the same-GPU alternative. Sarathi-Serve, from Agrawal and coauthors at OSDI 2024, cuts the prompt into pieces small enough that a decode gets the GPU back inside its gap budget. You pay scheduling complexity instead of a second pool. The transfer between a prefill worker and a decode worker is the KV cache for that prompt. On this 8B shape, a 2,048-token cache is 0.25 GiB. That transfer has to be faster than the stall you removed, or you traded a prefill stall for a network stall. Inside one node, NVLink is the comfortable path. Across a slow Ethernet link, the cache movement can dominate.

**Trade-offs.** Disaggregation protects ITL and lets each pool use the parallelism and batch size its phase wants. It leaves a pool idle when the mix shifts. A prefill-heavy hour wastes the decode GPUs. A decode-heavy hour wastes the prefill GPUs. Chunked prefill keeps one pool and can only shrink the stall, not remove the shared GPU. Colocation is the simplest scheduler and the one whose tail ITL moves with whatever prompt just arrived. Goodput is the metric that notices. Throughput is the metric that hides it. The 33.2 ms figure is a roof for one model and one length, not a DistServe result you can quote as a speedup.

**Interview.** Explain the interference with the two roofs: a 2,048-token Llama 3 8B prefill is 33.2 ms at the H100 SXM5 dense BF16 peak, and a decode step is 4.79 ms at the bandwidth roof, so an inline prefill blows a 20 ms gap. Name DistServe and Splitwise as the systems that split the pools, and chunked prefill as the option that stays on one pool. Say the KV cache has to move to the decode workers. Then say you would size the pools for goodput under the product's TTFT and TPOT caps, not for aggregate tokens.

**Recap.** Prefill and decode contend when they share a GPU, because a compute-bound prompt lands in a bandwidth-bound token loop. At the H100 SXM5 roofs, a 2,048-token Llama 3 8B prefill is 33.2 ms and a weight-only decode step is 4.79 ms, so a 20 ms gap fails if the prefill runs inline. DistServe and Splitwise put the phases on separate pools and optimize goodput under TTFT and TPOT caps. Chunked prefill keeps one pool and limits how long the prompt may hold the GPU. The cache has to be transferred, and a slow link can replace the stall you just removed.

## Prompt caching

Prompt caching stores the KV cache of a repeated prefix and reuses it on the next request that begins with that same prefix.

The prefill is the expensive read of a long system prompt, a tool list, or a book you are asking several questions about. If the next request starts with the same tokens, the keys and values are already on the server and the prefill can skip them. The stable product rule is on the Context length and context efficiency card in [Prompt Engineering](../05_Prompt_Engineering/). The cached portion is a prefix. Edit the first token and the rest misses. Two host shapes cover the mechanism. Implicit caching can apply by itself once a long prefix is identical. Explicit caching writes only at a breakpoint you mark, and a request with no breakpoint writes nothing. A minimum prefix applies in either shape, often on the order of a thousand tokens, and a provider may count cached tokens in blocks. TTL options are a short default, on the order of minutes, and a longer retention you pay more to keep. As checked 12 Nov 2026, check provider docs, a typical short-lived write is about 1.25 times the uncached input price, a longer TTL is about 2 to 2.5 times, and a typical read is about 0.1 times, with some models cheaper. The write rate replaces the input rate for those tokens. Those multipliers will move. The prefix rule will not. This card is the serving reason the discount exists, plus a bill at exercise rates that use the common 0.1 times read.

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

**Trade-offs.** Caching a stable prefix cuts prefill time and, on a hosted API, cuts the input line. It constrains order, and it does nothing for the question or the completion. A write premium on a one-shot prefix spends money to store state you never reread. A long TTL keeps a stale policy prompt in front of the model after you thought you had shipped a new one. Implicit caching is easy and can miss when a middleware script rewrites the first tokens, or when you switch that request to explicit mode and forget the breakpoint. Explicit breakpoints are precise and are easy to leave off the one prompt that most needed them. The rates move. The prefix rule does not.

**Interview.** Explain the mechanism as a reused KV cache, and give the 0.50 GiB for a 4,096-token Llama 3 8B prefix. Then give the prefix rule from the Context length and context efficiency card, and date the price shape. As checked 12 Nov 2026, check provider docs: a typical short-lived write is about 1.25 times uncached input, a longer TTL is about 2 to 2.5 times, and a typical read is about 0.1 times. Implicit caching can apply on its own. Explicit mode with no breakpoint writes nothing. Compute the exercise million calls, $7,010 uncached and $2,402 cached, saving $4,608, and say the 0.1 read is an exercise use of that common multiplier. Say a one-shot prefix loses money when the write costs more than a normal read of those tokens. Say you put the stable instructions first and the changing ticket last.

**Recap.** Prompt caching reuses the KV cache of an identical prefix so the server does not prefill it again. A 4,096-token prefix on Llama 3 8B is 0.50 GiB. At the exercise rates, one million calls with a 512-token question and 250 output tokens cost $7,010 uncached and $2,402 with the prefix cached, a saving of $4,608. The cached portion has to be a prefix. Implicit caching can apply to that prefix on its own. Explicit caching writes only at a breakpoint, and writes nothing when the breakpoint is missing. As checked 12 Nov 2026, check provider docs, a typical short-lived write is about 1.25 times uncached input, a longer TTL is about 2 to 2.5 times, and a typical read is about 0.1 times. A write that costs more than a normal input token makes a prefix used once the wrong thing to cache. A later price page replaces the multipliers.

## Replica parallelism

Replica parallelism serves several full copies of one model and sends each request to one copy.

A data-parallel training step also puts a full copy of the weights on each GPU, and then it all-reduces gradients. An inference replica does not synchronize. A router in front of several vLLM or TensorRT-LLM processes, each holding the Llama 3 8B, is this pattern. Four copies can finish about four times the requests when the router is fair and the GPUs are not already full. One Copilot suggestion does not get faster, because it still runs on one copy. The bytes do not shrink. Four H100 SXM5 GPUs do not make the 131.4 GiB BF16 Llama 3 70B fit if each replica needs the whole checkpoint. That fit is the tensor-parallelism card. Replicas are the right tool when the model fits and the queue is the problem. They are the wrong tool when one request does not fit.

Prompt caching cares which copy the request lands on. The KV state for a prefix lives on the GPU that computed it. A router that sends the next turn of the same conversation to a random replica misses that cache and pays the prefill again. A router that sticks a conversation to one replica keeps the cache and can leave the other replicas idle. The power card is why those idle copies still cost watts.

**Trade-offs.** Throughput scales with the number of copies. The latency of one request does not, and the bill scales with the idle copies. Sticky routing protects a prefix cache and unbalances the queue. Random routing fills the GPUs and throws the cache away. Replicas do not help a 70B that misses one 80 GiB GPU. Quantizing that 70B so it fits on one GPU, and then replicating it, is the quantization card's trade followed by this one. The 14.3 GiB INT8 spare in Understanding Foundation Models still has to hold the cache on every replica.

**Interview.** Define a replica as a full copy that does not all-reduce. Contrast it with data-parallel training, which does. Say four 8B copies raise throughput and do not shorten one suggestion. Say four copies of a 131.4 GiB checkpoint do not create a GPU that can hold it. Mention sticky routing if the product reuses a prefix. Tensor, pipeline, and context parallelism are the cards you pick when one request does not fit or one GPU is too slow for that request.

**Recap.** Replica parallelism runs full independent copies and routes each request to one of them. Training data parallelism all-reduces gradients. These replicas do not. Throughput scales with the copies. One request's latency does not, and a model that does not fit on one GPU still does not fit. A sticky router keeps a prompt-cache prefix on the GPU that built it. A random router prefills it again. Idle copies still draw power.

## Tensor parallelism

Tensor parallelism splits each layer's matrices across accelerators so every token uses every GPU in the group.

This is the Megatron pattern. Each layer ends in a collective. The bytes of that collective, for one token, are the hidden state. Llama 3 70B's hidden size is 8,192, so a BF16 activation is 16,384 bytes, 16 KiB. NVIDIA lists 900 GB/s of NVLink on the H100 SXM. That figure is the bidirectional aggregate. The bandwidth term is 0.018 microseconds at 900 GB/s and 0.036 microseconds at half of it. Either way the division is far below the latency of the collective, which this arithmetic does not show. Across PCIe or Ethernet the latency term gets worse and the 0.018 microsecond story stops being the one you tell. The inline-suggestion product, Copilot's latency class, wants this split when one GPU cannot hold the model or cannot hit the token gap. The four-GPU timing in the drills is an exercise tax on top of the split. It is not this 0.018.

```python
payload = 8192 * 2
print(payload)
print(f"{payload / 900e9 * 1e6:.3f}")
print(f"{payload / 450e9 * 1e6:.3f}")
# 16384
# 0.018
# 0.036
```

The fit constraint is the 70B checkpoint from [Understanding Foundation Models](../02_Understanding_Foundation_Models/): 131.4 GiB of BF16 weights, which misses one 80 GiB GPU. Two H100 SXM5 GPUs hold 160 GiB. The spare after the weights is 28.6 GiB, before runtime and fragmentation. If that spare were entirely KV cache, at this shape's 320 KiB a token, it would hold 93,716 tokens. It is not entirely cache. One 131,072-token request is 40 GiB of cache on this 70B shape, and 40 GiB does not fit in the 28.6 GiB spare. The INT8 weights in that topic are 65.7 GiB and leave 14.3 GiB on one GPU, a short-context spare, not a 40 GiB one. Tensor parallelism across two GPUs is how the BF16 weights get a home. It does not create a 40 GiB hole next to them. Replicas would need the full 131.4 GiB on each GPU and would not help.

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

**Trade-offs.** Tensor parallelism can cut single-request latency when the collective latency is smaller than the benefit of splitting the weights, and it wants NVLink. Across a slow link the bandwidth term is irrelevant and the latency term dominates, once per layer. The spare next to a split 70B is still only 28.6 GiB on two 80 GiB GPUs, so a 40 GiB cache does not fit. Quantizing to INT8 to stay on one GPU is the quantization card, and the 14.3 GiB spare still has to hold the cache. Pipeline parallelism, the next card, avoids a collective on every layer and adds a bubble instead.

**Interview.** Start from fit. Llama 3 70B in BF16 is 131.4 GiB, two 80 GiB GPUs leave 28.6 GiB, and a 131,072-token cache is 40 GiB, so it does not fit in the spare. Then describe the collective. The payload is 16 KiB. At the datasheet's 900 GB/s that is 0.018 microseconds, and at half, the one-direction reading of a bidirectional total, it is 0.036. Say the latency of the collective is the term the division leaves out, and that NVLink is why you keep the group inside one node. Replicas do not solve this fit. Pipeline parallelism is the other way to split the layers.

**Recap.** Tensor parallelism splits every layer across GPUs and ends the layer with a collective. A Llama 3 70B activation is 16 KiB. On an H100 SXM that is 0.018 microseconds at the printed 900 GB/s of NVLink and 0.036 microseconds at half of it, plus the collective's latency. Two H100 SXM5 GPUs hold the 131.4 GiB weights with 28.6 GiB spare, and a 40 GiB cache at 131,072 tokens does not fit in that spare. The split gives the weights a home. It does not give the long cache a free 40 GiB.

## Pipeline parallelism

Pipeline parallelism assigns consecutive layers to different accelerators, and a token walks those stages in order.

With one request there is nothing to overlap. The latency is the sum of the stages plus the sends between them, and the other GPUs are idle during another stage's work. With P stages and M microbatches, the fraction of pipeline slots that sit idle is `(P − 1) / (M + P − 1)`. Four stages and one wave of four microbatches idle 0.43 of the slots. Four stages and 32 microbatches idle 0.086. A chat request you cannot split into 32 independent microbatches pays the bubble. A saturated overnight batch can hide it. That is why Copilot-style inline suggestions want tensor parallelism, and a full batch job can fill a pipeline. The activation that moves between stages is small next to the weights. The cost you feel on one request is the stages adding, not the width of that activation.

```python
print(f"{(4 - 1) / (4 + 4 - 1):.2f}")
print(f"{(4 - 1) / (32 + 4 - 1):.3f}")
# 0.43
# 0.086
```

The same 70B can be staged instead of tensor-split. Each GPU holds some of the layers, so the weights can fit when they miss one GPU. A single inline suggestion still waits for every stage. The drills put a number on that wait for four H100s. This card keeps the bubble, which that drill does not recompute. The KV cache for a layer stays on the stage that owns the layer, so a long context is split with the layers rather than replicated. It is still memory you have to count.

**Trade-offs.** Pipeline parallelism raises throughput once the pipe is full and adds a bubble and a stage delay to every lonely request. A deeper pipeline cuts the weights per GPU and lengthens the bubble for a small M. Microbatching hides the bubble and raises the time until the first microbatch finishes, which is a TTFT cost. Tensor parallelism pays a collective every layer and can keep one token moving on all the GPUs at once. Using the pipeline for inline suggestions pays 0.43 idle when you only have four microbatches, and worse when you have one. Using it for the overnight batch, where 32 microbatches are normal, is the case the formula is kind to.

**Interview.** Write the idle fraction `(P − 1) / (M + P − 1)`. Four stages and four microbatches idle 0.43 of the slots. Four stages and 32 microbatches idle 0.086. Say a single chat request cannot supply 32 microbatches, so the latency is the sum of the stages. Point the four-GPU millisecond comparison at the drill rather than inventing a second one. Say the inline product wants the tensor-parallelism card, and the full batch can fill this pipe.

**Recap.** Pipeline parallelism splits the model by layers, and a token visits the stages in order. The idle fraction of pipeline slots is `(P − 1) / (M + P − 1)`. Four stages with four microbatches idle 0.43 of the slots. Four stages with 32 microbatches idle 0.086. One chat request pays the bubble. A saturated batch can hide it. The stage-to-stage send is an activation. The wait you feel is the stages adding up.

## Context parallelism and sequence parallelism

Context parallelism and sequence parallelism both cut a sequence across GPUs, and they cut different tensors.

Context parallelism shards the sequence so the attention itself is split. Ring attention, from Liu, Zaharia, and Abbeel in 2023, is one way to pass blocks of keys and values around a ring. It is how a context longer than one GPU's cache gets a home. The KV-cache card's 16 GiB on the 8B, or the 40 GiB on the 70B, is the thing you are splitting. Each GPU holds a slice of the keys and values and passes blocks to the next GPU. The prefill can run. The price is that pass. A short chat that already fits does not need it.

Megatron's sequence parallelism, from Korthikanti and coauthors in 2022, is a different device. Once tensor parallelism is on, the layer norms and the dropout that tensor parallelism would replicate are sharded on the sequence dimension, so those activations are not copied on every GPU. It reduces activation memory next to a tensor-parallel layer. It does not, by itself, split attention across a long prompt. The name is the trap. Saying "we turned on sequence parallelism" does not mean a 131,072-token cache was sharded. Context parallelism is the split that does that. Sequence parallelism is the activation shard that rides along with tensor parallelism.

**Trade-offs.** Context parallelism fits a long cache and adds a pass over the sequence, so a short prompt pays for a mechanism it did not need. Sequence parallelism saves activation memory in a tensor-parallel training or prefill step and does not replace context parallelism for a 128k request. Using the wrong name either wastes a ring on a short chat or fails to fit the cache you thought you had split. Replicas and tensor parallelism remain the tools when the unit of scale is requests or layers, not the sequence.

**Interview.** Give one sentence each. Context parallelism shards the sequence so attention is distributed, and ring attention is the 2023 schedule that passes key and value blocks. Megatron sequence parallelism shards activations that tensor parallelism would have replicated, and it comes from Korthikanti and coauthors in 2022. Say which one you would turn on for a 40 GiB cache that missed the spare on the tensor-parallelism card. The answer is context parallelism, not the Megatron activation shard, and not another replica.

**Recap.** Context parallelism splits a long sequence so each GPU holds part of the attention state. Ring attention, from Liu, Zaharia, and Abbeel in 2023, passes those blocks around a ring. Megatron sequence parallelism, from Korthikanti and coauthors in 2022, shards activations beside tensor parallelism so they are not copied on every GPU. One fits a long cache. The other saves activation memory. They are not two names for the same split.
