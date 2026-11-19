# Beyond the Book

Short introductions to Spring projects the book does not cover, each a starting point for further study.

## Key points

- Spring Modulith verifies module boundaries and connects modules with persisted events.
- Spring Batch 6 runs chunked, restartable jobs; Boot 4's default job repository is in memory.
- Spring for GraphQL maps schema fields to controller methods; `@BatchMapping` avoids N+1 queries.
- STOMP over WebSocket pushes updates to clients; use an external broker relay with several instances.
- Spring Cloud adds gateways, central config, and discovery; on Kubernetes, use what the platform already provides.

## Example

Generate a project with `-d dependencies=web,graphql`, add the [schema and controller](#13_Spring_Boot/32_Beyond_the_Book/concepts/graphql-apis-with-spring-for-graphql), and query one book with only the fields you need.

```properties
spring.graphql.graphiql.enabled=true
```

```sh
curl -s http://localhost:8080/graphql -H 'Content-Type: application/json' \
  -d '{"query":"{ bookByIsbn(isbn: \"1\") { title author { name } } }"}'
```

Open `http://localhost:8080/graphiql` to explore the schema interactively.
