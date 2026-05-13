# Backend API Design and Implementation Course Outlines

Five strong backend API design and implementation courses with published curriculum breakdowns.

---

## 1. Designing RESTful Web APIs

**Platform:** Pluralsight
**Instructor:** Shawn Wildermuth
**Rating:** Popular Pluralsight course with 722 reviews shown on the course page
**Duration:** 2h 6m
**URL:** https://www.pluralsight.com/courses/designing-restful-web-apis

### Curriculum

#### Course Overview
- Course overview

#### What Is REST?
- History of distributed computing
- HTTP in a nutshell
- HTTP in action
- What is REST
- An example of a well-designed API
- What we have learned

#### Designing a RESTful API
- Designing for REST
- Demo: using URIs
- Design verbs
- Demo: using verbs
- Idempotency in action
- Understanding idempotency
- Designing results
- Demo: designing your results
- Formatting results
- Demo: formatting results
- Hypermedia
- What we have learned

#### Handling More Complex Scenarios in Your API
- Designing associations
- Demo: associations
- Designing paging
- Demo: paging
- Error handling
- Demo: error handling
- Designing caching
- Demo: caching with ETags
- Functional APIs
- Demo: functional APIs
- Asynchronous APIs
- What we have learned

#### Versioning Your API
- Should you version your APIs
- Designing versioning
- Demo: versioning strategies
- What we have learned

#### Locking Down Your API
- APIs and security
- Cross-domain security
- Authentication and authorization
- Authentication types
- Understanding OAuth
- What we have learned

---

## 2. OpenAPI (Swagger): Designing & Documenting Rest APIs

**Platform:** Udemy
**Instructor:** Tobias Loser
**Rating:** Recently updated specialist course on OpenAPI and design-first API work
**Duration:** 2h 38m | 24 lectures | 5 sections
**URL:** https://www.udemy.com/course/openapi-swagger-designing-documenting-rest-apis/

### Curriculum

#### Introduction
- Legal notice (disclaimer)
- Welcome to the course
- What is the OpenAPI Specification?

#### Fundamentals of REST APIs
- Introduction to REST APIs
- URL structure: port, host, and path
- HTTP methods and status codes
- Data transfer: parameters and body
- Data formats: JSON, YAML, and XML
- Code-first vs. design-first API

#### The OpenAPI Specification
- Definitions, versions, and format
- Schema structure overview
- Info object
- Server object
- Paths object and path item object
- Parameter object and reference object
- Operation object
- Components object
- Tag object

#### Useful Tools for Management, Generation, and Documentation
- Interactive documentation
- OpenAPI editors (design-first)
- OpenAPI Generator CLI (design-first)

#### Summary & Tips
- Common mistakes and tips
- Further resources
- Summary

---

## 3. Back End Development and APIs

**Platform:** freeCodeCamp
**Instructor(s):** freeCodeCamp Team
**Rating:** Official freeCodeCamp certification track; Class Central lists it as a 300-hour self-paced free course
**Duration:** 300 hours | self-paced | guided lessons plus certification projects
**URL:** https://www.freecodecamp.org/learn/back-end-development-and-apis

### Curriculum

#### Node.js Foundations
- Learn Node.js REPL
- Learn how to build an NPM module
- Build a prime number checker module
- Learn Node.js common modules
- Learn Node.js by building a web server

#### HTTP, REST, and Express Foundations
- Learn Express by building a random joke app
- Build a personal profile app
- Learn Express middleware by building a submission form
- Build a data sanitizer
- Learn Express by building a weather service API

#### Microservices and Error Handling
- Build a timestamp microservice
- Learn error handling in Express by building a bank API

#### Real-Time Backend Work
- Learn WebSockets by building a resource monitor
- Build a chat app

#### Published Syllabus Topics
- Introduction to Node.js
- Node.js core libraries
- Node Package Manager
- HTTP and the Web Standards Model
- REST API and web services
- Introduction to Express
- Express middleware
- Error handling in Express
- WebSockets
- Node and SQL
- Security and privacy
- Authentication
- Tooling and deployment

---

## 4. Spring Boot REST APIs Ultimate Course

**Platform:** Udemy
**Instructor:** Nam Ha Minh
**Rating:** 4.6/5 (215 ratings)
**Duration:** Comprehensive multi-section course for building a weather API system and multiple API clients
**URL:** https://www.udemy.com/course/spring-boot-rest-apis-ultimate/

### Curriculum

#### REST API Core Concepts
- Understand URIs, URLs, and URNs
- HTTP methods and status codes
- Understand HATEOAS

#### Code Your First REST APIs
- Code your first REST API
- Code your second REST API
- Code your third REST API

#### REST API Design Best Practices
- Resource naming convention
- HTTP methods and status codes
- Use hypermedia (HATEOAS)
- APIs versioning
- Secure APIs
- Document APIs
- APIs caching
- APIs rate limit

#### Overview of the Sample System
- Overview of Weather Forecast API system
- Primary workflows of API usage
- Overview of sample applications
- Overview of database design
- Overview of system architecture

#### Referential Project Code
- Request access to GitHub repo
- Browse project code in web browser
- Download project code from GitHub
- Clone project code in command line
- Clone project code in IDE
- Browse code at a specific commit
- Disconnect from remote repository

#### Design Our REST APIs
- What are OpenAPI and Swagger
- Explore a sample API design with Swagger
- Design an example API with Swagger
- Generate server code for example API
- Check embedded docs for example API
- Generate client code for example API
- Package and run example API on localhost
- Deploy example API on Heroku
- API design exercise

#### Additional Published Scope Areas
- Implement REST APIs with Spring Boot
- Handle errors for REST APIs
- Validate REST API requests
- Test REST APIs with unit and integration tests
- Secure REST APIs with Spring Security, JWT, and OAuth2
- Secure authorization and resource servers
- Build client applications that consume the API

---

## 5. Mastering REST APIs with FastAPI

**Platform:** Packt / O'Reilly
**Instructor:** Jose Salvatierra Fuentes
**Rating:** Specialist production-focused FastAPI course; Packt lists a public rating and O'Reilly carries the full table of contents
**Duration:** 8h 47m | 11 chapters
**URL:** https://www.oreilly.com/library/view/mastering-rest-apis/9781835464694/

### Curriculum

#### Chapter 1: Course Introduction
- Community
- Welcome to this course
- What is an API?
- What is REST?

#### Chapter 2: Working with FastAPI
- Your first FastAPI app
- Initial app setup
- Linting, formatting, and sorting imports
- Social media API: adding posts
- Splitting the API into files with `APIRouter`
- Adding comments to the social media API

#### Chapter 3: Introduction to pytest
- The basics of pytest
- Getting started with FastAPI tests
- Creating posts in tests
- Adding tests for posts
- Adding comments tests

#### Chapter 4: Working with Async Databases
- Installing requirements for async databases in FastAPI
- Creating a config file using Pydantic
- Different configurations per environment
- Config caching and how to get the config object
- Async database setup with FastAPI
- Database connection with lifespan events in FastAPI
- Run your FastAPI test in test mode
- Using a database in the FastAPI router

#### Chapter 5: Logging in FastAPI Applications
- Python logging: loggers, handlers, and formatters
- Logger hierarchies and naming
- Adding logging configuration for FastAPI applications
- Configuring multiple loggers
- Adding file handlers for saving logs
- Adding logging to FastAPI endpoints
- Filters and custom filters
- Logging `HTTPException`s with an exception handler
- Correlation IDs
- JSON-formatted log files
- Obfuscating email addresses with a custom filter
- Adding Logtail for cloud logging
- Enabling Logtail only in production

#### Chapter 6: User Authentication with FastAPI
- Installing requirements and understanding JWTs
- Adding a users table and retrieving users by email
- Adding user registration and tests
- Adding tests for the user registration endpoint
- Hashing passwords with `passlib`
- Generating the access token
- Retrieving the current user with a token
- Using the current user in the API router
- Dependency injection for getting the user
- Adding user relationships to other tables
- OAuth Password Bearer and Swagger auth

#### Chapter 7: Many-to-Many Relationships
- Adding a table for post likes
- Adding an API route to like posts
- Extracting reusable queries with SQLAlchemy
- Query string arguments and data sorting with `Enum`

#### Chapter 8: User Email Confirmation
- Creating the confirmation token
- Decoding the confirmation token
- Adding a user confirmation endpoint
- Requiring user confirmation for authenticated requests
- Mailgun setup and configuration
- Sending emails and testing with Python
- Sending a confirmation email on registration
- Sending emails with background tasks

#### Chapter 9: File Uploads with FastAPI
- Configuration for Backblaze B2
- Internal library for Backblaze B2
- Writing the file upload endpoint
- Writing tests for file upload

#### Chapter 10: Background Tasks for Image Generation
- Model and database changes for image generation
- Configuration for DeepAI
- Generating images using background tasks
- Executing image generation in the FastAPI endpoint

#### Chapter 11: FastAPI Deployments and Application Management
- Updating the project to Pydantic v2
- Deploying a FastAPI app to Render
- Adding a free PostgreSQL database
- Error management with Sentry
- Continuous integration with GitHub Actions for Python apps

---

## Summary Comparison

| Course | Platform | Duration | Level | Price | Focus |
|--------|----------|----------|-------|-------|-------|
| Designing RESTful Web APIs | Pluralsight | 2h 6m | Beginner | Paid subscription | Design-first REST fundamentals: URIs, verbs, idempotency, paging, caching, versioning, security |
| OpenAPI (Swagger): Designing & Documenting Rest APIs | Udemy | 2h 38m | Beginner -> Intermediate | Paid | OpenAPI, design-first workflow, documentation, generators, and tooling |
| Back End Development and APIs | freeCodeCamp | 300 hours self-paced | Intermediate | Free | Node.js and Express implementation track with projects, microservices, WebSockets, and deployment |
| Spring Boot REST APIs Ultimate Course | Udemy | Multi-section comprehensive course | Intermediate | Paid | End-to-end Java REST API engineering: design, validation, testing, security, docs, and client integration |
| Mastering REST APIs with FastAPI | Packt / O'Reilly | 8h 47m | Intermediate -> Advanced | Paid subscription / paid video | Production-focused Python API work: testing, async DBs, logging, auth, uploads, background jobs, CI/CD |
