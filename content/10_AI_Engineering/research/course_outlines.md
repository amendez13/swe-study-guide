# AI Engineering Course Outlines

Single-source study track seeded from *AI Engineering: Building Applications with Foundation Models* by Chip Huyen. Unlike the other research folders in this repository, this one is intentionally based on one book rather than a five-course survey, because the goal is to turn the book itself into the initial course structure.

---

## 1. AI Engineering: Building Applications with Foundation Models

**Format:** Book
**Author:** Chip Huyen
**Publisher:** O'Reilly Media
**Edition / Year:** First Edition, 2025
**ISBN:** 978-1-098-16630-4
**Source:** Local PDF in `gitignored-sources/` (not committed to the repository)

### Curriculum

#### Chapter 1: Introduction to Building AI Applications with Foundation Models
- The Rise of AI Engineering
- From Language Models to Large Language Models
- From Large Language Models to Foundation Models
- From Foundation Models to AI Engineering
- Foundation Model Use Cases
- Planning AI Applications
- The AI Engineering Stack
- AI Engineering Versus ML Engineering
- AI Engineering Versus Full-Stack Engineering
- Summary

#### Chapter 2: Understanding Foundation Models
- Training Data
- Multilingual Models
- Domain-Specific Models
- Modeling
- Model Architecture
- Model Size
- Post-Training
- Supervised Finetuning
- Preference Finetuning
- Sampling
- Sampling Fundamentals
- Sampling Strategies
- Test Time Compute
- Structured Outputs
- The Probabilistic Nature of AI
- Summary

#### Chapter 3: Evaluation Methodology
- Challenges of Evaluating Foundation Models
- Understanding Language Modeling Metrics
- Entropy
- Cross Entropy
- Bits-per-Character and Bits-per-Byte
- Perplexity
- Perplexity Interpretation and Use Cases
- Exact Evaluation
- Functional Correctness
- Similarity Measurements Against Reference Data
- Introduction to Embedding
- AI as a Judge
- Why AI as a Judge?
- How to Use AI as a Judge
- Limitations of AI as a Judge
- What Models Can Act as Judges?
- Ranking Models with Comparative Evaluation
- Challenges of Comparative Evaluation
- The Future of Comparative Evaluation
- Summary

#### Chapter 4: Evaluate AI Systems
- Evaluation Criteria
- Domain-Specific Capability
- Generation Capability
- Instruction-Following Capability
- Cost and Latency
- Model Selection
- Model Selection Workflow
- Model Build Versus Buy
- Navigate Public Benchmarks
- Design Your Evaluation Pipeline
- Step 1. Evaluate All Components in a System
- Step 2. Create an Evaluation Guideline
- Step 3. Define Evaluation Methods and Data
- Summary

#### Chapter 5: Prompt Engineering
- Introduction to Prompting
- In-Context Learning: Zero-Shot and Few-Shot
- System Prompt and User Prompt
- Context Length and Context Efficiency
- Prompt Engineering Best Practices
- Write Clear and Explicit Instructions
- Provide Sufficient Context
- Break Complex Tasks into Simpler Subtasks
- Give the Model Time to Think
- Iterate on Your Prompts
- Evaluate Prompt Engineering Tools
- Organize and Version Prompts
- Defensive Prompt Engineering
- Proprietary Prompts and Reverse Prompt Engineering
- Jailbreaking and Prompt Injection
- Information Extraction
- Defenses Against Prompt Attacks
- Summary

#### Chapter 6: RAG and Agents
- RAG
- RAG Architecture
- Retrieval Algorithms
- Retrieval Optimization
- RAG Beyond Texts
- Agents
- Agent Overview
- Tools
- Planning
- Agent Failure Modes and Evaluation
- Memory
- Summary

#### Chapter 7: Finetuning
- Finetuning Overview
- When to Finetune
- Reasons to Finetune
- Reasons Not to Finetune
- Finetuning and RAG
- Memory Bottlenecks
- Backpropagation and Trainable Parameters
- Memory Math
- Numerical Representations
- Quantization
- Finetuning Techniques
- Parameter-Efficient Finetuning
- Model Merging and Multi-Task Finetuning
- Finetuning Tactics
- Summary

#### Chapter 8: Dataset Engineering
- Data Curation
- Data Quality
- Data Coverage
- Data Quantity
- Data Acquisition and Annotation
- Data Augmentation and Synthesis
- Why Data Synthesis
- Traditional Data Synthesis Techniques
- AI-Powered Data Synthesis
- Model Distillation
- Data Processing
- Inspect Data
- Deduplicate Data
- Clean and Filter Data
- Format Data
- Summary

#### Chapter 9: Inference Optimization
- Understanding Inference Optimization
- Inference Overview
- Inference Performance Metrics
- AI Accelerators
- Inference Optimization
- Model Optimization
- Inference Service Optimization
- Summary

#### Chapter 10: AI Engineering Architecture and User Feedback
- AI Engineering Architecture
- Step 1. Enhance Context
- Step 2. Put in Guardrails
- Step 3. Add Model Router and Gateway
- Step 4. Reduce Latency with Caches
- Step 5. Add Agent Patterns
- Monitoring and Observability
- AI Pipeline Orchestration
- User Feedback
- Extracting Conversational Feedback
- Feedback Design
- Feedback Limitations
- Summary

---

## Summary Comparison

| Source | Format | Scope | Structure |
| --- | --- | --- | --- |
| *AI Engineering* by Chip Huyen | Book | End-to-end AI application development with foundation models | 10 chapters, used as the initial chapter map for `content/10_AI_Engineering/` |

## Notes

- This folder is intentionally a single-source seed, not a multi-course market survey.
- The next authoring step is to extract a durable concept list from these chapters and turn each chapter scaffold into topic-level `concepts.md` content.
