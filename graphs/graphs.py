import heapq
import random
from collections import defaultdict, deque

class Graph:
    def __init__(self):
        self.adj = defaultdict(list)

    def add_edge(self, u, v, w):
        self.adj[u].append((v, w))

    # para debug: imprime o grafo
    def representation(self):
        result = []
        for u in self.adj:
            for v, w in self.adj[u]:
                result.append(f"{u} --({w})--> {v}")
        return result

def dijkstra(graph, source):
    INF = float('inf')

    # pega todos os vértices (origem + destinos)
    vertices = set(graph.adj.keys())
    for u in graph.adj:
        for v, _ in graph.adj[u]:
            vertices.add(v)

    dist = {v: INF for v in vertices}
    dist[source] = 0

    pq = [(0, source)]

    while pq:
        dist_u, u = heapq.heappop(pq)

        if dist_u > dist[u]:
            continue

        for v, w in graph.adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(pq, (dist[v], v))

    return dist

def bellman_ford(graph, source):
    INF = float('inf')

    # todos os vértices (inclui folhas)
    vertices = set(graph.adj.keys())
    for u in graph.adj:
        for v, _ in graph.adj[u]:
            vertices.add(v)

    dist = {v: INF for v in vertices}
    dist[source] = 0

    n = len(vertices)

    for _ in range(n - 1):
        changed = False

        for u in graph.adj:
            for v, w in graph.adj[u]:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
                    changed = True

        if not changed:
            break

    return dist

def generate_random_graph(num_vertices, edge_probability):
    g = Graph()
    for u in range(num_vertices):
        for v in range(num_vertices):
            if u != v and random.random() < edge_probability:
                w = random.randint(1, 10)
                g.add_edge(u, v, w)
    return g

def is_fully_reachable(graph, source, num_vertices):
    """Retorna True se todos os vértices são alcançáveis a partir de source."""
    visited = {source}
    queue = deque([source])

    while queue:
        u = queue.popleft()
        for v, _ in graph.adj[u]:
            if v not in visited:
                visited.add(v)
                queue.append(v)

    return len(visited) == num_vertices