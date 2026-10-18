"""Sound singularities: power-law price, logarithmic families, duality instances."""
import math, sys
import mpmath as mp
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
print(f"singularity: {checks} checks, {fails} failed")
sys.exit(1 if fails else 0)
