# Reactive Data with R2DBC

Read and write a relational database without blocking, from repository to HTTP response.

## Key points

- R2DBC drivers emit rows as a `Flux`, and backpressure reaches the database; every layer must be non-blocking.
- R2DBC is not an ORM: no lazy loading, relationships, or first-level cache.
- `@Table` records plus `ReactiveCrudRepository` give reactive CRUD; `@Query` takes native SQL.
- `R2dbcEntityTemplate` builds dynamic queries; inserts run only when subscribed.
- `@Transactional` on a publisher-returning method binds the transaction to the subscription.

## Example

Generate a project with `-d dependencies=webflux,data-r2dbc,h2`. H2 then runs in memory through its R2DBC driver. Add this schema, the [repository](#13_Spring_Boot/29_Reactive_Data_with_R2DBC/concepts/create-a-reactive-repository), the [seed runner](#13_Spring_Boot/29_Reactive_Data_with_R2DBC/concepts/load-data-with-r2dbcentitytemplate) and the [API controller](#13_Spring_Boot/29_Reactive_Data_with_R2DBC/concepts/return-data-reactively-from-an-api), then query an author.

```sql
-- src/main/resources/schema.sql
create table if not exists book (
    id bigint auto_increment primary key,
    title varchar(200) not null,
    author varchar(120) not null,
    pages int not null
);
```

```sh
curl -s http://localhost:8080/api/authors/Austen/books
```
