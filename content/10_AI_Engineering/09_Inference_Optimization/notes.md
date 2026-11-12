# Inference Optimization

Inference optimization is how a trained model meets a latency, throughput, and cost budget on every request. This topic covers the prefill and decode bottleneck, the clocks and utilization metrics, the accelerator limits, and the model and serving techniques that move those limits. Attention, sampling, and the 70B cache figures stay in Understanding Foundation Models. The latency formula, goodput, and the cost of a call stay in Evaluate AI Systems. Prompt-cache product rules stay in Prompt Engineering. Quantization's accuracy and the 2-byte BF16 weight stay in Finetuning. How a student is trained, and the license on a teacher's outputs, stay in Dataset Engineering.

## Key Points

- **What inference optimization is** — a forward pass on every request, inside a latency, throughput, and cost budget, without dropping the measured quality. The model half changes the checkpoint. The service half changes the schedule.
- **Prefill and decode** — prefill reads the prompt and writes the KV cache. Decode appends one token at a time. Time to first token is mostly the first. The later gaps are the second.
- **Arithmetic intensity and the roofline** — FLOPs per byte, against peak FLOPs over peak bandwidth. The H100 SXM5 ridge is 295.3 FLOPs per byte. A 4,096-wide BF16 projection is intensity 1.00 at one token and 1,365.3 at 4,096 tokens. The crossover is about 345 tokens. The A100 80GB SXM ridge is 153.0. The H200 SXM ridge, half of 1,979 over 4.8 TB/s, is 206.1.
- **Online and batch inference APIs** — interactive calls stay online. Delay-tolerant calls use a batch API. On the docs checked 12 November 2026, OpenAI and Anthropic both charge 50 percent of the synchronous price. OpenAI's only documented window is 24 hours. Anthropic expires unfinished requests at 24 hours and says most batches finish within an hour, which is not an SLO. At the exercise rates, 100,000 documents cost $1,200 synchronous and $600 in batch.
- **TTFT, TPOT, and inter-token latency** — `TTFT + TPOT × (N − 1)`, the same convention as Evaluate AI Systems. An 80-token reply at 1.20 seconds and 0.040 seconds takes 4.36 seconds, a 25 token-per-second decode and an 18.35 token-per-second end-to-end rate. Gaps of 0.030, 0.035, and 0.090 average to 0.052 and still hide a stall.
- **Throughput and goodput** — throughput counts finished requests. Goodput counts the ones that met every latency cap. Attainment is the fraction. In the worked minute, 900 of 1,200 is 0.75 and 720 of 1,800 is 0.40. DistServe uses goodput for the highest rate that still holds a TTFT and TPOT percentile.
- **Model FLOPs utilization** — model FLOPs per second over the chip's peak, rematerialization excluded. PaLM 540B reached 46.2 percent MFU on 6,144 TPU v4 chips, and 57.8 percent hardware FLOPs utilization with rematerialization. A bandwidth-saturated BF16 Llama 3 8B decode on an H100 SXM5 uses 0.339 percent of the dense BF16 peak.
- **Model bandwidth utilization** — bytes moved per second over the SKU's peak HBM bandwidth. The weight-only roof of 208.6 tokens a second is MBU 1. High MBU and tiny MFU is a healthy decode. Low MBU means the bytes are not coming from HBM.
- **What an accelerator is** — a parallel numeric chip. GPU tensor cores and a TPU systolic array are the two you will meet. A TPU v4 chip peaks at 275 TFLOPS of BF16 or INT8, and its ridge is 229 FLOPs per byte. FP8 tensor cores are Hopper, not A100.
- **FLOPs and number formats** — the H100 SXM5 dense BF16 peak is 989.4 TFLOPS in the architecture paper, and the datasheet's starred line is 1,979 with 2:4 sparsity. Bandwidth is 3.35 TB/s and TDP is up to 700 W. The H100 PCIe card is 756 TFLOPS dense BF16 in that paper, 2 TB/s, and 300 to 350 W. The H200 SXM table keeps the 1,979 sparse line, lists 141 GB at 4.8 TB/s, and is still marked preliminary. Half of 1,979 over 4.8 TB/s is a ridge of 206.1. The A100 80GB SXM is 312 TFLOPS dense BF16, 2,039 GB/s, and 400 W, with no FP8. SXM5 compute peak grew 3.17× and bandwidth 1.64× against that A100. The PCIe card's bandwidth is 0.98× that A100's.
- **Memory size and bandwidth** — HBM holds the model. Bandwidth sets the decode roof. Llama 3 8B in BF16 is 14.96 GiB, and 3.35 TB/s allows 208.6 tokens a second, or 195.5 once an 8,192-token cache is read. The step is 4.79 ms at the weight-only roof. The datasheet's 128 GB/s PCIe line is bidirectional. One way, at 64 GB/s, the same weights move at 4.0 tokens a second, not 8.0. The H100 PCIe module's 2 TB/s HBM is 124.5. The H200 SXM's 4.8 TB/s is 298.9.
- **Power** — TDP is a cap. Dense BF16 per nameplate watt is 1.41 TFLOPS on the H100 SXM5 and 0.78 on the A100 80GB SXM. HBM per watt is 4.79 GB/s against 5.10. The 11.5 megawatt training figure stays in Understanding Foundation Models. Google Cloud lists a TPU v4 at 90/170/192 W. The system paper's running range is 121/170/192 W, with 90 W idle, and TDP is not applicable. Do not rank 275 TFLOPS over 170 W against a TDP ratio.
- **Quantization** — a group-128 FP16 scale makes 4-bit weights 0.515625 bytes, 3.86 GiB on the 8B, and an H100 SXM5 roof of 809.1 tokens a second, 3.88× the BF16 roof. MFU moves to 1.31 percent. A 2-byte zero-point per group makes the factor 3.76×. A dequant that materializes BF16 weights cancels the roof. Accuracy stays in Finetuning.
- **Pruning** — unstructured sparsity, including SparseGPT and Wanda, can leave a dense HBM read. The 2:4 pattern is what the starred peak assumes. 1,979 is 2.00 times 989.4 only when that kernel runs.
- **Distillation at serving time** — training and the license stay in Dataset Engineering. Llama 3 8B against Llama 3 70B is 8.78× fewer BF16 weight bytes and 2.50× fewer cache bytes per token. The cache ratio is the attention shape, not an automatic result of a smaller N.
- **Speculative decoding** — a draft proposes γ tokens and the target verifies them, preserving the distribution when the residual rejection rule is used. Independent acceptance gives `(1 − α^(γ+1)) / (1 − α)` tokens. The speedup divides by `(γc + 1)` when verification fits in one target step. At a worked α of 0.7, γ of 4, and c of 0.05, one target step yields 2.77 tokens and the speedup is 2.31×. Leviathan and coauthors saw c always under 0.05. A bad draft is a slowdown.
- **Medusa, lookahead, and prompt lookup** — extra heads, n-grams from the same model, or a span copied from the prompt. The target still verifies. Prompt lookup helps when the answer quotes the source. A looser acceptance rule can move the distribution.
- **KV cache size** — the untied Llama 3 8B is 8,030,261,248 parameters and 14.96 GiB in BF16. The cache is 128 KiB a token, 1 GiB at 8,192, and 16 GiB at 131,072. One 128k request is 30.96 GiB. Four are 78.96 GiB. Five are 94.96 GiB. The 70B's 40 GiB stays in Understanding Foundation Models.
- **KV cache quantization and offloading** — a 1-byte packing is 64 KiB a token and 8 GiB at 131,072 tokens, before scales. Four of those caches plus the BF16 weights are 46.96 GiB. At 64 GB/s one way, an 8,192-token BF16 cache takes 16.8 ms to read and a 16 GiB cache takes 268.4 ms. Weight offload does not grow with the prompt. Cache offload does.
- **Multi-query, grouped-query, and sliding-window attention** — 8 key-value heads instead of 32 cut the 8B cache from 64 GiB to 16 GiB at 131,072 tokens. Mistral 7B's window of 4,096 keeps a rolling cache at 0.5 GiB, half of a full 8,192-token cache.
- **FlashAttention** — the score matrix stays on chip. One head at 8,192 tokens would write 128 MiB of BF16 scores against 6 MiB of QKV, 21.3 times. Thirty-two heads together would be 4 GiB. The KV cache remains. FlashAttention-3, from Shah and coauthors in 2024, targets Hopper.
- **PagedAttention** — vLLM's block allocator, from Kwon and coauthors in 2023, stops reserving the maximum length. Ten requests reserved at 8,192 and using 1,024 are 10.00 GiB reserved, 1.25 GiB live, and 8.75 GiB empty. A live token is still 128 KiB.
- **Kernels and compilers** — fusion keeps activations out of HBM. The unfused feed-forward epilogue moves 159,744 bytes against 36,864 fused, a 120 KiB saving next to a 112 MiB gate weight. `torch.compile`, Triton, and TensorRT-LLM are the tools. Batch-1 decode does not become 4.33× faster.
- **The cost of structured outputs** — a schema mask adds compile time to TTFT and a per-token check to TPOT. Outlines, XGrammar, and llguidance build the mask. A draft the grammar rejects lowers speculative acceptance. The output token price does not grow just because the sampler wore a mask. The contract stays in Understanding Foundation Models.
- **Static, dynamic, and continuous batching** — static padding uses 0.40 of the worked decode slots and 0.336 of the worked prefill positions. Dynamic batching adds a timeout. Continuous batching, from Orca, joins and leaves at token boundaries. It does not, by itself, stop a prefill from stalling decode.
- **Disaggregated prefill and decode** — at the H100 SXM5 roofs, a 2,048-token Llama 3 8B prefill is 33.2 ms and a decode step is 4.79 ms, so a 20 ms gap fails if they share the step. DistServe and Splitwise split the pools and optimize goodput. Sarathi-Serve, from Agrawal and coauthors at OSDI 2024, is the same-GPU chunked-prefill alternative.
- **Prompt caching** — reuse the KV cache of an identical prefix. A 4,096-token Llama 3 8B prefix is 0.50 GiB. At the exercise rates, one million calls cost $7,010 uncached and $2,402 cached, a saving of $4,608. On the docs checked 12 November 2026, OpenAI caching is on by default, GPT-5.6 writes are 1.25 times for 30 minutes and reads are 0.1 times on most of those models, and Anthropic's standard read is 0.1 times with a 1.25 times write for 5 minutes. The prefix rule stays in Prompt Engineering.
- **Replica parallelism** — full copies, no gradient all-reduce. Throughput scales. One request's latency does not, and a checkpoint that does not fit still does not fit. Sticky routing keeps a prefix cache.
- **Tensor parallelism** — a Llama 3 70B activation is 16 KiB, 0.018 microseconds at the H100 SXM's printed 900 GB/s NVLink and 0.036 at half of that bidirectional total, plus collective latency. Two H100 SXM5 GPUs leave 28.6 GiB beside the 131.4 GiB weights, and a 40 GiB cache does not fit there.
- **Pipeline parallelism** — the idle fraction is `(P − 1) / (M + P − 1)`. Four stages idle 0.43 of their slots with four microbatches and 0.086 with 32. One chat request pays the bubble.
- **Context parallelism and sequence parallelism** — context parallelism shards attention, and ring attention is the 2023 schedule. Megatron sequence parallelism, from Korthikanti and coauthors in 2022, shards activations beside tensor parallelism. They are not the same split.

## Example

The planning numbers are the H100 SXM5 ridge, the Llama 3 8B cache and decode roof, the MFU of that roof, a speculative-decoding speedup, and a prompt-cache bill. Bandwidths and peaks are the published SKU figures named in the cards. The acceptance rate, the draft cost, and the token prices are worked inputs, not a paper's table and not a rate card. GiB means 1024 cubed bytes.

```python
PARAMS = 8_030_261_248
PER_TOKEN = 2 * 32 * 8 * 128 * 2
BANDWIDTH = 3.35e12
PEAK = 989.4e12
ridge = PEAK / BANDWIDTH
tokens = BANDWIDTH / (PARAMS * 2)
expected = (1 - 0.7 ** 5) / (1 - 0.7)
speedup = expected / (4 * 0.05 + 1)
uncached = 4096 * 1.25 + 512 * 1.25 + 250 * 5
cached = 4096 * 0.125 + 512 * 1.25 + 250 * 5
print(f"{ridge:.1f}")
print(PER_TOKEN // 1024, PER_TOKEN * 8192 // 1024**3, PER_TOKEN * 131_072 // 1024**3)
print(f"{PARAMS * 2 / 1024**3:.2f} {tokens:.1f} {100 * tokens * (2 * PARAMS) / PEAK:.3f}")
print(f"{expected:.2f} {speedup:.2f}")
print(f"{uncached:.0f} {cached:.0f} {uncached - cached:.0f}")
# 295.3
# 128 1 16
# 14.96 208.6 0.339
# 2.77 2.31
# 7010 2402 4608
```

The ridge is 295.3 FLOPs per byte. Llama 3 8B's BF16 cache is 128 KiB a token, 1 GiB at 8,192 tokens, and 16 GiB at 131,072. The weights are 14.96 GiB, the H100 SXM5 weight-only decode roof is 208.6 tokens a second, and that roof uses 0.339 percent of the dense BF16 peak. A worked speculative decode at acceptance 0.7, four draft tokens, and cost 0.05 yields 2.77 tokens and a 2.31× speedup. One million exercise calls with a cached 4,096-token prefix cost $2,402 instead of $7,010. The drills apply the same arithmetic to a chat stall, a 32,768-token fit, an overnight queue, an A100 quantization choice, a draft model, a support-tool prefix, four GPUs on a 70B, and a server whose weights are still on the host. The one-way PCIe ceiling in that last drill is 4.0 tokens a second. Dividing by the printed 128 GB/s instead produces 8.0 and counts both directions.

## Source Chapter

- **Book chapter**: Chapter 9
- **Title**: Inference Optimization

## Book Outline

- Understanding Inference Optimization
  - Inference Overview
    - Computational bottlenecks
    - Online and batch inference APIs
  - Inference Performance Metrics
    - Latency, TTFT, and TPOT
    - Throughput and goodput
    - Utilization, MFU, and MBU
  - AI Accelerators
    - What's an accelerator?
    - Computational capabilities
    - Memory size and bandwidth
    - Power consumption
- Inference Optimization
  - Model Optimization
    - Model compression
    - Overcoming the autoregressive decoding bottleneck
    - Attention mechanism optimization
    - Kernels and compilers
  - Inference Service Optimization
    - Batching
    - Decoupling prefill and decode
    - Prompt caching
    - Parallelism
- Summary

## Status

- `concepts.md` is a study set of 31 cards: what inference optimization is, prefill and decode, arithmetic intensity and the roofline, online and batch inference APIs, TTFT and TPOT and inter-token latency, throughput and goodput, model FLOPs utilization, model bandwidth utilization, what an accelerator is, FLOPs and number formats, memory size and bandwidth, power, quantization, pruning, distillation at serving time, speculative decoding, Medusa lookahead and prompt lookup, KV cache size, KV cache quantization and offloading, multi-query grouped-query and sliding-window attention, FlashAttention, PagedAttention, kernels and compilers, the cost of structured outputs, static dynamic and continuous batching, disaggregated prefill and decode, prompt caching, replica parallelism, tensor parallelism, pipeline parallelism, and context parallelism and sequence parallelism. The key points above are the chapter summary.
- `drills.md` has eight worked drills. The site sets `hasDrills` from the file, so this topic shows a Drills tab.
- The worked figures are planning arithmetic: the H100 SXM5 dense BF16 peak of 989.4 TFLOPS and the datasheet bandwidth of 3.35 TB/s, the A100 80GB SXM datasheet bandwidth of 2,039 GB/s, 2 bytes per BF16 parameter, the untied Llama 3 8B count of 8,030,261,248, and the Llama 3 70B figures already computed in Understanding Foundation Models. Exercise prices, acceptance rates, profiler snapshots, and activation peaks are labeled where they are not derived. A launch replaces them with the current rate card, the SKU you rented, and a measured trace.
- The 70B cache and the `6ND` training estimate stay in Understanding Foundation Models. The latency formula and the goodput definition stay in Evaluate AI Systems. Prompt-cache pricing behavior stays in Prompt Engineering. GPTQ, AWQ, and the accuracy cost of INT4 stay in Finetuning. Distillation's training contract stays in Dataset Engineering.
- Diagrams are not part of this change.

## See also

- [Understanding Foundation Models](../02_Understanding_Foundation_Models/) — the causal transformer, the KV-cache formula, the 70B byte counts, sampling, and the 989.4 TFLOPS dense BF16 peak.
- [Evaluate AI Systems](../04_Evaluate_AI_Systems/) — TTFT, TPOT, goodput, attainment, and the cost of a call. This topic is how those numbers move.
- [Prompt Engineering](../05_Prompt_Engineering/) — the prefix rule, automatic caching, breakpoints, and the write-versus-read price shape.
- [Finetuning](../07_Finetuning/) — 2 bytes per BF16 parameter, GPTQ and AWQ, and the inference-memory budget this topic serves under.
- [Dataset Engineering](../08_Dataset_Engineering/) — soft targets, sequence-level distillation, and the license limit on training from a teacher's outputs.
- [RAG and Agents](../06_RAG_and_Agents/) — the long retrieved prompt that makes prefill, cache, and prompt lookup matter.
