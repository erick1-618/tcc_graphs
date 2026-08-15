from sys import argv
from time import process_time
from datetime import datetime
from graphs.graphs import Graph, dijkstra, is_fully_reachable
from graphs.duan_et_al import sssp_duan_et_al
import gzip
import shutil
import csv
import os
import glob


def load_graph(gr_file: str) -> tuple[Graph, int, int]:

    with open(gr_file, 'r') as f:
        data = f.read().splitlines()

    graph = Graph()
    n = m = 0

    for line in data:
        if line.startswith('a'):
            _, u, v, w = line.split()
            graph.add_edge(int(u), int(v), int(w))
        elif line.startswith('p'):
            _, _, n, m = line.split()

    return graph, int(n), int(m)


def process_file(arquivo_gz: str, r: int, algorithms: tuple) -> list[dict]:
    """Descompacta, carrega e roda os algoritmos sobre um único arquivo .gz,
    retornando a lista de resultados (um dict por execução)."""

    file_results = []
    arquivo_gr = arquivo_gz.replace('.gz', '')

    # Descompacta o arquivo
    with gzip.open(arquivo_gz, 'rb') as f_in:
        with open(arquivo_gr, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    graph, num_vertices, num_edges = load_graph(arquivo_gr)

    print("n = {}, m = {}".format(num_vertices, num_edges))

    qt_executions = len(algorithms) * r
    current_execution = 0

    for alg in algorithms:
        for i in range(r):

            current_execution += 1
            progress = (current_execution / qt_executions) * 100

            print(
                f"\rExecuted {progress:.2f}% "
                f"| arquivo: {os.path.basename(arquivo_gz)} "
                f"| algorithm: {alg.__name__} "
                f"| repetition: {i + 1}/{r}      ",
                end="",
                flush=True
            )

            start_time = process_time()
            alg(graph, 1)
            end_time = process_time()

            delta_time = end_time - start_time

            file_results.append({
                "arquivo": os.path.basename(arquivo_gz),
                "num_vertices": num_vertices,
                "num_edges": num_edges,
                "algorithm": alg.__name__,
                "execution_time": delta_time,
                "repetition": i,
                "fully_reachable": is_fully_reachable(graph, 0, num_vertices)
            })

    print()

    # Remover o arquivo descompactado
    os.remove(arquivo_gr)

    return file_results


# nome do arquivo .gz OU diretório contendo vários .gz
arquivo = argv[1]

is_directory = os.path.isdir(arquivo)

# repetições por algoritmo
r = int(argv[2])

# salvar rastreado ou não no git
salvar = argv[3]

while salvar not in ("--track", "--untrack"):
    print("Opção inválida. Deseja subir os resultados para o github? (--track / --untrack): ")
    exit(0)

# Algoritmos
algorithms = (dijkstra, sssp_duan_et_al)

# Monta a lista de arquivos .gz a processar
if is_directory:
    arquivos = sorted(glob.glob(os.path.join(arquivo, "*.gz")))
    if not arquivos:
        print(f"Nenhum arquivo .gz encontrado em '{arquivo}'.")
        exit(0)
else:
    arquivos = [arquivo]

results = []

for idx, arquivo_gz in enumerate(arquivos, start=1):
    if is_directory:
        print(f"\n[{idx}/{len(arquivos)}] Processando {os.path.basename(arquivo_gz)}")
    results.extend(process_file(arquivo_gz, r, algorithms))

print("\nExecution finished.")

dir = "data/untracked_results/" if salvar == "--untrack" else "data/"

name = f"dimacs-results-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"

# Criar diretório se não existir
if not os.path.exists(dir):
    os.makedirs(dir)

# Salvar os resultados em CSV
with open(f'{dir}{name}.csv', 'w', newline='') as f:
    writer = csv.DictWriter(
        f,
        fieldnames=[
            "arquivo",
            "num_vertices",
            "num_edges",
            "algorithm",
            "execution_time",
            "repetition",
            "fully_reachable"
        ]
    )

    writer.writeheader()
    writer.writerows(results)