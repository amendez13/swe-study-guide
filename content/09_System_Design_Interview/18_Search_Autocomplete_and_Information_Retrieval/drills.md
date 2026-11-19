# Search Autocomplete and Information Retrieval — Drills

Original practice for a prefix walk, a list stored on the node, and a committed document missing from search. Each card is one exercise: commit to an answer, then check it. The numbers are a worked example for a search box, the kind Google and Amazon product search show as you type, and for an Elasticsearch-style index over product pages. The cache tier stays in Caching. The search store and its lagging copy stay in Databases NoSQL and Specialized. A hash ring and a salted key stay in Data Partitioning and Consistent Hashing. The batch job and the change pipeline stay in Storage and Data Processing at Scale. A web crawler stays in Classic Design Problems. A geohash stays in Geospatial and Location-Based Services.

## Prefix Walk

The trie holds `night sky`, `night mode`, `nintendo`, and `maps`. Which queries does the walk return for `ni`, and which queries does it return for `night `?

```python
WORDS = ("night sky", "night mode", "nintendo", "maps")
SHORT = "ni"
LONG = "night "
```

**Answer:** `ni` stops at the node that still has three descendants: `night mode`, `night sky`, and `nintendo`. `night ` takes the space after `night` and leaves `nintendo` and `maps` off that node. The walk reads one character per step and then collects the queries stored under the node it reached. Paths in this design stop at 40 characters, and both prefixes are inside that cap.

```python
WORDS = ("night sky", "night mode", "nintendo", "maps")
SHORT = "ni"
LONG = "night "


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


root = build(WORDS)
print(completions(root, SHORT), completions(root, LONG))
# ['night mode', 'night sky', 'nintendo'] ['night mode', 'night sky']
```

![Prefix Walk](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search-drills-1-prefix-walk.png)

*Source: [`diagrams/search-drills.drawio`](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search-drills.drawio), page 1.*

## Top-K at the Node

The node for `ni` has three counts: `night sky` 40, `nintendo` 30, `night mode` 12. The box shows 2 queries. Which pair is stored? `night mode` later reaches 50, and the node has not been rebuilt. Which pair would a fresh trim keep, and what does the box still show?

```python
ON_NODE = (("night sky", 40), ("nintendo", 30), ("night mode", 12))
JUMPED = (("night sky", 40), ("nintendo", 30), ("night mode", 50))
K = 2
```

**Answer:** The stored pair is `night sky` then `nintendo`. A fresh trim after the jump is `night mode` then `night sky`. The box still shows the stored pair. The list sits on the node so the keystroke reads two queries. Collecting every descendant under `ni` and sorting them would repeat that work on every letter. The list goes stale when a count moves and the node is left as it was. A shared cache tier in front of the node, and eviction of that tier, stay in Caching.

```python
ON_NODE = (("night sky", 40), ("nintendo", 30), ("night mode", 12))
JUMPED = (("night sky", 40), ("nintendo", 30), ("night mode", 50))
K = 2


def top_k(rows: tuple[tuple[str, int], ...], k: int) -> tuple[str, ...]:
    ordered = sorted(rows, key=lambda row: (-row[1], row[0]))
    return tuple(title for title, _count in ordered[:k])


stored = top_k(ON_NODE, K)
fresh = top_k(JUMPED, K)
print(stored, fresh, stored == fresh)
# ('night sky', 'nintendo') ('night mode', 'night sky') False
```

![Top-K at the Node](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search-drills-2-top-k-at-the-node.png)

*Source: [`diagrams/search-drills.drawio`](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search-drills.drawio), page 2.*

## Gather Cadence

Yesterday's log holds 4,000 submitted queries. The nightly design counts that closed log and swaps a trie when the job finishes. The live design increments a count on every submit, on the keystroke path. How many count-writes does the keystroke path do under each design, and when is each design acceptable? `nintendo` has to leave the box before the next search. What removes it?

```python
SUBMITS = 4000
MODES = ("nightly", "live")
```

**Answer:** The nightly design does 0 count-writes on the keystroke path. At noon the box is still serving the trie from last night's swap, which fits suggestions that may trail the log by a day. The live design does 4,000 count-writes on the keystroke path, one per submit, and the rank can move during the day when that write rate fits. `nintendo` leaves by a delete. A nightly count and a live increment both leave the string in the lists until that delete. The delete is Trie Patch. The shape of the nightly job is Batch Processing.

```python
SUBMITS = 4000
MODES = ("nightly", "live")


def path_writes(mode: str, submits: int) -> int:
    if mode == "nightly":
        return 0
    return submits


print(*(path_writes(mode, SUBMITS) for mode in MODES))
# 0 4000
```

![Gather Cadence](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search-drills-3-gather-cadence.png)

*Source: [`diagrams/search-drills.drawio`](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search-drills.drawio), page 3.*

## Trie Patch

Four changes arrive. `night mode` jumped, and the morning box may show it. The same query jumped, and the evening box must show it. `nikon camera` passed the cutoff of 5 submits. `nintendo` is banned. The ancestor lists still hold `nintendo` beside `night sky`. What is the move for each change, and does a count set to zero, with those lists left in place, still suggest the banned query?

```python
EVENTS = ("jump-can-wait", "jump-tonight", "new-query", "banned")
LISTS = (("night sky", "nintendo"),)
BANNED = "nintendo"
```

**Answer:** A jump the morning can show waits for the rebuild. A jump the evening must show patches the top 5 on each node of the path. A new string past the cutoff is an insert. A ban is a delete now: unlink the terminal, prune empty nodes, and strip the string from every ancestor list. A count set to zero, with the lists left in place, still suggests `nintendo`. The rebuild replaces every list from the same counts. A patch has to rewrite each list that stored the string.

```python
EVENTS = ("jump-can-wait", "jump-tonight", "new-query", "banned")
MOVE = {
    "jump-can-wait": "rebuild",
    "jump-tonight": "patch",
    "new-query": "insert",
    "banned": "delete",
}
LISTS = (("night sky", "nintendo"),)
BANNED = "nintendo"


def still_suggested(lists: tuple[tuple[str, ...], ...], banned: str) -> bool:
    return any(banned in titles for titles in lists)


print(" ".join(MOVE[name] for name in EVENTS), still_suggested(LISTS, BANNED))
# rebuild patch insert delete True
```

![Trie Patch](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search-drills-4-trie-patch.png)

*Source: [`diagrams/search-drills.drawio`](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search-drills.drawio), page 4.*

## Prefix Shard

Host a–m holds a first character from `a` through `m`. Host n–z holds `n` through `z`. Where do `maps`, `night sky`, and the prefix `ni` land? Of 100 keystrokes, 70 begin with `n`. What does that 70 do to the pair of hosts?

```python
TITLES = ("maps", "night sky", "ni")
N_SHARE = 70
```

**Answer:** `maps` lands on host a–m. `night sky` and `ni` land on host n–z, so the walk from that prefix to its completions stays on one host. The 70 keystrokes sit on host n–z. That host's processor and its trie memory are the hot spot. The next cut lengthens the `n` prefixes and keeps each prefix with its descendants. Hashing the whole string can send `ni` and `night sky` to different hosts. Moving shards, and salting one key, stay on Horizontal Partitioning (Sharding) and Hot Partition Mitigation.

```python
TITLES = ("maps", "night sky", "ni")
N_SHARE = 70


def host(text: str) -> str:
    if text[0] < "n":
        return "a–m"
    return "n–z"


print(*(host(text) for text in TITLES), N_SHARE)
# a–m n–z n–z 70
```

![Prefix Shard](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search-drills-5-prefix-shard.png)

*Source: [`diagrams/search-drills.drawio`](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search-drills.drawio), page 5.*

## Postings Intersect

The posting lists are sorted. `wool` points at p1, p3. `trail` points at p1, p2. `rain` points at p3, p4. `boots` points at p2, p4. The pages are p1 "wool socks for the trail", p2 "trail boots at home", p3 "wool hat in the rain", and p4 "rain boots for the city". Which documents survive `wool` AND `trail`, and which survive `rain` AND `boots`?

```python
POSTINGS = {
    "wool": ("p1", "p3"),
    "trail": ("p1", "p2"),
    "rain": ("p3", "p4"),
    "boots": ("p2", "p4"),
}
```

**Answer:** `wool` AND `trail` leaves p1. `rain` AND `boots` leaves p4. The merge walks the two sorted lists once. A document that survives is a candidate. The order those candidates appear in is Rank Signal. The store that holds the lists, and the fact that they are a copy, are Search Index Store.

```python
POSTINGS = {
    "wool": ("p1", "p3"),
    "trail": ("p1", "p2"),
    "rain": ("p3", "p4"),
    "boots": ("p2", "p4"),
}


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


print(
    intersect(POSTINGS["wool"], POSTINGS["trail"]),
    intersect(POSTINGS["rain"], POSTINGS["boots"]),
)
# ('p1',) ('p4',)
```

![Postings Intersect](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search-drills-6-postings-intersect.png)

*Source: [`diagrams/search-drills.drawio`](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search-drills.drawio), page 6.*

## Rank Signal

`for` has term frequency 8 and weight 1. `merino` has term frequency 1 and weight 20. `phone case` was chosen 40 times this week. `merino socks` was chosen 3 times. What is each text score? When the shopper typed `merino`, which signal leads? When the typed words are common, which signal may lead?

```python
TF = {"for": 8, "merino": 1}
IDF = {"for": 1, "merino": 20}
CLICKS = {"phone case": 40, "merino socks": 3}
```

**Answer:** The text score is term frequency times the weight: 8 for `for`, 20 for `merino`. `merino` leads on the text score, and a rare typed word keeps that score in front of the click counts. Common words, `for` among them, leave the text score weak, so an item chosen 40 times can lead an item chosen 3 times. BM25 is the same idea with frequency saturation and a length term. The requirement says which signal leads. The weight cutoff of 10 in the snippet is the exercise's stand-in for "this word is rare," and the weights themselves are chosen so the arithmetic is obvious.

```python
TF = {"for": 8, "merino": 1}
IDF = {"for": 1, "merino": 20}
CLICKS = {"phone case": 40, "merino socks": 3}


def text_score(term: str) -> int:
    return TF[term] * IDF[term]


def leader(term: str) -> str:
    if IDF[term] >= 10:
        return "text"
    return "clicks"


print(text_score("for"), text_score("merino"), leader("merino"), leader("for"), CLICKS["phone case"])
# 8 20 text clicks 40
```

![Rank Signal](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search-drills-7-rank-signal.png)

*Source: [`diagrams/search-drills.drawio`](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search-drills.drawio), page 7.*

## Index Lag

Document p9, `nikon camera`, is committed on the catalog primary. The search index still holds p1, p2, and p3. A search for the words in p9 misses it. Where does that gap live?

```python
PRIMARY = ("p1", "p2", "p3", "p9")
INDEX = ("p1", "p2", "p3")
```

**Answer:** p9 is on the primary and absent from the index. The commit has landed. The gap is the copy that has not written p9's terms yet. Search Index Store is that copy. Change Data Capture is the pipeline that carries the committed change. A crawler that fetched a page is a different ingress, the Web Crawler. The suggestion trie can also lack `nikon camera` until the nightly swap or a patch. That delay is the trie cadence. This miss is the search copy.

```python
PRIMARY = ("p1", "p2", "p3", "p9")
INDEX = ("p1", "p2", "p3")


def missing(primary: tuple[str, ...], index: tuple[str, ...]) -> tuple[str, ...]:
    have = set(index)
    return tuple(document for document in primary if document not in have)


print(missing(PRIMARY, INDEX))
# ('p9',)
```

![Index Lag](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search-drills-8-index-lag.png)

*Source: [`diagrams/search-drills.drawio`](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search-drills.drawio), page 8.*
