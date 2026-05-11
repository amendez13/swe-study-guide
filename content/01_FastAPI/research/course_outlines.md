# FastAPI Course Outlines

Five highly rated FastAPI courses with full curriculum breakdowns.

---

## 1. FastAPI - The Complete Course 2026 (Beginner + Advanced)

**Platform:** Udemy
**Instructors:** Eric Roby & Chad Darby
**Rating:** 4.6/5 (10,590+ ratings) — #1 bestselling FastAPI course on Udemy
**Duration:** 21h 28m | 241 lectures | 19 sections
**URL:** https://www.udemy.com/course/fastapi-the-complete-course/

### Curriculum

- **Python Refresher** — string formatting, lists, tuples, sets, functions, imports, OOP
- **Project 1** — first FastAPI app, HTTP request methods, path and query parameters
- **Project 2** — CRUD operations, Pydantic schema validation, status codes, Swagger docs
- **Project 3** — SQLAlchemy ORM, database setup, table models
- **Project 3.5** — extended database work, table relationships, foreign keys
- **Project 4: TodoApp** — full CRUD REST API with SQLite, modular routers, bcrypt password hashing
- **Project 5** — authentication and authorization, OAuth2, JWT token creation and verification, production-ready PostgreSQL, full-stack frontend integration, deployment

### Key Topics

- Modern authentication (OAuth2 + JWT + bcrypt)
- SQLAlchemy ORM with SQLite and PostgreSQL
- API Router for modular code organization
- Full-stack application with HTML/JS frontend
- Production deployment

---

## 2. Mastering REST APIs with FastAPI

**Platform:** O'Reilly / Packt (also on Coursera)
**Instructor:** Jose Salvatierra (founder of Teclado)
**Rating:** Highly rated across platforms
**Duration:** ~8 hours | 11 chapters
**URL:** https://www.oreilly.com/videos/mastering-rest-apis/9781835464694/

### Curriculum

#### Chapter 1: Course Introduction (22m)
- What is an API?
- What is REST?

#### Chapter 2: Working with FastAPI (44m)
- Your first FastAPI app
- Initial app setup
- Linting, formatting, and import sorting
- Building a social media API — adding posts
- Splitting the API into files with APIRouter
- Adding comments to the social media API

#### Chapter 3: Introduction to pytest (36m)
- The basics of pytest
- Getting started with FastAPI tests
- Creating posts in tests
- Adding tests for posts
- Adding comment tests

#### Chapter 4: Working with Async Databases (48m)
- Installing async database requirements
- Creating a config file using Pydantic
- Different configurations per environment
- Config caching and retrieving the config object
- Async database setup with FastAPI
- Database connection with lifespan events
- Running tests in test mode
- Using a database in API routers

#### Chapter 5: Logging in FastAPI Applications (1h 26m)
- Python logging: loggers, handlers, and formatters
- Logger hierarchies and naming
- Adding logging configuration for FastAPI
- Configuring multiple loggers
- Adding file handlers for saving logs
- Logging to FastAPI endpoints
- Filters and custom filters
- Logging HTTPExceptions with an exception handler
- Correlation IDs for request tracing
- JSON-formatted log files
- Obfuscating email addresses with a custom filter
- Cloud logging with Logtail
- Enabling Logtail in production only

#### Chapter 6: User Authentication with FastAPI (1h 18m)
- What are JWTs?
- Adding a users table and retrieving users by email
- User registration endpoint and tests
- Password hashing with passlib
- Generating access tokens
- Retrieving the current user from a token
- Using the current user in API routers
- Dependency injection for user retrieval
- Adding user relationships to other tables
- OAuth2 Password Bearer and Swagger auth (optional)

#### Chapter 7: Many-to-Many Relationships (33m)
- Adding a post likes table
- API route for liking posts
- Extracting reusable queries with SQLAlchemy
- Query string arguments and data sorting with Enum

#### Chapter 8: User Email Confirmation (1h 5m)
- Creating the confirmation token
- Decoding the confirmation token
- User confirmation endpoint
- Requiring confirmation for authenticated requests
- Mailgun setup and configuration
- Sending emails with Python
- Sending a confirmation email on registration
- Sending emails with background tasks

#### Chapter 9: File Uploads with FastAPI (39m)
- Configuration for Backblaze B2
- Internal library for Backblaze B2
- Writing the file upload endpoint
- Writing tests for file upload

#### Chapter 10: Background Tasks for Image Generation (34m)
- Model and database changes for image generation
- Configuration for DeepAI (third-party service)
- Generating images using background tasks
- Executing image generation in a FastAPI endpoint

#### Chapter 11: FastAPI Deployments and Application Management (38m)
- Updating to Pydantic v2
- Deploying a FastAPI app to Render
- Adding a free PostgreSQL database
- Error management with Sentry
- Continuous integration with GitHub Actions

---

## 3. FastAPI Fundamentals

**Platform:** Pluralsight
**Instructor:** Reindert-Jan Ekker
**Rating:** Highly rated on Pluralsight
**Duration:** 3h 11m | Beginner level
**URL:** https://www.pluralsight.com/courses/fastapi-fundamentals

### Curriculum

#### Course Overview (1m 25s)

#### Introducing FastAPI (8m)
- What is FastAPI?
- Project overview
- Prerequisites and setup

#### First Steps (19m)
- Starting a FastAPI project
- Adding the first operation
- Running the project
- Exploring auto-generated documentation (Swagger UI)
- How FastAPI runs your code
- Async vs non-async functions

#### Serving Data with FastAPI (28m)
- Adding path parameters
- Serving car data
- Optional query parameters
- Typed parameters
- Get by ID with path parameters
- Debugging (PyCharm and VS Code)
- Returning 404 Not Found

#### Serving Structured Data Using Pydantic Models (40m)
- Creating a data model with Pydantic
- Pydantic field options
- Loading data from JSON
- Using Pydantic models in read operations
- HTTP methods recap
- POST to add new objects
- Separate input and output models
- PUT and DELETE implementation
- OpenAPI schema with Postman
- Adding example data
- Nested models

#### Using a Database with FastAPI (42m)
- Introducing SQLModel
- Creating a model class
- Creating the database
- Inserting a new record
- Querying the database
- Injecting the session (dependency injection)
- Implementing GET, PUT, and DELETE with DB
- Working with relations

#### Working with HTTP and FastAPI (32m)
- Code organization with APIRouter
- Serving a web page
- Dynamic HTML with Jinja templates
- Processing form data
- Status codes and error handling
- Middleware
- Headers and cookies
- CORS middleware

#### Adding Authentication (18m)
- Adding a user model
- Password hashing
- Unique and indexed columns
- HTTP Basic Authentication
- OAuth2

#### Testing and Deployment (15m)
- Unit testing
- Deployment options
- Deploying on Linux
- HTTPS

---

## 4. The Complete FastAPI Course with OAuth & JWT Authentication

**Platform:** Udemy
**Rating:** Highly rated on Udemy
**Duration:** ~8 sections
**URL:** https://www.udemy.com/course/fastapi-course-python/

### Curriculum

#### Section 1: Introduction & Installation
- What is an API and why FastAPI?
- FastAPI framework overview
- Setup and installation in a virtual environment
- Creating a basic API

#### Section 2: Path & Query Parameters
- Path parameters and how URLs are processed
- Query parameters
- Combining multiple parameters

#### Section 3: Models & Request Body
- Pydantic models for request and response schemas
- Defining data structure for API routes

#### Section 4: Connecting to the Database
- SQLAlchemy as ORM
- Establishing database connection
- Converting SQLAlchemy models to database tables

#### Section 5: Performing CRUD Operations
- Create, Read, Update, Delete routes
- Exception handling with appropriate HTTP status codes

#### Section 6: Creating Multiple Models & Establishing Relationships
- Multiple data models with foreign keys
- Secure password hashing with bcrypt
- API metadata

#### Section 7: Using API Router
- Modularizing routes across multiple files
- APIRouter for maintainability

#### Section 8: Authentication
- Validating user credentials
- Generating JWT tokens
- Restricting access to protected routes

---

## 5. Introduction to FastAPI

**Platform:** DataCamp
**Instructor:** Matt Eckerle
**Rating:** Highly rated, curated by DataCamp
**Duration:** ~4 hours | Interactive exercises
**URL:** https://www.datacamp.com/courses/introduction-to-fastapi

### Curriculum

#### Chapter 1: FastAPI Basics
- Why FastAPI? (overview and use cases vs Django/Flask)
- First application
- FastAPI vs Django comparison
- GET operations — path and query parameters
- Hello World exercise
- POST operations
- Pydantic request body models
- POST operation in action

#### Chapter 2: FastAPI Advanced Topics
- PUT and DELETE operations
- Error handling and HTTP status codes
- Status code classification
- Async and concurrent processing
- When to use async
- Asynchronous DELETE operation

#### Chapter 3: Building and Testing a JSON CRUD API
- FastAPI automated testing overview
- Unit tests vs system tests
- Writing system tests
- Building a full JSON CRUD API
- HTTP operations and CRUD steps
- DELETE operation response handling
- Complete CRUD API assembly
- Manual functional tests
- System tests vs functional tests
- Functional test implementation

---

## Summary Comparison

| Course | Platform | Duration | Level | Price | Focus |
|--------|----------|----------|-------|-------|-------|
| FastAPI - The Complete Course 2026 | Udemy | 21h 28m | Beginner → Advanced | Paid | Projects, full-stack, deployment |
| Mastering REST APIs with FastAPI | O'Reilly / Packt | ~8h | Intermediate → Advanced | Paid | Social media API, async DB, logging, JWT, email, file uploads, deployment |
| FastAPI Fundamentals | Pluralsight | 3h 11m | Beginner | Subscription | Core concepts, SQLModel, auth |
| Complete FastAPI Course (OAuth & JWT) | Udemy | ~6h | Beginner → Intermediate | Paid | Auth focus, clean ORM foundation |
| Introduction to FastAPI | DataCamp | ~4h | Intermediate | Subscription | CRUD, async, testing |
