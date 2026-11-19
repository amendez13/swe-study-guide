# Embeddings, Vector Stores, and RAG

Answer questions from your own documents: embed them, store the vectors, retrieve the best passages, and ground the model's answer in them.

## Key points

- RAG retrieves relevant passages at request time and puts them in the prompt; retrieval quality decides answer quality.
- Embeddings map meaning to vectors; use one embedding model for documents and queries.
- `VectorStore` adds and searches documents; metadata filters scope results, including per tenant.
- The ETL pipeline reads, splits, and loads documents; keep source metadata on each chunk.
- `RetrievalAugmentationAdvisor` wires retrieval into `ChatClient`; query transformers improve vague questions.

## Example

Run PostgreSQL with pgvector and a local Ollama embedding model, add the [ingestion component](#13_Spring_Boot/37_Embeddings_Vector_Stores_and_RAG/concepts/ingest-documents-with-an-etl-pipeline) and the [RAG chat client](#13_Spring_Boot/37_Embeddings_Vector_Stores_and_RAG/concepts/answer-questions-with-retrievalaugmentationadvisor), and ask a question about your own policy file.

```yaml
# compose.yaml
services:
  pgvector:
    image: pgvector/pgvector:pg18
    environment:
      POSTGRES_DB: study
      POSTGRES_USER: study
      POSTGRES_PASSWORD: study
    ports:
      - "5432:5432"
```

```properties
spring.ai.vectorstore.pgvector.initialize-schema=true
spring.datasource.url=jdbc:postgresql://localhost:5432/study
spring.datasource.username=study
spring.datasource.password=study
```

```sh
ollama pull nomic-embed-text
docker compose up -d pgvector
./mvnw spring-boot:run
```
