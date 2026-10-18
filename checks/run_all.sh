#!/usr/bin/env bash
# Run every check of the package from the repository root:
#   Python tests, the C, C++ and Julia programs, the Lean build, the Lean source scan,
#   the axiom audit (30 theorems, standard axioms only) and the example engine run.
# Set JULIA to the Julia binary if it is not on PATH; set SKIP_LEAN=1 to skip the Lean steps.
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build

echo "== Python tests"
PYTHONPATH=src python3 -m unittest discover -s tests

echo "== C: sand-tile toppling"
cc -O2 -std=c99 -Wall -Wextra -o build/sandtile checks/c/sandtile.c
./build/sandtile | tee build/sandtile.out
tail -n 1 build/sandtile.out | grep -qx OK

echo "== C++: scope loss and the collapse guard"
c++ -O2 -std=c++17 -Wall -Wextra -o build/scope_playbook checks/cpp/scope_playbook.cpp
./build/scope_playbook | tee build/scope_playbook.out
tail -n 1 build/scope_playbook.out | grep -qx OK

echo "== Julia: release algebra and Accuracy26"
"${JULIA:-julia}" checks/julia/release_accuracy.jl | tee build/release_accuracy.out
tail -n 1 build/release_accuracy.out | grep -qx OK

echo "== Counterexamples"
PYTHONPATH=src python3 -m ebllm counterexamples

if [ "${SKIP_LEAN:-0}" != 1 ]; then
  echo "== Lean: source scan"
  PYTHONPATH=src python3 -m ebllm scan lean/EBLLM lean/EBLLM.lean lean/Audit.lean
  echo "== Lean: build"
  (cd lean && lake build)
  echo "== Lean: axiom audit"
  (cd lean && lake env lean Audit.lean) > build/audit.log 2>&1 || { cat build/audit.log; exit 1; }
  PYTHONPATH=src python3 -m ebllm axioms build/audit.log 30
  echo "== Lean: independent kernel replay (leanchecker --fresh)"
  (cd lean && lake env leanchecker --fresh EBLLM)
  echo "== Example run (Theorem 10.4 refutation; the label must be CANDIDATE, blocked by human review)"
  set +e
  PYTHONPATH=src python3 -m ebllm run examples/theorem-10-4.json --ledger build/ledger.json > build/run.md
  status=$?
  set -e
  cat build/run.md
  [ "$status" = 2 ] && grep -q '^\*\*CANDIDATE\*\*.*blocking: human$' build/run.md
fi
echo "ALL CHECKS PASSED"
