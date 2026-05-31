from random import seed
from graphs.graphs import dijkstra, generate_random_graph
from graphs.duan_et_al import sssp_duan_et_al
import csv

# Garantir reprodutibilidade
seed(42)

# Quantidade de grafos por configuração
num_graphs = 5

# Quantidade de vértices
num_vertices = (10000, 50000, 100000, 500000)

# Grau médio
grau_médio = (5, 4.5, 4, 3.5, 3, 2.5, 2, 1.5, 1, 0.9, 0.8, 0.7, 0.6, 0.5) 

# Algoritmos
algorithms = (dijkstra, sssp_duan_et_al)

from time import perf_counter
import csv

results = []

qt_executions = (
    len(num_vertices)
    * len(grau_médio)
    * len(algorithms)
    * num_graphs
)

current_execution = 0

for num_v in num_vertices:
    for k in grau_médio:

        # conversão para probabilidade equivalente no G(n, p)
        edge_prob = k / (num_v - 1)

        # estimativa realista de número de arestas
        edge_estimate = (num_v * k)

        for i in range(num_graphs):

            g = generate_random_graph(num_v, edge_prob)

            for alg in algorithms:


                    current_execution += 1
                    progress = (current_execution / qt_executions) * 100

                    print(
                        f"\rExecuted {progress:.2f}% "
                        f"| num_vertices: {num_v} "
                        f"| k(avg_degree): {k:.2f} "
                        f"| algorithm: {alg.__name__} "
                        f"| edge_estimate: {edge_estimate:.0f}      ",
                        end="",
                        flush=True
                    )

                    start_time = perf_counter()
                    r = alg(g, 0)
                    end_time = perf_counter()

                    delta_time = end_time - start_time

                    results.append({
                        "num_vertices": num_v,
                        "avg_degree_k": k,
                        "algorithm": alg.__name__,
                        "execution_time": delta_time,
                        "edge_estimate": edge_estimate,
                        "graph": f"n{num_v}k{k:.2f}i{i}"
                    })

print("\nExecution finished.")

# Salvar os resultados em CSV
with open('data/more_sparse.csv', 'w', newline='') as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "num_vertices",
            "avg_degree_k",
            "algorithm",
            "execution_time",
            "edge_estimate",
            "graph"
        ]
    )

    writer.writeheader()
    writer.writerows(results)
