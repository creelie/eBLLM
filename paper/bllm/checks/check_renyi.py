"""Renyi law for polynomially sound checks and the duality criterion."""
import math, random, sys
random.seed(11)
fails = 0; checks = 0
for trial in range(400):
    n = random.randint(1, 12)
    a = [random.uniform(0.01, 3.0) for _ in range(n)]
    s = random.choice([0.25, 0.5, 1.0, 2.0, 3.0])
    theta = random.choice([1.0, 0.3, 0.05, 0.001])
    al = 1 / (1 + s)
    closed = theta ** (-s) * sum(x ** al for x in a) ** (1 + s)
    # the minimiser delta_i proportional to a_i^alpha
    S = sum(x ** al for x in a)
    d = [theta * x ** al / S for x in a]
    val = sum(x * di ** (-s) for x, di in zip(a, d))
    checks += 1
    if abs(val - closed) > 1e-9 * closed:
        fails += 1; print("FAIL attain", val, closed)
    # Renyi form A theta^-s exp(s H_alpha(p))
    A = sum(a); p = [x / A for x in a]
    Ha = math.log(sum(x ** al for x in p)) / (1 - al)
    checks += 1
    if abs(A * theta ** (-s) * math.exp(s * Ha) - closed) > 1e-9 * closed:
        fails += 1; print("FAIL renyi form")
    # no feasible point does better
    for _ in range(50):
        w = [random.random() ** 3 + 1e-9 for _ in range(n)]
        W = sum(w); dd = [theta * x / W for x in w]
        v = sum(x * di ** (-s) for x, di in zip(a, dd))
        checks += 1
        if v < closed * (1 - 1e-12):
            fails += 1; print("FAIL lower", v, closed)
# Shannon limit: (cost - A)/s -> sum a log(1/delta) behaviour, i.e. (Renyi law - A)/s -> A(H + log 1/theta)
for trial in range(50):
    n = random.randint(1, 10)
    a = [random.uniform(0.01, 3.0) for _ in range(n)]
    theta = random.choice([0.5, 0.1, 0.01])
    A = sum(a); p = [x / A for x in a]; H = -sum(x * math.log(x) for x in p)
    s = 1e-6; al = 1 / (1 + s)
    closed = theta ** (-s) * sum(x ** al for x in a) ** (1 + s)
    lim = (closed - A) / s
    checks += 1
    if abs(lim - A * (H + math.log(1 / theta))) > 1e-3 * A * (H + math.log(1 / theta)) + 1e-6:
        fails += 1; print("FAIL shannon limit", lim, A * (H + math.log(1 / theta)))
print(f"renyi: {checks} checks, {fails} failed")
sys.exit(1 if fails else 0)
