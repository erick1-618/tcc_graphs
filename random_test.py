from random import seed
from graphs.graphs import dijkstra, generate_random_graph, is_fully_reachable
from graphs.duan_et_al import sssp_duan_et_al
from time import process_time
from sys import argv
from graphs.degree_reduction import bounded_out_degree
import csv
from datetime import datetime
import os


salvar = argv[1]

while salvar not in ("--track", "--untrack"):
    print("Opção inválida. Deseja subir os resultados para o github? (--track / --untrack): ")
    exit(0)

# Garantir reprodutibilidade
seed(42)

# Quantidade de grafos por configuração
num_graphs = 5

num_vertices = (100, 500, 1000, 5000)

# Grau médio
grau_médio = (5, 3, 1, 0.8, 0.7, 0.5) 

# Algoritmos
algorithms = (dijkstra, sssp_duan_et_al)

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
            g = bounded_out_degree(g,2)

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

                    source = 0
                    start_time = process_time()
                    dist = alg(g, source)
                    end_time = process_time()

                    delta_time = end_time - start_time

                    num_explored = sum(1 for v in dist if dist[v] < float('inf'))
                    explored_percentage = (num_explored / num_v) * 100

                    results.append({
                        "num_vertices": num_v,
                        "avg_degree_k": k,
                        "algorithm": alg.__name__,
                        "execution_time": delta_time,
                        "edge_estimate": edge_estimate,
                        "graph": f"n{num_v}k{k:.2f}i{i}",
                        "fully_reachable": is_fully_reachable(g, source, num_v),
                        "explored_percentage": explored_percentage
                    })

print("\nExecution finished.")

# Nome dessa instância do teste com a data e hora atual
name = f"results-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"

dir = "data/untracked_results/" if salvar == "--untrack" else "data/"

# Criar diretório se não existir
if not os.path.exists(dir):
    os.makedirs(dir)

# Salvar os resultados em CSV
with open(f'{dir}{name}.csv', 'w', newline='') as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "num_vertices",
            "avg_degree_k",
            "algorithm",
            "execution_time",
            "edge_estimate",
            "graph",
            "fully_reachable",
            "explored_percentage"
        ]
    )

    writer.writeheader()
    writer.writerows(results)
