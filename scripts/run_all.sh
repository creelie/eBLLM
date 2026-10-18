#!/usr/bin/env bash
# Run the hardware check, the tests and the three studies of the paper in order.
#   scripts/run_all.sh [--quick] [--llm]
#   --quick  2 seeds and 2 rounds per study (a smoke run); default 60 seeds, 5-6 rounds.
#   Outputs go to $EBLLM_RUN_DIR (default runs/<UTC time>/), never over the recorded data in experiments/.
#   --llm    add the local model to the proposers (needs llama-cpp-python and a model file).
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
command -v python3 >/dev/null || { echo "python3 not found" >&2; exit 2; }
SEEDS=60; ROUNDS=5; LOOP=6; LLM=""
for a in "$@"; do
  case "$a" in
    --quick) SEEDS=2; ROUNDS=2; LOOP=2 ;;
    --llm) LLM="--llm" ;;
    *) echo "unknown option: $a" >&2; exit 2 ;;
  esac
done
export PYTHONPATH="$ROOT/src"
export EBLLM_RUN_DIR="${EBLLM_RUN_DIR:-$ROOT/runs/$(date -u +%Y%m%dT%H%M%SZ)}"
mkdir -p "$EBLLM_RUN_DIR"; echo "outputs in $EBLLM_RUN_DIR"
step() { echo "== $1"; local t0=$SECONDS; shift; "$@"; echo "   done in $((SECONDS - t0)) s"; }
step "hardware" python3 scripts/check_hardware.py --path "$ROOT"
step "unit tests" python3 -m unittest discover -s tests
step "memory study ($SEEDS seeds, $ROUNDS rounds)" python3 experiments/superbrain.py "$SEEDS" "$ROUNDS" $LLM
step "channel study ($SEEDS seeds, $((ROUNDS + 1)) rounds)" python3 experiments/channel_study.py "$SEEDS" "$((ROUNDS + 1))"
step "agent loop ($LOOP rounds)" python3 experiments/loop.py "$LOOP" $LLM
echo "all steps passed"
