# Embeddings, Vector Stores, and RAG

## Retrieval-augmented generation

A model knows only its training data, which ends at a cutoff date and never included your private documents. Retrieval-augmented generation (RAG) closes that gap at request time. The application searches its own documents for passages relevant to the question, puts them into the prompt, and asks the model to answer from them.

RAG keeps knowledge in a store you control: update a document and the next answer reflects it, with no retraining. It also lets answers cite their sources. It does not make answers correct by itself. If retrieval finds the wrong passages, the model answers from the wrong facts, so retrieval quality is most of the work.

```text
question ──► embed ──► vector search ──► top passages
                                            │
           answer ◄── model ◄── prompt: rules + passages + question
```

[Spring AI docs](https://docs.spring.io/spring-ai/reference/concepts.html#concept-rag)

## Embeddings

An embedding model turns text into a vector, a list of hundreds of numbers, so that texts with similar meaning have vectors that point in similar directions. "How do I renew a loan?" and "extend my borrowing period" end up close together, though they share no words. Similarity search compares vectors, usually by cosine similarity.

Spring AI exposes embedding models through `EmbeddingModel`. Use the same model to embed the documents and the questions, because vectors from different models are not comparable. Not every chat provider offers embeddings; a local Ollama model or a hosted embedding API can sit beside an Anthropic chat model. When several model starters are present, select one per role.

```properties
spring.ai.model.chat=anthropic
spring.ai.model.embedding=ollama
spring.ai.ollama.embedding.options.model=nomic-embed-text
```

```java
float[] vector = embeddingModel.embed("How do I renew a loan?");
System.out.println(vector.length + " dimensions");
```

[Spring AI docs](https://docs.spring.io/spring-ai/reference/api/embeddings.html)

## Vector stores

A vector store saves documents with their embeddings and finds the nearest ones to a query vector. Spring AI's `VectorStore` interface covers PGVector, Redis, Elasticsearch, Qdrant, Chroma, and many more, plus an in-memory `SimpleVectorStore` for experiments. `add` embeds and stores documents; `similaritySearch` embeds the query and returns the closest matches.

Each `Document` carries text and metadata, such as its source file and section. Metadata filters narrow a search, for example to one product or one tenant. Use them for access control, so a user's question never retrieves another customer's documents.

```xml
<dependency>
  <groupId>org.springframework.ai</groupId>
  <artifactId>spring-ai-starter-vector-store-pgvector</artifactId>
</dependency>
```

```java
import java.util.List;
import java.util.Map;
import org.springframework.ai.document.Document;
import org.springframework.ai.vectorstore.SearchRequest;

vectorStore.add(List.of(new Document(
        "Loans last 21 days and can be renewed twice online.", Map.of("source", "loans.md"))));

List<Document> hits = vectorStore.similaritySearch(SearchRequest.builder()
        .query("how long can I keep a book")
        .topK(3)
        .similarityThreshold(0.5)
        .filterExpression("source == 'loans.md'")
        .build());
```

[Spring AI docs](https://docs.spring.io/spring-ai/reference/api/vectordbs.html)

## Ingest documents with an ETL pipeline

Documents must be loaded, split, and embedded before they can be searched. Spring AI models this as extract, transform, load. A `DocumentReader` extracts text from a file type, such as `TextReader`, or `TikaDocumentReader` for PDF and Word. A transformer such as `TokenTextSplitter` cuts long text into chunks. The vector store's `add` loads them.

Chunk size matters. Chunks that are too large dilute the match and waste prompt tokens; chunks that are too small lose context. Keep source metadata on every chunk, and re-ingest a document when it changes, deleting its old chunks first.

```java
import java.util.List;
import org.springframework.ai.document.Document;
import org.springframework.ai.reader.TextReader;
import org.springframework.ai.transformer.splitter.TokenTextSplitter;
import org.springframework.ai.vectorstore.VectorStore;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.Resource;
import org.springframework.stereotype.Component;

@Component
class PolicyIngestion {
    private final VectorStore vectorStore;
    private final Resource policy;

    PolicyIngestion(VectorStore vectorStore, @Value("classpath:docs/library-policy.md") Resource policy) {
        this.vectorStore = vectorStore;
        this.policy = policy;
    }

    void ingest() {
        List<Document> documents = new TextReader(policy).get();
        List<Document> chunks = new TokenTextSplitter().apply(documents);
        vectorStore.add(chunks);
    }
}
```

[Spring AI docs](https://docs.spring.io/spring-ai/reference/api/etl-pipeline.html)

## Answer questions with RetrievalAugmentationAdvisor

Spring AI wires retrieval into `ChatClient` as an advisor. `QuestionAnswerAdvisor` is the simple form: it searches the vector store with the user's question and appends the hits to the prompt. `RetrievalAugmentationAdvisor` is the modular form: a pipeline of query transformers, a document retriever, and a query augmenter that you configure piece by piece.

By default the augmenter tells the model to answer only from the context and to say so when the context does not contain the answer. Keep that rule. Without it, the model fills gaps from its training data and the answer looks sourced when it is not.

```java
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.rag.advisor.RetrievalAugmentationAdvisor;
import org.springframework.ai.rag.retrieval.search.VectorStoreDocumentRetriever;

ChatClient policyChat = builder
        .defaultAdvisors(RetrievalAugmentationAdvisor.builder()
                .documentRetriever(VectorStoreDocumentRetriever.builder()
                        .vectorStore(vectorStore)
                        .similarityThreshold(0.5)
                        .topK(4)
                        .build())
                .build())
        .build();

String answer = policyChat.prompt().user("Can I renew a loan three times?").call().content();
```

[Spring AI docs](https://docs.spring.io/spring-ai/reference/api/retrieval-augmented-generation.html)

## Improve retrieval quality

Most RAG failures are retrieval failures. Users ask short, vague, or follow-up questions such as "and for DVDs?" that match nothing on their own. Query transformers fix that before the search: `CompressionQueryTransformer` folds the chat history into a standalone question, and `RewriteQueryTransformer` rephrases a query for search. Each one costs an extra model call.

Measure before tuning. Keep a set of test questions with the passages that should be found, and check how often the retriever returns them as you change chunk size, `topK`, and the threshold. Combine the advisor with [chat memory](#13_Spring_Boot/28_Spring_AI_ChatClient_Prompts_and_Tools/concepts/conversation-memory-with-advisors) for a conversational assistant over your documents.

```java
import org.springframework.ai.rag.preretrieval.query.transformation.RewriteQueryTransformer;

RetrievalAugmentationAdvisor advisor = RetrievalAugmentationAdvisor.builder()
        .queryTransformers(RewriteQueryTransformer.builder()
                .chatClientBuilder(builder.build().mutate())
                .build())
        .documentRetriever(VectorStoreDocumentRetriever.builder().vectorStore(vectorStore).build())
        .build();
```

[Spring AI docs](https://docs.spring.io/spring-ai/reference/api/retrieval-augmented-generation.html#_pre_retrieval)
