# Trees

Tree problems hand over a root and ask for something about the whole structure. The mechanics, from the node definition to the four traversals, are on the Data Structures [Trees](#07_Data_Structures_and_Algorithms/05_Trees) topic. This topic is the problem set: what each recursive call returns, which traversal matches the question, how breadth-first search splits levels, and a run of standard problems from inverting a tree to the maximum path sum. The two decisions are the contract of the recursive call, returned up or carried down, and the order of visits, depth-first or level by level.

## Key Points

- **Binary tree vocabulary** — root, leaf, subtree, path, depth from the root, height from the leaves. Height runs from about log₂ n to n - 1 and sets the recursion depth. Say whether you count edges or nodes.
- **Return up or carry down** — bottom-up calls return a subtree summary (postorder), top-down calls receive state as arguments (preorder). A sentinel such as -1 folds failure into the return value. An outer variable records answers that are not returned.
- **Choose a traversal** — preorder hands state to children, inorder reads a BST in sorted order, postorder needs children first, BFS answers by level. DFS memory is O(h), BFS memory is O(w).
- **Level-order with the level-size loop** — snapshot `len(queue)` and pop that many nodes per pass. Minimum depth stops at the first leaf.
- **Recursion to an explicit stack** — push right before left, put the call's arguments in the stack entry. CPython stops at 1000 frames.
- **Invert a tree and check symmetry** — swap both children in one tuple assignment. Symmetry compares crossed pairs and handles the two null cases first.
- **Balanced tree check** — one postorder pass returns the height in nodes or -1. The top-down height calls cost O(n²) on a chain.
- **Rightmost node of each level** — the last node of each BFS level, or the first node per depth in a right-first DFS. A left-subtree node can be visible.
- **Widest level** — heap slots `2i + 1` and `2i + 2`, width `last - first + 1`. Subtract the first slot per level to keep numbers small.
- **Validate a BST** — carry an open range `(low, high)` down, or check that inorder is strictly increasing. Parent-child checks miss deep violations.
- **K-th smallest in a BST** — iterative inorder that stops at the k-th pop, O(h + k). Subtree sizes give O(h) per query.
- **Lowest common ancestor** — postorder that returns p or q when found. The first node with reports from both sides is the answer.
- **Rebuild a tree from traversals** — preorder gives roots, inorder splits them, a value-to-index map keeps it O(n). Preorder with null markers alone is a full serialization.
- **Maximum path sum** — return the one-sided gain, record the two-sided peak, clamp negative gains at 0, and start the best at negative infinity.
- **Vertical columns** — BFS with a column index, left `- 1`, right `+ 1`. BFS order already sorts each column top to bottom. Track min and max to skip sorting.

## Example

```python
from collections import deque
from dataclasses import dataclass


@dataclass
class Node:
    val: int
    left: "Node | None" = None
    right: "Node | None" = None


def level_order(root: Node | None) -> list[list[int]]:
    out, queue = [], deque([root] if root else [])
    while queue:
        row = []
        for _ in range(len(queue)):
            node = queue.popleft()
            row.append(node.val)
            queue.extend(child for child in (node.left, node.right) if child)
        out.append(row)
    return out


def height(node: Node | None) -> int:
    return 0 if node is None else 1 + max(height(node.left), height(node.right))


root = Node(8, Node(3, Node(1), Node(6, Node(5))), Node(12, None, Node(15)))
print(level_order(root), height(root))
print(level_order(None), height(None))
# [[8], [3, 12], [1, 6, 15], [5]] 4
# [] 0
```

The level-size loop splits the queue into rows, and the height counts nodes on the longest path, `8, 3, 6, 5`. An empty tree has no rows and height 0 in this convention. All inputs are exercise inputs.

## More practice

Work the original exercises on the **Drills** tab. Each one names the rule, the cost, and a Python check.
