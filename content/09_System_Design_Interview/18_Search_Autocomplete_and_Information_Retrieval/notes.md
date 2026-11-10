# Search Autocomplete and Information Retrieval

Redcedar Listening Room keeps a catalog of spoken programs and a desk board where patrons type the start of a title. A trie answers that prefix from a short list stored on the node. A nightly count of submitted queries rebuilds the trie, and a ban or a jump that cannot wait patches it. Gallery and annex split the trie by first letter. Transcript search is a separate path: an inverted index, a score, and a copy that can lag the primary. The cache tier, the search store, generic sharding, the batch job, the change pipeline, a crawler, and a geohash stay in the topics that own them.

## Key Points

- **Trie (Prefix Tree)** — one step per character. "ni" reaches night jar, night market, and nine bells. Paths stop at 40 characters. The keystroke reads the ordered top 5 stored on the node.
- **Search Autocomplete System** — the online read. Return the list on the node inside 40 ms. An empty box uses the root list. A banned title is omitted in the response. One patron's recent plays can reorder the same five.
- **Query Log Aggregation** — a nightly count of submitted queries builds a new trie and swaps it in at close. The counted thing is the query string. The job shape is Batch Processing. A ban does not wait for the swap.
- **Trie Operations** — insert a string past 5 submits, re-sort the top 5 when a count jumps, or unlink a banned string and strip it from every ancestor list. The rebuild is the consistent picture. A patch is for a change that cannot wait.
- **Trie Partition** — gallery holds a–m, annex holds n–z, and a prefix stays with its completions. Annex takes about 70 of 100 keystrokes. The next cut is a longer prefix. A hash ring and a salted key stay in Data Partitioning and Consistent Hashing.
- **Inverted Index** — a term points at program ids. owls AND fen leaves p1. Term counts and positions can ride on the posting. The store, and the lag of that copy, are Search Index Store.
- **Relevance Ranking** — eight times "over" at weight 1 scores 8. One "quay" at weight 20 scores 20. BM25 saturates frequency and accounts for length. A distinctive word keeps the text score in front. Common words leave room for plays or recency.
- **Full-Text Search Architecture** — p9 can be committed on the primary and missing from search until the copy lands. That pipeline is Change Data Capture. A word query scatters by program id and the coordinator merges scores. An id lookup stays on the primary.

## Example

The board walks "ni". The node for that prefix is rebuilt after "night market" reaches 50. A transcript query for owls and fen intersects two sorted posting lists.

```python
WORDS = ("night jar", "night market", "nine bells", "marsh rail")
PREFIX = "ni"
JUMPED = (("night jar", 40), ("nine bells", 30), ("night market", 50))
K = 2
OWLS = ("p1", "p3")
FEN = ("p1", "p2")


def build(words: tuple[str, ...]) -> dict:
    root: dict = {}
    for word in words:
        node = root
        for ch in word:
            node = node.setdefault(ch, {})
        node.setdefault("$", []).append(word)
    return root


def completions(root: dict, prefix: str) -> list[str]:
    node = root
    for ch in prefix:
        if node is None:
            return []
        node = node.get(ch)
    if node is None:
        return []
    found: list[str] = []
    stack = [node]
    while stack:
        cur = stack.pop()
        found.extend(cur.get("$", ()))
        for key, child in cur.items():
            if key != "$":
                stack.append(child)
    return sorted(found)


def top_k(rows: tuple[tuple[str, int], ...], k: int) -> tuple[str, ...]:
    ordered = sorted(rows, key=lambda row: (-row[1], row[0]))
    return tuple(title for title, _count in ordered[:k])


def intersect(left: tuple[str, ...], right: tuple[str, ...]) -> tuple[str, ...]:
    i = 0
    j = 0
    found: list[str] = []
    while i < len(left) and j < len(right):
        if left[i] == right[j]:
            found.append(left[i])
            i += 1
            j += 1
        elif left[i] < right[j]:
            i += 1
        else:
            j += 1
    return tuple(found)


print(completions(build(WORDS), PREFIX), top_k(JUMPED, K), intersect(OWLS, FEN))
# ['night jar', 'night market', 'nine bells'] ('night market', 'night jar') ('p1',)
```

The walk returns the three titles under "ni" and leaves "marsh rail" on its own branch. The fresh top 2 leads with "night market". The posting lists meet at p1. A list still showing the pair from before the jump is stale until a patch or the nightly swap. p9 can be committed on the primary and absent from a posting list until the copy lands.

## See also

- [Interview Framework and Process](../01_Interview_Framework_and_Process/) — The Four-Step Framework. Scoping the question stays there.
- [Scalability Fundamentals](../02_Scalability_Fundamentals/) — Describing Load. A keystroke rate and the bytes in the trie stay there.
- [Caching](../05_Caching/) — the cache tier. A shared copy of a hot prefix, and eviction of that tier, stay there. The top 5 on a trie node stays here.
- [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/) — Search Index Store. The store choice, and a copy that can lag the primary, stay there.
- [Data Partitioning and Consistent Hashing](../08_Data_Partitioning_and_Consistent_Hashing/) — Horizontal Partitioning (Sharding) and Hot Partition Mitigation. A hash ring, a move, and a salted key stay there. The first-letter split stays here.
- [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/) — Batch Processing and Change Data Capture. The job shape and the change pipeline stay there. What the nightly job counts, and the search gap after a commit, stay here.
- [Geospatial and Location-Based Services](../20_Geospatial_and_Location_Based_Services/) — Geohash and Quadtree. Nearby programs stay there.
- [Classic Design Problems](../24_Classic_Design_Problems/) — Web Crawler. Pages fetched by a crawler stay there.
