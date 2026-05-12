# LangChain and LangGraph Course Outlines

Five highly rated LangChain and LangGraph courses with full curriculum breakdowns, sourced from official platforms (LangChain Academy, DeepLearning.AI), a flagship paid Udemy course, and a Coursera specialization.

---

## 1. Foundation: Introduction to LangGraph (Python)

**Platform:** LangChain Academy (free)
**Instructors:** LangChain team (Lance Martin and others)
**Rating:** Official LangChain course; widely treated as the canonical reference
**Duration:** 6 modules, lesson-by-lesson video + notebooks
**URL:** https://academy.langchain.com/courses/intro-to-langgraph

### Curriculum

#### Module 1: Introduction
- Motivation
- Simple Graph
- LangSmith Studio
- Chain
- Router
- Agent
- Agent with Memory
- (Optional) Intro to Deployment

#### Module 2: State and Memory
- State Schema
- State Reducers
- Multiple Schemas
- Trim and Filter Messages
- Chatbot with Summarizing Messages and Memory
- Chatbot with Summarizing Messages and External Memory

#### Module 3: UX and Human-in-the-Loop
- Streaming
- Breakpoints
- Editing State and Human Feedback
- Dynamic Breakpoints
- Time Travel

#### Module 4: Building Your Assistant
- Parallelization
- Sub-graphs
- Map-reduce
- Research Assistant

#### Module 5: Long-Term Memory
- Short vs. Long-Term Memory
- LangGraph Store
- Memory Schema + Profile
- Memory Schema + Collection
- Build an Agent with Long-Term Memory

#### Module 6: Deployment
- Deployment Concepts
- Creating a Deployment
- Connecting to a Deployment
- Double Texting
- Assistants

---

## 2. LangChain - Agentic AI Engineering with LangChain & LangGraph

**Platform:** Udemy
**Instructor:** Eden Marco (LLM Specialist at Google Cloud)
**Rating:** 4.6+/5 with 71,000+ students enrolled
**Duration:** 19h 8m | 179 lectures | 28 sections
**URL:** https://www.udemy.com/course/langchain/

### Curriculum

A project-based course that builds agentic systems end-to-end. The curriculum is organized around seven complete projects plus prompt-engineering and "agents under the hood" theory sections.

#### Foundations
- Course introduction and Python setup
- LangChain v1+ overview and ecosystem (LangGraph, LangSmith)
- Prompt engineering theory — Chain of Thought, ReAct, Few-Shot prompting
- "Agents Under the Hood" — how LangChain agents work internally, tool calling primitives

#### Project 1: Hello World Chain
- First LangChain app, environment setup, basic chain composition

#### Project 2: Ice Breaker
- Real-world agent that scrapes a person's social media (LinkedIn, Twitter)
- Output parsers, custom agents, data collection pipelines

#### Project 3: Documentation Helper
- Retrieval-Augmented Generation (RAG) over technical documentation
- Document loaders, text splitting, embeddings, vector stores (Pinecone, FAISS)
- Conversational retrieval chains

#### Project 4: Code Interpreter
- ReAct agent that writes and executes Python in a sandbox
- Tool calling, controlled code execution, REPL integration

#### Project 5: Blog Analyzer / Medium Analyzer
- Multi-step reasoning over scraped articles
- Summarization, sentiment, fact extraction

#### Project 6: Reflection Agent
- Self-critique loop: agent reviews and revises its own output
- Generator/reflector dual-node patterns in LangGraph

#### Project 7: Reflexion Agent
- Self-correcting agent with external knowledge integration
- Memory of prior failures, structured Pydantic critiques

#### Project 8: Agentic RAG
- Self-correcting RAG with adaptive routing
- Query rewriting, hallucination grading, relevance grading
- Production-ready patterns

#### Wrap-up
- LangSmith tracing and evaluation
- Deployment and production considerations

---

## 3. AI Agents in LangGraph

**Platform:** DeepLearning.AI (free)
**Instructors:** Harrison Chase (LangChain CEO) and Rotem Weiss (Tavily CEO)
**Rating:** Free, taught by the framework's creator; one of the most-cited LangGraph intros
**Duration:** ~99 minutes, 10 lessons
**URL:** https://learn.deeplearning.ai/courses/ai-agents-in-langgraph

### Curriculum

1. **Introduction** (6m) — what an agent is, why LangGraph
2. **Build an Agent from Scratch** (12m) — implement a ReAct loop in pure Python so you understand what LangGraph is replacing
3. **LangGraph Components** (19m) — State, Nodes, Edges, Conditional Edges; rebuild the agent in LangGraph
4. **Agentic Search Tools** (5m) — Tavily integration; agentic search vs traditional web search
5. **Persistence and Streaming** (9m) — Checkpointers, thread state, streaming intermediate tokens
6. **Human in the Loop** (14m) — interrupts and state editing for human approval steps
7. **Essay Writer** (18m) — multi-node graph replicating a researcher's workflow
8. **LangChain Resources** (2m)
9. **Conclusion** (4m)
10. **Quiz** (10m)

---

## 4. LangChain for LLM Application Development

**Platform:** DeepLearning.AI (free)
**Instructors:** Harrison Chase (LangChain CEO) and Andrew Ng (DeepLearning.AI)
**Rating:** Free, canonical LangChain introduction
**Duration:** ~106 minutes, 9 lessons
**URL:** https://learn.deeplearning.ai/courses/langchain

### Curriculum

1. **Introduction** (3m) — what LangChain is and why composability matters
2. **Models, Prompts and Parsers** (18m) — chat models, prompt templates, output parsers
3. **Memory** (17m) — buffer, window, summary, vector-store memory; choosing for context window
4. **Chains** (13m) — LLMChain, sequential chains, router chains
5. **Question and Answer** (15m) — first pass at RAG: loaders, embeddings, retrievers, retrieval chains
6. **Evaluation** (15m) — generating Q/A pairs, programmatic + LLM-based grading
7. **Agents** (14m) — ReAct loop, tool calling, building a math agent
8. **Conclusion** (1m)
9. **Quiz** (10m)

---

## 5. Agentic AI with LangChain and LangGraph

**Platform:** Coursera (IBM)
**Instructors:** Faranak Heidari, Kunal Makwana, Karan Goswami, Joseph Santarcangelo, Martin Keen
**Rating:** 4.6/5 (95 reviews)
**Duration:** 10 hours over 1 week | 3 modules with videos + labs + quizzes
**URL:** https://www.coursera.org/learn/agentic-ai-with-langchain-and-langgraph

### Curriculum

#### Module 1: Introduction to LangGraph (3h)
- Course Introduction (3m)
- Generative vs Agentic AI (7m)
- Core Components of LangGraph (4m)
- LangGraph vs LangChain: When to Use What (10m)
- Getting Started with LangGraph 101 (7m)
- **Lab:** LangGraph 101 — Building Stateful AI Workflows (60m)
- Practice quizzes + graded quiz (39m)

#### Module 2: Build Self-Improving Agents with LangGraph (4h)
- Overview: Types of AI Agents (10m)
- The Art of AI Self-Improvement: Building Reflection Agents (8m)
- Understanding Reflexion Agents (6m)
- Building Reflexion Agents (8m)
- ReAct: Building Agents that Reason Before Acting (9m)
- **Lab:** Building a Reflection Agent with LangGraph (45m)
- **Lab:** Building a Reflexion Agent with External Knowledge Integration (30m)
- **Lab:** ReAct — Build Reasoning and Acting AI Agents with LangGraph (90m)
- Practice quizzes + graded quiz (39m)
- Reference: Structuring LLM Tool Calls with Pydantic and JSON Serialization

#### Module 3: Multi-Agent Systems and Agentic RAG with LangGraph (3h)
- Introduction to Multi-Agent Systems (8m)
- Risks of Agentic AI (7m)
- Agentic RAG: Enhance Retrieval with Multi-Agent Systems (6m)
- Course Wrap-up (5m)
- **Lab:** DocChat — Build a Multi-Agent RAG System (60m)
- Practice quizzes + graded quiz (33m)

---

## Summary Comparison

| Course | Platform | Duration | Level | Price | Focus |
|--------|----------|----------|-------|-------|-------|
| Foundation: Introduction to LangGraph | LangChain Academy | ~6 modules of notebooks | Intermediate → Advanced | Free | LangGraph fundamentals from the source: state, memory, HITL, long-term memory, deployment |
| LangChain - Agentic AI Engineering | Udemy | 19h 8m | Intermediate → Advanced | Paid | Project-based: 7 hands-on projects from Ice Breaker to Agentic RAG |
| AI Agents in LangGraph | DeepLearning.AI | ~99 min | Beginner → Intermediate | Free | Build a ReAct loop from scratch, then rebuild it in LangGraph; HITL and essay writer |
| LangChain for LLM Application Development | DeepLearning.AI | ~106 min | Beginner | Free | LangChain fundamentals: models, prompts, memory, chains, RAG, agents |
| Agentic AI with LangChain and LangGraph | Coursera (IBM) | ~10h | Intermediate | Paid (or Coursera Plus) | Self-improving agents (Reflection, Reflexion, ReAct) and multi-agent systems with hands-on labs |
