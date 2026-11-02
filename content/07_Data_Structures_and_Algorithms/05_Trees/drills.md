# Trees — Drills

Original mini-drills for binary tree and BST skills. Each card is one exercise: read the prompt and snippet, commit to an answer, then check it. Each Answer has a short Python solution that runs on its own. No copyrighted book text.

## Trace it: three depth-first orders

Write down the pre-order, in-order, and post-order sequences for this tree before running anything.

```text
        F
       / \
      B   G
     / \    \
    A   D    I
       / \   /
      C   E H
```

**Answer:** Pre-order (node, left, right) is `F B A D C E G I H`. In-order (left, node, right) is `A B C D E F G H I`, which is alphabetical because the letters form a BST. Post-order (left, right, node) is `A C E D B H I G F`; the root always comes last.

```python
class T:
    def __init__(self, v, l=None, r=None):
        self.v, self.l, self.r = v, l, r

def pre(n):  return [n.v] + pre(n.l) + pre(n.r) if n else []
def ino(n):  return ino(n.l) + [n.v] + ino(n.r) if n else []
def post(n): return post(n.l) + post(n.r) + [n.v] if n else []

root = T("F", T("B", T("A"), T("D", T("C"), T("E"))), T("G", None, T("I", T("H"))))
print(" ".join(pre(root)))   # F B A D C E G I H
print(" ".join(ino(root)))   # A B C D E F G H I
print(" ".join(post(root)))  # A C E D B H I G F
```

## Sorted input, sorry tree

You insert the keys 1 through 7, in that order, into a plain (non-balancing) BST. What is the height, and what does a search for 7 cost? Then insert the same keys in the order 4, 2, 6, 1, 3, 5, 7. What changes?

**Answer:** Sorted inserts always go right, so the tree is a chain: height 6 and a search for 7 visits all 7 nodes, O(N). The second order puts the median first at every level, giving a perfect tree of height 2 where any search visits at most 3 nodes, O(log N). Same keys, same BST rules; only insertion order changed. This is the reason self-balancing trees (or shuffled input) exist.

```python
class T:
    def __init__(self, v):
        self.v, self.l, self.r = v, None, None

def insert(n, v):
    if n is None:
        return T(v)
    if v < n.v:
        n.l = insert(n.l, v)
    else:
        n.r = insert(n.r, v)
    return n

def height(n):
    return 1 + max(height(n.l), height(n.r)) if n else -1

def visits(n, v):
    steps = 0
    while n:
        steps += 1
        if v == n.v:
            return steps
        n = n.l if v < n.v else n.r
    return steps

for order in ([1, 2, 3, 4, 5, 6, 7], [4, 2, 6, 1, 3, 5, 7]):
    root = None
    for v in order:
        root = insert(root, v)
    print(height(root), visits(root, 7))
# prints 6 7, then 2 3
```

## Bug hunt: the insert that loses nodes

After inserting 5, 3, and 8, the tree only contains 5. Find the bug.

```python
def insert(node, val):
    if node is None:
        return TreeNode(val)
    if val < node.val:
        insert(node.left, val)
    else:
        insert(node.right, val)
    return node
```

**Answer:** The recursive call returns the new subtree, but the result is thrown away. When `node.left` is `None`, the call builds a new node and returns it, and nothing links it to the parent. Assign the result back: `node.left = insert(node.left, val)` (and the same on the right). Recursive tree builders and editors almost always follow "return the new subtree root, parent reassigns it".

```python
class TreeNode:
    def __init__(self, val):
        self.val, self.left, self.right = val, None, None

def insert(node, val):
    if node is None:
        return TreeNode(val)
    if val < node.val:
        node.left = insert(node.left, val)    # reassign the child link
    else:
        node.right = insert(node.right, val)
    return node

def inorder(n):
    return inorder(n.left) + [n.val] + inorder(n.right) if n else []

root = None
for v in [5, 3, 8]:
    root = insert(root, v)
print(inorder(root))  # [3, 5, 8]
```

## Height off by one

Two teammates write `height`. One returns `0` for `None`, the other returns `-1`. What does each return for a single node, and for a root with one child? Which one matches "number of edges on the longest path"?

**Answer:** With `None -> 0` you get 1 for a single node and 2 for root+child: that counts **nodes** on the longest path (some texts call it "max depth"). With `None -> -1` you get 0 and 1: that counts **edges**, the definition used on the Concepts tab (a leaf has height 0). Both are fine; just state your convention out loud in an interview, because off-by-one height bugs break balance checks and level counts.

```python
class T:
    def __init__(self, l=None, r=None):
        self.l, self.r = l, r

def height_nodes(n):
    return 0 if n is None else 1 + max(height_nodes(n.l), height_nodes(n.r))

def height_edges(n):
    return -1 if n is None else 1 + max(height_edges(n.l), height_edges(n.r))

single, pair = T(), T(T())
print(height_nodes(single), height_nodes(pair))  # 1 2
print(height_edges(single), height_edges(pair))  # 0 1
```

## Which traversal rebuilds the same BST?

You dump a BST's values into a list, then re-insert them one by one into an empty BST. Which dump order gives back a tree with the identical shape: in-order, pre-order, or level-order?

**Answer:** Pre-order and level-order both work, because each node is inserted before any of its descendants, so it lands in its original position and its descendants follow it down. In-order gives sorted values, and sorted inserts build a right-leaning chain, so the shape is lost (height becomes N - 1). This is why pre-order is the usual choice for saving a BST.

```python
from collections import deque

class T:
    def __init__(self, v):
        self.v, self.l, self.r = v, None, None

def insert(n, v):
    if n is None:
        return T(v)
    if v < n.v: n.l = insert(n.l, v)
    else:       n.r = insert(n.r, v)
    return n

def build(vals):
    root = None
    for v in vals:
        root = insert(root, v)
    return root

def pre(n): return [n.v] + pre(n.l) + pre(n.r) if n else []
def ino(n): return ino(n.l) + [n.v] + ino(n.r) if n else []
def level(n):
    out, q = [], deque([n])
    while q:
        x = q.popleft(); out.append(x.v)
        q.extend(c for c in (x.l, x.r) if c)
    return out
def shape(n): return (n.v, shape(n.l), shape(n.r)) if n else None

orig = build([50, 30, 70, 20, 40, 60, 80])
for name, dump in (("in", ino), ("pre", pre), ("level", level)):
    print(name, shape(build(dump(orig))) == shape(orig))
# in False, pre True, level True (one per line)
```

## Iterative pre-order: why push right first?

This explicit-stack pre-order prints the wrong order. What does it print for the tree `1 (left 2, right 3)`, and what is the fix?

```python
def preorder(root):
    out, stack = [], [root]
    while stack:
        node = stack.pop()
        out.append(node.val)
        if node.left:
            stack.append(node.left)
        if node.right:
            stack.append(node.right)
    return out
```

**Answer:** It prints `[1, 3, 2]`. A stack is LIFO, so whatever you push last is visited next; pushing left then right visits the right child first. Push **right first, then left**, so the left child is on top. (The buggy version is a valid "node, right, left" traversal, which reversed gives post-order, a useful trick to remember.)

```python
class T:
    def __init__(self, val, left=None, right=None):
        self.val, self.left, self.right = val, left, right

def preorder(root):
    out, stack = [], [root] if root else []
    while stack:
        node = stack.pop()
        out.append(node.val)
        if node.right:
            stack.append(node.right)   # pushed first, popped later
        if node.left:
            stack.append(node.left)
    return out

print(preorder(T(1, T(2), T(3))))                       # [1, 2, 3]
print(preorder(T(1, T(2, T(4), T(5)), T(3))))           # [1, 2, 4, 5, 3]
```

## Deep tree, crashing recursion

A config loader builds a tree from a nested file. One customer file nests 10,000 levels deep and `height(root)` raises `RecursionError`. Rewrite `height` so it works at any depth.

**Answer:** CPython keeps a recursion limit of about 1000 frames, and a skewed tree needs one frame per level. Replace recursion with level-order BFS: count how many levels you process. It is O(N) time and O(width) extra space, and it never touches the call stack. (An explicit stack of `(node, depth)` pairs works too.) Raising the limit with `sys.setrecursionlimit` is a band-aid that can crash the interpreter.

```python
from collections import deque

class T:
    def __init__(self, child=None):
        self.left, self.right = child, None

def height_bfs(root):
    if root is None:
        return -1
    levels, q = 0, deque([root])
    while q:
        for _ in range(len(q)):
            n = q.popleft()
            q.extend(c for c in (n.left, n.right) if c)
        levels += 1
    return levels - 1   # edges, not nodes

deep = None
for _ in range(10_000):
    deep = T(deep)
print(height_bfs(deep))  # 9999
```

## Diameter: longest path between any two nodes

The **diameter** of a binary tree is the number of edges on the longest path between any two nodes; the path does not have to pass through the root. Compute it in one O(N) pass.

**Answer:** Work bottom-up. Each call returns the height of its subtree, and on the way it updates a running best with `left_height + right_height + 2` (the longest path that bends at this node). Computing heights separately from every node would be O(N²) on a skewed tree; returning the height while you compute the answer keeps it O(N). In the example the longest path, 4 to 6, never touches the root.

```python
class T:
    def __init__(self, v, l=None, r=None):
        self.v, self.l, self.r = v, l, r

def diameter(root):
    best = 0
    def h(n):
        nonlocal best
        if n is None:
            return -1
        lh, rh = h(n.l), h(n.r)
        best = max(best, lh + rh + 2)   # path that bends at n
        return 1 + max(lh, rh)
    h(root)
    return best

#        1
#       /
#      2
#     / \
#    3   5
#   /     \
#  4       6
root = T(1, T(2, T(3, T(4)), T(5, None, T(6))))
print(diameter(root))  # 4
```

## Visible nodes: carry the maximum down

A node is **visible** if no node on the path from the root down to it (including the root) has a larger value. Count visible nodes in the tree below.

```text
        3
       / \
      1   4
     /   / \
    3   1   5
```

**Answer:** This needs information about *ancestors*, so pass it top-down: carry the largest value seen so far as an argument. A node is visible if its value is at least that maximum. Here 3 (root), the left-left 3, 4, and 5 are visible; the two 1s are not. Answer: 4. O(N) time, O(h) stack.

```python
class T:
    def __init__(self, v, l=None, r=None):
        self.v, self.l, self.r = v, l, r

def visible(n, best=float("-inf")):
    if n is None:
        return 0
    here = 1 if n.v >= best else 0
    best = max(best, n.v)
    return here + visible(n.l, best) + visible(n.r, best)

root = T(3, T(1, T(3)), T(4, T(1), T(5)))
print(visible(root))  # 4
```

## Price ceiling with a BST

A shop stores price points in a BST: 10, 25, 40, 55, 70, 85 (inserted in the order 55, 25, 85, 10, 40, 70). A customer says "the cheapest option at or above 42". Without a full traversal, what do you return, and which nodes do you visit?

**Answer:** Walk down once, remembering the best candidate. At 55, 55 >= 42 so it is a candidate; go left. At 25, too small; go right. At 40, too small; go right; the slot is empty. The answer is the last candidate, 55, after visiting only 55, 25, 40. That is O(h), not O(N). The same walk with the comparisons flipped gives the floor.

```python
class T:
    def __init__(self, v):
        self.v, self.l, self.r = v, None, None

def insert(n, v):
    if n is None:
        return T(v)
    if v < n.v: n.l = insert(n.l, v)
    else:       n.r = insert(n.r, v)
    return n

def ceiling(n, x):
    best, path = None, []
    while n:
        path.append(n.v)
        if n.v == x:
            return x, path
        if n.v > x:
            best, n = n.v, n.l
        else:
            n = n.r
    return best, path

root = None
for p in [55, 25, 85, 10, 40, 70]:
    root = insert(root, p)
print(ceiling(root, 42))  # (55, [55, 25, 40])
print(ceiling(root, 90))  # (None, [55, 85])
```

## Range sum with pruning

Sum every key between `lo` and `hi` (inclusive) in a BST. A full traversal works but visits every node. Use the BST order to skip whole subtrees, and count how many nodes you visit.

**Answer:** At each node: if its key is below `lo`, nothing in its left subtree can be in range, so only go right; if it is above `hi`, only go left; otherwise add it and go both ways. On a balanced tree this costs O(log N + k) where k is the number of keys in range, instead of O(N). In the example only 7 of 15 nodes are visited.

```python
class T:
    def __init__(self, v):
        self.v, self.l, self.r = v, None, None

def build(lo, hi):            # balanced BST over lo..hi
    if lo > hi:
        return None
    mid = (lo + hi) // 2
    n = T(mid); n.l = build(lo, mid - 1); n.r = build(mid + 1, hi)
    return n

def range_sum(n, lo, hi, seen):
    if n is None:
        return 0
    seen.append(n.v)
    if n.v < lo:
        return range_sum(n.r, lo, hi, seen)
    if n.v > hi:
        return range_sum(n.l, lo, hi, seen)
    return n.v + range_sum(n.l, lo, hi, seen) + range_sum(n.r, lo, hi, seen)

root = build(1, 15)
seen = []
print(range_sum(root, 10, 12, seen), len(seen))  # 33 7
```

## k-th smallest without sorting everything

Return the k-th smallest key (1-based) in a BST. The naive answer builds the full in-order list. Write a version that stops as soon as it has the answer.

**Answer:** In-order traversal yields keys in sorted order, so use a generator (or an iterative in-order loop) and stop after k items. That costs O(h + k) instead of O(N) time, and you never materialise the full list. If the tree is queried often, store each node's subtree size so you can jump directly in O(h).

```python
from itertools import islice

class T:
    def __init__(self, v, l=None, r=None):
        self.v, self.l, self.r = v, l, r

def inorder(n, counter):
    if n:
        yield from inorder(n.l, counter)
        counter[0] += 1           # count nodes actually visited
        yield n.v
        yield from inorder(n.r, counter)

def kth_smallest(root, k):
    counter = [0]
    value = next(islice(inorder(root, counter), k - 1, None))
    return value, counter[0]

root = T(50, T(30, T(20), T(40)), T(70, T(60), T(80)))
print(kth_smallest(root, 3))  # (40, 3)
```

## Why the null markers matter

A teammate serializes trees as a plain pre-order list of values and says that is enough to rebuild any binary tree. Find two different trees with the same plain pre-order, then show a format that fixes it.

**Answer:** `1` with left child `2`, and `1` with right child `2`, both give `[1, 2]`, so the list alone is ambiguous. Writing a marker for every empty child makes the encoding unique (`1,2,#,#,#` vs `1,#,2,#,#`), and a recursive reader can rebuild the exact shape. (A BST is the exception: there the order rule alone pins down the shape, as the "Which traversal rebuilds the same BST?" card shows.)

```python
class T:
    def __init__(self, v, l=None, r=None):
        self.v, self.l, self.r = v, l, r

def plain(n):
    return [n.v] + plain(n.l) + plain(n.r) if n else []

def ser(n):
    return "#" if n is None else f"{n.v},{ser(n.l)},{ser(n.r)}"

def de(s):
    it = iter(s.split(","))
    def build():
        t = next(it)
        if t == "#":
            return None
        return T(int(t), build(), build())
    return build()

a, b = T(1, T(2)), T(1, None, T(2))
print(plain(a) == plain(b))   # True
print(ser(a), ser(b))         # 1,2,#,#,# 1,#,2,#,#
print(ser(de(ser(b))) == ser(b))  # True
```

## Rotate it by hand

Starting from this right-leaning chain, perform one left rotation at the root. Draw the result, give its height, and confirm the in-order sequence did not change.

```text
    10
      \
       20
         \
          30
```

**Answer:** The right child 20 moves up to become the root, 10 becomes its left child, and 20's old left subtree (empty here) becomes 10's right subtree. The result is `20` with children `10` and `30`; height drops from 2 to 1, and in-order stays `[10, 20, 30]`. Rotations change shape, never order, which is why balancing trees can use them freely.

```python
class T:
    def __init__(self, v, l=None, r=None):
        self.v, self.l, self.r = v, l, r

def rotate_left(x):
    y = x.r
    x.r = y.l
    y.l = x
    return y

def ino(n): return ino(n.l) + [n.v] + ino(n.r) if n else []
def h(n):   return 1 + max(h(n.l), h(n.r)) if n else -1

root = T(10, None, T(20, None, T(30)))
print(ino(root), h(root))   # [10, 20, 30] 2
root = rotate_left(root)
print(root.v, root.l.v, root.r.v, ino(root), h(root))  # 20 10 30 [10, 20, 30] 1
```

## Folder sizes: post-order on an N-ary tree

A disk-usage tool must print every folder's total size (its own files plus everything below it). Each node has a `size` (0 for folders) and a list of `children`. Which traversal fits, and what is the cost?

**Answer:** Post-order: a folder's total is only known after all its children report their totals, so compute children first and then add your own size. One pass gives every folder's total in O(N) time, because each node is summed once. Doing a separate full walk from every folder would be O(N²) on a deep tree.

```python
class Node:
    def __init__(self, name, size=0, children=()):
        self.name, self.size, self.children = name, size, list(children)

def folder_totals(node, out):
    total = node.size + sum(folder_totals(c, out) for c in node.children)
    if node.children:
        out[node.name] = total
    return total

root = Node("/", children=[
    Node("src", children=[Node("main.py", 12), Node("util", children=[Node("io.py", 5)])]),
    Node("README", 3),
])
totals = {}
folder_totals(root, totals)
print(totals)  # {'util': 5, 'src': 17, '/': 20}
```

## Evaluate an expression tree

Leaves hold numbers and internal nodes hold operators. Evaluate the tree for `(7 - 2) * (3 + 1)` and print it back in fully parenthesised infix. Which traversals do you use?

**Answer:** Evaluation is post-order: compute both operand subtrees, then apply the operator at the parent. Printing infix is in-order with parentheses around each internal node. Keep the operand order (left before right) or `7 - 2` turns into `2 - 7`. The value is 20.

```python
import operator

OPS = {"+": operator.add, "-": operator.sub, "*": operator.mul, "/": operator.truediv}

class T:
    def __init__(self, v, l=None, r=None):
        self.v, self.l, self.r = v, l, r

def evaluate(n):
    if n.l is None and n.r is None:
        return n.v
    return OPS[n.v](evaluate(n.l), evaluate(n.r))   # left operand first

def infix(n):
    if n.l is None and n.r is None:
        return str(n.v)
    return f"({infix(n.l)} {n.v} {infix(n.r)})"

expr = T("*", T("-", T(7), T(2)), T("+", T(3), T(1)))
print(evaluate(expr))  # 20
print(infix(expr))     # ((7 - 2) * (3 + 1))
```
