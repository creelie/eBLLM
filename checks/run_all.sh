#!/usr/bin/env bash
# Runs every numerical check of the BLLM paper and the Lean build; exits non-zero on any failure.
set -euo pipefail
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$here"
status=0
for f in check_entropy_law.py check_gating.py check_renyi.py check_singularity.py check_branching.py; do
  python3 "$here/$f" || status=1
done
build="$(mktemp -d)"
trap 'rm -rf "$build"' EXIT
gcc -O2 -o "$build/huffman_schedule" "$here/c/huffman_schedule.c" -lm && "$build/huffman_schedule" || status=1
g++ -O2 -std=c++17 -o "$build/renyi_gating" "$here/c/renyi_gating.cpp" && "$build/renyi_gating" || status=1
if command -v lake >/dev/null 2>&1; then
  (cd "$here/../lean" && lake build && lake env lean Axioms.lean) || status=1
else
  echo "lake not found: Lean build skipped"
fi
exit $status
