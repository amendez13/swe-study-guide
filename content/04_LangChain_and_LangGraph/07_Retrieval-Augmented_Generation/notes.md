# Retrieval-Augmented Generation (RAG)

How you make an LLM answer questions about data it wasn't trained on — without fine-tuning. The pipeline has seven well-known stages and a handful of tuning knobs that determine whether it works or hallucinates.

## Key Points

- **Seven stages** — load, split, embed, store, retrieve, augment, generate. First four at index time; last three per query.
- **Document loaders** — produce uniformly-shaped `Document` objects (`page_content`, `metadata`) from PDFs, URLs, folders, Notion, etc.
- **Text splitting** — `RecursiveCharacterTextSplitter` is the default; tune `chunk_size` (500-1500) and `chunk_overlap` (10-20%).
- **Embeddings** — same model for indexing and retrieval; don't mix providers in one index.
- **Vector stores** — Chroma for dev, `pgvector` for most production, specialized DBs (Pinecone, Qdrant) at scale.
- **Retrievers** — MMR for diversity, multi-query for paraphrase coverage, self-querying for metadata filters, contextual compression for noise reduction.
- **`create_retrieval_chain`** — the helper; hand-rolled LCEL is easier to customize.
- **Stuff vs map-reduce vs refine** — stuff is right almost always given modern context windows.
- **Agentic RAG** — wrap retrieval in a graph with query rewriting, relevance grading, and hallucination grading.
- **Evaluation** — measure retrieval recall and answer faithfulness separately; LangSmith has built-in RAG evaluators.

## Example

A minimal but realistic RAG pipeline over a folder of markdown docs, using local Chroma + OpenAI embeddings, with a hand-rolled LCEL retrieval chain:

```python
from langchain_chroma import Chroma
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


def build_index(docs_dir: str = "./docs", persist_dir: str = "./chroma_db"):
    # 1. Load
    loader = DirectoryLoader(docs_dir, glob="**/*.md", loader_cls=TextLoader)
    raw_docs = loader.load()
    print(f"Loaded {len(raw_docs)} docs")

    # 2. Split
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = splitter.split_documents(raw_docs)
    print(f"Produced {len(chunks)} chunks")

    # 3. Embed + 4. Store
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
        persist_directory=persist_dir,
    )
    return vectorstore


def build_chain(vectorstore):
    # 5. Retrieve — top-3 with MMR for diversity
    retriever = vectorstore.as_retriever(
        search_type="mmr",
        search_kwargs={"k": 3, "fetch_k": 10, "lambda_mult": 0.5},
    )

    # 6. Augment — splice retrieved docs into a prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "Answer the user's question using only the context below. "
         "If the context doesn't contain the answer, say you don't know — "
         "do not invent facts.\n\n"
         "Context:\n{context}"),
        ("user", "{question}"),
    ])

    def format_docs(docs):
        return "\n\n---\n\n".join(
            f"[{d.metadata.get('source', 'unknown')}]\n{d.page_content}"
            for d in docs
        )

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    # 7. Generate — composed end to end with LCEL
    return (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | model
        | StrOutputParser()
    )


if __name__ == "__main__":
    # Index once
    vs = build_index()

    # Query many
    chain = build_chain(vs)
    print(chain.invoke("What's the refund policy?"))
    print(chain.invoke("How do I rotate my API key?"))
```

What's worth noticing:

- **MMR** (`search_type="mmr"`) returns 3 diverse chunks pulled from 10 candidates — no near-duplicates dominating the prompt.
- **`format_docs`** stamps each chunk with its source path; the prompt sees provenance, which the model can cite in its answer.
- **"Say you don't know"** in the system prompt is the single most effective hallucination guard you'll add.
- **Persist directory** — Chroma writes to disk, so subsequent runs reuse the index without re-embedding.

When this pipeline gives bad answers, the fix is almost never "use a bigger model." Look at retrieval first (are the right chunks coming back?), then at chunking (are chunks the right size?), then at the prompt. Generation is rarely the bottleneck.
