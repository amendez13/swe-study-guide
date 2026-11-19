# Method Security and Data Ownership — Drills

Predict the result before running the example.

## Find the ownership hole

Ada and Grace are both members. Ada owns note 1. What happens when Grace calls `GET /api/notes/1` and `PUT /api/notes/1` against this controller? Fix the hole.

```java
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

@RestController
class LeakyNoteApi {
    private final NoteRepository notes;

    LeakyNoteApi(NoteRepository notes) {
        this.notes = notes;
    }

    @GetMapping("/api/notes/{id}")
    Note one(@PathVariable long id) {
        return notes.findById(id).orElseThrow();
    }

    @PutMapping("/api/notes/{id}")
    Note replace(@PathVariable long id, @RequestBody Note body) {
        return notes.save(body);
    }
}
```

**Answer**

Grace can read Ada's note, and the PUT saves whatever the body contains, including an `id` and `owner` of Grace's choosing. Look up the note with `findByIdAndOwner(id, user.getUsername())` and return 404 when it is empty. Accept a `NewNote`-style record instead of the entity and copy only the text onto the loaded note. See [scope queries to the owner](#13_Spring_Boot/09_Method_Security_and_Data_Ownership/concepts/scope-queries-to-the-owner).

## Predict an annotation that does nothing

A librarian-only rule is on the service, but members can still retire books. Method security is enabled. Why is the rule skipped?

```java
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Service;

@Service
class ShelfService {
    void retireAll(java.util.List<String> titles) {
        titles.forEach(this::retire);
    }

    @PreAuthorize("hasRole('LIBRARIAN')")
    void retire(String title) {
        System.out.println("Retired " + title);
    }
}
```

**Answer**

`retireAll` calls `retire` on `this`, not through the Spring proxy, so the authorization interceptor never runs. Put the annotation on `retireAll` (the method other beans call) or move `retire` to another bean. The same proxy rule applies to `@Transactional`; see [enable method security](#13_Spring_Boot/09_Method_Security_and_Data_Ownership/concepts/enable-method-security).
