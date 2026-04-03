import heapq

example_graph = {
    'A': [('B', 1.5), ('C', 2.0)],
    'B': [('D', 3.0)],
    'C': [('D', 1.2)],
    'D': []
}

def dijkstra(grafo, fonte):
    # Inicialização: distâncias começam como infinito, fonte como 0 [4]
    distancias = {vertice: float('inf') for vertice in grafo}
    distancias[fonte] = 0
    
    # Fila de prioridade (heap binário) [2]
    # Armazena tuplas (distancia_estimada, vertice)
    pq = [(0, fonte)]
    
    while pq:
        # Extrai o vértice u com a distância mínima [1, 2]
        dist_u, u = heapq.heappop(pq)
        
        # Se a distância extraída for maior que a já registrada, ignore
        if dist_u > distancias[u]:
            continue
            
        # Relaxamento: para cada aresta (u, v) com peso w [1, 4]
        for v, peso in grafo.get(u, []):
            # d_hat[v] = d_hat[u] + wuv se for menor que o valor atual [4]
            if distancias[u] + peso < distancias[v]:
                distancias[v] = distancias[u] + peso
                heapq.heappush(pq, (distancias[v], v))
                
    return distancias

def bellman_ford(grafo, fonte):
    # Inicialização conforme descrito no paper [4]
    distancias = {vertice: float('inf') for vertice in grafo}
    distancias[fonte] = 0
    
    vertices = list(grafo.keys())
    n = len(vertices)
    
    # O Bellman-Ford relaxa todas as arestas por várias etapas [1]
    # Para encontrar caminhos mínimos, são necessários até n-1 passos
    for _ in range(n - 1):
        houve_mudanca = False
        for u in grafo:
            for v, peso in grafo[u]:
                # Operação de relaxamento: d_hat[v] <- d_hat[u] + wuv [4]
                if distancias[u] + peso < distancias[v]:
                    distancias[v] = distancias[u] + peso
                    houve_mudanca = True
        
        # Se nenhuma distância mudou em uma iteração, o algoritmo pode parar
        if not houve_mudanca:
            break
            
    return distancias

def transformar_para_grau_constante(grafo_original):
    """
    Transforma um grafo em um novo grafo com grau constante.
    Args:       grafo_original (dict): O grafo original representado como um dicionário de adjacências.
    Returns:    dict: O novo grafo com grau constante.
    """

    novo_adj = {}
    for v, vizinhos in grafo_original.items():
        # Cria um ciclo de nós internos para v: v_in_1 -> v_in_2 -> ... -> v_in_n -> v_in_1
        # Cada aresta interna tem peso 0.0
        # Cada vizinho externo é conectado a um desses nós do ciclo
        n = len(vizinhos)
        for i in range(n):
            u_original, peso = vizinhos[i]
            no_atual = f"{v}_node_{i}"
            proximo_no_ciclo = f"{v}_node_{(i+1)%n}"
            
            # Aresta do ciclo (peso zero)
            if no_atual not in novo_adj: novo_adj[no_atual] = []
            novo_adj[no_atual].append((proximo_no_ciclo, 0.0))
            
            # Aresta real para o vizinho (peso original)
            # Nota: O destino deve ser o primeiro nó do ciclo do vizinho
            novo_adj[no_atual].append((f"{u_original}_node_0", peso))
            
    return novo_adj