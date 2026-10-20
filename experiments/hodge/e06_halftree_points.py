"""C-type half-trees through the skyscraper of one point q of order two (candidate C8):
L(2k) -ev_q-> O_{E[2]} -X-> L(2 l_1) -> ... -> L(2k), every bracketing with one homotopy, generic classes.
In this Cech model the value depends on the point: e.g. k = 5, l = 0,2,3,4 gives 0 at oo, P1, P-1 and
nonzero at P0; so vanishing at oo alone excludes nothing.

    python3 e06_halftree_points.py 5 0,2,3,4
"""
import sys, random

from fractions import Fraction
import e0_twisted as T, e06_points as Pt
A = Pt.FunctionsOnE2(); Z = Pt.Z
k = int(sys.argv[1]) if len(sys.argv) > 1 else 5
ls = [int(a) for a in sys.argv[2].split(",")] if len(sys.argv) > 2 else [0, 2, 3, 4]
objs = [T.L(2 * k), Z] + [T.L(2 * a) for a in ls] + [T.L(2 * k)]
n_in = len(objs) - 1
def name(e):
    # which point: compose with the sections 1, x, x - 1, x + 1 of O(2 oo) (zero at oo, P0, P1, P-1)
    R = T.retract(T.L(2), Z); out = []
    for nm, sec in (("oo", {0: 1}), ("P0", {2: 1}), ("P1", {2: 1, 0: -1}), ("P-1", {2: 1, 0: 1})):
        s = T.Mor(T.L(0), T.L(2), 0, {(0, 0): Pt.E.incl(0, 2, 0, {n: Fraction(c) for n, c in sec.items()})})
        f = R.iota(0, [Fraction(3 ** i + 7) for i in range(R.dim(0))])
        fe = T.retract(T.L(2), Z).iota(0, T.retract(T.L(2), Z).proj(T.mu(f, T.retract(Z, Z).iota(0, e))))
        v = T.retract(T.L(0), Z).proj(T.mu(s, fe))
        if not any(v): out.append(nm)
    return out
def ip(f):
    R = T.retract(f.X, f.Y); return R.iota(f.n, R.proj(f))
rng = random.Random(7)
def gen(X, Y):
    R = T.retract(X, Y); n = [m for m in range(-1, 3) if R.dim(m)]
    assert len(n) == 1
    return R.iota(n[0], [Fraction(rng.choice([-1, 1]) * rng.randint(1, 10 ** 6)) for _ in range(R.dim(n[0]))])
for e in A.idem:
    eq = T.retract(Z, Z).iota(0, e)
    xs = [gen(objs[t], objs[t + 1]) for t in range(n_in)]
    xs[0] = ip(T.mu(xs[0], eq))
    def trees(a, b, top=True):
        if b - a == 1:
            yield xs[a]; return
        for m in range(a + 1, b):
            for u in trees(a, m, False):
                for v in trees(m, b, False):
                    w = T.mu(u, v)
                    yield w
                    if not top and not w.iszero():
                        yield ip(w)
    tot = bad = 0
    for a in range(n_in):
        for b in range(a + 2, n_in + 1):
            if (a, b) == (0, n_in):
                continue
            for Lv in ([None] if a == 0 else list(trees(0, a))):
                for Mv in trees(a, b, False):
                    if Mv.iszero():
                        continue
                    hM = T.retract(Mv.X, Mv.Y).h(Mv)
                    if hM.iszero():
                        continue
                    for Rv in ([None] if b == n_in else list(trees(b, n_in))):
                        z = hM
                        if Lv is not None: z = T.mu(Lv, z)
                        if Rv is not None: z = T.mu(z, Rv)
                        if z.iszero(): continue
                        tot += 1
                        bad += any(T.retract(z.X, z.Y).proj(z))
    print("point", name(e), "half-trees:", tot, "nonzero:", bad, flush=True)
