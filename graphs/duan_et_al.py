import heapq
from collections import defaultdict
import logging
from graphs.graphs import Graph, dijkstra
from utils.logger import IndentLogger

INF = float('inf')
logger = IndentLogger(logging.INFO)

# =========================
# Base Case (Algoritmo 2)
# =========================
def base_case(graph, s, B, db, k):

    with logger.section(f"BASE_CASE(s={s}, B={B})"):

        U0 = set()
        heap = [(db[s], s)]

        while heap and len(U0) < k + 1:

            dist_u, u = heapq.heappop(heap)

            logger.debug(f"Heap pop ({dist_u}, {u})")

            if u in U0:
                continue

            U0.add(u)

            for v, w in graph.adj[u]:

                nova = db[u] + w

                logger.debug(
                    f"{u}->{v} peso={w} nova={nova}"
                )

                if nova <= db[v] and nova < B:
                    db[v] = nova
                    heapq.heappush(heap, (db[v], v))

                    logger.debug(f"Relaxou {v}")

        logger.debug(f"U0={U0}")

        if len(U0) <= k:
            return B, U0

        B_prime = max(db[v] for v in U0)
        U = {v for v in U0 if db[v] < B_prime}

        return B_prime, U


# =========================
# FindPivots (Algoritmo 1)
# =========================
def find_pivots(graph, S, B, db, k):

    with logger.section(f"FIND_PIVOTS(S={S}, B={B}, k={k})"):

        W = set(S)
        Wi_prev = set(S)

        for i in range(k):

            logger.debug(f"iteração {i}")

            Wi = set()

            for u in Wi_prev:
                for v, w in graph.adj[u]:

                    nova = db[u] + w

                    logger.debug(
                        f"{u}->{v} peso={w} nova={nova} atual={db[v]}"
                    )

                    if nova <= db[v]:
                        db[v] = nova

                        if db[v] < B:
                            Wi.add(v)
                            logger.debug(f"{v} entrou em Wi")

            W |= Wi
            Wi_prev = Wi

            logger.debug(f"W parcial = {W}")

            if len(W) > k * len(S):
                logger.debug("corte antecipado")
                return set(S), W

        parent = {}

        for u in W:
            for v, w in graph.adj[u]:
                if v in W and db[u] + w == db[v]:
                    parent[v] = u

        logger.debug(f"parent = {parent}")

        roots = {u for u in S if u not in parent}
        logger.debug(f"roots = {roots}")

        def count_subtree(root):
            count = 0
            stack = [root]
            visited = set()

            while stack:
                x = stack.pop()

                if x in visited:
                    continue

                visited.add(x)
                count += 1

                for v, w in graph.adj[x]:
                    if v in W and parent.get(v) == x:
                        stack.append(v)

            return count

        P = set()

        for u in roots:
            tam = count_subtree(u)

            logger.debug(f"subárvore {u} tamanho={tam}")

            if tam >= k:
                P.add(u)

        logger.debug(f"Pivots = {P}")
        logger.debug(f"W final = {W}")

        return P, W

# =========================
# Estrutura D simplificada
# =========================
class SimpleD:
    def __init__(self):
        self.data = []

    def insert(self, v, val):
        logger.debug(f"D.insert ({val}, {v})")
        heapq.heappush(self.data, (val, v))

    def batch_prepend(self, items):
        logger.debug(f"D.batch_prepend {items}")

        for v, val in items:
            heapq.heappush(self.data, (val, v))

    def pull(self, M):

        logger.debug(f"D.pull M={M}")

        S = []

        for _ in range(min(M, len(self.data))):
            val, v = heapq.heappop(self.data)

            logger.debug(f"D.pop ({val}, {v})")

            S.append(v)

        x = self.data[0][0] if self.data else INF

        logger.debug(f"D.ret x={x}, S={S}")

        return x, S

    def empty(self):
        vazio = len(self.data) == 0
        logger.debug(f"D.empty? {vazio}")
        return vazio


# =========================
# BMSSP (Algoritmo 3)
# =========================
def BMSSP(graph, l, B, S, db, k, t):

    with logger.section(f"BMSSP(l={l}, B={B}, S={S})"):

        if l == 0:
            logger.debug("Caso base")
            return base_case(graph, next(iter(S)), B, db, k)

        P, W = find_pivots(graph, S, B, db, k)

        logger.debug(f"Pivots = {P}")
        logger.debug(f"W = {W}")

        D = SimpleD()
        M = 2 ** ((l - 1) * t)

        logger.debug(f"M = {M}")

        for x in P:
            D.insert(x, db[x])

        B_prime = min((db[x] for x in P), default=B)

        U = set()

        while len(U) < (k**2) * (2 ** (l * t)) and not D.empty():

            logger.debug(f"Loop principal | U={U}")

            Bi, Si = D.pull(M)

            logger.debug(f"Pull -> Bi={Bi}, Si={Si}")

            if not Si:
                logger.debug("Si vazio")
                break

            B_i_prime, Ui = BMSSP(
                graph,
                l - 1,
                Bi,
                set(Si),
                db,
                k,
                t
            )

            logger.debug(f"Retorno recursão -> B'={B_i_prime}, Ui={Ui}")

            U |= Ui

            K = []

            for u in Ui:
                for v, w in graph.adj[u]:

                    nova = db[u] + w

                    logger.debug(
                        f"Testando {u}->{v} | nova={nova} atual={db[v]}"
                    )

                    if nova <= db[v]:
                        db[v] = nova

                        logger.debug(
                            f"Relaxou {v} = {db[v]}"
                        )

                        if Bi <= db[v] < B:
                            D.insert(v, db[v])

                        elif B_i_prime <= db[v] < Bi:
                            K.append((v, db[v]))

            prepend_items = K + [
                (x, db[x]) for x in Si
                if B_i_prime <= db[x] < Bi
            ]

            D.batch_prepend(prepend_items)

            B_prime = min(B_i_prime, B)

        U |= {x for x in W if db[x] < B_prime}

        logger.debug(f"Saída final -> B'={B_prime}, U={U}")

        return B_prime, U


# =========================
# SSSP principal
# =========================
def sssp_duan_et_al(graph, source):

    with logger.section(f"Grafo"):
        for edge in graph.representation():
            logger.debug(edge)

    with logger.section(f"SSSP(source={source})"):

        db = defaultdict(lambda: INF)
        db[source] = 0

        import math

        n = len(graph.adj)

        k = max(2, int(math.log(n) ** (1/3))) if n > 1 else 2
        t = max(2, int(math.log(n) ** (2/3))) if n > 1 else 2
        l = int(math.log(n) / t) + 1 if n > 1 else 1

        logger.debug(f"n={n}")
        logger.debug(f"k={k}")
        logger.debug(f"t={t}")
        logger.debug(f"l={l}")

        BMSSP(graph, l, INF, {source}, db, k, t)

        logger.debug(f"distâncias finais = {dict(db)}")

        return dict(db)

# =========================
# TESTE PRINCIPAL
# =========================
if __name__ == "__main__":
    g = Graph()

    g.add_edge('A', 'B', 1.5)
    g.add_edge('A', 'C', 2.0)
    g.add_edge('A', 'E', 2.8)

    g.add_edge('B', 'D', 3.0)
    g.add_edge('B', 'F', 1.7)

    g.add_edge('C', 'D', 1.2)
    g.add_edge('C', 'F', 2.5)
    g.add_edge('C', 'G', 3.1)

    g.add_edge('D', 'H', 2.2)

    g.add_edge('E', 'F', 1.1)
    g.add_edge('E', 'I', 2.9)

    g.add_edge('F', 'H', 1.4)
    g.add_edge('F', 'J', 2.6)

    g.add_edge('G', 'J', 1.3)

    g.add_edge('H', 'K', 2.0)

    g.add_edge('I', 'J', 1.8)

    g.add_edge('J', 'K', 1.5)
    g.add_edge('J', 'L', 2.7)

    g.add_edge('K', 'M', 1.9)

    g.add_edge('L', 'M', 2.3)

    g.adj['M'] = []

    source = 'A'

    print("Rodando BMSSP...")
    result_bmssp = sssp_duan_et_al(g, source)

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