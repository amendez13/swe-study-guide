## Why evaluation is hard

Evaluating a foundation model means deciding whether a sample is good enough to ship, when more than one sample can be acceptable and the next call can draw a different one.

The difficulty is built into the product. A classifier on a fixed label set has one test, and the test is whether the label matches. ChatGPT, Claude, Gemini, GitHub Copilot, and a Zendesk draft are one family of models asked to do many jobs. A summary, a code suggestion, and a refund reply fail in different ways, so one public rank cannot be the launch gate for all three. The rank also moves as new models are added. The output is a sample from the distribution in [Understanding Foundation Models](../02_Understanding_Foundation_Models/). Two calls at a chat temperature can differ in wording, or in the fact. A stored golden sentence then rejects a faithful paraphrase and can accept a lucky draw that will not be the draw you serve tomorrow.

Public benchmarks have two further failures, and both show up before you pick a metric. They leak into training crawls. HumanEval was handwritten because code models had already seen public solutions on GitHub, and a score on a test that was in the crawl is recall. The decontamination step in the training-data card exists so a later number measures generalization. They also saturate. A benchmark that every frontier model aces no longer separates the systems you are choosing, and it was never your support queue. The metrics in the rest of this topic can move in opposite directions on the same change: next-token fit can worsen after the post-training that makes a chat model useful, and a word-overlap score can prefer a fluent answer that states the wrong policy. That is not a bug in the arithmetic. The numbers answer different questions. The work is to match the question to the failure a user would notice, to keep a program that can mark the output wrong wherever such a program exists, and to treat a judgment as a measurement you calibrate.

**Trade-offs.** A single leaderboard number is cheap to quote and it is the wrong gate for a support desk or an editor. A private set costs labeling and stays about your traffic. Judging every sample with a frontier model scales past a person on every row and spends a second model call, and it imports the judge's biases. A meeting that liked twenty tickets is still a demo, which is the milestone bar from the introduction topic.

**Interview.** Name the four reasons the score is hard: the task is open-ended, one model serves many tasks, each call is a sample, and public benchmarks leak and saturate. Then refuse a one-number launch decision. Ask which failure the metric is for. A wrong amount wants a checker. A paraphrase wants something other than string equality. A choice among five variants wants a comparison. Exact checks, similarity to a reference, a model used as a judge, and a pairwise ranking are the four tools, and the rest of the conversation is which failure each one can see.

**Recap.** Evaluating a foundation model is hard because many answers can be acceptable, one model is used for many tasks, each call is a sample, and public benchmarks leak into training data and then saturate. Metrics that all sound like quality answer different questions, and they can move in opposite directions. Match the metric to the failure a user would notice, and keep a real checker wherever one exists.

## Entropy

Entropy is the average surprise in a probability distribution, measured in bits when the logarithm is base 2. It is the shortest average encoding of draws from that distribution, and it is the floor under every language-model loss in this topic.

A distribution that always produces the same outcome has entropy 0, because there is nothing to learn. A fair coin has entropy 1 bit. A biased coin carries less, because you can guess the likely face and be right more often. The formula is the same for a next token. Sum over the vocabulary, and skip any outcome whose probability is 0, taking `0 log 0` as 0. The context changes the distribution, so a model has a different entropy at each position. Training does not minimize entropy. Entropy belongs to the data. Training minimizes the extra surprise of a model that has not matched the data, which is the next card.

Shannon's 1951 experiments put the entropy of printed English on the order of one bit per character. That estimate is a historical yardstick for the bits-per-character number later in this topic, not a score you can paste onto Llama or GPT-4. A base Llama or GPT model scoring the next piece of a Wikipedia sentence is the same sum, taken over that model's vocabulary at that context. The number moves if the tokenizer's pieces change, because two tokenizers define different random variables. A model's cross entropy on held-out text can approach the entropy of that text, and in expectation it does not fall below that entropy except by noise on a small sample. A very low number on the training text is a memorization smell. The number you trust is on bytes the training run did not use.

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

The formula is `H(p, q) = -Σ p(x) log q(x)`. It splits into two pieces that the previous card set up. `H(p, q) = H(p) + KL(p ‖ q)`. The entropy is the data. The KL divergence is the extra cost of encoding the data with the model's probabilities instead of the true ones. KL is zero only when `q` matches `p`, and it is positive otherwise, so cross entropy is entropy plus a penalty for being wrong. If the model puts probability 0 on an outcome the data still produces, the penalty is infinite. A softmax over the vocabulary gives every token a nonzero probability, which is why a training loss is a finite number rather than an infinity the first time a rare token appears.

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

The second tokenizer has the lower perplexity, 4.0552 against 7.3891, because each of its tokens was an easier local prediction. It used 400 tokens at 1.4 nats, 560 nats in total, against 250 tokens at 2.0 nats, 500 nats in total. The first model is the better encoding of these bytes, at 0.7213 bits per byte against 0.8079. A byte-level model such as ByT5 scores the next byte directly, so its average cross entropy, converted to bits, is already bits per byte. That is how a paper can set it next to a BPE model on one file. Shannon's order-of-one-bit-per-character estimate is the historical human yardstick for this scale. A model number far below the entropy of the text, on text it trained on, is the memorization smell from the entropy card.

**Trade-offs.** Bits per byte lets you compare tokenizers and languages, and it still only measures next-token fit on the bytes you scored. It says nothing about instruction following. Computing it requires the token counts and the original file length, which a per-token loss chart hides. Bits per character is easier to explain on English prose and it becomes a different metric the moment the corpus is not ASCII or the normalization changes. Reporting either number on the training file flatters the model. The held-out file is the measurement.

**Interview.** Say that perplexity and token loss live on the tokenizer's pieces, and bits per byte lives on the file. Walk the conversion, total nats divided by `ln(2)` divided by bytes, and give a pair of exercise losses where the lower perplexity is the worse encoding. Mention UTF-8 so you have a reason to prefer bytes over characters for a multilingual launch. If the question is which chat model to ship, say this number is the wrong tool once post-training has changed the objective, and go to the next card.

**Recap.** Bits per character and bits per byte divide a model's total cross entropy, in bits, by the length of the original text. They exist so a 250-token encoding and a 400-token encoding of the same file can be ranked. On the exercise pair, perplexity prefers the 400-token model, 4.0552 against 7.3891, and bits per byte prefers the 250-token model, 0.7213 against 0.8079. Use bytes when the script or the normalization would make a character count ambiguous.

## Perplexity

Perplexity is the exponential of the average next-token cross entropy. It restates that loss as an effective number of equally likely choices at each token.

If the mean loss is in nats, perplexity is `e` to that power. If the mean loss is in bits, perplexity is 2 to that power. The two formulas agree when the bit figure is the nat figure divided by `ln(2)`. A model that assigned probability 1 to every observed token has perplexity 1. A model that assigned probability `1/k` to every observed token has perplexity `k`. That is the reading to keep: perplexity 7.39 means that, on this corpus, the model was as uncertain as a uniform guess among about 7.39 tokens. Lower is a tighter fit to the measured text. It is not a percent accuracy, and it is not comparable to a score on HumanEval or to a preference win rate.

The base is part of the definition. A dashboard that prints "loss 2.0" might be nats, which is what a standard causal-language-model trainer reports, or it might already be bits. Exponentiating with the wrong base invents a different model. The check below is the whole trap. The same printed 2.0 is perplexity 7.3891 in nats and perplexity 4 in bits.

```python
import math

loss_nats = 2.0
loss_bits = loss_nats / math.log(2)
as_nats = math.exp(loss_nats)
as_bits = 2**loss_bits
wrong_base = 2**loss_nats
print(f"{as_nats:.4f} {as_bits:.4f} {wrong_base:.4f}")
# 7.3891 7.3891 4.0000
```

The three-outcome model on the cross-entropy card had a cross entropy of 0.8869 nats. Its perplexity is `e` to that power, about 2.43, which is small because that example had only three outcomes. A real vocabulary has tens or hundreds of thousands of pieces, and a perplexity in the tens can still be a strong next-token model. You only interpret the number next to the vocabulary, the tokenizer, and the corpus that produced it.

**Trade-offs.** Perplexity is a faithful rescaling of the training loss, which makes it a good chart for a pretraining run and a bad chart for a product. A perplexity chart stretches absolute gaps at the high end. A drop from 20 to 10 and a drop from 4 to 2 are the same factor of two, and the same loss gap of `ln(2)` nats, about 0.693. The chart shows the first drop as ten points and the second as two. Quoting perplexity without the tokenizer and the corpus lets a larger vocabulary, or an easier test file, win an argument it did not earn.

**Interview.** Define perplexity as `exp` of the mean nat loss, give the 2.0 nats example as 7.3891, and show that treating those 2.0 as bits yields 4. Explain the branching-factor reading in one sentence. Then say what would make you refuse a comparison: a different tokenizer, a different corpus, or a chat model whose training objective is no longer the corpus you measured. The next card is that refusal, in detail.

**Recap.** Perplexity is `e` raised to the average next-token cross entropy in nats, which is the same number as 2 raised to that cross entropy in bits. A loss of 2.0 nats is perplexity 7.3891, the uncertainty of a uniform guess among about 7.39 tokens. Treating the same 2.0 as bits produces 4, so the base is part of the answer. Lower perplexity means a tighter fit to the measured text, for one tokenizer and one corpus.

## How to read perplexity

Reading perplexity means deciding what a change in that number is evidence of. The number is evidence about next-token fit on one corpus under one tokenizer, and several common changes are evidence of something else.

Use it inside a pretraining run. The same tokenizer, the same held-out slice of the same mix, a falling perplexity: the run is still fitting that slice. That curve is the smooth loss the scaling cards extrapolate, and it is still not a help-desk rubric. Use it as a domain probe. If a base model has a much higher perplexity on your Zendesk exports than on a Wikipedia slice, under one tokenizer, the tickets are surprising to that model. The gap is a domain gap. It does not, by itself, say the model will be a bad support bot once the reply is in the prompt and the policy is retrieved. Use it as a corpus filter. The perplexity cutoff in the training-data card is one model scoring documents. A very high score is often junk or a language the model barely saw. A very low score, on text the model trained on, can be a duplicate it has memorized. Both thresholds are valid for that model and that tokenizer only.

Do not use it across tokenizers. The bits-per-byte card is the counterexample: a drop in perplexity from 7.3891 to 4.0552 was a worse encoding of the same bytes. Do not use a raw web perplexity to accept or reject a post-trained chat model. Supervised finetuning and preference training change the objective. The model is pushed toward replies a rater preferred, and away from continuing a Wikipedia article in the raw. Perplexity on that article can rise while win rate on your replies rises. The InstructGPT work called the regressions on tasks the preference step was not optimizing an alignment tax, and it mixed pretraining updates back in to reduce them. Quote a measured tax on your tasks if you have one. A rise in pretraining perplexity is a reason to look at those tasks. It is not, by itself, a reason to revert the chat model. Perplexity also cannot see a wrong fact that was locally probable, a failed unit test, or a preference between two fluent answers.

**Trade-offs.** A held-out perplexity chart is the cheapest honest monitor for a pretraining run, and it will smile on a run that is fitting the web while your product metric is flat. Bits per byte fixes the tokenizer comparison and inherits every other limit of next-token fit. Keeping a base-model perplexity gate on an instruct checkpoint will reject useful post-training. Dropping perplexity entirely leaves you without a training curve and without a simple domain probe. The split is: perplexity for "are we fitting this text under this tokenizer," and a task metric for "should a user see this answer."

**Interview.** The uses you defend are comparing checkpoints of one training run, comparing domains under one tokenizer, and filtering a corpus with one scoring model. The uses you refuse are ranking two tokenizers by perplexity, and accepting a chat model because Wikipedia perplexity fell. Tell the alignment-tax story without inventing a delta you did not measure. Offer bits per byte as the repair for the tokenizer case. If the interviewer wants the product decision, leave perplexity and name the checker: tests, execution, or a calibrated judge.

**Recap.** Perplexity compares next-token fit for one tokenizer on one corpus. It is a training curve, a domain probe, and a corpus filter. It is not a ranking across tokenizers, and a rise after supervised or preference training can be the objective changing rather than the chat model getting worse. The ship decision stays with the task metric the user actually feels.

## Exact and subjective evaluation

Exact evaluation marks an output right or wrong with a program. Subjective evaluation marks quality by a judgment, because more than one output is acceptable and no program has the rule.

A unit test, a multiple-choice key, a normalized short label, and a SQL result set are exact. The program can be harsh and still be the right judge, because the product needs that field to be that value. "Was this helpful," "is this summary fair," and "does this Claude reply sound like our support desk" are subjective. People disagree on the boundary, so the metric has to include the rubric and the rater, not only the model. Most shipped features are mixed, and the mix is the design. A Notion AI summary of a meeting note has a decision and a date that either match the note or do not, and it has a phrasing that can go several acceptable ways. The date wants an exact check against the note. The phrasing wants a judgment, and only after the facts have passed. A JSON schema, from the structured-output card, is exact about syntax and silent about whether the total is the total on the receipt.

The common failure is crossing the streams. String-matching a Gmail summary treats a subjective phrasing as if it were a label, so a correct paraphrase looks like a defect. Asking a model "is this SQL right" treats an exact, executable question as if it were an opinion. You already have the database. The functional-correctness card and the judge cards later in this topic are the two tools. This card is only the choice of which tool you are allowed to use.

**Trade-offs.** Exact checks are repeatable, cheap to rerun, and blind to every quality they were not coded to see. A test suite can pass a patch that implements the wrong product behavior the tests forgot. Subjective judgments cover tone, usefulness, and the open residue, and they drift with the rater, the prompt, and the day. Using a judgment where a checker exists spends money to approximate a bit you could have measured. Using a checker where the answer is genuinely open punishes every acceptable answer except the one in the file.

**Interview.** Split the feature into fields before you name a metric. Facts, amounts, labels, code behavior, and query results are exact. Tone and "which of these two helpful replies" are subjective. Say that a schema check is exact and is not the business rule. Give the Notion-style summary as the mixed case: the date is checked against the source, and the prose is judged only if the date survived. If you cannot name a program that could mark the output wrong, you are in the subjective half, and you owe a rubric.

**Recap.** Exact evaluation is a program that marks the output right or wrong. Subjective evaluation is a judgment on a quality no program has a rule for. Code tests, labels, and query results are exact. Helpfulness and tone are subjective. A real feature usually has both, and each field should use the tool that matches that field.

## Functional correctness

Functional correctness means the output does the job when a program runs it: the tests pass, the query returns the right rows, or the patch builds and the suite goes green.

Natural language has no such oracle for a paragraph. Code and queries do. HumanEval, from Chen and coauthors in the Codex paper, is 164 handwritten Python problems, each with unit tests, about 7.7 tests per problem in the paper. A sample is correct when those tests pass. The problems were handwritten because the training corpus already contained public solutions, which is the leak from the first card. The headline metric is pass@k, the probability that at least one of k samples passes. Generating k samples and calling a problem solved when any one passes is an unbiased estimate with high variance. The paper instead draws `n ≥ k` samples, counts the `c` that pass, and uses an unbiased estimator for that problem: `1 - C(n - c, k) / C(n, k)`, or 1 when fewer than k samples failed, because every subset of size k then contains a pass. The paper uses n = 200 samples per problem. Average the per-problem estimates. The product form in the paper is the same estimator written so large binomial coefficients do not overflow.

If you already know a single sample passes with probability p and the failures are independent, the chance that k tries contain a pass is `1 - (1 - p)^k`. That is the ceiling on the test-time compute card. HumanEval does not hand you p. It hands you c successes in n draws. Plugging `p̂ = c / n` into the independence formula is a different, biased number. On 3 successes out of 10, the unbiased pass@5 is 0.9167 and the plug-in is 0.8319.

```python
import math


def pass_at_k(n: int, c: int, k: int) -> float:
    if n - c < k:
        return 1.0
    return 1.0 - math.comb(n - c, k) / math.comb(n, k)


print(f"{pass_at_k(10, 3, 1):.4f} {pass_at_k(10, 3, 5):.4f}")
print(f"{1 - (1 - 3 / 10) ** 5:.4f}")
print(f"{pass_at_k(10, 6, 5):.4f} {pass_at_k(10, 0, 5):.4f}")
# 0.3000 0.9167
# 0.8319
# 1.0000 0.0000
```

pass@1 and pass@10 are different budgets. Copilot ghost text gets one try inside a tight latency budget. A background agent that opens a pull request can spend several tries and a test suite, which is why a leaderboard pass@100 is not the number for an inline suggestion. SWE-bench is the same idea at issue size: a generated patch is correct when the project's tests pass. Execute untrusted code in a sandbox with a timeout. The metric is not a reason to `exec` a model string on the host.

Text-to-SQL has the same shape and a trap in the string. Spider's published metric matches SQL structure. BIRD's headline metric runs the query and compares the result. Two strings can differ by case, quoting, or an `ORDER BY` and still return the same rows, and two identical-looking queries can return different rows on a database the string does not reveal. A product checker runs a single read-only statement, with a timeout and a row cap, and compares the result multiset. It refuses anything that is not that statement. A model judge reading the SQL text is a later card, and it is the wrong first checker when the warehouse is right there.

**Trade-offs.** Execution is the metric the user feels, and it is only as good as the tests. A thin HumanEval-style suite can pass a function that fails the next input. A result-set match can pass a query that scanned a private table to get there, so the authorization check sits beside the correctness check. pass@k rises with k and will flatter a system that spends more samples than the product will spend. String match on SQL or on source code is cheaper than execution and rejects equivalent programs. Sandboxing costs engineering and is the cost of running the metric at all.

**Interview.** Define functional correctness as behavior under execution, and name HumanEval and pass@k. Compute the unbiased estimator on a small n, c, and k, and contrast it with `1 - (1 - p)^k` so you do not mix the estimate with the independence ceiling. Say pass@1 and pass@10 are different products. For SQL, prefer the result table over the string, and name the read-only guard. Mention that the tests can be wrong or incomplete, so a green suite is evidence about those tests.

**Recap.** Functional correctness runs the output. HumanEval's 164 problems and SWE-bench patches are correct when tests pass, and text-to-SQL is correct when the result table matches. pass@k is the chance that k samples contain a pass. With 3 successes in 10 draws, unbiased pass@1 is 0.3000 and pass@5 is 0.9167, against a biased plug-in of 0.8319 for k of 5. Compare that number at the sample budget the product actually has.

## Exact match

Exact match means the output and the reference are the same string after a normalization you wrote down before you looked at the score.

The normalization is the metric. Case, whitespace, punctuation, and whether articles count are decisions, and changing them changes the number. SQuAD reports exact match after a published normalization that lowercases, strips punctuation, and drops the articles "a," "an," and "the," and it also reports a token-level F1 that gives partial credit when the predicted span and the gold span share words. Both still want the answer's words. A classification label, a multiple-choice letter, and a normalized entity are the settings where exact match is the whole evaluation. The output is short, the legal answers were enumerated, and a near miss is a miss.

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

N-gram overlap counts shared chunks of tokens. Precision is the fraction of the candidate's chunks that appear in the reference. Recall is the fraction of the reference's chunks that appear in the candidate. On the strings "the refund was issued today" and "the refund was issued yesterday," five of the six tokens match, and the token that differs is the fact. BLEU, from Papineni and coauthors in 2002, is a precision of n-grams, usually up to 4-grams, times a brevity penalty, designed for machine translation and read at corpus level. The penalty is 1 when the candidate is at least as long as the reference, and `e^(1 - reference_length / candidate_length)` when the candidate is shorter. A candidate of length 5 against a reference of length 10 is multiplied by `e^(-1)`, about 0.3679, even if every n-gram it did emit was perfect. The penalty exists because raw precision rewards saying less. ROUGE, from Lin in 2004, is the recall-oriented cousin used for summarization. ROUGE-N is n-gram recall. ROUGE-L uses the longest common subsequence, so it gives credit for shared words in order with gaps. sacreBLEU exists because small choices in tokenization and smoothing were making published BLEU numbers incomparable. Use one declared implementation.

Sentence BLEU without smoothing is 0 when any n-gram precision is 0. A good one-sentence paraphrase often shares no 4-gram with the reference and scores 0, which is the metric as specified and a bad product gate. Corpus BLEU over a whole test set is what the metric was built for, and it still prefers shared phrasing over a correct paraphrase and can score a wrong number highly when the rest of the sentence was copied. Overlap cannot see that "yesterday" and "today" are the whole task.

```python
import math

print(f"{math.exp(1 - 10 / 5):.4f}")
# 0.3679
```

**Trade-offs.** Lexical scores are deterministic, cheap, and reproducible, which is why translation and summarization research ran on them for years. They correlate with human judgments better in aggregate, on many similar sentences, than on one reply you are about to send. They punish a right answer in new words and forgive a wrong fact in familiar words. Edit distance is interpretable on short fields and absurd on a paragraph. Adding more references helps and does not create a notion of meaning. A modern product that still gates a chatbot on BLEU is using a translation metric on a job it was not designed to score.

**Interview.** Separate precision from recall, and place BLEU on the precision side with a brevity penalty and ROUGE on the recall side. Compute a tiny edit distance whose numeric closeness is a different amount, and a brevity penalty on a short candidate. Say sentence BLEU can be 0 for a fine paraphrase, so you want corpus BLEU or you want a different metric. Name sacreBLEU as the way two teams get the same number. Then say the metric you would actually ship for a support reply: check the facts exactly, and judge the wording with a calibrated rater.

**Recap.** Lexical similarity measures shared surface form. Levenshtein distance counts edits, and "$12.50" versus "$125.0" is only distance 2 while the amount grows by ten. BLEU is n-gram precision with a brevity penalty, and a candidate half as long is multiplied by about 0.3679. ROUGE is n-gram recall. All of them prefer familiar wording, and none of them know that the unmatched word was the fact.

## Semantic similarity

Semantic similarity scores whether two texts mean the same thing, including when they share few words.

"We sent the money back" and "The refund was issued" can be the same support event and a near-zero BLEU. The previous card is blind to that pair on purpose. A semantic metric tries to score the pair anyway, using a model of meaning rather than a count of tokens. Three tools show up in practice. A sentence embedding turns each text into one vector and uses cosine similarity, which is the next card. BERTScore, from Zhang and coauthors, stays at the token level: each token is a contextual vector from a model such as BERT, tokens in the candidate are matched greedily to tokens in the reference by cosine, and precision, recall, and F1 fall out of that matching. Optional inverse-document-frequency weights keep "the" from counting like "refund." A natural-language-inference model, such as a DeBERTa model finetuned on MNLI, answers a different question: does the source entail the candidate, contradict it, or neither. Entailment is the check you want for a summary sentence against the Gmail thread or the help-center article. Cosine similarity of two fluent sentences is not that check.

The limit is the same one embeddings have. Meaning-shaped models still miss the distinctions products care about. A negated policy, a swapped number, and a name replaced by a similar name can sit close in embedding space because the topic is the same. BERTScore will not save "30 days" against "60 days" just because both are durations, and it can look strong when the surrounding words match. An NLI model can catch a contradiction the cosine missed, and it can also miss it, or mark a paraphrase as a contradiction because the wording moved. You measure these failures on pairs from your own desk. A high semantic score is not functional correctness and not factuality. Two confident wrong answers can be very similar to each other.

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

Human preference is the quantity ChatGPT-style products are aligned to, and it is expensive. A rater has to read the source and the draft, apply a rubric, and do it again next week when the prompt changes. A strong model can do a first pass of that reading at the cost of another generation. Zheng and coauthors, in the MT-Bench and Chatbot Arena paper, found that a strong judge, GPT-4 in that study, agreed with human preferences more than 80 percent of the time, in the same range as people agreed with each other, on MT-Bench questions and on crowdsourced arena votes. That figure is for that judge and those questions. It is the existence proof that a judge can be in the band of human agreement. It is not a property of every model you might put in the judge seat, and it is not a result about your Zendesk rubric until you measure it there. Leaderboards and which model is "strong" move.

The economic case is real and easy to overread. A judge is cheaper than a trained rater on every row of a nightly regression, and it is more expensive than a unit test or an embedding cosine. It belongs on the residue those checks cannot see: whether a summary a person would accept, whether a refusal was appropriate, whether a draft followed the policy in a way the tests did not encode. It does not belong on a question the database can answer. Teams use judges to label preference pairs for the reward-model and DPO training in the previous topic, and to pick a winner among samples. Both uses inherit the judge. If the judge is wrong in a systematic way, the training update and the eval gate learn that way.

**Trade-offs.** A judge scales a kind of evaluation that otherwise stops at a few hundred human labels, and it adds a model you have to pin, pay for, and revalidate. Human labels on a slice are slow and are the calibration the judge cannot provide for itself. Using the judge without that slice turns MT-Bench's 80 percent story into an unmeasured hope on a different task. Skipping the judge and waiting on people for every prompt experiment freezes the iteration the feature needs. The workable split is a judge on the bulk, people on a stratified sample, and a program on every field a program can check.

**Interview.** Explain the missing oracle first. Open text has no test suite, people do not scale to every prompt change, and a strong model can approximate preference judgments well enough to be useful once it is calibrated. Cite MT-Bench as evidence that agreement can reach the human-human range, and immediately qualify the citation with the judge and the benchmark. Say you would double-label a slice of your own tickets before a judge could block a launch. Place exact checks ahead of the judge whenever they exist.

**Recap.** An AI judge grades open-ended model output so you can evaluate without a person on every row. The MT-Bench paper reported that GPT-4, as a judge, agreed with people more than 80 percent of the time, about as often as people agreed with each other, on that benchmark. Your rubric starts uncalibrated. Use the judge for the residue a program cannot check, and keep people on a slice large enough to see when the judge drifts.

## How to use an AI judge

Using an AI judge means choosing what you show it, what verdict you ask for, and how you will know the verdict matches a person.

Four setups cover the jobs teams actually run. A pointwise score asks for a number on one answer, often 1 to 5, against a rubric. Absolute scores drift, because the judge uses the scale differently on Tuesday than on Thursday, and a 4 is hard to compare across tasks. A pairwise verdict shows two answers and asks which is better, with a tie allowed. It is the more stable question for ranking, and it does not tell you whether either answer is good enough to send. A reference-based verdict gives the judge the source, or a gold answer, and asks whether the candidate is faithful to it or as good as the gold. That is the right shape for a summary against a Gmail thread. A rubric with anchored levels turns "helpful" into checks a second rater could apply. "The return window matches the article" is a level a person can agree on. "Be helpful" is a level the judge will invent.

| Setup | What you ask | What you can conclude |
| --- | --- | --- |
| Pointwise score | You show one answer and ask for a number on the rubric. | The number is useful when the levels are anchored. It drifts, so compare it inside one pinned judge and one rubric. |
| Pairwise | You show two answers and ask which is better, with ties allowed. | This is the stabler ranking signal. A win does not mean the winner is fit to ship. |
| Reference-based | You show the source or a gold answer beside the candidate. | The verdict is faithfulness to that source. A thin gold set still punishes other acceptable answers. |
| Anchored rubric | You write each level as a check, with an example of that level. | This is what keeps a pointwise score meaningful across weeks. |

The prompt is part of the metric, in the same way the normalization is part of exact match. Ask for a structured verdict, a label plus a short citation of the rubric line, so you can audit it. Put one graded example of each level in the prompt. Hide the model name, because a judge can prefer a name it recognizes. Pin the judge's model id and its temperature. A low temperature makes the verdict less noisy and does not remove a bias. Run the judge at the same setting you used when you measured its agreement with people.

Calibration is a small human set, not a feeling. Double-label a slice with the rubric you intend to keep. Report agreement, and report it in a form that subtracts the agreement you would get from the base rate. Cohen's kappa does that. Percent agreement looks strong when both the person and the judge mark most rows as a pass. Read every disagreement before you change the model. The disagreements are the spec: a vague level, a missing check, or a judge that cannot see the failure. Then relabel. A judge you have not run through this loop is a demo of a judge.

**Trade-offs.** Pairwise judgments are better for "which variant" and they multiply cost, because each row carries two answers. Pointwise scores are cheaper and harder to keep stable. Reference-based grading is only as good as the source you passed in. A long rubric improves agreement and starts to be ignored, or to dominate the context window, once it is a policy manual. Few-shot anchors help a weaker judge and can leak the style of the anchors into every verdict. Reasoning before the label gives you an audit trail and can be a fluent story written to fit a verdict the model already reached, so you still read a sample of the reasons.

**Interview.** Walk the four setups and match each to a decision. Ranking five prompt variants is pairwise. A nightly faithfulness gate on a summary is reference-based against the thread. A 1-to-5 helpfulness score needs anchored levels or you do not trust the 4. Then describe calibration: a double-labeled slice, a chance-corrected agreement, and a read of the disagreements. Mention that the judge prompt is pinned with the model id. Offer to swap answer order, which is the next card's bias, as the check you run before you believe a pairwise win rate.

**Recap.** An AI judge is a prompt plus a verdict schema plus a calibration. Pointwise scores, pairwise wins, reference-based checks, and anchored rubrics answer different questions. Hide model names, pin the judge, and keep the temperature where you measured it. Percent agreement is not enough. A chance-corrected agreement on a human slice, and a review of the rows where you differ, is what makes the number a metric.

## Limits of an AI judge

The limits of an AI judge are the ways the verdict moves when the answer did not: inconsistency, a vague criterion, the cost and latency of a second model, and systematic biases.

Inconsistency is the judge's version of the sampling problem. Close answers flip when you change a space, rename "Assistant A," or move to the next judge build. Temperature 0 reduces the flip rate and does not make the verdict a property of the answers alone. Treat a one-level gap on a 1-to-5 scale as a tie unless a second judgment agrees. For a launch gate, take a small majority on the pairs that sit near the boundary. Pin the judge id the way you pin the model you ship, and re-run the human slice when the id changes.

Criteria ambiguity means the rubric used a word the judge has to interpret. "Helpful," "natural," and "high quality" each hide a product decision. The judge will fill them in with a preference for fluent, complete, agreeable prose, which is the same shortcut a reward model learns when the comparisons contain it. The repair is an anchored check. "The window in the draft equals the window in the article" is a criterion. "Be helpful" is not. If two careful people cannot apply the level to a sample and land on the same mark, the judge cannot save the level.

Cost and latency are the reason the judge is an offline tool. The prompt carries the rubric, the source, and one or two answers, so the judge call is often more tokens than the draft you are grading. That is acceptable in a nightly regression and in a batch that labels preference pairs. It is the wrong addition to Copilot ghost text or to Gmail Smart Compose, where the user is waiting on the first model. A reward model distilled from judge labels, the scorer in the preference cards, is the cheap online stand-in, and it keeps the judge's mistakes at a lower latency. Prices move. Recompute the bill from the current rate card and from the token counts you measured, and compare it with a person on the slice you still double-label.

Bias is what remains when the prompt is stable. Three biases are documented well enough to design for. Position bias: the judge prefers a slot. On near-duplicate MT-Bench answers, Zheng and coauthors found the effect large, with most of the judges they tried favoring the first position, and only GPT-4 staying consistent across a swap on more than 60 percent of those hard pairs. The sign can flip with the prompt, so you measure it rather than memorizing "first place wins." The measurement is to swap the order and keep a win only when the same answer wins both ways. A flip is a tie. Verbosity bias: the longer answer wins because it is longer. The same paper's repetitive-list attack, padding a list without new information, fooled judges, with the stronger judge resisting more often. Hold length roughly fixed in pairs that should be about facts, and write "extra length is not a reason to prefer" in the rubric, then measure whether the instruction stuck. Self-preference, which that paper calls self-enhancement: a judge favors answers from its own family or its own style. The paper treats this as a bias to test, and you should too, without assuming a universal rate. Do not let a model grade its own outputs and call that an evaluation. Use another family for the judge, or use people, on the slice that decides the launch.

**Trade-offs.** Swap-and-agree removes position flips and doubles the judge bill on pairwise rows. A tight rubric raises human agreement and misses qualities you failed to write down. A frontier judge is closer to people on open text and too slow and too expensive for the request path. A cheap judge, or a reward model, fits the path and needs a fresh calibration because it will miss failures it cannot see. Ignoring these limits and shipping the judge raw is how a verbose answer from the judge's own family becomes the definition of quality.

**Interview.** List the four limits and a mitigation for each. Inconsistency: pin the model, low temperature, a tie band. Ambiguity: anchored checks, and if people cannot agree, the level is not ready. Cost: offline for the frontier judge, a distilled reward model if you need a score on the request path. Bias: swap for position, length-controlled pairs for verbosity, a different model family for self-preference. Quote the MT-Bench position result with its condition, near-duplicate answers, so you do not treat that hard-slice result as the flip rate on every prompt. Offer the human slice as the ongoing control, not as a one-time ceremony.

**Recap.** An AI judge is inconsistent on close calls, inventive when the rubric is vague, and too costly to sit on the user-facing path of a fast feature. It also has position bias, verbosity bias, and a self-preference for its own family's answers. Swap the order and keep consistent wins, write criteria a person could reapply, and calibrate against people. A low temperature makes the judge repeatable. It does not make it right.

## Which models can judge

Which model judges is a choice among a stronger model, the same model, a weaker model, and a specialized scorer. The right choice is the weakest judge that still sees the failures you care about, after you measure that it sees them.

A stronger model judging a weaker one is the default for open-ended quality. The MT-Bench result is about that setup. The judge has to be able to notice a mistake the generator makes. A frontier judge grading a small open model is the usual direction, and "frontier" is a moving target, so you name the model id you measured. The same model judging itself is a different test. It is a reasonable way to compare two prompts when you only care which prompt this model prefers, and it is a weak proof that the answer is good. Self-preference means the judge shares the generator's blind spots and its taste. A pairwise comparison of two samples from one model, judged by that model, tells you about its preference. It does not tell you about the truth of a refund.

A weaker judge is a cost decision with a hard condition. It can check a narrow criterion you have already shown it gets right, and it will miss subtle errors. Format is usually the wrong thing to spend it on, because a parser or a schema check is exact and cheaper. A weaker judge of open quality is something you earn with a calibration, not something you assume from the price. If its disagreements with people are exactly the severe failures, the savings are fake. Specialized scorers sit in this same budget slot and are often the better tool. A reward model trained on preference pairs is a judge distilled into a single score, which is what best-of-N uses at serving time. An NLI model checks entailment. A toxicity or policy classifier checks one harm. Each of them is strong on the narrow job and unqualified on the others. The reward-model card already notes the usual shortcut: if longer answers won the comparisons, length wins the score.

| Judge | The job it can hold | The check you still owe |
| --- | --- | --- |
| A stronger model | Open-ended quality of a weaker generator, and preference labels for training. | A human slice. The strong model has its own position, verbosity, and style biases. |
| The same model | Which of two prompts this model prefers. | Someone else, or a checker, before you call the result correct. It shares the generator's blind spots. |
| A weaker model | A narrow criterion whose agreement with people you have measured, at a bill you can run often. | The severe rows. Agreement on easy passes is not enough. |
| A specialized scorer | A reward model for best-of-N, an NLI model for faithfulness, a classifier for one policy. | The shortcut it learned. Length is the usual one for a reward model. |

The judge and the generator should not be the same training run when the verdict gates a launch. Pin both ids. When you change the generator, the old calibration is a hypothesis. When you change the judge, it is a new metric.

**Trade-offs.** The strongest judge is the most credible open-ended rater and the most expensive, and it is a poor use of money on checks a program already makes. The same model is free of a second vendor and circular as an evaluation of itself. A weaker judge or a reward model makes nightly and online scoring affordable and will rubber-stamp failures below its ability. Keeping one judge for every criterion is simple and worse than a parser for syntax, an execution check for SQL, an NLI model for faithfulness, and a strong judge for the residue.

**Interview.** Match the judge to the asymmetry. Stronger judges weaker for open quality. Same model only for a preference between its own samples, not for truth. Weaker only where a measured agreement says the severe misses are rare. Specialized when the criterion is narrow enough to train or to prompt a small scorer. Say a schema does not need a judge at all. Mention the reward model as the distilled judge you already met in post-training, including its length shortcut. End with the pin: both model ids are part of the metric.

**Recap.** A stronger model is the default judge of open-ended quality, and it still needs a human slice. The same model can rank its own prompts and cannot acquit its own answers. A weaker model or a reward model, an NLI checker, or a policy classifier is the right judge when the criterion is narrow and you have measured agreement. Use a program instead of a model whenever a program can decide.

## Ranking from pairwise votes

Comparative evaluation ranks models by pairwise preferences. Each vote says which of two answers a person, or a judge, liked better. A rating system turns the votes into a strength for every model.

A win rate is the simplest summary and it lies when the schedule is uneven. A model that played more games, or played weaker opponents, can lead the win count while being the worse system. Head-to-head results are the data. Two statistical models turn head-to-head results into strengths, and they are the same idea in different clothes.

Elo updates a rating after each game. The expected score of A against B is `1 / (1 + 10 ^ ((R_B - R_A) / 400))`. A win scores 1, a loss scores 0, and a tie, if you allow one, scores 1/2. The update is `R + K (score - expected)`. K is a step size. A K of 32, a common step size in Elo implementations, moves a rating quickly and swings on a short streak. Two players who both start at 1500, and one win for A, move to 1516 and 1484. A 400-point gap is a 10-to-1 expectation under this formula: the favorite's expected score is `1 / 1.1`, about 0.9091. Online Elo depends on the order of the games and on K. Shuffle the votes and the path changes.

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

Bradley-Terry fits a strength to the whole vote matrix at once. The probability that i beats j is `1 / (1 + e^(-(s_i - s_j)))`, the logistic of the strength gap. That is the model behind the reward-model loss in the previous topic. A gap of `ln(10)` is the same 10-to-1 that 400 Elo points represents, so the two formulas differ by a change of unit, not by a different story about pairs. The fit is maximum likelihood over the observed games. It does not depend on the order you feed the games in. Chatbot Arena, from LMSYS, is the public version of this evaluation. People chat with two anonymous models and vote. The May 2023 launch leaderboard used Elo. Later Arena writeups fit Bradley-Terry on the votes and display the coefficients on an Elo-like scale. The multiplier and the additive shift are display choices. A displayed gap of 400 on that board is not automatically a 10-to-1 under the chess formula. Read the method note on the board you cite. The board moves, and a rank without the date and the method is incomplete.

Votes include ties. A plain win/loss Bradley-Terry model drops ties or forces them into a win, and either choice answers a different question than the ballot asked. Report how you treated them. Bootstrap or another resampling of the votes gives an interval on the strength. Two models whose intervals overlap are not a clean ranking, however the table sorts them.

**Trade-offs.** Pairwise votes match the way people experience a chat product, side by side, and they scale poorly in the number of models, which is the next card. Elo is easy to update online and path-dependent. Bradley-Terry uses all the votes and needs a refit when new votes arrive. A public arena rank is a useful external signal and a poor internal launch gate, because the prompts are whoever showed up and the rank is relative. Hiding the model names during the vote is what makes the comparison about the answer. Showing them turns it into a brand preference.

**Interview.** Write the Elo expected-score formula, update 1500 against 1500 with a K of 32, and state that 400 points is 10-to-1 in that formula. Then write Bradley-Terry as the logistic of a strength gap, and connect it to the reward model. Say Arena launched on Elo and later reported a Bradley-Terry fit on an Elo-like scale, so you cite the method with the date. Mention ties and order dependence as the two ways a casual implementation picks a different winner. Finish by separating the ranking from a ship decision. The best of this pool can still fail an absolute test.

**Recap.** Comparative evaluation ranks models from pairwise preferences. Elo updates a rating after each game. From 1500 and 1500, one win at K of 32 moves the ratings to 1516 and 1484, and a 400-point gap means a 10-to-1 expected score. Bradley-Terry fits the same kind of pairwise strength on the whole matrix at once and does not depend on game order. Chatbot Arena has used both, displayed on an Elo-like scale, and the current board's method note is the citation.

## Challenges of comparative evaluation

The challenges of comparative evaluation are the reasons a careful ranking still misleads: you cannot afford every pair, the votes are only as good as the raters and the prompts, and a relative win is not an absolute pass.

Scalability is the quadratic. Five models are 10 pairs. Twenty models are 190 pairs. Fifty votes on each of those 190 pairs is 9,500 judgments, and the next model you want to try starts the problem again. A full matrix is the wrong plan past a handful of variants. You sample pairs. Random pairing, which is what a public arena does when two available models are shown together, is simple and spends votes on lopsided matchups. Pairing a new model with its nearest neighbors, or with the current production model, spends the votes where the decision is. Active schemes help and can bias the rating if the rule that picks the next pair is itself correlated with the outcome. The estimator has to match the sampling. A win count on a partial schedule is the failure mode the ranking card already flagged. People do not scale to 9,500 careful reads. An AI judge scales and brings the previous card's biases, so a judged arena is only as trustworthy as the swap check and the human slice.

Standardization and quality control are the other half of a vote. Chatbot Arena's prompts are whatever people type. The Arena paper argues those prompts are diverse and that the crowd votes agreed with expert raters in their study, which is a reason to take the public board seriously as a board. It is not a reason to treat the board as your support eval. Employee votes in an internal tool, with no guideline and no gold pairs, are a different measurement. A rater who prefers long, friendly answers will crown a verbose model. A rater who stops reading will vote for the first position. The controls are the same ones survey work uses. Write the guideline. Insert gold pairs whose winner you know, and drop raters who fail them. Keep the prompt mix matched to production traffic, including the languages you ship. Hide model names. Decide what a tie is. Publish the agreement between raters. A program that copies the arena user interface and skips these controls has copied the form.

From comparative performance to absolute performance is the launch gap. A rating says who won among the models you entered. It does not say the winner is good. The best of five internal drafts can still state the wrong return window, fail a HumanEval-style check, or lose to the current production model on the slice that matters while beating it on a general chat vote. Elo and Bradley-Terry have no unit for "correct." A gap of a few dozen points is not an accuracy. The absolute gate stays with the exact checks and with a rubric that has a pass line, not only a preference. Use the ranking to choose which variant earns the expensive absolute eval. Use the absolute eval to decide whether anything ships. A pool of weak models will happily rank itself.

**Trade-offs.** Sampling pairs makes a comparison affordable and makes a naive win rate wrong. Crowd votes are plentiful and off your distribution. Expert votes match the rubric and do not scale. An AI-judge arena is fast and needs the bias controls. Optimizing the arena rank as if it were the product metric produces models that win side-by-side chats and fail the task. Keeping only absolute metrics makes model selection among close variants slower than it has to be, because people are bad at giving stable 1-to-5 scores and better at saying which of two answers they prefer.

**Interview.** Quantify the quadratic with five models and twenty. Then give the sampling response, and the reason a raw win count fails on a partial schedule. Separate a public arena, which has a measured prompt mix and a paper behind it, from an informal internal vote. List the quality controls: guidelines, gold pairs, hidden names, a tie rule, rater agreement. Close on the absolute gap. The ranking chooses the candidate. Tests, execution, and a pass line on the rubric choose the launch. A win inside a weak pool is not a quality bar.

**Recap.** Comparative evaluation does not scale as a full matrix: five models are 10 pairs and twenty are 190, before you repeat the votes. The votes need guidelines, gold pairs, hidden model names, and a prompt mix from your traffic, and a public arena's crowd is not that mix. A rating is relative. The winner of the comparison still has to pass the absolute checks before it ships.

## Where comparative evaluation is going

The direction of comparative evaluation is a standing system: pairwise ranking for model choice, exact checks wherever a program can decide, a calibrated judge for the open residue, and people on a sample that keeps the judge honest.

The pieces already exist, and the practice is assembling them. Chatbot Arena showed that blind pairwise votes from a crowd can rank chat models in public, and category comparisons, a coding board beside a general chat ranking, have been published so one overall score is not the only number. Private arenas on a company's own tickets are the same protocol pointed at production traffic, which is the fix for a public board that is off-distribution, saturated, or contaminated by being famous. Contamination is why the handwritten HumanEval problems mattered, and it is why a public set you do not rotate will eventually flatter a model that trained on it. Confidence intervals are becoming part of the citation. A rank whose interval overlaps the next rank is not a decision, and Arena's statistical writeups already resample votes for that reason. Reward models are the training-time form of the same pairwise signal: a judge labels pairs, a scorer distills them, and the policy updates. That loop does not retire the judge. It makes an unevaluated judge more expensive, because the mistake is now in the weights.

What this does not become is a single automatic number that replaces measurement. A comparative win stays relative. An AI judge stays biased and in need of a human slice. Perplexity stays a next-token statistic. The teams that get this right keep the absolute gate, report the method and the date next to any public rank, and rebuild the human slice when the judge model id changes. [Evaluate AI Systems](../04_Evaluate_AI_Systems/) is the pipeline that turns the tools in this topic into that gate: which criteria, which data, and how the score is produced for a launch. Prices, boards, and which model is a credible judge all move. The structure of the measurement does not.

**Trade-offs.** A standing eval system catches a regression the week it ships and costs a permanent labeling and judging budget. A one-time leaderboard read is free and stale. Category and private arenas are more relevant than one global chat rank and are another set of votes to keep healthy. Distilling the judge into a reward model makes the signal cheap to apply and expensive to audit. Waiting for a perfect automatic metric delays the launch. Shipping without the absolute checks launches the best of a bad pool.

**Interview.** Describe the system you would run, not a prediction about a future model. Pairwise votes, with a declared Elo or Bradley-Terry fit and an interval, choose the variant. Execution and exact checks gate the fields they can see. A pinned judge scores the open residue, calibrated against a human slice you refresh when the judge changes. A private prompt set, drawn from production and kept out of training, replaces a public board as the internal source of truth. Say that a public rank is context, dated and method-stamped, and that the next topic is how this becomes a pipeline.

**Recap.** Comparative evaluation is heading toward a standing measurement: pairwise ranks with intervals, private sets drawn from real traffic, exact checks on every field a program can decide, and a calibrated judge for the rest. Public boards remain a dated external signal, not the launch gate. Reward models distill the same pairwise signal into training and do not remove the need to audit the judge. The winner of a comparison still has to clear an absolute bar.
