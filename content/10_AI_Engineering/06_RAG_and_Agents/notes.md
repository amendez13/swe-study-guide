# RAG and Agents

RAG fetches passages at request time so a model can answer from them. An agent is that model in a loop, choosing tools and using what the tools return. This topic covers why retrieval sits beside a long context, how term and vector indexes are built and combined, how chunks, rerankers, query rewrites, and contextual notes change what comes back, and how tables and page images are retrieved. It then covers tools, plans, reflection, failure, evaluation, and memory. Cosine and the embedding models stay in Evaluation Methodology. Component scores and grounded answers stay in Evaluate AI Systems. Context cost, indirect prompt injection, and the tool boundary stay in Prompt Engineering. The inverted index, BM25's single-term saturation, and index lag stay in Search Autocomplete and Information Retrieval.

## Key Points

- **Why retrieve** — a long context holds a document the user already pasted. A permissioned corpus that changes wants an index. Lewis and coauthors, 2020, paired a BART generator with retrieved Wikipedia passages. A missed page is an abstention or an answer from the weights. Permissions are applied before the prompt.
- **RAG architecture** — an index, a retriever, and a generator. The index is a copy, with the lag and refresh of a search index. Log the query, the passage ids, and the draft, because an empty retrieval and a contradicted passage are different failures.
- **Term-based retrieval** — an inverted index plus TF-IDF or BM25. On the three-chunk exercise, Lucene BM25 with `k1` 1.2 and `b` 0.75 ranks "refund policy" first at 0.9984. Raw TF-IDF ranks the chunk that repeats "refund" first at 1.2164. Elasticsearch and OpenSearch default to BM25. The postings merge and the single-term saturation stay in the search topic.
- **Embedding-based retrieval** — dense neighbors, exact or approximate. DPR is the 2020 dual encoder. HNSW (`efSearch`), IVF (`nprobe`), and product quantization are the index choices, in FAISS, pgvector, a vector database, or Elasticsearch and OpenSearch kNN. Index recall is not task recall. A new embedding model rewrites the index.
- **Comparing retrieval algorithms** — on exercise ranks 1, 4, and 8, mean recall at 5 is 0.6667, mean precision at 5 is 0.1333, and MRR is 0.4583. Linear-gain NDCG on a separate list is 0.9639. Latency, query cost, and the cost of updates sit beside those numbers. Generation quality is a different score.
- **Combining retrieval algorithms** — do not add a BM25 score to a cosine. Reciprocal rank fusion, `1 / (60 + rank)`, fuses the exercise lists into A, C, B, D. Elasticsearch's `rank_constant` defaults to 60. A sequential pool cannot recover a passage the first stage dropped.
- **Chunking strategy** — 400 articles of 1,200 tokens, windows of 300 and stride 250, become 2,000 chunks and 12,288,000 bytes of float32 vectors at 1,536 dimensions, 11.71875 MiB. Overlap stores 560,000 tokens against 480,000 source tokens. A split rule wants a section chunk or a parent, not a paste of the corpus.
- **Reranking** — a cross-encoder such as Cohere Rerank, an MS MARCO MiniLM, or a bge-reranker orders a short candidate list. It cannot see a passage the first stage missed. The score is an order, not a grounding check.
- **Query rewriting** — resolve follow-ups and split compound questions before search. HyDE, Gao and coauthors 2022, embeds a hypothetical answer. The hypothetical can retrieve a policy it invented. The passage that comes back is the source.
- **Contextual retrieval** — prepend a situating note, then index it with BM25 and with embeddings. Anthropic, September 2024, reported 35 percent, 49 percent, and, with reranking, 67 percent reductions in their top-20 failure rate, from a 5.7 percent baseline to 3.7 percent and 2.9 percent on the first two. A bare "14 days" shares no term with "headphone return" until the note adds those words. A wrong note poisons both indexes.
- **Multimodal RAG** — captions and OCR drop what they fail to read. CLIP, Radford and coauthors 2021, is one vector per image. ColPali, Faysse and coauthors 2024, embeds page patches and matches them with ColBERT-style late interaction. The generator has to be able to read what you retrieved.
- **RAG with tabular data** — a small rate table can be a chunk. A warehouse question is text-to-SQL: one read-only statement, known columns, the caller's permissions, then the rows. Spider and BIRD stay on the functional-correctness card. An empty result from the wrong filter is not "zero."
- **What an agent is** — an environment, tools, and a planner in a loop. One retrieval and one draft is RAG. A model that chooses the next tool is an agent. The step cap has to be able to stop when the model does not.
- **Agent tools** — knowledge tools return untrusted text, capability tools need a sandbox, and write tools need checked arguments and a person on irreversible actions. A retried charge uses an idempotency key. The model's JSON is a proposal.
- **Planning, then checking, then acting** — propose, validate in code, then execute. ReWOO, Xu and coauthors 2023, writes the plan before observations return. A frozen plan misses tool errors. A replan can be steered by them. The model agreeing with its own plan is not the check.
- **Foundation models as planners** — they draft fluent steps and they invent tools. A plan that names `issue_refund` when that tool was not offered is already illegal. A classical planner is sound only relative to an action model you wrote down.
- **Plan generation and control flow** — function calling, in hosted APIs since June 2023, returns a name and arguments. MCP, November 2024, lets a separate server advertise tools and does not make them safe. Independent reads can run together. A draft waits. A retry has a cap. The host owns that control flow.
- **Reflection and error correction** — ReAct, Yao and coauthors 2022, feeds the tool's real observation back. Reflexion, Shinn and coauthors 2023, stores a verbal note and can store a wrong one. A changed argument is a repair. An identical call is a repeat the host stops.
- **Tool selection** — the description is a prompt, including when not to call the tool. Fewer tools on one entry point beat a long overlapping menu. Ablation, not a hunch, decides whether a tool stays.
- **Agent failure modes** — planning, tool use, and wasted steps are different fixes. At the exercise prices of $0.50 and $2.00 per million tokens, a six-step loop with a growing context is $684.00 per 100,000 tasks, against $140.00 for one retrieve-then-answer call. Earlier turns are paid again as input.
- **Agent evaluation** — score the steps and the final state. SWE-bench uses repository tests, WebArena uses website state, and τ-bench uses the database after a policy-bound conversation. pass^k requires every trial to succeed. On 5 successes in 8 trials, pass^3 is 0.1786 and pass@3 is 0.9821. The τ-bench abstract's agents succeeded on fewer than half the tasks, with pass^8 under 25 percent in retail.
- **Agent memory** — weights, the context window, and an external store such as ChatGPT memory or MemGPT, later Letta. Summaries drop fields. On an 800-token budget, evicting the oldest item drops a 200-token allergy and keeps small talk and a trip. A pin keeps the allergy. Conflicting values wait for a person before a write tool uses them.

## Example

The numbers that come up in a design review are a BM25 score against a TF-IDF score, a recall and an MRR, and the bill for a six-step loop. The corpus, the ranks, the token counts, and the prices are exercises. A launch replaces them with the index you built, judgments on your questions, and the provider's current rate card.

```python
import math


def bill(calls: int, input_tokens: int, output_tokens: int) -> float:
    return calls * input_tokens / 1_000_000 * 0.50 + calls * output_tokens / 1_000_000 * 2.00


inputs = [800 + step * 400 for step in range(6)]
ranks = (1, 4, 8)
print(f"{math.log(1 + (3 - 2 + 0.5) / (2 + 0.5)):.4f}")
print(f"{sum(1.0 if rank <= 5 else 0.0 for rank in ranks) / 3:.4f} {sum(1 / rank for rank in ranks) / 3:.4f}")
print(f"{bill(100_000, sum(inputs), 120 * 6):.2f} {bill(100_000, 2_000, 200):.2f}")
# 0.4700
# 0.6667 0.4583
# 684.00 140.00
```

Both query terms in the three-chunk corpus have Lucene idf 0.4700, and the full scores on the term-based card put BM25's winner and TF-IDF's winner on different chunks. Mean recall at 5 is 0.6667 and MRR is 0.4583 when the gold chunks sit at ranks 1, 4, and 8. The six-step agent is $684.00 per 100,000 tasks at the exercise prices, against $140.00 for one retrieve-then-answer call. The drills apply the same separation of lists, chunks, and tools to a catalog, a documentation section, a latency budget, a warehouse, a stuck search, a booking, a tool menu, and a memory conflict.

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

- `concepts.md` is a study set of 22 cards: why retrieve, RAG architecture, term-based retrieval, embedding-based retrieval, comparing retrieval algorithms, combining retrieval algorithms, chunking strategy, reranking, query rewriting, contextual retrieval, multimodal RAG, RAG with tabular data, what an agent is, agent tools, planning then checking then acting, foundation models as planners, plan generation and control flow, reflection and error correction, tool selection, agent failure modes, agent evaluation, and agent memory.
- `drills.md` has eight worked drills. The site sets `hasDrills` from the file, so this topic shows a Drills tab.
- The worked figures are planning arithmetic: a three-chunk BM25 and TF-IDF, recall at 5 and MRR, reciprocal rank fusion, a chunk count and an index size, and a six-step bill at the exercise prices of $0.50 per million input tokens and $2.00 per million output tokens. A launch replaces them with a measured index, judgments on your questions, and the provider's current rate card.
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
