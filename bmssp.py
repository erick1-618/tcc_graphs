import math
import heapq

# Parâmetros baseados nas fontes [5]
def get_params(n):
    log_n = math.log2(n) if n > 1 else 1
    k = max(1, int(log_n**(1/3)))
    t = max(1, int(log_n**(2/3)))
    return k, t

# Algoritmo 1: FindPivots [1]
def find_pivots(B, S, adj, d_hat, k):
    W = set(S)
    W_layers = [set(S)]
    
    # Relaxamento de k passos (estilo Bellman-Ford) [1]
    for i in range(1, k + 1):
        current_layer = set()
        for u in W_layers[-1]:
            for v, weight in adj.get(u, []):
                if d_hat[u] + weight <= d_hat[v]:
                    d_hat[v] = d_hat[u] + weight
                    if d_hat[v] < B:
                        current_layer.add(v)
        W.update(current_layer)
        W_layers.append(current_layer)
        
        if len(W) > k * len(S): # Limite de tamanho de W [1]
            return list(S), W

    # Construção da floresta F para identificar pivôs [8]
    forest_adj = {u: [] for u in W}
    for u in W:
        for v, weight in adj.get(u, []):
            if v in W and d_hat[v] == d_hat[u] + weight:
                forest_adj[u].append(v)
    
    def count_nodes(u, visited):
        count = 1
        visited.add(u)
        for v in forest_adj.get(u, []):
            if v not in visited:
                count += count_nodes(v, visited)
        return count

    pivots = []
    for u in S:
        # Se a raiz u cobre uma árvore com >= k vértices, vira pivô [8]
        if count_nodes(u, set()) >= k:
            pivots.append(u)
            
    return pivots, W

# Algoritmo 2: Base Case [2, 9]
def base_case(B, S, adj, d_hat, k):
    x = list(S) # S é um singleton {x} [2]
    U0 = set()
    h = [(d_hat[x], x)]
    
    while h and len(U0) < k + 1:
        d, u = heapq.heappop(h)
        if u in U0: continue
        U0.add(u)
        
        for v, weight in adj.get(u, []):
            if d_hat[u] + weight <= d_hat[v] and d_hat[u] + weight < B:
                d_hat[v] = d_hat[u] + weight
                heapq.heappush(h, (d_hat[v], v))
                
    if len(U0) <= k:
        return B, U0
    else:
        B_prime = max(d_hat[v] for v in U0)
        return B_prime, {v for v in U0 if d_hat[v] < B_prime}

# Mock da Estrutura de Dados do Lemma 3.3 [10, 11]
class SpecialDS:
    def __init__(self, M, B):
        self.elements = [] # (valor, chave)
        self.M = M
        self.B = B

    def insert(self, key, value):
        heapq.heappush(self.elements, (value, key))

    def batch_prepend(self, records):
        for val, key in records:
            heapq.heappush(self.elements, (val, key))

    def pull(self):
        S_prime = set()
        last_val = self.B
        for _ in range(min(self.M, len(self.elements))):
            val, key = heapq.heappop(self.elements)
            S_prime.add(key)
            last_val = val
        
        # x deve separar S' do restante [11]
        remaining_min = self.elements if self.elements else self.B
        return remaining_min, S_prime

# Algoritmo 3: BMSSP [3, 12]
def bmssp(l, B, S, adj, d_hat, k, t):

    """
    Implementação do BMSSP, seguindo o artigo original
    Args:
    l: nível de recursão
    B: limite superior para distâncias
    S: conjunto de vértices
    adj: representação do grafo
    d_hat: estimativas de distância
    k: parâmetro para pivôs
    t: parâmetro para recursão
    """

    if l == 0:
        return base_case(B, S, adj, d_hat, k)
    
    P, W = find_pivots(B, S, adj, d_hat, k)
    M = 2**((l-1)*t)
    D = SpecialDS(M, B)
    
    for x in P:
        D.insert(x, d_hat[x])
        
    U = set()
    limit_U = k * (2**(l * t))
    
    while len(U) < limit_U and D.elements:
        Bi, Si = D.pull()
        B_prime_i, Ui = bmssp(l - 1, Bi, Si, adj, d_hat, k, t)
        U.update(Ui)
        
        K = []
        for u in Ui:
            for v, weight in adj.get(u, []):
                if d_hat[u] + weight <= d_hat[v]:
                    new_dist = d_hat[u] + weight
                    d_hat[v] = new_dist
                    if Bi <= new_dist < B:
                        D.insert(v, new_dist)
                    elif B_prime_i <= new_dist < Bi:
                        K.append((new_dist, v))
        
        # Batch Prepend para manter eficiência [12, 13]
        add_back = K + [(d_hat[x], x) for x in Si if B_prime_i <= d_hat[x] < Bi]
        D.batch_prepend(add_back)
        
    # Define o limite final B' e finaliza o conjunto W [12, 14]
    B_prime = B # Simplificação para retorno bem-sucedido
    U.update({x for x in W if d_hat[x] < B_prime})
    return B_prime, U