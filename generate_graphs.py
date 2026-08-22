import argparse
import os
import sys
from random import seed
from graphs.graphs import generate_random_graph, save_graph, graph_cache_path

def main():
    parser = argparse.ArgumentParser(
        description="Script para gerar e salvar grafos aleatórios.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--path",
        type=str,
        default="data/graphs",
        help="Diretório onde os grafos serão salvos."
    )
    parser.add_argument(
        "--num-graphs",
        type=int,
        default=5,
        help="Quantidade de grafos por configuração."
    )
    parser.add_argument(
        "--vertices",
        type=int,
        nargs="+",
        default=[100, 500, 1000, 5000],
        help="Lista de número de vértices."
    )
    parser.add_argument(
        "--degrees",
        type=float,
        nargs="+",
        default=[5.0, 3.0, 1.0, 0.8, 0.7, 0.5],
        help="Lista de graus médios (k)."
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Semente (seed) para o gerador de números aleatórios."
    )

    args = parser.parse_args()

    # Garantir reprodutibilidade
    seed(args.seed)

    # Criar diretório se não existir
    os.makedirs(args.path, exist_ok=True)

    total_graphs = len(args.vertices) * len(args.degrees) * args.num_graphs
    current = 0

    print(f"Iniciando a geração de {total_graphs} grafos...")
    print(f"Salvar em: {args.path}")
    print(f"Vértices: {args.vertices}")
    print(f"Graus médios (k): {args.degrees}")
    print(f"Seed: {args.seed}\n")

    for num_v in args.vertices:
        for k in args.degrees:
            # Conversão para probabilidade equivalente no G(n, p)
            # Evitar divisão por zero se num_v <= 1
            if num_v <= 1:
                print(f"Ignorando num_v={num_v} (número de vértices deve ser maior que 1).")
                continue
            
            edge_prob = k / (num_v - 1)

            for i in range(args.num_graphs):
                current += 1
                graph_path = graph_cache_path(args.path, num_v, k, i)
                print(
                    f"\r[{current}/{total_graphs}] Gerando: V={num_v}, k={k:.2f}, inst={i}... ",
                    end="",
                    flush=True
                )
                
                g = generate_random_graph(num_v, edge_prob)
                save_graph(g, graph_path)

    print("\n\nGeração concluída com sucesso!")

if __name__ == "__main__":
    main()
