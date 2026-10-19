"""Online entropy law (Theorem G): soundness, the upper bound, the doubling lower bound."""
import math, random, sys
from common import entropy
fails = 0; checks = 0

def ok(cond, msg):
    global fails, checks
    checks += 1
    if not cond:
        fails += 1; print("FAIL", msg)

def online(loga, eps, theta):
    """Runs r_n of the online rule, from log-costs; returns r and the log of the weights."""
    L = math.log(1 / eps)
    r, logw, lS = [], [], -math.inf
    for la in loga:
        lS = max(lS, la) + math.log1p(math.exp(-abs(lS - la))) if lS > -math.inf else la
        u = lS - loga[0]
        lw = (la - lS) - math.log(2) - 2 * math.log1p(u)
        logw.append(lw)
        r.append(math.ceil((math.log(1 / theta) - lw) / L - 1e-12))
    return r, logw

def prefix_stats(loga, r, N):
    m = max(loga[:N])
    q = [math.exp(x - m) for x in loga[:N]]
    s = sum(q)
    p = [x / s for x in q]
    return p, sum(pi * ri for pi, ri in zip(p, r[:N])), math.log(s) + m

rng = random.Random(20261018)
for eps in [0.5, 0.1, 0.9]:
    L = math.log(1 / eps)
    for theta in [1.0, 0.1, 1e-6]:
        for trial in range(40):
            n = rng.choice([1, 2, 5, 50, 400])
            kind = trial % 4
            if kind == 0:
                loga = [rng.gauss(0, 3) for _ in range(n)]
            elif kind == 1:
                loga = [0.7 * k + rng.gauss(0, 1) for k in range(n)]
            elif kind == 2:
                loga = [-0.5 * k for k in range(n)]
            else:
                loga = [k * math.log(2) for k in range(n)]
            r, logw = online(loga, eps, theta)
            W = sum(math.exp(x) for x in logw)
            ok(W <= 1 + 1e-12, f"weights sum {W}")
            F = sum(eps ** ri for ri in r)
            ok(F <= theta * (1 + 1e-9), f"online sound eps={eps} theta={theta}")
            for N in sorted({1, max(1, n // 3), n}):
                p, VA, lA = prefix_stats(loga, r, N)
                H = entropy(p)
                logR = lA - loga[0]
                up = (H + math.log(1 / theta) + math.log(2) + 2 * math.log1p(logR)) / L + 1
                lo = (H + math.log(1 / theta)) / L
                ok(lo - 1e-9 <= VA <= up + 1e-9, f"online bounds N={N}")
# doubling costs: V_N - (offline upper bound) against the necessary excess, for three sound online rules
for eps in [0.5, 0.25]:
    L = math.log(1 / eps)
    for theta in [1.0, 1e-3]:
        Nmax = 4000
        loga = [k * math.log(2) for k in range(Nmax)]
        r_main, _ = online(loga, eps, theta)
        r_zeta = [math.ceil(math.log(math.pi ** 2 * (k + 1) ** 2 / (6 * theta)) / L) for k in range(Nmax)]
        r_geo = [math.ceil(((k + 1) * math.log(2) + math.log(1 / theta)) / L) for k in range(Nmax)]
        for name, r in [("main", r_main), ("zeta", r_zeta), ("geometric", r_geo)]:
            ok(sum(eps ** x for x in r) <= theta * (1 + 1e-9), f"doubling sound {name}")
            hits = 0
            for N in [10, 30, 100, 300, 1000, 3000, 4000]:
                p, VA, lA = prefix_stats(loga, r, N)
                H = entropy(p)
                offline_up = (H + math.log(1 / theta)) / L + 1
                nec = math.log(N) / (2 * L) - 1 - 2 * math.log(2) / L
                if VA - offline_up >= nec:
                    hits += 1
            ok(hits >= 1, f"doubling lower bound attained for {name}")
# the number quoted in the text: range 10^100 gives 2 log(1 + 100 log 10) = 10.9 to one decimal
ok(abs(2 * math.log1p(100 * math.log(10)) - 10.9) < 0.05, "quoted 10.9")
print(f"online law: {checks - fails} checks passed, {fails} failed")
sys.exit(1 if fails else 0)
