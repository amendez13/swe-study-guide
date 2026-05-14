# Graphs

Graphs are the most general structure for modeling relationships between entities. A graph consists of vertices (nodes) connected by edges, and unlike trees, graphs can have cycles, disconnected components, and no root. Mastering graph representations and traversal algorithms is essential because graphs appear everywhere in engineering: network routing, dependency resolution, social networks, recommendation engines, and scheduling problems. The two core traversals, DFS and BFS, are the building blocks for nearly every graph algorithm, and knowing when to apply Dijkstra's versus a simple BFS can mean the difference between a correct solution and a wrong one.

## Key Points

- **Graphs generalize trees** - A tree is a connected acyclic undirected graph; a graph lifts all three constraints, allowing cycles, disconnected components, and directed edges.
- **Directed vs. undirected determines edge semantics** - Undirected edges imply bidirectional traversal; directed edges are one-way. Directed graphs require separate in-degree and out-degree tracking and change how reachability works.
- **Weighted edges require different algorithms** - BFS finds shortest paths only in unweighted graphs; weighted graphs need Dijkstra's (non-negative weights) or Bellman-Ford (allows negative weights).
- **Adjacency list is the default representation** - O(V + E) space, efficient neighbor iteration, and works well for sparse graphs. Use an adjacency matrix (O(V^2) space, O(1) edge lookup) only for dense graphs or matrix-based algorithms.
- **Always track visited nodes** - Without a visited set, traversals on cyclic graphs loop forever. This is the single most common graph algorithm bug.
- **DFS explores depth-first using a stack** - Recursion or an explicit stack. Used for cycle detection, topological sort, connected components, and path existence. O(V + E) time, O(V) space.
- **BFS explores breadth-first using a queue** - Guarantees shortest path in unweighted graphs. Used for shortest paths, level-order traversal, and minimum-step problems. O(V + E) time, O(V) space.
- **Bidirectional BFS reduces exponential search** - Two BFS frontiers from source and destination meet in the middle, reducing O(k^d) to O(k^(d/2)). Requires knowing the destination and traversing edges in reverse.
- **Topological sort linearizes a DAG** - Produces an ordering where every edge goes from earlier to later. Essential for dependency resolution, build systems, and task scheduling. Only valid on acyclic directed graphs.
- **Dijkstra's uses a min-heap for weighted shortest paths** - Greedily finalizes the nearest unvisited vertex, then relaxes its neighbors. O((V + E) log V) with a binary heap. Fails with negative edge weights.
- **DAGs have no cycles and enable topological ordering** - Every DAG has at least one topological sort. If Kahn's algorithm processes fewer than V vertices, the graph contains a cycle.
- **Graph problems hide in many interview questions** - Any problem involving states and transitions, dependencies, or "minimum steps to reach X" is likely a graph problem even if the word "graph" never appears.

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
# Dijkstra from A: {'A': 0, 'C': 2, 'B': 3, 'D': 6, 'E': 8}
```

This single `Graph` class covers the four most important graph operations. In interviews, you rarely need the full class -- a plain `defaultdict(list)` as the adjacency list and standalone DFS/BFS functions are usually sufficient. The class form is useful for studying because it makes the relationship between representation and algorithm explicit.
