## AI engineering

AI engineering is the work of building a product on a foundation model that already exists. The daily decisions are which task to give the model, how to adapt it, how to judge the output, and how to keep the feature reliable after launch.

The work exists because a small number of general models can now do many tasks that used to need a separate trained model each: drafting, coding, summarizing, classifying messy text, pulling fields out of a document, and choosing a tool to call. A team calling the OpenAI, Anthropic, or Google model APIs can put GitHub Copilot-style suggestions, a Gmail summary, or a support draft in front of users without owning a training cluster. Training a base model from scratch remains a research and infrastructure project. Most product teams never do it. Their leverage is the application around the model: the context they assemble, the interface they put the output in, the checks they run, and the fallback when the model is wrong.

**Trade-offs.** A foundation-model feature ships faster than a task-specific model and is harder to make boringly reliable. The same model that writes a good summary will sometimes write a fluent false one, the bill moves with every token, and the provider can change the model under you. You trade a long training project for a permanent evaluation and operations project.

**Interview.** Say what the product does with the model, who checks the output, and what happens on a bad day. Name the adaptation lever you would try first. Put training-from-scratch on the table only when a hosted model cannot meet privacy, quality, latency, or unit cost, and you have the data and the budget to do better.

**Recap.** AI engineering builds products on models someone else already trained. The job is choosing the task, adapting the model, evaluating open-ended output, and operating the feature. The base-model training run is a different job, and most teams buy it as an API.

## Language models in product terms

A language model scores possible continuations of a piece of text. In a product, that shows up as a completion: you send a prompt, and the model appends one likely next piece, then another, until it stops.

Many tasks are the same loop with a different prompt. "Summarize this thread," "is this reply angry," "finish this function," and "translate this paragraph" can all be written as "continue the text in the way the instruction describes." ChatGPT, Claude, and Gemini are this loop behind a conversation UI. The output is a sample from a distribution, so a finished-sounding answer can still be wrong.

Two older shapes are worth keeping straight, and [Understanding Foundation Models](../02_Understanding_Foundation_Models/) goes into the architecture. A masked model, the BERT family being the well-known one, hides a span and predicts it using words on both sides. That shape fits classification, tagging, and embedding search. An autoregressive model, the GPT family and today's chat models, predicts the next piece using only what came before. That one-direction loop is what lets a chatbot keep writing. Products that generate email, code, and answers are built on the autoregressive side.

The model reads tokens, not words as a person counts them. A tokenizer cuts text into a fixed vocabulary of pieces. Everyday English words are often one piece. A long code identifier, a rare word, or text in a script the vocabulary barely covers becomes many pieces. For English prose a rough planning estimate is about four characters per token, and code and non-English text often cost more. You hit the context limit in tokens, you wait in tokens, and the API bills you in tokens. Output tokens are usually priced higher than input tokens, so a rambling answer costs more than a short one. Pasting a whole repository into Copilot Chat or Cursor pays for mostly irrelevant code. Pasting the open file and the compiler error is smaller and usually more useful.

```text
Instruction: name the tone in a few words, then stop.
Email: "The package never arrived and I need it today."
Tone:
```

A useful completion is "frustrated, time-sensitive." The model is finishing the prompt. It has no separate "classifier" product inside the API.

**Trade-offs.** One completion API covering many tasks is why these models are general. The cost of that generality is a soft failure mode: the completion always looks like text of the kind you asked for, including when it is unfaithful. Token accounting is the other cost. A longer context can help the model and can also crowd out the relevant part, add latency, and dominate the bill.

**Interview.** Describe the feature as a completion over a specific context, then say what the context contains and how you will notice a wrong completion. Mention tokens when you talk about cost or latency. Leave sampling, attention, and training curves to the foundation-model topic unless the interviewer asks.

**Recap.** A product language model finishes a prompt one piece at a time. Masked models fill a gap using both sides and mostly serve understanding tasks. Autoregressive models write the chat, code, and draft features people ship. Tokens are the unit of context, latency, and price.

## Self-supervision

Self-supervision is training a model on labels that the data already contains. For an autoregressive language model, the label for a prefix of a document is the next piece of that same document.

That is why language models could grow to web scale. A spam classifier needs people to mark mail. Next-token training can use books, bug reports, documentation, code, and articles without a new human label on each row. The bottlenecks moved to which data you keep, how much compute you spend, and how you filter junk. Scale on that signal produced models that could continue many kinds of text. Following a user's instruction reliably is a later adaptation, the post-training step covered in [Understanding Foundation Models](../02_Understanding_Foundation_Models/). An application team usually starts from a model that has already had both steps. A label that comes free with the file says nothing about whether the data was licensed, representative, or safe to repeat. Curation is part of building the model, and it belongs to the model-development layer of the stack.

```text
The document supplies the target.
"...refunds over 50 dollars need a"
next piece to predict: "manager"
```

**Trade-offs.** Self-supervision removes the labeling bottleneck and removes the guarantee that the model learned the task you care about. A model can be excellent at sounding like the web and weak at your refund policy until you adapt it. More data also copies the web's mistakes, secrets, and skewed coverage into the weights.

**Interview.** If you are asked why large language models arrived when they did, point at this label: the next token is already in the file, so training could scale with data and compute. Then say what that does not give you: your private facts, your quality bar, and the right to treat a fluent answer as a source.

**Recap.** The model learns by predicting a piece the document already holds, so nobody labels every example. That is what made internet-scale language models possible. The application still has to supply the task, the private facts, and the check on the answer.

## Foundation models

A foundation model is a large model trained on broad data, usually with self-supervision, and then adapted to many downstream tasks. A large language model is the text case. The term is wider than text.

Image models behind Midjourney, Adobe Firefly, and Stable Diffusion are foundation models for pictures. GPT-4o, Gemini, and Claude accept images alongside text, so a user can paste a screenshot of a failing UI or a photo of a receipt. Video models such as Runway and Sora extend the same idea to clips. Speech models cover audio. The shift that matters for a product team is from "train one model per task" to "start from a strong base and adapt it." Translation, summarization, code completion, and captioning can share a base model. They should not share a product design, because the input, the cost, and the review are different.

Multimodal input is worth it when the user's artifact is not text. A bug report that is a screenshot, a receipt that is a photo, and a storyboard that is a sequence of frames are poor fits for a text-only prompt unless someone retypes them. The output modality is a separate choice. Captioning an image is cheap to review. Generating a minute of video is expensive to render and expensive to watch.

**Trade-offs.** A general base model gives you a head start on every task and a specialist's peak on none of them until you adapt it. Multimodal models widen what a user can submit and widen the ways the model can misread the input. A video output multiplies latency, cost, and review time compared with a paragraph.

**Interview.** Define a foundation model as a reusable base, then say which modality goes in and which comes out for this product. Offer one adaptation plan. If the interviewer calls every API model a foundation model, agree that the product pattern is the same, and be precise about whether you are adapting a general base or calling a small task model.

**Recap.** Foundation models are broad bases you adapt, and language models are the text-shaped ones. Images, audio, and video are the same product pattern with different cost and review. The application chooses the modality. It does not retrain the base for every task.

## Why AI engineering became practical

AI engineering became a normal software job when three conditions arrived together: the models became useful on open-ended tasks, a developer could call them as an API, and investment followed the products people could see.

ChatGPT, released at the end of 2022, made the capability obvious outside research labs. GitHub Copilot had already shown the same shift for code. Before that, a strong demo often stayed a paper. After hosted APIs from OpenAI, Anthropic, and Google, a small team could put a model behind a button without running a GPU cluster. Capital and hiring then paid for better models and better tooling, which pulled in more teams. A strong model you cannot call stays a research result. An easy API in front of a weak model misses the product bar. The discipline is what you do once both exist.

The practical consequence is where time goes. An application team spends it on the task, the prompt and the retrieved context, the interface, the evaluation set, and the operating plan. They spend less of it on feature pipelines and training loops for a model that only does one classification.

**Trade-offs.** Hosted models make the first version fast and make you a tenant. Price, latency, privacy, rate limits, and model updates are partly someone else's roadmap. Self-hosting an open model reverses that: you gain control and you take on the GPU fleet, the serving stack, and the evaluation that the API vendor was bundling.

**Interview.** Answer "why now" with the three conditions, capability, access, and investment, and say which one your design depends on. If the design dies when the API raises prices or changes behavior, say how you will pin a model version and what would push you to self-host.

**Recap.** Useful models, model APIs, and the investment those products attracted showed up together. That is when building on a foundation model became ordinary engineering. The new center of effort is adaptation, evaluation, and the product around the call.

## Prompting, RAG, and finetuning

Prompting, retrieval-augmented generation, and finetuning are the three usual ways to make a foundation model behave like your application. Prompting changes the instructions and examples in the request. Retrieval changes which facts are inserted into that request. Finetuning changes the weights.

Start with prompting. It is how Gmail summarizes a thread you just opened, and how ChatGPT follows "answer in five bullets." You can change it in an afternoon, version it next to your code, and see the effect on the next call. It cannot teach the model a fact that is absent from the request and absent from training, and it gets worse when the instruction plus the documents overflow the context window.

Add retrieval when the facts live outside the model and change on their own. A Notion Q&A over a company wiki, a Zendesk bot over the help center, and NotebookLM over papers you uploaded are this pattern. A search step returns passages, and the prompt says to answer from those passages. When a page is edited, the next retrieval sees the edit. The failure is a missed page: the model then either abstains or answers from memory and may invent a policy. Finetuning those pages into the weights would freeze yesterday's wiki.

Finetune when the gap is behavior that a prompt does not hold, and you have examples of the behavior done well. A house style for thousands of Shopify product descriptions, a stable JSON shape the model keeps breaking, or domain phrasing your support agents actually use are the usual cases. Finetuning spends a training job, a dataset, and a new model version to evaluate. It does not absorb a fact that appears tomorrow. The product facts still go in the prompt, and a changing knowledge base still wants retrieval. The three levers stack. Prompting stays even when you add the others. [Prompt Engineering](../05_Prompt_Engineering/), [RAG and Agents](../06_RAG_and_Agents/), and [Finetuning](../07_Finetuning/) cover the mechanics.

| Situation | Lever to add | What goes wrong if you skip it |
| --- | --- | --- |
| The task and the text are both in the request, as in a Gmail thread summary. | Prompt only. | A heavier lever adds delay and a model to maintain. |
| The facts are private or they change, as in a Notion wiki. | Retrieval, plus the prompt. | The model answers from memory and the wiki has moved on. |
| A behavior will not stick, and you have many good examples. | Finetuning, plus the prompt. | The prompt keeps drifting, and a retrieval index cannot store a style. |

**Trade-offs.** Prompting is cheap to try and easy to outgrow. Retrieval stays fresh and fails open when search misses. Finetuning holds a behavior at volume and is the slowest to iterate, the easiest to overfit, and the one tied to a base-model version. Doing all three on day one hides which lever actually moved the metric.

**Interview.** Name the missing piece before the lever. Missing words in the request are a prompt. Missing fresh or private facts are retrieval. A behavior the prompt will not hold, with examples on disk, is a finetune. Say that you would measure the prompt before paying for a training job, and that a finetune does not replace retrieval for a wiki that edits daily.

**Recap.** Prompting steers a single request. Retrieval inserts facts at request time. Finetuning writes a behavior into the weights. Use them in that order, and keep the earlier lever when you add the next.

## Coding and writing

Coding assistants and writing assistants are generation features: the model drafts, and a person decides what ships. GitHub Copilot and Cursor suggest code in the editor. ChatGPT and Claude take a pasted error or a function and propose a change. Notion AI, Gemini in Gmail, and Grammarly draft and rewrite prose the user already has in front of them.

Code suggestions are a strong fit for boilerplate, a test for a function you can specify, and an explanation of a stack trace. They are a weak fit for a change that depends on a private API absent from the prompt, and for a check that is almost right. The compiler and the test suite reject a large share of the bad output automatically. A suggestion that compiles and is still wrong is the one a reviewer has to catch. The person who merges owns the diff.

Writing suggestions are a strong fit when the facts are already in the document: shorten this, sound calmer, turn these bullets into a paragraph. They are a weak fit when the draft needs a number, a policy, or a promise the source text never made. The model will often supply one anyway, in a confident sentence. There is rarely a compiler for a paragraph. The person who sends the email or publishes the page owns the claim.

**Trade-offs.** A draft helps when editing it is faster than writing it. Copilot's inline suggestion interrupts typing, so a low-precision ghost text trains people to ignore the feature. A Gmail draft the user explicitly requested can be rougher, because they asked for it and they still press Send. Code has tests as a backstop. Marketing copy and support email usually have only the reader's eye, so the review cost can erase the savings.

**Interview.** Say what the model may emit (a diff or a draft), what checks it (tests, a send button, a reviewer), and what context it must see (the open file, the error, the style notes). If the design jumps to a custom code model before the relevant file is in the prompt, the cheaper lever was skipped.

**Recap.** Copilot, Cursor, Notion AI, and Gmail drafts all generate a first version a person accepts. Code gets a partial automatic check from the compiler and the tests. Prose usually does not. The human who ships the result owns it.

## Image, video, and tutoring

Image generation, video generation, and tutoring are also foundation-model products, and the review step is different in each.

Midjourney, Adobe Firefly, and the image tools in ChatGPT produce stills from a prompt. The working pattern in design teams is many variations and a person picking one. Concept art and mood boards fit that pattern. Exact words drawn inside the picture, a precise layout, and a look that stays on-brand across a campaign are the weak spots. Firefly's place inside Adobe's tools matters because the file has to land in a layout the designer already has. That is an interface problem as well as a model problem.

Runway and Sora produce video. A clip costs more to generate than a still, and someone has to watch it before it publishes. A mistake in the last second wastes the whole render. A previz or a social cut that a person reviews is the fit. A shot that must match a storyboard frame for frame is a higher bar and often the wrong tool.

Duolingo's conversation practice and Khan Academy's Khanmigo are the education shape. A practice dialogue fits well: one wrong hint is cheap, the learner can try again, and the next turn can correct it. A score that changes a credential, or a worked solution a student will treat as the answer key, needs a known-correct source beside the model. The useful tutor pattern is a model that stays on the course material and asks questions, with a teacher still responsible for the class.

**Trade-offs.** These features feel finished in a demo because the output is something you can see. Each generation spends money, video spends more, and a fluent tutor can teach a mistake with the same tone as the lesson. Putting the curriculum, the brand references, or the storyboard in the context is what keeps the model on the artifact the user actually has.

**Interview.** Split "options a person selects" from "an artifact the user trusts." Concept art and a practice conversation are the first. An answer key and a grade are the second, and they need a source of truth outside the model's sample.

**Recap.** Image tools fit a person choosing among variations. Video adds render cost and a watch-before-publish review. Tutoring fits low-stakes practice on material you retrieved, and it stays off any decision that changes a credential by itself.

## Bots and information aggregation

A conversational bot talks with a person. An information product compresses sources into something the person can check. Both are foundation-model interfaces, and both fail when a fluent paragraph is treated as the source.

ChatGPT and Claude are bots that are the whole product: if the model is down, the page is empty. Intercom Fin and Zendesk's AI agents are bots on a help desk that already has articles, a queue, and human agents. The support bot should answer from the published help center, refuse when retrieval finds nothing, and hand the ticket to a person when the user disputes the answer or asks for something the policy does not let a bot do. The failure that matters is a confident reply that contradicts the refund rule, the outage notice, or the account-recovery steps.

Perplexity and NotebookLM aggregate sources and show them. Gmail's thread summary compresses a conversation the user can still open. Google's AI Overviews place a summary above search results. The design problem is the same: a sentence in the summary has to be checkable against a source in one step. A summary that states something none of the sources support, in a layout that looks like the answer, is worse than a list of links.

**Trade-offs.** A support bot that escalates almost every ticket saves little agent time. A bot that almost never escalates will send the policy error. A research answer that cites every clause is slower to read. An answer that cites nothing is a rumor with punctuation. For support, extra escalations are the affordable error. For a notebook over the user's own sources, a missing citation is the expensive one.

**Interview.** Name the corpus, the abstain rule, and the handoff. "We will add a chatbot" does not specify a system. "We answer from the latest help-center articles, we refuse on an empty retrieval, and a person gets any ticket about money or a disputed answer" does.

**Recap.** ChatGPT-style bots are the product. Intercom and Zendesk bots sit on a desk that already has people and articles. Perplexity, NotebookLM, and Gmail summaries are useful when each claim is one step from its source. A fluent paragraph with no source is the failure mode.

## Extraction and workflow automation

Extraction turns an unstructured document into fields. Workflow automation lets the model choose an action in a system that can change something. The first one wants a schema and a validator. The second one wants a short list of tools and a rule for side effects.

Expensify reading a receipt is extraction. So is an accounts-payable flow that reads an invoice into vendor, date, total, and line items. The model fills a schema. Ordinary code then checks that the lines sum to the total, the date parses, and the vendor exists. A clerk sees the original next to the fields and commits the payment. A free-text "summary of this invoice" is a worse interface, because a paragraph cannot fail a reconciliation check. The human remains on the payment.

Zapier-style agents, and similar tool-using flows in automation products, are the action case. The model can tag a ticket, draft a reply, create a calendar hold, or call Stripe's refund API. Tagging is reversible. Email is hard to unsend. A refund moves money. The application should expose a small tool list, require a person for the irreversible tools, and log every call with its arguments so a bad day can be replayed. The model proposes the action. The system decides whether the action is allowed to run.

**Trade-offs.** More tools make a demo look like an employee and multiply side effects. A validator after extraction catches format errors and will not catch a vendor that looks legitimate and is wrong, so the clerk stays. An agent with write access and no confirmation will eventually do the wrong write with correct grammar.

**Interview.** Draw the boundary at side effects. List the read-only tools, the writes, and the ones that need a confirmation. Say that the reconciliation after extraction is ordinary code. That combination, a model plus a deterministic check plus a person on the irreversible step, is the design.

**Recap.** Receipt and invoice tools should emit fields that code can validate and a person can compare to the document. Automation agents should start with drafts and read-only tools. Writes that move money or send on behalf of the company wait for a person.

## Task-level use case fit

Use-case fit is a property of a task, not of a job title. A foundation model is a candidate when the task is mostly language or other unstructured input, an approximate draft is acceptable, a person or a program can check the result, and a mistake is reversible or cheap.

The 2023 paper "GPTs are GPTs" (Eloundou, Manning, Mishkin, and Rock) defines a task as exposed when access to a model, or to software built on one, could cut the time to do that task by at least half at the same quality. On their measures, about 80 percent of the U.S. workforce is in an occupation where at least a tenth of the tasks are exposed, and about 19 percent is in an occupation where more than half the tasks are exposed. In their skill comparisons, writing and programming line up with higher exposure. At the industry level, manufacturing, agriculture, and mining sit lower. Those figures measure time that could be saved on tasks. An occupation can be highly exposed and still keep a person on the parts a model does badly.

Apply that at the task, inside products you can name. Summarizing a Gmail thread, suggesting a Copilot completion, and drafting a Duolingo reply are exposed tasks. Filing the exact payroll numbers in Gusto or ADP, computing a driving route in Google Maps, and deciding a brake input are poor fits: the first two already have a deterministic system that is right, and the third is a physical control loop with no tolerance for a sample. A useful enterprise starting point is an internal assistant on documents the company already has, with a person still accountable, because the task can be worth doing at imperfect quality when the output is advisory.

| Signal | What you should see | Familiar case |
| --- | --- | --- |
| Strong fit | Messy input, a draft is enough, someone can review, feedback is quick. | Copilot, Gmail summarize, a help-center draft. |
| Weak fit | Exactness, an irreversible effect, or a solved algorithm. | Payroll totals, a card charge, Google Maps routing. |
| Fit with a boundary | The draft is useful and a person commits the side effect. | Invoice fields a clerk approves, a refund a person confirms. |

**Trade-offs.** Rejecting every imperfect task misses the drafts people will happily edit. Accepting every language-shaped task puts a model on decisions that have a correct number and a real side effect. Exposure research is a screen for where to look, and a weak substitute for measuring your own task.

**Interview.** Evaluate one task, not a department. State the input, the output, the check, and the cost of a wrong answer. Mention the 50 percent time cut as the public definition of exposure, and say clearly that exposure is a time claim about tasks. Then give your own go, draft-for-a-human, or skip for the feature in front of you.

**Recap.** Judge the task. Language in, a reviewable draft out, and a cheap mistake are the strong-fit signs. Exact, irreversible, or already-solved tasks stay with ordinary software. Exposure numbers say where a model can save time. The occupation can remain.

## Critical, reactive, and human roles

An AI feature has four independent choices: whether the product works without the model, whether the user asked for the output, whether behavior changes per user over time, and what the human still decides.

Critical means the product's promise depends on the model. ChatGPT, Midjourney, and Perplexity are empty when the model is down, so the reliability bar is the product's reliability bar. Complementary means the product still works. Gmail sends mail with Smart Compose off. VS Code edits code with Copilot off. A bad day is a missing convenience, and you can ship a kill switch.

Reactive means the user invoked it: they sent the ChatGPT message, or they clicked Summarize in Notion. They expect a wait, and a weak answer is a turn they can retry. Proactive means the system spoke first. Smart Compose and Copilot ghost text appear unasked. A wrong suggestion interrupts, and people learn to ignore the feature, so the precision bar is higher even though the feature is complementary.

Static means everyone gets the same behavior until you ship a new prompt or model. A single help-center bot with one system prompt is static, and one eval set describes it. Dynamic means the behavior moves with the user. ChatGPT's memory is dynamic. So is a ranker you add that promotes completions this person accepted today. Dynamic behavior can be more useful, and it can repeat a mistake the user once accepted. You evaluate cohorts, because one global screenshot no longer describes the product.

The human role is the automation boundary. A person edits the Copilot suggestion and the Gmail draft. A bot answers the easy help-center questions and routes the rest. A model takes an action alone only after you know the failure rate on that action and can afford it. "Human in the loop" hides which of these you mean.

| Axis | One end | The other end |
| --- | --- | --- |
| Dependency | Complementary: Gmail still sends. | Critical: ChatGPT has nothing else to show. |
| Invocation | Reactive: the user clicked Summarize. | Proactive: ghost text while they type. |
| Change over time | Static: one prompt until the next release. | Dynamic: memory or per-user ranking. |
| Human | Edits a draft, or handles the hard cases. | The model acts, and people audit samples. |

**Trade-offs.** Critical plus proactive plus dynamic is the expensive corner: an outage is the product, an unasked action annoys or harms people, and the behavior drifts per user. Complementary, reactive, and static is how most teams should ship the first version. Moving the human boundary outward without a measured error rate is how a demo becomes an incident.

**Interview.** Place the feature on all four axes and say which axis sets which bar. Critical sets uptime and quality. Proactive sets precision. Dynamic sets whether one global eval is enough. The human role sets which side effects exist. Then say how the boundary moves later, with a metric, such as an agent accept rate, rather than on a date.

**Recap.** Critical or complementary sets how bad an outage is. Reactive or proactive sets how polished an unasked suggestion must be. Static or dynamic sets the shape of the eval. The human role sets who may cause a side effect.

## Expectations, thresholds, and metrics

A usefulness threshold is the quality below which people turn the feature off. It is specific to the task and to the alternative the user already has. Latency and unit cost have thresholds of their own, and a feature has to clear all three.

Quality first. If the alternative is a blank page, a rough Notion draft can be useful. If the alternative is a correct query an analyst already knows how to write, a wrong one wastes the afternoon. Inline Copilot suggestions have to be accepted often enough to beat typing, and wrong ones have to be rare enough that people leave the feature on. A support draft has to be faster to edit than to write. A refund, a payroll figure, or a medical note a professional will sign has a threshold at which the model does not get to be the signer. An "80 percent" score is not one of these thresholds. On editable drafts, 80 percent "usable with light edits" can be a win. On policy-bearing replies, the same 80 percent can mean a large daily pile of wrong promises. Users also compare you with the best demo they have used. A box that looks like ChatGPT gets judged like ChatGPT.

Latency next. Copilot-style suggestions have to return before the user has typed the line, which in practice means a fraction of a second. A ChatGPT turn can take several seconds because the user is waiting on a conversation. An invoice batch can take minutes if the clerk reviews it later. Building the slow product's latency budget into the fast product makes the fast one feel broken.

Cost last, counted per successful task. You pay for the suggestions people reject and for the retries after a weak answer. A cheap model that people run three times can lose to a pricier model they trust once. [Evaluation Methodology](../03_Evaluation_Methodology/) is where metric design goes deeper. For this planning step, pick a small set tied to the task: acceptance rate, how much the user edits, escalation rate, policy-violation rate, a latency percentile, and dollars per successful task. A single accuracy number flattens a stiff sentence and a made-up refund into the same miss.

**Trade-offs.** Raising quality usually raises latency or cost, through a larger model, a longer prompt, or a retrieval step. Lowering latency by skipping retrieval makes a support bot faster and less grounded. Optimizing the average hides the tail you will be paged for. Write the threshold down before the demo, or the demo will become the threshold.

**Interview.** State the three bars for this feature in numbers you invented from the product, and label them as targets: for example a suggestion inside 300 milliseconds, an agent edit on most drafts, and a policy-violation rate you are willing to show a customer. Say what "80 percent" refers to. Offer the metric you would refuse to launch on if it missed, which is usually the harmful tail and not the average.

**Recap.** A feature has to be good enough to beat the user's current alternative, fast enough for the interaction, and cheap enough per success. Those bars differ for Copilot, ChatGPT, and a support bot. Average accuracy is the wrong summary of an open-ended task.

## Milestones from demo to production

A milestone plan is the sequence of evidence between a curated demo and a feature customers can trust. The last mile is the gap in the middle: real traffic, the tail, latency, cost, guardrails, and a way to notice when the model changes.

Teams get a demo easily. Twenty help-center tickets, chosen because they look like the happy path, answered live in a meeting, feel like a product. That meeting measures whether the model can sometimes do the task. It does not measure how often, on which tickets, at what latency, or at what cost. Shipping from the meeting is how an 80 percent slide becomes a customer-facing incident.

A practical sequence for a Zendesk or Intercom bot:

| Milestone | What is true when it is done |
| --- | --- |
| Demo | A few hand-picked tickets produce answers people in the room like. |
| Eval set | A few hundred real tickets, including boring and hostile ones, are scored with a written rubric. Tone and policy errors are separate numbers. |
| Shadow | Agents see the draft. Customers do not. You learn the edit rate without the harm. |
| Limited send | Only intents under the policy bar are sent, the rest go to a person, and a kill switch exists. |
| Production | A pinned model, a regression set, a latency and cost watch, and an on-call path for a bad day. |

The same sequence fits other products with different evidence. Copilot's shadow is "suggestion shown, acceptance logged, nothing merges by itself." An invoice extractor's limited send is "fields filled, payment still needs the clerk." Skipping from the demo to production skips the only steps that look at your distribution.

**Trade-offs.** Each milestone delays the launch and reduces the chance you launch a harmful bot. Shadow mode costs agent attention and produces the first honest edit rate. A long limited send on only the easy intents can look like stalling, and it is also how you learn the tail before it has a side effect. Cutting the eval set to save a week is how the demo's tickets become the whole measurement program.

**Interview.** Draw this sequence and say which milestone the team is actually in. If the evidence is "the room liked it," they are on the demo, whatever the roadmap calls it. Name the metric that blocks the next step, such as a policy-error rate on the eval set, and name the kill switch.

**Recap.** A demo shows the model can do the task on tickets someone picked. An eval set, a shadow period, and a limited send are the last mile. Production adds a pinned model and a watch on quality, latency, and cost.

## Maintenance under a moving model

Maintenance is the work of keeping a shipped feature inside its quality, latency, and cost bars after the model, the prompt, the prices, and the users move. A foundation-model feature keeps changing on days you do not deploy.

Providers replace weights behind names, deprecate model ids, and change prices. A prompt tuned on one snapshot can regress on the next even when your code is identical. A finetune is attached to a base model and often has to be rebuilt when that base is retired. Users drift too: a support bot launched on billing questions starts seeing screenshots and legal threats. Input prices often fall. The bill can still rise, because a new snapshot writes longer answers, people retry weak ones, or a longer default context gets stuffed on every call. A floating alias such as a "latest" model makes all of this automatic, including the bad days.

Operate it like a dependency you do not control. Pin a model id. Keep the regression set from the milestone plan and run it on every model change and every prompt change. Watch faithfulness or acceptance, a latency percentile, and dollars per successful task. Roll back to the pinned previous id when the new one misses the bar. Recheck the bill with input and output tokens, not with the headline price cut. Rebuild finetunes on a schedule instead of assuming they carry over. [AI Engineering Architecture and User Feedback](../10_AI_Engineering_Architecture_and_User_Feedback/) is the later topic for monitoring and feedback design.

**Trade-offs.** Pinning buys stability and forgoes improvements until you choose them. Following an alias gets the improvements and the regressions on the same day. A large regression set catches more and costs more to run every time the provider ships. Skipping it because the last three upgrades were fine is how the fourth one reaches customers.

**Interview.** Say that the model is a moving dependency. Your controls are a pinned id, a regression eval, a bill computed from real token mix, and a rollback. A price cut is not a launch by itself. If faithfulness fell under the bar, you keep the old snapshot and treat the cheaper rate as unused.

**Recap.** Models, prompts, prices, and users change under a shipped feature. Pin the model, re-run the eval, and recompute the bill from input and output tokens. Take an upgrade when it clears the same bars you launched with.

## The three-layer AI stack

The AI stack has three layers. Application development decides what the product does with a model. Model development changes the model. Infrastructure runs the compute, the storage, and the serving.

Application development is prompts, retrieved context, tool use, the interface, and the product's evaluation. The citation list in Perplexity, the ghost text in Copilot, the Summarize button in Notion, and the decision to put three help-center passages into the prompt all live here. This is where most AI engineering time goes, because many teams share the same base model and the product difference is the application.

Model development changes weights or the model artifact. Training, finetuning, the datasets those jobs need, distillation, and quantization sit here. A finetune on your support transcripts is this layer. So is a smaller model built so the suggestion path gets faster. Evaluation happens here too, on the checkpoint, and it is a different question from the product eval upstairs.

Infrastructure serves the model and keeps the platform up: GPUs, orchestration, storage, request logs, autoscaling, and the metrics pipeline for latency and spend. The process that holds an embedding index is infrastructure. The decision of which passages to fetch and how to phrase them is application. vLLM and similar servers are serving infrastructure. The quantization choice that made the model fit the GPU is model development.

You start at the top and move down when a measurement says you have to. A hosted API means someone else runs the lower two layers, which is the right architecture until privacy, quality, latency, or unit cost cannot be met there.

| Work | Layer | Example |
| --- | --- | --- |
| Which passages enter the prompt, and what the UI shows. | Application | Perplexity's sources list, a Gmail summary button. |
| A finetune, a dataset, a quantized checkpoint. | Model | A support-model finetune, a smaller code model. |
| The fleet, the logs, the dollars-per-query dashboard. | Infrastructure | GPU autoscaling, request tracing. |

**Trade-offs.** Staying at the application layer is faster and leaves you exposed to API price and behavior. Dropping to model development can cut cost and raise quality, and it adds a training pipeline and a model to regress. Owning infrastructure is justified at large, steady spend or strict data control, and it is a poor use of a team that has not yet written an eval set.

**Interview.** Place each responsibility in a layer before you name a vendor. Say you start at the application layer. Give the measurement that would push you down: a missed quality bar after prompting and retrieval, a unit cost that does not work on the API price, or a privacy rule that forbids the request from leaving your network. If someone files the vector database under "the model," put the database in infrastructure and the retrieval policy in the application.

**Recap.** Application development shapes the request, the interface, and the product eval. Model development changes weights and artifacts. Infrastructure runs serving, storage, and monitoring. Start at the top, and move down for a measured reason.

## AI engineering versus ML engineering

AI engineering and ML engineering both put learned models in products. The default center of the work is different. ML engineering trains and operates a model for a task you defined. AI engineering adapts a general model and evaluates open-ended behavior.

An ML engineer building a spam filter or a fraud score collects labels, designs features, trains a model whose outputs are classes or numbers, and watches precision and recall. The model is yours, it is often small enough that a single scoring call is sub-millisecond and almost free, and a held-out label set tells you if you got better. An AI engineer building a support draft starts from a hosted foundation model, writes a prompt, maybe retrieves help-center articles, and judges paragraphs. There is no single correct string. A rubric, an agent accept rate, and a count of policy violations replace a neat accuracy chart. One call can take hundreds of milliseconds to several seconds, and the token bill is visible at product scale. The context you assemble is the input, on every request.

The models are larger, so inference cost and latency are design constraints on day one, where a traditional scorer could ignore them until the batch got huge. Evaluation is harder because the output is open-ended and because a fluent error looks like success in a log. The base model also changes on a vendor's schedule, which a model you trained does not do unless you retrain it.

The boundary is porous, and that is useful to say out loud. Finetuning, training a reranker for retrieval, and building a careful eval set are ML work inside an AI-engineering product. A team can do both. The mistake is to staff the project as a pure training team when the unsolved problems are the prompt, the corpus, and the rubric, or to staff it as a pure API integration when the unsolved problem is a model that prompting cannot steer.

**Trade-offs.** Starting from a foundation model skips a training program and accepts a weaker grip on behavior, cost, and change control. Training your own task model gives you that grip and is the wrong expense when a prompt already clears the bar. Open-ended evaluation is slower than precision and recall and is the evaluation that matches the output you actually ship.

**Interview.** Compare the two on starting point, daily work, metrics, and the cost of a single call. Then place this product: a fraud score can stay a classical model, a help-center draft is adaptation plus a rubric, and a finetuned support model is both. Offer ML knowledge as the tool you use when you cross into weight changes or into a metric you cannot eyeball.

**Recap.** ML engineering's default is a task model you train, with labels and a scalar metric. AI engineering's default is a general model you adapt, with a context you build and an open-ended output you have to judge. Large-model latency and token cost show up immediately. The same team often does some of each.

## AI engineering versus full-stack engineering

Full-stack engineering is the interface, the API, the data, the auth, and the deploy. An AI feature needs all of that, and it adds a component that is slow, billed per token, and willing to return the wrong answer with a 200 status.

The UI for ChatGPT, the editor surface for Copilot, the document store behind NotebookLM, and the ticket queue behind a Zendesk bot are ordinary product engineering. Accounts, rate limits, pagination, and a place to put the transcript do not become optional because a model is involved. The model call is the extra dependency. It has a latency budget, a cost budget, and a failure mode unit tests do not see: a grammatical paragraph that invents a refund. A test can check that a tool call matches a schema. It cannot check that a summary is faithful to the thread. That check is an eval set plus sampling in production.

The program itself grows a new kind of source code. The prompt, the retrieval policy, and the tool list change behavior as much as the Python around them, so they belong in version control and in review. Fallbacks are product decisions. Show the source email under a Gmail summary. Send the ticket to a person when retrieval is empty. Let the tax calculation, the maps route, and the payment total stay on the deterministic path.

**Trade-offs.** Treating the model as a normal HTTP client gets a demo up and leaves quality, cost, and the fluent failure unowned. Building a separate "AI platform" before the product has a single measured task adds process without evidence. The full-stack skills stay necessary. They are not sufficient once the answer can be wrong and still look done.

**Interview.** Describe the feature as a normal service plus one probabilistic dependency. Say what you unit-test (auth, schema, tool permissions), what you eval (faithfulness, policy, acceptance), and what the fallback is when the eval would have failed. Mention that prompts are reviewed like code. If you hear "it is just an API call," agree that the transport is an API call, and describe the latency, the bill, and the 200-status failure that the call can still produce.

**Recap.** The app around the model is full-stack work. The model adds token cost, a slower call, prompts that act like code, and wrong answers that look successful. Tests cover the deterministic shell. An eval set and a fallback cover the generation.
