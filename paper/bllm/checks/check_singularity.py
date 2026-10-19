"""Sound singularities: power-law price, logarithmic families, duality instances, Osgood takeoffs."""
import math, sys
import mpmath as mp
from common import entropy
mp.mp.dps = 30
fails = 0; checks = 0

def ok(cond, msg):
    global fails, checks
    checks += 1
    if not cond:
        fails += 1; print("FAIL", msg)

# (A) power law a_n = n^-p: A = zeta(p), sum a log(1/a) = -p zeta'(p)
for p in [1.05, 1.1, 1.25, 1.5, 2.0, 3.0]:
    A = mp.zeta(p)
    S = -p * mp.zeta(p, 1, 1)
    ok(abs(S + p * mp.diff(mp.zeta, p)) < mp.mpf(10)**-15 * abs(S), f"zeta' two ways p={p}")
    if p >= 1.5:
        S2 = mp.nsum(lambda n: p * mp.log(n) / n**p, [1, mp.inf], method='euler-maclaurin')
        ok(abs(S - S2) < mp.mpf(10)**-12 * abs(S), f"zeta' series p={p}")
    H = mp.log(A) + S / A
    # entropy bounds for a truncated chain with the ceiling schedule
    for L in [math.log(2), 1.0, math.log(10)]:
        for theta in [0.1, 0.01, 1e-6]:
            N = 4000
            a = [n ** (-p) for n in range(1, N + 1)]
            AN = sum(a)
            r = [math.ceil(math.log(AN / (theta * x)) / L) for x in a]
            F = sum(math.exp(-L * ri) for ri in r)
            V = sum(x * ri for x, ri in zip(a, r))
            HN = sum(x / AN * math.log(AN / x) for x in a)
            lo = AN / L * (HN + math.log(1 / theta))
            ok(F <= theta * (1 + 1e-12), f"budget p={p}")
            ok(lo - 1e-9 <= V <= lo + AN + 1e-9, f"cost bounds p={p}")
# (B) asymptotics as p -> 1: (p-1)^2 zeta'(p) -> -1, (p-1) zeta(p) -> 1, (p-1) H -> 1
for e in [mp.mpf('1e-2'), mp.mpf('1e-3'), mp.mpf('1e-4')]:
    p = 1 + e
    z = mp.zeta(p); dz = mp.diff(mp.zeta, p)
    H = mp.log(z) - p * dz / z
    ok(abs(e * z - 1) < 2 * e, f"zeta pole {e}")
    ok(abs(e * e * dz + 1) < 3 * e, f"zeta' pole {e}")
    ok(abs(e * H - 1) < 10 * e * abs(mp.log(e)), f"entropy pole {e}")
# (C) logarithmic families a_n = 1/(n log^b n): condensed series
#     2^k a_{2^k} = (k log 2)^-b,  2^k a log(1/a) at 2^k ~ (k log 2)^(1-b)
for b in [1.5, 2.0, 2.5, 3.0]:
    for k in [10, 100, 1000]:
        n = mp.mpf(2) ** k
        a = 1 / (n * mp.log(n) ** b)
        ok(abs(n * a - (k * mp.log(2)) ** (-b)) < mp.mpf(10)**-20, f"condensed a b={b} k={k}")
        t = n * a * mp.log(1 / a)
        ratio = t / (k * mp.log(2)) ** (1 - b)
        ok(1 <= ratio <= 1 + (b * mp.log(k * mp.log(2)) + 1) / (k * mp.log(2)) + 1e-20,
           f"condensed entropy b={b} k={k}")
# (D) duality: exponential checks psi(u) = (1 + log(uL))/L for uL >= 1; polynomial checks
for L in [0.5, 1.0, 2.0]:
    for u in [1 / L, 2 / L, 10 / L, 1000 / L]:
        f = lambda d: math.log(1 / d) / L + u * d
        grid = min(f(10 ** (-j / 200)) for j in range(0, 2000))
        exact = (1 + math.log(u * L)) / L
        ok(grid >= exact - 1e-12 and grid - exact < 1e-4, f"psi exp L={L} u={u}")
for s in [0.5, 1.0, 2.0]:
    for u in [0.5, 1.0, 10.0, 100.0]:
        f = lambda d: d ** (-s) + u * d
        dstar = min(1.0, (s / u) ** (1 / (1 + s)))
        exact = f(dstar)
        grid = min(f(10 ** (-j / 300)) for j in range(0, 3000))
        ok(grid >= exact - 1e-12 and grid - exact < 1e-3 * exact, f"psi poly s={s} u={u}")
        if dstar < 1:
            closed = (1 + s) * s ** (-s / (1 + s)) * u ** (s / (1 + s))
            ok(abs(exact - closed) < 1e-12 * closed, f"psi poly closed s={s} u={u}")
# (E) Osgood takeoffs (Proposition osgood): geometric entropy formula, its limit, the
# bounds of part (i) on long truncations, and the polynomial value of part (iv)
def H_geom(q):
    return math.log(1 / (1 - q)) + q / (1 - q) * math.log(1 / q)
for lam in [1.5, 2.0, 4.0]:
    for alpha in [1.05, 1.3, 2.0, 3.0]:
        q = lam ** (-(alpha - 1))
        N = int(60 / (1 - q)) + 50
        p = [(1 - q) * q ** n for n in range(N)]
        tot = sum(p)
        ok(abs(entropy([x / tot for x in p]) - H_geom(q)) < 1e-6, f"geometric entropy lam={lam} alpha={alpha}")
        pw = sum(x ** (1 / 2) for x in p)
        ok(abs(pw - (1 - q) ** 0.5 / (1 - q ** 0.5)) < 1e-6 * pw, f"geometric renyi sum lam={lam} alpha={alpha}")
    for e in [1e-3, 1e-4, 1e-5]:
        u = e * math.log(lam); q = math.exp(-u)
        ok(abs(H_geom(q) - (math.log(1 / u) + 1)) < 2 * u, f"geometric entropy limit lam={lam} e={e}")
for alpha in [1.5, 2.0, 3.0]:
    for kappa in [0.1, 1.0]:
        for th in [1e-2, 1e-6]:
            L = math.log(2); N = 200000
            g = [1 / n ** alpha for n in range(1, N + 1)]
            G = sum(g); a = [kappa * x for x in g]; A = sum(a)
            Hp = entropy([x / A for x in a])
            r = [math.ceil(math.log(A / (th * x)) / L) for x in a]
            ok(sum(0.5 ** k for k in r) <= th * (1 + 1e-12), f"osgood sound alpha={alpha} kappa={kappa} th={th}")
            ratio = (G + sum(x * k for x, k in zip(a, r))) / G
            lo = 1 + kappa / L * (Hp + math.log(1 / th))
            ok(lo - 1e-9 <= ratio <= lo + kappa + 1e-9, f"osgood ratio alpha={alpha} kappa={kappa} th={th}")
for alpha, s in [(3.0, 1.0), (2.5, 0.5), (4.0, 2.0)]:
    beta = 1 / (1 + s); N = 400000
    a = [1 / n ** alpha for n in range(1, N + 1)]
    S = sum(x ** beta for x in a)
    th = 1e-3
    d = [th * x ** beta / S for x in a]
    cost = sum(x * y ** (-s) for x, y in zip(a, d))
    ok(abs(cost - th ** (-s) * S ** (1 + s)) < 1e-9 * cost and sum(d) <= th * (1 + 1e-12), f"poly takeoff value alpha={alpha} s={s}")
print(f"singularity: {checks} checks, {fails} failed")
sys.exit(1 if fails else 0)
