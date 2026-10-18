"""The gap law (Theorem I), the learning rate of square-root sampling, the spiking selector and the
table of costs computed from the data of Chen, Zhao and Cohan (arXiv:2607.01233)."""
import json, math, os, random

fails = 0; checks = 0

def ok(cond, msg):
    global fails, checks
    checks += 1
    if not cond:
        fails += 1; print("FAIL", msg)

def norm(v):
    s = sum(v)
    return [x / s for x in v]

def cost(pi, q):
    return sum(a / b for a, b in zip(pi, q) if a > 0)

def sqrt_profile(pi):
    return norm([math.sqrt(x) for x in pi])

rng = random.Random(20261018)
# (i)-(iii) and the cost K of copying the needs
for trial in range(2000):
    K = rng.randint(1, 25)
    pi = norm([math.exp(rng.gauss(0, 1.5)) for _ in range(K)])
    q = norm([math.exp(rng.gauss(0, 1.5)) for _ in range(K)])
    S = sum(math.sqrt(x) for x in pi)
    r = sqrt_profile(pi)
    C = cost(pi, q)
    ok(C >= S * S * (1 - 1e-12), "lower bound")
    ok(abs(cost(pi, r) - S * S) < 1e-9 * S * S, "attained at square-root sampling")
    chi2 = sum((a - b) ** 2 / b for a, b in zip(r, q))
    ok(abs(C - S * S * (1 + chi2)) < 1e-9 * C, "chi-squared identity")
    lam = rng.uniform(0.01, 1)
    qm = [(1 - lam) * a + lam * b for a, b in zip(q, r)]
    ok(cost(pi, qm) <= S * S / lam * (1 + 1e-12), "mixture bound")
    ok(abs(cost(pi, pi) - K) < 1e-9 * K and K >= S * S * (1 - 1e-12), "copying the needs costs K >= S^2")
    # the cost of the mixture decreases in lam
    lams = sorted(rng.uniform(0, 1) for _ in range(5))
    cs = [cost(pi, [(1 - l) * a + l * b for a, b in zip(q, r)]) for l in lams]
    ok(all(x >= y * (1 - 1e-12) for x, y in zip(cs, cs[1:])), "mixture cost decreasing")

# the mean number of draws is the cost, by simulation
for trial in range(20):
    K = rng.randint(2, 8)
    pi = norm([rng.random() + 0.05 for _ in range(K)])
    q = norm([rng.random() + 0.05 for _ in range(K)])
    tot, n = 0, 20000
    for _ in range(n):
        need = rng.choices(range(K), pi)[0]
        d = 1
        while rng.choices(range(K), q)[0] != need:
            d += 1
        tot += d
    C = cost(pi, q)
    sd = math.sqrt(sum(a * (2 - b) / b ** 2 for a, b in zip(pi, q)) - C * C)
    ok(abs(tot / n - C) < 5 * sd / math.sqrt(n), "simulated draws")

# learning: E[cost(pi, sqrt(estimated pi))] / S^2 = 1 + beta / (4 n) + o(1/n)
def learned_ratio(pi, n, trials, alpha=0.5):
    K = len(pi); S2 = sum(map(math.sqrt, pi)) ** 2
    tot = 0.0
    for _ in range(trials):
        c = [0] * K
        for j in rng.choices(range(K), pi, k=n):
            c[j] += 1
        tot += cost(pi, sqrt_profile([x + alpha for x in c])) / S2
    return tot / trials

for trial in range(6):
    K = rng.randint(2, 7)
    pi = norm([rng.random() + 0.1 for _ in range(K)])
    S = sum(map(math.sqrt, pi))
    beta = sum(x ** -0.5 for x in pi) / S - K / S ** 2
    ok(beta >= (K * K - K) / S ** 2 - 1e-12, "beta >= K(K-1)/S^2")
    n = 4000
    got = learned_ratio(pi, n, 3000) - 1
    ok(abs(got * 4 * n / beta - 1) < 0.15, f"learning rate {got * 4 * n / beta:.3f}")

# the spiking selector: a race of Poisson neurons picks k with probability lam_k / sum lam, and the
# reward rule makes w_k = (delta/2) log(c_k + alpha) + const, so the choice is sqrt(c_k + alpha)
for trial in range(10):
    K = rng.randint(2, 6); delta = rng.uniform(0.1, 1); alpha = 0.5
    counts = [0.0] * K; w = [1.0] * K
    for _ in range(rng.randint(0, 60)):
        k = rng.randrange(K)
        w[k] += 0.5 * delta * math.log((counts[k] + 1 + alpha) / (counts[k] + alpha))
        counts[k] += 1
    rates = [math.exp(x / delta) for x in w]
    p = norm(rates)
    t = sqrt_profile([c + alpha for c in counts])
    ok(max(abs(a - b) for a, b in zip(p, t)) < 1e-12, "reward rule gives square-root sampling")
    hits = [0] * K; n = 40000
    for _ in range(n):
        times = [rng.expovariate(x) for x in rates]
        hits[times.index(min(times))] += 1
    ok(max(abs(h / n - a) for h, a in zip(hits, p)) < 0.012, "first spike of a Poisson race")

# the table of the paper from the data
here = os.path.dirname(os.path.abspath(__file__))
data = json.load(open(os.path.join(here, "..", "paper", "figures", "src", "data", "idea_gap.json")))
expect = {"opportunity": {"opt": 6.503, "Human": 7.00, "Claude-Sonnet-4.6": 14.14, "GPT-OSS-120B": 27.81,
                          "Qwen3-8B": 23.38},
          "method": {"opt": 6.445, "Human": 7.00, "Claude-Sonnet-4.6": 9.74, "GPT-OSS-120B": 20.94}}
for ax, ex in expect.items():
    pi = norm(data["shares"]["Human"][ax])
    S2 = sum(map(math.sqrt, pi)) ** 2
    ok(abs(S2 - ex["opt"]) < 5e-4, f"optimum {ax}")
    for src, v in ex.items():
        if src != "opt":
            ok(abs(cost(pi, norm(data["shares"][src][ax])) - v) < 5e-3, f"cost {src} {ax}")
    for src, sh in data["shares"].items():
        q = norm(sh[ax]); r = sqrt_profile(pi)
        ok(cost(pi, [(a + b) / 2 for a, b in zip(q, r)]) <= 2 * S2, f"50/50 bound {src}")

print(f"check_gap: {checks} checks, {fails} failures")
raise SystemExit(1 if fails else 0)
