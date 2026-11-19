# Spring MVC Controllers and Templates — Drills

Predict the result before running the example.

## Predict the response body

Both methods return the string `"index"`, and a Thymeleaf template named `index.html` exists. What does a browser receive from `/a` and from `/b`?

```java
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@SpringBootApplication
public class StudyApplication {
    public static void main(String[] args) {
        SpringApplication.run(StudyApplication.class, args);
    }
}

@Controller
class PageController {
    @GetMapping("/a")
    String a() {
        return "index";
    }
}

@RestController
class TextController {
    @GetMapping("/b")
    String b() {
        return "index";
    }
}
```

**Answer**

`/a` renders the template as HTML because a `@Controller` return value is a view name. `/b` returns the five characters `index` as the body because `@RestController` adds `@ResponseBody`. Compare [a controller that renders a view](#13_Spring_Boot/03_Spring_MVC_Controllers_and_Templates/concepts/a-controller-that-renders-a-view).

## Stop a duplicate submission

After adding a book, the user presses refresh and the browser offers to resubmit the form. A second copy of the book appears. What should the handler return instead?

```java
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.ModelAttribute;
import org.springframework.web.bind.annotation.PostMapping;

record Book(String title, int pages) {
}

@Controller
class NewBookController {
    @PostMapping("/books")
    String add(@ModelAttribute Book book, Model model) {
        model.addAttribute("added", book);
        return "index";
    }
}
```

**Answer**

Return `"redirect:/"` after saving. The browser then issues a GET for `/`, and refreshing repeats the GET instead of the POST. Use flash attributes (`RedirectAttributes`) when the next page must show a confirmation. See [change data through an HTML form](#13_Spring_Boot/03_Spring_MVC_Controllers_and_Templates/concepts/change-data-through-an-html-form).
