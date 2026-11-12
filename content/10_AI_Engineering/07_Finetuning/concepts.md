## What finetuning is

Finetuning is continued training of a model that already has weights, so those weights pick up a behavior you have examples of. It is the form of transfer learning used on a foundation model: the pretraining run is the transferred start, and the new run moves it.

A base Llama checkpoint continues text. Llama 2-Chat, the Instruct variants, and a classifier head on the last token are later training runs on top of a checkpoint like that. The same idea is older than transformers. A ResNet trained on ImageNet, then trained again on a smaller labeled set, is transfer learning. Freezing the backbone and training only a new head is the cheap version, feature extraction. Updating every weight is full finetuning. BERT finetuned on a GLUE task is that full update on an encoder. A foundation-model finetune is the same choice on a much larger checkpoint: move every weight, move a new head, or move a small added piece and leave the rest frozen. Parameter-efficient methods, later in this topic, are the third option, and they exist because a full update of a 7B model does not fit the way a BERT update did.

Transfer is only as good as the start and the examples. Pretraining has already paid for a representation of language. Finetuning spends a much smaller run to aim that representation at your replies, your labels, or your domain text. It copies what is in the examples, including their mistakes, which is the ceiling the supervised-finetuning card in [Understanding Foundation Models](../02_Understanding_Foundation_Models/) states. The loss you pick is the next card. The decision to spend the run at all is the one after that. Prompting and retrieval stay available. [Introduction to Building AI Applications with Foundation Models](../01_Introduction_to_Building_AI_Applications_with_Foundation_Models/) places finetuning as the third lever, after a prompt and after retrieval, and this topic is the mechanics of that lever.

**Trade-offs.** A full update can move every habit the base model has, and it costs a gradient, an optimizer moment, and a master copy for every parameter. A frozen body with a new head is cheap and can only express what a head can read off the frozen representation. A small added adapter sits between them. Starting from a weak checkpoint, or from examples you have not read, transfers the weakness. The run also ties you to that base: when the base is replaced, the finetune is redone and evaluated again.

**Interview.** Define finetuning as continued training from an existing checkpoint, and name it as transfer learning. Give the three degrees: a new head, a full update, and a parameter-efficient update. Say the demonstrations set the ceiling. Place the lever after prompting and retrieval, and say a finetune does not absorb a document that changes tomorrow.

**Recap.** Finetuning continues training from weights you already have, which is transfer learning applied to a foundation model. A new head, a full update, and a small adapter are the three degrees, and the full update is the expensive one. The examples you train on are the ceiling. Prompting and retrieval remain the earlier levers.

## Finetuning objectives

A finetuning objective is which loss you keep training. The three objectives product teams actually choose are continued pretraining, supervised finetuning, and a preference loss.

Continued pretraining keeps the original next-token loss and changes the data. Code Llama started from Llama 2 and kept training on code. That is continued pretraining: the model gets more of a domain's language before anyone asks it to chat. Gururangan and coauthors, in the 2020 paper "Don't Stop Pretraining," measured the same idea on smaller models. Domain text moves the distribution. It does not, by itself, teach the model to treat a prefix as a question. A base model that has only been continued on your wiki will still continue the wiki.

Supervised finetuning is the instruction step. Each example is a prompt and a target answer, and the loss sits on the answer tokens. The supervised-finetuning card in [Understanding Foundation Models](../02_Understanding_Foundation_Models/) is that loss and that ceiling. This topic does not rebuild it. What this topic adds is the machinery around it: which parameters receive the gradient, how the tensors fit, and which trainer runs the job. A JSON schema the model fills in correctly, a support tone, and a label set are supervised objectives. The demonstrations can be written by people or produced by a stronger model. The second case is distillation, on the base-model card.

Preference finetuning ranks answers the model can already produce. A reward model plus PPO, as in the InstructGPT recipe and Llama 2-Chat, or a direct preference loss such as DPO, as in Llama 3's published post-training, is that rank. The reward-model card and the RLHF card in [Understanding Foundation Models](../02_Understanding_Foundation_Models/) own the Bradley-Terry loss, the KL penalty, and β. Use them. The mechanical point here is smaller. Preference data assumes a model that already answers. If the preferred reply is something the reference model almost never says, supervised finetuning has to move it into that neighborhood first. A preference run is still a finetune: it still stores gradients for whatever you mark as trainable, and it still does not insert this week's help center.

The order follows the gap. Continued pretraining when the domain language is missing. Supervised finetuning when the model does not yet reply in the shape you need. A preference loss when it replies and the worse reply ranks too high. Retrieval when the missing piece is a fact that should stay in a document.

**Trade-offs.** Continued pretraining teaches domain language and spends a large token budget to do it. Supervised finetuning is the shortest path to a reply and copies the average demonstration. Preference optimization improves a ranking and cannot invent a behavior the model never emits. Running all three because the stack diagram shows all three hides which loss the eval actually needed.

**Interview.** Name the three losses and the order. Continued pretraining is still next-token training on new text. Supervised finetuning is prompt and answer, with the loss on the answer, and the details stay on that card. Preference finetuning is a ranking, PPO or DPO, and it comes after the model can answer. Say which one you would run for a label set, for a code domain, and for a model that answers but pads.

**Recap.** Continued pretraining keeps the next-token loss and changes the corpus, which is what Code Llama did on top of Llama 2. Supervised finetuning teaches replies from demonstrations, and the loss mask and the ceiling are the earlier card. Preference finetuning ranks answers the model can already produce, through a reward model or a direct loss such as DPO. The help center still does not move into the weights.

## Reasons to finetune

A reason to finetune is a behavior you have examples of, that a serious prompt does not hold, and that you want on every request without pasting those examples again.

The behavior is the thing to name before the job. A house style for Shopify product text, a Zendesk label set, a tool-call argument that keeps landing in the wrong field, and a refusal policy are behaviors. The structured-output card in [Understanding Foundation Models](../02_Understanding_Foundation_Models/) already places finetuning as the rung you buy when the JSON is valid and the values are still wrong, the schema is stable, and the volume is high. This card is that decision, not the mask and the parser. Those stay there. A schema that changes every sprint is a reason to wait, on the next card.

Volume is the second reason, and it is arithmetic you already know how to do. Few-shot examples sit in every request. The zero-shot and few-shot card in [Prompt Engineering](../05_Prompt_Engineering/) prices that tax. A finetune moves the pattern into the weights so the request can carry the ticket and a short instruction. You keep the finetune when a held-out eval, the pipeline in [Evaluate AI Systems](../04_Evaluate_AI_Systems/), beats the prompt by enough to pay for the training run and the model you now have to version. A smaller model that has learned one task can also be cheaper to serve than a frontier model that re-reads eight examples. That serving win is real only if the small model clears the same bar.

The third reason is a teacher you cannot afford on the request path. A strong model writes the demonstrations, and a smaller model trains on them. Distillation in that form is supervised finetuning whose targets came from the teacher. It belongs here as a reason: you finetune because the behavior already exists in a model you can call offline and does not exist, reliably, in the model you can serve. The base-model card is how you pick the student.

You should already have tried the prompt. Finetuning is the lever you add when that measured prompt stalls, the examples exist, and the behavior is stable enough to be worth a checkpoint.

**Trade-offs.** A finetune holds a stable behavior at a low per-request token cost, and it freezes the behavior you trained. New examples need a new run. A prompt is an afternoon, and at high volume the afternoon becomes the bill. Distillation compresses a teacher onto your task and drops whatever the teacher could do that the demonstrations never showed. Skipping the held-out eval and shipping the checkpoint with the lowest training loss is how an overfit labeler reaches production.

**Interview.** Ask for the behavior, the eval against a prompt baseline, and the volume. If the gap is a fact in a changing document, say retrieval. If the gap is a trailing comma, say a schema mask. If the gap is a tone, a label, or a field the model systematically fills wrong, and the schema will still be here next quarter, say finetune. Mention distillation when the constraint is the model you can serve.

**Recap.** Finetune when a behavior survives a serious prompt, you have demonstrations, and the behavior should apply without those demonstrations in every request. Volume and a smaller student model are the cost reasons. A changing fact, a syntax error, and an unmeasured prompt are not.

## Reasons not to finetune

A reason not to finetune is a gap a cheaper lever still owns, or a constraint the weights cannot meet.

Fresh or private facts are the usual mismatch. A Notion wiki, a Zendesk help center, and a contract that was edited this morning belong in an index. [RAG and Agents](../06_RAG_and_Agents/) is that index. A finetune of yesterday's pages serves yesterday. Putting the pages in the weights also makes them hard to delete: a later request can still echo a sentence you no longer have a document for. Retrieval drops the page from the index. Weights do not have that switch.

Other gaps have a better tool than a gradient. Illegal JSON is a schema mask and a parser, the structured-output card in [Understanding Foundation Models](../02_Understanding_Foundation_Models/). A prompt you have not scored is still an afternoon, and [Prompt Engineering](../05_Prompt_Engineering/) is that afternoon. A few dozen noisy demonstrations will be memorized. A label set or a policy paragraph that changes every week will be stale as soon as the job finishes. A license that forbids the derivative, or forbids the use, ends the plan before the GPU does. The open-weights card in [Evaluate AI Systems](../04_Evaluate_AI_Systems/) is where those terms live. This card only requires you to read them before you train.

The last reason is operational. A finetune is a model you version, reload, and re-score when the base changes. The iterate-and-version card in [Evaluate AI Systems](../04_Evaluate_AI_Systems/) is the discipline. If you have no held-out set, you cannot tell the new base plus the old data from a regression. Training anyway produces a checkpoint nobody can promote.

None of these forbid a finetune later. They forbid it as the first spend, and they forbid it as a store for facts the product has to update or forget.

**Trade-offs.** Refusing the run keeps you on a prompt and an index you can edit today, and it leaves a real behavioral gap in place. Taking the run locks a behavior, spends the GPUs, and starts a model-version obligation. The expensive mistake is a finetune that seemed to work because the training loss fell, on data that was the eval set, for a policy that changed on Monday.

**Interview.** Give the vetoes in the order you would apply them. License, then "is this a fact or a behavior," then "have we scored a prompt," then "will the target still be true when the job ends," then "do we have a held-out set." A wiki in the weights fails the fact test. A trailing comma fails the tool test. A stable house style with a measured prompt gap passes.

**Recap.** Do not finetune facts you need to update or delete, syntax a mask can forbid, or a task you have not yet tried to prompt. Do not finetune on a handful of noisy examples, on a target that changes weekly, or under a license that forbids the derivative. A finetune you cannot score is a checkpoint you cannot promote.

## Finetuning and RAG

Finetuning and retrieval answer different gaps. Retrieval puts information in the request. Finetuning changes how the model behaves when it reads a request.

The split is the three levers in [Introduction to Building AI Applications with Foundation Models](../01_Introduction_to_Building_AI_Applications_with_Foundation_Models/), applied one level down. A return window that changed belongs in the article, and the article belongs in the index from [RAG and Agents](../06_RAG_and_Agents/). A tone, a label taxonomy, a habit of quoting the passage, and a habit of abstaining when the passage is silent are behaviors. An index cannot store a habit. A prompt can ask for the habit, and at volume a finetune can make the habit the model's default so the prompt can stay short.

They combine, and the combination is the production shape more often than either one alone. The index still returns the passage. The model is finetuned to use passages: quote the sentence, abstain when it is absent, fill the schema, keep the company's tone. The original RAG paper trained the generator as well as retrieving. A product can train that behavior with supervised finetuning, or it can leave the generator frozen and put the habit in the prompt. What it cannot do is finetune on answers that ignore the passage and then expect the model to lean on retrieval in production. The demonstrations have to contain the passage and the answer that followed from it. Otherwise the gradient teaches the model that the context is decoration.

A missed page is still a retrieval failure. The finetune does not contain the page. Local consistency against the retrieved text stays the factual-consistency check in [Evaluate AI Systems](../04_Evaluate_AI_Systems/). Score the retrieval and the behavior separately. A fluent label on the wrong article is a retriever problem. A right article quoted with the wrong policy is a generator problem.

| Gap | Where it lives | What you change |
| --- | --- | --- |
| The policy text changed, or the user may not see that document. | The index, with permissions applied before the prompt. | Reindex. A finetune would keep serving the old sentence. |
| The reply has the wrong shape, tone, or label, and you have examples. | The weights, plus a short instruction. | Finetune. An index has nowhere to put a style. |
| The model answers without using the passage you retrieved. | The demonstrations and the prompt. | Train on examples that contain the passage and the answer that follows from it. |

**Trade-offs.** Retrieval stays current and fails open when the search misses. Finetuning holds a behavior and goes stale when the behavior was secretly a fact. Using both adds a training run and an index. Using neither, a long prompt full of policies and examples, is the right first measurement and the wrong steady state at volume. A finetune that bakes in the windows will be confidently wrong the morning the policy changes, and the log will look like a model failure rather than a stale weight.

**Interview.** Sort the failure into information or behavior before you pick the project. Give the combination: retrieve the current article, finetune the habit of quoting it and of abstaining. Say that the training examples have to include the retrieved text, or the model learns to ignore the index. A single accuracy number that mixes retrieval misses and bad tone is the number you refuse to optimize.

**Recap.** Retrieval supplies information at request time. Finetuning changes behavior. A changing policy stays in the index. A stable habit of tone, format, quoting, or abstaining can go in the weights. The usual system does both, and the finetune's examples include the passage so the model keeps reading the index.

## Backpropagation and trainable parameters

Backpropagation is the backward pass that gives every trainable parameter a gradient. It is why a training step stores much more than the weights a forward pass needs.

The forward pass computes the loss. The backward pass applies the chain rule from that loss back to each weight you allowed to change. For a trainable matrix, the gradient is another matrix of the same shape. AdamW, the optimizer almost every finetune actually runs, then keeps a first moment and a second moment, each the same shape again. AdamW is Adam with the weight decay applied separately from the gradient update. The two moments are the memory. The mixed-precision practice that matches the parameters card in [Understanding Foundation Models](../02_Understanding_Foundation_Models/) also keeps an FP32 master copy of each trainable weight, because the BF16 or FP16 compute copy is a coarse place to accumulate a small step. Counted that way, a trainable parameter costs the BF16 weight (2 bytes), the FP32 master (4), the FP32 gradient (4), and two FP32 moments (4 and 4). That is 18 bytes, against 2 bytes to serve the same parameter in BF16. The 18 is an accounting choice, the same one as that card, not a law. A trainer that stores the gradient in BF16, or that skips a master copy, stores less and has a different numerical risk.

A frozen parameter skips the rows that exist only for the update. No gradient, no moments, no master copy. The forward weight remains. Freezing is not free once a trainable parameter sits downstream. The chain rule still needs the activations of the frozen layer so the gradient can reach the trainable one. LoRA adapters in every block, later in this topic, are that situation: the base weights are frozen and the backward still walks every block. A classification head on a frozen body is the opposite. Nothing trainable sits inside the body, so the backward can stop at the head and the body's activations do not have to be kept for a gradient. That is why "we froze 99 percent of the weights" does not tell you the memory until you know where the trainable 1 percent is.

One square matrix is enough to see the jump. Take a 4096 by 4096 weight, the attention projection size in Llama 2 7B. Inference in BF16 is 32 MiB. The 18-byte training state is 288 MiB, nine times the inference weight, before any activation is stored.

```python
HIDDEN = 4096
PARAMS = HIDDEN * HIDDEN
print(PARAMS)
print(f"{PARAMS * 2 / 1024**2:.1f}")
print(f"{PARAMS * 18 / 1024**2:.1f}")
print(18 / 2)
# 16777216
# 32.0
# 288.0
# 9.0
```

Sixteen million parameters is a small slice of a 7B model. The factor of nine is the point. Apply it to every trainable weight and the machine changes, which is the training-memory card.

**Trade-offs.** Training every weight gives every weight a gradient and an optimizer state, which is the full behavior change and the full bill. Freezing a weight removes that state and leaves the activation cost in place whenever a trainable parameter still depends on it. Stopping the backward at a head removes both, and the head can only do what a head can do. Storing less than the 18 bytes, with 8-bit moments or a BF16 gradient, fits more and changes the numerical behavior you then have to measure.

**Interview.** Walk the bytes for one trainable parameter: weight, master, gradient, two moments. Say freezing drops the update state and does not drop activations if the backward still flows through that layer. Contrast a head, where the backward stops, with adapters in every block, where it does not. The 32 MiB versus 288 MiB on a 4096 by 4096 matrix is the figure to put on the board.

**Recap.** Backpropagation stores a gradient the same shape as each trainable parameter, and AdamW stores two moments of that shape. In the mixed-precision accounting, that is 18 bytes against 2 bytes to serve the weight in BF16. A 4096 by 4096 matrix is 32 MiB to serve and 288 MiB to train. Frozen weights skip the update state, and they still cost activations when a trainable parameter sits above them.

## Inference memory

Inference memory is the state a GPU holds to answer a request: the weights, the KV cache, and the activations of the forward pass.

The weights are the checkpoint. FP16 and BF16 are 2 bytes a parameter. The untied Llama 2 7B layout is vocabulary 32,000, 32 layers, hidden size 4,096, intermediate size 11,008, no biases, and separate input and output embeddings. That count is 6,738,415,616 parameters, 12.6 GiB in BF16. A whiteboard 7 billion is 13.0 GiB. The parameters card in [Understanding Foundation Models](../02_Understanding_Foundation_Models/) uses the same rounding for a 70B model. Name which count you are holding. A round 7B and this configuration differ by about half a gigabyte, and the half gigabyte matters when the card is full.

The KV cache is the part that grows with the conversation. The attention card in that topic derives it: two tensors, layers, key-value heads, head dimension, bytes, and the tokens so far. Llama 2 7B uses multi-head attention, so it has 32 key-value heads, and the head dimension is 128. Each new token adds `2 × 32 × 32 × 128 × 2 = 524,288` bytes, which is 512 KiB. A 4,096-token context, Llama 2's original length, is exactly 2 GiB. One request is 14.6 GiB before the forward activations: 12.6 of weights and 2 of cache. Eight such requests are 16 GiB of cache and 28.6 GiB with the weights. The weights are paid once. The cache is paid per request.

```python
def llama2_params(layers: int, hidden: int, intermediate: int, vocab: int = 32_000) -> int:
    per_layer = 4 * hidden * hidden + 3 * intermediate * hidden + 2 * hidden
    return layers * per_layer + hidden + 2 * vocab * hidden


PARAMS = llama2_params(32, 4096, 11008)
PER_TOKEN = 2 * 32 * 32 * 128 * 2
CACHE = PER_TOKEN * 4096
WEIGHTS = PARAMS * 2
print(PARAMS)
print(PER_TOKEN, PER_TOKEN // 1024)
print(CACHE // 1024**3)
print(f"{WEIGHTS / 1024**3:.1f}")
print(f"{(WEIGHTS + CACHE) / 1024**3:.1f}")
print(f"{(WEIGHTS + 8 * CACHE) / 1024**3:.1f}")
# 6738415616
# 524288 512
# 2
# 12.6
# 14.6
# 28.6
```

Activations are the third term, and they behave differently from the cache. During decode they are the workspace for one new token. During prefill they scale with the prompt and the batch, and the peak can rival the weights. Quantizing the weights, on the quantization cards, shrinks the first term only. The cache shrinks if you quantize the cache or if the model uses fewer key-value heads, which is the grouped-query point on the attention card. Eight concurrent 4,096-token requests already miss a 24 GB card before a weight is quantized. [Inference Optimization](../09_Inference_Optimization/) is the serving work, the kernels and the paging, once this budget is the constraint.

**Trade-offs.** A longer context and more concurrent requests raise the cache linearly and do nothing to the quality of a short request. Quantizing weights fits a larger model and adds a rounding error the accuracy cards cover. Keeping BF16 weights is simpler and, at 12.6 GiB plus cache, spends the card on a 7B model that a 4-bit checkpoint would have left room to batch. Counting weights and forgetting the cache is how a capacity plan passes a single demo request and fails the concurrent ones.

**Interview.** Separate the three terms and say which one the question is about. Compute the Llama 2 7B cache from the formula rather than quoting a screenshot: 512 KiB a token, 2 GiB at 4,096 tokens, 14.6 GiB with the BF16 weights, 28.6 GiB at eight of those requests. Say quantization changes the weight bytes and a grouped-query model changes the cache bytes. Activations spike at prefill and shrink at decode.

**Recap.** Inference memory is weights plus KV cache plus forward activations. The untied Llama 2 7B layout is 6,738,415,616 parameters and 12.6 GiB in BF16. Its cache is 512 KiB a token, 2 GiB at 4,096 tokens, so one request is 14.6 GiB before activations and eight requests are 28.6 GiB. The weights are paid once. The cache is paid per live request.

## Training memory

Training memory is the inference state plus everything the update needs: gradients, optimizer state, and the activations the backward pass will reuse or recompute.

Use the 18-byte accounting from the backpropagation card, the same one as the parameters card in [Understanding Foundation Models](../02_Understanding_Foundation_Models/). A whiteboard 7 billion parameters is 13.0 GiB of BF16 weights and 117.3 GiB of training state, before activations. The Llama 2 7B configuration, 6,738,415,616 parameters, is 113.0 GiB of that state. One GPU sold as 80 GB holds 80 GiB and does not hold 113. An 8-GPU node of those devices holds 640 GiB, the node from the parameters card. Ordinary data parallel does not turn that node into 640 GiB of room. It puts a full copy of the state on every GPU, and the copy does not fit. The node fits this finetune when the state is sharded.

ZeRO and FSDP are that sharding. ZeRO, from Rajbhandari and coauthors, partitions optimizer states at stage 1, gradients as well at stage 2, and the parameters as well at stage 3. PyTorch FSDP shards all three, the stage-3 pattern. The GPUs all-gather a layer's weights for the forward and the backward, then free them. The sum of the cards has to cover the 113 GiB plus activations. No single card has to. Tensor and pipeline parallelism split a layer a different way. They are the other tool when a shard still does not fit, and this topic does not build them.

Activations are the term sharding does not remove. Gradient checkpointing, from Chen and coauthors, drops stored activations and recomputes them on the backward pass. On the `6ND` split from the parameters card, the forward is about two of the six, so an extra forward is about a third more compute. That is a planning figure for the recompute, not a benchmark of a trainer. Checkpointing does not shrink the 113 GiB. It shrinks the activation term that sits on top of it. Bitsandbytes' 8-bit optimizers shrink a different term, the moments, by storing them in block-wise 8-bit with a scale. Useful, and a different mechanism from sharding.

LoRA and QLoRA change the equation by refusing to train the base. The base stays a forward weight: 2 bytes in BF16, or about 4.127 bits with the QLoRA storage on the training-quantization card. Only the adapters pay 18 bytes. For the query and value adapters at rank 8, 4,194,304 parameters from the LoRA card, the adapter state is 0.07 GiB. The BF16 base plus that state is 12.62 GiB. The 4-bit base plus that state is 3.31 GiB. Activations, the allocator, and fragmentation sit on top of all three numbers. They are not peaks. They are the reason a 7B full finetune is a multi-GPU job and a 7B adapter finetune fits a much smaller machine, provided the sequence and the batch leave room for the backward.

```python
def llama2_params(layers: int, hidden: int, intermediate: int, vocab: int = 32_000) -> int:
    per_layer = 4 * hidden * hidden + 3 * intermediate * hidden + 2 * hidden
    return layers * per_layer + hidden + 2 * vocab * hidden


PARAMS = llama2_params(32, 4096, 11008)
ROUND = 7_000_000_000
LORA = 32 * 2 * 8 * (4096 + 4096)
BITS = 4 + 8 / 64 + 32 / (64 * 256)
print(PARAMS)
print(f"{ROUND * 2 / 1024**3:.1f} {ROUND * 18 / 1024**3:.1f}")
print(f"{PARAMS * 18 / 1024**3:.1f}")
print(f"{LORA * 18 / 1024**3:.2f}")
print(f"{(PARAMS * 2 + LORA * 18) / 1024**3:.2f}")
print(f"{(PARAMS * BITS / 8 + LORA * 18) / 1024**3:.2f}")
# 6738415616
# 13.0 117.3
# 113.0
# 0.07
# 12.62
# 3.31
```

| State | What you store | Llama 2 7B, before activations |
| --- | --- | --- |
| Serve in BF16 | The weights. | 12.6 GiB, plus cache. |
| Full AdamW, 18 bytes | Weight, master, gradient, two moments, for every parameter. | 113.0 GiB. A whiteboard 7B is 117.3 GiB. |
| LoRA on a BF16 base | The base at 2 bytes, and 18 bytes only on the adapters. | 12.62 GiB for query and value at rank 8. |
| QLoRA | The base at about 4.127 bits, and 18 bytes on the adapters. | 3.31 GiB for those same adapters. |

**Trade-offs.** A full update is the most a finetune can change and it does not fit one 80 GiB GPU at this size. Sharding spreads the 113 GiB and spends communication. Checkpointing spends compute to cut activations. Adapter methods cut the optimizer term and leave the activation term, so a long sequence can still exhaust the card. Eight-bit moments sit in between. Stacking every saving at once makes the run hard to debug when the loss misbehaves.

**Interview.** Start from 18 bytes and the question "does each GPU hold a copy." A full Llama 2 7B finetune is 113 GiB of parameter state, so data parallel needs ZeRO or FSDP, and checkpointing is a separate switch for activations. Then give the adapter numbers: about 12.6 GiB if the frozen base stays in BF16, and 3.31 GiB if the base is stored at QLoRA's width, both before activations. Say the 3.31 is not a measured peak.

**Recap.** Full mixed-precision AdamW is 18 bytes a trainable parameter: 117.3 GiB for a whiteboard 7B, and 113.0 GiB for the Llama 2 7B configuration, before activations. That state does not fit one 80 GiB GPU, and extra GPUs help when ZeRO or FSDP shards it. Query and value LoRA at rank 8 adds 0.07 GiB of optimizer state, so the bill is about 12.62 GiB on a BF16 base and 3.31 GiB on a 4-bit base, plus the activations the backward still needs.

## Numerical representations

A numerical representation is how a weight, an activation, or a gradient is written in bits: how many bits, how they split between range and precision, and which real numbers exist at all.

The training-memory card's 18 bytes and the inference card's 2 bytes are this choice. A bit spent on the exponent buys range, the largest and smallest finite values. A bit spent on the mantissa buys precision, how close two nearby values can be. FP32 spends 8 bits on the exponent and 23 on the mantissa. FP16 spends 5 and 10. BF16 spends 8 and 7. BF16 keeps FP32's exponent and gives up mantissa. FP16 keeps more mantissa than BF16 and overflows much sooner. That single swap is why LLM training moved to BF16 on Ampere and later, including a 4090 and an A100. The small updates survive the range. They do not need three extra bits of mantissa as much as they need to avoid overflowing at 65,504.

FP16's largest finite value is `(2 − 2^-10) × 2^15`, which is 65,504. Its smallest positive normal is `2^-14`, about `6.104 × 10^-5`. BF16's largest finite value is `(2 − 2^-7) × 2^127`, about `3.390 × 10^38`, and its smallest positive normal is `2^-126`, about `1.175 × 10^-38`. FP32's maximum is only slightly higher than BF16's, because the extra mantissa bits fill the last fraction of the same exponent. A gradient of `10^-8` is a normal BF16 number. It is smaller than FP16's tiniest subnormal, about `5.96 × 10^-8`, so in FP16 it flushes to zero. The practical consequence in training is loss scaling. Mixed-precision FP16 multiplies the loss so the gradients land inside the FP16 range, unscales before the optimizer, and skips the step if the scaled value overflowed. BF16 usually skips the scale, because the range already matches, and still keeps an FP32 master copy because the 7-bit mantissa is a poor place to accumulate.

```python
print(f"{(2 - 2**-10) * 2**15:.0f}")
print(f"{2**-14:.3e}")
print(f"{(2 - 2**-7) * 2**127:.3e}")
print(f"{2**-126:.3e}")
# 65504
# 6.104e-05
# 3.390e+38
# 1.175e-38
```

The other formats you will be asked to place sit around that pair. TF32 is a tensor-core compute format on Ampere and later, not a storage format: 8 exponent bits and 10 mantissa bits, with the value kept in FP32 memory. A "full FP32" matmul may be running TF32 unless the matmul precision setting says otherwise. FP8, on Hopper, comes as two NVIDIA formats from the FP8 formats paper. E4M3, 4 exponent bits and 3 mantissa bits, max 448, is the one used for weights and activations. E5M2, 5 and 2, max 57,344, is the one used for gradients, which want range more than precision. INT8 and INT4 are not floats. INT8 has 256 codes and INT4 has 16, and a scale, sometimes a zero-point, maps those codes onto the tensor. NF4, on the training-quantization card, places the 16 codes for a normal distribution rather than on a uniform grid.

| Format | Bits, sign plus exponent plus mantissa | Where it shows up |
| --- | --- | --- |
| FP32 | 1 + 8 + 23. Range out to about 3.4e38. | Master weights and Adam moments. |
| TF32 | 1 + 8 + 10 inside the matmul. Stored as FP32. | Ampere and later tensor cores, when FP32 matmuls are allowed to use it. |
| FP16 | 1 + 5 + 10. Max finite value 65,504. | Compute, with loss scaling in training. |
| BF16 | 1 + 8 + 7. FP32's exponent range, less precision. | The usual training and inference compute type on Ampere and later. |
| FP8 E4M3 | 1 + 4 + 3. NVIDIA max 448. | Hopper weights and activations. |
| FP8 E5M2 | 1 + 5 + 2. NVIDIA max 57,344. | Hopper gradients. |
| INT8 | 256 integer codes, plus a scale. | Weight and activation quantization, and 8-bit optimizer moments. |
| INT4 | 16 integer codes, plus a scale. NF4 redistributes those 16 for normal weights. | Weight-only serving, and QLoRA's stored base weights. |

**Trade-offs.** BF16 trains stably and rounds small differences away. FP16 keeps those differences and overflows without a loss scale. FP8 and INT4 cut memory again and need a format matched to the tensor: gradients want range, weights can spend the bits on a careful set of codes. TF32 speeds FP32 matmuls and means a result can move when the precision setting changes. Storing everything in FP32 avoids those questions and spends the 18-byte budget twice over.

**Interview.** Draw the exponent and the mantissa for FP16 and BF16, and give 65,504 against about 3.4e38. Explain loss scaling as the patch for FP16's range, and say BF16 usually does not need it. Place TF32 as compute, not storage. Place INT4 as 16 codes plus a scale, and name NF4 as the normal-distribution version of those 16 codes. Say which format you would store, which you would compute in, and which GPU generation you are assuming.

**Recap.** Range comes from the exponent and precision from the mantissa. FP16 tops out at 65,504 and its smallest positive normal is about 6.1e-5, so training in FP16 needs loss scaling. BF16 reaches about 3.4e38, the FP32 range, with a shorter mantissa, which is why it became the LLM compute format. TF32 and FP8 are compute formats with their own splits. INT8 and INT4 are scaled integers, and 4-bit weights have only 16 codes.

## Inference quantization

Inference quantization rewrites a trained model's numbers into a cheaper representation after training, so serving stores less and moves less.

Post-training quantization, PTQ, does it without a training run. A calibration set, a few hundred passages that look like production, estimates the scales. The result is only as relevant as that set. Calibrating on Wikipedia and serving code is a different rounding than calibrating on code.

Weight-only quantization leaves the activations in BF16 or FP16 and stores the weights in INT8 or INT4. The matmul dequantizes a weight on the fly or uses a kernel that does the equivalent. Compute is still a 16-bit matmul. Memory and memory bandwidth fall. Decode is usually bandwidth-bound, so fewer weight bytes often make it faster. Prefill is more compute-bound, so the same checkpoint can save memory and still spend a similar prefill time. GPTQ, from Frantar and coauthors, is a one-shot weight quantizer. It walks the weights a block at a time and uses a Hessian approximation so the not-yet-rounded weights compensate for the rounding. AWQ, from Lin and coauthors, protects the channels whose activations are large, scaling those salient weights before they are rounded. Both need calibration samples. Neither needs a loss or a backward pass. bitsandbytes' 8-bit and 4-bit inference paths are the other widely used implementation. A group of 128 weights sharing one scale is a common GPTQ and AWQ setting. Smaller groups follow the tensor more closely and store more scales.

Weight-and-activation quantization puts both sides of the matmul in integers so the tensor cores can do an integer multiply. Activations are harder than weights because a few channels are outliers. LLM.int8, from Dettmers and coauthors, keeps those outlier dimensions in 16-bit and quantizes the rest to INT8. SmoothQuant, from Xiao and coauthors, rescales per channel, moving the outlier difficulty from the activations into the weights, so both can sit in INT8. That is a serving kernel decision. [Inference Optimization](../09_Inference_Optimization/) owns the kernel. This card owns the accuracy choice you make before you pick one.

The accuracy cost is not uniform. Chat can look unchanged while arithmetic, code, and rare tokens move, because those depend on small weight differences and INT4 has 16 codes in the group. The output projection and the embedding are where a rounding error becomes a different token, so a common practice is to leave them in higher precision, or to give them a finer scale, and to measure. The measurement is a task slice, not a single perplexity. A math slice and a chat slice can disagree, and the eval pipeline in [Evaluate AI Systems](../04_Evaluate_AI_Systems/) is how you refuse to ship the one that only the chat slice approved.

**Trade-offs.** INT8 weight-only is often close to BF16 and saves about half the weight memory. INT4 saves about three quarters and is the usual serving point, with a real risk on exact strings and on arithmetic. Finer groups and a calibration set that matches traffic buy some of that back and cost bytes and a prep step. Quantizing activations speeds the matmul further and fails first on outlier channels. Skipping the task slice because the demo chat looked fine is how a tutor ships a model that cannot carry a digit.

**Interview.** Separate PTQ from a training run, and weight-only from weight-and-activation. Name GPTQ and AWQ as calibrated weight-only methods, and say what each uses: a Hessian compensation, and activation-aware scales. Name LLM.int8 or SmoothQuant as the activation side. Then say you would score math and extraction beside chat, and that the embedding and the output projection are the matrices you quantize last and measure first.

**Recap.** Inference quantization is a post-training rewrite of the checkpoint into fewer bits. GPTQ and AWQ quantize weights with a calibration set, to INT8 or INT4, and leave activations in 16-bit. Quantizing activations as well needs an outlier strategy such as LLM.int8 or SmoothQuant. INT4 is the memory win that most often moves arithmetic and exact tokens, so those tasks are part of the decision to ship it.

## Training quantization

Training quantization uses low-precision numbers inside the training step, either so the matmul is cheaper or so the finetune fits.

Mixed precision is the ordinary case and is not a 4-bit method. The forward and backward run in BF16 or FP16. The master weights and the AdamW moments stay in FP32. That is the 18-byte row. BF16 is the default on Ampere and later because its range matches FP32, so you usually do not loss-scale. FP16 needs the scale from the numerical-representations card. Hopper adds an FP8 mixed precision, E4M3 for weights and activations and E5M2 for gradients. The worked memory in this topic stays on the BF16-and-FP32 accounting so it matches the earlier chapter. An FP8 run is a different byte count you measure on that GPU.

Quantization-aware training is what you do when post-training quantization misses the bar. The forward pass inserts a fake quantizer, so the loss sees rounded values. The backward pass uses a straight-through estimator, treating the rounding as if its derivative were one, and the underlying weights move to a place that survives rounding. At the end you export real integer weights. QAT costs a training run. PTQ costs a calibration pass. You pay for QAT when the INT4 or INT8 checkpoint fails a task you cannot give up.

QLoRA, from Dettmers and coauthors, is the method that makes a large finetune fit on one GPU. The base weights are frozen and stored in NF4, 4-bit NormalFloat. NF4 places its 16 codes so that a normal distribution fills the bins evenly. It is not a uniform INT4 grid, and the paper finds it more accurate than FP4 and integer 4-bit on the models they measured. The computation dequantizes those weights to BF16 for the matmul. Gradients are computed only for the LoRA adapters, which stay in BF16. The base does not receive an update.

Two further pieces are what make the memory small enough. Double quantization quantizes the quantization scales. With a block of 64 weights, one FP32 scale would add `32 / 64 = 0.5` bits per parameter. QLoRA stores those scales in FP8 with a second block of 256, which is `8 / 64 + 32 / (64 × 256) = 0.126953` bits per parameter. The paper reports 0.127. The saving is 0.373 bits per parameter, 3.03 decimal GB on a 65B model, which the paper calls about 3 GB. The stored base is then about 4.127 bits per parameter, the width used on the training-memory card. Paged optimizers use NVIDIA unified memory so an optimizer spike, the kind gradient checkpointing causes on a long sequence, pages to CPU RAM instead of crashing. The paper reports that this is what made 33B finetunes practical on a 24 GB GPU and 65B finetunes practical on a 48 GB GPU, and that on a 65B run with batch size 16 the paged optimizer matched ordinary Adam's speed because the paging rarely fired. Their headline comparison is a 65B finetune from more than 780 GB down to under 48 GB. That is their measurement, under their batch and sequence, not the 3.31 GiB static figure for Llama 2 7B.

```python
PLAIN = 32 / 64
DOUBLE = 8 / 64 + 32 / (64 * 256)
print(f"{PLAIN:.1f}")
print(f"{DOUBLE:.6f}")
print(f"{PLAIN - DOUBLE:.3f}")
print(f"{65e9 * (PLAIN - DOUBLE) / 8 / 1e9:.2f}")
# 0.5
# 0.126953
# 0.373
# 3.03
```

bitsandbytes is the library that implements NF4, double quantization, and the paged AdamW. A Hugging Face load in 4-bit with NF4, double quantization, and a BF16 compute dtype is the QLoRA storage setup. The adapters are still a LoRA configuration on top.

**Trade-offs.** Mixed precision is the default and it is already in the 18-byte budget. QAT recovers accuracy PTQ lost and spends a full run to do it. QLoRA fits a finetune that otherwise needs a cluster, freezes the base, and can still miss full-finetune quality if the adapters are too narrow a slice of the network. Paged optimizers turn an out-of-memory crash into a slow step, and a slow step on every batch means the sequence is too long for the card. The 65B-on-48GB result is not a promise about your sequence length.

**Interview.** Separate mixed precision, QAT, and QLoRA. Mixed precision is BF16 compute with FP32 state. QAT trains through a fake quantizer. QLoRA freezes an NF4 base, trains BF16 adapters, double-quantizes the scales from 0.5 bits to about 0.127, and pages the optimizer. Give the paper's 65B result as their measured comparison, from over 780 GB to under 48 GB, and keep your own static byte count labeled as weights plus adapter state.

**Recap.** Training quantization means mixed precision, quantization-aware training, or a quantized base. Mixed precision computes in BF16 or FP16 and keeps FP32 master weights and moments. QAT learns weights that survive rounding. QLoRA stores a frozen base in NF4, double-quantizes the scales to about 0.127 bits from 0.5, trains LoRA adapters in BF16, and uses paged optimizers for spikes. The paper's 65B finetune is the result that brought that stack under 48 GB.

## Parameter-efficient finetuning

Parameter-efficient finetuning trains a small added or selected set of parameters and leaves the pretrained weights frozen.

It exists because the training-memory card's 113 GiB is the cost of treating every Llama 2 7B weight as trainable. The behavior you want is often a small direction in that weight space. Houlsby and coauthors showed, on BERT, that a bottleneck inserted into a frozen transformer can carry a task. The methods since then, adapters, soft prompts, IA3, LoRA, and the variants PEFT implements, are different answers to the same question: which small set of new numbers is enough, and can you serve them without a second full model.

Hugging Face PEFT is the library that packages those answers. You wrap a transformers model, mark the base frozen, and train the piece the config names. TRL's supervised and preference trainers sit on top of that wrapper, so an SFT or DPO job can be a LoRA job without a separate backward implementation. The frameworks card is how you choose the trainer. The split inside PEFT that matters for the memory and the serving is the family. Adapter-based methods add parameters inside the block: bottlenecks, low-rank matrices, or a rescaling vector. Soft-prompt methods add parameters to the input the block reads: virtual tokens at the embedding, or a prefix on the keys and values. LoRA is the adapter-based method the next card but one is about, and it is the one you try first unless you already know the task wants a prompt instead of a weight update.

Freezing the base removes the base's gradient and optimizer state. It does not remove a forward pass through the base, and it does not remove activations where the backward still flows. A method whose trainable parameters sit in every layer pays the activation cost of every layer. A soft prompt at the input pays a shorter backward. That difference, not the parameter count alone, is what decides whether a long sequence fits.

**Trade-offs.** A small trainable set fits, finishes, and is a small file to store per task. It can underfit a shift the base barely represents. A full update can make that shift and may not fit. Soft prompts add tokens and latency at serve time. Adapters add a branch unless you can fold them back into the weight, which is LoRA's advantage and not Houlsby's. Several tasks can be several small files on one frozen base, or one merged checkpoint. Both are later cards. Neither is free quality.

**Interview.** Define PEFT as training a small set while the base stays frozen, and tie it to the 113 GiB you are not storing. Name the two families, adapters inside the block and soft prompts at the input, and say Hugging Face PEFT is where those configs live. Then say freezing removes optimizer state and not the activations above a trainable layer. Offer LoRA as the default you would measure, not as a law.

**Recap.** Parameter-efficient finetuning freezes the pretrained weights and trains a small added set, which is how you avoid a 113 GiB optimizer state. Adapter methods put that set inside the block. Soft-prompt methods put it on the input. PEFT is the library, and the backward still costs activations wherever the trainable piece sits.

## Adapters, prefixes, and rescaling

Adapters, prefixes, and rescaling vectors are parameter-efficient methods that add a small trained piece beside a frozen model. They are the family LoRA was simplified from, and they do not all fold back into the original matrix.

A Houlsby adapter is a bottleneck on the transformer's residual stream. After the attention block, and again after the feed-forward block, the hidden state goes down to a small rank, through a nonlinearity, and back up, and a residual adds that branch to the frozen path. The original weights do not move. For a hidden size of 4,096, a bottleneck rank of 64, and 32 layers, the two matrices in each of the two bottlenecks are `32 × 2 × 2 × 4096 × 64 = 33,554,432` parameters, biases aside. That is a real trainable set and it is about half a percent of the Llama 2 7B count. At serve time the branch is still a branch. You pay the extra matmul on every token unless a kernel fuses it. You do not get to add the adapter into the original weight and delete it, because of the nonlinearity and the separate residual path.

```python
print(32 * 2 * 2 * 4096 * 64)
# 33554432
```

A soft prompt does not touch the weight at all. Prefix tuning, from Li and Liang, learns continuous vectors that are prepended to the keys and values at each layer, so every attention lookup sees a learned prefix. Prompt tuning, from Lester, Al-Rfou, and Constant, learns the virtual tokens only at the input embedding. The embedding-only version has far fewer parameters and, in that paper, becomes competitive with full finetuning as the frozen model gets larger. A prefix at every layer has more capacity and consumes context: those virtual tokens occupy KV-cache slots on every request. Neither one is a matrix you can merge into `W` and then serve as the original architecture.

IA3, infused adapter by inhibiting and amplifying inner activations, from Liu and coauthors, is the small rescaling version. It learns vectors that multiply the keys, the values, and the feed-forward activations. The trainable object is a vector per targeted activation, on the order of the hidden width rather than a pair of matrices, which is why IA3 is among the smallest of these methods. It is still a multiply on the activation at serve time, not a merged weight.

You pick among them when LoRA is a poor fit for the constraint. A prefix is a learned context, useful when the task is a shift in conditioning and you want the weights literally untouched. A Houlsby bottleneck is the classical adapter and the one to name in the history. IA3 is the one to name when the parameter budget is tiny. For a generation finetune you intend to serve as a normal checkpoint, the next card is the method that was designed to disappear into `W`.

**Trade-offs.** Bottleneck adapters are expressive and add a permanent branch. Prefixes are a pure conditioning change and they spend context and cache. Prompt tuning is tiny and, in the Lester result, wants a large frozen model before it matches a full update. IA3 is smaller still and can only rescale activations, not rotate them arbitrarily. All four leave you with something to apply at serve time. LoRA, when you can merge it, does not.

**Interview.** Draw the Houlsby bottleneck, down and up with a residual, after attention and after the feed-forward, and give the 33.6 million parameter count for rank 64 on the 7B shape. Separate prefix tuning, at every layer's keys and values, from prompt tuning, at the input only. Say IA3 is a learned rescale. Then say which of them add serve-time work, and why a merged low-rank update does not.

**Recap.** A Houlsby adapter is a down-up bottleneck with a residual after attention and after the feed-forward. At rank 64 on a 32-layer, 4,096-wide model that is 33,554,432 parameters, and it remains an extra branch at serve time. Prefix tuning adds learned keys and values at each layer. Prompt tuning adds virtual tokens only at the input. IA3 multiplies activations by a learned vector. None of these is a matrix you simply add back into the weight.

## LoRA

LoRA is a low-rank update added beside a frozen weight matrix. You train the update, and for a single adapter you can add it back into the matrix and serve the original architecture.

Hu and coauthors freeze `W` and write the change as `BA`, with the inner dimension `r` much smaller than the matrix. For a weight of shape `d × k`, `B` is `d × r` and `A` is `r × k`. The forward pass is the frozen matrix plus a scaled low-rank branch.

```text
h = W x + (alpha / r) B A x
W_merged = W + (alpha / r) B A
```

`alpha` is a constant scale. Dividing by `r` keeps the branch from growing just because the rank grew, which is why the original paper could change rank without retuning the learning rate from scratch. They set alpha to the first rank they try and leave it there. A rank of 8 and an alpha of 16 scale the branch by 2. The QLoRA paper's published run used rank 64 and alpha 16, which scales the branch by 0.25. The scale has to be in the merged matrix. Merging `BA` and forgetting `alpha / r` silently ships a different model.

```python
print(f"{16 / 8:.1f} {16 / 64:.2f}")
# 2.0 0.25
```

The parameter count is `r × (d + k)`. A 4096 by 4096 matrix at rank 8 is `8 × (4096 + 4096) = 65,536` trainable parameters, against 16,777,216 in the frozen matrix, a fraction of 1/256. Query and value projections, the pair the original paper emphasized, across Llama 2 7B's 32 layers, are `32 × 2 × 65,536 = 4,194,304` parameters. Stored in BF16 that adapter file is 8 MiB, next to 12.6 GiB of base weights. The training state for those parameters is the 0.07 GiB on the training-memory card.

```python
HIDDEN = 4096
RANK = 8
MATRIX = HIDDEN * HIDDEN
ADAPTER = RANK * (HIDDEN + HIDDEN)
QV = 32 * 2 * ADAPTER
print(MATRIX)
print(ADAPTER)
print(QV)
print(QV * 2 // 1024**2)
# 16777216
# 65536
# 4194304
# 8
```

Which matrices you adapt matters at least as much as the rank. Query and value are the historical default. Later recipes, and the QLoRA paper's ablation on Llama 7B, find that adapters on all linear layers of the block are what matched full finetuning in that experiment, while raising the rank was not the sensitive knob. The MLP projections are rectangular. Llama 2 7B's intermediate size is 11,008, so a gate, up, or down matrix at rank 8 costs `8 × (11008 + 4096) = 120,832` parameters rather than 65,536. Embeddings and the output projection usually stay frozen, or they dominate the count and the risk. Rank is still a capacity knob. Higher rank can overfit a small set and costs a wider adapter to serve. The rank you ship is the one the held-out eval supports, not the one the paper used.

DoRA, from Liu and coauthors, splits a weight into a magnitude vector and a direction and applies LoRA to the direction. PEFT implements it. It trains slightly more than a plain LoRA and is a variant you can ablate, not a different serving story.

Serving one adapter is the merge. `W_merged` has the original shape, so latency matches the base architecture and the adapter file can be deleted from the hot path. Serving many adapters is the opposite. Fifty tenant-specific updates cannot be merged into one `W` and still be fifty behaviors. The base stays resident and the server applies `BA` for the tenant on that request. S-LoRA, from Sheng and coauthors, is the design that pages many adapters beside the KV cache and batches the low-rank multiplies. vLLM's LoRA support is the serving stack you will meet in practice. The constraints to ask the current server about are which ranks and target modules can share a batch, and how many adapter files stay hot. The KV cache does not shrink because the adapters are small.

**Trade-offs.** A merged LoRA has no extra latency and is one behavior. An unmerged LoRA is a few million parameters and an extra matmul, which is what makes many tenants affordable and what you must not forget to scale by `alpha / r` if you later merge. A higher rank and a wider set of modules raise capacity and raise the chance of fitting the small training set too well. Query and value only can underfit a task the MLP was doing. Merging fifty adapters into one matrix destroys the distinction you stored them to keep.

**Interview.** Write `BA` and the `alpha / r` scale, and compute 65,536 for a 4096 square matrix at rank 8. Say query and value are the historical targets and that all linear layers were the QLoRA paper's finding when the goal was to match full finetuning. Explain merging as adding the scaled product into `W`, and multi-tenant serving as refusing to merge, with S-LoRA and vLLM as the systems that batch the branches. Mention that the 8 MiB file is not the activation memory of training.

**Recap.** LoRA trains `B` and `A` beside a frozen `W`, scaled by `alpha / r`, and can add that product back into `W` for serving. A 4096 by 4096 matrix at rank 8 is 65,536 trainable parameters. Query and value across Llama 2 7B's 32 layers are 4,194,304 parameters, an 8 MiB BF16 file. Many adapters stay unmerged on one base, which is the S-LoRA and vLLM serving pattern. The rank and the target modules are an eval decision, and the QLoRA ablation says the set of modules can matter more than the rank.

## Model merging

Model merging builds one checkpoint from two or more checkpoints that share an architecture, without going back to the training data.

The operation is on the weights. A code finetune and a chat finetune of the same Llama 2 base are two files of the same shape. Merging them produces a third file of that shape. No tokens are read. That is the appeal, and it is the constraint. Different hidden sizes, different layer counts, or different vocabularies are not addable. A LoRA merged into its own base is a legal input. Two full models trained from unrelated initializations are a much weaker one. Methods that add task differences want a shared base so the difference is a direction rather than the whole model.

Three goals come up. Multi-task: one model that keeps a coding skill and a support skill, instead of routing every request to a specialist. On-device: a phone or a laptop holds one set of weights, not a directory of finetunes. Federated: clients train locally, and the server averages updates without collecting the raw examples. FedAvg, from McMahan and coauthors, is that average. It is model merging with a training round attached. The same arithmetic shows up because the constraint is the same. The data cannot, or should not, move.

The three operations in the rest of this section do different things to the tensors. Summing adds or averages parameters that already line up. Layer stacking concatenates blocks along depth to make a deeper model. Concatenation places parameters side by side to make a wider model or a set of experts. Summing needs the same shape. Stacking needs the same hidden size, so one block's output is the next block's input. Concatenation changes a dimension, so something has to map that width back. They are not interchangeable, and only summing is a one-line tensor add.

Merging is not training. If the merged model loses a skill, the fixes are a different merge, a short continued training on data you do have, or serving the specialists separately as adapters. The multi-task card is that choice. mergekit is the practical implementation: linear and spherical interpolation, TIES, DARE, and a passthrough mode for layer arrangements.

**Trade-offs.** A merge is cheap and can be done without the data, which is the point for licensed or private corpora. It can also average away the skill you merged to keep. A joint training run sees every task and costs the run and the data access. Separate adapters keep every skill and cost a router or a tenant id at serve time. Merging across a real architectural difference does not produce a runnable model. It produces a shape error, which is the better failure.

**Interview.** State the constraint first: same architecture, and for task arithmetic the same base. Give the three goals, multi-task, on-device, and federated averaging. Name summing, layer stacking, and concatenation as different tensor operations, not as three names for an average. Say mergekit is where you would run the experiment, and that the eval has to score each skill. A merged model you only scored on chat has not kept the code skill.

**Recap.** Model merging combines checkpoints that share an architecture, without the training data. Summing adds aligned weights. Layer stacking adds depth. Concatenation adds width. The reasons are a single multi-task model, a single on-device file, and a federated average such as FedAvg. The merge still has to pass an eval on every skill you meant to keep.

## Summing weights

Summing merges models by adding or averaging parameters that already have the same shape.

A model soup, from Wortsman and coauthors, averages checkpoints that were finetuned from the same initialization, often several hyperparameter runs of one task. The average can beat the best single run. The weights are the soup. There is no router. The coefficients usually add to one, so the result stays on the scale of the ingredients. `θ = a θ_a + (1 − a) θ_b` is the two-model case.

Task arithmetic, from Ilharco and coauthors, adds differences from a shared base instead of averaging the checkpoints themselves. The task vector is `τ = θ_finetuned − θ_base`. A new model is the base plus a scaled sum of task vectors, `θ_base + λ_code τ_code + λ_chat τ_chat`. Negating a task vector is the paper's way to push a behavior down. Because the vectors are differences, two finetunes that each changed a different coordinate can, in the lucky case, both survive in the sum. When they changed the same coordinate in opposite directions, the sum compromises that coordinate. The compromise is the interference.

TIES, from Yadav and coauthors, tries to drop the interference before the add. It trims small-magnitude entries in each task vector, elects one sign per coordinate by the total magnitude of the vectors that want that sign, and averages only the entries that agree with the elected sign. Coordinates where the tasks disagree are not all written into the result. DARE, from Yu and coauthors, in the paper whose title calls language models Super Mario, drops a random fraction `p` of each task vector and rescales what remains by `1 / (1 − p)`, so the expected update stays the same while many of the small conflicts are gone. DARE is often followed by the TIES sign step. SLERP, spherical linear interpolation, walks the arc between two checkpoints rather than the straight chord. It is a two-model method. It does not elect signs among five tasks. mergekit implements the linear average, SLERP, TIES, and DARE.

A toy pair of coordinates is enough to see the compromise. A code vector that moves the first coordinate by `+0.4` and a chat vector that moves it by `−0.4` sum to zero at equal weight. TIES would keep the sign with the larger total magnitude and drop the other contribution on that coordinate. The toy is the mechanism. It is not a prediction of your HumanEval score.

```python
code = (0.4, 0.0)
chat = (-0.4, 0.6)
added = (code[0] + chat[0], code[1] + chat[1])
print(added)
# (0.0, 0.6)
```

The base has to be the base of both finetunes. Adding `θ_code − θ_llama` to Mistral is not task arithmetic. It is a shape that might even match and a direction that means something else. After a summing merge you have one weight matrix again, so serving is ordinary. You cannot unmerge it per request. If the product needed both specialists intact, the LoRA card's multi-adapter serving was the closer design.

**Trade-offs.** A soup is simple and wants several finetunes of one task from one init. Task arithmetic composes skills and cancels them where they overlap. TIES and DARE spend a trim or a random drop to reduce that cancellation, and they can also drop a small update that was the whole skill. SLERP respects the geometry of two models and does not extend to a pile of task vectors. Every one of these can look fine on the task you happened to score.

**Interview.** Write a task vector as finetuned minus base, and the merged model as the base plus a scaled sum. Give the coordinate that cancels, the `+0.4` against the `−0.4`. Then say what TIES adds, a trim and an elected sign, and what DARE adds, a random drop with a `1 / (1 − p)` rescale. Mention SLERP as the two-model arc. Require the same base, and require an eval per skill.

**Recap.** Summing averages aligned checkpoints, as in a model soup, or adds task vectors, the finetuned weights minus the shared base. Overlapping edits cancel, which is the interference TIES addresses by trimming and electing a sign, and DARE addresses by dropping entries and rescaling the rest. SLERP interpolates two models on an arc. The result is one ordinary checkpoint, and it needs the same base the task vectors were built from.

## Layer stacking

Layer stacking merges by depth. Blocks from one or more checkpoints are placed in a sequence, and the result is a deeper model of the same hidden size.

A transformer block reads a hidden vector and writes a hidden vector of the same width. That is why you can pick up layer 20 of a model and put it where layer 12 was, as long as the width, the attention layout, and the vocabulary line up. You cannot stack a 4,096-wide block on a 5,120-wide block. The residual stream would change shape in the middle of the network. Summing never had that option, because summing requires the two tensors to be the same shape already. Stacking requires a matching interface and produces a new depth.

SOLAR 10.7B, from Kim and coauthors at Upstage, is the public depth up-scaling. They start from a 32-layer model initialized with Mistral 7B weights, duplicate it, drop the last 8 layers of one copy and the first 8 of the other, and concatenate what remains. The depth is `2 × (32 − 8) = 48` layers. The result is the 10.7B checkpoint. Depth up-scaling in that paper is the splice plus continued pretraining. The continued training is part of the method, not a polish step they happened to have budget for. The splice alone is the community frankenmerge. mergekit's passthrough mode is how those layer arrangements are built. The SOLAR paper points at the same kind of splice and then trains. Skipping the continued pretraining leaves you with a deeper model whose middle layers were never trained to follow the layers you placed above them.

```python
print(2 * (32 - 8))
# 48
```

The Apache 2.0 SOLAR checkpoint is a useful existence proof that a depth splice can be the start of a real model. It is not a reason to stack two finetunes you like and ship the stack. A code model's middle layers and a chat model's middle layers do not become a coherent residual stream because the hidden sizes matched. If you stack, the next step is the one SOLAR took: more training, then an eval on the tasks each donor was for.

**Trade-offs.** Stacking builds a deeper model without a pretraining run from scratch, and the deeper model is more expensive to serve than either donor. Continued pretraining repairs the joints and costs tokens. A frankenmerge skips that bill and can be worse than the smaller donor. The hidden size is a hard constraint. A stack you cannot train further is a research artifact until an eval says otherwise.

**Interview.** Explain why equal hidden size is the requirement: each block's output is the next block's input. Walk SOLAR's arithmetic, 32 layers, drop 8 from each end of a duplicated pair, 48 layers, then continued pretraining. Separate that published method from a passthrough frankenmerge that stops at the splice. Say you would not ship the splice as a product model without the further training and a per-task eval.

**Recap.** Layer stacking places transformer blocks in a deeper sequence. The blocks have to share a hidden size. SOLAR 10.7B builds 48 layers from a 32-layer Mistral-initialized model by dropping 8 layers from each end of a duplicated pair, then continues pretraining. A splice without that continued training is a frankenmerge, and mergekit can assemble it. The stack is a starting checkpoint, not yet a model you serve.

## Concatenation

Concatenation merges by width. Parameters are placed side by side so a layer gets wider, or so several copies of a layer become experts that a router mixes back down to the hidden size.

Width is the axis stacking does not touch. Stacking adds blocks and keeps the residual width. Concatenation changes a dimension inside the block. That is why it is not a free tensor operation the way a sum of two identical shapes is. If you concatenate two output projections along the output axis, the next layer receives a wider vector than it was built for. Something has to project that width back, or every downstream matrix has to be widened too. Doing that by hand to two whole checkpoints produces a new architecture, not a drop-in checkpoint.

The version that has a published training recipe is sparse upcycling, from Komatsuzaki and coauthors. A dense feed-forward is copied into several experts, a router is added, and training continues so the copies can specialize. The residual width stays the same because the router mixes the experts back to the hidden size. The SOLAR paper cites that MoE upcycling as the width-wise alternative to its own depth up-scaling. Upcycling spends continued training for the same reason the depth splice does. The copied experts are identical on day one, and they stay identical until the data pulls them apart.

An ensemble that averages two models' probabilities is a different concatenation, at the output rather than in the weights. It keeps two full models resident. It does not produce the one on-device file the merging goals asked for. It is a serving decision, closer to holding two LoRAs than to a merged checkpoint.

You reach for concatenation when the product you want is a wider model or a mixture of experts and you have the continued-training budget. You do not reach for it to combine a code finetune and a chat finetune by this afternoon. Those two are a sum, if they share a base, or two adapters, if the requests are separable. A width change is a new model to train and to serve.

**Trade-offs.** A wider model or a routed set of experts can hold more specialized computation, and it costs a new training run plus the serving complexity of the router. A naive concat of two checkpoints breaks the next layer's shape. An output ensemble keeps both skills and keeps both models in memory. Upcycling from a dense checkpoint you trust is a head start. It is not a substitute for the data the experts need in order to differ.

**Interview.** Separate width from depth. Stacking keeps the hidden size and adds layers. Concatenation changes a dimension, so a projection or a router has to restore the residual. Give sparse upcycling as the concrete method: copy the feed-forward into experts, add a router, keep training. Say an average of two models' logits is an ensemble, not a merged checkpoint. Then say a code skill plus a chat skill is the wrong job for this operation.

**Recap.** Concatenation places parameters side by side and makes a model wider. Unlike a sum, it changes a dimension, so the next layer has to be widened or a router has to mix the new width back down. Sparse upcycling does the practical version: copy a feed-forward into experts, add a router, and continue training. An average of two models' outputs is an ensemble that still stores both models. A pair of same-shaped finetunes is a summing problem, not a width problem.

## Multi-task finetuning and merging

Multi-task finetuning trains one model on several tasks together. Merging and multi-adapter serving are what you do when that joint run is not the right spend.

Joint supervised finetuning concatenates the demonstrations. A code example and a support example land in the same optimizer. The model can trade a little of each skill off against the other while the gradients still see both, and a mixture ratio you choose decides which task's tokens dominate the step. This is the right design when you have the data in one place, you can afford the run, and the product is one model that will see both kinds of request with no router. It is also the design that needs a per-task eval. An average of a code score and a chat score can rise while code falls. That is the aggregation trap in [Evaluate AI Systems](../04_Evaluate_AI_Systems/). This card does not rebuild it. It refuses a single number as the launch gate.

Merging, the summing card, is the alternative when the data cannot sit in one job. The sets may belong to different owners, a license may forbid mixing them, or a federated client may never upload them. You finetune each skill where the data lives, on a shared base, and you add the task vectors. TIES or DARE is the attempt to keep the skills from erasing each other. You still score each skill. If both dropped, the merge failed, and the joint run is the honest next step if the data can move.

Multi-LoRA serving is the alternative when the requests are separable and one weight file is not a requirement. The code completion calls the code adapter. The support chat calls the chat adapter. The base is shared, which is the LoRA card's point about S-LoRA and vLLM. Nothing is averaged, so nothing is cancelled. The cost is operational: adapter routing, the server's batching rules, and several files to version. On a phone that can hold one checkpoint, that cost is the reason to merge instead. In a datacenter that already runs vLLM, it is often the reason not to.

A negative task vector, subtracting a behavior, is the merging operation people reach for when they want a skill gone. It is a blunt instrument. It can turn the behavior down on the eval you measured and leave it on the prompt you did not. Deletion of a fact is still the reason-not-to-finetune problem. Prefer dropping the document from the index.

**Trade-offs.** Joint training usually wins on quality when you can run it, and it needs every dataset and a careful mixture. Merging needs none of the new joint data and can cancel a skill. Separate adapters keep the skills and spend serving complexity. One averaged metric will bless all three while a skill regresses. Continued training after a merge can repair a joint and reintroduces the data requirement the merge was meant to avoid.

**Interview.** Ask whether the data can be in one room and whether one checkpoint is a real constraint. Data together and one model: joint finetuning, scored per task. Data apart and one file: task arithmetic, TIES or DARE, scored per task. Requests separable and a server that can batch adapters: multi-LoRA, no merge. Say an average score is not the gate. Mention that subtracting a task vector is not a deletion guarantee.

**Recap.** Multi-task finetuning trains one model on the combined demonstrations and is the quality path when the data can be together. Merging adds task vectors when the data cannot move and one file is required. Separate LoRA adapters keep every skill when requests can be routed. Each skill needs its own number. An average that hides a regression is not a launch metric.

## Finetuning frameworks

A finetuning framework is the trainer that owns the data, the trainable parameters, the optimizer, and the checkpoint you will actually load.

Hugging Face is the usual open stack. PEFT marks the adapter and freezes the base. TRL runs the objective: supervised finetuning, a reward model, PPO, or DPO, on top of that adapter or on a full model. You stay close to the transformers model definition, which is what you want when the architecture is new and what you pay for in glue code when the job is a standard Llama QLoRA. Axolotl is a YAML recipe layer used widely for that standard job: the base, the chat template, the LoRA targets, the sequence length, and the trainer, in a config you can review. Unsloth replaces kernels in the LoRA and QLoRA step to cut memory and time on a single GPU. Treat its current speed and memory claims as something you read on the release you pin, not as a fixed multiplier. torchtune is PyTorch's own post-training library, with full finetune, LoRA, QLoRA, and distributed recipes expressed in PyTorch rather than in the Hugging Face trainer. It is the one to look at when FSDP is the main problem.

The hosted alternative is an API that never returns weights. OpenAI's fine-tuning API takes a JSONL file of chat messages, runs a job on a base they currently allow, and gives you a model id to call. You pay for the training tokens and then for inference of that id. The eligible bases and whether the job is supervised finetuning or a preference method change, so the current docs are the spec. What does not change is the constraint. You cannot load the result in vLLM, merge it with a LoRA, or inspect the tensors. You can call it. A similar hosted job from another provider has the same shape. Pick it when operating the GPU is the problem you do not want, and the data is allowed to leave.

The choice follows the constraint you already computed. One GPU, a 7B or 13B behavior, and you need the weights: QLoRA through PEFT and TRL, Axolotl, or Unsloth. Many GPUs and a full update: torchtune or FSDP, because the 113 GiB state has to be sharded. No GPUs and no need for the file: the hosted API. A chat template mismatch will make any of these look trained. The loss falls because the model is predicting something, and the something is the wrong wrapping. Apply the template that shipped with the base, the chat-template card in [Prompt Engineering](../05_Prompt_Engineering/).

**Trade-offs.** PEFT and TRL are flexible and easy to assemble wrong. Axolotl is reproducible and one more abstraction to debug. Unsloth is fast on the paths it supports and is not the tool for an architecture it has not written kernels for. torchtune matches a PyTorch distributed stack and is a different set of configs to learn. A hosted API removes the memory problem and removes the checkpoint. The wrong chat template makes every option look like a successful loss curve.

**Interview.** Map the constraint to the tool. Weights on one GPU, QLoRA in PEFT, TRL, Axolotl, or Unsloth. A sharded full finetune, torchtune or FSDP. No weights wanted, the OpenAI fine-tuning API, JSONL in and a model id out. Say you would pin the version and the template. Mention that a falling loss under the wrong template is not a trained chat model.

**Recap.** PEFT and TRL are the Hugging Face stack for adapters and for SFT or DPO. Axolotl is a config-driven recipe around that stack. Unsloth is a kernel-optimized LoRA and QLoRA trainer. torchtune is the PyTorch-native and distributed option. The OpenAI fine-tuning API takes JSONL chat messages and returns a hosted model id, not weights. The template that shipped with the base is part of the training data.

## Choosing a base model

Choosing a base model is deciding which checkpoint the trainer is allowed to move, at which size, and whether a smaller student should learn from a larger teacher.

The progression is the levers you already have, in order. Prompt the strongest model you can call, and score it, which is [Prompt Engineering](../05_Prompt_Engineering/) and the pipeline in [Evaluate AI Systems](../04_Evaluate_AI_Systems/). If the miss is a fact, add retrieval before you train. If the miss is a behavior and you have demonstrations, finetune the smallest open model that might clear the bar, with LoRA or QLoRA, on hardware you can serve as well as train. A 13B checkpoint you can train and cannot serve is the wrong base for a product that has to answer from those weights. If a large model can already do the task and a small one cannot, distill: run the teacher offline, save the answers, and supervise the student on them. DistilBERT, from Sanh and coauthors, is the classic published student, a smaller BERT trained against a larger BERT. For a Llama-sized student the same idea is the supervised objective whose targets came from the teacher. The student learns the teacher's behavior on that set. It does not inherit the teacher's behavior on the questions you never asked.

Full finetuning or continued pretraining is the step after a measured PEFT plateau, not the opening move. Continued pretraining is for a domain whose language the base lacks. Code Llama's start from Llama 2 is the shape of that step, and the domain-model card in [Understanding Foundation Models](../02_Understanding_Foundation_Models/) is the map of code, finance, and medical checkpoints. BloombergGPT was pretrained from scratch. You do not repeat that. You start from a checkpoint you are allowed to train.

License and lineage come before the GPU. The open-weights card in [Evaluate AI Systems](../04_Evaluate_AI_Systems/) has the Llama community terms, Apache 2.0, and the difference between downloadable weights and the open-source definition. SOLAR's Apache 2.0 is why a depth-upscaled checkpoint can be a base other people ship. A finetune inherits the base's terms. Read them before the run, not when the product asks to redistribute the file.

Instruct against base is a task decision. An instruct checkpoint already replies, so a light finetune can add a skill and keep general chat. It can also spend capacity defending a chat style your classifier does not want. A base checkpoint plus supervised finetuning is the cleaner start for a narrow label or a format that fights the chat template. Measure both when the cost of two QLoRA runs is small beside the cost of the wrong default. Match the domain when a domain checkpoint exists and the license fits. A code labeler starts from a code model. A general support labeler usually does not.

Size is the serving number and the training number together. The inference card's 12.6 GiB says a Llama 2 7B in BF16 is a single-GPU serve. A full AdamW update of it is the 113 GiB training state. QLoRA moves the training onto one card and does not change the serving size unless you also quantize for inference. Pick the size whose serving form meets the latency bar and whose training form fits the GPUs you will still have next month.

**Trade-offs.** A larger base has more to transfer and costs more to serve on every request forever. A distilled student is cheap to serve and capped by the demonstrations. An instruct start preserves chat and can fight a narrow output. A base start is easier to shape and has to be taught to answer at all. A domain checkpoint helps when the domain language was the gap and hurts when it was specialized away from your actual task. Changing the base later invalidates the eval series. Pin it.

**Interview.** Walk the progression: prompt, then retrieval if the gap is a fact, then PEFT on the smallest model you can serve, then distillation if a teacher already does the task, then full finetuning or continued pretraining if PEFT plateaued. Name the license check. Separate an instruct start from a base start by what the product must keep. Give DistilBERT as the classic student and a teacher's demonstrations as the LLM version. Refuse a base you can train and cannot serve.

**Recap.** Start by prompting, then retrieve facts, then parameter-efficiently finetune the smallest base you can also serve. Distill a teacher into a student when the large model already has the behavior, the way DistilBERT was trained from BERT. Full finetuning and continued pretraining come after a PEFT plateau, on a checkpoint the license allows. An instruct base keeps chat. A raw base is the cleaner start for a narrow label. The serving size is part of the choice.

## Finetuning hyperparameters

Finetuning hyperparameters are the knobs that decide whether the run moves the right weights: the learning rate, the batch, the number of passes, and how much of the prompt the loss is allowed to see.

The learning rate is the step size on the trainable parameters. A full update moves every weight, so the starting band people sweep is around `10^-5`. A LoRA update moves a small factor, and the starting band is around `10^-4`. These are places to start a sweep, not optima. The QLoRA paper used a constant learning rate after trying linear and cosine schedules. The right value on your data is the one that lowers the held-out loss without a spike. Too high and the loss diverges or turns to NaN, especially in FP16 without a working loss scale. Too low and the loss sits on the floor while the weights barely leave the base. Change the learning rate before you invent a new architecture explanation for a flat curve.

The batch that fits in memory is the microbatch. Gradient accumulation steps the optimizer every several microbatches, so the effective batch is microbatch times accumulation steps times the number of data-parallel GPUs. Activations and the peak memory follow the microbatch, not the effective batch. That is the point of accumulating. A microbatch of 1, accumulated for 8 steps, on 4 GPUs, is an effective batch of 32, and the card only has to hold one example's activations. The linear scaling rule, larger batches with larger learning rates, was measured for large-batch pretraining. A finetune that accumulates only to fit the GPU often keeps the learning rate put and treats the accumulation as a memory tool. Say which one you are doing.

```python
MICRO = 1
ACCUM = 8
GPUS = 4
PROMPT = 100
ANSWER = 20
print(MICRO * ACCUM * GPUS)
print(f"{ANSWER / (PROMPT + ANSWER):.3f}")
# 32
# 0.167
```

Epochs are passes over the training set. Instruction finetunes are often one to a few passes. A small set memorized for five epochs posts a beautiful training loss and a worse eval than the checkpoint from pass one. Early stopping uses the held-out set from [Evaluate AI Systems](../04_Evaluate_AI_Systems/). That set is not training data and not a pool you peek at between every tweak. When the eval loss rises, you keep the earlier checkpoint. When both losses stay high, the problem is the data, the template, or the base, not another epoch.

The prompt loss weight is how much of the prompt tokens enter the loss. A weight of 0 is the mask from the supervised-finetuning card: the model is scored only on the answer. A weight of 1 trains on the prompt too. On a 100-token prompt and a 20-token answer, a weight of 1 makes the answer `20 / 120` of the tokens, about 0.167 of an unweighted token count, so the gradient mostly copies the user. A weight of 0 makes the answer the whole loss. Some trainers then average over the unmasked tokens, which changes the scale of the number you plot. Keep the weight at 0 unless you have a reason to learn the prompt's own language, and do not compare a masked loss to an unmasked loss as if they were the same quantity. Rank, alpha, and the target modules are the LoRA card's knobs. They belong in the same sweep and in the same config file as the learning rate.

**Trade-offs.** A high learning rate finishes or diverges. A large effective batch is a stabler gradient and, without accumulation, a bigger activation spike. More epochs fit a small set and then fit it too well. Training on the prompt teaches the model to continue the user. A sweep of all of these at once is not a sweep. Move one, on a frozen eval.

**Interview.** Define effective batch as microbatch times accumulation times GPUs, and say memory tracks the microbatch. Give the 1 by 8 by 4 example, effective batch 32. Place the learning-rate bands as starting sweeps, `10^-5` for a full update and `10^-4` for LoRA, and say the curve decides. Explain the prompt loss weight with the 100-and-20 split, and tie a weight of 0 to the answer-only mask. Stop on the held-out eval, not on the training loss.

**Recap.** The learning rate is swept, around `10^-5` for a full finetune and around `10^-4` for LoRA, and a spike or a flat line is a reason to change it. Effective batch size is microbatch times accumulation steps times GPUs. One, eight, and four make 32, while the GPU holds one example. A prompt loss weight of 0 trains on the answer only. On a 100-token prompt and a 20-token answer, a weight of 1 lets the prompt dominate. Stop when the held-out loss rises, which is often after a small number of epochs.
