# PostgreSQL Course Outlines

Five highly rated PostgreSQL courses with full curriculum breakdowns.

---

## 1. SQL and PostgreSQL: The Complete Developer's Guide

**Platform:** Udemy
**Instructor:** Stephen Grider
**Rating:** 4.7/5 (12,500+ ratings)
**Duration:** 22h 12m | 289 lectures | 37 sections
**URL:** https://www.udemy.com/course/sql-and-postgresql/

### Curriculum

#### Simple — But Powerful — SQL Statements
- What is PostgreSQL All About?
- Database Design
- Database Terminology
- Creating Tables
- Analyzing CREATE TABLE
- Inserting Data Into a Table
- Retrieving Data with Select
- Calculated Columns
- String Operators and Functions

#### Filtering Records
- Filtering Rows with "Where"
- Compound "Where" Clauses
- "Where" With Lists
- Calculations in "Where" Clauses
- Updating Rows
- Deleting Rows

#### Working with Tables
- Approaching Database Design
- One-to-Many and Many-to-One Relationships
- One-to-One and Many-to-Many Relationships
- Primary Keys and Foreign Keys
- Understanding Foreign Keys
- Auto-Generated IDs
- Creating Foreign Key Columns
- Foreign Key Constraints Around Insertion
- Constraints Around Deletion
- Setting Foreign Keys to Null on Delete

#### Relating Records with Joins
- Joining Data from Different Tables
- Alternate Forms of Syntax
- Missing Data in Joins
- Four Kinds of Joins (Inner, Left Outer, Right Outer, Full Outer)
- Each Join in Practice
- Does Order Matter?
- Where with Join
- Three Way Joins

#### Aggregation of Records
- Picturing Group By
- Selecting Columns After Grouping
- Aggregate Functions
- Combining Group By and Aggregates
- A Gotcha with Count
- Filtering Groups with Having

#### Working with Large Datasets
- Investigating a Real Dataset
- Group By and Join Review with Real Data

#### Sorting Records
- The Basics of Sorting
- Two Variations on Sorting
- Offset and Limit

#### Unions and Intersections with Sets
- Handling Sets with Union
- Commonalities with Intersect
- Removing Commonalities with Except

#### Assembling Queries with SubQueries
- Subqueries in a Select
- Subqueries in a From
- Subqueries in a Join Clause
- Subqueries with Where
- The Not In Operator with a List
- Correlated Subqueries
- A Select Without a From

#### Selecting Distinct Records
- Selecting Distinct Values

#### Utility Operators, Keywords, and Functions
- The Greatest and Least Value in a List
- The Case Keyword

#### PostgreSQL Complex Datatypes
- Data Types Overview
- Numeric Data Types
- Character Types
- Boolean Data Types
- Times, Dates, and Timestamps
- Intervals

#### Database-Side Validation and Constraints
- Applying a Null Constraint
- Default Column Values
- Applying a Unique Constraint to One Column
- Multi-Column Uniqueness
- Adding a Validation Check
- Checks Over Multiple Columns

#### Database Structure Design Patterns
- Using a SQL Design Tool
- A Config-based Schema Designer

#### How to Build a 'Like' System
- Requirements of a Like System
- Designing a Like System
- Polymorphic Associations
- Alternative Implementations

#### How to Build a 'Mention' System
- Photo Mentions vs Caption Mentions
- Considerations on Photo Tags vs Caption Tags

#### How to Build a 'Hashtag' System
- Designing a Hashtag System
- Tables for Hashtags

#### How to Design a 'Follower' System
- Designing a Follower System

#### Implementing Database Design Patterns
- Creating Tables with Checks
- Posts, Comments, Likes, Photo Tags, Caption Tags Creation
- Creating Hashtags, Hashtag Posts, and Followers

#### Approaching and Writing Complex Queries
- Complex Queries with Real Instagram-like Data

#### Understanding the Internals of PostgreSQL
- Where Does Postgres Store Data?
- Heaps, Blocks, and Tuples
- Block Data Layout
- Heap File Layout

#### A Look at Indexes for Performance
- Full Table Scans
- What's an Index
- How an Index Works
- Creating an Index
- Benchmarking Queries
- Downsides of Indexes
- Index Types
- Automatically Generated Indexes
- Behind the Scenes of Indexes

#### Basic Query Tuning
- The Query Processing Pipeline
- Explain and Explain Analyze

#### Advanced Query Tuning
- Developing an Intuitive Understanding of Cost
- Calculating Cost by Hand
- Startup vs Total Costs
- Costs Flow Up

#### Simple Common Table Expressions
- Common Table Expressions (CTEs)

#### Recursive Common Table Expressions
- Recursive CTEs Step by Step
- Why Use Recursive CTEs?

#### Simplifying Queries with Views
- Creating a View
- When to Use a View
- Deleting and Changing Views

#### Optimizing Queries with Materialized Views
- Materialized Views
- Writing a Slow Query
- Creating and Refreshing Materialized Views
- Views vs Materialized Views

#### Handling Concurrency and Reversibility with Transactions
- Opening and Closing Transactions
- Transaction Cleanup on Crash
- Closing Aborted Transactions

#### Managing Database Design with Schema Migrations
- Migration Files
- Issues Solved by Migrations
- Generating and Writing Migrations
- Applying and Reverting Migrations

#### Schema vs Data Migrations
- Dangers Around Data Migrations
- Properly Running Data and Schema Migrations
- Transaction Locks
- Updating Values and Dropping Columns

#### Accessing PostgreSQL From APIs
- Building a Users Router
- Understanding Connection Pools
- Validating Connection Credentials

#### Data Access Pattern — Repositories
- The Repository Pattern
- Creating a Repository

#### Security Around PostgreSQL
- SQL Injection Exploits
- Handling SQL Injection with Prepared Statements
- Inserting, Updating, and Deleting Safely

#### Fast Parallel Testing
- Multi-DB Setup
- Isolation with Schemas
- Creating and Accessing Schemas
- Controlling Schema Access with Search Paths
- Programmatic Schema Creation
- Escaping Identifiers
- Parallel Tests

---

## 2. Mastering Postgres

**Platform:** Database School (formerly masteringpostgres.com)
**Instructor:** Aaron Francis
**Rating:** Highly rated (independent platform, no aggregated star rating)
**Duration:** 16h 13m | 118 lessons
**URL:** https://masteringpostgres.com/

### Curriculum

#### Introduction
- Introduction to the course
- Overview of course structure
- Postgres vs. everyone
- The psql CLI
- Introduction to schema

#### Data Types
- Integers
- Numeric
- Floating point
- Storing money
- NaNs and infinity
- Casting types
- Character types
- Check constraints
- Domain types
- Characters and collations
- Binary data
- UUIDs
- Boolean
- Enums
- Timestamps
- Timezones
- Dates and times
- Intervals
- Serial type
- Sequences
- Identity
- Network and MAC addresses
- JSON
- Arrays
- Generated columns
- Text search types
- Bit string
- Ranges
- Composite types
- Nulls

#### Constraints
- Unique constraints
- Exclusion constraints
- Foreign key constraints

#### Indexes
- Introduction to indexes
- Heaps and CTIDs
- B-Tree overview
- Primary keys vs. secondary indexes
- Primary key types
- Where to add indexes
- Index selectivity
- Composite indexes
- Composite range
- Combining multiple indexes
- Covering indexes
- Partial indexes
- Index ordering
- Ordering nulls in indexes
- Functional indexes
- Duplicate indexes
- Hash indexes
- Naming indexes

#### Understanding Query Plans
- Introduction to EXPLAIN
- EXPLAIN structure
- Scan nodes
- Cost and rows
- EXPLAIN ANALYZE

#### Queries
- Introduction to queries
- Inner joins
- Outer joins
- Subqueries
- Lateral joins
- ROWS FROM
- Filling gaps in sequences
- Subquery elimination
- Combining queries
- Set generating functions
- Indexing joins

#### Advanced SQL
- Cross joins
- Grouping
- Grouping sets, rollups, cubes
- Window functions
- CTEs
- CTEs with window functions
- Recursive CTE
- Hierarchical recursive CTE
- Handling nulls
- Row value syntax
- Views
- Materialized views
- Removing duplicate rows
- Upsert
- RETURNING keyword
- COALESCE + generated column

#### Full Text Search
- Introduction to full text search
- Searching with LIKE
- Vectors, queries, and ranks
- Websearch
- Ranking
- Indexing full text search
- Highlighting

#### JSON
- Intro to JSON
- JSON vs JSONB
- Validating JSON
- Creating JSON objects and arrays
- JSON extraction
- JSON containment
- JSON existence
- JSON recordset
- Updating JSON
- Indexing JSON parts
- GIN index

#### pgvector
- Intro to pgvector
- Vector embedding columns
- Find related articles
- Upsert vector embedding
- Semantic search
- Other operators
- Vector indexes

#### Bonus Interviews
- Heroku's glory days & Postgres vs the world (with Craig Kerstiens)
- Creating a Postgres platform (with Monica & Tudor from Xata.io)
- Bootstrapping an email service provider (with Jesse Hanley)

---

## 3. PostgreSQL for Everybody Specialization

**Platform:** Coursera (University of Michigan)
**Instructor:** Charles Russell Severance
**Rating:** 4.7/5 (1,434+ reviews)
**Duration:** ~57h across 4 courses | 43,880+ learners enrolled
**URL:** https://www.coursera.org/specializations/postgresql-for-everybody

### Curriculum

#### Course 1: Database Design and Basic SQL in PostgreSQL (14h)

**Module 1 — Introduction to SQL (6h)**
- History of relational databases
- SQL standards and architecture overview
- PythonAnywhere and DBeaver setup
- Creating and inserting data into initial tables
- psql commands and CRUD fundamentals

**Module 2 — Single Table SQL (3h)**
- PostgreSQL tables and command-line operations
- Data types in PostgreSQL
- Database keys and indexes
- Musical Track Database introduction using CSV data
- SERIAL fields and auto-increment functionality
- Common SQL commands (INSERT INTO, WHERE, ORDER BY)

**Module 3 — One-To-Many Data Models (2h)**
- Relational database design principles
- Keys in database structure
- Normalization concepts
- Building interconnected tables and joining data

**Module 4 — Many-To-Many Data Models (2h)**
- Many-to-many relationship structures
- Advanced normalization techniques
- Building roster management system

#### Course 2: Intermediate PostgreSQL (16h)

**Module 1 — SQL Techniques (7h)**
- Altering table schemas and columns
- Working with dates in SQL
- SELECT DISTINCT and GROUP BY
- Subqueries and their applications
- Concurrency and transactions management
- Creating and using stored procedures

**Module 2 — Using SQL Techniques (3h)**
- Parsing and reading CSV files into databases
- Creating properly normalized tables
- Loading and normalizing CSV data
- ALTER TABLE commands for schema adjustments

**Module 3 — Text in PostgreSQL (4h)**
- Text functions and character handling
- Character set implementations
- Hashtag algorithms and their attributes
- Index choices and optimization techniques
- Hashing concepts and cryptography basics

**Module 4 — Regular Expressions (2h)**
- Regular expression fundamentals and syntax
- Constructing patterns to match specific rows
- Practical applications in databases
- Using regex with flat files and email validation

#### Course 3: JSON and Natural Language Processing in PostgreSQL (16h)

**Module 1 — Natural Language (6h)**
- Row allocation and block structures in PostgreSQL
- Index implementation details
- Building inverted indexes with SQL
- Natural language indexing techniques

**Module 2 — Inverted Indexes with PostgreSQL (3h)**
- GIN-based inverted indexes
- ts_vector() and ts_query() functions
- Full-text search implementation
- String array-based indexes

**Module 3 — Python and PostgreSQL (4h)**
- Connecting Python to PostgreSQL
- Mail archive processing
- Search result ranking techniques

**Module 4 — JSON and PostgreSQL (3h)**
- JavaScript Object Notation fundamentals
- JSON handling in Python and PostgreSQL
- Working with APIs (Star Wars, PokéAPI examples)

#### Course 4: Database Architecture and NoSQL at Scale with Deno (11h)

**Module 1 — Scaling Databases (3h)**
- To SQL or to NoSQL?
- Scaling Relational Databases
- Database architecture overview

**Module 2 — Cloud Scale Applications (3h)**
- First Generation Cloud Applications
- Second Generation Cloud Applications
- The Emergence of BASE Solutions (NoSQL)
- Reacting to the Rise of NoSQL
- ACID versus BASE Architectures

**Module 3 — Deno KV (5h)**
- Intro to Deno and Deno KV
- Exploring Deno KV Architecture Through B-Trees
- Exploring CRUD in Deno KV
- Building a Deno KV Model with Secondary Indexes

---

## 4. Fundamentals of Database Engineering

**Platform:** Udemy
**Instructor:** Hussein Nasser
**Rating:** 4.7/5 (10,977+ ratings) | 109,495+ students
**Duration:** 27h | 11 sections
**URL:** https://www.udemy.com/course/database-engines-crash-course/

### Curriculum

#### ACID Properties
- ACID overview and critical properties (Atomicity, Consistency, Isolation, Durability)
- Practical demonstration on PostgreSQL
- Transaction isolation levels

#### Understanding Database Internals
- How tables and indexes are stored on disk
- Row-oriented vs column-oriented databases
- Pages, IO, and the heap
- Row ID and page layout

#### Database Indexing
- Index fundamentals and when to create indexes
- Primary vs secondary keys and performance impact
- Creating large tables in PostgreSQL for benchmarking
- Bitmap Index Scan and its benefits
- Concurrent index creation in production (CREATE INDEX CONCURRENTLY)
- Key vs non-key column database indexing
- Index-only scans and covering indexes

#### B-Tree vs B+Tree in Production Database Systems
- B-Tree and B+Tree theoretical and practical considerations
- B+Tree storage cost analysis
- Production database applications (PostgreSQL, MySQL)

#### Database Partitioning
- Horizontal vs vertical partitioning
- Range partitioning strategies with PostgreSQL
- Partition pruning
- Automated partition creation
- Advantages and disadvantages of partitioning

#### Database Sharding
- Consistent hashing
- Horizontal partitioning vs sharding
- When to shard and when not to

#### Concurrency Control
- Exclusive (write) and shared (read) locks
- Two-phase locking
- Double booking prevention with row-level locks
- Optimistic vs pessimistic concurrency control
- Dead locks and how to avoid them

#### Database Replication
- Master-standby replication setup
- Synchronous vs asynchronous replication
- PostgreSQL replication configuration
- Statement-based vs row-based replication

#### Database Cursors
- Server-side vs client-side cursors
- Cursor performance considerations
- Pros and cons of cursors

#### Connection Management
- Connection pooling patterns
- The cost of establishing database connections
- Node.js PostgreSQL connection pool implementation

#### Database Engines
- Storage engine comparisons (MyISAM, InnoDB, RocksDB, LevelDB)
- Engine switching in MySQL
- Embedded vs networked database engines

#### Database Security
- Homomorphic encryption
- Database security best practices

#### System Design
- Backend engineering and scaling considerations
- Database design principles at scale

---

## 5. PostgreSQL Learning Path (5 Courses)

**Platform:** Pluralsight
**Instructor:** Pinal Dave
**Rating:** 4.0/5 (avg. across courses)
**Duration:** ~11h total across 5 courses
**URL:** https://www.pluralsight.com/authors/pinal-dave

### Curriculum

#### Course 1: PostgreSQL: Getting Started (1h 52m)

**Installation and Configuration (24m)**
- PostgreSQL or Postgres — a brief history of the name
- PostgreSQL important features
- PostgreSQL limits
- Prominent users of PostgreSQL
- Installing PostgreSQL
- Loading sample data

**Creating and Accessing Database Tables (24m)**
- Restore database
- Restore table schema only
- Copy a single table schema and data
- Generate HTML report for dependencies

**Data Operations — Select, Update, Delete (29m)**
- Retrieve data from table
- Order data by column names
- Count distinct values
- Using HAVING clause
- Update table with new data, insert data
- Generate script with pgAdmin
- Delete rows from table

**Database Joins — Retrieving Data From Multiple Tables (30m)**
- Inner Join
- Left Outer Join
- Right Outer Join
- Cross Join
- Full Outer Join

#### Course 2: PostgreSQL: Introduction to SQL Queries (2h 19m)

**Introduction to Various Data Types (50m)**
- Advantages of proper data types
- Different data types overview
- Create table with different data types
- Boolean columns accepting yes/no
- Data type and default values
- Incorrect data type and problems
- Data type and integrity
- Data type and MAC address

**Table Operations: Schemas, Constraints, and Keys (44m)**
- What is a schema?
- Two schemas with same table name
- Check constraint
- NOT-NULL constraint
- Unique constraint
- Primary key
- Foreign key

**Data Operations: Insert, Update, and Delete (38m)**
- SELECT statement
- Inserting data from another table
- Inserting single and multiple rows
- Updating single and multiple rows
- Deleting data from table

#### Course 3: PostgreSQL: Advanced SQL Queries (1h 42m)

**Operators and Functions (54m)**
- Logical operators
- Comparison operators
- Mathematical operators and functions
- Mathematical advanced operators and functions
- String operators and functions
- Date time operators and functions
- Aggregate functions

**Type Conversion (21m)**
- Implicit and explicit type conversion
- Impact of type conversion

**Transactions (18m)**
- Significance of transactions
- Update statements within transactions
- Transaction syntax (BEGIN, COMMIT, ROLLBACK)

#### Course 4: PostgreSQL: Advanced Server Programming (2h 14m)

**Triggers (35m)**
- What is a trigger?
- Types of triggers (BEFORE, AFTER, INSTEAD OF)
- Notes on triggers
- Data integrity with triggers
- Data auditing with triggers

**Rules and Alternatives (50m)**
- What is a rule?
- Types of rules
- Rules and views for SELECT
- Rules and views for table modification
- Triggers vs rules for table modification

**Procedural Languages (45m)**
- What are procedural languages?
- Types of PLs
- PL/pgSQL design goals and advantages
- Structure of PL/pgSQL
- Basics: variables, control structures, loops
- Procedures and error handling
- Procedure and control structures

#### Course 5: PostgreSQL: Index Tuning and Performance Optimization (3h 7m)

**Understanding Significance of EXPLAIN Keyword (41m)**
- What is EXPLAIN?
- Various options of EXPLAIN
- Query plan and cost
- Query plan and conditions
- Query plan and advanced conditions
- EXPLAIN ANALYZE

**Improving Query Performance with Indexes (37m)**
- What is an index?
- Types of indexes
- B-Tree index internals, advantages, and disadvantages
- Index and query performance
- Multicolumn index and covering index
- Order of column in index
- Index maintenance with REINDEX

**Index Tuning for Complex Queries (40m)**
- Unique index
- Difference between key, index, and constraint
- Primary key constraint and catalog tables
- Unique constraint and catalog tables
- Case insensitive search and performance
- Partial index

**Best Practices to Populate Large Database (24m)**
- Disable autocommit for bulk loading
- COPY command for efficient data import
- Remove indexes before bulk insert, rebuild after
- VACUUM command

---

## Summary Comparison

| Course | Platform | Duration | Level | Price | Focus |
|--------|----------|----------|-------|-------|-------|
| SQL and PostgreSQL (Grider) | Udemy | 22h | Beginner → Advanced | Paid | Comprehensive SQL + PG, schema design patterns, API integration, testing |
| Mastering Postgres (Francis) | Database School | 16h | Intermediate → Advanced | Paid | Deep PG-specific: data types, indexes, EXPLAIN, FTS, JSON, pgvector |
| PostgreSQL for Everybody (Severance) | Coursera | 57h (4 courses) | Beginner → Advanced | Free audit / Paid cert | Academic, structured: design → intermediate → NLP/JSON → architecture |
| Fundamentals of DB Engineering (Nasser) | Udemy | 27h | Intermediate → Advanced | Paid | Database internals: ACID, B-trees, partitioning, replication, sharding |
| PostgreSQL Learning Path (Dave) | Pluralsight | 11h (5 courses) | Beginner → Intermediate | Subscription | Scenario-driven: data types, queries, triggers, PL/pgSQL, index tuning |
