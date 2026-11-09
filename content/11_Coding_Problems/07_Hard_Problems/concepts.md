## Hard means the structure is not obvious

A hard interview problem still has a correct brute force. What it does not have is an obvious next step. The search space looks exponential, the state you want to remember is unclear, or a direct simulation is far too slow for the stated limits. The work of the interview is to find a structure that shrinks that search: a recurrence, a bound, or a representation. Treat "hard" as a signal to spend longer on the model, not as a signal to guess.

## Spend time on the model

Before code, define the object you are actually computing. "The answer for the first `i` items," "the best score using exactly `k` steps," or "whether this prefix can reach the target." A vague model produces a vague recurrence. Write the small case next to the definition and check that the definition even makes sense there. Ten quiet minutes on the model beat a fast start on the wrong state.

## Shrink the argument

Recursive solutions need an argument that gets strictly smaller, or they do not terminate. The smaller piece might be the length of the remaining input, the number of choices left, or a bound that moved. State the base case in the same vocabulary as the recursive case. If you cannot say what decreased, you have a loop, not a recursion. If every branch decreases the same budget, you can also bound the depth.

## Cache repeated subproblems

If the same smaller question appears on many branches, the recursion is doing duplicated work. Store the answer under the arguments that fully describe the subproblem, and return the stored answer on the next visit. That is top-down dynamic programming. It is only valid when the subproblem really depends only on those arguments. If a hidden extra fact changes the answer, the cache is wrong. Name the arguments out loud; they are the cache key.

## Rewrite the question in math

Some hard problems stop being search problems once you restate them. A count becomes a formula. A "can you reach" question becomes a bound you can check. An invariant shows a position is unreachable, so you stop searching. Try this before you build a large table. The test is whether the rewrite agrees with the brute force on a small input. A pretty formula that fails `n = 3` is a guess.

## Keep the state small

The state is whatever you must remember to extend a partial answer. Extra fields multiply the number of states and can push a feasible solution out of time. Drop a field by proving it is determined by the others, or by processing the input in an order that makes the field unnecessary. If the state is still the entire input, you have not found the structure yet, and the algorithm is the brute force with more syntax.

## A correct slower solution beats a stuck clever one

Ship the brute force if the clever version is not ready, and say its complexity. Then describe the state you would cache and the cost you expect, even if you do not finish the code. Interviewers can give credit for a correct slow program and a clear faster plan. They cannot give credit for a fast idea you cannot show is correct. Mark the plan as a plan so you do not hand in an unfinished optimization as if it were done.
