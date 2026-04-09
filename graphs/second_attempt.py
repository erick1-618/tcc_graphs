import heapq
from collections import defaultdict

INF = float('inf')


class Graph:
    def __init__(self):
        self.adj = defaultdict(list)

    def add_edge(self, u, v, w):
        self.adj[u].append((v, w))


# =========================
# Base Case (Algoritmo 2)
# =========================
def base_case(graph, s, B, db, k):
    U0 = set()
    heap = [(db[s], s)]

    while heap and len(U0) < k + 1:
        dist_u, u = heapq.heappop(heap)

        if u in U0:
            continue

        U0.add(u)

        for v, w in graph.adj[u]:
            if db[u] + w <= db[v] and db[u] + w < B:
                db[v] = db[u] + w
                heapq.heappush(heap, (db[v], v))

    if len(U0) <= k:
        return B, U0
    else:
        B_prime = max(db[v] for v in U0)
        U = {v for v in U0 if db[v] < B_prime}
        return B_prime, U


# =========================
# FindPivots (Algoritmo 1)
# =========================
def find_pivots(graph, S, B, db, k):
    W = set(S)
    Wi_prev = set(S)

    for _ in range(k):
        Wi = set()

        for u in Wi_prev:
            for v, w in graph.adj[u]:
                if db[u] + w <= db[v]:
                    db[v] = db[u] + w

                    if db[v] < B:
                        Wi.add(v)

        W |= Wi
        Wi_prev = Wi

        if len(W) > k * len(S):
            return set(S), W

    # Construir floresta F implicitamente
    # Aqui simplificamos: escolhemos pivôs como subset heurístico
    P = set()

    for u in S:
        count = 0
        stack = [u]

        visited = set()

        while stack:
            x = stack.pop()
            if x in visited:
                continue
            visited.add(x)
            count += 1

            for v, w in graph.adj[x]:
                if db[v] == db[x] + w:
                    stack.append(v)

        if count >= k:
            P.add(u)

    return P, W


# =========================
# Estrutura D simplificada
# =========================
class SimpleD:
    def __init__(self):
        self.data = []

    def insert(self, v, val):
        heapq.heappush(self.data, (val, v))

    def batch_prepend(self, items):
        for v, val in items:
            heapq.heappush(self.data, (val, v))

    def pull(self, M):
        S = []
        for _ in range(min(M, len(self.data))):
            val, v = heapq.heappop(self.data)
            S.append(v)

        if self.data:
            x = self.data[0][0]
        else:
            x = INF

        return x, S

    def empty(self):
        return len(self.data) == 0


# =========================
# BMSSP (Algoritmo 3)
# =========================
def BMSSP(graph, l, B, S, db, k, t):
    if l == 0:
        s = next(iter(S))
        return base_case(graph, s, B, db, k)

    P, W = find_pivots(graph, S, B, db, k)

    D = SimpleD()
    M = 2 ** ((l - 1) * t)

    for x in P:
        D.insert(x, db[x])

    if P:
        B_prime_0 = min(db[x] for x in P)
    else:
        B_prime_0 = B

    U = set()
    B_prime = B_prime_0

    while len(U) < (k**2) * (2 ** (l * t)) and not D.empty():
        Bi, Si = D.pull(M)

        if not Si:
            break

        B_i_prime, Ui = BMSSP(graph, l - 1, Bi, set(Si), db, k, t)

        U |= Ui

        K = []

        for u in Ui:
            for v, w in graph.adj[u]:
                if db[u] + w <= db[v]:
                    db[v] = db[u] + w

                    if Bi <= db[v] < B:
                        D.insert(v, db[v])
                    elif B_i_prime <= db[v] < Bi:
                        K.append((v, db[v]))

        prepend_items = K + [(x, db[x]) for x in Si if B_i_prime <= db[x] < Bi]
        D.batch_prepend(prepend_items)

        B_prime = min(B_i_prime, B)

    U |= {x for x in W if db[x] < B_prime}

    return B_prime, U


# =========================
# SSSP principal
# =========================
def sssp(graph, source):
    db = defaultdict(lambda: INF)
    db[source] = 0

    import math

    n = len(graph.adj)
    k = int(math.log(n) ** (1/3)) if n > 1 else 1
    t = int(math.log(n) ** (2/3)) if n > 1 else 1

    l = int(math.log(n) / t) + 1 if n > 1 else 1

    BMSSP(graph, l, INF, {source}, db, k, t)

    return dict(db)

def dijkstra(graph, source):
    import heapq
    INF = float('inf')

    dist = {v: INF for v in graph.adj}
    dist[source] = 0

    heap = [(0, source)]

    while heap:
        d, u = heapq.heappop(heap)

        if d > dist[u]:
            continue

        for v, w in graph.adj[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                heapq.heappush(heap, (dist[v], v))

    return dist

# =========================
# TESTE PRINCIPAL
# =========================
if __name__ == "__main__":
    g = Graph()

    # Grafo de exemplo
    edges = [
        ('A', 'B', 1),
        ('A', 'C', 4),
        ('B', 'C', 2),
        ('B', 'D', 5),
        ('C', 'D', 1),
        ('D', 'E', 3),
        ('C', 'E', 7)
    ]

    for u, v, w in edges:
        g.add_edge(u, v, w)

    source = 'A'

    print("Rodando BMSSP...")
    result_bmssp = sssp(g, source)

    print("\nRodando Dijkstra...")
    result_dijkstra = dijkstra(g, source)

    print("\nResultados BMSSP:")
    for k in sorted(result_bmssp):
        print(f"{k}: {result_bmssp[k]}")

    print("\nResultados Dijkstra:")
    for k in sorted(result_dijkstra):
        print(f"{k}: {result_dijkstra[k]}")

    print("\nComparação:")
    for v in result_dijkstra:
        if abs(result_bmssp[v] - result_dijkstra[v]) > 1e-6:
            print(f"ERRO em {v}: BMSSP={result_bmssp[v]}, Dijkstra={result_dijkstra[v]}")
        else:
            print(f"{v}: OK")