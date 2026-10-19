"""Entropy law and Huffman schedules, checked on random instances."""
import math, random, sys
from common import entropy, huffman_lengths, brute_kraft, brute_schedule

random.seed(20261018)
fails = 0; checks = 0
# (A) entropy-law bounds against the exact integer optimum, general eps
for trial in range(300):
    n = random.randint(1, 5)
    a = [random.uniform(0.05, 2.0) for _ in range(n)]
    eps = random.choice([0.5, 0.3, 0.2, 0.37, 0.61])
    theta = random.choice([0.5, 0.2, 0.1, 0.05, 0.013])
    L = math.log(1 / eps)
    A = sum(a); p = [x / A for x in a]; H = entropy(p)
    lo = A / L * (H + math.log(1 / theta))
    hi = lo + A
    rmax = int(math.ceil(math.log(1 / (theta * min(p))) / L)) + 2
    v = brute_schedule(a, eps, theta, rmax)
    checks += 1
    if not (lo - 1e-9 <= v <= hi + 1e-9):
        fails += 1; print("FAIL A", a, eps, theta, lo, v, hi)
# (B) Huffman is exactly optimal when eps = 1/D and theta = D^-k
for trial in range(200):
    D = random.choice([2, 3, 4])
    n = random.randint(1, 6 if D == 2 else 5)
    k = random.randint(0, 2)
    a = [random.uniform(0.05, 2.0) for _ in range(n)]
    A = sum(a); p = [x / A for x in a]
    hl = huffman_lengths(p, D)
    vh = sum(pi * l for pi, l in zip(p, hl))
    vb = brute_kraft(p, D, n)
    checks += 1
    if abs(vh - vb) > 1e-9:
        fails += 1; print("FAIL B", p, D, vh, vb)
    if k >= 1:
        vs = brute_schedule(a, 1.0 / D, float(D) ** (-k), n + k + 1)
        checks += 1
        if abs(vs - A * (k + vh)) > 1e-7:
            fails += 1; print("FAIL B2", a, D, k, vs, A * (k + vh))
# (C) uniform chains: n = D^m items, optimum n a (m + k)
for D in (2, 3):
    for m in range(0, 4):
        n = D ** m
        hl = huffman_lengths([1.0 / n] * n, D)
        checks += 1
        if any(l != m for l in hl):
            fails += 1; print("FAIL C", D, m, hl)
print(f"entropy law: {checks} checks, {fails} failed")
sys.exit(1 if fails else 0)
