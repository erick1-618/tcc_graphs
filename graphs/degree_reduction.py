from graphs.graphs import Graph

CHAIN_EDGE_WEIGHT = 0.0


def bounded_out_degree(graph: Graph, max_degree: int = 2) -> Graph:
    
    assert max_degree >= 2, "max_degree precisa ser >= 2"

    new_g = Graph()
    slots_por_no = max_degree - 1  

    for u, edges in graph.adj.items():
        if len(edges) <= max_degree:
            for v, w in edges:
                new_g.add_edge(u, v, w)
            continue

        
        chunks = []
        i, n = 0, len(edges)
        while i < n:
            restante = n - i
            if restante <= max_degree:
                chunks.append(edges[i:])
                i = n
            else:
                chunks.append(edges[i:i + slots_por_no])
                i += slots_por_no

        node_names = [u] + [f"{u}#{k}" for k in range(1, len(chunks))]

        for idx, (nome, chunk) in enumerate(zip(node_names, chunks)):
            for v, w in chunk:
                new_g.add_edge(nome, v, w)
            if idx < len(node_names) - 1:
                new_g.add_edge(nome, node_names[idx + 1], CHAIN_EDGE_WEIGHT)  

    # preserva vértices-folha (sem arestas de saída) que existiam no original
    for u in graph.adj:
        if u not in new_g.adj:
            new_g.adj[u] = []

    return new_g


if __name__ == "__main__":
    from graphs.graphs import dijkstra, generate_random_graph
    import random

    random.seed(0)
    g = generate_random_graph(200, 0.08)  # grau médio alto o suficiente pra ter vértices > max_degree

    max_deg_encontrado = max(len(v) for v in g.adj.values())
    print(f"Grau de saída máximo original: {max_deg_encontrado}")

    g2 = bounded_out_degree(g, max_degree=3)
    max_deg_transformado = max(len(v) for v in g2.adj.values())
    print(f"Grau de saída máximo após transformação: {max_deg_transformado}")

    # confere que as distâncias pros vértices originais não mudaram
    d1 = dijkstra(g, 0)
    d2 = dijkstra(g2, 0)

    all_ok = True
    for v in d1:
        if v not in d2 or abs(d1[v] - d2[v]) > 1e-9:
            all_ok = False
            print(f"DIVERGIU em {v}: original={d1.get(v)} transformado={d2.get(v)}")

    print("Distâncias preservadas: OK" if all_ok else "Distâncias preservadas: FALHOU")