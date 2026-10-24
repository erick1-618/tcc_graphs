"""BMSSP otimizado (BMSSP-Opt).

Mesmo algoritmo das versões recursiva/iterativa, mas com estruturas de dados
mais eficientes no Python:

* vértices renomeados para inteiros densos 0..N-1 (a renomeação faz parte do
  tempo medido, assim como a inicialização do Dijkstra);
* distâncias, saltos e predecessores em listas indexadas por inteiro, no lugar
  de dicionários/defaultdicts;
* o rank usado na ordem total de caminhos é o próprio índice do vértice;
* relaxamento de arestas inlined (sem chamada de função nem tupla de retorno);
* fila em lote (BatchPQOpt) com remoção preguiçosa e blocos ordenados por bisect;
* contagem de subárvore do FindPivots com parada antecipada em k.
"""
import bisect
import math
from heapq import heappop, heappush

INF = float("inf")
TOP = (INF, INF, INF)


class _Blk:
    __slots__ = ("items", "upper")

    def __init__(self, items=None, upper=None):
        self.items = items if items is not None else []
        self.upper = upper

    def split(self):
        mid = len(self.items) // 2
        right = _Blk(self.items[mid:], self.items[-1][0])
        self.items = self.items[:mid]
        self.upper = self.items[-1][0]
        return right


class BatchPQOpt:
    """Fila em lote (Lema 3.3) com D0/D1 e remoção preguiçosa."""

    __slots__ = ("M", "B", "d0", "d1", "d1_up", "kv")

    def __init__(self, M, B):
        self.M = M
        self.B = B
        self.d0 = []
        self.d1 = []
        self.d1_up = []
        self.kv = {}      # vértice -> chave vigente nesta fila

    def insert(self, v, key):
        kv = self.kv
        cur = kv.get(v)
        if cur is not None and key >= cur:
            return
        kv[v] = key
        d1, up = self.d1, self.d1_up
        if not d1:
            d1.append(_Blk([(key, v)], key))
            up.append(key)
            return
        idx = bisect.bisect_left(up, key)
        if idx == len(d1):
            idx -= 1
        blk = d1[idx]
        items = blk.items
        bisect.insort(items, (key, v))
        last = items[-1][0]
        blk.upper = last
        up[idx] = last
        if len(items) > self.M:
            right = blk.split()
            up[idx] = blk.upper
            d1.insert(idx + 1, right)
            up.insert(idx + 1, right.upper)

    def batch_prepend(self, pairs):
        if not pairs:
            return
        deduped = {}
        for v, key in pairs:
            c = deduped.get(v)
            if c is None or key < c:
                deduped[v] = key
        kv = self.kv
        filtered = []
        for v, key in deduped.items():
            cur = kv.get(v)
            if cur is not None and key >= cur:
                continue
            kv[v] = key
            filtered.append((key, v))
        if not filtered:
            return
        filtered.sort()
        L = len(filtered)
        M = self.M
        if L <= M:
            self.d0.insert(0, _Blk(filtered, filtered[-1][0]))
        else:
            chunk = max(1, M // 2)
            new_blocks = []
            for i in range(0, L, chunk):
                part = filtered[i:i + chunk]
                new_blocks.append(_Blk(part, part[-1][0]))
            self.d0[0:0] = new_blocks

    def _collect(self, seq, limit):
        out = []
        kv = self.kv
        visited = 0
        for blk in seq:
            visited += 1
            for p in blk.items:
                if kv.get(p[1]) == p[0]:
                    out.append(p)
            if len(out) >= limit:
                break
        return out, visited

    def _compact(self, seq, visited, with_up):
        kv = self.kv
        keep = []
        for i in range(visited):
            b = seq[i]
            b.items = [p for p in b.items if kv.get(p[1]) == p[0]]
            if b.items:
                b.upper = b.items[-1][0]
                keep.append(b)
        seq[0:visited] = keep
        if with_up:
            self.d1_up[:] = [b.upper for b in seq]

    def pull(self):
        c0, v0 = self._collect(self.d0, self.M)
        c1, v1 = self._collect(self.d1, self.M)
        cand = c0 + c1
        if not cand:
            return self.B, []
        cand.sort()
        seen = set()
        valid = []
        M = self.M
        for key, v in cand:
            if v in seen:
                continue
            seen.add(v)
            valid.append(v)
            if len(valid) == M:
                break
        kv = self.kv
        for v in valid:
            del kv[v]
        self._compact(self.d0, v0, False)
        self._compact(self.d1, v1, True)
        d0, d1 = self.d0, self.d1
        if d0:
            if d1:
                a, b = d0[0].items[0][0], d1[0].items[0][0]
                x = a if a < b else b
            else:
                x = d0[0].items[0][0]
        elif d1:
            x = d1[0].items[0][0]
        else:
            x = self.B
        return x, valid

    def is_empty(self):
        return not self.kv


class _Ctx:
    """Estado compartilhado do algoritmo (arrays indexados por vértice)."""

    __slots__ = ("adj", "dist", "hops", "pred")


def _base_case(c, s, B, k):
    adj, dist, hops, pred = c.adj, c.dist, c.hops, c.pred
    U0 = set()
    heap = [((dist[s], hops[s], s), s)]
    while heap and len(U0) < k + 1:
        _, u = heappop(heap)
        if u in U0:
            continue
        U0.add(u)
        du = dist[u]
        hu1 = hops[u] + 1
        for v, w in adj[u]:
            nd = du + w
            od = dist[v]
            if nd < od:
                dist[v] = nd
                hops[v] = hu1
                pred[v] = u
            elif nd == od:
                pv = pred[v]
                if (hu1, u) < (hops[v], pv if pv >= 0 else v):
                    hops[v] = hu1
                    pred[v] = u
            else:
                continue
            key = (dist[v], hops[v], v)
            if key < B:
                heappush(heap, (key, v))
    if len(U0) <= k:
        return B, U0
    keys = [(dist[v], hops[v], v) for v in U0]
    max_key = max(keys)
    U = {key[2] for key in keys if key < max_key}
    return max_key, U


def _find_pivots(c, S, B, k):
    adj, dist, hops, pred = c.adj, c.dist, c.hops, c.pred
    W = set(S)
    prev = set(S)
    nS = len(S)
    for _ in range(k):
        cur = set()
        for u in prev:
            du = dist[u]
            hu1 = hops[u] + 1
            for v, w in adj[u]:
                nd = du + w
                od = dist[v]
                if nd < od:
                    dist[v] = nd
                    hops[v] = hu1
                    pred[v] = u
                elif nd == od:
                    pv = pred[v]
                    if (hu1, u) < (hops[v], pv if pv >= 0 else v):
                        hops[v] = hu1
                        pred[v] = u
                else:
                    continue
                if (dist[v], hops[v], v) < B:
                    cur.add(v)
        W |= cur
        prev = cur
        if len(W) > k * nS:
            return set(S), W

    children = {}
    has_parent = set()
    for v in W:
        p = pred[v]
        if p >= 0 and p in W:
            has_parent.add(v)
            lst = children.get(p)
            if lst is None:
                children[p] = [v]
            else:
                lst.append(v)
    P = set()
    for u in S:
        if u in has_parent:
            continue
        # contagem da subárvore com parada antecipada em k
        count = 0
        stack = [u]
        visited = set()
        while stack:
            x = stack.pop()
            if x in visited:
                continue
            visited.add(x)
            count += 1
            if count >= k:
                P.add(u)
                break
            ch = children.get(x)
            if ch:
                stack.extend(ch)
    return P, W


def _bmssp(c, l, B, S, k, t):
    if l == 0:
        return _base_case(c, next(iter(S)), B, k)

    adj, dist, hops, pred = c.adj, c.dist, c.hops, c.pred
    P, W = _find_pivots(c, S, B, k)
    D = BatchPQOpt(2 ** ((l - 1) * t), B)
    for x in P:
        D.insert(x, (dist[x], hops[x], x))

    B_prime = min(((dist[x], hops[x], x) for x in P), default=B)
    U = set()
    limit = (k ** 2) * (2 ** (l * t))

    while len(U) < limit and not D.is_empty():
        Bi, Si = D.pull()
        if not Si:
            break
        Bip, Ui = _bmssp(c, l - 1, Bi, set(Si), k, t)
        U |= Ui

        K = []
        for u in Ui:
            du = dist[u]
            hu1 = hops[u] + 1
            for v, w in adj[u]:
                nd = du + w
                od = dist[v]
                if nd < od:
                    dist[v] = nd
                    hops[v] = hu1
                    pred[v] = u
                elif nd == od:
                    pv = pred[v]
                    if (hu1, u) < (hops[v], pv if pv >= 0 else v):
                        hops[v] = hu1
                        pred[v] = u
                else:
                    continue
                key = (dist[v], hops[v], v)
                if Bi <= key < B:
                    D.insert(v, key)
                elif Bip <= key < Bi:
                    K.append((v, key))
        for x in Si:
            key = (dist[x], hops[x], x)
            if Bip <= key < Bi:
                K.append((x, key))
        D.batch_prepend(K)
        B_prime = Bip if Bip < B else B

    for x in W:
        if (dist[x], hops[x], x) < B_prime:
            U.add(x)
    return B_prime, U


def sssp_duan_et_al_opt(graph, source):
    # Renomeia vértices para inteiros densos e monta listas de adjacência
    src_adj = graph.adj
    idx = {}
    names = []
    for u in src_adj:
        idx[u] = len(names)
        names.append(u)
    for u in src_adj:
        for v, _ in src_adj[u]:
            if v not in idx:
                idx[v] = len(names)
                names.append(v)
    if source not in idx:
        idx[source] = len(names)
        names.append(source)
    n = len(names)

    adj = [()] * n
    for u, edges in src_adj.items():
        adj[idx[u]] = [(idx[v], w) for v, w in edges]

    c = _Ctx()
    c.adj = adj
    c.dist = [INF] * n
    c.hops = [0] * n
    c.pred = [-1] * n
    s = idx[source]
    c.dist[s] = 0

    k = max(2, int(math.log2(n) ** (1 / 3))) if n > 1 else 2
    t = max(2, int(math.log2(n) ** (2 / 3))) if n > 1 else 2
    l = int(math.log2(n) / t) + 1 if n > 1 else 1
    _bmssp(c, l, TOP, {s}, k, t)

    return {names[i]: d for i, d in enumerate(c.dist) if d < INF}
