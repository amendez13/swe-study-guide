## The RAG pipeline

Retrieval-Augmented Generation answers the question "how do I make the LLM know about my data without fine-tuning?" The pipeline has seven stages, each with a named LangChain primitive:

```
Load → Split → Embed → Store → Retrieve → Augment → Generate
```

- **Load** — pull source documents from somewhere (file system, URL, database)
- **Split** — chunk them into model-sized pieces
- **Embed** — turn each chunk into a vector
- **Store** — persist the vectors with their text
- **Retrieve** — at query time, find chunks similar to the question
- **Augment** — splice the retrieved chunks into the prompt
- **Generate** — call the LLM with the augmented prompt

The first four stages run at index time; the last three run at query time. Most production RAG complexity is in tuning the retrieve step.

## Document loaders

LangChain ships dozens of loaders, all producing the same `Document` type (`page_content: str` + `metadata: dict`):

```python
from langchain_community.document_loaders import (
    WebBaseLoader, PyPDFLoader, DirectoryLoader, NotionDBLoader,
)

docs = WebBaseLoader("https://example.com/docs").load()
pdf_docs = PyPDFLoader("./report.pdf").load()
folder_docs = DirectoryLoader("./docs", glob="**/*.md").load()
```

Loader choice matters: `PyPDFLoader` extracts text but loses layout; `UnstructuredPDFLoader` keeps structure but is slower. For HTML, `WebBaseLoader` is fast but blunt; `RecursiveUrlLoader` follows links; structured-content loaders (Confluence, Notion) preserve metadata. Pick by what downstream consumers need.

## Text splitting

LLMs have context limits, and dense chunks retrieve better than long ones. Splitters break documents into pieces, ideally at semantic boundaries.

`RecursiveCharacterTextSplitter` is the right default — it tries paragraph breaks, then sentences, then words, then characters, falling back gracefully:

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""],
)
chunks = splitter.split_documents(docs)
```

Two knobs that matter:

- **chunk_size** — too small (200) loses context; too large (4000) dilutes relevance. 500–1500 is the sweet spot for most prose.
- **chunk_overlap** — ~10–20% of chunk_size; prevents semantic units from being split in half between chunks.

For code, use `RecursiveCharacterTextSplitter.from_language(Language.PYTHON, ...)` which knows about function/class boundaries.

## Embeddings

Embeddings turn text into fixed-length vectors where semantic similarity ≈ cosine similarity. Two documents about the same topic produce vectors close in space, regardless of word overlap.

```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vec = embeddings.embed_query("What is RAG?")
# vec is a list[float] of length 1536
```

Provider options:

- **OpenAI `text-embedding-3-small`** — cheap, decent quality, 1536 dimensions.
- **OpenAI `text-embedding-3-large`** — better, 3072 dimensions, more expensive.
- **Cohere, Voyage, Mistral** — competitive alternatives; Voyage in particular is strong for retrieval-specific tasks.
- **`HuggingFaceEmbeddings`** — local models (BGE, GTE, MiniLM); zero API cost, requires GPU for speed.

Don't mix embedding models in one index — vectors from different models live in incompatible spaces.

## Vector stores

The persistence layer for embeddings plus efficient similarity search:

```python
from langchain_chroma import Chroma

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="./chroma_db",
)
```

Common choices:

- **Chroma** — local-first, file-based; great for dev and small deployments.
- **FAISS** — Meta's library, in-memory or persisted to disk; very fast.
- **Pinecone, Weaviate, Qdrant** — managed/self-hosted vector databases for production scale.
- **pgvector** — Postgres extension; lets you keep vectors and relational data in one DB.

For most production projects, `pgvector` is the right answer: one database, transactional consistency, and operationally familiar. Specialized vector DBs win at very large scale (100M+ vectors) or for hybrid search features.

## Retrievers

A retriever wraps a vector store with retrieval **policy**. The base retriever does cosine similarity; the interesting variants change how the query is interpreted or how results are filtered:

- **`as_retriever()`** — the default; similarity search top-k.
- **MMR (max marginal relevance)** — penalize redundant results so the top-k are diverse, not all near-duplicates.
- **Multi-query retriever** — LLM rewrites the user's query into N variants, retrieves for each, merges.
- **Self-querying retriever** — LLM extracts metadata filters from the query (`"docs from 2024"` → `WHERE year=2024`).
- **Contextual compression** — retrieve broadly, then ask an LLM to keep only the relevant spans.
- **Parent document retriever** — retrieve on small chunks, return the larger parent document containing them.

The default works for prototypes; the variants are how you fix bad retrieval in production.

## Retrieval chains

Two canonical compositions to glue retrieval into a chain:

**`create_retrieval_chain`** (v1+ helper) — combines a retriever with a "combine documents" chain:

```python
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

document_chain = create_stuff_documents_chain(model, prompt)
retrieval_chain = create_retrieval_chain(vectorstore.as_retriever(), document_chain)

result = retrieval_chain.invoke({"input": "What's the refund policy?"})
# {"input": ..., "context": [Document, ...], "answer": "..."}
```

**LCEL by hand** — explicit, easier to customize:

```python
from langchain_core.runnables import RunnablePassthrough

chain = (
    {"context": vectorstore.as_retriever(), "question": RunnablePassthrough()}
    | prompt
    | model
    | StrOutputParser()
)
```

The helpers are convenient; the LCEL form is what you'll actually want for production customizations.

## Document chains: stuff, map-reduce, refine

How retrieved documents enter the prompt:

- **Stuff** — concatenate all retrieved docs into one prompt. Simplest, fastest, works when documents fit. Default and almost always right.
- **Map-reduce** — run the question against each doc separately, then summarize the answers. Slower (one LLM call per doc), used when stuffing exceeds context window.
- **Refine** — sequential: answer using doc 1, then refine the answer with doc 2, etc. Slow and order-dependent; rarely the right choice.

Modern context windows (100k+ tokens) mean stuff handles almost all realistic use cases; reach for map-reduce only when you genuinely have too much text to fit.

## Agentic RAG

A naive RAG pipeline retrieves once, hopes the chunks are good, and answers. **Agentic RAG** wraps the retrieval in an agent loop that can:

- **Rewrite the query** if initial retrieval is poor.
- **Grade retrieved chunks** for relevance before generation.
- **Grade the generated answer** against the source docs to detect hallucination.
- **Retry** with different queries when grading fails.

LangGraph is the natural home for this — the loop is a cyclic state graph. The patterns appear under names like **Corrective RAG** (CRAG), **Self-RAG**, and **Adaptive RAG** in the literature. See [Self-Improving Agent Patterns](../17_Self-Improving_Agent_Patterns/) for the broader family.

## Evaluating RAG

RAG quality depends on retrieval quality. Two things to measure separately:

- **Retrieval recall** — for a curated set of (question, ground-truth-doc) pairs, does the top-k retrieval include the ground truth? Measure with hit rate, MRR (mean reciprocal rank), or NDCG.
- **Answer quality** — given the retrieved docs and the question, is the generated answer faithful (no hallucinations not supported by docs) and useful (answers the question)?

LangSmith has built-in RAG evaluators (`context_relevance`, `faithfulness`, `answer_correctness`). Set up an eval suite before tuning — you can't optimize what you can't measure, and "vibes-based" RAG tuning is how teams ship regressions.
