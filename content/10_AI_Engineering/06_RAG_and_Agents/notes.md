# RAG and Agents

RAG fetches passages at request time so a model can answer from them. An agent is that model in a loop, choosing tools and using what the tools return. This topic covers why retrieval sits beside a long context, how term and vector indexes are built and combined, how chunks, rerankers, query rewrites, and contextual notes change what comes back, and how tables and page images are retrieved. It then covers tools, plans, reflection, failure, evaluation, and memory. Cosine and the embedding models stay in Evaluation Methodology. Component scores and grounded answers stay in Evaluate AI Systems. Context cost, indirect prompt injection, and the tool boundary stay in Prompt Engineering. The inverted index, BM25's single-term saturation, and index lag stay in Search Autocomplete and Information Retrieval.

## Key Points

- **Why retrieve** — a long context holds a document the user already pasted. A permissioned corpus that changes wants an index. Lewis and coauthors, 2020, paired a trained BART generator with retrieved Wikipedia passages. A product page does not tell you whether the vendor also trains. A missed page is an abstention or an answer from the weights. Permissions are applied before the prompt.
- **RAG architecture** — an index, a retriever, and a generator. The index is a copy, with the lag and refresh of a search index. Log the query, the passage ids, and the draft, because an empty retrieval and a contradicted passage are different failures.
- **Term-based retrieval** — an inverted index plus TF-IDF or Lucene BM25. On the three-chunk exercise, Lucene BM25 with `k1` 1.2 and `b` 0.75 ranks "refund policy" first at 0.9984. Raw TF-IDF ranks the chunk that repeats "refund" first at 1.2164. Textbook idf is -0.5108 here and ranks the shipping chunk first. Elasticsearch and OpenSearch default to Lucene BM25. The postings merge and the single-term saturation stay in the search topic.
- **Embedding-based retrieval** — dense neighbors, exact or approximate. DPR, 2020, trained two encoders. E5 uses one model with a query prefix and a passage prefix. HNSW (`efSearch`, `efConstruction`), IVF (`nprobe`), product quantization, ScaNN, and locality-sensitive hashing are the index choices. LSH here hashes vectors. The Deduplicating data card's LSH hashes shingles. HNSW keeps full vectors plus links. IVF, product quantization, and ScaNN train. pgvector has exact scan, IVFFlat, and HNSW, and not a product-quantization index. Index recall is not task recall.
- **Comparing retrieval algorithms** — on exercise ranks 1, 4, and 8, mean recall at 5 is 0.6667, mean precision at 5 is 0.1333, and MRR is 0.4583. Linear-gain NDCG on a separate list is 0.9639. RAGAS context precision and context recall are reference-based. They are not this card's precision at k and recall at k. ANN indexes are also compared on queries per second, build time, and index size. A retrieval choice still has to name mechanism, scale, index time, latency, price, and access control. Generation quality is a different score.
- **Combining retrieval algorithms** — do not add a BM25 score to a cosine. Cosine is in [-1, 1], and Elasticsearch's cosine score is often in [0, 2]. Reciprocal rank fusion, `1 / (60 + rank)`, fuses the exercise lists into A, C, B, D. Two hits at rank 62 tie one hit at rank 1. Elasticsearch's `rank_constant` defaults to 60, and the 8.19 guide defaults the rank window to 10. A sequential pool cannot recover a passage the first stage dropped.
- **Chunking strategy** — 400 articles of 1,200 tokens, windows of 300 and stride 250, become 2,000 chunks and 12,288,000 bytes of float32 vectors at 1,536 dimensions, 11.71875 MiB. Overlap stores 560,000 tokens against 480,000 source tokens. An exercise graph of 32 links per chunk is 256,000 bytes. A split rule wants a section chunk or a parent, not a paste of the corpus.
- **Reranking** — a cross-encoder such as an MS MARCO MiniLM or a bge-reranker, or a hosted reranker such as Cohere Rerank, orders a short candidate list. ColBERT stores a vector per token and scores with MaxSim. None of them can see a passage the first stage missed. The score is an order, not a grounding check.
- **Query rewriting** — resolve follow-ups and split compound questions before search. HyDE, Gao and coauthors 2022, embeds a hypothetical answer. The hypothetical can retrieve a policy it invented. The passage that comes back is the source.
- **Contextual retrieval** — prepend a situating note, usually 50 to 100 tokens in Anthropic's description, then index it with BM25 and with embeddings. Their 19 September 2024 write-up defines top-20 failure as one minus recall at 20. The highlighted setup moved 5.7 percent to 3.7 percent, then 2.9 percent with contextual BM25, then 1.9 percent with those two plus the Cohere reranker. A bare "14 days" shares no term with "headphone return" until the note adds those words. A wrong note poisons both indexes.
- **Multimodal RAG** — captions and OCR drop what they fail to read. CLIP, Radford and coauthors 2021, is one vector per image. ColPali, Faysse and coauthors 2024, embeds page patches and matches them with ColBERT's MaxSim. The generator has to be able to read what you retrieved.
- **RAG with tabular data** — a small rate table can be a chunk. A warehouse question is text-to-SQL: one read-only statement, known columns, the caller's permissions, then the rows. Spider and BIRD stay on the functional-correctness card. An empty result from the wrong filter is not "zero."
- **What an agent is** — an environment, tools, and a planner in a loop. One retrieval and one draft is RAG. A model that chooses the next tool is an agent. The step cap has to be able to stop when the model does not.
- **Knowledge tools** — search returns untrusted text. Permissions are applied before the prompt. A second search does not refresh a stale index. An instruction inside the page is indirect prompt injection.
- **Capability tools** — a calculator or a test interpreter does work the model should not fake. The sandbox, the timeout, and the network policy are code. The observation you keep is the exit code or the number, not an unfiltered log.
- **Write tools** — a refund, a sent message, or a merge is a proposal until the program recomputes the arguments. Irreversible actions wait for a person. An idempotency key stops a retry from applying the change twice, including when the notification fails after the write succeeds.
- **Planning, then checking, then acting** — plan-and-execute writes the steps, then acts. ReWOO, Xu and coauthors 2023, writes the plan before observations return. A frozen plan misses tool errors. A replan can be steered by them. The model agreeing with its own plan is not the check.
- **Foundation models as planners** — they draft fluent steps and they invent tools. A plan that names `issue_refund` when that tool was not offered is already illegal. Planning in the classical sense is search and backtracking, which an autoregressive sample does not do unless a tool can undo. A reinforcement-learning policy learns one environment from reward. A foundation model plans from the context you just handed it. A classical planner is sound only relative to an action model you wrote down.
- **Plan generation and control flow** — function calling, in hosted APIs since June 2023, returns a name and arguments. A plan of exact calls can be validated. A plan in prose needs a translator, and that translator has to be redone when the tool names change. Toolformer, Schick and coauthors 2023, finetunes the habit of inserting calls and still does not know today's wiki. MCP, November 2024, lets a separate server advertise tools and does not make them safe. Independent reads can run together. A draft waits. A retry has a cap. The host owns that control flow.
- **Reflection and error correction** — ReAct, Yao and coauthors, ICLR 2023, feeds the tool's real observation back. Reflexion, Shinn and coauthors 2023, stores a verbal note and can store a wrong one. A changed argument is a repair. An identical call is a repeat the host stops.
- **Tool selection** — the description is a prompt, including when not to call the tool. Fewer tools on one entry point are easier to describe. Chameleon plots tool transitions in the programs its planner emitted. The graph is a measurement, not a selector. Voyager stores a successful program as a skill and retrieves it. Ablation, not a hunch, decides whether a longer menu selects worse.
- **Planning failures** — an illegal step, the wrong goal, or a loop that never stops. The tool does not have to run. The allow-list, the plan checker, and the step cap are the fixes. A thought with no observation is not a success.
- **Tool failures** — an allowed, well-typed call can still name the wrong record, time out, read a stale index, or return an instruction. A schema check is not evidence you touched the right record.
- **Efficiency failures** — at the exercise prices of $0.50 and $2.00 per million tokens, a six-step loop with a growing context is $684.00 per 100,000 tasks, against $140.00 for one retrieve-then-answer call. The reply is paid as output and then, with the observation, as input. Parallel tools shrink the bill only when they remove a model call.
- **Compounding error in agents** — independent per-step accuracy multiplies. Ten steps at 0.95 succeed about 0.599 of the time, ten at 0.99 about 0.904, and ten at 0.90 about 0.349. Agents need a stronger model and fewer steps. A write raises the stakes. Verification, a checkpoint, human approval, and reflection on a failed read are how a task beats the product. The product is already the case where a miss is not repaired. A single-call demo is not the conditional rate inside the trace.
- **Agent evaluation** — score the steps and the final state. SWE-bench uses repository tests, and SWE-bench Verified is the 500-instance subset from August 2024. WebArena uses website state. τ-bench uses the database after a policy-bound conversation. In that paper, gpt-4o function calling is about 61 percent pass^1 on retail and about 35 percent on airline, with retail pass^8 near 25 percent. GAIA, 2023, scores short answers; that paper's humans scored 92 percent and GPT-4 with plugins scored 15 percent. pass^k requires every trial to succeed. On an exercise of 5 successes in 8 trials, pass^3 is 0.1786 and pass@3 is 0.9821.
- **What an agent remembers** — weights, the context window, and an external store. Memory keeps a later turn consistent with a commitment already made, and it keeps an order id exact when a summary would paraphrase it. ChatGPT memory, shipped in 2024, can save a fact because the person asked or because the model decided to, and the person can review and delete it. MemGPT, Packer and coauthors 2023, pages with tool calls. Letta is the continuation. A stored sentence is not a permission.
- **Managing agent memory** — summaries drop fields, so fields a tool will act on stay structured. On an 800-token budget the three notes sum to 950. Oldest-first eviction drops the allergy. A pin keeps it. Pinning every note leaves the prompt at 950 on purpose. Conflicting values wait for a person before a write tool uses them.

## Example

The numbers that come up in a design review are a BM25 score against a TF-IDF score, a recall and an MRR, and the bill for a six-step loop. The corpus, the ranks, the token counts, and the prices are exercises. A launch replaces them with the index you built, judgments on your questions, and the provider's current rate card.

```python
import math


def bill(calls: int, input_tokens: int, output_tokens: int) -> float:
    return calls * input_tokens / 1_000_000 * 0.50 + calls * output_tokens / 1_000_000 * 2.00


inputs = [800 + step * 400 for step in range(6)]
ranks = (1, 4, 8)
print(f"{math.log(1 + (3 - 2 + 0.5) / (2 + 0.5)):.4f}")
print(f"{math.log((3 - 2 + 0.5) / (2 + 0.5)):.4f}")
print(f"{sum(1.0 if rank <= 5 else 0.0 for rank in ranks) / 3:.4f} {sum(1 / rank for rank in ranks) / 3:.4f}")
print(f"{bill(100_000, sum(inputs), 120 * 6):.2f} {bill(100_000, 2_000, 200):.2f}")
# 0.4700
# -0.5108
# 0.6667 0.4583
# 684.00 140.00
```

Both query terms in the three-chunk corpus have Lucene idf 0.4700. The textbook idf on the same counts is -0.5108, and the term-based card shows that sign flip ranking the shipping chunk first. Mean recall at 5 is 0.6667 and MRR is 0.4583 when the gold chunks sit at ranks 1, 4, and 8. The six-step agent is $684.00 per 100,000 tasks at the exercise prices, against $140.00 for one retrieve-then-answer call. The drills apply the same separation of lists, chunks, and tools to a code search box, a documentation section, a latency budget, a pull-request count, a stuck search, a booking, a calendar tool menu, and a timezone conflict.

## Source Chapter

- **Book chapter**: Chapter 6
- **Title**: RAG and Agents

## Book Outline

- RAG
  - RAG Architecture
  - Retrieval Algorithms
    - Term-based retrieval
    - Embedding-based retrieval
    - Comparing retrieval algorithms
    - Combining retrieval algorithms
  - Retrieval Optimization
    - Chunking strategy
    - Reranking
    - Query rewriting
    - Contextual retrieval
  - RAG Beyond Texts
    - Multimodal RAG
    - RAG with tabular data
- Agents
  - Agent Overview
  - Tools
    - Knowledge augmentation
    - Capability extension
    - Write actions
  - Planning
    - Planning overview
    - Foundation models as planners
    - Plan generation
    - Reflection and error correction
    - Tool selection
  - Agent Failure Modes and Evaluation
    - Planning failures
    - Tool failures
    - Efficiency
- Memory
- Summary

## Status

- `concepts.md` is a study set of 28 cards: why retrieve, RAG architecture, term-based retrieval, embedding-based retrieval, comparing retrieval algorithms, combining retrieval algorithms, chunking strategy, reranking, query rewriting, contextual retrieval, multimodal RAG, RAG with tabular data, what an agent is, knowledge tools, capability tools, write tools, planning then checking then acting, foundation models as planners, plan generation and control flow, reflection and error correction, tool selection, planning failures, tool failures, efficiency failures, compounding error in agents, agent evaluation, what an agent remembers, and managing agent memory.
- `drills.md` has eight worked drills. The site sets `hasDrills` from the file, so this topic shows a Drills tab.
- The worked figures are planning arithmetic: a three-chunk Lucene BM25, textbook BM25, and TF-IDF, recall at 5 and MRR, reciprocal rank fusion, a chunk count and an index size, a six-step bill at the exercise prices of $0.50 per million input tokens and $2.00 per million output tokens, and an 800-token eviction. A launch replaces them with a measured index, judgments on your questions, and the provider's current rate card.
- Embeddings and cosine stay in Evaluation Methodology. Component and grounding scores stay in Evaluate AI Systems. Context cost, indirect prompt injection, and the system-level tool boundary stay in Prompt Engineering. The inverted index, BM25's single-term saturation, and index lag stay in Search Autocomplete and Information Retrieval.
- Diagrams are not part of this change.

## See also

- [Introduction to Building AI Applications with Foundation Models](../01_Introduction_to_Building_AI_Applications_with_Foundation_Models/) — prompting, retrieval, and finetuning as the three levers, and a person on any action that moves money.
- [Understanding Foundation Models](../02_Understanding_Foundation_Models/) — the KV cache behind a long context, and the structured outputs a function call depends on.
- [Evaluation Methodology](../03_Evaluation_Methodology/) — embeddings and cosine, and functional correctness for text-to-SQL, SWE-bench, and pass@k.
- [Evaluate AI Systems](../04_Evaluate_AI_Systems/) — scoring retrieval, tool arguments, and the task separately, and local consistency against a retrieved page.
- [Prompt Engineering](../05_Prompt_Engineering/) — context efficiency, indirect prompt injection, and the system-level defenses an agent tool has to sit behind.
- [Finetuning](../07_Finetuning/) — when a behavior should live in the weights, including a model trained to call tools, which still does not replace a wiki that changes.
- [Search Autocomplete and Information Retrieval](../../09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/) — the inverted index, BM25's single-term saturation, and the lag between a committed document and a searchable copy.
- [Payment and Financial Systems](../../09_System_Design_Interview/23_Payment_and_Financial_Systems/) — the idempotency key that keeps a retried charge from billing twice.
