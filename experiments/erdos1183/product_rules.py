"""Product rules for Erdos 1183: from level colourings w1 of 2^[a] and w2 of 2^[b], colour 2^[a+b] by
rule(w1[|S n A|], w2[|S n B|]) (a grid colouring with dims (a, b)) and measure its largest monochromatic
sublattice with gridsearch.c.  A rule with M(a+b) <= M(a) + M(b) + C for all a, b would give f(n) = O(n).
Usage: python3 product_rules.py AMAX"""
import itertools, subprocess, sys, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
GS = os.path.join(HERE, "gridsearch")

def score(k, dims, s, bits):
    return int(subprocess.run([GS, "check", str(k), *map(str, dims), str(s), bits], capture_output=True, text=True).stdout)

def maxmono(k, dims, bits):
    s = 2
    while score(k, dims, s, bits) > 0:
        s += 1
    return s - 1

def best_level(n):
    best = None
    for w in itertools.product("01", repeat=n + 1):
        if w[0] == "1":
            continue
        w = "".join(w)
        m = maxmono(1, (n,), w)
        if best is None or m < best[0]:
            best = (m, w)
    return best

RULES = {"xor": lambda x, y: x ^ y, "and": lambda x, y: x & y, "or": lambda x, y: x | y,
         "first": lambda x, y: x, "xnor": lambda x, y: 1 - (x ^ y)}
amax = int(sys.argv[1]) if len(sys.argv) > 1 else 6
lv = {n: best_level(n) for n in range(1, amax + 1)}
print("best level", {n: v for n, v in lv.items()}, flush=True)
out = []
for a in range(1, amax + 1):
    for b in range(a, amax + 1):
        for name, r in RULES.items():
            w1, w2 = lv[a][1], lv[b][1]
            bits = "".join(str(r(int(w1[x]), int(w2[y]))) for x in range(a + 1) for y in range(b + 1))
            m = maxmono(2, (a, b), bits)
            out.append(dict(a=a, b=b, rule=name, M=m, Ma=lv[a][0], Mb=lv[b][0], level_ab=None))
            print(a, b, name, m, lv[a][0] + lv[b][0], flush=True)
json.dump(dict(level=lv, rows=out), open(os.path.join(HERE, "product_rules.json"), "w"), indent=1)
