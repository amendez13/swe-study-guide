# Spring MVC Controllers and Templates

Build a small server-rendered page: generate a project, render data with Thymeleaf, inject a service, and accept form input.

## Key points

- start.spring.io generates the project; reuse it to find the dependency entries for a new feature.
- A `@Controller` returns a view name and fills the `Model`; a `@RestController` writes the return value as the body.
- Inject collaborators through a single constructor into `final` fields.
- Bind form fields to a record with `@ModelAttribute`, then redirect after the POST.
- A JavaScript bundle built into `target/classes/static` is served by the same app.

## Example

Generate the project with the [start.spring.io command](#13_Spring_Boot/03_Spring_MVC_Controllers_and_Templates/concepts/generate-a-project-with-start-spring-io). Run the [form example](#13_Spring_Boot/03_Spring_MVC_Controllers_and_Templates/concepts/change-data-through-an-html-form) with the list template and form, then add a book from the command line.

```sh
curl -i http://localhost:8080/books -d title=Accelerate -d pages=288
curl -s http://localhost:8080/ | grep Accelerate
```
