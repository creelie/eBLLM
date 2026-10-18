#!/usr/bin/env bash
# Second pass at dims (18,2): replay the run that reached score 1 (seed 13), then anneal onwards from
# its best colouring with several seeds, alongside fresh seeds.
cd "$(dirname "$0")/.."
./gridsearch anneal 2 18 2 12 010011000101101110010 13 4000 > n20/replay_18x2_13.log
B=$(grep "score 1 bits" n20/replay_18x2_13.log | tail -n 1 | awk '{print $NF}')
echo "seed bits: $B"
W=(001001110100110001101 000101100111001011100 001101000111010011010 010011000101101110010)
for r in 0 1 2 3 4 5 6 7; do
  ./gridsearch anneal 2 18 2 12 "$B" $((200 + r)) 6000 > "n20/c_18x2_$((200 + r)).log" &
  ./gridsearch anneal 2 18 2 12 "$B" $((300 + r)) 6000 > "n20/c_18x2_$((300 + r)).log" &
  ./gridsearch anneal 2 18 2 12 "${W[$((r % 4))]}" $((400 + r)) 8000 > "n20/c_18x2_$((400 + r)).log" &
  wait
  if grep -l FOUND n20/c_*.log; then break; fi
done
grep -H "best\|FOUND" n20/c_*.log
