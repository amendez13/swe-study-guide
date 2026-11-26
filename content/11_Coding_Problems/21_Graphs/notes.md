# Graphs

Graph problems hide nodes and edges inside grids, words, states, and dependencies, then ask about reachability, fewest steps, cheapest cost, an order, or group membership. The representations, traversals, and the algorithms themselves are on the Data Structures [Graphs](#07_Data_Structures_and_Algorithms/07_Graphs) topic. This topic is the problem set: spotting the graph, building it, cloning it, flood fills, multi-source spreading, two-colouring, a memoised path on a DAG, bidirectional word search, union-find, prerequisites, Dijkstra, and spanning trees. The two decisions are what a node and an edge are, and which question the problem asks.

## Key Points

- **Spotting a graph** — decide what a node and an edge are. Grids, word puzzles, lock states, and dependencies are graphs. Traversals cost O(n + e).
- **Building an adjacency list** — one pass over the edge list, both directions for undirected edges. Seed isolated nodes. Generate grid neighbours on the fly.
- **Clone a graph** — a dict from original to copy is both the visited set and the copy lookup. Register the copy before visiting neighbours. O(n + e).
- **Count islands** — scan every cell and start a fill from unclaimed land. Ask before overwriting the input and avoid deep recursion. O(m × n).
- **Spread from many sources** — queue every source at level 0 and count BFS levels. Track the remaining healthy cells and return −1 if any are left.
- **Two-colour check** — colour neighbours opposite colours and fail on a same-colour edge. Start from every uncoloured node. An odd cycle means not bipartite.
- **Longest increasing path in a grid** — strictly increasing steps form a DAG, so memoise and drop the visited set. O(m × n).
- **Word ladder with bidirectional BFS** — generate neighbours by trying 26 letters per position and expand the smaller frontier. Count words, not edges.
- **Union-find for merging groups** — union by size and path compression give near-O(1) operations. Keep sizes at roots and skip merges within one group.
- **Prerequisites and topological order** — Kahn's algorithm: in-degrees and a queue. All n nodes processed means no cycle and a valid order.
- **Dijkstra for weighted distances** — a min-heap of `(distance, node)` and skip stale entries. Non-negative weights only. O((n + e) log n).
- **Minimum spanning tree** — Kruskal sorts edges and joins with union-find until n − 1 edges. Array-based Prim's is O(n²) for complete graphs.
- **Choosing a graph algorithm** — reach or group: DFS/BFS; fewest steps: BFS; cheapest path: Dijkstra; order: topological sort; growing connectivity: union-find; cheapest network: MST.

## Example

```python
from collections import deque


def bfs_steps(graph: dict[str, list[str]], start: str) -> dict[str, int]:
    steps = {start: 0}
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for nb in graph[node]:
            if nb not in steps:
                steps[nb] = steps[node] + 1
                queue.append(nb)
    return steps


graph = {
    "home": ["park", "shop"],
    "park": ["home", "lake"],
    "shop": ["home", "lake", "school"],
    "lake": ["park", "shop"],
    "school": ["shop"],
    "island": [],
}
print(bfs_steps(graph, "home"))
print("island" in bfs_steps(graph, "home"))
# {'home': 0, 'park': 1, 'shop': 1, 'lake': 2, 'school': 2}
# False
```

The dict of steps is both the answer and the visited set, and each node is marked when it is queued, so it is queued once. `island` has no edges and never appears, which is the case a disconnected graph adds. All places are exercise names.

## More practice

Work the original exercises on the **Drills** tab. Each one names the rule, the cost, and a Python check.
