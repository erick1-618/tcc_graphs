#!/bin/bash
set -e

source .venv/bin/activate

# ==== Configurações (ajuste conforme necessário) ====
SALVAR="--untrack"                 # --track ou --untrack
GRAPHS_PATH="data/graphs"          # onde generate_graphs.py salva os grafos
EXECUTIONS_PER_GRAPH=5
DIMACS_PATH="data/dimacs"          # arquivo .gz ou diretório com .gz
DIMACS_REPETITIONS=5

# ==== 1. Gerar e salvar os grafos em disco ====
echo "==> Gerando grafos..."
python generate_graphs.py

# ==== 2. Rodar random_tests sobre os grafos salvos, com e sem transformação ====
echo "==> Rodando random_tests (com transform)..."
python random_tests.py \
    "$SALVAR" \
    --mode load \
    --path "$GRAPHS_PATH" \
    --executions-per-graph "$EXECUTIONS_PER_GRAPH" \
    --transform

echo "==> Rodando random_tests (sem transform)..."
python random_tests.py \
    "$SALVAR" \
    --mode load \
    --path "$GRAPHS_PATH" \
    --executions-per-graph "$EXECUTIONS_PER_GRAPH"

# ==== 3. Rodar run_dimacs, com e sem transformação ====
echo "==> Rodando run_dimacs (com transform)..."
python run_dimacs.py \
    "$DIMACS_PATH" \
    -r "$DIMACS_REPETITIONS" \
    "$SALVAR" \
    --transform

echo "==> Rodando run_dimacs (sem transform)..."
python run_dimacs.py \
    "$DIMACS_PATH" \
    -r "$DIMACS_REPETITIONS" \
    "$SALVAR"

echo "==> Concluído."