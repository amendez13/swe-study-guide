# Trees

Trees are recursive, acyclic, connected structures used to represent hierarchical data. The binary search tree is the foundational variant: it enforces an ordering invariant (left < node < right) that enables O(log N) search, insert, and delete when balanced. Mastering trees means knowing the node structure, the four traversal orders, how BST operations maintain invariants, and why self-balancing matters.

## Key Points

- **Tree terminology** -- a tree has a root node, edges connecting parents to children, leaf nodes with no children, depth measured from root down, and height measured from node to deepest leaf.
- **Binary tree node** -- each node stores a value plus optional `left` and `right` child references; when both are `None`, the node is a leaf.
- **BST invariant** -- for every node, all left-subtree values are less than or equal and all right-subtree values are greater; this enables binary search on a tree structure.
- **BST search** -- start at the root, compare the target to the current node, go left if smaller, right if larger; O(log N) average, O(N) worst case on a skewed tree.
- **BST insert** -- follow the same search path until you find a `None` slot and place the new node there as a leaf.
- **BST deletion** -- three cases: leaf (remove directly), one child (replace with child), two children (swap with in-order successor then delete successor).
- **Balanced trees** -- AVL trees enforce height difference <= 1 at every node; Red-Black trees use coloring rules to guarantee height <= 2 log(N+1); both ensure O(log N) worst-case operations.
- **Complete, full, perfect** -- complete means levels filled left to right (heap shape); full means every node has 0 or 2 children; perfect means full and complete with all leaves at the same depth.
- **In-order traversal** -- left, node, right; produces sorted output for a BST.
- **Pre-order traversal** -- node, left, right; useful for serialization and tree copying.
- **Post-order traversal** -- left, right, node; useful for deletion and expression evaluation.
- **Level-order traversal (BFS)** -- uses a queue to visit nodes level by level; the `for _ in range(len(queue))` pattern processes one level per iteration.
- **Height vs. depth** -- height is longest path down to a leaf (leaves have height 0); depth is distance from root to node (root has depth 0); tree height determines BST operation cost.

## Example

A complete binary search tree with insert, search, all four traversals, and height calculation:

```python
from collections import deque


class TreeNode:
    def __init__(self, val, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def bst_insert(root: TreeNode | None, val: int) -> TreeNode:
    if root is None:
        return TreeNode(val)
    if val <= root.val:
        root.left = bst_insert(root.left, val)
    else:
        root.right = bst_insert(root.right, val)
    return root


def bst_search(root: TreeNode | None, target: int) -> bool:
    if root is None:
        return False
    if target == root.val:
        return True
    return bst_search(root.left, target) if target < root.val else bst_search(root.right, target)


def inorder(root: TreeNode | None) -> list[int]:
    if root is None:
        return []
    return inorder(root.left) + [root.val] + inorder(root.right)


def preorder(root: TreeNode | None) -> list[int]:
    if root is None:
        return []
    return [root.val] + preorder(root.left) + preorder(root.right)


def postorder(root: TreeNode | None) -> list[int]:
    if root is None:
        return []
    return postorder(root.left) + postorder(root.right) + [root.val]


def level_order(root: TreeNode | None) -> list[list[int]]:
    if root is None:
        return []
    result = []
    queue = deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        result.append(level)
    return result


def height(root: TreeNode | None) -> int:
    if root is None:
        return -1
    return 1 + max(height(root.left), height(root.right))


# Build BST by inserting values
root = None
for val in [8, 3, 10, 1, 6, 14, 4, 7]:
    root = bst_insert(root, val)

#         8
#        / \
#       3   10
#      / \    \
#     1   6   14
#        / \
#       4   7

print("Search 6:", bst_search(root, 6))    # True
print("Search 5:", bst_search(root, 5))    # False
print("In-order: ", inorder(root))          # [1, 3, 4, 6, 7, 8, 10, 14]
print("Pre-order:", preorder(root))         # [8, 3, 1, 6, 4, 7, 10, 14]
print("Post-order:", postorder(root))       # [1, 4, 7, 6, 3, 14, 10, 8]
print("Level-order:", level_order(root))    # [[8], [3, 10], [1, 6, 14], [4, 7]]
print("Height:", height(root))              # 3
```

The in-order output is sorted because the BST invariant guarantees left values come before the node and right values come after. Level-order shows the tree's shape layer by layer, which is useful for debugging and for problems that operate on entire levels at once.
