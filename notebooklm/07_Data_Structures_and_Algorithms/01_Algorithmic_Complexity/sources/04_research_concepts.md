# Data Structures and Algorithms Concepts

A distilled concept reference for studying data structures and algorithms, synthesized from the technical chapters of *Cracking the Coding Interview, 6th Edition* (see [course_outlines.md](course_outlines.md)). The book teaches through Java examples, but the durable value is the structural and algorithmic thinking: how to choose data structures, analyze complexity, and decompose problems.

---

## 1. Algorithmic Complexity

- **Big O notation** — describes how runtime or memory scales as input grows; industry usage typically expects the tightest practical upper bound.
- **Big Theta and Big Omega** — tight bound and lower bound respectively; academic distinctions that clarify what Big O alone leaves ambiguous.
- **Best, worst, and expected case** — the same algorithm can have different runtimes depending on input; worst case is the safety guarantee, expected case is the practical one.
- **Space complexity** — memory usage including stack frames from recursion and allocated data structures; tracked separately from time.
- **Dropping constants and non-dominant terms** — O(2N) simplifies to O(N), O(N^2 + N) becomes O(N^2); constants matter in practice but not in asymptotic analysis.
- **Multi-part algorithms** — sequential independent steps add their runtimes (O(A + B)); nested dependent steps multiply (O(A * B)).
- **Amortized time** — average cost across a sequence of operations; a single expensive resize does not change the per-operation average when surrounded by cheap appends.
- **Log N runtimes** — halving the problem space each step yields O(log N); binary search is the canonical example; base of the logarithm is irrelevant in Big O.
- **Recursive runtimes** — pattern: O(branches^depth); a dual-recursive call yields O(2^N) time but only O(N) space from the call stack.

## 2. Arrays

- **Fixed-size array** — contiguous block of memory with O(1) indexed access; size must be known at allocation.
- **Dynamic array (ArrayList)** — resizes by doubling capacity when full; preserves O(1) indexed access with amortized O(1) append.
- **Two-pointer technique** — using two indices to traverse an array from different positions or speeds; reduces many O(N^2) scans to O(N).
- **In-place manipulation** — modifying array contents without allocating a proportional extra structure; common interview constraint.
- **Matrix as 2D array** — row-column representation with coordinate transforms for rotation, zeroing, and traversal patterns.

## 3. Strings

- **Strings as character arrays** — string questions are often interchangeable with array questions; treat strings as sequences unless immutability changes the implementation.
- **String immutability** — in languages like Java and Python, string concatenation creates new objects; repeated concatenation can be O(xN^2).
- **StringBuilder / string buffer** — mutable buffer that avoids quadratic concatenation cost; accumulates parts and builds the final string in one pass.
- **Character set and encoding** — clarify assumptions about ASCII vs. Unicode, case sensitivity, and whitespace handling before solving string problems.
- **Frequency map** — counting character occurrences in a hash map or fixed-size array; foundational technique for anagram, permutation, and uniqueness checks.

## 4. Hash Tables

- **Hash table** — maps keys to values for efficient lookup; a common implementation uses an array of buckets plus a hash function.
- **Hash function and collision handling** — the hash function maps keys to array indices; collisions are resolved by chaining (linked list per bucket) or open addressing.
- **O(1) average, O(N) worst case** — lookup, insert, and delete are constant time with a good hash function, but degrade with many collisions.
- **Balanced BST as map alternative** — guarantees O(log N) lookup with ordered key iteration; useful when ordering or range queries matter.

## 5. Linked Lists

- **Singly linked list** — each node stores data and a pointer to the next node; O(1) insert/remove at head, O(k) access to the kth element.
- **Doubly linked list** — adds a previous pointer per node; allows O(1) removal given a reference to the node.
- **Head reference vs. wrapper class** — a bare head pointer is simple but complicates head-change operations; a wrapper class provides a stable entry point.
- **Node deletion** — find the previous node, update its next pointer; handle edge cases for head and tail nodes.
- **Runner (two-pointer) technique** — fast and slow pointers moving at different speeds; used for finding the midpoint, detecting cycles, and interleaving.
- **Recursive list processing** — many list problems have elegant recursive solutions, but each recursive call uses O(1) stack space, totaling O(N) for the full list.

## 6. Stacks

- **Stack (LIFO)** — last-in, first-out; supports push, pop, peek, and isEmpty, all in O(1).
- **Linked-list implementation** — add and remove from the same end of a linked list.
- **Explicit stack for recursion** — any recursive algorithm can be converted to iterative by managing an explicit stack of state.
- **Stack for backtracking** — push state when exploring a branch, pop when returning; foundational for DFS and expression evaluation.
- **Min stack** — augmenting a stack to track the current minimum in O(1) by storing min metadata alongside each element or in a parallel stack.

## 7. Queues

- **Queue (FIFO)** — first-in, first-out; supports add (enqueue), remove (dequeue), peek, and isEmpty, all in O(1).
- **Linked-list implementation** — add at one end, remove from the other; requires maintaining both first and last pointers.
- **Queue for BFS** — process nodes in discovery order; enqueue neighbors as they are found.
- **Two-stack queue** — a queue can be implemented with two stacks by reversing element order on demand; amortized O(1) per operation.

## 8. Trees

- **Tree** — a recursive, acyclic, connected structure with a root node and zero or more children per node.
- **Binary tree** — each node has at most two children (left and right).
- **Binary search tree (BST)** — a binary tree where all left descendants are less than or equal to the node, and all right descendants are greater; supports O(log N) search, insert, and delete when balanced.
- **Balanced trees** — self-balancing variants (Red-Black Trees, AVL Trees) guarantee O(log N) operations by maintaining height constraints.
- **Complete binary tree** — every level is fully filled except possibly the last, which is filled left to right.
- **Full binary tree** — every node has either zero or two children.
- **Perfect binary tree** — both full and complete; has exactly 2^k - 1 nodes for k levels.
- **In-order traversal** — visit left subtree, current node, right subtree; produces sorted output for a BST.
- **Pre-order traversal** — visit current node before children; useful for serialization and tree copying.
- **Post-order traversal** — visit children before current node; useful for deletion and expression evaluation.

## 9. Heaps

- **Binary heap** — a complete binary tree where each parent satisfies the heap property relative to its children.
- **Min-heap** — parent is less than or equal to both children; the root is the minimum element.
- **Max-heap** — parent is greater than or equal to both children; the root is the maximum element.
- **Insert** — add at the next available position (to maintain completeness), then bubble up to restore the heap property; O(log N).
- **Extract min/max** — remove the root, replace with the last element, then bubble down; O(log N).
- **Array representation** — for node at index i: left child at 2i+1, right child at 2i+2, parent at (i-1)/2.

## 10. Tries

- **Trie (prefix tree)** — an n-ary tree where each node represents a character; paths from root to terminal nodes spell out stored words or prefixes.
- **O(K) lookup** — finding a word or prefix of length K takes O(K) time, independent of the total number of stored words.
- **Prefix-based operations** — tries excel at autocomplete, spell checking, and prefix matching where hash tables would need to iterate all keys.
- **Space tradeoff** — tries can use more memory than hash tables due to pointer overhead per character, but null-link compression and other tricks help.

## 11. Graphs

- **Graph** — a set of nodes (vertices) connected by edges; more general than trees (can have cycles, disconnected components, no root).
- **Directed vs. undirected** — edges can be one-way (directed) or bidirectional (undirected).
- **Connected vs. disconnected** — a connected graph has a path between every pair of nodes; a disconnected graph has isolated components.
- **Cyclic vs. acyclic** — a directed acyclic graph (DAG) has no cycles; trees are connected acyclic undirected graphs.
- **Adjacency list** — each node stores a list of its neighbors; the most common representation; space-efficient for sparse graphs.
- **Adjacency matrix** — an NxN boolean matrix where matrix[i][j] indicates an edge from node i to node j; efficient for dense graphs and edge-existence queries.

## 12. Graph Search

- **Depth-first search (DFS)** — explore as deep as possible along each branch before backtracking; uses recursion or an explicit stack; must track visited nodes to avoid cycles.
- **Breadth-first search (BFS)** — explore all neighbors at the current depth before moving deeper; uses a queue; finds shortest path in unweighted graphs.
- **Bidirectional search** — run two simultaneous BFS searches from source and destination; they meet in the middle; reduces O(k^d) to O(k^(d/2)).
- **Topological sort** — linear ordering of DAG vertices such that every edge goes from earlier to later; used for dependency resolution and build ordering.
- **Dijkstra's algorithm** — finds shortest paths in weighted graphs with non-negative edge weights; uses a priority queue.

## 13. Bit Manipulation

- **Two's complement** — standard representation for signed integers; the most significant bit represents the sign; negation is bitwise NOT plus one.
- **Bitwise operators** — AND, OR, XOR, NOT, left shift, right shift; foundational for low-level manipulation and optimization.
- **Arithmetic vs. logical right shift** — arithmetic shift (>>) preserves the sign bit; logical shift (>>>) fills with zeros.
- **Bit masks** — using shifts and boolean operators to get, set, clear, or update individual bits at specific positions.
- **XOR properties** — x ^ 0 = x, x ^ x = 0, x ^ ~0 = ~x; useful for toggling bits, finding unique elements, and computing Hamming distance.
- **Power-of-two check** — n & (n - 1) == 0 tests whether n is a power of two (exactly one bit set).

## 14. Recursion

- **Recursive decomposition** — breaking a problem into smaller instances of the same problem until reaching a base case.
- **Base case** — the termination condition that returns a result without further recursion.
- **Bottom-up approach** — solve the simplest subproblem first, then build up to the full problem.
- **Top-down approach** — start with the full problem, divide into subproblems, and solve those recursively.
- **Half-and-half approach** — split the data in two and process each half; merge sort and binary search follow this pattern.
- **Stack space** — each recursive call adds a frame to the call stack; deep recursion can overflow the stack; iterative alternatives avoid this.
- **Recursion tree** — visualizing the call structure to count work and derive the runtime.

## 15. Dynamic Programming

- **Dynamic programming** — recursion plus caching of overlapping subproblems, or an equivalent bottom-up iterative computation.
- **Memoization (top-down DP)** — cache the results of recursive calls so each unique subproblem is solved only once; often transforms exponential time to polynomial.
- **Tabulation (bottom-up DP)** — fill a table iteratively from base cases forward; avoids recursion overhead and stack depth limits.
- **Space optimization** — when the recurrence only depends on a fixed number of prior values, reduce the table to a few variables; Fibonacci from O(N) space to O(1).
- **Fibonacci as case study** — naive O(2^N) -> memoized O(N) -> bottom-up O(N) -> O(1) space; the canonical example of each DP technique.
- **Overlapping subproblems** — the key property that makes DP applicable: the same subproblem is computed multiple times in the naive recursive approach.
- **Optimal substructure** — the optimal solution to the full problem can be constructed from optimal solutions to its subproblems.

## 16. Sorting Algorithms

- **Bubble sort** — O(N^2) time, O(1) space; repeatedly swap adjacent elements until sorted; simple but impractical for large inputs.
- **Selection sort** — O(N^2) time, O(1) space; find the minimum unsorted element and place it at the front; always makes the same number of comparisons.
- **Merge sort** — O(N log N) time, O(N) space; divide the array in half, sort each half recursively, merge the sorted halves.
- **Quick sort** — O(N log N) average, O(N^2) worst case; pick a pivot, partition elements around it, recurse on each side; O(log N) space from recursion.
- **Radix sort** — O(kN) time where k is the number of digits; sorts by individual digit position; non-comparison-based.
- **Bucket sort** — O(N) time when keys have a small range; distribute elements into buckets, then concatenate.
- **Stability** — a stable sort preserves the relative order of elements with equal keys; merge sort is stable, quick sort is typically not.
- **Comparison-based lower bound** — no comparison-based sort can do better than O(N log N) in the worst case.

## 17. Searching Algorithms

- **Binary search** — O(log N) search in a sorted array by repeatedly halving the search range; boundary arithmetic (plus/minus ones) is the main source of bugs.
- **Linear search** — O(N) scan through all elements; the fallback when data is unsorted or the structure does not support faster access.
- **Search in modified structures** — rotated sorted arrays, sparse arrays, and unknown-length arrays require adapted binary search variants.
- **Matrix search** — in a matrix sorted by both row and column, start from a corner and eliminate a row or column each step; O(N + M) for an NxM matrix.

## 18. Problem-Solving Patterns

- **Frequency counting** — use a hash map or array to count occurrences; solves anagram, duplicate, and permutation problems.
- **Sliding window** — maintain a window over a sequence and slide it to avoid recomputation; useful for substring and subarray problems.
- **Divide and conquer** — split the problem, solve each part independently, combine results; merge sort and binary search are canonical examples.
- **Greedy** — make the locally optimal choice at each step; works when local optima lead to global optima.
- **Backtracking** — build a solution incrementally and abandon partial solutions that violate constraints; the algorithmic pattern behind N-queens, permutations, and parentheses generation.
- **Flood fill** — BFS or DFS from a starting cell, visiting all connected cells that meet a condition; the pattern behind paint-fill and island-counting problems.
- **Bit vector for space optimization** — use individual bits as boolean flags to compress a large boolean array into compact storage; enables problems like finding missing or duplicate integers in constrained memory.

---

## How to use this list

This is a self-check, not a memorization contest. Pick any concept and ask:

1. Can I explain what it is in plain language?
2. Can I analyze the time and space complexity of an algorithm that uses it?
3. Can I implement it from scratch and use it to solve an unfamiliar problem?

If any answer is "no," that concept is a study target.
