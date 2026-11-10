## Trie (Prefix Tree)

A trie stores previous search queries one character per step from the root. The node you land on is that prefix, and the lookup cost is the number of characters typed.

**Why it exists.** A search box like Google's has to answer after every letter. Scanning 20,000 stored queries on each keystroke would reread the whole set. The trie touches only the path for the letters already typed, so the other queries stay unread.

**How it works.**

1. Each edge is one character, including the space. With a map from character to child, each step is one lookup.
2. Suppose the trie holds `night sky`, `night mode`, `nintendo`, and `maps`. The prefix `ni` walks `n`, then `i`. Under that node sit `night mode`, `night sky`, and `nintendo`. `maps` sits on the `m` branch and is never visited.
3. This design stops each path at 40 characters. A pasted paragraph is stored under its first 40 characters, so one long string cannot add a chain of hundreds of nodes. Elasticsearch's completion field caps an input at 50 characters by default, for the same reason.
4. The node also holds the top 5 completions for its prefix, already ordered. The keystroke reads that list. Collecting every descendant and sorting them would repeat that work on every letter. The list is computed ahead of the keystroke and kept on the node.

A shared cache of one hot prefix, and eviction of that tier, stay in [Caching](../05_Caching/). The request that returns the list is Search Autocomplete System.

**Trade-offs.** A hash map from the full prefix string to its top 5 is a single lookup, and it stores the prefix characters again at every length. The trie shares those characters across queries that start the same way. A radix tree collapses a chain of nodes that have only one child, which shrinks `nintendo` once the path has branched. Elasticsearch's completion suggester compacts this idea into an in-memory finite-state transducer built at index time. Any of these can hold the top 5. The expensive part is keeping that list fresh, which is Trie Operations.

**In an interview.** Say you are suggesting previous queries, the way the Google box does, and give the two limits out loud: paths stop at 40 characters, and each node stores an ordered top 5. Then say the read is a walk of the typed prefix plus a return of the list already on the node.

**Recap.**

| Choice | What the search box gets |
| --- | --- |
| One step per character | `ni` reads two nodes. The other 20,000 queries stay unread. |
| Cap of 40 characters | A pasted paragraph cannot add hundreds of nodes. |
| Top 5 stored on the node | The keystroke returns a list that was ordered ahead of time. |
| Space is a character | `night ` and `ni` are different nodes, so `nintendo` drops off once the space is typed. |

![Trie (Prefix Tree)](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search-1-trie-prefix-tree.png)

*Source: [`diagrams/search.drawio`](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search.drawio), page 1.*

## Search Autocomplete System

This is the online path from the search box to a short list of suggestions. The service walks the trie to the node for the typed prefix and returns the list stored there.

**Why it exists.** The person is still typing. The list has to be on screen before the next character, and it has to be safe to show. Building that list from the raw query log on the request would miss the latency budget.

**How it works.**

1. The box sends the prefix, here `ni`. The service walks `n`, then `i`, and returns the top 5 stored on that node. This design's budget is 40 ms, so the answer is that stored list.
2. An empty box has a prefix of length zero. The root holds the five most common queries, and the box shows those.
3. A banned query is dropped in this response even when an older list still names it. The check is a small denylist on the way out, so every replica hides the query as soon as the denylist updates.
4. The same five can be reordered from the three queries this person submitted this week. That reorder uses one trie. It can only reshuffle queries that were already in the five. A favorite that missed the global top 5 stays hidden.

The counts, and the swap that installs a trie built from them, are Query Log Aggregation. A shared cache in front of a hot prefix is [Caching](../05_Caching/). How to scope the question is The Four-Step Framework in [Interview Framework and Process](../01_Interview_Framework_and_Process/). A keystroke rate, and how many bytes the trie occupies, are Describing Load in [Scalability Fundamentals](../02_Scalability_Fundamentals/).

**Trade-offs.** Returning the stored list meets 40 ms and can be a day stale, which is the cadence in Query Log Aggregation. Filtering a ban on the way out is immediate, and it spends one of the five slots on a query you then hide. Deleting it from the trie, in Trie Operations, frees the slot. Personalizing by reordering the five needs no second trie. A different candidate set per person is a larger design. An Amazon-style product box often mixes recent product queries with this global list. Recent queries are a per-person list. The trie remains the global one.

**In an interview.** Separate the read path from the count path. The read path is walk, denylist, optional reorder, respond inside 40 ms. Name 40 ms, the empty-box root list, and the denylist as decisions. Leave the nightly rebuild for the next card.

**Recap.**

| What the box sent | What comes back |
| --- | --- |
| `ni` | The ordered list stored on that node, inside a 40 ms budget. |
| An empty box | The five most common queries, stored at the root. |
| A prefix whose list still names a banned query | That query omitted in this response. |
| A signed-in person with three recent searches | The same five, reordered from those three. |

![Search Autocomplete System](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search-2-search-autocomplete-system.png)

*Source: [`diagrams/search.drawio`](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search.drawio), page 2.*

## Query Log Aggregation

Query log aggregation counts submitted searches offline and builds the next trie from those counts. A query typed today becomes a suggestion after the next build.

**Why it exists.** The search box is a read path with a 40 ms budget. Incrementing a counter on every submit would write on that path and would move the ranking during the day. Most suggestions can trail the log by a day. The log is the source of "what people actually searched," which is the list a Google-style box is showing.

**How it works.**

1. The service appends a log line when someone submits a query. Keystrokes are reads against the current trie. They are not the log. The counted thing is the submitted string.
2. A nightly job reads that closed day, counts each distinct string, and drops strings under the cutoff of 5 submits. Those are usually one-off typos.
3. The job builds a new trie whose nodes hold the top 5 for their prefix, then the service swaps in that trie. Requests in flight keep the previous trie. The swap is a pointer exchange, so one request sees one trie.
4. A title, a product query, or a navigation query can wait for that swap. A ban cannot. Removing a banned string is Trie Operations.

The job is a scheduled read of a finished log. Map, shuffle, reduce, and the choice of engine are Batch Processing in [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/). A word inside a document is a term in the inverted index. This job never sees that word unless someone submitted it as a query.

**Trade-offs.** The nightly build does zero count-writes on the keystroke path, and at noon the box is still serving last night's trie. A live counter on the submit path can move the rank the same day, at one write per submit. A query that must trend within minutes, such as a breaking name, is a short-window counter beside the trie. The shape of that counter is Stream Processing in [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/). Sampling the log keeps the head of the distribution and can miss a query sitting just over the cutoff of 5. Counting the closed day keeps every string that passed the cutoff.

**In an interview.** Say what you count: submitted queries, once each, from a closed log. Say the box keeps serving the previous trie until the swap. Then draw the line the requirement has to draw: suggestions may be a day old, and a ban may not.

**Recap.**

| Step | What happens |
| --- | --- |
| During the day | Submits are appended. The box does no count-writes. |
| Nightly job | Count each distinct string in the closed log. Keep strings with at least 5 submits. |
| Build | Write a new trie with an ordered top 5 on each node. |
| Swap | Install that trie when the job finishes. Today's query is a suggestion tomorrow. |
| A ban | Leaves this schedule and is handled in Trie Operations. |

![Query Log Aggregation](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search-3-query-log-aggregation.png)

*Source: [`diagrams/search.drawio`](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search.drawio), page 3.*

## Trie Operations

Trie operations are the three writes against a trie that is already serving: create a query, update its count, and delete it. The nightly rebuild replaces every list from one set of counts. A patch is the same write, done on the live trie because the change cannot wait for that rebuild.

**Why it exists.** The swap in Query Log Aggregation is a consistent picture, and it lands on a schedule. A query that just crossed the cutoff, a count that jumped this afternoon, or a ban that has to disappear before the next search cannot sit in yesterday's trie until morning.

**How it works.**

1. Create runs when a string passes 5 submits. `nikon camera` is inserted, any missing prefix nodes are added, and the top 5 on that path are refreshed.
2. Update runs when a count changes. `night mode` moving from 12 to 50 re-sorts the top 5 on `n`, on `ni`, and on each longer node of its path. A jump the morning box can show waits for the nightly rebuild. A jump the evening box must show is a patch of those nodes.
3. Delete unlinks a banned or withdrawn string. The terminal mark goes away, nodes that no longer lead anywhere can be removed, and the string is taken out of the top 5 of every ancestor.
4. A count left at zero, with the string still sitting in an ancestor list, still suggests it. The rebuild avoids that leftover because every list is written again from the same counts. A patch has to rewrite each list that stored the string.

Omitting a banned query at response time, even before this delete lands, is Search Autocomplete System. The filter hides the string. The delete frees the slot so a legitimate query can take its place.

**Trade-offs.** The rebuild touches the whole trie once and leaves every replica with the same lists after the swap. A patch touches only the path, which is at most 40 nodes, and it has to reach every copy that is serving. Miss one copy and that copy keeps suggesting the banned string until the filter or the next rebuild. Updating the top 5 on every ancestor is the write cost of the fast read. Store the top 5 only at the terminal, and the keystroke goes back to walking the subtree.

**In an interview.** Sort the change by how long it can wait. Overnight is a rebuild. This evening is a patch of the path: insert, re-sort, or delete. Say the failure mode out loud: a zero count that leaves the string in an ancestor list still shows it.

**Recap.**

| Change | Move |
| --- | --- |
| A new string has 5 or more submits, and morning is soon enough | Wait for the rebuild, which inserts it with its prefixes. |
| The evening box must show a count jump | Patch the top 5 on each node of that path. |
| The string is banned | Delete now: clear the terminal, prune empty nodes, and strip every ancestor list. |
| The count is set to zero and the lists are left in place | The box still suggests the string. |

![Trie Operations](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search-4-trie-operations.png)

*Source: [`diagrams/search.drawio`](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search.drawio), page 4.*

## Trie Partition

Trie partition places a prefix and the queries that continue it on the same host. The keystroke walk then stays on one machine.

**Why it exists.** One host runs out of memory or CPU once the trie or the keystroke rate no longer fits. The split has to preserve the walk. A prefix on one host and its completions on another turns every letter into a remote call.

**How it works.**

1. Host a–m holds prefixes whose first character is `a` through `m`. Host n–z holds `n` through `z`. `maps` is on a–m. `ni` and `night sky` are on n–z, so the walk from that prefix to its completions stays local.
2. Hashing the whole string can place `ni` and `night sky` on different hosts. The walk then needs both.
3. In this worked example, 70 of every 100 keystrokes start with `n`, the way one viral query can pile onto a single first letter. Host n–z takes that traffic. Its processor and the memory of its trie are the hot spot.
4. The next cut lengthens the prefix: `na` through `nh` on one host, `ni` through `nz` on another. Each prefix stays with its descendants.
5. The top 5 for a prefix shorter than the cut, including the empty prefix at the root, is assembled by asking the child hosts or stored as its own small list.

Placing a generic key, moving shards, and salting one key are Horizontal Partitioning (Sharding) and Hot Partition Mitigation in [Data Partitioning and Consistent Hashing](../08_Data_Partitioning_and_Consistent_Hashing/). This first-letter split is the one the document index does not use. That split is Full-Text Search Architecture.

**Trade-offs.** A first-letter split is easy to explain and easy to route: the router looks at one character. It is uneven, because real query logs are lumpy. A longer prefix spreads a hot letter and makes the root, and any prefix shorter than the cut, a scatter of child hosts. Caching that short-prefix list removes the scatter from the keystroke path and adds a list you have to refresh when the children change. Salting the hot prefix spreads its CPU and splits the walk, which is the problem this partition was built to avoid.

**In an interview.** Name the shard key as the prefix, and say the completion has to live with it. Then give the skew a number. Here, 70 of 100 keystrokes start with `n`, so the next move is a longer prefix, with descendants kept on the same host. Point hashing, rebalancing, and salting at Data Partitioning and Consistent Hashing.

**Recap.**

| Prefix | Where the walk runs |
| --- | --- |
| `maps` | Host a–m. The first character is `m`. |
| `ni` and `night sky` | Host n–z, together, so the walk is local. |
| 70 of 100 keystrokes start with `n` | Host n–z is the hot spot in this example. |
| The next cut | A longer prefix, and the queries that continue it stay on that host. |
| The root, or any prefix shorter than the cut | Merge the child hosts, or serve a list stored for that short prefix. |

![Trie Partition](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search-5-trie-partition.png)

*Source: [`diagrams/search.drawio`](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search.drawio), page 5.*

## Inverted Index

An inverted index maps a term to the documents that contain it. It is the structure behind an Elasticsearch-style full-text search.

**Why it exists.** The autocomplete trie answers "what queries start with these letters." A product search or a web search asks a different question: which documents contain these words. Scanning every product description for `wool` and `trail` rereads the catalog. The index has already listed the documents for each word.

**How it works.**

1. Each document is analyzed into terms. Lowercasing is the usual first step, so `Wool` and `wool` meet. Stemming, which would fold `boots` into `boot`, is a choice you name.
2. Take four product pages. p1 is "wool socks for the trail", p2 is "trail boots at home", p3 is "wool hat in the rain", and p4 is "rain boots for the city". The postings are `wool → p1, p3`, `trail → p1, p2`, `rain → p3, p4`, and `boots → p2, p4`. The ids in each list are sorted.
3. A query that wants both `wool` and `trail` walks the two sorted lists once and keeps the ids that appear in both. That intersection leaves p1. A query that wants either term unions the lists.
4. A posting can also carry the term's count in that document, and the positions a phrase query uses. Positions are how "rain boots" as a phrase stays distinct from the two words anywhere in the page.

The structure is this map. Which store holds it, and the fact that the map is a secondary copy that can lag the catalog primary, are Search Index Store in [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/). Ordering the ids that survive the intersection is Relevance Ranking. A nearby-document lookup, a geohash, and a quadtree stay in [Geospatial and Location-Based Services](../20_Geospatial_and_Location_Based_Services/).

```python
def intersect(left: tuple[str, ...], right: tuple[str, ...]) -> tuple[str, ...]:
    """Both lists are sorted document ids. One pass keeps the ids in both."""
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
```

**Trade-offs.** The merge is linear in the two list lengths, which is why a common word with a huge posting list dominates the cost. Search engines skip ahead inside a long list. The interview version is the two-pointer merge above. Phrase positions make the posting heavier and make "rain boots" precise. Drop the positions and the query becomes a bag of words. The trie and this index answer different questions, and they are built from different inputs: submitted query strings, and words inside documents.

**In an interview.** Draw the map, then the intersection, and say the lists are sorted so the merge is one pass. Name analysis in one sentence: lowercase, and stemming only if the requirement wants `boot` and `boots` to meet. Leave ranking for the next card and the store's lag for Search Index Store.

**Recap.**

| Query | Result on these four pages |
| --- | --- |
| `wool` AND `trail` | p1. It is the only id in both lists. |
| `rain` AND `boots` | p4. |
| `wool` OR `trail` | p1, p2, and p3. The union keeps either list. |
| Phrase "rain boots" | Needs positions. p4 has the words together. A page with `rain` in one sentence and `boots` in another does not. |

![Inverted Index](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search-6-inverted-index.png)

*Source: [`diagrams/search.drawio`](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search.drawio), page 6.*

## Relevance Ranking

Relevance ranking orders the document ids that survived the inverted-index intersection. The text score is the start. Clicks, purchases, and recency sit beside it when the product needs them.

**Why it exists.** The intersection is a set. A search results page is an order. Eight mentions of a common word and one mention of a rare word are not equally useful, and a page nobody opens can still contain the rare word.

**How it works.**

1. Term frequency is how often the word appears in this document. A rarity weight rises when few documents contain the word. In this worked example the weight is 1 for `for` and 20 for `merino`. Those weights are chosen so the arithmetic is obvious. They are a sketch of inverse document frequency, which is high for rare terms.
2. Eight occurrences of `for` score 8 times 1, which is 8. One occurrence of `merino` scores 1 times 20, which is 20. On this sketch the rare word leads.
3. BM25 is the form to name from there. Elasticsearch and Lucene use it as the default similarity. Extra repetitions add less once the word is already present. With the length knob turned off and with `k1` at its default 1.2, one occurrence contributes 1 and eight occurrences contribute about 1.9, which is the saturation. The length knob `b` defaults to 0.75, so a document longer than average is pulled down and a shorter one is lifted. A long page does not win only by containing more words. BM25's rarity formula is its own formula. The interview point is the direction: rare terms count more.
4. Choice count and age sit beside the text score. `phone case` was chosen 40 times this week. `merino socks` was chosen 3 times. A typed `merino` keeps the text score in front, so the rare-word match leads. Common words leave the text scores small and close, so the item chosen 40 times can lead the item chosen 3 times. The requirement says which signal leads.

Reordering one person's query suggestions, inside a fixed five, is Search Autocomplete System. That reorder is a different list from this document ranking.

**Trade-offs.** Text-only ranking is stable and explainable, and it surfaces a perfect lexical match that nobody has clicked. Blending in clicks or purchases follows what people chose, and it buries a new document that has had no traffic. A time decay lets a new page compete. Turning `b` to 0 drops length from the formula, which fits a catalog of short titles that are all about the same length. Turning it up punishes a long page that mentions the word once.

**In an interview.** Compute the sketch out loud, 8 times 1 and 1 times 20, and label it as a sketch. Then name BM25 and the two defaults, `k1` 1.2 and `b` 0.75, for saturation and length. Ask which signal the requirement wants in front when the typed words are common. A shopping search often puts purchases beside the text. A documentation search often stays on the text.

**Recap.**

| Signal | Worked result |
| --- | --- |
| `for` eight times, weight 1 | Text sketch 8. The word is common, so the score stays small. |
| `merino` once, weight 20 | Text sketch 20. The rare word leads the sketch. |
| BM25 frequency piece, `k1` 1.2, length ignored, before the rarity weight | One occurrence contributes 1. Eight contribute about 1.9. |
| BM25 length, `b` 0.75 | A longer-than-average document is pulled down. |
| Chosen 40 times versus 3 times | Can lead when the typed words are common and the text scores are close. |

![Relevance Ranking](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search-7-relevance-ranking.png)

*Source: [`diagrams/search.drawio`](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search.drawio), page 7.*

## Full-Text Search Architecture

Full-text search architecture is the path from a committed document to a ranked hit. The catalog primary holds the document. An Elasticsearch-style index holds a copy of the terms, split across shards, and a coordinator merges the scores.

**Why it exists.** The inverted index is a secondary copy. Product search and web search both need that copy to be large, current enough, and able to answer a word query without reading the primary. The primary still owns the row you load by id, including the price and the fields the index left out.

**How it works.**

1. The catalog primary commits document p9, `nikon camera`. A search for p9's words can miss it until a later copy has written those terms into the index. The commit has landed. The gap is the copy.
2. The pipeline that carries a committed change is Change Data Capture in [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/). The primary already wrote the change to its log. A tailer reads that log and updates the index. The store that holds the copy is Search Index Store in [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/).
3. After the copy reaches a shard, Elasticsearch still hides it from search until a refresh. The refresh interval defaults to about one second. That is a second, smaller gap, on top of the pipeline lag.
4. A query for `rain` goes to every shard that might hold a matching document. The index is split by document id, so one term's postings are spread and the read scatters. The coordinator merges the scored ids. Each shard scores with the document frequencies it holds, so the same rare word can weigh differently on two shards. A pass that collects global frequencies makes the scores comparable and adds a round trip.
5. More documents fill the shards. In Elasticsearch the primary shard count is chosen when the index is created, so growing past it means a new index and a reindex. A higher query rate adds replicas. How a generic key is placed and moved is [Data Partitioning and Consistent Hashing](../08_Data_Partitioning_and_Consistent_Hashing/). A lookup by document id stays on the primary.

Text that arrives because a crawler fetched a page is the Web Crawler in [Classic Design Problems](../24_Classic_Design_Problems/). A product catalog usually takes the change pipeline above. The suggestion trie and its first-letter split are Trie Partition. That split keeps a prefix with its completions. This one spreads a term across document shards on purpose.

**Trade-offs.** Acknowledging the write when the primary commits keeps the catalog available when the index is behind. The searcher can miss p9 until the copy and the refresh land. Waiting for the index before acknowledging ties the product write to search lag. Dual-writing from the application can lose the index update if the process dies after the primary commit. The log tailer replays a change the primary has already recorded. Replicas add read capacity for the query rate. They do not add room for more documents. That room is the primary shard count, set at index creation.

**In an interview.** Draw two copies and name the gap: p9 is committed, and search misses it until the index catches up. Point the pipeline at Change Data Capture and the store at Search Index Store. Then say the query scatters by document id and the coordinator merges by score, while a lookup of p9 by id stays on the primary. Keep the suggestion trie on its own prefix split.

**Recap.**

| Step | Where it lives |
| --- | --- |
| Commit p9 | The catalog primary has the row. |
| Search misses p9 | The index copy has not landed, or the shard has not refreshed. |
| The pipeline | Change Data Capture, reading the primary's log. |
| A query for `rain` | Every shard that might hold a match, then a merge by score. |
| More documents | Primary shards, chosen when the index is created. |
| A higher query rate | Replicas. |
| Load p9 by id | The primary, which still holds the price and the unindexed fields. |

![Full-Text Search Architecture](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search-8-full-text-search-architecture.png)

*Source: [`diagrams/search.drawio`](/content/09_System_Design_Interview/18_Search_Autocomplete_and_Information_Retrieval/diagrams/search.drawio), page 8.*
