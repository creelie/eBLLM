#!/usr/bin/env bash
# Fourth pass: balanced two-block grids (a, 20 - a), a = 10, 12, 14, from level words of 2^[20].
cd "$(dirname "$0")/.."
W=(000101100111001011100 001001110100110001101 001101000111010011010)
run() { local dims="$1" w="$2" seed="$3"; timeout 3000 ./gridsearch anneal 2 $dims 12 "$w" "$seed" 4000 > "n20/e_${dims// /x}_${seed}.log"; }
run "10 10" ${W[0]} 701 & run "12 8" ${W[1]} 702 & run "14 6" ${W[2]} 703 &
wait
grep -H "best\|FOUND" n20/e_*.log
