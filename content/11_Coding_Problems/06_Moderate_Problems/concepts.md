## A moderate problem has one insight

A moderate interview problem is usually a straightforward goal with one structural trick: a counter that replaces a scan, a sort that makes a later step linear, or a representation that makes an update cheap. You are not expected to invent a new algorithm. You are expected to find the trick and implement it cleanly. If the solution needs several independent inventions, you have probably overcomplicated it, or the problem belongs in the hard set.

## Restate and constrain

Repeat the input, the output, and the limits in your own words. Ask what is large, what fits in memory, and whether duplicates or empty inputs are in bounds. Those answers choose the tool. A limit of "a few thousand" permits a quadratic check that a limit of "ten million" does not. Do this before you write code; a solution to a problem you misheard is a confident wrong answer.

## Try the brute force on a small input

Write the obvious correct approach and its cost, and run it by hand on an input of size three or four. The brute force is a specification you can test a faster idea against. It also shows the interviewer a correct answer early, which matters if you run out of time while optimizing. Skip it only when the brute force is the same idea as the improvement.

## Name the bookkeeping

Most of the trick is a structure that remembers something the brute force recomputes. Say what you look up and what you store: a count by key, the best value seen so far, the index of the partner this element needs. If you cannot name the lookup, you do not have the trick yet. The structure should make that lookup cheap, and the rest of the algorithm should be a loop that maintains it.

## Shrink what you search

Look for a reason a large part of the input cannot contain the answer. Sorted order lets you discard a half. A bound lets you stop early. A constraint that forces one variable lets you stop looping over it. State the discarded region and why it is safe. "I skip some of it" is not an argument; "anything past this index is larger than the target, and the array is sorted" is.

## Check the answer against the brute force

On a tiny input, compute the brute-force result and the improved result and demand that they match. Then check the edges you asked about at the start: empty, one element, all duplicates, the value that sits on the boundary. A mismatch is a bug in the optimization or a case the brute force handled and the new code skipped. Either way you would rather find it before the interviewer does.

## Practice by category, not by memorized prompts

Group practice by the shape of the trick: counting, sorting then scanning, two indexes moving inward, a small simulation, a careful reading of a limit. After you solve one, write down the trigger that should have suggested the structure ("I need a partner for each value" → a set of values already seen). Drilling titles trains recall of a writeup. Drilling triggers trains the next unseen problem. Do not store solutions to published problem lists in these notes.
