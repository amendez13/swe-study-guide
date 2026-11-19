# Spring Project Anatomy and Startup — Drills

Predict the result before running the example.

## Predict the missing controller

The main class is `com.example.study.StudyApplication`. A teammate adds this controller. What does `GET /api/ping` return, and why?

```java
package com.example.api;

@RestController
class PingController {
    @GetMapping("/api/ping")
    String ping() {
        return "pong";
    }
}
```

**Answer**

404. Component scanning starts at `com.example.study`, and `com.example.api` is outside it, so the controller is never registered. Move it to `com.example.study.api`, or below. Widening the scan with `scanBasePackages` also works but hides a layout problem. See [project layout](#13_Spring_Boot/33_Spring_Project_Anatomy_and_Startup/concepts/project-layout).

## Order the startup output

The app below prints three lines. In which order, and why?

```java
@Component
class Catalog {
    Catalog() {
        System.out.println("A: Catalog created");
    }
}

@Configuration
class StartupConfig {
    @Bean
    CommandLineRunner runner() {
        return args -> System.out.println("B: runner");
    }

    @EventListener(ApplicationReadyEvent.class)
    void ready() {
        System.out.println("C: ready");
    }
}
```

**Answer**

A, then B, then C. Beans are created during the context refresh. Runners are called after the refresh, and `ApplicationReadyEvent` is published last, once the runners have finished. See [how an app starts](#13_Spring_Boot/33_Spring_Project_Anatomy_and_Startup/concepts/how-an-app-starts).
