"""Step and outcome gating: exact formulas against Monte Carlo."""
import math, random, sys
random.seed(7)
fails = 0; checks = 0

def step_exact(rho, eta, delta):
    s = [(1 - r) * (1 - eta) + r * delta for r in rho]
    cost = sum(1 / x for x in s)
    prec = math.prod((1 - r) * (1 - eta) / x for r, x in zip(rho, s))
    return cost, prec

def outcome_exact(rho, eta, delta):
    c = math.prod(1 - r for r in rho)
    s = c * (1 - eta) + (1 - c) * delta
    return len(rho) / s, c * (1 - eta) / s

def step_mc(rho, eta, delta, T):
    cost = 0; good = 0
    for _ in range(T):
        ok = True
        for r in rho:
            while True:
                cost += 1
                correct = random.random() >= r
                acc = (random.random() >= eta) if correct else (random.random() < delta)
                if acc:
                    ok = ok and correct
                    break
        good += ok
    return cost / T, good / T

def outcome_mc(rho, eta, delta, T):
    cost = 0; good = 0
    for _ in range(T):
        while True:
            cost += len(rho)
            correct = all(random.random() >= r for r in rho)
            acc = (random.random() >= eta) if correct else (random.random() < delta)
            if acc:
                good += correct
                break
    return cost / T, good / T

for trial in range(12):
    n = random.randint(2, 8)
    rho = [random.uniform(0.05, 0.4) for _ in range(n)]
    eta = random.choice([0.0, 0.05, 0.2])
    delta = random.choice([0.0, 0.02, 0.1])
    T = 20000
    for exact, mc in ((step_exact, step_mc), (outcome_exact, outcome_mc)):
        ce, pe = exact(rho, eta, delta)
        cm, pm = mc(rho, eta, delta, T)
        checks += 1
        # five standard errors, generous for the cost (geometric) and the precision (Bernoulli)
        tol_c = 6 * ce / math.sqrt(T) * 3 + 1e-9
        tol_p = 6 * math.sqrt(max(pe * (1 - pe), 1e-6) / T) + 1e-9
        if abs(cm - ce) > tol_c or abs(pm - pe) > tol_p:
            fails += 1; print("FAIL", exact.__name__, rho, eta, delta, ce, cm, pe, pm)
# exact separation ratio for constant rho with perfect verifiers
for n in (5, 20, 60):
    for r in (0.05, 0.1, 0.3):
        cs, _ = step_exact([r] * n, 0, 0); co, _ = outcome_exact([r] * n, 0, 0)
        checks += 1
        if abs(co / cs - (1 - r) ** (-(n - 1))) > 1e-9 * co / cs:
            fails += 1; print("FAIL ratio", n, r)
# precision bounds of Theorem 4.2(d)
for trial in range(500):
    n = random.randint(1, 50)
    rho = [random.uniform(0.0, 0.9) for _ in range(n)]
    eta = random.uniform(0, 0.5); delta = random.uniform(0, 0.5)
    _, P = step_exact(rho, eta, delta)
    x = [r * delta / ((1 - r) * (1 - eta)) for r in rho]
    lo = math.exp(-sum(x)); hi = math.exp(-sum(t / (1 + t) for t in x))
    checks += 1
    if not (lo - 1e-12 <= P <= hi + 1e-12):
        fails += 1; print("FAIL bounds", P, lo, hi)
print(f"gating: {checks} checks, {fails} failed")
sys.exit(1 if fails else 0)
