#!/bin/bash
set -e

source venv/bin/activate

# ==== Configurações (ajuste conforme necessário) ====
SALVAR="--track"                       # --track ou --untrack
GRAPHS_PATH="data/lote3-tcc2/graphs"   # grafos do lote 3, reutilizados (mesmos grafos => lotes comparaveis)
RESULTS_PATH="data/lote4-tcc2/results" # onde os CSVs de resultado serão salvos
EXECUTIONS_PER_GRAPH=5
DIMACS_PATH="input_graphs/"            # arquivo .gz ou diretório com .gz
DIMACS_REPETITIONS=5

# Algoritmos a testar:
# dijkstra: baseline
# sssp_duan_et_al: recursivo corrigido (cleanup_passes=0)
# sssp_duan_et_al_iter: iterativo corrigido (cleanup_passes=0)
# sssp_duan_et_al_opt: otimizado (lote 4: arrays indexados, relaxamento inline, BatchPQOpt)
ALGORITHMS="dijkstra sssp_duan_et_al sssp_duan_et_al_iter sssp_duan_et_al_opt"

mkdir -p "$GRAPHS_PATH"
mkdir -p "$RESULTS_PATH"

# ==== 1. Gerar e salvar os grafos em disco (só se ainda não existirem) ====
if ls "$GRAPHS_PATH"/*.json >/dev/null 2>&1; then
    echo "==> Reutilizando grafos existentes em $GRAPHS_PATH"
else
    echo "==> Gerando grafos..."
    python generate_graphs.py \
        --path "$GRAPHS_PATH" \
        --vertices 10000 50000 100000
fi

# ==== 2. Rodar random_tests sobre os grafos salvos, com e sem transformação ====
echo "==> Rodando random_tests (com transform)..."
python random_test.py \
    "$SALVAR" \
    --mode load \
    --path "$GRAPHS_PATH" \
    --output-dir "$RESULTS_PATH" \
    --algorithms $ALGORITHMS \
    --executions-per-graph "$EXECUTIONS_PER_GRAPH" \
    --transform

echo "==> Rodando random_tests (sem transform)..."
python random_test.py \
    "$SALVAR" \
    --mode load \
    --path "$GRAPHS_PATH" \
    --output-dir "$RESULTS_PATH" \
    --algorithms $ALGORITHMS \
    --executions-per-graph "$EXECUTIONS_PER_GRAPH"

# ==== 3. Rodar run_dimacs, com e sem transformação ====
echo "==> Rodando run_dimacs (com transform)..."
python dimacs_test.py \
    "$DIMACS_PATH" \
    -r "$DIMACS_REPETITIONS" \
    "$SALVAR" \
    --output-dir "$RESULTS_PATH" \
    --algorithms $ALGORITHMS \
    --transform

echo "==> Rodando run_dimacs (sem transform)..."
python dimacs_test.py \
    "$DIMACS_PATH" \
    -r "$DIMACS_REPETITIONS" \
    "$SALVAR" \
    --output-dir "$RESULTS_PATH" \
    --algorithms $ALGORITHMS

echo "==> Concluído com sucesso. Resultados salvos em $RESULTS_PATH"