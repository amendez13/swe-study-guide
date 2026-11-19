# Method Security and Data Ownership

## Enable method security

URL rules protect endpoints, but the same service method can be reached from several controllers, a scheduled job, or a message listener. `@EnableMethodSecurity` lets you put the rule on the method itself. `@PreAuthorize` evaluates a Spring Expression Language (SpEL) expression before the call and throws `AuthorizationDeniedException` if it is false, which Spring MVC returns as 403.

Expressions can use `hasRole`, `hasAuthority`, `authentication`, and method arguments by name, such as `#title`. Keep URL rules as a coarse outer layer and method rules as the precise inner one. This service lets only librarians retire books.

```java
import org.springframework.context.annotation.Configuration;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.stereotype.Service;

@Configuration
@EnableMethodSecurity
class MethodSecurityConfig {
}

@Service
class CatalogService {
    @PreAuthorize("hasRole('LIBRARIAN')")
    void retire(String title) {
        System.out.println("Retired " + title);
    }
}
```

[Spring Security docs](https://docs.spring.io/spring-security/reference/servlet/authorization/method-security.html)

## Record the owner of data

To restrict data to its owner, the data must record who owns it. Add an `owner` column and set it on the server from the authenticated user, never from the request body. `@AuthenticationPrincipal` injects the current principal into a controller method; with username and password login it is a `UserDetails`.

The app below is the base for this topic. Each member keeps private reading notes, and creating a note stamps it with the caller's username. Run it with the security and JPA starters, H2, and the [in-memory users](#13_Spring_Boot/08_Spring_Security_Foundations/concepts/users-and-password-encoding).

```java
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.Id;
import java.util.List;
import java.util.Optional;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.data.repository.ListCrudRepository;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
public class StudyApplication {
    public static void main(String[] args) {
        SpringApplication.run(StudyApplication.class, args);
    }
}

@Entity
class Note {
    @Id @GeneratedValue Long id;
    String owner;
    String text;

    protected Note() {
    }

    Note(String owner, String text) {
        this.owner = owner;
        this.text = text;
    }

    public Long getId() { return id; }
    public String getOwner() { return owner; }
    public String getText() { return text; }
}

interface NoteRepository extends ListCrudRepository<Note, Long> {
    List<Note> findByOwner(String owner);
    Optional<Note> findByIdAndOwner(Long id, String owner);
}

record NewNote(String text) {
}

@RestController
class NoteApi {
    private final NoteRepository notes;

    NoteApi(NoteRepository notes) {
        this.notes = notes;
    }

    @PostMapping("/api/notes")
    Note create(@AuthenticationPrincipal UserDetails user, @RequestBody NewNote input) {
        return notes.save(new Note(user.getUsername(), input.text()));
    }

    @GetMapping("/api/notes")
    List<Note> mine(@AuthenticationPrincipal UserDetails user) {
        return notes.findByOwner(user.getUsername());
    }
}
```

[Spring Security docs](https://docs.spring.io/spring-security/reference/servlet/integrations/mvc.html#mvc-authentication-principal)

## Scope queries to the owner

The most reliable ownership check is a query that cannot return another member's rows. Include the owner in the repository method, such as `findByIdAndOwner`, and treat an empty result as not found. A request for someone else's note then gets the same 404 as a note that does not exist, which also hides which identifiers are in use.

This endpoint reads one note through the owner-scoped finder from the [base example](#13_Spring_Boot/09_Method_Security_and_Data_Ownership/concepts/record-the-owner-of-data). Apply the same pattern to updates and deletes so every data path carries the owner.

```java
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

@RestController
class OneNoteApi {
    private final NoteRepository notes;

    OneNoteApi(NoteRepository notes) {
        this.notes = notes;
    }

    @GetMapping("/api/notes/{id}")
    ResponseEntity<Note> one(@PathVariable long id, @AuthenticationPrincipal UserDetails user) {
        return ResponseEntity.of(notes.findByIdAndOwner(id, user.getUsername()));
    }
}
```

[Spring Data JPA docs](https://docs.spring.io/spring-data/jpa/reference/jpa/query-methods.html)

## Ownership rules on methods

When the check needs logic, put it in a bean and call the bean from `@PreAuthorize` with `@beanName`. The expression below passes the note identifier and the authentication to `noteAccess.canDelete`, which allows the owner or a librarian. `@PostAuthorize` is the alternative when the rule depends on the returned object, available as `returnObject`.

Annotations work on Spring Data repository interfaces too, which secures a method for every caller that uses it. Method parameters are referenced by name, which works because Boot's Maven parent compiles with `-parameters`. Use this service with the [base example](#13_Spring_Boot/09_Method_Security_and_Data_Ownership/concepts/record-the-owner-of-data) and [method security enabled](#13_Spring_Boot/09_Method_Security_and_Data_Ownership/concepts/enable-method-security).

```java
import org.springframework.security.access.prepost.PostAuthorize;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.security.core.Authentication;
import org.springframework.stereotype.Component;
import org.springframework.stereotype.Service;

@Component("noteAccess")
class NoteAccess {
    private final NoteRepository notes;

    NoteAccess(NoteRepository notes) {
        this.notes = notes;
    }

    boolean canDelete(long id, Authentication auth) {
        var librarian = auth.getAuthorities().stream().anyMatch(a -> "ROLE_LIBRARIAN".equals(a.getAuthority()));
        return librarian || notes.findByIdAndOwner(id, auth.getName()).isPresent();
    }
}

@Service
class NoteService {
    private final NoteRepository notes;

    NoteService(NoteRepository notes) {
        this.notes = notes;
    }

    @PreAuthorize("@noteAccess.canDelete(#id, authentication)")
    void delete(long id) {
        notes.deleteById(id);
    }

    @PostAuthorize("returnObject.owner == authentication.name")
    Note load(long id) {
        return notes.findById(id).orElseThrow();
    }
}
```

[Spring Security docs](https://docs.spring.io/spring-security/reference/servlet/authorization/method-security.html#using_method_parameters)

## A delete button for the owner

The page should offer a delete button only to someone allowed to use it. Add the Thymeleaf Spring Security dialect, `thymeleaf-extras-springsecurity6`, which Boot manages and autoconfigures. Templates can then read the current authentication as `#authentication` and test rules with `sec:authorize`.

Hiding the button is a usability feature, not protection. The POST handler must still enforce the rule, here through the `NoteService.delete` method from the [ownership rules card](#13_Spring_Boot/09_Method_Security_and_Data_Ownership/concepts/ownership-rules-on-methods). Thymeleaf adds the CSRF token to the form.

```java
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;

@Controller
class NotePages {
    private final NoteService service;

    NotePages(NoteService service) {
        this.service = service;
    }

    @PostMapping("/notes/{id}/delete")
    String delete(@PathVariable long id) {
        service.delete(id);
        return "redirect:/notes";
    }
}
```

```html
<li th:each="note : ${notes}">
  <span th:text="${note.text}">Note</span>
  <form th:if="${note.owner == #authentication.name}" method="post"
        th:action="@{/notes/{id}/delete(id=${note.id})}">
    <button type="submit">Delete</button>
  </form>
</li>
```

[Thymeleaf Spring Security docs](https://github.com/thymeleaf/thymeleaf-extras-springsecurity)

## Show who is signed in

Templates and controllers can both show details of the signed-in user. In a template, `sec:authentication="name"` prints the username and `sec:authorize` renders an element only when an expression passes. In a controller, `@AuthenticationPrincipal` provides the principal for building a model.

Keep the page generic for anonymous visitors with `isAnonymous()` and `isAuthenticated()`. The sign-out form posts to `/logout`, Spring Security's default logout URL, with the CSRF token added by `th:action`.

```java
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
class AccountPage {
    @GetMapping("/account")
    String account(@AuthenticationPrincipal UserDetails user, Model model) {
        model.addAttribute("roles", user.getAuthorities());
        return "account";
    }
}
```

```html
<html xmlns:th="http://www.thymeleaf.org" xmlns:sec="http://www.thymeleaf.org/extras/spring-security">
<body>
  <p sec:authorize="isAuthenticated()">Signed in as <span sec:authentication="name">user</span></p>
  <p sec:authorize="hasRole('LIBRARIAN')">You can manage the catalog.</p>
  <ul><li th:each="role : ${roles}" th:text="${role.authority}">ROLE</li></ul>
  <form sec:authorize="isAuthenticated()" method="post" th:action="@{/logout}">
    <button type="submit">Sign out</button>
  </form>
</body>
</html>
```

[Spring Security docs](https://docs.spring.io/spring-security/reference/servlet/integrations/mvc.html)
