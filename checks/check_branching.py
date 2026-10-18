"""Branching takeoff: near-critical survival, contamination mean, amplified checks."""
import math, random, sys
import numpy as np
rng = np.random.default_rng(20261018)
fails = 0; checks = 0

def ok(cond, msg):
    global fails, checks
    checks += 1
    if not cond:
        fails += 1; print("FAIL", msg)

def survival(one_minus_pgf, lo):
    """Largest root q of q = 1 - f(1 - q); one_minus_pgf(q) = 1 - f(1 - q) computed stably."""
    a, b = lo, 1.0
    g = lambda q: one_minus_pgf(q) - q
    if g(a) <= 0:
        return 0.0
    for _ in range(200):
        c = (a + b) / 2
        if g(c) > 0: a = c
        else: b = c
    return (a + b) / 2

# (A) near-critical survival: q = 2(m-1)/sigma^2 + O((m-1)^2)
for m in [1.001, 1.01, 1.05, 1.1, 1.2]:
    lo = 1e-3 * (m - 1)
    q = survival(lambda t: -math.expm1(-m * t), lo)        # Poisson(m), sigma^2 = m
    ok(abs(q - 2 * (m - 1) / m) <= 3 * (m - 1) ** 2, f"poisson m={m} q={q}")
    for k in [2, 5, 20]:
        pr = m / k                                         # Binomial(k, m/k)
        s2 = k * pr * (1 - pr)
        q = survival(lambda t: -math.expm1(k * math.log1p(-pr * t)), lo / max(1, s2))
        ok(abs(q - 2 * (m - 1) / s2) <= 6 * (m - 1) ** 2 / s2 ** 2, f"binomial k={k} m={m}")
for m in [0.5, 0.9, 1.0]:
    ok(survival(lambda t: -math.expm1(-m * t), 1e-9) < 1e-6, f"extinction m={m}")

# (B) contamination mean: E F = mu (1 - gamma) sum_k m^k delta_k
def simulate(mu, gamma, eta, deltas, T):
    tot = 0
    for _ in range(T):
        z = 1
        for d in deltas:
            if z == 0: break
            N = rng.poisson(mu, size=z).sum()
            good = rng.binomial(N, gamma)
            bad = N - good
            tot += rng.binomial(bad, d)
            z = rng.binomial(good, 1 - eta)
    return tot / T
for (mu, gamma, eta) in [(2.0, 0.8, 0.1), (3.0, 0.5, 0.2), (1.6, 0.9, 0.05)]:
    m = mu * gamma * (1 - eta)
    K = 10
    for deltas in [[0.05] * K, [0.2 * 0.5 ** k for k in range(K)],
                   [min(1.0, (2 * m) ** (-k)) for k in range(K)]]:
        T = 40000
        exact = mu * (1 - gamma) * sum(m ** k * d for k, d in enumerate(deltas))
        est = simulate(mu, gamma, eta, deltas, T)
        ok(abs(est - exact) <= 0.05 * exact + 0.01, f"contamination mu={mu} est={est} exact={exact}")

# (C) amplified checks: r_k = ceil(k log(2m) / log(1/eps)) gives m^k eps^r_k <= 2^-k
for m in [1.1, 1.5, 3.0, 10.0]:
    for eps in [0.5, 0.1, 0.01]:
        L = math.log(1 / eps)
        for k in range(0, 200):
            r = math.ceil(k * math.log(2 * m) / L)
            ok(k * math.log(m) - r * L <= -k * math.log(2) + 1e-9, f"amplified m={m} eps={eps} k={k}")
print(f"branching: {checks} checks, {fails} failed")
sys.exit(1 if fails else 0)
