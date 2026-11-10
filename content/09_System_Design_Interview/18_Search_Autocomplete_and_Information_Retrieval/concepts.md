## Trie (Prefix Tree)

A trie stores the queries patrons of Redcedar Listening Room have submitted, one character per step from the root. The prefix "ni" walks n and then i. The titles that continue from that node are "night jar", "night market", and "nine bells". "marsh rail" sits on another branch. The cost of the lookup is the number of characters in the prefix. The other 20,000 stored queries stay unread.

Each path stops at 40 characters. A pasted paragraph is stored under its first 40 characters, so one long string cannot add a chain of hundreds of nodes. The node also holds the top 5 completions for its prefix, already ordered. The keystroke reads that list. Gathering every descendant and sorting them would reread the subtree on every letter. The list is a result computed ahead of the keystroke and kept on the node. A shared cache of one hot prefix, and eviction of that tier, stay in [Caching](../05_Caching/). The read that returns the list is Search Autocomplete System.

```text
"ni"      night jar, night market, nine bells
"mar"     marsh rail
walk      one step per character
cap       40 characters
on node   top 5, already ordered
```

## Search Autocomplete System

This is the online path. A patron types "ni" on the desk board. The service walks to that node and returns the five titles stored there. The board's budget is 40 ms, so the answer is that list. An empty box returns the five most played programs, the list stored at the root. A title that has been banned is omitted in this response even when an older list still names it.

The same five can be reordered from the three programs this patron played this week. That reorder uses one trie. The counts, and the swap that installs a trie built from them, are Query Log Aggregation. A shared cache in front of a hot prefix is [Caching](../05_Caching/). How to scope the question is The Four-Step Framework in [Interview Framework and Process](../01_Interview_Framework_and_Process/). A keystroke rate, and how many bytes the trie occupies, are Describing Load in [Scalability Fundamentals](../02_Scalability_Fundamentals/).

```text
typed "ni"    the list on that node
budget        40 ms
empty box     five most played, at the root
banned        omitted in the response
reorder       this patron's three recent plays
counts        Query Log Aggregation
```

## Query Log Aggregation

The room writes a log line when a patron submits a query. A nightly job reads that closed day, counts each distinct string, and builds a trie whose nodes hold the top 5 for their prefix. At close the service swaps in the new trie. A title typed today is a suggestion tomorrow. That delay fits titles. A ban cannot wait for it.

The job is a scheduled read of a finished log. Map, shuffle, reduce, and the choice of engine are Batch Processing in [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/). The counted thing is the submitted query. A word inside a transcript is a term in the inverted index. A counter incremented on the board path would move the rank during the day and would write on every submit. The room keeps that write off the board. A change that cannot wait for the swap is Trie Operations.

```text
input     yesterday's submitted queries
count     one total per distinct string
write     a new trie, top 5 on each node
swap      at close
ban       cannot wait for the swap
shape     Batch Processing
```

## Trie Operations

Create runs when a string passes a cutoff of 5 submits. The new string is inserted, any missing prefix nodes are added, and the top 5 on that path are refreshed. Update runs when a count changes. "night market" moving from 12 to 50 re-sorts the top 5 on "n", on "ni", and on each longer node of its path. A jump the morning board can show waits for the nightly rebuild. A jump the evening board must show is a patch of those nodes.

Delete unlinks a banned or withdrawn string. The terminal mark goes away, nodes that no longer lead anywhere can be removed, and the string is taken out of the top 5 of every ancestor. A count left at zero, with the string still sitting in an ancestor list, still suggests it. The nightly rebuild is the consistent picture, because every list is replaced from the same counts. A patch is the path for a change that cannot wait, and it has to rewrite every list that stored the string. Omitting a banned title at response time is Search Autocomplete System.

```text
create    a string past 5 submits, plus its prefixes
update    a new count, re-sort the top 5 on the path
wait      nightly rebuild
tonight   patch the nodes on the path
delete    unlink, prune, strip every ancestor list
```

## Trie Partition

Gallery holds prefixes whose first character is a through m. Annex holds n through z. "marsh rail" is gallery. "ni" and "night jar" are annex, on one host, so the walk stays local. Hashing the whole string can place the prefix and a completion on different hosts, and the walk then needs both.

Annex takes about 70 of every 100 keystrokes, because night programs dominate the log. That host's processor and the memory of its trie are the hot spot. The next cut lengthens the prefix: "na" through "nh" on one host, "ni" through "nz" on another, each prefix kept with its descendants. The top 5 for a prefix shorter than the cut, including the root, is assembled from the children or stored as its own list. Placing a generic key, moving shards, and salting one key are Horizontal Partitioning (Sharding) and Hot Partition Mitigation in [Data Partitioning and Consistent Hashing](../08_Data_Partitioning_and_Consistent_Hashing/). This first-letter split is the one Search Index Store defers here.

```text
gallery    a–m, including "marsh rail"
annex      n–z, "ni" with "night jar"
hot        annex, about 70 of 100 keystrokes
next cut   a longer prefix, descendants stay with it
ring, salt Horizontal Partitioning, Hot Partition Mitigation
```

## Inverted Index

An inverted index maps a term to the programs whose transcripts contain it. Program p1 is "owls over the fen", p2 is "fen rails at dusk", and p3 is "owls at the quay". The postings are owls → p1, p3 and fen → p1, p2. A query that wants both terms intersects the lists and leaves p1. A query that wants either term unions them. A posting can also carry the term's count in that program, and the positions a phrase query uses.

The structure is this map. Which store holds it, and the fact that the map is a secondary copy that can lag the catalog primary, are Search Index Store in [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/). Ordering the ids that survive the intersection is Relevance Ranking. A nearby-program lookup, a geohash, and a quadtree stay in [Geospatial and Location-Based Services](../20_Geospatial_and_Location_Based_Services/).

```text
owls → p1, p3
fen  → p1, p2
both → p1
store, lagging copy   Search Index Store
nearby programs       Geohash, Quadtree
```

## Relevance Ranking

The ids that survive the intersection still need an order. Term frequency is how often the word appears in this transcript. Inverse document frequency is a weight that rises when few programs contain the word. With weights 1 for "over" and 20 for "quay", eight occurrences of "over" score 8, and one occurrence of "quay" scores 20. BM25 is the form to name from there. Further repetitions of a word add less once it is already present, and a long transcript does not win only by containing more words.

Play count and the age of the recording sit beside the text score. A distinctive typed word keeps the text score in front. Common words leave room for a program played 40 times this week to lead a rare-word match nobody played. The requirement says which of those signals leads. Reordering one patron's suggestions is Search Autocomplete System.

```text
"over" × 8, weight 1     score 8
"quay" × 1, weight 20    score 20
BM25                     frequency saturates, length is in the formula
distinctive word         text score leads
common words             plays or recency can lead
```

## Full-Text Search Architecture

The catalog primary commits program p9. A search for p9's words can miss it until a later copy has written those terms into the index. The commit has landed. The gap is the copy. The pipeline that carries a committed change is Change Data Capture in [Storage and Data Processing at Scale](../13_Storage_and_Data_Processing_at_Scale/). The store that holds the copy is Search Index Store in [Databases NoSQL and Specialized](../07_Databases_NoSQL_and_Specialized/). Text that arrives because a crawler fetched a page is the Web Crawler in [Classic Design Problems](../24_Classic_Design_Problems/).

A query for "quay" goes to every shard that might hold a matching program, and a coordinator merges the scored ids. The index is split by program id, so one term's postings are spread and the read scatters. More programs add shards. A higher query rate adds replicas. How a generic key is placed and moved is [Data Partitioning and Consistent Hashing](../08_Data_Partitioning_and_Consistent_Hashing/). A lookup by program id stays on the primary. The suggestion trie and its first-letter split are Trie Partition.

```text
commit p9         the primary has the row
search misses p9  the copy has not landed
pipeline          Change Data Capture
scatter           every shard that might hold "quay"
gather            merge by score
id lookup         the primary
```
