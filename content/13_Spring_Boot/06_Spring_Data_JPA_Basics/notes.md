# Spring Data JPA Basics

Store data with Spring Data JPA: map an entity, declare a repository, and keep entities behind DTOs at the API boundary.

## Key points

- The JPA starter plus an embedded database gives a working persistence stack with no configuration.
- Entities are classes with an `@Id` and a no-argument constructor; records cannot be entities.
- A repository interface gets its CRUD implementation from Spring Data at startup.
- Controllers return DTO records, not entities.
- A `@Transactional` service method saves changes to managed entities at commit.

## Example

Run the [repository example](#13_Spring_Boot/06_Spring_Data_JPA_Basics/concepts/repositories) with the JPA starter and H2, and add the [DTO controller](#13_Spring_Boot/06_Spring_Data_JPA_Basics/concepts/entities-dtos-and-pojos). Watch the SQL that Hibernate logs.

```sh
./mvnw spring-boot:run -Dspring-boot.run.arguments=--spring.jpa.show-sql=true
curl -s http://localhost:8080/api/books
```
