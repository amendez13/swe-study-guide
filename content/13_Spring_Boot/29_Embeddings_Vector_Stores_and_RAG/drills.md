# Embeddings, Vector Stores, and RAG — Drills

Predict the result before running the example.

## Predict the empty search

A team ingested its policy documents with an OpenAI embedding model. Later it switched `spring.ai.model.embedding` to a local Ollama model to save money, without re-ingesting. What happens to searches?

**Answer**

They return irrelevant documents or none at all. Query vectors now come from a different model, so they cannot be compared with the stored ones, and if the dimensions differ the store may reject the query. Embed documents and queries with the same model, and re-ingest everything after changing it. See [embeddings](#13_Spring_Boot/29_Embeddings_Vector_Stores_and_RAG/concepts/embeddings).

## Keep tenants apart

The assistant serves several libraries from one vector store. Each chunk has a `library` metadata field. Write the search request so that a question from library `north` retrieves only that library's documents.

**Answer**

```java
SearchRequest request = SearchRequest.builder()
        .query(question)
        .topK(4)
        .filterExpression("library == 'north'")
        .build();
```

Take the library id from the authenticated user, never from the question text, so a user cannot ask for another tenant's data. With the advisor, pass the filter per request as an advisor parameter. See [vector stores](#13_Spring_Boot/29_Embeddings_Vector_Stores_and_RAG/concepts/vector-stores).
