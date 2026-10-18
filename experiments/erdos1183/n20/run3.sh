#!/usr/bin/env bash
# Third pass: lift the best (18,2) colouring to the finer grids (16,2,2) and (17,2,1), which contain
# every (18,2) colouring, and anneal there.
cd "$(dirname "$0")/.."
B=$(cat n20/best_score1.txt)
lift() { python3 -c "
import sys,itertools
B=sys.argv[1]; d=list(map(int,sys.argv[2:]))
out=''.join(B[(v[0]+v[1])*3+v[2]] for v in itertools.product(*[range(x+1) for x in d]))
print(out)" "$B" "$@"; }
L1=$(lift 16 2 2); L2=$(lift 17 1 2)
echo "check lift 16 2 2: $(./gridsearch check 3 16 2 2 12 $L1)"
echo "check lift 17 1 2: $(./gridsearch check 3 17 1 2 12 $L2)"
for r in 0 1; do
  timeout 3000 ./gridsearch anneal 3 16 2 2 12 "$L1" $((500 + r)) 3000 > "n20/d_16x2x2_$((500 + r)).log" &
  timeout 3000 ./gridsearch anneal 3 17 1 2 12 "$L2" $((600 + r)) 3000 > "n20/d_17x1x2_$((600 + r)).log" &
done
wait
grep -H "best\|FOUND" n20/d_*.log
