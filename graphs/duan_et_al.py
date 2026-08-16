import heapq
import math
import bisect
from collections import defaultdict
from graphs.graphs import Graph, dijkstra

INF = float('inf')


# =============================================================================
# BatchPQ — estrutura D fiel ao Lema 3.3
# =============================================================================

class _Block:
    def __init__(self):
        self.items: list[tuple[float, object]] = []
        self.upper: float = INF

    def push_sorted(self, pairs):
        self.items = pairs
        self.upper = pairs[-1][0] if pairs else INF

    def split(self) -> "_Block":
        mid = len(self.items) // 2
        right = _Block()
        right.push_sorted(self.items[mid:])
        self.push_sorted(self.items[:mid])
        return right

    def __len__(self):
        return len(self.items)


class BatchPQ:
    """
    Estrutura de dados D do Lema 3.3.

    Parâmetros
    ----------
    M : int   — tamanho de bloco e quantidade de itens por Pull
    B : float — upper-bound global (retornado pelo Pull quando vazio)
    """

    def __init__(self, M: int, B: float):
        assert M >= 1
        self.M = M
        self.B = B
        self._d0: list[_Block] = []   # blocos de BatchPrepend
        self._d1: list[_Block] = []   # blocos de Insert
        self._key_val: dict = {}       # key -> menor val atualmente na estrutura

    # ------------------------------------------------------------------
    def insert(self, key, val: float):
        """Insert: O(max{1, log(N/M)}) amortizado."""
        if key in self._key_val and val >= self._key_val[key]:
            return
        self._key_val[key] = val
        block = self._find_or_create_d1_block(val)
        block.items.append((val, key))
        block.items.sort(key=lambda p: p[0])
        block.upper = block.items[-1][0]
        if len(block) > self.M:
            self._split_d1_block(block)

    def _find_or_create_d1_block(self, val: float) -> _Block:
        uppers = [b.upper for b in self._d1]
        idx = bisect.bisect_left(uppers, val)
        if idx < len(self._d1):
            return self._d1[idx]
        b = _Block()
        b.upper = self.B
        self._d1.append(b)
        return b

    def _split_d1_block(self, block: _Block):
        idx = self._d1.index(block)
        right = block.split()
        self._d1.insert(idx + 1, right)

    # ------------------------------------------------------------------
    def batch_prepend(self, pairs: list[tuple[object, float]]):
        """BatchPrepend: O(|L| · max{1, log(|L|/M)}) amortizado."""
        if not pairs:
            return
        deduped: dict = {}
        for key, val in pairs:
            if key not in deduped or val < deduped[key]:
                deduped[key] = val
        filtered = []
        for key, val in deduped.items():
            if key in self._key_val and val >= self._key_val[key]:
                continue
            self._key_val[key] = val
            filtered.append((val, key))
        if not filtered:
            return
        filtered.sort(key=lambda p: p[0])
        L = len(filtered)
        if L <= self.M:
            b = _Block()
            b.push_sorted(filtered)
            self._d0.insert(0, b)
        else:
            chunk = max(1, self.M // 2)
            new_blocks = []
            for i in range(0, L, chunk):
                b = _Block()
                b.push_sorted(filtered[i: i + chunk])
                new_blocks.append(b)
            self._d0[0:0] = new_blocks

    # ------------------------------------------------------------------
    def pull(self) -> tuple[float, list]:
        """Pull: retorna (x, S') com |S'| ≤ M."""
        candidates = []
        self._collect_prefix(self._d0, candidates, self.M)
        self._collect_prefix(self._d1, candidates, self.M)
        if not candidates:
            return self.B, []
        candidates.sort(key=lambda p: p[0])
        valid = []
        seen = set()
        for val, key in candidates:
            if key in seen:
                continue
            seen.add(key)
            if self._key_val.get(key, INF) < val:
                continue   # lazy deletion
            valid.append((val, key))
            if len(valid) == self.M:
                break
        if not valid:
            return self.B, []
        pulled_keys = {key for _, key in valid}
        self._remove_keys(pulled_keys)
        for key in pulled_keys:
            del self._key_val[key]
        x = self._min_remaining_val()
        return x, [key for _, key in valid]

    def _collect_prefix(self, seq, out, limit):
        collected = 0
        for block in seq:
            for pair in block.items:
                out.append(pair)
                collected += 1
            if collected >= limit:
                break

    def _remove_keys(self, keys: set):
        for seq in (self._d0, self._d1):
            for block in seq:
                block.items = [(v, k) for v, k in block.items if k not in keys]
                if block.items:
                    block.upper = block.items[-1][0]
        self._d0 = [b for b in self._d0 if b.items]
        self._d1 = [b for b in self._d1 if b.items]

    def _min_remaining_val(self) -> float:
        mins = []
        if self._d0 and self._d0[0].items:
            mins.append(self._d0[0].items[0][0])
        if self._d1 and self._d1[0].items:
            mins.append(self._d1[0].items[0][0])
        return min(mins) if mins else self.B

    def is_empty(self) -> bool:
        return not self._key_val

# =============================================================================
# base_case (Algoritmo 2) — inalterado
# =============================================================================

def base_case(graph, s, B, db, k):
    U0 = set()
    heap = [(db[s], s)]
    while heap and len(U0) < k + 1:
        dist_u, u = heapq.heappop(heap)
        if u in U0:
            continue
        U0.add(u)
        for v, w in graph.adj[u]:
            nova = db[u] + w
            if nova <= db[v] and nova < B:
                db[v] = nova
                heapq.heappush(heap, (db[v], v))
    if len(U0) <= k:
        return B, U0
    B_prime = max(db[v] for v in U0)
    U = {v for v in U0 if db[v] < B_prime}
    return B_prime, U


# =============================================================================
# find_pivots (Algoritmo 1) — inalterado
# =============================================================================

def find_pivots(graph, S, B, db, k):
    W = set(S)
    Wi_prev = set(S)
    for i in range(k):
        Wi = set()
        for u in Wi_prev:
            for v, w in graph.adj[u]:
                nova = db[u] + w
                if nova <= db[v]:
                    db[v] = nova
                    if db[v] < B:
                        Wi.add(v)
        W |= Wi
        Wi_prev = Wi
        if len(W) > k * len(S):
            return set(S), W
    parent = {}
    for u in W:
        for v, w in graph.adj[u]:
            if v in W and db[u] + w == db[v]:
                parent[v] = u
    roots = {u for u in S if u not in parent}

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
        if count_subtree(u) >= k:
            P.add(u)
    return P, W


# =============================================================================
# BMSSP (Algoritmo 3) — 3 linhas alteradas, marcadas com "# ALTERADO"
# =============================================================================

def BMSSP(graph, l, B, S, db, k, t):

    if l == 0:
        return base_case(graph, next(iter(S)), B, db, k)

    P, W = find_pivots(graph, S, B, db, k)

    M = 2 ** ((l - 1) * t)

    # ALTERADO: BatchPQ recebe M e B no construtor (era SimpleD())
    D = BatchPQ(M=M, B=B)

    for x in P:
        D.insert(x, db[x])

    B_prime = min((db[x] for x in P), default=B)
    U = set()

    # ALTERADO: is_empty() no lugar de empty()
    while len(U) < (k ** 2) * (2 ** (l * t)) and not D.is_empty():

        # ALTERADO: pull() sem argumento (M já está no construtor)
        Bi, Si = D.pull()

        if not Si:
            break

        B_i_prime, Ui = BMSSP(graph, l - 1, Bi, set(Si), db, k, t)

        U |= Ui

        K = []
        for u in Ui:
            for v, w in graph.adj[u]:
                nova = db[u] + w
                if nova <= db[v]:
                    db[v] = nova
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
    return B_prime, U


# =============================================================================
# sssp_duan_et_al — inalterado
# =============================================================================

def sssp_duan_et_al(graph, source):
    db = defaultdict(lambda: INF)
    db[source] = 0
    n = len(graph.adj)
    k = max(2, int(math.log2(n) ** (1 / 3))) if n > 1 else 2
    t = max(2, int(math.log2(n) ** (2 / 3))) if n > 1 else 2
    l = int(math.log2(n) / t) + 1 if n > 1 else 1
    BMSSP(graph, l, INF, {source}, db, k, t)
    return dict(db)


# =============================================================================
# Teste de regressão: compara BMSSP com Dijkstra no grafo original do paper
# =============================================================================

if __name__ == "__main__":
    g = Graph()
    g.add_edge('A', 'B', 1.5);  g.add_edge('A', 'C', 2.0);  g.add_edge('A', 'E', 2.8)
    g.add_edge('B', 'D', 3.0);  g.add_edge('B', 'F', 1.7)
    g.add_edge('C', 'D', 1.2);  g.add_edge('C', 'F', 2.5);  g.add_edge('C', 'G', 3.1)
    g.add_edge('D', 'H', 2.2)
    g.add_edge('E', 'F', 1.1);  g.add_edge('E', 'I', 2.9)
    g.add_edge('F', 'H', 1.4);  g.add_edge('F', 'J', 2.6)
    g.add_edge('G', 'J', 1.3)
    g.add_edge('H', 'K', 2.0)
    g.add_edge('I', 'J', 1.8)
    g.add_edge('J', 'K', 1.5);  g.add_edge('J', 'L', 2.7)
    g.add_edge('K', 'M', 1.9)
    g.add_edge('L', 'M', 2.3)
    g.adj['M'] = []

    source = 'A'
    result_bmssp    = sssp_duan_et_al(g, source)
    result_dijkstra = dijkstra(g, source)

    print("Comparação BMSSP vs Dijkstra:")
    all_ok = True
    for v in sorted(result_dijkstra):
        bv = result_bmssp.get(v, INF)
        dv = result_dijkstra[v]
        ok = abs(bv - dv) < 1e-9
        if not ok:
            all_ok = False
        print(f"  {v}: BMSSP={bv:.4f}  Dijkstra={dv:.4f}  {'OK' if ok else 'ERRO'}")

    print()
    if all_ok:
        print("Todos os vértices corretos.")
    else:
        print("FALHOU em algum vértice.")