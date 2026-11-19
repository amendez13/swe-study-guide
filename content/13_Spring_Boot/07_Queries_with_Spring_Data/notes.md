# Queries with Spring Data

Read data with as little query code as the job allows: derived names first, then `@Query`, then hand-written JPA.

## Key points

- Derived method names are parsed and validated at startup.
- Use `Sort` for caller-chosen order and `OrderBy` in the name for a fixed order.
- Cap results with `First`/`Top` or a `Limit` parameter; page with `Pageable` and return `PagedModel` from controllers.
- Query by Example fits search forms that match on equality or text.
- `@Query` handles joins and aggregates; a record return type projects only the needed columns.
- A repository fragment with an `Impl` class holds dynamic queries built with the `EntityManager`.

## Example

Run the [derived query example](#13_Spring_Boot/07_Queries_with_Spring_Data/concepts/derived-query-methods) with the paging and search endpoints added, then try a few requests.

```sh
curl -s 'http://localhost:8080/api/books?page=0&size=2&sort=title'
curl -s 'http://localhost:8080/api/books/search?author=fow'
curl -s http://localhost:8080/api/stats/authors
```
