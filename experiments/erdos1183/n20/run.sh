#!/usr/bin/env bash
# Anneal grid colourings of 2^[20] towards no monochromatic sublattice of 12 members (f(20) <= 11).
cd "$(dirname "$0")/.."
W=(000101100111001011100 001001110100110001101 001101000111010011010 010011000101101110010)
run() { local dims="$1" w="$2" seed="$3"; ./gridsearch anneal 2 $dims 12 "$w" "$seed" 4000 > "n20/anneal_${dims// /x}_${seed}.log"; }
for r in 0 1 2; do
  run "19 1" ${W[$r]} $((r+1)) & run "18 2" ${W[$((r+1))]} $((r+11)) & run "17 3" ${W[$r]} $((r+21)) & run "16 4" ${W[$((r+1))]} $((r+31)) &
  wait
done
grep -H "best\|FOUND" n20/*.log
