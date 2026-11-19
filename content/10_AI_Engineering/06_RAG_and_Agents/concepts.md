## Why retrieve

Retrieval-augmented generation, RAG, fetches passages at request time and puts them in the prompt so the model can answer from those passages.

A long context can hold the Gmail thread or contract the user just pasted. It does not hold a permissioned help center that changes hourly, and pasting a corpus that fits still spends input tokens on pages the question does not need and buries spans in the middle (the context-efficiency card in [Prompt Engineering](../05_Prompt_Engineering/)). RAG keeps the corpus in an index, fetches a short set, and generates from it. Lewis et al. named the pattern in 2020: a dense Wikipedia index conditioned a BART generator, with RAG-Sequence using one passage for the whole answer and RAG-Token mixing passages during generation. Products such as Notion AI, NotebookLM, Perplexity with citations, and a Zendesk bot answer from a maintained index. Whether they also train the generator is not on the product page; copy the split (a prompted model plus an index you can rebuild), not a guess about their training. Of the three levers in [Introduction to Building AI Applications with Foundation Models](../01_Introduction_to_Building_AI_Applications_with_Foundation_Models/), a finetune freezes yesterday's wiki, a prompt cannot see an unsent page, and retrieval sees the page but fails open on a miss: the model abstains or answers from its weights.

Access control is the other reason for an index: a pasted shared drive will quote documents the asker may not open, so the retriever drops them before they enter the prompt. Citations make answers checkable only when the quote occurs in a retrieved passage (the quote field on the Specifying the output format card in [Prompt Engineering](../05_Prompt_Engineering/)). The passage can still be wrong, stale, or hostile. Local consistency against a bad page is the Factual consistency card in [Evaluate AI Systems](../04_Evaluate_AI_Systems/), and a hostile page is indirect prompt injection, which RAG does not close. Production usually combines a short retrieved set inside a long window. Retrieving hundreds of chunks recreates the middle-of-the-paste failure and bill, and the index is operational work, but facts left only in weights are how yesterday's policy survives an edit.

```text
user pasted it and it fits      -> prompt
large, permissioned, changing   -> retrieval (permissions before the prompt)
retrieval miss                  -> abstain, or an answer from memory
citation not in a passage       -> failure
```

![Why retrieve](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-1-why-retrieve.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 1.*

## RAG architecture

A RAG system has an index built ahead of the question, a retriever that returns passages for the question, and a generator that writes the answer from those passages.

The index is a derived copy of the source of truth. For a help center, it stores chunks, a term index, embeddings, and metadata (title, URL, updated time, readers). It is built offline, so an edit is visible only after reindexing; that lag and refresh pipeline is Full-Text Search Architecture in [Search Autocomplete and Information Retrieval](../../09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/). Online, the retriever runs a term query, a vector query, or both, optionally reranks, and returns passage ids the user may see. The generator is the prompted model, given the instruction, question, and passages. A grounded product returns the ids too, and a checker rejects answers whose required facts are not in them. The check is a program (substring, entailment), not "only use the articles" in the prompt.

The stages fail differently, which is why [Evaluate AI Systems](../04_Evaluate_AI_Systems/) scores each stage and the task. A fluent answer on an empty retrieval is a retriever failure a task score can hide, because it may be right from pretraining today and wrong when the workspace disagrees. A retrieval containing the policy followed by a draft with a different window is a generator failure. A citation pointing at a passage the draft does not follow is a checker failure. Log the query, ids, and draft to separate them. The 2020 paper marginalizes over documents during training; a Zendesk bot usually retrieves, prompts, and checks a frozen model. Say which parts you trained, or a design review talks past itself. A separate index can be rebuilt, permissioned, and swapped when the embedding model changes, at the cost of a second system to keep fresh.

```text
index      chunks + ACL + term index + vectors      log: chunk id, ACL
retriever  term / vector / both, rerank, permit    log: query, passage ids
generator  prompted model + checker                 log: draft, citations
```

![RAG architecture](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-2-rag-architecture.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 2.*

## Term-based retrieval

Term-based retrieval ranks documents by the words they share with the query, using an inverted index and a score such as TF-IDF or BM25.

The inverted index and its postings merge are the Inverted Index card in [Search Autocomplete and Information Retrieval](../../09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/); Elasticsearch and OpenSearch answer lexical search this way. This card is the score. TF-IDF here is raw count times `ln(N / df)`. BM25, the Lucene and Elasticsearch default, keeps an idf, saturates the count so the third "refund" adds less than the first, and normalizes length. Lucene's idf is `ln(1 + (N − df + 0.5) / (df + 0.5))`, with `k1` = 1.2 and `b` = 0.75 by default (`b` = 0 suits short titles of similar length). The single-term saturation picture is the Relevance Ranking card in that topic. Lucene compresses length norms into a byte, so production floats will differ; the ranking is the point.

The exercise has three chunks: A is "refund refund refund," B is "refund policy," and C is "shipping policy," with query "refund policy." Both terms have Lucene idf 0.4700. BM25 ranks B first (0.9984 vs A 0.6960, C 0.4992) because B covers both words and A's repetition is saturated. Raw TF-IDF ranks A first (1.2164 vs 0.8109, 0.4055), which is how a help center ranked by raw counts surfaces a page that hammers "refund" above the policy page. The textbook idf, without Lucene's `1 +`, is −0.5108 for a term in more than half the chunks; the scores turn negative and sorting ranks the shipping chunk first and "refund policy" last. Stemming, synonyms, and stop words change tokens before either formula and are choices you name. Term search is fast and exact, which product codes, error strings, and names need. It cannot match a paraphrase that shares no words, and it does not know "30 days" and "60 days" differ when the surrounding words match. Idf on a small, fast-changing corpus also jumps when one document is added.

```python
import math


DOCS = {
    "A": ["refund", "refund", "refund"],
    "B": ["refund", "policy"],
    "C": ["shipping", "policy"],
}
QUERY = ["refund", "policy"]


def idf_lucene(n: int, df: int) -> float:
    return math.log(1 + (n - df + 0.5) / (df + 0.5))


def idf_classic(n: int, df: int) -> float:
    return math.log((n - df + 0.5) / (df + 0.5))


def bm25_scores(
    docs: dict[str, list[str]],
    query: list[str],
    k1: float = 1.2,
    b: float = 0.75,
    idf=idf_lucene,
) -> dict[str, float]:
    n = len(docs)
    avgdl = sum(len(tokens) for tokens in docs.values()) / n
    df: dict[str, int] = {}
    for tokens in docs.values():
        for term in set(tokens):
            df[term] = df.get(term, 0) + 1
    scores = {}
    for name, tokens in docs.items():
        norm = 1 - b + b * len(tokens) / avgdl
        score = 0.0
        for term in query:
            tf = tokens.count(term)
            if tf == 0:
                continue
            saturation = tf * (k1 + 1) / (tf + k1 * norm)
            score += idf(n, df[term]) * saturation
        scores[name] = score
    return scores


def tfidf_scores(docs: dict[str, list[str]], query: list[str]) -> dict[str, float]:
    n = len(docs)
    df: dict[str, int] = {}
    for tokens in docs.values():
        for term in set(tokens):
            df[term] = df.get(term, 0) + 1
    scores = {}
    for name, tokens in docs.items():
        score = 0.0
        for term in query:
            score += tokens.count(term) * math.log(n / df[term])
        scores[name] = score
    return scores


bm25 = bm25_scores(DOCS, QUERY)
classic = bm25_scores(DOCS, QUERY, idf=idf_classic)
tfidf = tfidf_scores(DOCS, QUERY)
print(f"{idf_lucene(3, 2):.4f} {idf_classic(3, 2):.4f}")
print(f"{bm25['A']:.4f} {bm25['B']:.4f} {bm25['C']:.4f}")
print(f"{classic['A']:.4f} {classic['B']:.4f} {classic['C']:.4f}")
print(f"{tfidf['A']:.4f} {tfidf['B']:.4f} {tfidf['C']:.4f}")
# 0.4700 -0.5108
# 0.6960 0.9984 0.4992
# -0.7564 -1.0851 -0.5425
# 1.2164 0.8109 0.4055
```

![Term-based retrieval](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-3-term-based-retrieval.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 3.*

## Embedding-based retrieval

Embedding-based retrieval ranks passages by the similarity of dense vectors, so a question and a passage can match when they share a meaning and few words.

The vector is the embedding from [Evaluation Methodology](../03_Evaluation_Methodology/) (Sentence-BERT, E5, BGE, Cohere Embed, text-embedding-3; cosine and the negation warning live there). This card is the index that avoids comparing the query with every passage. Dense Passage Retrieval (Karpukhin et al., 2020) is a dual encoder that embeds question and passage separately with two trained encoders. Many current APIs use one model, while E5 marks the sides with query and passage prefixes. Passage vectors are stored, the query vector is computed per request, and the neighbors go to the generator. Exact search is a scan, the right baseline for a small help center and correctness check, but the wrong default at millions of vectors. Approximate nearest neighbor (ANN) indexes trade a missed true neighbor for speed. Index recall (did the true vector neighbor come back) is not task recall (did the answering passage come back).

The structures trade recall, latency, memory, and update pain. HNSW (Malkov and Yashunin; hnswlib, also in FAISS) searches a graph, where `efSearch` and `efConstruction` trade recall for latency or build time. It stores full vectors plus links, inserts can slowly degrade it, and deletes are often tombstones until a rebuild. IVF (FAISS inverted file) clusters the space and searches `nprobe` lists; the clustering is a training pass, and centroids stay wrong after drift until retrained. Locality-sensitive hashing buckets similar vectors by colliding hashes, is usually weaker than HNSW or IVF, and differs from the MinHash LSH that the Deduplicating data card in [Dataset Engineering](../08_Dataset_Engineering/) uses on token shingles. Product quantization (Jégou et al.) compresses vectors to short codes, with approximate distances and an optional refine step; IVF plus PQ is the large-scale FAISS pattern. ScaNN (Guo et al., ICML 2020) is a trained compression index for maximum inner product search, penalizing error parallel to the vector more because that error moves an inner product. pgvector offers exact scan, IVFFlat, and HNSW in Postgres, but not PQ. Pinecone, Weaviate, Milvus, Qdrant, and Chroma make the same choices, and Elasticsearch/OpenSearch keep term and vector indexes in one engine for hybrid search. Dense retrieval misses exact product codes and error strings that BM25 hits, and a new embedding model invalidates every vector, graph, and threshold.

```text
exact scan   small corpus, correctness baseline
HNSW         fast queries; memory for vectors + links; tombstones, rebuilds
IVF          trained partition; nprobe; centroids drift
PQ / ScaNN   compressed, trained; distorted distances (ScaNN tuned for inner product)
```

![Embedding-based retrieval](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-4-embedding-retrieval.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 4.*

## Comparing retrieval algorithms

Comparing retrievers means scoring whether the right passages came back, and at what latency, cost, and update pain, before you look at the generated answer.

Recall at k is the fraction of relevant passages in the top k, and precision at k is the fraction of those k that are relevant. MRR averages `1 / rank` of the first relevant passage, with 0 if none returned. NDCG rewards higher relevance higher up, normalized by the ideal order. This exercise uses linear gain (relevance ÷ log2(rank + 1)); the other common gain is 2^relevance − 1, so name the one you computed. Three questions with gold chunks at ranks 1, 4, and 8 and k = 5 give recall 0.6667, precision 0.1333 (with one gold chunk, a perfect top 5 is still 1/5), and MRR 0.4583 using full-ordering ranks. A truncated five-item list would score that missing question 0, so say which list you scored. Graded relevances 3, 0, 1 give NDCG 0.9639 (3.5000 of an ideal 3.6309). These are exercise ranks, not a leaderboard, and none is a generation metric; log ids and score them per the component pipeline in [Evaluate AI Systems](../04_Evaluate_AI_Systems/).

Latency, cost, and updates decide whether recall ships. BM25 is a cheap CPU query. An exact vector scan is linear, fine for the 2,000-chunk exercise index; at millions of chunks, HNSW or IVF adds its own index recall, which can be high while task recall is low. Query cost is the embedding call, index, and reranker. Index cost is embedding the corpus, which dominates on a model change. A text edit re-embeds one chunk, while BM25 statistics shift as the corpus grows, so its scores are not stable thresholds. ann-benchmarks reports recall, queries per second, build time, and size; read it at your corpus size. RAGAS context precision (relevant chunks ranked above irrelevant ones, given a reference answer) and context recall (fraction of reference claims supported) are not precision and recall at k, so say which you mean. Choose with a checklist: mechanisms, scale, build and refresh time, latency at your concurrency, price per query and stored vector, and whether permissions run before the prompt. A vendor that cannot express permissions is not a candidate.

```python
import math


RANKS = (1, 4, 8)
K = 5


def mean(values: tuple[float, ...]) -> float:
    return sum(values) / len(values)


recall = tuple(1.0 if rank <= K else 0.0 for rank in RANKS)
precision = tuple((1 / K) if rank <= K else 0.0 for rank in RANKS)
reciprocal = tuple(1 / rank for rank in RANKS)


def dcg(gains: tuple[int, ...]) -> float:
    return sum(gain / math.log2(rank + 1) for rank, gain in enumerate(gains, start=1))


gains = (3, 0, 1)
ideal = tuple(sorted(gains, reverse=True))
got = dcg(gains)
best = dcg(ideal)
print(f"{mean(recall):.4f} {mean(precision):.4f} {mean(reciprocal):.4f}")
print(f"{got:.4f} {best:.4f} {got / best:.4f}")
# 0.6667 0.1333 0.4583
# 3.5000 3.6309 0.9639
```

![Comparing retrieval algorithms](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-5-comparing-retrievers.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 5.*

## Combining retrieval algorithms

Combining retrieval algorithms uses more than one ranker so a query that needs an exact token and a query that needs a paraphrase can both succeed.

Adding a BM25 score to a cosine looks obvious and misleads. Cosine lies in [−1, 1], Elasticsearch often stores dense cosine as one plus that in [0, 2], and BM25 is unbounded and corpus-dependent, so the larger scale wins and you have attended to one system. A normalized sum can use score gaps and silently breaks when one distribution shifts. Reciprocal rank fusion (RRF; Cormack, Clarke, and Buettcher, SIGIR 2009) ignores scores: a document's fused score is the sum of `1 / (k + rank)` over the lists it appears in, with `k` = 60 in the paper and as Elasticsearch's `rank_constant` default. Appearing in both lists is not automatically a win. At `k` = 60, rank 62 in both ties rank 1 in one (2/122 = 1/61), and rank 63 in both loses. On short lists, a hit in both still separates itself. Fusing BM25 order C, A, D with vector order A, B, C gives A (1/62 + 1/61 = 0.032522), C (0.032266), B, and D. A smaller `k` exaggerates rank 1; if you change it, do not compare against runs at 60.

Sequential combination is the other shape. A cheap retriever builds a pool (BM25 can require the product code), and an expensive ranker or cross-encoder orders the survivors. That is reranking, not fusion, and it cannot save a passage the first stage dropped. Fusion can save only a passage some returned list contains. Elasticsearch 8.19 also defaults `rank_window_size` to 10, so rank 11 in both child results never enters fusion. OpenSearch can run lexical and vector queries in one engine. Either way, two indexes mean two update paths and a fusion step to log. Pay for both only when the query mix contains both exact-token questions and paraphrases, and measure each list's recall first.

```python
def rrf(lists: tuple[tuple[str, ...], ...], k: int = 60) -> dict[str, float]:
    scores: dict[str, float] = {}
    for ranking in lists:
        for rank, doc in enumerate(ranking, start=1):
            scores[doc] = scores.get(doc, 0.0) + 1 / (k + rank)
    return scores


fused = rrf((("C", "A", "D"), ("A", "B", "C")))
order = sorted(fused, key=fused.get, reverse=True)
print(" ".join(order))
print(" ".join(f"{fused[doc]:.6f}" for doc in order))
# A C B D
# 0.032522 0.032266 0.016129 0.015873
```

![Combining retrieval algorithms](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-6-combining-retrievers.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 6.*

## Chunking strategy

Chunking strategy is how you split a document before it is indexed, so each unit is large enough to mean something and small enough to retrieve and to fit in the prompt.

A fixed window of a few hundred tokens with overlap is the baseline, so a boundary sentence survives somewhere. Structure is a better cut when you have it: headings for help articles, sections for specs, functions for code (half a function embeds as two wrong units). Parent-child (small-to-big) retrieval matches a short span and sends the surrounding section, keeping the adjacent exception. Semantic splitting adds a model with its own failures at index time and is no reason to skip existing headings. The failure that makes this a design choice is facts split across chunks. "Headphones are electronics" and "electronics are 14 days" do not individually answer "how long do I have to return headphones." Overlap repairs a cut sentence, not two facts with no shared tokens. Retrieving more chunks recreates the long-context problem. Index the section holding the rule and its case, or retrieve the child and send the parent.

The exercise sizes a help center: 400 articles of 1,200 tokens, 300-token windows with 50-token overlap (stride 250), and 1,536-dimensional float32 vectors (text-embedding-3-small's default width). Each article yields five chunks, the last 200 tokens, for 2,000 chunks and 12,288,000 bytes (11.71875 MiB) of vectors. The overlap stores 560,000 tokens against 480,000 source tokens, or 2,240,000 characters at an assumed 4 per token. An assumed graph degree of 32 integer links is 256,000 bytes, so vectors dominate. float16 halves vector bytes only if the index stores float16. At this size an exact scan is still sane. A model swap rewrites the vectors but not the chunk text, while a heading change re-chunks the article. Short chunks match precisely and split rules from exceptions; long chunks keep sections together, waste prompt, and embed any single fact worse. Pick the size your recall at k moves on, measured on questions with marked answers.

```python
import math


ARTICLES = 400
TOKENS = 1_200
CHUNK = 300
STRIDE = 250
DIM = 1_536


def chunk_starts(n_tokens: int, chunk: int, stride: int) -> list[int]:
    starts = []
    start = 0
    while start < n_tokens:
        starts.append(start)
        if start + chunk >= n_tokens:
            break
        start += stride
    return starts


starts = chunk_starts(TOKENS, CHUNK, STRIDE)
lengths = [min(CHUNK, TOKENS - start) for start in starts]
chunks = ARTICLES * len(starts)
vector_bytes = chunks * DIM * 4
stored_tokens = ARTICLES * sum(lengths)
link_bytes = chunks * 32 * 4
print(starts, lengths)
print(chunks, vector_bytes, f"{vector_bytes / 1024 / 1024:.5f}")
print(stored_tokens, ARTICLES * TOKENS, stored_tokens * 4, link_bytes)
# [0, 250, 500, 750, 1000] [300, 300, 300, 300, 200]
# 2000 12288000 11.71875
# 560000 480000 2240000 256000
```

![Chunking strategy](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-7-chunking.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 7.*

## Reranking

Reranking takes a short list of retrieved passages and orders that list with a model that reads the query and the passage together.

The first stage is a bi-encoder or BM25. A bi-encoder embeds each side alone, which makes it indexable and blind to the query beside the passage. A cross-encoder scores the pair in one forward pass, so it can notice a different product or the right number next to "days," but it cannot run over the whole corpus per request. The pattern is to retrieve a few dozen, rerank, and keep the few you prompt with. Cohere Rerank is a hosted example; open cross-encoders include the MS MARCO MiniLM rerankers and BAAI's bge-reranker models. The score orders candidates and is not a calibrated support probability unless you calibrate it on your pairs. Late interaction sits between: ColBERT (Khattab and Zaharia, 2020) stores a vector per token and scores by MaxSim (each query token takes its best passage token, and the similarities add). It is precomputable, unlike a cross-encoder, with a much larger index, and works as first stage or reranker. The multimodal card applies the same MaxSim to image patches.

Reranking cannot create recall the first stage never had; a gold chunk both retrievers missed never reaches the cross-encoder, so fix retrieval or chunking instead. What it changes is precision at the small k you prompt with. Five good chunks beat fifty with the gold one buried, for the bill and the lost-in-the-middle tendency. A reranker can prefer a fluent chunk that contradicts the question, so rank is not grounding; entailment stays on the Factual consistency card. Each candidate scored adds latency and money, and batching does not make a million-chunk cross-encode reasonable. An MS MARCO reranker is general until measured on help-center questions, and a hosted reranker is another place customer text goes. Skip reranking when the first stage already puts gold in the top few and the budget is gone.

```text
bi-encoder / BM25     whole corpus, indexable, sides scored apart
ColBERT (MaxSim)      stored token vectors, heavier index
cross-encoder         pair in one pass, short list only (rerank 50 -> prompt 5)
```

![Reranking](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-8-reranking.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 8.*

## Query rewriting

Query rewriting changes the user's question into a search query, or into several, before retrieval runs.

People do not type the index's words. A Notion follow-up such as "what about returns?" needs "returns" resolved against the product from the previous turn. A two-part question (the window, plus the electronics exception) retrieves better as two queries whose passages both reach the generator. A lexical index benefits from adding a term the user did not know and is harmed by adding one they did not mean. The rewrite is a query, not a source: answering from rewritten text without reading a passage is skipping RAG while calling it RAG. Log the original question and the query you ran, or you cannot debug a miss.

HyDE (hypothetical document embeddings; Gao et al., 2022) has the model write a passage that might answer the question, embeds it, and searches with that, on the bet that an answer sits closer to answers than a question does. It helps on vague questions over answer-shaped corpora. It hurts when the hypothetical invents a policy: an invented "30 days" retrieves the 30-day page, and the electronics exception never surfaces. Discard the hypothetical after retrieval; the returned passage is what the generator may use. A rewrite model call also adds latency before search starts, and a hand-built resolver for follow-ups is easier to test. Multi-query retrieval raises recall at the cost of extra reads and chunks.

```text
follow-up     resolve references from earlier turns
compound      split into several queries, show all passages
HyDE          embed a hypothetical answer; discard it after search
always        log the original and the executed query; never cite the rewrite
```

![Query rewriting](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-9-query-rewriting.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 9.*

## Contextual retrieval

Contextual retrieval prepends a short note that says where a chunk sits in its document, then indexes that combined text with embeddings and with BM25.

"The limit is 14 days" does not say 14 days of what; the heading, product, and title were cut off by the window. Anthropic's contextual retrieval (19 September 2024) has a model write a situating note, usually 50 to 100 tokens, from the whole document and the chunk, and prepends it before embedding and BM25 indexing. It is generated at index time, not a query rewrite. Defining top-20 failure as one minus recall at 20, the domain average on their highlighted embedding setup moved from 5.7% to 3.7% with contextual embeddings (35% reduction), to 2.9% adding contextual BM25 (49%), and to 1.9% with both plus their Cohere reranker over a wide candidate list cut to 20 (67%). That is their setup, not a promise for your help center; copy the direction that a chunk should carry the words searches use.

In the term-overlap exercise below (not a BM25 score), the bare chunk shares no term with "headphone return" and the noted chunk shares both. A vector index has the same hole, since the bare chunk's neighborhood is every "14 days" in the corpus. The note is a generated prefix: attach it to the wrong product and both retrievers go to the wrong place, worse than no note. Notes cost a model call per chunk, lengthen every chunk (changing counts and how much of the chunk is note), and must be regenerated when the article changes. Otherwise the index is stale with extra confidence. A real heading from the HTML is cheaper and should come first. The 67% figure includes contextual BM25 and the reranker, not a reranker alone, and your recall at 20 needs its own measurement.

```python
def shared(query: str, text: str) -> list[str]:
    return sorted(set(query.split()) & set(text.split()))


bare = "the limit is 14 days"
contextual = "headphone return rule for this section. the limit is 14 days"
print(shared("headphone return", bare))
print(shared("headphone return", contextual))
# []
# ['headphone', 'return']
```

![Contextual retrieval](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-10-contextual-retrieval.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 10.*

## Multimodal RAG

Multimodal RAG retrieves images, or pages that are images, along with text, so the generator can use a figure, a screenshot, or a scan.

Three pipelines lose different information. Captioning or OCR indexes text: a Shopify photo becomes "blue wool socks," but an earnings chart becomes "a chart of revenue" if the captioner skips the axis, and OCR loses a table that is a picture of a table. A shared embedding space, CLIP (Radford et al., 2021), contrastively trains one vector per image and caption. It is right for "a photo of wool socks" and weak on a page of small type, because one vector stands for the whole image. Page-image multi-vector retrieval, ColPali (Faysse et al., 2024), runs a vision-language model (PaliGemma originally) over the page and scores queries with ColBERT-style late interaction against patch vectors. It avoids an OCR layout pipeline at the cost of a heavier index and a vision model at query time. ViDoRe is their benchmark, not a score on your documents.

The generator must be able to use what was retrieved. A page image needs a model that reads images; a caption needs only a text model, with its omissions already baked in and unrecoverable. A Notion page mixing paragraph and screenshot wants both paths. OCR plus text RAG suits a clean digital PDF and fails on a photographed packing slip. Sending every image to a vision model with no retrieval is the long-context bill again. Permissions apply to images exactly as to documents; a contract scan is still a contract.

```text
caption / OCR   cheap; drops what it fails to read (axes, numbers, stamps)
CLIP            one vector per image; good for photos, coarse on dense pages
ColPali         patch vectors + late interaction; heavier, keeps the page
generator       must be able to read what you retrieved
```

![Multimodal RAG](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-11-multimodal-rag.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 11.*

## RAG with tabular data

RAG over tables either retrieves the table as text or asks a query the warehouse runs, and the warehouse result is the source.

A small table in a help article, such as shipping rates or a short price grid, can be a chunk that BM25 and embeddings find, and the generator can quote a cell. A sales warehouse is different: Shopify orders, refunds, and taxes do not belong in a vector index as dumped rows, and "how many orders were refunded last week" needs a filter, a date column, and an aggregation. Text-to-SQL is that path. Retrieve the relevant schema cards, not every table, and prompt with them, the question, and a few labeled examples. The model writes one statement. Your program checks it is a single read, every column exists, and the caller's permissions allow those tables; the warehouse runs it with a timeout and row cap; the answer is narrated from, or shows, the result. Execution accuracy, Spider, and BIRD are the functional-correctness card in [Evaluation Methodology](../03_Evaluation_Methodology/); this card is the system around that metric.

The failures are specific: a column never in the schema, filtering the order's created date when the event is on the refund, or counting refund rows when the question asked for distinct orders. An empty result looks like zero unless you trust the statement, so show the query with the count and check the count against the rows. An update, delete, or DDL never runs, however helpful. The model's prose cannot override the warehouse, and a write tool against it is an agent with a side effect, not retrieval. Chunking small tables collapses once a question needs a sum, join, or split date. Retrieving every table blows the context and still lacks row values. A semantic layer of approved metrics is slower to build and stops the model inventing a definition of "refunded" that finance does not use.

```text
small table         chunk it
warehouse question  schema retrieval -> one statement -> guard -> execute -> answer from rows
guard               single read, known columns, caller permissions, timeout, row cap
```

![RAG with tabular data](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-12-tabular-rag.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 12.*

## What an agent is

An agent is a model in a loop that observes an environment, chooses a tool, and uses the tool's result to decide what to do next, until the task stops.

The environment is what the loop can see and change: a GitHub repository and its tests, a browser, a travel API, a help center plus a ticket. Tools are the only actions. The planner, usually the model and sometimes a program that calls and overrides it, picks the next action. A single RAG answer retrieves once and generates once, so it is not an agent; it becomes one when the model can search again, call a different tool, or stop. ChatGPT with a browser, a Copilot coding agent that reads a repository and runs tests, and a support bot that looks up an order and drafts a reply are agents of increasing side effect. That side effect is the safety question. A planner that can only retrieve is multi-step RAG; one that can charge a card moves money, and the System-level defenses card in [Prompt Engineering](../05_Prompt_Engineering/) sets that boundary.

An agent is not a smarter prompt. The prompt still conditions one sample, and the loop is the program around samples: append the observation, call again, and stop on a condition your code enforces. The model can propose "stop," but the step cap and tool allow-list must stop it when it never does, or a sample runs until the budget does. A loop can recover from a bad search by searching again, and it can also repeat, drift, and spend many calls on a question one retrieval would answer. A fixed retrieve-then-draft pipeline is easier to test and cannot handle a task whose second step depends on the first result. Calling every chatbot an agent makes the word useless; it should mean a loop plus a tool choice.

```text
environment   repository, browser, ticket + help center
tools         the only actions
planner       proposes the next action (usually the model)
host          appends observations, enforces stop, cap, allow-list
```

![What an agent is](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-13-what-an-agent-is.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 13.*

## Knowledge tools

A knowledge tool returns text the model did not have in the prompt. Search over a Notion workspace, a web search, and the help-center retriever from the first half of this topic are knowledge tools.

The result is untrusted context, neither fact nor instruction. A page, snippet, or payload can tell the model to ignore the policy, which is indirect prompt injection in [Prompt Engineering](../05_Prompt_Engineering/). Retrieval makes text present, not true or safe. Permissions apply before the passage enters the prompt; a tool that can see a document the caller cannot has already failed, even if the draft never quotes it. Passages can be stale: index lag is Full-Text Search Architecture in [Search Autocomplete and Information Retrieval](../../09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/), and searching again does not refresh a stale index; reindexing does.

Classify the tool before discussing the planner. A Notion search is knowledge; capability tools and write tools are the next two cards, and a tool that both searches the wiki and sends mail has skipped that split. Returning a whole page spends the window, while a snippet can drop the exception. When a draft is wrong, the log should show the query, the returned ids, and whether the answering page was among them; that separates a wrong draft from a missed page.

```text
returns   text the prompt lacked (untrusted, maybe stale)
before    permission check
log       query, ids, whether the answering page was present
```

![Knowledge tools](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-14-knowledge-tools.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 14.*

## Capability tools

A capability tool does work the model should not fake. A calculator returns the product of the numbers. A code interpreter runs a repository's tests. A clock returns the date a refund window is counted from.

The model can write a plausible test summary without running anything; the tool makes the observation the run itself. The sandbox is the control from the System-level defenses card in [Prompt Engineering](../05_Prompt_Engineering/): no production credentials, a network policy, a timeout, and a filesystem that is not customer data. "Run the tests" in a prompt is not that sandbox. GitHub-hosted runners and a locked-down CI job are the same idea at different sizes. Process output is still untrusted if code under test or a dependency can print an instruction, so append the exit code and the assertion you trust, not an unfiltered log.

A calculator is the small version: the draft's arithmetic must match the tool's number or you do not show the draft. A calculator the draft may override is decoration. Capability tools add latency and a runtime to patch. Doing the work in tokens is right for a one-line rewrite and wrong for a test suite. A general "run this shell" tool bundles a capability with a write, because the shell can edit the repository, and belongs with write tools.

```text
calculator, interpreter, clock -> the observation is the source
sandbox (code): no creds, network policy, timeout, isolated filesystem
append: exit code + trusted assertion, not raw output
```

![Capability tools](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-15-capability-tools.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 15.*

## Write tools

A write tool changes a system outside the conversation. A Stripe refund, outbound mail, and a merge to a protected branch are write tools. The model's JSON is a proposal. The program decides whether the call happens.

The checks are specific. Recompute the amount from the order, or check it against what the person saw. Reject tool names not on the allow-list. Require a person for irreversible actions, confirming the arguments your program computed, not the ones the model echoed; "yes, refund me" in chat is not that confirmation. The introduction topic puts a person on money movement, and the System-level defenses card in [Prompt Engineering](../05_Prompt_Engineering/) explains why the prompt cannot waive them. A retried refund needs an idempotency key so the loop does not refund twice; that is the attempt key on the Idempotency in Payments card in [Payment and Financial Systems](../../09_System_Design_Interview/23_Payment_and_Financial_Systems/).

Partial failure is the other half. If the refund succeeds and the confirmation email fails, retrying the whole plan moves money again unless the key and recorded outcome show it already happened. A tool that both reads the inbox and sends mail skips least privilege, so split it. Reads of a public help page are not on this card and need no human gate. An expiring hold that cannot capture funds is closer to a capability; a hold that becomes a charge unless cancelled is a write. Least privilege, an idempotency key, and a person on the irreversible step are three different controls, and a refund usually needs all three. A merge to a protected branch is the case you do not automate.

```text
model     proposes (tool, arguments)
program   allow-list, recompute arguments, human on irreversible, idempotency key
retry     never re-apply a write because a later step (the email) failed
```

![Write tools](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-16-write-tools.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 16.*

## Planning, then checking, then acting

Planning, then checking, then acting means the agent produces a plan, your program validates it, and only then does a tool run.

A loop that acts on every sample can reject a bad step only after it happened. Decoupling gives a rejection point. The planner proposes "look up the order, read the policy, draft the reply," or wrongly "charge the card, then look up the order." The checker rejects tools you did not offer, skipped preconditions, and writes sequenced before the read that justifies them. The executor runs passing steps and rechecks each write at execution time, because the order may have been refunded since. The check is code: an allow-list, an argument schema, a permission check, and a human gate on writes. Asking the model whether its plan is safe is another sample. The dual-LLM and capability checks on the system-defense card handle untrusted text choosing the action; the plan checker handles the planner proposing something disallowed.

Plan-and-execute is the pattern of writing steps, then acting. ReWOO (Xu et al., 2023) is a published version: the plan and tool placeholders are written before observations return, so tool results cannot rewrite the planner. That also means the planner sees no tool error without an explicit replan. A frozen plan is cheap, reviewable, and blind to errors. Replanning after every observation is ReAct (reflection card); it uses new evidence, spends calls, can loop, and lets a hostile observation steer the next plan. Checking only the first step and then free-running is the decoupling with the lock left off.

```text
propose (model) -> validate (code: allow-list, schema, permission, order)
-> execute (recheck each write now) -> replan only where you chose
```

![Planning, then checking, then acting](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-17-plan-check-act.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 17.*

## Foundation models as planners

A foundation model used as a planner proposes the next steps in language. It is not a classical planner that searches a declared model of the actions and proves the plan.

The useful half is real. Given a ticket, schema, and tool list, a model drafts ordered steps like an engineer's notes: coding agents choose which file to read before which test, and travel agents search before booking. The weak half is real too. It samples a continuation rather than expanding a state space, so it invents tools, skips preconditions, and states steps as done. A classical (PDDL-style) planner with an explicit action model cannot emit an absent action and is sound only relative to the world model you wrote, which is a poor fit for "figure out what this customer wants." The model proposes; a program with an allow-list disposes. "The model planned it" is not a root cause after the wrong tool runs.

Classical planning is search: expand, score against the goal, backtrack. An autoregressive model commits to tokens and cannot unsay them. Give it tools that make search and undo real, such as a test command, reverting an uncommitted edit, browser back, or a rolled-back transaction. Without undo, "try the other approach" is another forward sample with the bad edit still in place, and compounding error multiplies the early mistake. A model planner differs from a reinforcement-learning agent. The model plans from context, takes a new tool list via prompt, and has not practiced your queue. An RL policy learns from reward over many episodes, can become reliable there, and does not absorb Tuesday's refund policy the same day. Use the model when goals are messy text and tools change; use a learned policy or plain code for repeated, scorable actions. Shorter plans, replanned at boundaries you choose, fail in smaller pieces than long one-shot plans.

```python
OFFERED = {"lookup_order", "read_policy", "draft_reply"}
plan = ["lookup_order", "read_policy", "issue_refund"]
unknown = [step for step in plan if step not in OFFERED]
print(unknown)
# ['issue_refund']
```

![Foundation models as planners](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-18-models-as-planners.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 18.*

## Plan generation and control flow

Plan generation is how a model emits the next action as a structure your program can run, and control flow is where sequence, parallelism, branches, and loops live.

Function calling, shipped in OpenAI's API in June 2023 and also implemented by Anthropic tool use and Gemini function calling, is the emission format. You send names, descriptions, and argument schemas; the model returns a name and arguments or a final answer; your code validates and runs or refuses. Structured outputs ([Understanding Foundation Models](../02_Understanding_Foundation_Models/)) keep the call on schema when a mask or strict mode exists. Toolformer (Schick et al., 2023) is the training route: a model finetuned to insert calls (calculator, calendar, Wikipedia, translator, QA system) where they reduced the perplexity of following tokens. The habit lives in the weights; today's help center does not. The Model Context Protocol (Anthropic, November 2024) sits a level up: an MCP server advertises tools and a host forwards calls, so one packaged tool is discoverable by many apps. Connecting a server is a trust decision, and neither a finetune nor MCP makes a write tool safe.

Tool granularity is a product choice. One tool per business action (`lookup_order`, `draft_reply`) gives the checker something to allow. `run_sql` with warehouse credentials bundles capability and write. One tool per trivial function crowds the menu. Plan granularity is the second choice: steps as exact calls (`lookup_order(order_id="1001")`) can be validated and run, while prose ("look up the order, check the window") needs a translator call that silently breaks when tools are renamed. Prefer calls when a program executes the plan, and do not finetune a translator against a tool list you will edit next week. The host owns control flow: independent reads run together, the draft waits for both, branches use results your code computed, and loops (pagination, retries) have caps. Parallel reads race if they were not truly independent. A strict schema stops malformed arguments but not a well-typed wrong order id.

```python
STEPS = {
    "lookup_order": set(),
    "read_policy": set(),
    "draft_reply": {"lookup_order", "read_policy"},
}


def ready(done: set[str]) -> list[str]:
    return sorted(name for name, deps in STEPS.items() if name not in done and deps <= done)


print(ready(set()))
print(ready({"lookup_order", "read_policy"}))
# ['lookup_order', 'read_policy']
# ['draft_reply']
```

![Plan generation and control flow](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-19-plan-generation-control-flow.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 19.*

## Reflection and error correction

Reflection is the agent looking at a failed step and changing the next step. Error correction is the program giving the failure back in a form the model can use, once, rather than hoping the next sample guesses better.

ReAct (Yao et al., 2022 preprint, ICLR 2023) interleaves thought, action, and observation, where the observation is the tool's real result appended for the next turn. It works when the observation can change the plan, for example a failed lookup on the subject-line id followed by a retry using the id from the body. It fails when the "observation" is a thought pretending success, or when the model re-emits the same action without reading the error, so the logged trace must contain tool results, not only thoughts. Reflexion (Shinn et al., 2023) writes and stores a note about what went wrong, then retries. The note is language, not a weight update. It can be wrong, and a wrong reflection steers every later attempt. For code, running the tests is a better critic than a note about whether they would pass.

The program makes errors specific and refuses repeats. A schema failure returns the parser error, a missing order returns the lookup message, and a timeout gets one retry with backoff. The fifth identical call is a stuck agent. A changed argument is a repair; an identical call is a repeat the host stops, and the model's reflection may explain a repair but cannot override the stop. Append the error code and message you trust, not an unfiltered upstream body that could itself be an injection. Cap attempts: unlimited retries turn a missing order into a bill, while a hard stop with no repair path turns a typo into a failed task.

```python
def classify(previous: tuple[str, str], proposed: tuple[str, str]) -> str:
    if proposed == previous:
        return "repeat"
    if proposed[0] == previous[0]:
        return "repair"
    return "new tool"


print(classify(("lookup_order", "1001"), ("lookup_order", "1002")))
print(classify(("lookup_order", "1002"), ("lookup_order", "1002")))
# repair
# repeat
```

![Reflection and error correction](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-20-reflection.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 20.*

## Tool selection

Tool selection is the model's choice of which offered tool to call. The choice is only as good as the set you offered and the descriptions you wrote.

A description is a prompt. "Helps the user" matches every question, so it matches none of them usefully. "Use when the customer asks where a package is. Do not use this to refund an order." can be graded against a ticket. The negative sentence matters where tracking and refunding both sound relevant, since much training text has dissatisfied customers getting refunds. Schemas matter too: `id` gets filled with whatever id is nearby, while `order_id` described as the order-system id, not the user's sentence, is a smaller hole. The tool list costs tokens on every call. Overlapping descriptions give two plausible names for one ticket, and whether a longer menu selects worse is an ablation on your list, not a law. When it does, offer fewer tools per entry point: tracking on the tracking page, refund in the refund flow behind write checks. Ablation (remove the tool and rerun the tasks it should handle) shows whether a tool is needed. If success does not drop, the tool was a way to be wrong; if it drops, improve the description before adding neighbors.

A router that picks tools by embedding their descriptions is another retriever, with the same paraphrase and exact-token issues, and is scored as its own component. Two published systems treat selection as more than one pick. Chameleon (Lu et al.) plans module sequences with a language model and then plots which module followed which on the test set. That transition graph measures plans and does not replace the planner; read it once you have traces. Voyager (Wang et al.) stores successful programs as skills and retrieves them instead of reinventing procedures. That is procedural memory, which goes stale when tools change, the same inventory problem as a finetuned translator. A tool the router never selects is either badly described or does not belong on that surface.

```text
description   when to use it + when not to, named arguments
surface       few tools per entry point
evidence      ablation: remove it, rerun, see if success drops
```

![Tool selection](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-21-tool-selection.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 21.*

## Planning failures

A planning failure is a step that is illegal, aimed at the wrong goal, or never ends. The tool does not have to run for the failure to be real. The plan already contains it.

The model names `force_push` when it was not offered. The GitHub issue asks to fix the retry bug and the plan opens by renaming the package. A thought says the tests passed with no test observation in the log. The loop proposes steps until the budget dies because the model never proposes stop. These are one gap in different shapes: a plausible continuation is not a legal plan. The allow-list rejects unknown tools, the plan checker rejects a write before its justifying read, and the step cap stops the endless loop. A thought without an observation is not success. Asking the model whether its plan is safe is another sample.

The host records a stop reason, so an eval can separate an illegal plan from a timed-out tool. That distinction decides the fix. Editing the prompt can be right for an illegal plan and is wrong for a timeout. A wrong id on an offered tool belongs to the next card, not this class. A tight allow-list and short cap also stop long tasks you did not anticipate, and a frozen legal plan can still hit a tool failure on its next step.

```text
invented tool         -> allow-list
wrong goal / order    -> plan checker
claimed success       -> require an observation
never stops           -> step cap
log                   proposed step + rejection reason
```

![Planning failures](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-22-planning-failures.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 22.*

## Tool failures

A tool failure is a call that was allowed and is still wrong. The tool exists, the arguments match the schema, and the outcome is not the outcome the task needed.

The host offered `comment_on_issue`, and the model comments on GitHub issue 10 while the person is looking at 11: the schema is satisfied and the issue is wrong. A tracking lookup times out and the draft fills in a delivery date from the weights. The help-center index is a day behind the article just published, which is search-index lag, not new hallucination. A lookup returns a customer note saying to ignore the refund policy, and the next step follows it; that is indirect prompt injection carried in a tool result ([Prompt Engineering](../05_Prompt_Engineering/)). An allowed refund retried after a failed email is the idempotency failure from the Write tools card.

The fixes match the mechanism. Check or recompute arguments, because a green schema check is not evidence you touched the right record. Put a timeout on each call so one stuck call cannot eat the step budget. Refresh the index when the source changes. Append an error you trust, not an unfiltered upstream body. Retrying a read can be right; retrying a write without a key can apply it twice. A planning cap will not catch a single legal call that names the wrong issue.

```text
wrong record    -> recompute / check arguments
timeout         -> bounded call, handled failure (no invented value)
stale index     -> reindex on source change
injected body   -> append trusted error only
retried write   -> idempotency key
```

![Tool failures](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-23-tool-failures.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 23.*

## Efficiency failures

An efficiency failure is a plan that is legal and still too expensive. The task can succeed. The bill, the latency, or both are what failed.

The same lookup gets proposed on several steps, independent reads run one model call apart, and context grows by the whole history so the sixth call pays for the first five. At this series' exercise prices ($0.50/$2.00 per million), a six-step loop starts from an 800-token prefix (instructions, schemas, request); each step emits 120 tokens and appends a 280-token observation, so input grows by 400. Inputs sum to 10,800 and outputs to 720: $0.00684 per task, $684.00 per 100,000. A one-shot retrieve-then-answer call (2,000 in, 200 out) is $140.00. The gap is not "six times one call." Each reply is billed as output once, then with its observation as input on every later step.

Parallel tool calls shrink this sum only when they remove a model call: two lookups returned in one step are one output plus one later input. Six model calls with side-by-side tools change latency, not tokens. A step cap is both an efficiency and planning control, and the reflection card's repeat check stops identical calls before the cap is the only defense. A tight cap also cuts tasks that legitimately need another lookup. Classify failures before fixing them (invented tool: planning; wrong id: tool; growing legal loop: efficiency), logging the tool name, arguments, observation, and stop reason, or you will edit the prompt when the tool timed out. Deleting a necessary verification to save the $684 optimizes the wrong failure. Prices move; recompute the growing-context shape on the current card.

```python
INPUT_PER_M = 0.50
OUTPUT_PER_M = 2.00
CALLS = 100_000
PREFIX = 800
GROWTH = 400
OUTPUT = 120
STEPS = 6


def bill(calls: int, input_tokens: int, output_tokens: int) -> float:
    input_cost = calls * input_tokens / 1_000_000 * INPUT_PER_M
    output_cost = calls * output_tokens / 1_000_000 * OUTPUT_PER_M
    return input_cost + output_cost


inputs = [PREFIX + step * GROWTH for step in range(STEPS)]
agent = bill(CALLS, sum(inputs), OUTPUT * STEPS)
once = bill(CALLS, 2_000, 200)
print(inputs, sum(inputs), OUTPUT * STEPS)
print(f"{agent / CALLS:.5f} {agent:.2f} {once:.2f}")
# [800, 1200, 1600, 2000, 2400, 2800] 10800 720
# 0.00684 684.00 140.00
```

![Efficiency failures](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-24-efficiency-failures.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 24.*

## Compounding error in agents

Compounding error is the drop in end-to-end success when each step has to be right and a later step does not repair an earlier miss. Per-step accuracy multiplies.

If each of ten steps is right with probability 0.95 given a correct prefix, and misses are not repaired, the task succeeds `0.95^10` ≈ 0.599 of the time. A model strong on one tool call succeeds about six times in ten on a ten-step refund or coding task. At 0.99 it is about 0.904, and at 0.90 about 0.349. So a one-point per-step gain matters more as plans lengthen, and agents want stronger models than one-shot summaries. The product is the no-repair case, not a floor: a repairing checker beats it, and a cascade does not push below it because the product already treats a miss as final. The real trap is plugging in a 0.95 measured on a clean single call when the conditional rate inside a long trace, with the model continuing its own text, can differ; measure that on model-produced prefixes. This is the product along one trial. pass^k (Agent evaluation) is every repeated trial succeeding, and pass@k ([Evaluation Methodology](../03_Evaluation_Methodology/)) is at least one succeeding, where independence is a ceiling.

Stronger models raise the base and the per-step price; fewer steps shrink the exponent. A fixed retrieve-then-draft pipeline does not pay `0.95^10`, and the step cap is an accuracy control as well as a cost one. Writes raise the stakes: a wrong lookup can be repaired by the next call, but a wrong refund, sent email, or merge cannot. The mitigations break the product in different places. Verification uses a checker that does not share the failure (tests, a recomputed amount, a schema). A checkpoint (commit, draft, held payment) preserves a correct prefix, and it must be a real undo, since an autoregressive sample cannot unsay a token. Human approval cuts the chain at the write. Reflection repairs failed reads, not successful wrong writes, and a wrong reflection is another factor below 1, so attempts stay capped. If someone quotes a 95% tool-call demo as agent reliability, multiply.

```python
print(f"{0.95 ** 10:.3f}")
print(f"{0.99 ** 10:.3f} {0.90 ** 10:.3f}")
# 0.599
# 0.904 0.349
```

![Compounding error in agents](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-25-compounding-error.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 25.*

## Agent evaluation

Agent evaluation scores the steps and the outcome, on tasks where a program can tell that the world ended in the right state.

The component pipeline in [Evaluate AI Systems](../04_Evaluate_AI_Systems/) logs every stage; for an agent that means retrievals, tool names and arguments, observations, the plan, and the final state. A grounded answer on an empty retrieval is a component failure even if true, and a coding agent that edits the right file without running tests is one even if a human later makes them pass. Task success is the outcome: tests pass, the booking matches, the database row is allowed. Report both, since they disagree often. Final-state checks resist eloquent nonsense but miss a dangerous step that was undone; component checks catch it and can fail a designed recovery.

Public benchmarks make this concrete without being your queue. SWE-bench scores patches by fail-to-pass and pass-to-pass tests (the functional-correctness card). SWE-bench Verified (OpenAI with the authors, August 2024) is a 500-instance human-filtered subset that removes underspecified issues and unfair tests, under the same rule. WebArena (Zhou et al., 2023) scores the resulting state of self-hosted sites: a shop, its admin, a forum, a GitLab-style site, a wiki, and a map. τ-bench (Yao et al., 2024) has a simulated user, tools, and a written policy in retail and airline domains, scored on final database state, with pass^k (all k trials succeed) as its reliability metric. Its results section reports gpt-4o function calling at about 61% pass^1 on retail and 35% on airline, with retail pass^8 near 25%; the abstract compresses that to under half the tasks and pass^8 under 25% in retail. Quote the domain. GAIA (Mialon et al., 2023) has 466 short-answer questions in three levels, with humans at 92% and GPT-4 with plugins at 15% in that paper. These are dated results with simulators. On exercise counts of 5 successes in 8 trials, unbiased pass^3 is 0.1786 and pass@3 is 0.9821. A booking flow that must work every time is the first number; sampling three and keeping a success is the second. pass^k rejects inconsistent models as k grows, and pass@k flatters samples the product will not take. Report the matching one beside component scores, and launch on a private set of your tasks with the policy and a database fixture.

```python
from math import comb


n, c, k = 8, 5, 3
pass_hat = comb(c, k) / comb(n, k)
pass_at = 1 - comb(n - c, k) / comb(n, k)
print(f"{pass_hat:.4f} {pass_at:.4f}")
# 0.1786 0.9821
```

![Agent evaluation](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-26-agent-evaluation.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 26.*

## What an agent remembers

Agent memory is state that survives a step. Some of it is in the weights, some of it is in the current context, and some of it is in a store outside the model.

Internal knowledge is the weights: what the model says with an empty prompt, changed by training or replacement, not by editing a help page, which is why a changing wiki stays on the retrieval lever. Short-term memory is the context window: conversation, plan, tool results, and any inserted summary. It lasts one call, costs input tokens, has a KV-cache memory cost ([Understanding Foundation Models](../02_Understanding_Foundation_Models/)), loses facts in the middle (the context-efficiency card), and dies with the session unless written somewhere. Long-term memory is external: a vector index of past tickets, a CRM profile row, or a store paged in by tool call. ChatGPT memory (OpenAI, 2024) keeps facts across chats, some saved at the person's request and some by the model, and the person can review and delete them. A saved sentence is not permission to act. MemGPT (Packer et al., 2023; continued as Letta) treats the window as scarce and pages data in and out of external storage by tool call, like virtual memory. Paging can retrieve the wrong page and write a wrong one.

Memory does two jobs a longer prompt does not reliably do. It keeps the agent consistent with commitments, such as the return window it already quoted. It preserves structured facts (an order id, an allergy, a date) exactly, where a summary paraphrases and then errs. Keep those fields in records, not in a prose summary a write tool reads; a system storing only chat embeddings gives a vibe of consistency and drops the id. An external store is a second source of truth that can conflict with the person, the CRM, and itself. A memory the person cannot see or delete is a support incident when it is wrong. Putting every past ticket in the window is the long-context bill; storing and retrieving them is RAG again, with the same misses.

```text
weights        updated by training       lag the wiki
window         updated per request       gone after the session, costs input
external store updated by writes          persists, can be wrong, must be visible/deletable
```

![What an agent remembers](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-27-agent-memory.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 27.*

## Managing agent memory

Memory management is how you decide what stays in the budget, what gets compressed, and what happens when two stored facts disagree.

Summarization compresses older turns to fit. A summary is a generation that can drop or invent an order id, so actionable fields stay in structured records and the summary is for prose. Eviction drops items when the budget is full, and its order encodes a priority whether you wrote one or not. Dropping the oldest is simple and forgets a constraint in favor of a recent note. Conflicts are two records that cannot both be acted on: the user said vegetarian, and a later note says they eat chicken. They need timestamps and a question before a reservation tool runs. Newest-wins is fine for displaying a suggestion and wrong for authorizing a booking. Confirming every memory is safe and exhausting; confirming before a write tool uses one is the narrower ask.

In the exercise, three memories use 950 tokens against an 800 budget. Oldest-first eviction keeps small talk and the trip and drops the 200-token allergy. Evicting unpinned items first keeps the allergy and trip. If every remaining item is pinned, all three stay at 950, over budget on purpose, because dropping the allergy to satisfy the number is the bug the pin exists to prevent. A travel note can be rebuilt from the itinerary; an allergy in the prompt keeps a dinner booking safe. ChatGPT memory and MemGPT-style stores have the same bug if they save sentences without marking which ones are constraints.

```python
BUDGET = 800
ITEMS = (("allergy", 200), ("smalltalk", 250), ("trip", 500))
PINNED = {"allergy"}


def evict_oldest(items: tuple[tuple[str, int], ...], budget: int) -> list[str]:
    kept = list(items)
    while sum(size for _, size in kept) > budget and kept:
        kept.pop(0)
    return [name for name, _ in kept]


def evict_unpinned(items: tuple[tuple[str, int], ...], budget: int, pinned: set[str]) -> list[str]:
    kept = list(items)
    while sum(size for _, size in kept) > budget:
        index = next((i for i, (name, _) in enumerate(kept) if name not in pinned), None)
        if index is None:
            break
        kept.pop(index)
    return [name for name, _ in kept]


print(sum(size for _, size in ITEMS))
print(evict_oldest(ITEMS, BUDGET))
print(evict_unpinned(ITEMS, BUDGET, PINNED))
print(evict_unpinned(ITEMS, BUDGET, {"allergy", "smalltalk", "trip"}))
# 950
# ['smalltalk', 'trip']
# ['allergy', 'trip']
# ['allergy', 'smalltalk', 'trip']
```

![Managing agent memory](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents-28-managing-memory.png)

*Source: [`diagrams/rag-and-agents.drawio`](/content/10_AI_Engineering/06_RAG_and_Agents/diagrams/rag-and-agents.drawio), page 28.*
