"""Subagents (Theorem H) and cascades (Theorem on weak before strong checks)."""
import math, random, sys
from common import entropy
fails = 0; checks = 0

def ok(cond, msg):
    global fails, checks
    checks += 1
    if not cond:
        fails += 1; print("FAIL", msg)

def ceil_sched(a, A, theta, L):
    return [math.ceil(math.log(A / (theta * x)) / L) for x in a]

rng = random.Random(20261018)
for trial in range(300):
    n = rng.randint(2, 30)
    m = rng.randint(1, min(6, n))
    a = [math.exp(rng.gauss(0, 2)) for _ in range(n)]
    g = [rng.randrange(m) for _ in range(n)]
    for k in range(m):  # every group nonempty
        g[k] = k
    A = sum(a)
    p = [x / A for x in a]
    Ak = [sum(x for x, gi in zip(a, g) if gi == k) for k in range(m)]
    P = [x / A for x in Ak]
    Hk = [entropy([x / Ak[k] for x, gi in zip(a, g) if gi == k]) for k in range(m)]
    # (i) chain rule
    ok(abs(entropy(p) - entropy(P) - sum(Pk * h for Pk, h in zip(P, Hk))) < 1e-10, "chain rule")
    # (ii) price of a split, exactly
    L = math.log(1 / rng.choice([0.5, 0.1, 0.9]))
    theta = rng.choice([1.0, 0.1, 1e-4])
    tk = [math.exp(rng.gauss(0, 1)) for _ in range(m)]
    s = sum(tk) / (theta * rng.uniform(0.3, 1.0))
    tk = [t / s for t in tk]
    Th = sum(tk)
    q = [t / Th for t in tk]
    groups = sum(Ak[k] / L * (Hk[k] + math.log(1 / tk[k])) for k in range(m))
    flat = A / L * (entropy(p) + math.log(1 / theta))
    D = sum(Pk * math.log(Pk / qk) for Pk, qk in zip(P, q))
    price = A / L * (D + math.log(theta / Th))
    ok(abs(groups - flat - price) < 1e-8 * max(1, abs(flat)), "split price identity")
    ok(price >= -1e-10, "split price nonnegative")
    # even split: price log m - H(P)
    ev = sum(Ak[k] / L * (Hk[k] + math.log(m / theta)) for k in range(m)) - flat
    ok(abs(ev - A / L * (math.log(m) - entropy(P))) < 1e-8 * max(1, abs(flat)), "even split price")
    # (iii) proportional split reproduces the flat ceiling schedule
    r_flat = ceil_sched(a, A, theta, L)
    agree = True
    for k in range(m):
        idx = [i for i in range(n) if g[i] == k]
        rk = ceil_sched([a[i] for i in idx], Ak[k], theta * P[k], L)
        agree &= all(r_flat[i] == x for i, x in zip(idx, rk))
    ok(agree, "proportional split equals flat schedule")
    ok(sum(math.exp(-L * r) for r in r_flat) <= theta * (1 + 1e-9), "union sound")
    # (iv) tree identity: group subgroups again
    sub = [rng.randrange(2) for _ in range(n)]
    tree = A * entropy(P)
    for k in range(m):
        idx = [i for i in range(n) if g[i] == k]
        parts = [sum(a[i] for i in idx if sub[i] == j) for j in range(2)]
        parts = [x for x in parts if x > 0]
        tree += Ak[k] * entropy([x / Ak[k] for x in parts])
        for j in range(2):
            leaf = [a[i] for i in idx if sub[i] == j]
            if leaf:
                tree += sum(leaf) * entropy([x / sum(leaf) for x in leaf])
    ok(abs(tree - A * entropy(p)) < 1e-8 * A * max(1, entropy(p)), "tree identity")

def E(r, b, c, rho, eps):
    return b * r + c * (1 - rho) + c * rho * eps ** r

for trial in range(2000):
    eps = rng.choice([0.5, 0.1, 0.9, rng.uniform(0.01, 0.99)])
    L = math.log(1 / eps)
    c = math.exp(rng.uniform(-2, 8))
    rho = rng.uniform(0.01, 0.999)
    b = c * rho * L * math.exp(-rng.uniform(0, 12))
    best = min(E(r, b, c, rho, eps) for r in range(0, 3000))
    lo = c * (1 - rho) + b / L * (1 + math.log(c * rho * L / b))
    rs = math.ceil(math.log(c * rho * L / b) / L)
    ok(lo - 1e-9 * c <= best, "cascade lower bound")
    ok(E(rs, b, c, rho, eps) <= lo + b + 1e-9 * c, "cascade upper bound at r*")
    ok(best <= c + 1e-12, "cascade never worse than strong check alone")
# the example of the text: c = 1000, b = 1, eps = 1/2, rho = 0.9
c, b, eps, rho = 1000, 1, 0.5, 0.9
L = math.log(2)
vals = [E(r, b, c, rho, eps) for r in range(60)]
rbest = min(range(60), key=lambda r: vals[r])
ok(rbest == 9, f"example best r = {rbest}")
ok(math.ceil(math.log(c * rho * L / b) / L) == 10 and vals[10] <= vals[9] + b, "example ceiling rule within b")
ok(abs(vals[9] - 110.8) < 0.05, f"example cost {vals[9]}")
ok(abs(c * (1 - rho) + b / L * (1 + math.log(c * rho * L / b)) - 110.7) < 0.05, "example lower bound")
print(f"subagents and cascades: {checks - fails} checks passed, {fails} failed")
sys.exit(1 if fails else 0)
