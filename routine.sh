#!/bin/bash
set -e

source venv/bin/activate

# ==== Configurações (ajuste conforme necessário) ====
SALVAR="--untrack"                 # --track ou --untrack
GRAPHS_PATH="data/graphs"          # onde generate_graphs.py salva os grafos
EXECUTIONS_PER_GRAPH=5
DIMACS_PATH="input_graphs/"          # arquivo .gz ou diretório com .gz
DIMACS_REPETITIONS=5

# ==== 1. Gerar e salvar os grafos em disco ====
echo "==> Gerando grafos..."
python generate_graphs.py \
    --vertices 10000 50000 100000

# ==== 2. Rodar random_tests sobre os grafos salvos, com e sem transformação ====
echo "==> Rodando random_tests (com transform)..."
python random_test.py \
    "$SALVAR" \
    --mode load \
    --path "$GRAPHS_PATH" \
    --executions-per-graph "$EXECUTIONS_PER_GRAPH" \
    --transform

echo "==> Rodando random_tests (sem transform)..."
python random_test.py \
    "$SALVAR" \
    --mode load \
    --path "$GRAPHS_PATH" \
    --executions-per-graph "$EXECUTIONS_PER_GRAPH"

# ==== 3. Rodar run_dimacs, com e sem transformação ====
echo "==> Rodando run_dimacs (com transform)..."
python dimacs_test.py \
    "$DIMACS_PATH" \
    -r "$DIMACS_REPETITIONS" \
    "$SALVAR" \
    --transform

echo "==> Rodando run_dimacs (sem transform)..."
python dimacs_test.py \
    "$DIMACS_PATH" \
    -r "$DIMACS_REPETITIONS" \
    "$SALVAR"

echo "==> Concluído."