## Why evaluation is hard

Evaluating a foundation model means deciding whether a sample is good enough to ship, when more than one sample can be acceptable and the next call can draw a different one.

The difficulty is built into the product. A classifier on a fixed label set has one test, and the test is whether the label matches. ChatGPT, Claude, Gemini, GitHub Copilot, and a Zendesk draft are one family of models asked to do many jobs. A summary, a code suggestion, and a refund reply fail in different ways, so one public rank cannot be the launch gate for all three. The rank also moves as new models are added. The output is a sample from the distribution in [Understanding Foundation Models](../02_Understanding_Foundation_Models/). Two calls at a chat temperature can differ in wording, or in the fact. A stored golden sentence then rejects a faithful paraphrase and can accept a lucky draw that will not be the draw you serve tomorrow.

Public benchmarks have two further failures, and both show up before you pick a metric. They leak into training crawls. HumanEval was handwritten because code models had already seen public solutions on GitHub, and a score on a test that was in the crawl can be recall of that test rather than generalization. The decontamination step in the training-data card exists so a later number measures generalization. They also saturate. A benchmark that every frontier model aces no longer separates the systems you are choosing, and it was never your support queue. The metrics in the rest of this topic can move in opposite directions on the same change: next-token fit can worsen after the post-training that makes a chat model useful, and a word-overlap score can prefer a fluent answer that states the wrong policy. That is not a bug in the arithmetic. The numbers answer different questions. The work is to match the question to the failure a user would notice, to keep a program that can mark the output wrong wherever such a program exists, and to treat a judgment as a measurement you calibrate.

**Trade-offs.** A single leaderboard number is cheap to quote and it is the wrong gate for a support desk or an editor. A private set costs labeling and stays about your traffic. Judging every sample with a frontier model scales past a person on every row and spends a second model call, and it imports the judge's biases. A meeting that liked twenty tickets is still a demo, which is the milestone bar from the introduction topic.

**Interview.** Name the four reasons the score is hard: the task is open-ended, one model serves many tasks, each call is a sample, and public benchmarks leak and saturate. Then refuse a one-number launch decision. Ask which failure the metric is for. A wrong amount wants a checker. A paraphrase wants something other than string equality. A choice among five variants wants a comparison. Exact checks, similarity to a reference, a model used as a judge, and a pairwise ranking are the four tools, and the rest of the conversation is which failure each one can see.

**Recap.** Evaluating a foundation model is hard because many answers can be acceptable, one model is used for many tasks, each call is a sample, and public benchmarks leak into training data and then saturate. Metrics that all sound like quality answer different questions, and they can move in opposite directions. Match the metric to the failure a user would notice, and keep a real checker wherever one exists.

## Entropy

Entropy is the average surprise in a probability distribution, measured in bits when the logarithm is base 2. It is the lower bound on the average number of bits needed to encode draws from that distribution, and it is the floor under every language-model loss in this topic.

A distribution that always produces the same outcome has entropy 0, because there is nothing to learn. A fair coin has entropy 1 bit. A biased coin carries less, because you can guess the likely face and be right more often. The formula is the same for a next token. Sum over the vocabulary, and skip any outcome whose probability is 0, taking `0 log 0` as 0. The context changes the distribution, so a model has a different entropy at each position. Training does not minimize entropy. Entropy belongs to the data. Training minimizes the extra surprise of a model that has not matched the data, which is the next card.

Shannon's 1951 experiments put the entropy of printed English on the order of one bit per character, with his bounds spanning a range around that figure rather than a single constant. That estimate is a historical yardstick for the bits-per-character number later in this topic, not a score you can paste onto Llama or GPT-4. A base Llama or GPT model scoring the next piece of a Wikipedia sentence is the same sum, taken over that model's vocabulary at that context. The number moves if the tokenizer's pieces change, because two tokenizers define different random variables. When the model was not fit on the bytes you score, the expected cross entropy on those bytes is at least the entropy of the text. One small sample can land below that floor by chance. A very low number on the training text is a memorization smell. The number you trust is on bytes the training run did not use.

```python
import math


def entropy_bits(probabilities: tuple[float, ...]) -> float:
    total = 0.0
    for probability in probabilities:
        if probability > 0.0:
            total -= probability * math.log(probability, 2)
    return total


fair = entropy_bits((0.5, 0.5))
biased = entropy_bits((0.9, 0.1))
print(f"{fair:.4f} {biased:.4f}")
# 1.0000 0.4690
```

**Trade-offs.** Entropy tells you how predictable the data is, and it tells you nothing about whether a particular model has captured that predictability. A low-entropy task, such as a support macro with three legal replies, can still be failed by a model that puts its mass on a fourth string. A high-entropy task, such as an open ChatGPT conversation, has a high floor, so you should not expect a tiny loss from a perfect chatbot. Changing the tokenizer changes the distribution whose entropy you are talking about, which is why a later card refuses to compare per-token losses across tokenizers.

**Interview.** Write `H = -Σ p log p` and state the base. Compute the fair coin as 1 bit and a 0.9/0.1 coin as about 0.469 bits, and say the deterministic case is 0. Then separate entropy of the data from cross entropy of a model. The interview trap is calling the training loss "entropy." The loss is cross entropy. Entropy is the part of that loss that remains when the model has matched the data.

**Recap.** Entropy is the average information in a distribution. A fair coin is 1 bit, a 0.9/0.1 coin is about 0.469 bits, and a sure outcome is 0. Language-model training does not minimize entropy. It minimizes the model's extra surprise on top of the entropy of the text, and a number below that floor on the training slice is a sign you measured memorization.

## Cross entropy

Cross entropy is the average surprise of a model distribution `q` when events actually arrive from a data distribution `p`. It is the language-model training loss, and it is the quantity perplexity is computed from.

The formula is `H(p, q) = -Σ p(x) log q(x)`. It splits into two pieces that the previous card set up. `H(p, q) = H(p) + KL(p ‖ q)`. The entropy is the data. The KL divergence is the extra cost of encoding the data with the model's probabilities instead of the true ones. KL is zero only when `q` matches `p`, and it is positive otherwise, so cross entropy is entropy plus a penalty for being wrong. This KL is between the data distribution and the model. The KL penalty on the RLHF and direct preference optimization card in [Understanding Foundation Models](../02_Understanding_Foundation_Models/) is a different divergence, between the updated policy and the supervised checkpoint. If the model puts probability 0 on an outcome the data still produces, the penalty is infinite. A softmax over finite logits gives every token a nonzero probability, which is why a training loss is a finite number rather than an infinity the first time a rare token appears.

You do not observe `p` for language. You observe tokens. The training loss replaces the sum with an average, over a corpus, of `-log q(next token | context)`. That is a Monte Carlo estimate of the cross entropy under the contexts the corpus actually contains. PyTorch and the Hugging Face causal-language-model loss use the natural logarithm, so the number on the dashboard is in nats. Divide by `ln(2)` to get bits. The same three-outcome picture is enough to see the split. Take a true next-token distribution of 0.7, 0.2, and 0.1, and a model that says 0.5, 0.3, and 0.2.

```python
import math


def cross_entropy(truth: tuple[float, ...], model: tuple[float, ...], base: float) -> float:
    return -sum(p * math.log(q, base) for p, q in zip(truth, model))


def entropy(probabilities: tuple[float, ...], base: float) -> float:
    return -sum(p * math.log(p, base) for p in probabilities if p > 0.0)


truth = (0.7, 0.2, 0.1)
model = (0.5, 0.3, 0.2)
h_bits = entropy(truth, 2.0)
ce_bits = cross_entropy(truth, model, 2.0)
kl_bits = ce_bits - h_bits
ce_nats = cross_entropy(truth, model, math.e)
matched = cross_entropy(truth, truth, 2.0)
print(f"{h_bits:.4f} {ce_bits:.4f} {kl_bits:.4f} {ce_nats:.4f}")
print(f"{matched:.4f}")
# 1.1568 1.2796 0.1228 0.8869
# 1.1568
```

The matched model lands back on the entropy, 1.1568 bits. The mismatched model pays 1.2796 bits, and the 0.1228 bit gap is the KL. In nats that cross entropy is 0.8869, which is the unit the next card exponentiates. Nothing in the arithmetic says the model is a good chatbot. It says the model was surprised by these three outcomes, by this much, relative to a model that had `p` exactly.

**Trade-offs.** Cross entropy is the right training objective for next-token prediction and a weak product metric for an answer a person reads. It punishes any probability the model fails to put on the observed token, including probability it spent on another acceptable paraphrase. It is comparable across checkpoints that share a tokenizer and a test corpus. It is not comparable across tokenizers, because both the tokens and the distribution change. A loss of 0 from a softmax would mean the model assigned probability 1 to every observed token, which is the right target on a closed label set and a suspicious target on open text.

**Interview.** Write the split, entropy plus KL, and compute a three-outcome case so the interviewer can see the penalty is the gap. Say the training loss is the empirical version, an average of `-log q` on held-out tokens, and say whether the log is natural. Offer nats times `1 / ln(2)` as the conversion to bits. Close by refusing to rank two chat models by this loss alone when one of them has been preference-tuned. That comparison is the perplexity card.

**Recap.** Cross entropy is the average surprise of a model on data from another distribution. It equals the entropy of the data plus the KL penalty for disagreeing with it. On a 0.7, 0.2, 0.1 distribution, a model that predicts 0.5, 0.3, 0.2 has cross entropy 1.2796 bits against an entropy of 1.1568 bits. The language-model loss is this quantity averaged over next tokens, usually in nats, and perplexity is what you get by exponentiating it.

## Bits per character and bits per byte

Bits per character and bits per byte take a model's total cross entropy and divide by the length of the original text, so two models can be compared when they cut the text into different tokens.

Per-token loss rewards a tokenizer that makes easy predictions, and it punishes one that makes fewer, harder predictions, whether or not the model assigns a higher probability to the actual string. The quantity that belongs to the string is the sum of `-log q` over every token, the total negative log likelihood. Divide that sum, in bits, by the number of characters and you have bits per character. Divide by the number of UTF-8 bytes and you have bits per byte. On ASCII the two denominators match, because each character is one byte. On other scripts they do not. A character count also depends on what you call a character: a Unicode code point, a grapheme cluster, and a string in NFC versus NFD can disagree. Bytes are the file. That is why bits per byte is the comparison you want across tokenizers and across languages, and bits per character is the same idea when the character definition is written down.

The conversion from a dashboard loss is mechanical. If the loss is mean nats per token, total nats is the loss times the token count, and total bits is total nats divided by `ln(2)`. The same 1,000 ASCII bytes, scored by two exercise tokenizers, are enough to see a reversed ranking. Neither loss is a published Llama or GPT figure. They are the arithmetic.

```python
import math

BYTES = 1000
LN2 = math.log(2)


def bits_per_byte(loss_nats: float, tokens: int) -> float:
    return loss_nats * tokens / (BYTES * LN2)


first = bits_per_byte(2.0, 250)
second = bits_per_byte(1.4, 400)
print(f"{first:.4f} {math.exp(2.0):.4f}")
print(f"{second:.4f} {math.exp(1.4):.4f}")
# 0.7213 7.3891
# 0.8079 4.0552
```

The second tokenizer has the lower perplexity, 4.0552 against 7.3891, because each of its tokens was an easier local prediction. It used 400 tokens at 1.4 nats, 560 nats in total, against 250 tokens at 2.0 nats, 500 nats in total. The first model is the better encoding of these bytes, at 0.7213 bits per byte against 0.8079. A causal model whose vocabulary is the 256 bytes scores the next byte directly, so its average cross entropy, converted to bits, is already bits per byte, and that is the number you can set next to a BPE model on one file. ByT5 also uses a byte vocabulary, and it is an encoder-decoder trained to reconstruct corrupted spans, so its training loss is not that next-byte figure. Shannon's order-of-one-bit-per-character estimate is the historical human yardstick for this scale. A model number far below the entropy of the text, on text it trained on, is the memorization smell from the entropy card.

**Trade-offs.** Bits per byte lets you compare tokenizers and languages, and it still only measures next-token fit on the bytes you scored. It says nothing about instruction following. Computing it requires the token counts and the original file length, which a per-token loss chart hides. Bits per character is easier to explain on English prose and it becomes a different metric the moment the corpus is not ASCII or the normalization changes. Reporting either number on the training file flatters the model. The held-out file is the measurement.

**Interview.** Say that perplexity and token loss live on the tokenizer's pieces, and bits per byte lives on the file. Walk the conversion, total nats divided by `ln(2)` divided by bytes, and give a pair of exercise losses where the lower perplexity is the worse encoding. Mention UTF-8 so you have a reason to prefer bytes over characters for a multilingual launch. If the question is which chat model to ship, say this number is the wrong tool once post-training has changed the objective, and go to the next card.

**Recap.** Bits per character and bits per byte divide a model's total cross entropy, in bits, by the length of the original text. They exist so a 250-token encoding and a 400-token encoding of the same file can be ranked. On the exercise pair, perplexity prefers the 400-token model, 4.0552 against 7.3891, and bits per byte prefers the 250-token model, 0.7213 against 0.8079. Use bytes when the script or the normalization would make a character count ambiguous.

## Perplexity

Perplexity is the exponential of the average next-token cross entropy. It restates that loss as an effective number of equally likely choices at each token.

If the mean loss is in nats, perplexity is `e` to that power. If the mean loss is in bits, perplexity is 2 to that power. The two formulas agree when the bit figure is the nat figure divided by `ln(2)`. A model that assigned probability 1 to every observed token has perplexity 1. A model that assigned probability `1/k` to every observed token has perplexity `k`. That is the reading to keep: perplexity 7.39 means that, on this corpus, the model was as uncertain as a uniform guess among about 7.39 tokens. Lower is a tighter fit to the measured text. It is not a percent accuracy, and it is not comparable to a score on HumanEval or to a preference win rate.

The base is part of the definition. A dashboard that prints "loss 2.0" might be nats, which is what a standard causal-language-model trainer reports, or it might already be bits. Exponentiating with the wrong base invents a different model. The check below is the whole trap.

```python
import math

loss_printed = 2.0
as_nats = math.exp(loss_printed)
as_bits = 2 ** (loss_printed / math.log(2))
if_already_bits = 2**loss_printed
print(f"{as_nats:.4f} {as_bits:.4f} {if_already_bits:.4f}")
# 7.3891 7.3891 4.0000
```

The first number treats 2.0 as nats, so perplexity is 7.3891. The second converts those nats into bits and raises 2 to that power. It matches, which is the check that the two formulas are the same quantity. The third treats the printed 2.0 as if it were already bits and gets 4. That 4 is the right perplexity only when the dashboard was in bits. When the dashboard was in nats, 4 is a different model. The three-outcome model on the cross-entropy card had a cross entropy that prints as 0.8869 nats. Exponentiating the unrounded value gives perplexity 2.4277, which is small because that example had only three outcomes. A real vocabulary has tens or hundreds of thousands of pieces, and a perplexity in the tens can still be a strong next-token model. You only interpret the number next to the vocabulary, the tokenizer, and the corpus that produced it.

**Trade-offs.** Perplexity is a faithful rescaling of the training loss, which makes it a good chart for a pretraining run and a bad chart for a product. A perplexity chart stretches absolute gaps at the high end. A drop from 20 to 10 and a drop from 4 to 2 are the same factor of two, and the same loss gap of `ln(2)` nats, about 0.693. The chart shows the first drop as ten points and the second as two. Quoting perplexity without the tokenizer and the corpus lets a larger vocabulary, or an easier test file, win an argument it did not earn.

**Interview.** Define perplexity as `exp` of the mean nat loss, give the 2.0 nats example as 7.3891, and show that treating those 2.0 as bits yields 4. Explain the branching-factor reading in one sentence. Then say what would make you refuse a comparison: a different tokenizer, a different corpus, or a chat model whose training objective is no longer the corpus you measured. The next card is that refusal, in detail.

**Recap.** Perplexity is `e` raised to the average next-token cross entropy in nats, which is the same number as 2 raised to that cross entropy in bits. A loss of 2.0 nats is perplexity 7.3891, the uncertainty of a uniform guess among about 7.39 tokens. Treating that same printed 2.0 as bits produces 4, so the unit is part of the answer. Lower perplexity means a tighter fit to the measured text, for one tokenizer and one corpus.

## How to read perplexity

Reading perplexity means deciding what a change in that number is evidence of. The number is evidence about next-token fit on one corpus under one tokenizer, and several common changes are evidence of something else.

Use it inside a pretraining run. The same tokenizer, the same held-out slice of the same mix, a falling perplexity: the run is still fitting that slice. That curve is the smooth loss the scaling cards extrapolate, and it is still not a help-desk rubric. Use it as a domain probe. If a base model has a much higher perplexity on your Zendesk exports than on a Wikipedia slice, under one tokenizer, the tickets are surprising to that model. The gap is a domain gap. It does not, by itself, say the model will be a bad support bot once the reply is in the prompt and the policy is retrieved. Use it as a corpus filter. The perplexity cutoff in the training-data card is one model scoring documents. A very high score is often junk or a language the model barely saw. A very low score, on text the model trained on, can be a duplicate it has memorized. Both thresholds are valid for that model and that tokenizer only.

Three properties of the measurement move the number before any model gets better. More predictable text scores lower. A formulaic log line or a repetitive template has less next-token surprise than open prose, so a corpus that got "cleaner" by becoming more templated will look like a better model. A larger vocabulary scores higher, all else equal. The uniform distribution over a vocabulary of size V has perplexity V, and a bigger menu of next tokens raises the chance of surprise even when the model is similarly calibrated. That is one reason two tokenizers are not ranked by perplexity. The bits-per-byte card is the other. A longer context usually scores lower, because the model conditions on more of the document and later tokens are less surprising. A perplexity at 512 tokens and a perplexity at 8,192 tokens are different measurements. Compare checkpoints at the same context length, the same tokenizer, and the same mix, or the movement is the setup.

Do not use it across tokenizers. The bits-per-byte card is the counterexample: a drop in perplexity from 7.3891 to 4.0552 was a worse encoding of the same bytes. Do not use a raw web perplexity to accept or reject a post-trained chat model. Supervised finetuning and preference training change the objective. The model is pushed toward replies a rater preferred, and away from continuing a Wikipedia article in the raw. Perplexity on that article can rise while win rate on your replies rises. InstructGPT called the drop on public tasks the preference step was not optimizing an alignment tax. The tasks they named included SQuAD, DROP, HellaSwag, and WMT 2015 French-to-English. Mixing pretraining-distribution updates back into PPO, their PPO-ptx run, reduced those regressions and did not erase them. A rise in pretraining perplexity is the same kind of objective change, visible in next-token fit. It is a reason to go measure those tasks. It is not itself the tax, and it is not, by itself, a reason to revert the chat model. Perplexity also cannot see a wrong fact that was locally probable, a failed unit test, or a preference between two fluent answers.

Use a suspiciously low score as a contamination smell only against a matched control. A benchmark item whose perplexity sits far below the perplexity of similar text the model should not have memorized may have been in the crawl. Easy or formulaic text also has low perplexity, so a universal cutoff is not proof. The n-gram decontamination in the training-data card is the removal you do before training, when you still have the crawl. Perplexity is a check you can run afterward, for that model and that tokenizer only. A stricter membership test averages the least likely tokens in the example rather than every token, and it still needs the control set. Neither test replaces a fresh, handwritten set once the public one is famous.

**Trade-offs.** A held-out perplexity chart is the cheapest honest monitor for a pretraining run, and it will smile on a run that is fitting the web while your product metric is flat. Bits per byte fixes the tokenizer comparison and inherits every other limit of next-token fit. Keeping a base-model perplexity gate on an instruct checkpoint will reject useful post-training. Dropping perplexity entirely leaves you without a training curve and without a simple domain probe. The split is: perplexity for "are we fitting this text under this tokenizer," and a task metric for "should a user see this answer."

**Interview.** The uses you defend are comparing checkpoints of one training run, comparing domains under one tokenizer, filtering a corpus with one scoring model, and flagging a benchmark item whose perplexity is far below a matched control. The uses you refuse are ranking two tokenizers by perplexity, treating a low score on easy text as proof of leakage, and reverting a chat model because Wikipedia perplexity rose. Tell the alignment-tax story as task regressions on the sets InstructGPT named, not as a perplexity quota you did not measure. Offer bits per byte as the repair for the tokenizer case. If the interviewer wants the product decision, leave perplexity and name the checker: tests, execution, or a calibrated judge.

**Recap.** Perplexity compares next-token fit for one tokenizer on one corpus. It is a training curve, a domain probe, a corpus filter, and, against a matched control, a contamination smell. It is not a ranking across tokenizers, and a rise after supervised or preference training can be the objective changing rather than the chat model getting worse. InstructGPT's alignment tax was that kind of regression on public tasks, reduced by mixing pretraining updates back in, and not removed. The ship decision stays with the task metric the user actually feels.

## Exact and subjective evaluation

Exact evaluation marks an output right or wrong with a program. Subjective evaluation marks quality by a judgment, because more than one output is acceptable and no program has the rule.

A unit test, a multiple-choice key, a normalized short label, and a SQL result set are exact. The program can be harsh and still be the right judge, because the product needs that field to be that value. "Was this helpful," "is this summary fair," and "does this Claude reply sound like our support desk" are subjective. People disagree on the boundary, so the metric has to include the rubric and the rater, not only the model. Most shipped features are mixed, and the mix is the design. A Notion AI summary of a meeting note has a decision and a date that either match the note or do not, and it has a phrasing that can go several acceptable ways. The date wants an exact check against the note. The phrasing wants a judgment, and only after the facts have passed. A JSON schema, from the Structured outputs card, is exact about syntax and silent about whether the total is the total on the receipt.

The common failure is crossing the streams. String-matching a Gmail summary treats a subjective phrasing as if it were a label, so a correct paraphrase looks like a defect. Asking a model "is this SQL right" treats an exact, executable question as if it were an opinion. You already have the database. The functional-correctness card and the judge cards later in this topic are the two tools. This card is only the choice of which tool you are allowed to use.

Not every question should be settled by a preference. A factual answer, a dose, a refund window, and a medical claim have a correct value or they have a source. Forcing a rater to pick the "better" of two wrong answers writes a vote the ranking cards will treat as taste, and it frustrates the rater, who can see that neither answer is acceptable. Offer a both-bad tie, or leave the row on an exact check. Preference is for what remains: tone, usefulness, and which of two faithful replies a person would rather read.

Comparative evaluation and an A/B test answer different questions, and the names get swapped. Comparative evaluation, later in this topic, shows two answers and records which one a person or a judge preferred. The result is a rank. An A/B test assigns live users at random to two variants and records a product metric: accept rate, task completion, whether they come back. A model can win the pairwise read and lose the A/B test, because people prefer a fluent paragraph and still fail the task. A model can lose the pairwise read and win the A/B test, because a shorter, plainer answer gets the job done. Run the comparison to choose a candidate. Run the experiment, the Online experiments card in [AI Engineering Architecture and User Feedback](../10_AI_Engineering_Architecture_and_User_Feedback/), to see whether the candidate changed the product. Neither one is a substitute for an exact field check.

**Trade-offs.** Exact checks are repeatable, cheap to rerun, and blind to every quality they were not coded to see. A test suite can pass a patch that implements the wrong product behavior the tests forgot. Subjective judgments cover tone, usefulness, and the open residue, and they drift with the rater, the prompt, and the day. Using a judgment where a checker exists spends money to approximate a bit you could have measured. Using a checker where the answer is genuinely open punishes every acceptable answer except the one in the file.

**Interview.** Split the feature into fields before you name a metric. Facts, amounts, labels, code behavior, and query results are exact. Tone and "which of these two helpful replies" are subjective. Say that a schema check is exact and is not the business rule. Give the Notion-style summary as the mixed case: the date is checked against the source, and the prose is judged only if the date survived. If you cannot name a program that could mark the output wrong, you are in the subjective half, and you owe a rubric.

**Recap.** Exact evaluation is a program that marks the output right or wrong. Subjective evaluation is a judgment on a quality no program has a rule for. Code tests, labels, and query results are exact. Helpfulness and tone are subjective. A real feature usually has both, and each field should use the tool that matches that field.

## Functional correctness

Functional correctness means the output does the job when a program runs it: the tests pass, the query returns the right rows, or the patch builds and the suite goes green.

Natural language has no such oracle for a paragraph. Code and queries do. HumanEval, from Chen and coauthors in the Codex paper, is 164 handwritten Python problems, each with unit tests, an average of 7.7 tests per problem in the paper. A sample is correct when those tests pass. The problems were handwritten because the training corpus already contained public solutions, which is the leak from the first card. The headline metric is pass@k, the probability that at least one of k samples passes. Generating exactly k samples and calling a problem solved when any one passes is an unbiased estimate with high variance, because the result on each problem is a single 0 or 1. The paper instead draws `n ≥ k` samples, counts the `c` that pass, and uses an unbiased estimator for that problem: `1 - C(n - c, k) / C(n, k)`, or 1 when fewer than k samples failed, because every subset of size k then contains a pass. The paper uses n = 200 samples per problem and k up to 100. Average the per-problem estimates. The product form in the paper is the same estimator written so large binomial coefficients do not overflow.

If you already know a single sample passes with probability p and the failures are independent, the chance that k tries contain a pass is `1 - (1 - p)^k`. That is the ceiling on the test-time compute card in [Understanding Foundation Models](../02_Understanding_Foundation_Models/). HumanEval does not hand you p. It hands you c successes in n draws. Plugging `p̂ = c / n` into the independence formula is a different estimator, and the Codex appendix shows it is biased low. On 3 successes out of 10, the unbiased pass@5 is 0.9167 and the plug-in is 0.8319.

```python
import math


def pass_at_k(n: int, c: int, k: int) -> float:
    if n - c < k:
        return 1.0
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)


def pass_at_k_product(n: int, c: int, k: int) -> float:
    if n - c < k:
        return 1.0
    failed = 1.0
    for index in range(n - c + 1, n + 1):
        failed *= 1.0 - k / index
    return 1.0 - failed


print(f"{pass_at_k(10, 3, 1):.4f} {pass_at_k(10, 3, 5):.4f}")
print(f"{pass_at_k_product(10, 3, 5):.4f}")
print(f"{1 - (1 - 3 / 10) ** 5:.4f}")
print(f"{pass_at_k(10, 6, 5):.4f} {pass_at_k(10, 0, 5):.4f}")
# 0.3000 0.9167
# 0.9167
# 0.8319
# 1.0000 0.0000
```

pass@1 and pass@10 are different budgets. Copilot ghost text gets one try inside a tight latency budget. A background agent that opens a pull request can spend several tries and a test suite, which is why a leaderboard pass@100 is not the number for an inline suggestion. SWE-bench is the same idea at issue size. A generated patch counts as resolved when every test that failed before the gold fix now passes, and every test that already passed still passes. A green run of unrelated tests is not that score. Execute untrusted code in a sandbox with a timeout. The metric is not a reason to `exec` a model string on the host.

Text-to-SQL has the same shape and a trap in the string. Spider's original published metric is an exact match of SQL components, compared as sets so column order inside a clause does not matter, and the early script did not score the literal values. Execution accuracy was added later, and two different queries can return the same rows, especially an empty result, so a match is not a proof of semantic equivalence. BIRD's headline metric runs the query. Its common scorer compares result sets, so row order does not count. Two strings can differ by case, quoting, or an `ORDER BY` and still return the same rows, and two identical-looking queries can return different rows on a database the string does not reveal. A product checker runs a single read-only statement, with a timeout and a row cap, and compares the result the user asked for: a multiset when the question is "which rows," and the ordered rows when the question asked for an order. It refuses anything that is not that statement. A model judge reading the SQL text is a later card, and it is the wrong first checker when the warehouse is right there.

**Trade-offs.** Execution is the metric the user feels, and it is only as good as the tests. A thin HumanEval-style suite can pass a function that fails the next input. A result-set match can pass a query that scanned a private table to get there, so the authorization check sits beside the correctness check. pass@k rises with k and will flatter a system that spends more samples than the product will spend. String match on SQL or on source code is cheaper than execution and rejects equivalent programs. Sandboxing costs engineering and is the cost of running the metric at all.

**Interview.** Define functional correctness as behavior under execution, and name HumanEval and pass@k. Compute the unbiased estimator on a small n, c, and k, and contrast it with `1 - (1 - p)^k` so you do not mix the estimate with the independence ceiling. Say pass@1 and pass@10 are different products. For SQL, prefer the result table over the string, and name the read-only guard. Mention that the tests can be wrong or incomplete, so a green suite is evidence about those tests.

**Recap.** Functional correctness runs the output. HumanEval's 164 problems are correct when the unit tests pass. A SWE-bench patch is resolved when the fail-to-pass tests now pass and the pass-to-pass tests still pass. Text-to-SQL is correct when the result the user asked for matches, with the order rule written down. pass@k is the chance that k samples contain a pass. With 3 successes in 10 draws, unbiased pass@1 is 0.3000 and pass@5 is 0.9167, against a plug-in of 0.8319 that the Codex appendix shows is biased low. Compare that number at the sample budget the product actually has.

## Exact match

Exact match means the output and the reference are the same string after a normalization you wrote down before you looked at the score.

The normalization is the metric. Case, whitespace, punctuation, and whether articles count are decisions, and changing them changes the number. SQuAD reports exact match after a published normalization that lowercases, strips punctuation, drops the articles "a," "an," and "the," and collapses whitespace, and it also reports a token-level F1 on that same normalization that gives partial credit when the predicted span and the gold span share words. Both still want the answer's words. A classification label, a multiple-choice letter, and a normalized entity are the settings where exact match is the whole evaluation. The output is short, the legal answers were enumerated, and a near miss is a miss.

It stops being the right metric as soon as a fluent system writes a sentence around the answer, or a second phrasing is also right. "New York" against a key of "New York City" fails a raw match and may fail the normalized one too. A Zendesk draft that states the correct window in different words fails exact match and may be the reply you want to send. A Copilot line that is behaviorally identical and textually different fails exact match and passes the tests from the previous card. Exact match also accepts a copy of the reference that is right for the wrong reason only if the reference itself is right. It cannot grade a question whose answer is not in the key. Multiple references raise the chance that a good answer hits one of them, and they do not cover the space of good answers. That uncovered space is why similarity, embeddings, and judges exist. They are not a reason to fuzzy-match a label that really is a label.

**Trade-offs.** Exact match is free, deterministic, and easy to explain, and it is brittle in proportion to how open the answer is. A strict normalization makes scores comparable across papers and punishes harmless variation. A loose normalization raises the score and can hide a real difference, including a different number. Partial-credit F1, as in SQuAD, reports a near miss and can score a longer prediction as mostly right when the extra words change the claim. Publishing the normalization with the score is cheap. Publishing the score without it makes the number impossible to reproduce.

**Interview.** Say exact match is equality after a declared normalization, and give SQuAD's exact match and token F1 as the classic pair. Name a case where you want it, a closed label, and a case where you do not, a summary or a code line with tests available. Offer the failure mode of a helpful sentence wrapped around a correct span: the span is right and the string match is wrong, so you extract the field and match that. Ask what the normalization does with "NYC" and "New York City" before you accept the score.

**Recap.** Exact match scores an output as right when it equals the reference after a normalization you wrote down. SQuAD uses it, alongside token F1, for short answer spans. It is the right metric for closed labels and the wrong metric for paraphrases, summaries, and code that should be executed. The normalization is part of the result, and a second reference does not turn it into a judge of every acceptable answer.

## Lexical similarity

Lexical similarity scores how much surface form two strings share: overlapping words and n-grams, or a short edit script from one string to the other.

Edit distance is the smallest number of insertions, deletions, and substitutions that turn one string into the other. Levenshtein distance is that count. It is the right tool for a short string with a typo, and it is a bad proxy for meaning. The strings "$12.50" and "$125.0" are distance 2. The second amount is ten times the first. A support tool that ranks replies by edit distance will treat that pair as almost the same text.

```python
def levenshtein(left: str, right: str) -> int:
    previous = list(range(len(right) + 1))
    for i, left_char in enumerate(left, start=1):
        current = [i]
        for j, right_char in enumerate(right, start=1):
            insert_cost = current[-1] + 1
            delete_cost = previous[j] + 1
            replace_cost = previous[j - 1] + (left_char != right_char)
            current.append(min(insert_cost, delete_cost, replace_cost))
        previous = current
    return previous[-1]


print(levenshtein("$12.50", "$125.0"))
# 2
```

N-gram overlap counts shared chunks of tokens. Precision is the fraction of the candidate's chunks that appear in the reference. Recall is the fraction of the reference's chunks that appear in the candidate. On the strings "the refund was issued today" and "the refund was issued yesterday," five of the six tokens match, and the token that differs is the fact. BLEU, from Papineni and coauthors in 2002, is a precision of n-grams, usually up to 4-grams, times a brevity penalty, designed for machine translation and read at corpus level. The penalty is 1 when the candidate is at least as long as the reference, and `e^(1 - reference_length / candidate_length)` when the candidate is shorter. A candidate of length 5 against a reference of length 10 is multiplied by `e^(-1)`, about 0.3679, even if every n-gram it did emit was perfect. The penalty exists because raw precision rewards saying less. ROUGE, from Lin in 2004, is the recall-oriented cousin used for summarization. ROUGE-N is n-gram recall. ROUGE-L uses the longest common subsequence, so it gives credit for shared words in order with gaps. METEOR, from Banerjee and Lavie in 2005, was built for a single sentence, where unsmoothed BLEU often collapses to 0. It aligns unigrams by exact match, then by stem, then by WordNet synonym, scores a harmonic mean of precision and recall that weights recall higher, and applies a penalty when the matched words are broken into many chunks. It correlates better with human translation judgments at sentence scale than BLEU does, and it is still a surface metric. WordNet does not know that 30 days and 60 days are different commitments, the synonym list is English-centric, and a wrong fact that shares stems still scores. sacreBLEU exists because small choices in tokenization and smoothing were making published BLEU numbers incomparable. Use one declared implementation.

Sentence BLEU without smoothing is 0 when any n-gram precision is 0. A good one-sentence paraphrase often shares no 4-gram with the reference and scores 0, which is the metric as specified and a bad product gate. Corpus BLEU over a whole test set is what the metric was built for, and it still prefers shared phrasing over a correct paraphrase and can score a wrong number highly when the rest of the sentence was copied. Overlap cannot see that "yesterday" and "today" are the whole task.

```python
import math

print(f"{math.exp(1 - 10 / 5):.4f}")
# 0.3679
```

**Trade-offs.** Lexical scores are deterministic, cheap, and reproducible, which is why translation and summarization research ran on them for years. They correlate with human judgments better in aggregate, on many similar sentences, than on one reply you are about to send. They punish a right answer in new words and forgive a wrong fact in familiar words. Edit distance is interpretable on short fields and absurd on a paragraph. Adding more references helps and does not create a notion of meaning. A modern product that still gates a chatbot on BLEU is using a translation metric on a job it was not designed to score.

**Interview.** Separate precision from recall, and place BLEU on the precision side with a brevity penalty, ROUGE on the recall side, and METEOR as the sentence-level unigram aligner that still does not know a swapped number. Compute a tiny edit distance whose numeric closeness is a different amount, and a brevity penalty on a short candidate. Say sentence BLEU can be 0 for a fine paraphrase, so you want corpus BLEU, METEOR, or a different metric, and you still do not want any of them as the fact check. Name sacreBLEU as the way two teams get the same BLEU number. Then say the metric you would actually ship for a support reply: check the facts exactly, and judge the wording with a calibrated rater.

**Recap.** Lexical similarity measures shared surface form. Levenshtein distance counts edits, and "$12.50" versus "$125.0" is only distance 2 while the amount grows by ten. BLEU is n-gram precision with a brevity penalty, and a candidate half as long is multiplied by about 0.3679. ROUGE is n-gram recall. METEOR aligns stems and synonyms and still misses a swapped window. All of them prefer familiar wording, and none of them know that the unmatched word was the fact.

## Semantic similarity

Semantic similarity scores whether two texts mean the same thing, including when they share few words.

"We sent the money back" and "The refund was issued" can be the same support event and a near-zero BLEU. The previous card is blind to that pair on purpose. A semantic metric tries to score the pair anyway, using a model of meaning rather than a count of tokens. Three tools show up in practice. A sentence embedding turns each text into one vector and uses cosine similarity, which is the next card. BERTScore, from Zhang and coauthors, stays at the token level: each token is a contextual vector from an encoder such as BERT or RoBERTa, tokens in the candidate are matched greedily to tokens in the reference by cosine, and precision, recall, and F1 fall out of that matching. Optional inverse-document-frequency weights keep "the" from counting like "refund." A natural-language-inference model, such as a DeBERTa-v3 checkpoint finetuned on MNLI, answers a different question: does the source entail the candidate, contradict it, or neither. Entailment is the check you want for one summary sentence against one source sentence from the Gmail thread or the help-center article. Cosine similarity of two fluent sentences is not that check.

The limit is the same one embeddings have. Meaning-shaped models still miss the distinctions products care about. A negated policy, a swapped number, and a name replaced by a similar name can sit close in embedding space because the topic is the same. BERTScore does not know that "30 days" and "60 days" are different commitments. When the other tokens match, one mismatched span is a small fraction of the score, so the number can look strong while the policy is wrong. An NLI model can catch a contradiction the cosine missed, and it can also miss it, or mark a paraphrase as a contradiction because the wording moved. MNLI-style models were trained on sentence pairs. A long Gmail thread has to be split, or the model is being used off the distribution it learned. You measure these failures on pairs from your own desk. A high semantic score is not functional correctness and not factuality. Two confident wrong answers can be very similar to each other.

**Trade-offs.** Semantic scores accept the paraphrases lexical scores punish, and they spend a model call or a vector lookup to do it. They are still reference-based when the second text is a gold answer, so they inherit a thin reference set. Entailment against the source is closer to faithfulness than similarity against one gold summary, and it fails when the source itself is wrong or incomplete. None of the three tools replace an executable check when you have one. Tuning a cosine threshold on one embedding model and applying it to another model is a silent metric change.

**Interview.** Contrast the refund paraphrase with the five-of-six token overlap from the lexical card, and say which metric can see which pair. Name BERTScore as token matching with contextual vectors, and name an NLI entailment check as the faithfulness version. Give negation or a swapped window as the case where a similarity score stays high and the product outcome flips. Then place the tool: semantic similarity ranks or filters open text, and an amount, a date, or a query result stays on an exact check.

**Recap.** Semantic similarity scores meaning rather than shared words, so a paraphrase of a refund can pass it and fail BLEU. Sentence embeddings, BERTScore's token matching, and an NLI entailment model are the usual tools. They still miss negations and swapped numbers often enough that a high score is not a fact check. Use them for open wording, and keep exact checks on the fields a program can decide.

## Embeddings

An embedding is a list of numbers that stands in for a piece of text, trained so that texts people treat as similar land in nearby directions. Cosine similarity is the usual way to score that closeness.

The vectors come from a model trained for retrieval or similarity, not from the raw hidden state of a chat model. Sentence-BERT, from Reimers and Gurevych, trains a BERT-style encoder so that cosine similarity of the sentence vectors tracks a labeled similarity. Later open models such as E5 and BGE, Cohere's Embed models, and OpenAI's text-embedding-3 family are the same product at different sizes and training mixes. MTEB is a public suite that compares them, and the top of that suite moves. A raw BERT CLS vector was not trained for this cosine, so a similarity you computed with it is a different metric from Sentence-BERT. The dimension, the normalization, and the input length live on the model card you called. Prices and default dimensions move with the API.

Cosine similarity is the dot product of two vectors divided by both lengths. It is 1 when the directions match, 0 when they are orthogonal, and -1 when they point opposite ways. It does not change if you rescale either vector. The dot product does, which is why a longer unnormalized vector looks "more similar" under a dot product for no semantic reason. Many APIs return normalized vectors, and the scores you see in a retrieval log are still not probabilities. A cosine of 0.8 on one model is not a cosine of 0.8 on another, and it is not an 80 percent chance the texts match.

```python
import math


def cosine(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    return dot / (left_norm * right_norm)


pair = cosine((1.0, 2.0, 2.0), (2.0, 1.0, 2.0))
scaled = cosine((1.0, 2.0, 2.0), (20.0, 10.0, 20.0))
orthogonal = cosine((1.0, 0.0), (0.0, 1.0))
opposite = cosine((1.0, 0.0), (-1.0, 0.0))
print(f"{pair:.4f} {scaled:.4f}")
print(f"{orthogonal:.4f} {opposite:.4f}")
# 0.8889 0.8889
# 0.0000 -1.0000
```

The first pair has dot product 8 and both lengths are 3, so the cosine is 8/9, about 0.8889. Scaling the second vector by 10 multiplies the dot product by 10 and leaves the cosine alone. That is the whole reason to divide by the lengths. In a product, these vectors are how retrieval finds a help-center article, how a corpus pipeline finds near-duplicate pages, and how a cheap semantic filter compares a draft to a reference. [RAG and Agents](../06_RAG_and_Agents/) is the retrieval use. The evaluation use is the semantic-similarity card, with the same warning: "do not issue the refund" and "issue the refund" share a topic, and a topical embedding often places them near each other. The threshold that means "same meaning" has to be measured on your pairs, for the model you deploy. A number copied from a blog post is someone else's calibration.

**Trade-offs.** One vector per text is fast to index and loses the token alignment BERTScore keeps, so it is a better retrieval key than a fine-grained grader. Cosine is stable under scaling and blind to magnitude cues you might have wanted. A larger embedding model can retrieve better and costs more at index time and query time. Changing models invalidates every stored vector and every threshold. Using the chat model that wrote the draft as its own embedding model mixes two jobs and is usually worse at retrieval than a model trained for it.

**Interview.** Define an embedding as a vector trained so similar texts point the same way, and write the cosine formula. Compute a tiny pair, including a rescaled copy, to show the dot product moves and the cosine does not. Name a real family, Sentence-BERT or E5 or text-embedding-3, and say MTEB is not your corpus. Give the negation pair as the case where a high cosine is the wrong product decision. Say the vector is for retrieval and coarse semantic comparison, and the refund amount is still an exact field.

**Recap.** An embedding is a vector that places similar texts in nearby directions, and cosine similarity scores that closeness independent of vector length. On the vectors (1, 2, 2) and (2, 1, 2) the cosine is 8/9, about 0.8889, and it stays 0.8889 if the second vector is scaled by 10. Sentence-BERT, E5, BGE, Cohere Embed, and OpenAI's text-embedding-3 family are real models of this kind. The score is not a probability, it is not comparable across models, and a topical near-miss such as a negated refund can look close.

## Why use an AI judge

An AI judge is a model asked to grade another model's output. It exists because open-ended text has no unit test, and people cannot relabel every row each time the prompt, the retriever, or the model changes.

Human preference is the quantity ChatGPT-style products are aligned to, and it is expensive. A rater has to read the source and the draft, apply a rubric, and do it again next week when the prompt changes. A strong model can do a first pass of that reading at the cost of another generation. Zheng and coauthors, in the 2023 MT-Bench and Chatbot Arena paper, measured how close that first pass was for GPT-4, and the number depends on how ties are counted. On MT-Bench, with ties removed and with a judgment that flips when the two answers are swapped also removed, GPT-4 as a pairwise judge agreed with expert voters on 85 percent of the first-turn judgments they compared, and two experts agreed with each other on 81 percent. Count the ties, and count an order-inconsistent judgment as a tie, and GPT-4's agreement with experts on that same first turn is 66 percent, next to 63 percent agreement between experts. The second turn is the same shape, 85 percent against 82 percent with ties removed, and 66 percent against 67 percent with ties kept. On the crowdsourced arena votes in that paper, the non-tie figure for GPT-4 against the human vote is 87 percent, and the figure that keeps ties is 64 percent. The abstract's "over 80 percent" is the non-tie number. Agreement was higher when one model was clearly ahead of the other. None of these figures is a property of an arbitrary judge, and none of them is a result about your Zendesk rubric until you measure it there. Leaderboards and which model is "strong" move.

The economic case is real and easy to overread. A judge is cheaper than a trained rater on every row of a nightly regression, and it is more expensive than a unit test or an embedding cosine. It belongs on the residue those checks cannot see: whether a summary a person would accept, whether a refusal was appropriate, whether a draft followed the policy in a way the tests did not encode. It does not belong on a question the database can answer. Teams use judges to label preference pairs for the reward-model and DPO training in the previous topic, and to pick a winner among samples. Both uses inherit the judge. If the judge is wrong in a systematic way, the training update and the eval gate learn that way.

**Trade-offs.** A judge scales a kind of evaluation that otherwise stops at a few hundred human labels, and it adds a model you have to pin, pay for, and revalidate. Human labels on a slice are slow and are the calibration the judge cannot provide for itself. Using the judge without that slice turns the MT-Bench non-tie figure into an unmeasured hope on a different task. Skipping the judge and waiting on people for every prompt experiment freezes the iteration the feature needs. The workable split is a judge on the bulk, people on a stratified sample, and a program on every field a program can check.

**Interview.** Explain the missing oracle first. Open text has no test suite, people do not scale to every prompt change, and a strong model can approximate preference judgments well enough to be useful once it is calibrated. Cite the MT-Bench paper with the counting rule: about 85 percent non-tie agreement for GPT-4 against experts, in the same range as expert-expert agreement, and about 66 percent once ties and order flips are kept. Say you would double-label a slice of your own tickets before a judge could block a launch. Place exact checks ahead of the judge whenever they exist.

**Recap.** An AI judge grades open-ended model output so you can evaluate without a person on every row. On MT-Bench, GPT-4 agreed with experts about 85 percent of the time when ties were removed, and about 66 percent when ties and order-inconsistent votes were counted as ties. Both sit near expert-expert agreement under the same counting. Your rubric starts uncalibrated. Use the judge for the residue a program cannot check, and keep people on a slice large enough to see when the judge drifts.

## How to use an AI judge

Using an AI judge means choosing what you show it, what verdict you ask for, and how you will know the verdict matches a person.

Four setups cover the jobs teams actually run. A pointwise score asks for a number on one answer, often 1 to 5, against a rubric. Absolute scores drift, because the judge uses the scale differently on Tuesday than on Thursday, and a 4 is hard to compare across tasks. A pairwise verdict shows two answers and asks which is better, with a tie allowed. It is the more stable question for ranking, and it does not tell you whether either answer is good enough to send. A reference-based verdict gives the judge the source, or a gold answer, and asks whether the candidate is faithful to it or as good as the gold. That is the right shape for a summary against a Gmail thread. A rubric with anchored levels turns "helpful" into checks a second rater could apply. "The return window matches the article" is a level a person can agree on. "Be helpful" is a level the judge will invent.

| Setup | What you ask | What you can conclude |
| --- | --- | --- |
| Pointwise score | You show one answer and ask for a number on the rubric. | The number is useful when the levels are anchored. It drifts, so compare it inside one pinned judge and one rubric. |
| Pairwise | You show two answers and ask which is better, with ties allowed. | This is the stabler ranking signal. A win does not mean the winner is fit to ship. |
| Reference-based | You show the source or a gold answer beside the candidate. | The verdict is faithfulness to that source. A thin gold set still punishes other acceptable answers. |
| Anchored rubric | You write each level as a check, with an example of that level. | This is what keeps a pointwise score meaningful across weeks. |

The prompt is part of the metric, in the same way the normalization is part of exact match. Ask for a structured verdict, a label plus a short citation of the rubric line, so you can audit it. Put one graded example of each level in the prompt. Hide the model name, because a judge can prefer a name it recognizes. Pin the judge's model id and its temperature. A low temperature makes the verdict less noisy and does not remove a bias. Run the judge at the same setting you used when you measured its agreement with people. On a math or reasoning item, have the judge commit to its own answer before it sees the candidates, or show a reference solution it produced separately. The limits card has the small probe where that changed the error rate. A program that can check the number still goes first.

Calibration is a small human set, not a feeling. Double-label a slice with the rubric you intend to keep. Report agreement, and report it in a form that subtracts the agreement you would get from the base rate. Cohen's kappa does that. Percent agreement looks strong when both the person and the judge mark most rows as a pass. Read every disagreement before you change the model. The disagreements are the spec: a vague level, a missing check, or a judge that cannot see the failure. Then relabel. A judge you have not run through this loop is a demo of a judge.

Self-critique is a judging pattern, not a fifth setup. The same model reads its own draft against the rubric and revises. It is cheap, it needs no second vendor, and it shares every blind spot the draft had. It belongs as a revision step when a second pass catches format and omission errors you have shown it catches. It does not belong as the score that ships. The reflection card in [RAG and Agents](../06_RAG_and_Agents/) is the agent version of the same move: a note after a failed step, which can itself be wrong. A self-score of "faithful" is another sample. The calibration above is what would make it a metric, and a model grading itself is the weakest place to skip that calibration.

**Trade-offs.** Pairwise judgments are better for "which variant" and they multiply cost, because each row carries two answers. Pointwise scores are cheaper and harder to keep stable. Reference-based grading is only as good as the source you passed in. A long rubric improves agreement and starts to be ignored, or to dominate the context window, once it is a policy manual. Few-shot anchors help a weaker judge and can leak the style of the anchors into every verdict. Reasoning before the label gives you an audit trail and can be a fluent story written to fit a verdict the model already reached, so you still read a sample of the reasons.

**Interview.** Walk the four setups and match each to a decision. Ranking five prompt variants is pairwise. A nightly faithfulness gate on a summary is reference-based against the thread. A 1-to-5 helpfulness score needs anchored levels or you do not trust the 4. Then describe calibration: a double-labeled slice, a chance-corrected agreement, and a read of the disagreements. Mention that the judge prompt is pinned with the model id. Offer to swap answer order, which is the position check on the bias card, before you believe a pairwise win rate.

**Recap.** An AI judge is a prompt plus a verdict schema plus a calibration. Pointwise scores, pairwise wins, reference-based checks, and anchored rubrics answer different questions. Hide model names, pin the judge, and keep the temperature where you measured it. Percent agreement is not enough. A chance-corrected agreement on a human slice, and a review of the rows where you differ, is what makes the number a metric.

## Limits of an AI judge

The limits of an AI judge are the ways a verdict fails before you even get to a stable bias: the call is a sample, the rubric is vague, the second model is expensive, and the judge can be talked out of a math answer it could have solved alone.

Inconsistency is the judge's version of the sampling problem, separate from the generator's inconsistency in [Understanding Foundation Models](../02_Understanding_Foundation_Models/). Close answers flip when you change a space, rename "Assistant A," or move to the next judge build. Temperature 0 reduces the flip rate and does not make the verdict a property of the answers alone. Treat a one-level gap on a 1-to-5 scale as a tie unless a second judgment agrees. For a launch gate, take a small majority on the pairs that sit near the boundary. Pin the judge id the way you pin the model you ship, and re-run the human slice when the id changes.

Criteria ambiguity means the rubric used a word the judge has to interpret. "Helpful," "natural," and "high quality" each hide a product decision. The judge will fill them in with a preference for fluent, complete, agreeable prose, which is the same shortcut a reward model learns when the comparisons contain it. The repair is an anchored check. "The window in the draft equals the window in the article" is a criterion. "Be helpful" is not. If two careful people cannot apply the level to a sample and land on the same mark, the judge cannot save the level.

Cost and latency are the reason the judge is an offline tool. The prompt carries the rubric, the source, and one or two answers, so the judge call is often more tokens than the draft you are grading. That is acceptable in a nightly regression and in a batch that labels preference pairs. It is the wrong addition to Copilot ghost text or to Gmail Smart Compose, where the user is waiting on the first model. A reward model distilled from judge labels, the scorer in the preference cards, is the cheap online stand-in, and it keeps the judge's mistakes at a lower latency. Prices move. Recompute the bill from the current rate card and from the token counts you measured, and compare it with a person on the slice you still double-label.

Limited reasoning is a different failure, and Zheng and coauthors measured it on math. The judge does not only fail questions it cannot solve. On their probe it could solve the item alone and still accept a wrong candidate once that candidate was in the prompt. They graded LLaMA-13B against Vicuna-13B, in both orders, on 10 elementary math questions: 20 judgments. GPT-4's default prompt called a wrong answer correct on 14 of those 20. Asking it to reason in the same prompt cut that to 6 of 20. A reference answer the judge had produced on its own, shown beside the candidates, cut it to 3 of 20. Ten questions is a probe, not a rate for your exam set. The pattern is the one to keep. A number, a unit test, or a reference the judge did not see the candidate invent belongs in front of the prose verdict.

**Trade-offs.** A tight rubric raises human agreement and misses qualities you failed to write down. A frontier judge is closer to people on open text and too slow and too expensive for the request path. A cheap judge, or a reward model, fits the path and needs a fresh calibration because it will miss failures it cannot see. A reference answer helps on math and imports whatever is wrong in the reference. Ignoring these limits and shipping the judge raw is how a fluent, agreeable paragraph becomes the definition of quality. The systematic preferences that remain once the prompt is stable are the next card.

**Interview.** List the four limits and a mitigation for each. Inconsistency: pin the model, low temperature, a tie band. Ambiguity: anchored checks, and if people cannot agree, the level is not ready. Cost: offline for the frontier judge, a distilled reward model if you need a score on the request path. Limited reasoning: a program or an independent reference before the verdict, and quote the 14 of 20 probe as a probe. Leave position, verbosity, and self-enhancement for the bias card, and offer the human slice as the ongoing control, not as a one-time ceremony.

**Recap.** An AI judge is inconsistent on close calls, inventive when the rubric is vague, and too costly to sit on the user-facing path of a fast feature. It can also accept a wrong math answer it would have rejected in isolation. On a 10-question probe, that happened on 14 of 20 default judgments and on 3 of 20 once a separate reference was shown. Write criteria a person could reapply, keep the judge off the latency path, and put a program in front of any field a program can decide. A low temperature makes the judge repeatable. It does not make it right.

## Biases of an AI judge

Biases of an AI judge are systematic preferences that survive a stable prompt. Zheng and coauthors measured position and verbosity directly. They also looked for a self-enhancement effect, and that study could not establish it.

Position bias is a preference for a slot. The hard case in that paper is two similar answers to each first-turn MT-Bench question, both sampled from GPT-3.5 at temperature 0.7. The authors note that people sometimes cannot tell those answers apart, so this is not the flip rate on every prompt. On the default prompt, Claude-v1 gave the same verdict after a swap on 23.8 percent of pairs and favored the first position on 75.0 percent. GPT-3.5 was consistent on 46.2 percent and favored first on 50.0 percent. GPT-4 was consistent on 65.0 percent, the only judge in that table above 60 percent, and it still favored the first position on 30.0 percent. Renaming the assistants moved Claude's preference off the first slot, so the sign is a property of the prompt, not a law that first place wins. The measurement is the swap. Keep a win only when the same answer wins both orders. A flip is a tie. A few-shot prompt in the paper's appendix raised GPT-4's consistency on this probe from 65.0 percent to 77.5 percent, at about four times the prompt cost, and the authors left zero-shot as the default because a more consistent judge is not automatically a more accurate one.

Verbosity bias is a preference for a longer answer. The paper's repetitive-list attack took 23 MT-Bench answers that already contained a numbered list, asked GPT-4 to rephrase that list without adding information, and prepended the copy, so a 5-item list became 10 items of the same content. The attack counts as a success when the judge prefers the padded answer. Claude-v1 and GPT-3.5 fell for it on 91.3 percent of those pairs. GPT-4 fell for it on 8.7 percent. The same judges returned a tie for two identical answers, so the failure is the padding, not an inability to notice an exact copy. Hold length roughly fixed when the pair is about a fact, and write in the rubric that extra length is not a reason to prefer. Then measure whether the instruction stuck. A public preference board has the same exposure. Arena's later style control puts length and markdown features into the Bradley-Terry regression so the displayed strength is what remains after those features. That is a control on the rating. It is not evidence that the voters stopped liking long answers.

Self-enhancement is the paper's name, taken from the social-cognition literature, for a judge favoring answers from itself. The study does not establish that bias. Against the human voters, GPT-4's win rate for itself was 10 percent higher, and Claude-v1's was 25 percent higher. GPT-3.5 did not favor itself, and the judges that favored themselves also favored some other models. The authors say the data cannot determine whether a self-enhancement bias is real, because they could not rewrite an answer into another model's style without also changing its quality. Later arena writeups have kept measuring self-preference. Treat the effect as a test you run on your slice, not as a rate you cite from 2023. On the rows that decide a launch, use a different model family or use people. A model that ranks two of its own prompts can tell you which prompt it prefers. It cannot acquit its own answer.

**Trade-offs.** Swap-and-agree removes position flips and doubles the judge bill on pairwise rows. Length-controlled pairs make a factual comparison readable and hide a real quality difference that was mostly length, so you report both the controlled and the raw result when length is part of what users like. A different judge family reduces the chance that you are grading a model's taste with the same taste, and it adds a vendor and a new calibration. Ignoring the three and shipping the raw verdict is how a long answer in the first slot, written in the judge's own voice, becomes the definition of quality.

**Interview.** Name the three, and give the condition on each number. Position: two similar GPT-3.5 samples, GPT-4 consistent on 65.0 percent, others lower, and the sign moved when the prompt renamed the assistants. Verbosity: 91.3 percent failure for Claude-v1 and GPT-3.5 against 8.7 percent for GPT-4, on 23 padded lists. Self-enhancement: the paper reports a higher self win rate and then says the bias is not established. The mitigations are the swap, a length control you measure, and a different family or a person on the launch slice. Do not quote any of those rates as the flip rate of the judge you have not tested.

**Recap.** An AI judge can prefer a slot, a longer answer, or its own voice, and only the first two were clearly measured in the MT-Bench study. On similar answers, GPT-4 kept the same verdict across a swap 65.0 percent of the time, and the other judges they tried did worse. On 23 padded lists, GPT-4 preferred the padding 8.7 percent of the time and the other two judges 91.3 percent. Self-enhancement was not established. Swap the order, hold length fixed when the fact is the question, and do not let a model grade its own family on the slice that ships.

## Which models can judge

Which model judges is a choice among a stronger model, the same model, a weaker model, and a specialized scorer. The right choice is the weakest judge that still sees the failures you care about, after you measure that it sees them.

A stronger model judging a weaker one is the default for open-ended quality. The MT-Bench result is about that setup. The judge has to be able to notice a mistake the generator makes. A frontier judge grading a small open model is the usual direction, and "frontier" is a moving target, so you name the model id you measured. The same model judging itself is a different test. It is a reasonable way to compare two prompts when you only care which prompt this model prefers, and it is a weak proof that the answer is good. Self-preference means the judge shares the generator's blind spots and its taste. A pairwise comparison of two samples from one model, judged by that model, tells you about its preference. It does not tell you about the truth of a refund.

A weaker judge is a cost decision with a hard condition. It can check a narrow criterion you have already shown it gets right, and it will miss subtle errors. Format is usually the wrong thing to spend it on, because a parser or a schema check is exact and cheaper. A weaker judge of open quality is something you earn with a calibration, not something you assume from the price. If its disagreements with people are exactly the severe failures, the savings are fake. Specialized scorers sit in this same budget slot and are often the better tool. They are not one tool. A reward model maps one completion to a scalar, which is what best-of-N uses at serving time. A reference-based judge scores a completion against a gold answer or a source. A preference model takes the question and two completions and predicts which one wins. PandaLM, JudgeLM, and Prometheus are published models in that specialized family. The input is the difference that matters: one completion and a score, a completion plus a reference, or two completions and a preference. An NLI model checks entailment. A toxicity or policy classifier checks one harm. The MT-Bench paper tried a Vicuna-13B judge trained on arena votes and reported the result as preliminary. Each of these scorers is strong on the narrow job and unqualified on the others, and a fine-tuned judge has learned the biases in the votes it was trained on. The Reward models card in [Understanding Foundation Models](../02_Understanding_Foundation_Models/) already notes the usual shortcut: if longer answers won the comparisons, length wins the score.

| Judge | The job it can hold | The check you still owe |
| --- | --- | --- |
| A stronger model | Open-ended quality of a weaker generator, and preference labels for training. | A human slice. The strong model still has position and verbosity biases, and a self-preference you measure rather than assume. |
| The same model | Which of two prompts this model prefers. | Someone else, or a checker, before you call the result correct. It shares the generator's blind spots. |
| A weaker model | A narrow criterion whose agreement with people you have measured, at a bill you can run often. | The severe rows. Agreement on easy passes is not enough. |
| A specialized scorer | A reward model for one completion, a reference-based judge against a gold answer, or a preference model such as PandaLM, JudgeLM, or Prometheus on a pair. Also an NLI model or a policy classifier. | The input it was trained on, and the shortcut it learned. Length is the usual one for a reward model. |

The judge and the generator should not be the same training run when the verdict gates a launch. Pin both ids. When you change the generator, the old calibration is a hypothesis. When you change the judge, it is a new metric.

**Trade-offs.** The strongest judge is the most credible open-ended rater and the most expensive, and it is a poor use of money on checks a program already makes. The same model is free of a second vendor and circular as an evaluation of itself. A weaker judge or a reward model makes nightly and online scoring affordable and will rubber-stamp failures below its ability. Keeping one judge for every criterion is simple and worse than a parser for syntax, an execution check for SQL, an NLI model for faithfulness, and a strong judge for the residue.

**Interview.** Match the judge to the asymmetry. Stronger judges weaker for open quality. Same model only for a preference between its own samples, not for truth. Weaker only where a measured agreement says the severe misses are rare. Specialized when the criterion is narrow enough to train or to prompt a small scorer. Say a schema does not need a judge at all. Mention the reward model as the distilled judge you already met in post-training, including its length shortcut. End with the pin: both model ids are part of the metric.

**Recap.** A stronger model is the default judge of open-ended quality, and it still needs a human slice. The same model can rank its own prompts and cannot acquit its own answers. A weaker model or a reward model, an NLI checker, or a policy classifier is the right judge when the criterion is narrow and you have measured agreement. Use a program instead of a model whenever a program can decide.

## Ranking from pairwise votes

Comparative evaluation ranks models by pairwise preferences. Each vote says which of two answers a person, or a judge, liked better. A rating system turns the votes into a strength for every model.

A win rate is the simplest summary and it lies when the schedule is uneven. A model that played more games, or played weaker opponents, can lead the win count while being the worse system. Head-to-head results are the data. Two statistical models turn head-to-head results into strengths, and they are the same idea in different clothes.

Elo updates a rating after each game. The expected score of A against B is `1 / (1 + 10 ^ ((R_B - R_A) / 400))`. A win scores 1, a loss scores 0, and a tie, if you allow one, scores 1/2. The update is `R + K (score - expected)`. K is a step size. A K of 32, a common step size in Elo implementations, moves a rating quickly and swings on a short streak. Two players who both start at 1500, and one win for A, move to 1516 and 1484. A 400-point gap is a 10-to-1 expectation under this formula: the favorite's expected score is `1 / 1.1`, about 0.9091. Online Elo depends on the order of the games and on K. Shuffle the votes and the path changes.

Both Elo and Bradley-Terry put every model on one line of strength. That placement assumes transitivity. If A is stronger than B and B is stronger than C, A is stronger than C, including on pairs you never showed. Sparse pairing depends on the assumption: the edges you did not annotate are filled in by the strengths the edges you did annotate implied. Real preferences cycle. A rater can prefer the careful answer to the short one, the short one to the witty one, and the witty one to the careful one, and no three numbers on a line represent that rock-paper-scissors. The fit will still emit strengths. The cycle shows up as a model that looks decisive in the table and contradictory in the votes. When the product has that kind of disagreement, report the pairwise matrix on the close models instead of only the rating, and do not treat a missing pair as decided.

```python
def expected(left: float, right: float) -> float:
    return 1 / (1 + 10 ** ((right - left) / 400))


def update(left: float, right: float, left_score: float, k: float = 32) -> tuple[float, float]:
    left_expected = expected(left, right)
    right_expected = 1.0 - left_expected
    return (
        left + k * (left_score - left_expected),
        right + k * ((1.0 - left_score) - right_expected),
    )


print(update(1500, 1500, 1))
print(f"{expected(1900, 1500):.4f}")
# (1516.0, 1484.0)
# 0.9091
```

Bradley-Terry fits a strength to the whole vote matrix at once. The probability that i beats j is `1 / (1 + e^(-(s_i - s_j)))`, the logistic of the strength gap. That is the model behind the reward-model loss in the previous topic. A gap of `ln(10)` in that logistic is the same 10-to-1 that 400 Elo points represents, so the two formulas differ by a change of unit, not by a different story about pairs. The fit is maximum likelihood over the observed games. It does not depend on the order you feed the games in. Chatbot Arena, from LMSYS, is the public version of this evaluation. People chat with two anonymous models and vote. The board launched in May 2023 on online Elo. A December 2023 writeup explains the switch to Bradley-Terry, because the board has the whole vote history and treats a pinned checkpoint as a fixed player, and the leaderboard dataset records the change in January 2024. The project was later called LMArena, and it now publishes as Arena. Cite the name on the page you read.

Their fit is meant as the maximum-likelihood version of the chess Elo model. The notebook that reproduces it puts log base 10 into the design matrix and multiplies the coefficients by 400, so a displayed gap of 400 is 10-to-1 by construction, before a constant that pins a reference model to a chosen score. A constant shift does not change gaps. A different codebase that multiplies raw natural-logit coefficients by 400 and calls the multiply cosmetic does not preserve the odds: a gap of 400 on that scale is odds of `e`, about 2.718 to 1. Style control, added after the switch and made the default on the text and vision boards in 2025, puts answer length and markdown counts into the same regression. A style-controlled gap is the preference left after those features, not the raw vote. The fixed-strength assumption also fails when a hosted API changes under one name, which is why the board separated versions such as GPT-4-0314 and GPT-4-0613. Read the method note, the date, and whether style control is on.

Votes include ties. A plain win/loss Bradley-Terry model drops ties or forces them into a win, and either choice answers a different question than the ballot asked. Arena's published fit counts a tie as half a win for each side, and the ballot also separates a tie where both answers are bad from a tie where both are acceptable. Report which rule you used. Bootstrap or another resampling of the votes gives an interval on the strength. The online-Elo intervals on the early board were too wide because the same shuffled paths were used for the point and for the interval. The Bradley-Terry bootstrap is the later interval. Two models whose intervals overlap are not a clean ranking, however the table sorts them. Overlap is a conservative reading: a real gap can still have overlapping marginal intervals, so overlap means you do not treat the sort order as the decision.

**Trade-offs.** Pairwise votes match the way people experience a chat product, side by side, and they scale poorly in the number of models, which is the next card. Elo is easy to update online and path-dependent. Bradley-Terry uses all the votes and needs a refit when new votes arrive. A public arena rank is a useful external signal and a poor internal launch gate, because the prompts are whoever showed up and the rank is relative. Hiding the model names during the vote is what makes the comparison about the answer. Showing them turns it into a brand preference.

**Interview.** Write the Elo expected-score formula, update 1500 against 1500 with a K of 32, and state that 400 points is 10-to-1 in that formula. Then write Bradley-Terry as the logistic of a strength gap, and connect it to the reward model. Say Arena launched in May 2023 on online Elo, switched to a Bradley-Terry fit whose 400-point gap is 10-to-1 under their scale, and later added style control, so you cite the method, the date, and the style setting. Mention ties, order dependence, and a hosted model that changed under one name as the three ways a casual implementation picks a different winner. Finish by separating the ranking from a ship decision. The best of this pool can still fail an absolute test.

**Recap.** Comparative evaluation ranks models from pairwise preferences. Elo updates a rating after each game. From 1500 and 1500, one win at K of 32 moves the ratings to 1516 and 1484, and a 400-point gap means a 10-to-1 expected score in the chess formula. Bradley-Terry fits the same kind of pairwise strength on the whole matrix at once and does not depend on game order. Chatbot Arena, later LMArena and now Arena, launched on online Elo in May 2023 and moved to Bradley-Terry, with style control as a later default. A rank needs the method, the date, and whether that control was on.

## Challenges of comparative evaluation

The challenges of collecting a comparative evaluation are the quadratic number of pairs and the quality of the votes. A relative win is a separate problem, on the next card.

Scalability is the quadratic. Five models are 10 pairs. Twenty models are 190 pairs. Fifty votes on each of those 190 pairs is 9,500 judgments, and the next model you want to try starts the problem again. A full matrix is the wrong plan past a handful of variants. You sample pairs. Uniform random pairing is simple and spends votes on lopsided matchups whose winner you already knew. Pairing a new model with the current production model spends the votes on the decision you actually have. Active pairing spends the next vote on a comparison that would change the ranking, instead of filling every cell. Arena's writeups use a non-uniform schedule rather than a full matrix. That spends votes where the ranking is uncertain. It also means a raw win count, or a Bradley-Terry fit that assumes every pair was equally likely to be shown, is the wrong estimator unless the likelihood describes the sampling rule. An active rule that secretly prefers a model you hope will win bakes that preference into the rating. People do not scale to 9,500 careful reads. An AI judge scales and brings the bias card with it, so a judged arena is only as trustworthy as the swap check and the human slice.

Standardization and quality control are the other half of a vote. Chatbot Arena's prompts are whatever people type. Chiang and coauthors, in the 2024 platform paper, argue that those prompts are diverse and that the crowd votes agreed with expert raters in their study. That is a reason to take the public board seriously as a board. It is not a measurement of a Shopify returns queue or a Notion summary. Employee votes in an internal tool, with no guideline and no gold pairs, are a different measurement. A rater who prefers long, friendly answers crowns a verbose model, which is why the public board later put length into the regression instead of trusting the raw vote. A rater who stops reading votes for the first position. The controls are the ones survey work uses. Write the guideline. Insert gold pairs whose winner you know, and drop or retrain raters who fail them. Match the prompt mix to production traffic, including the languages you ship. Hide model names. Decide what a tie is, including a both-bad tie, which the arena ballot separates from a tie where both answers are acceptable. Publish the agreement between raters. A program that copies the arena interface and skips these controls has copied the form.

**Trade-offs.** Sampling pairs makes a comparison affordable and makes a naive win rate wrong. Crowd votes are plentiful and off your distribution. Expert votes match the rubric and do not scale. An AI-judge arena is fast and needs the bias controls. Active sampling finds the close pairs sooner and misspecifies the rating if you ignore the sampling rule. A copied leaderboard UI without gold pairs, hidden names, and a tie rule measures the raters' habits.

**Interview.** Quantify the quadratic with five models and twenty, and with fifty votes on the twenty-model matrix, 9,500 judgments. Then give the sampling response, and the reason a raw win count fails when the schedule is partial or active. Separate a public arena, which has a measured prompt mix and a paper behind it, from an informal internal vote. List the quality controls: guidelines, gold pairs, hidden names, a both-bad tie, rater agreement, and a prompt mix from your traffic. Leave the question "does the winner actually work" to the next card.

**Recap.** Comparative evaluation does not scale as a full matrix. Five models are 10 pairs and twenty are 190, and fifty votes on those 190 pairs is 9,500 judgments. Sample the pairs, and use an estimator that matches the sampling. The votes need guidelines, gold pairs, hidden model names, a declared tie rule, and a prompt mix from your traffic. A public arena's crowd is evidence about that crowd. It is not your support queue.

## From a ranking to a pass

A ranking says who won among the models you entered. It does not say the winner is good enough to ship. Elo and Bradley-Terry have no unit for "correct."

A gap of a few dozen points is not an accuracy. Two models whose bootstrap intervals overlap are not a decision, however the table sorts them, and a gap can be real while the marginal intervals still overlap. Style control removes a length and markdown effect from the strength. The residual is still a preference. A preference for a fluent answer that states the wrong return window is still a win. The best of five internal drafts can fail a fail-to-pass test, or lose to the current production model on the slice that pays the bills, while beating it on a general chat vote. The absolute gate stays with the exact checks and with a rubric that has a pass line, not only a preference. Use the ranking to choose which variant earns the expensive absolute eval. Use execution, exact field checks, and that pass line to decide whether anything ships. A pool of weak models will happily rank itself.

**Trade-offs.** Optimizing the arena rank as if it were the product metric produces models that win side-by-side chats and fail the task. Keeping only absolute metrics makes model selection among close variants slower than it has to be, because people are bad at giving stable 1-to-5 scores and better at saying which of two answers they prefer. Reporting the style-controlled rank without the raw rank hides the case where users really do prefer the longer answer. Reporting only the raw rank crowns length.

**Interview.** Separate the two questions in one sentence. The ranking chooses the candidate. Tests, execution, and a pass line on the rubric choose the launch. Give the failure mode: the winner of a weak pool, or a style-controlled preference for a wrong window. A win inside the pool is not a quality bar.

**Recap.** A comparative rating is relative. Elo and Bradley-Terry do not measure correctness, and a style-controlled score is still a preference. The winner of the comparison still has to pass the absolute checks before it ships. Use the ranking to decide who earns that expensive eval, and use the eval to decide what launches.

## Where comparative evaluation is going

The useful direction is a standing system a team actually runs: pairwise ranking for model choice, exact checks wherever a program can decide, a calibrated judge for the open residue, and people on a sample that keeps the judge honest.

The public board already did the statistical half. It moved from online Elo to Bradley-Terry, publishes bootstrap intervals, splits category boards so a coding rank is not the chat rank, and fits style features so length is not the whole score. What a product team still has to assemble is the private half of the same protocol. The prompts come from production traffic, they stay out of the training crawl, and every field a program can decide is checked before a judge sees the residue. Contamination is why the handwritten HumanEval problems mattered, and it is why a public set you do not rotate will flatter a model that trained on it. A private set has the same fate if those prompts are pasted into a finetune. Reward models are the training-time form of the pairwise signal. A judge labels pairs, a scorer distills them, and the policy updates. That loop does not retire the judge. It makes an unevaluated judge more expensive, because the mistake is now in the weights.

What this does not become is a single automatic number that replaces measurement. A comparative win stays relative. An AI judge stays biased and in need of a human slice. Perplexity stays a next-token statistic. Report the method, the date, and whether style control was on next to any public rank, and rebuild the human slice when the judge model id changes. [Evaluate AI Systems](../04_Evaluate_AI_Systems/) is the pipeline that turns the tools in this topic into that gate: which criteria, which data, and how the score is produced for a launch. Prices, boards, and which model is a credible judge all move. The structure of the measurement does not.

**Trade-offs.** A standing eval system catches a regression the week it ships and costs a permanent labeling and judging budget. A one-time leaderboard read is free and stale. Category and private arenas are more relevant than one global chat rank and are another set of votes to keep healthy. Distilling the judge into a reward model makes the signal cheap to apply and expensive to audit. Waiting for a perfect automatic metric delays the launch. Shipping without the absolute checks launches the best of a bad pool.

**Interview.** Describe the system you would run, not a prediction about a future model. Pairwise votes, with a declared Elo or Bradley-Terry fit, an interval, and a style setting, choose the variant. Execution and exact checks gate the fields they can see. A pinned judge scores the open residue, calibrated against a human slice you refresh when the judge changes. A private prompt set, drawn from production and kept out of training, replaces a public board as the internal source of truth. Say that a public rank is context, dated and method-stamped, and that the next topic is how this becomes a pipeline.

**Recap.** The public board already ranks with Bradley-Terry, intervals, category splits, and style control. The work left is the private half: prompts from real traffic, kept out of training, exact checks on every field a program can decide, and a calibrated judge for the rest. Public ranks remain a dated external signal, not the launch gate. Reward models distill the same pairwise signal into training and do not remove the need to audit the judge. The winner of a comparison still has to clear an absolute bar.
