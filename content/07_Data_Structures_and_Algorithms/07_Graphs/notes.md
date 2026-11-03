# Graphs

Graphs are the most general structure for modeling relationships between entities. A graph consists of vertices (nodes) connected by edges, and unlike trees, graphs can have cycles, disconnected components, and no root. Mastering graph representations and traversal algorithms is essential because graphs appear everywhere in engineering: network routing, dependency resolution, social networks, recommendation engines, and scheduling problems. The two core traversals, DFS and BFS, are the building blocks for nearly every graph algorithm, and knowing when to apply Dijkstra's versus a simple BFS can mean the difference between a correct solution and a wrong one.

## Key Points

- **Graph basics** - Vertices plus edges with no root and no hierarchy; cycles and separate pieces are allowed. Degrees in an undirected graph sum to 2E; a tree is a connected acyclic graph with V - 1 edges.
- **Directed vs. undirected** - Directed edges are one-way, so in-degree and out-degree differ and reachability is not symmetric. Store an undirected edge in both directions.
- **Weighted vs. unweighted** - BFS counts hops and is only correct when every edge costs the same; weights call for Dijkstra (non-negative) or Bellman-Ford (negative).
- **Adjacency list** - The default: O(V + E) space, O(degree) neighbor scan. Use neighbor sets for O(1) edge checks and keep sink vertices as keys.
- **Adjacency matrix** - O(V^2) space, O(1) edge check, O(V) neighbor scan. Good for dense or small graphs and Floyd-Warshall.
- **Edge lists and implicit graphs** - Build the adjacency list from pairs in O(V + E), or generate neighbors on demand for grids and "states plus moves" puzzles.
- **Visited set** - Every traversal needs one; it is what makes BFS and DFS O(V + E). In BFS mark on enqueue, not on dequeue.
- **Depth-first search (DFS)** - Stack or recursion, deep before wide; O(V + E) time, O(V) space. Watch Python's recursion limit on long paths and big grids.
- **Breadth-first search (BFS)** - FIFO queue (`deque`), ring by ring from the start; O(V + E) time, and the queue can hold a whole layer.
- **BFS shortest path** - First arrival is a fewest-edges route; keep `dist` and one `parent` pointer per vertex, then walk parents back to rebuild the path.
- **Multi-source BFS** - Seed the queue with every source at distance 0 to get distance-to-nearest for all vertices in one O(V + E) pass.
- **Bidirectional search** - BFS from both ends, one layer at a time; about 2 * k^(d/2) work instead of k^d. Needs a known goal and reverse edges.
- **Connected components** - Start a traversal from every unvisited vertex; each start is a new component. SCCs are the directed version (Tarjan or Kosaraju, O(V + E)).
- **Cycle detection** - Undirected: DFS with a parent check (or union-find). Directed: three colors; an edge into a gray (on-path) vertex is a back edge.
- **Bipartite check** - BFS 2-coloring; an edge between same-colored vertices means an odd cycle and no valid split.
- **Topological sort** - Linear order of a DAG with every edge pointing forward. Kahn (in-degree queue, detects cycles) or reversed DFS post-order, both O(V + E).
- **Dijkstra's algorithm** - Min-heap of `(dist, vertex)`, settle the closest, relax edges, skip stale entries. O((V + E) log V); breaks on negative edges.
- **Choosing a shortest-path algorithm** - BFS for unweighted, 0-1 BFS for 0/1 weights, Dijkstra for non-negative, Bellman-Ford for negative, topological relaxation for DAGs, Floyd-Warshall for small all-pairs.
- **Union-find** - Near-constant `find` and `union` with path compression and union by size; answers "same group?" as edges stream in, and the first failed union closes a cycle.

## Example

```python
"""
Complete graph toolkit: build a weighted directed graph, run DFS, BFS,
topological sort, and Dijkstra's shortest path.
"""
import heapq
from collections import defaultdict, deque


class Graph:
    def __init__(self, directed: bool = True):
        self.directed = directed
        self.adj: dict[str, list[tuple[str, int]]] = defaultdict(list)

    def add_edge(self, src: str, dst: str, weight: int = 1) -> None:
        self.adj[src].append((dst, weight))
        if not self.directed:
            self.adj[dst].append((src, weight))
        # Ensure all vertices appear as keys
        if dst not in self.adj:
            self.adj[dst] = []

    def dfs(self, start: str) -> list[str]:
        """Recursive DFS returning visit order."""
        visited: set[str] = set()
        order: list[str] = []

        def explore(v: str) -> None:
            visited.add(v)
            order.append(v)
            for neighbor, _ in self.adj[v]:
                if neighbor not in visited:
                    explore(neighbor)

        explore(start)
        return order

    def bfs(self, start: str) -> list[str]:
        """BFS returning visit order."""
        visited: set[str] = {start}
        order: list[str] = []
        queue: deque[str] = deque([start])

        while queue:
            v = queue.popleft()
            order.append(v)
            for neighbor, _ in self.adj[v]:
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(neighbor)

        return order

    def topological_sort(self) -> list[str]:
        """Kahn's algorithm. Raises ValueError on cycle."""
        in_deg: dict[str, int] = {v: 0 for v in self.adj}
        for v in self.adj:
            for nb, _ in self.adj[v]:
                in_deg[nb] += 1

        queue = deque(v for v in self.adj if in_deg[v] == 0)
        order: list[str] = []

        while queue:
            v = queue.popleft()
            order.append(v)
            for nb, _ in self.adj[v]:
                in_deg[nb] -= 1
                if in_deg[nb] == 0:
                    queue.append(nb)

        if len(order) != len(self.adj):
            raise ValueError("Graph has a cycle -- topological sort impossible")
        return order

    def dijkstra(self, start: str) -> dict[str, int]:
        """Shortest distances from start (non-negative weights)."""
        dist: dict[str, float] = {v: float("inf") for v in self.adj}
        dist[start] = 0
        heap: list[tuple[float, str]] = [(0, start)]

        while heap:
            d, u = heapq.heappop(heap)
            if d > dist[u]:
                continue
            for nb, w in self.adj[u]:
                nd = d + w
                if nd < dist[nb]:
                    dist[nb] = nd
                    heapq.heappush(heap, (nd, nb))

        return {v: int(d) for v, d in dist.items() if d != float("inf")}


# --- Build and explore a graph ---

g = Graph(directed=True)
g.add_edge("A", "B", 4)
g.add_edge("A", "C", 2)
g.add_edge("B", "D", 3)
g.add_edge("C", "B", 1)
g.add_edge("C", "D", 5)
g.add_edge("D", "E", 2)

print("DFS from A:", g.dfs("A"))
# DFS from A: ['A', 'B', 'D', 'E', 'C']

print("BFS from A:", g.bfs("A"))
# BFS from A: ['A', 'B', 'C', 'D', 'E']

print("Topological order:", g.topological_sort())
# Topological order: ['A', 'C', 'B', 'D', 'E']

print("Dijkstra from A:", g.dijkstra("A"))
# Dijkstra from A: {'A': 0, 'B': 3, 'C': 2, 'D': 6, 'E': 8}
```

This single `Graph` class covers the four most important graph operations. In interviews, you rarely need the full class -- a plain `defaultdict(list)` as the adjacency list and standalone DFS/BFS functions are usually sufficient. The class form is useful for studying because it makes the relationship between representation and algorithm explicit.

## More practice

Work the original exercises on the **Drills** tab: read each prompt, commit to an answer, then open the card to check it. For background reading, open CTCI Chapter 4 on the private reader under `#graphs` (with `#adjacency-list` and `#adjacency-matrices`) and `#graph-search` (with `#depth-first-search-dfs`, `#breadth-first-search-bfs`, and `#bidirectional-search`), plus the Advanced Topics sections `#topological-sort` and `#dijkstras-algorithm`. Tree, heap, and trie sections of that chapter belong to the Trees and Heaps and Tries topics. Do not copy book text or solutions into these study files.
