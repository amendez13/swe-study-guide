# Data Structures and Algorithms Source Outlines

Primary source material extracted from *Cracking the Coding Interview, 6th Edition* by Gayle Laakmann McDowell. The book covers data structures, algorithms, and problem-solving patterns through a combination of conceptual chapters and interview problem sets.

---

## 1. Big O (Chapter VI)

**Scope:** Asymptotic analysis, runtime and space complexity, simplification rules, common runtime patterns.

### Topics

- Big O, Big Theta, Big Omega (upper bound, tight bound, lower bound)
- Best case, worst case, expected case (illustrated via QuickSort)
- Space complexity (stack frames, allocated structures)
- Drop the constants
- Drop non-dominant terms
- Multi-part algorithms: add vs. multiply (sequential vs. nested)
- Amortized time (ArrayList doubling example)
- Log N runtimes (halving the problem space, binary search)
- Recursive runtimes (branches^depth pattern)
- Memoization (Fibonacci from O(2^N) to O(N))
- Common runtimes: O(1), O(log N), O(N), O(N log N), O(N^2), O(2^N), O(N!), O(sqrt(N))
- Practice examples: product via addition, recursive power, mod, integer division, binary-search sqrt, linear sqrt, unbalanced BST search, unsorted binary tree search, repeated array copy, digit sum, sorted string generation, intersection via sort+binary search

---

## 2. Arrays and Strings (Chapter 1)

**Scope:** Hash tables, dynamic arrays, string building, in-place array/string manipulation.

### Topics

- Hash tables: array of linked lists + hash function, collision handling, O(1) average / O(N) worst case
- Balanced BST as map alternative: O(log N) lookup, ordered key iteration
- ArrayList / resizable array: doubling capacity, amortized O(1) insertion, O(1) random access
- StringBuilder: resizable buffer to avoid quadratic string concatenation
- Character set and encoding assumptions
- Two-pointer technique for arrays
- Frequency maps and boolean sets
- Matrix coordinate transforms

### Practice Problems

- 1.1 Is Unique (unique characters, variant without extra data structures)
- 1.2 Check Permutation
- 1.3 URLify (in-place space replacement)
- 1.4 Palindrome Permutation
- 1.5 One Away (edit distance = 1)
- 1.6 String Compression (run-length encoding)
- 1.7 Rotate Matrix (90-degree in-place NxN rotation)
- 1.8 Zero Matrix (zero out row and column)
- 1.9 String Rotation (using single isSubstring call)

---

## 3. Linked Lists (Chapter 2)

**Scope:** Singly and doubly linked lists, pointer manipulation, runner technique, recursion on lists.

### Topics

- Singly linked list: node with data + next pointer, O(1) insert/remove at head, O(k) access
- Doubly linked list: data + next + prev pointers
- Creating a linked list: head-reference approach vs. wrapper class
- Deleting a node: find previous, update pointers, handle head/tail
- Runner (two-pointer) technique: fast/slow pointers for midpoint, interleaving, cycle detection
- Recursive approaches on lists: natural recursion with O(n) stack space
- Converting recursive list algorithms to iterative

### Practice Problems

- 2.1 Remove Dups (with/without buffer)
- 2.2 Return Kth to Last
- 2.3 Delete Middle Node
- 2.4 Partition (around value x)
- 2.5 Sum Lists (reverse and forward digit order)
- 2.6 Palindrome check
- 2.7 Intersection (by reference)
- 2.8 Loop Detection (find loop start)

---

## 4. Stacks and Queues (Chapter 3)

**Scope:** LIFO and FIFO data structures, implementation, and applications.

### Topics

- Stack (LIFO): push, pop, peek, isEmpty; O(1) add/remove; linked-list implementation
- Queue (FIFO): add, remove, peek, isEmpty; linked-list implementation with first/last pointers
- Stack for recursive backtracking
- Converting recursion to iteration using an explicit stack
- BFS using a queue
- Queue for cache implementation

### Practice Problems

- 3.1 Three in One (three stacks in one array)
- 3.2 Stack Min (O(1) min tracking)
- 3.3 Stack of Plates (SetOfStacks with capacity threshold + popAt)
- 3.4 Queue via Stacks (two-stack queue)
- 3.5 Sort Stack (sort using one temporary stack)
- 3.6 Animal Shelter (FIFO with type-specific dequeue)

---

## 5. Trees and Graphs (Chapter 4)

**Scope:** Tree and graph terminology, traversals, heaps, tries, graph representation/search.

### Topics

- Trees: recursive node-based structure (root, children, no cycles)
- Binary tree: each node has at most 2 children
- Binary search tree (BST): left descendants <= node < right descendants
- Balanced trees: O(log N) insert/find; Red-Black Trees, AVL Trees
- Complete binary tree: every level full except last (filled left to right)
- Full binary tree: every node has 0 or 2 children
- Perfect binary tree: full + complete; exactly 2^k - 1 nodes
- Binary heap (min-heap / max-heap): complete binary tree, parent <= children, O(log N) insert and extract
- Trie (prefix tree): n-ary tree storing characters, O(K) prefix lookup
- Graph: nodes + edges; directed vs. undirected; connected vs. disconnected; cyclic vs. acyclic
- Adjacency list (most common representation)
- Adjacency matrix (NxN boolean)
- In-order, pre-order, post-order traversal (recursive)
- Depth-first search (DFS): recursive, visited flag
- Breadth-first search (BFS): iterative with queue, shortest path
- Bidirectional search: two simultaneous BFS, O(k^(d/2)) vs. O(k^d)
- Topological sort (referenced)
- Dijkstra's algorithm (referenced)

### Practice Problems

- 4.1 Route Between Nodes
- 4.2 Minimal Tree
- 4.3 List of Depths
- 4.4 Check Balanced
- 4.5 Validate BST
- 4.6 Successor (in-order)
- 4.7 Build Order (topological sort)
- 4.8 First Common Ancestor (LCA)
- 4.9 BST Sequences
- 4.10 Check Subtree
- 4.11 Random Node
- 4.12 Paths with Sum

---

## 6. Bit Manipulation (Chapter 5)

**Scope:** Bit operations, two's complement, shifts, bit masks.

### Topics

- Two's complement representation for negative numbers
- Arithmetic right shift (>>, preserves sign) vs. logical right shift (>>>, fills with 0)
- Bit facts: XOR, AND, OR identity/complement rules
- getBit: isolate bit i with mask (1 << i)
- setBit: OR with (1 << i)
- clearBit: AND with negated mask ~(1 << i)
- clearBitsMSBthroughI: mask = (1 << i) - 1
- clearBitsIthrough0: mask = (-1 << (i+1))
- updateBit: clear then OR with (value << i)

### Practice Problems

- 5.1 Insertion (bit range replacement)
- 5.2 Binary to String (double to binary)
- 5.3 Flip Bit to Win (longest 1s sequence)
- 5.4 Next Number (same number of 1-bits)
- 5.5 Debugger (n & (n-1) == 0)
- 5.6 Conversion (bit diff count via XOR)
- 5.7 Pairwise Swap (odd/even bits)
- 5.8 Draw Line (byte-array screen)

---

## 7. Recursion and Dynamic Programming (Chapter 8)

**Scope:** Recursive problem-solving approaches, memoization, dynamic programming.

### Topics

- Bottom-up approach: solve base case, build up incrementally
- Top-down approach: divide case N into subproblems
- Half-and-half approach: split data in two (binary search, merge sort)
- Memoization (top-down DP): cache recursive results
- Bottom-up DP: iterative, fill table from base cases forward
- Space optimization: reduce memo table to constant variables
- Fibonacci case study: naive O(2^N) -> memoized O(N) -> bottom-up O(N) -> O(1) space
- Recursion tree analysis for runtime estimation
- Recursive vs. iterative tradeoffs (stack depth = O(N) memory)

### Practice Problems

- 8.1 Triple Step (staircase counting)
- 8.2 Robot in a Grid (pathfinding with obstacles)
- 8.3 Magic Index (A[i]=i search)
- 8.4 Power Set (all subsets)
- 8.5 Recursive Multiply (without * operator)
- 8.6 Towers of Hanoi
- 8.7 Permutations without Dups
- 8.8 Permutations with Dups
- 8.9 Parens (valid parentheses generation)
- 8.10 Paint Fill (flood fill)
- 8.11 Coins (change-making)
- 8.12 Eight Queens
- 8.13 Stack of Boxes (LIS-style)
- 8.14 Boolean Evaluation (expression parenthesization counting)

---

## 8. Sorting and Searching (Chapter 10)

**Scope:** Sorting algorithms, searching algorithms, and hybrid problem patterns.

### Topics

- Bubble sort: O(N^2) time, O(1) space; repeated adjacent swaps
- Selection sort: O(N^2) time, O(1) space; find min, place at front
- Merge sort: O(N log N) time, O(N) space; divide, sort halves, merge
- Quick sort: O(N log N) average, O(N^2) worst; random pivot, partition; O(log N) space
- Radix sort: O(kN) time; digit-by-digit grouping; non-comparison-based
- Bucket sort: O(N) with small-range keys
- Binary search: O(log N); boundary arithmetic details
- Beyond binary search: binary trees, hash tables

### Practice Problems

- 10.1 Sorted Merge (merge two sorted arrays in place)
- 10.2 Group Anagrams
- 10.3 Search in Rotated Array
- 10.4 Sorted Search No Size (unknown-length array)
- 10.5 Sparse Search (sorted strings with empties)
- 10.6 Sort Big File (external sort, 20GB)
- 10.7 Missing Int (4 billion integers, bit vector)
- 10.8 Find Duplicates (32K range, 4KB memory, bit vector)
- 10.9 Sorted Matrix Search (row+col sorted)
- 10.10 Rank from Stream (BST-based rank tracking)
- 10.11 Peaks and Valleys (alternating arrangement)

---

## Summary

| Chapter | CTCI Section | Focus |
|---------|-------------|-------|
| Big O | VI | Asymptotic analysis, complexity classes, simplification rules |
| Arrays and Strings | 1 | Hash tables, dynamic arrays, string building, in-place manipulation |
| Linked Lists | 2 | Pointer manipulation, runner technique, recursive list processing |
| Stacks and Queues | 3 | LIFO/FIFO structures, stack-based recursion, queue-based BFS |
| Trees and Graphs | 4 | Tree types, BST, heaps, tries, graphs, DFS, BFS, bidirectional search |
| Bit Manipulation | 5 | Two's complement, bitwise operations, bit masks |
| Recursion and DP | 8 | Recursive decomposition, memoization, bottom-up DP, space optimization |
| Sorting and Searching | 10 | Comparison and non-comparison sorts, binary search, hybrid problems |
