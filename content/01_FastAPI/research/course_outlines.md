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

## 2. Python API Development - Comprehensive Course for Beginners

**Platform:** freeCodeCamp (YouTube, free)
**Instructor:** Sanjeev Thiyagarajan
**Rating:** Widely praised — millions of views, highly recommended in the Python community
**Duration:** 19 hours
**URL:** https://www.freecodecamp.org/news/creating-apis-with-python-free-19-hour-course/

### Curriculum

#### Section 1: Intro
- Course overview and project walkthrough

#### Section 2: Setup & Installation
- Python installation (Mac/Windows)
- VS Code setup
- Virtual environments
- pip dependency management

#### Section 3: FastAPI Basics
- Installing FastAPI and uvicorn
- Path operations
- Postman intro
- HTTP request/response basics
- Pydantic schema validation
- CRUD operations
- HTTP status codes
- Automatic documentation (Swagger/ReDoc)

#### Section 4: Databases
- PostgreSQL installation
- Database schema and tables
- PgAdmin GUI
- SQL queries (SELECT, WHERE, operators, INSERT, UPDATE, DELETE)

#### Section 5: Python + Raw SQL
- Database connection with psycopg2
- Retrieving, creating, updating, and deleting posts with raw SQL

#### Section 6: ORM (SQLAlchemy)
- SQLAlchemy setup
- ORM-based CRUD operations replacing raw SQL

#### Section 7: Pydantic Models
- Pydantic models vs SQLAlchemy ORM models
- Response models and schema separation

#### Section 8: Authentication & Users
- User registration and password hashing
- JWT token basics and login flow
- OAuth2 PasswordRequestForm
- Protected routes and token verification

#### Section 9: Relationships
- SQLAlchemy foreign keys
- SQLAlchemy relationships
- Query parameters and environment variables

#### Section 10: Vote / Like System
- Votes table design
- SQL joins
- Likes endpoint

#### Section 11: Database Migrations
- Alembic setup
- Schema migration management

#### Sections 12–14: Deployment
- CORS middleware
- Heroku deployment
- Ubuntu server deployment with Nginx reverse proxy
- SSL/HTTPS setup

#### Section 15: Docker
- Writing a Dockerfile
- Docker Compose with Postgres container
- Bind mounts and Dockerhub

#### Section 16: Testing
- pytest basics (-s and -v flags)
- Fixtures and parametrize
- Testing exceptions
- FastAPI TestClient and integration tests

#### Section 17: CI/CD Pipeline
- GitHub Actions workflow
- Automated testing and deployment

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
| Python API Development | freeCodeCamp | 19h | Beginner → Advanced | Free | Social media API, SQL, Docker, CI/CD |
| FastAPI Fundamentals | Pluralsight | 3h 11m | Beginner | Subscription | Core concepts, SQLModel, auth |
| Complete FastAPI Course (OAuth & JWT) | Udemy | ~6h | Beginner → Intermediate | Paid | Auth focus, clean ORM foundation |
| Introduction to FastAPI | DataCamp | ~4h | Intermediate | Subscription | CRUD, async, testing |
