# Tries

Trie problems store many strings so that shared prefixes share one path, then answer questions one character at a time. The node structure, insert, search, deletion, and the comparison with hash tables are on the Data Structures [Heaps and Tries](#07_Data_Structures_and_Algorithms/06_Heaps_and_Tries) topic. This topic is the problem set: designing the class, keeping answers in the nodes, wildcard search, a trie that steers a grid search, suffix and binary tries, compression, and when a set or a sorted list is the better tool. The two decisions are what each node stores and whether the walk follows one edge or branches.

## Key Points

- **Tries as a pattern** — one character per edge, shared prefixes share nodes. Use it for prefix questions across many strings. Every operation is O(k) for a key of length k.
- **Node design** — dict children store only real edges, 26-slot arrays reserve every slot. Mark the end with a boolean, the word itself, or a counter. Never use a mutable default for children.
- **Design a trie** — insert, search, and `has_prefix` share one walk. Search also needs the end marker. `has_prefix("")` is true.
- **Store answers in the nodes** — keep a total on every node of the path. Apply the difference when a key is updated.
- **Wildcard search** — a letter follows one edge, a dot tries every child. Check the end marker at the last position and stop at the first match.
- **Trie-guided grid backtracking** — carry the trie node with the cell and step only along trie edges. Mark visited cells with `"#"` and restore them.
- **Find all words on a board** — store each word at its end node, search from every cell, and keep going after a hit. O(N L + m n 3^L).
- **Remove found words and dead branches** — clear the stored word on its first hit, and delete a child that has no children and no word.
- **Suffix trie for substring queries** — insert every suffix, and a substring test becomes a prefix walk. O(n²) build, so switch to suffix arrays for long texts.
- **Binary trie for maximum XOR** — store numbers by bits from the top and prefer the opposite bit at each level. O(n b) instead of O(n²).
- **Compressed tries** — merge one-child chains into string-labeled edges and split an edge when a new word diverges. Linux routing and Redis streams use this layout.
- **Trie, set, or sorted list** — a set for exact lookups, `bisect` on a sorted list for occasional prefix queries, a trie for frequent prefix queries, updates, or letter-by-letter search.

## Example

```python
class TrieNode:
    __slots__ = ("children", "is_word")

    def __init__(self) -> None:
        self.children: dict[str, "TrieNode"] = {}
        self.is_word = False


def insert(root: TrieNode, word: str) -> None:
    node = root
    for ch in word:
        node = node.children.setdefault(ch, TrieNode())
    node.is_word = True


def walk(root: TrieNode, text: str) -> TrieNode | None:
    node = root
    for ch in text:
        node = node.children.get(ch)
        if node is None:
            return None
    return node


root = TrieNode()
for word in ["note", "notes", "nova"]:
    insert(root, word)
for text in ("note", "not", "nov", "nest"):
    node = walk(root, text)
    print(text, node is not None, node is not None and node.is_word)
# note True True
# not True False
# nov True False
# nest False False
```

The middle column answers "is this a prefix" and the last column answers "is this a stored word". `not` and `nov` are prefixes but not words, which is exactly the case the end marker exists for. All words are exercise words.

## More practice

Work the original exercises on the **Drills** tab. Each one names the rule, the cost, and a Python check.
