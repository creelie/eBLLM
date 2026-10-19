"""Twisted complexes of line bundles on E_0 (skyscrapers of the points of order two) and their exact products.

An object is a list of components (a_i, s_i), meaning O(a_i oo)[s_i], with a strictly upper triangular
twisting cochain delta of total degree 1. A morphism X -> Y of total degree n has components phi_ij, Cech
cochains of Hom(O(a_i oo), O(b_j oo)) of degree p = n - s_i + t_j. Products are written left to right ("phi
then psi"); the differential of a component is (-1)^{s_i} d, and the twisted differential is
D(phi) = d phi + delta_X phi - (-1)^n phi delta_Y. The homotopy of e0_ainf is perturbed by the twisting
(basic perturbation lemma) and then reduced over Q to the cohomology, which gives a special deformation
retract of each Hom complex onto its cohomology; the transferred A-infinity products follow by the tree formula.

The skyscraper of oo is O_oo = [O(-oo)[1] -> O] with delta = 1 in H^0(O(oo)).

    python3 e0_twisted.py
"""
from fractions import Fraction
import random
import e0_ainf as E


class Obj:
    def __init__(self, comps, delta=None):
        self.comps = comps            # [(a, s)]
        self.delta = delta or {}      # {(i, j): Elt}, total degree 1

    def __repr__(self):
        return f"Obj({self.comps})"


def line(a):
    return Obj([(a, 0)])


def skyscraper_oo():
    one = E.Elt(-1, 0, 0, {0: Fraction(1)}, {0: Fraction(1)})
    return Obj([(-1, 1), (0, 0)], {(0, 1): one})


class Mor:
    def __init__(self, X, Y, n, comp=None):
        self.X, self.Y, self.n = X, Y, n
        self.c = {k: v for k, v in (comp or {}).items() if not v.iszero()}

    def __add__(self, o):
        assert (self.X, self.Y, self.n) == (o.X, o.Y, o.n)
        c = dict(self.c)
        for k, v in o.c.items():
            c[k] = c[k] + v if k in c else v
        return Mor(self.X, self.Y, self.n, c)

    def scale(self, s):
        return Mor(self.X, self.Y, self.n, {k: v.scale(s) for k, v in self.c.items()})

    def iszero(self):
        return not self.c


def cech_deg(X, Y, n, i, j):
    return n - X.comps[i][1] + Y.comps[j][1]


def mu(f, g):
    assert f.Y is g.X
    out = {}
    for (i, j), x in f.c.items():
        for (j2, k), y in g.c.items():
            if j2 != j:
                continue
            z = E.mu(x, y)
            if z.deg not in (0, 1):
                continue
            out[(i, k)] = out[(i, k)] + z if (i, k) in out else z
    return Mor(f.X, g.Y, f.n + g.n, out)


def delta_mor(X):
    return Mor(X, X, 1, X.delta)


def dtot(f):
    out = {}
    for (i, j), x in f.c.items():
        z = E.dd(x)
        if z.deg in (0, 1):
            out[(i, j)] = z.scale((-1) ** f.X.comps[i][1])
    return Mor(f.X, f.Y, f.n + 1, out)


def pert(f):
    a = mu(delta_mor(f.X), f) if f.X.delta else Mor(f.X, f.Y, f.n + 1)
    b = mu(f, delta_mor(f.Y)) if f.Y.delta else Mor(f.X, f.Y, f.n + 1)
    return a + b.scale(-((-1) ** f.n))


def D(f):
    return dtot(f) + pert(f)


def h0(f):
    out = {}
    for (i, j), x in f.c.items():
        if x.deg == 1:
            z = E.h(x, 1)
            out[(i, j)] = z.scale((-1) ** f.X.comps[i][1])
    return Mor(f.X, f.Y, f.n - 1, out)


def basis0(X, Y, n):
    """Basis of the untwisted cohomology: (i, j, p, basis index n_b)."""
    out = []
    for i, (a, s) in enumerate(X.comps):
        for j, (b, t) in enumerate(Y.comps):
            p = n - s + t
            if p in (0, 1):
                for nb in E.cohom_basis(b - a, p):
                    out.append((i, j, p, nb))
    return out


def iota0(X, Y, n, vec):
    out = {}
    for (i, j, p, nb), v in vec.items():
        if v == 0:
            continue
        a, b = X.comps[i][0], Y.comps[j][0]
        z = E.incl(a, b, p, {nb: v})
        out[(i, j)] = out[(i, j)] + z if (i, j) in out else z
    return Mor(X, Y, n, out)


def p0(f):
    vec = {}
    for (i, j), x in f.c.items():
        p = x.deg
        for nb, v in E.proj(x).items():
            vec[(i, j, p, nb)] = vec.get((i, j, p, nb), 0) + v
    return {k: v for k, v in vec.items() if v != 0}


def A_op(f):
    """A = sum_k (-1)^k (P h0)^k P."""
    tot = None
    cur = pert(f)
    sgn = 1
    while not cur.iszero():
        tot = cur.scale(sgn) if tot is None else tot + cur.scale(sgn)
        cur = pert(h0(cur))
        sgn = -sgn
    return tot if tot is not None else Mor(f.X, f.Y, f.n + 1)


def iota1(X, Y, n, vec):
    x = iota0(X, Y, n, vec)
    return x + h0(A_op(x)).scale(-1)


def p1(f):
    v = p0(f)
    w = p0(A_op(h0(f)))
    for k, a in w.items():
        v[k] = v.get(k, 0) - a
    return {k: a for k, a in v.items() if a != 0}


def h1(f):
    return h0(f) + h0(A_op(h0(f))).scale(-1)


def dH(X, Y, n, vec):
    return p0(A_op(iota0(X, Y, n, vec)))


# finite linear algebra over Q for the second reduction
def rref_solve(cols, target):
    """Solve sum c_k cols[k] = target (dicts); return coefficients or None."""
    keys = sorted({k for c in cols for k in c} | set(target), key=str)
    m = [[Fraction(c.get(k, 0)) for c in cols] + [Fraction(target.get(k, 0))] for k in keys]
    ncol = len(cols)
    piv = []
    r = 0
    for cidx in range(ncol):
        pr = next((i for i in range(r, len(m)) if m[i][cidx] != 0), None)
        if pr is None:
            continue
        m[r], m[pr] = m[pr], m[r]
        inv = Fraction(1) / Fraction(m[r][cidx])
        m[r] = [v * inv for v in m[r]]
        for i in range(len(m)):
            if i != r and m[i][cidx] != 0:
                fac = m[i][cidx]
                m[i] = [a - fac * b for a, b in zip(m[i], m[r])]
        piv.append(cidx)
        r += 1
    for i in range(r, len(m)):
        if m[i][-1] != 0:
            return None
    sol = [Fraction(0)] * ncol
    for i, cidx in enumerate(piv):
        sol[cidx] = m[i][-1]
    return sol


class Retract:
    """SDR of Hom^*(X, Y) onto its cohomology, degrees nmin..nmax.

    In each degree the finite complex (H0, dH) is split as H0_n = Hn + In + Cn: Cn a complement of the cocycles,
    In = dH(C_{n-1}), Hn a complement of In in the cocycles. p2 and h2 read off the Hn and In coordinates."""

    def __init__(self, X, Y, nmin=-3, nmax=3):
        self.X, self.Y = X, Y
        self.B = {n: basis0(X, Y, n) for n in range(nmin - 1, nmax + 2)}
        self.C, self.I, self.Hb = {}, {}, {}
        for n in range(nmin - 1, nmax + 1):
            cols = [dH(X, Y, n, {b: Fraction(1)}) for b in self.B[n]]
            ker = kernel(cols, self.B[n])
            span = [dict(v) for v in ker]
            comp, imgs = [], []
            for b, col in zip(self.B[n], cols):
                e = {b: Fraction(1)}
                if rref_solve(span, e) is None:
                    span.append(e)
                    comp.append(e)
                    imgs.append(col)
            self.C[n] = comp
            self.I[n + 1] = imgs
            self.K = getattr(self, "K", {})
            self.K[n] = ker
        for n in range(nmin, nmax + 1):
            chosen, span = [], [dict(v) for v in self.I[n]]
            for kv in self.K[n]:
                if rref_solve(span, kv) is None:
                    chosen.append(kv)
                    span.append(kv)
            self.Hb[n] = chosen

    def dim(self, n):
        return len(self.Hb[n])

    def split(self, n, vec):
        H, I, C = self.Hb[n], self.I[n], self.C[n]
        sol = rref_solve(H + I + C, vec)
        assert sol is not None
        return sol[:len(H)], sol[len(H):len(H) + len(I)], sol[len(H) + len(I):]

    def iota(self, n, cls):
        vec = {}
        for cf, kv in zip(cls, self.Hb[n]):
            for k, v in kv.items():
                vec[k] = vec.get(k, 0) + cf * v
        return iota1(self.X, self.Y, n, {k: v for k, v in vec.items() if v != 0})

    def proj(self, f):
        vec = p1(f)
        if not vec:
            return [Fraction(0)] * self.dim(f.n)
        return self.split(f.n, vec)[0]

    def h(self, f):
        """h = h1 + iota1 h2 p1."""
        out = h1(f)
        vec = p1(f)
        if vec:
            _, beta, _ = self.split(f.n, vec)
            pre = {}
            for cf, cv in zip(beta, self.C[f.n - 1]):
                if cf != 0:
                    for k, v in cv.items():
                        pre[k] = pre.get(k, 0) + cf * v
            pre = {k: v for k, v in pre.items() if v != 0}
            if pre:
                out = out + iota1(self.X, self.Y, f.n - 1, pre)
        return out


def kernel(cols, basis):
    """Kernel of the map basis -> dicts given by cols, as dicts over basis."""
    keys = sorted({k for c in cols for k in c}, key=str)
    n = len(cols)
    m = [[Fraction(c.get(k, 0)) for c in cols] for k in keys]
    piv = []
    r = 0
    for cidx in range(n):
        pr = next((i for i in range(r, len(m)) if m[i][cidx] != 0), None)
        if pr is None:
            continue
        m[r], m[pr] = m[pr], m[r]
        inv = Fraction(1) / Fraction(m[r][cidx])
        m[r] = [v * inv for v in m[r]]
        for i in range(len(m)):
            if i != r and m[i][cidx] != 0:
                fac = m[i][cidx]
                m[i] = [a - fac * b for a, b in zip(m[i], m[r])]
        piv.append(cidx)
        r += 1
    free = [c for c in range(n) if c not in piv]
    out = []
    for fcol in free:
        v = {basis[fcol]: Fraction(1)}
        for i, pc in enumerate(piv):
            if m[i][fcol] != 0:
                v[basis[pc]] = -m[i][fcol]
        out.append(v)
    return out


_RC = {}


def retract(X, Y):
    k = (id(X), id(Y))
    if k not in _RC:
        _RC[k] = Retract(X, Y)
    return _RC[k]


def b2(x, y):
    r = mu(x, y)
    return r.scale(-1) if x.n % 2 else r


def phi(xs):
    if len(xs) == 1:
        return xs[0]
    tot = None
    for k in range(1, len(xs)):
        t = b2(phi(xs[:k]), phi(xs[k:]))
        tot = t if tot is None else tot + t
    return retract(tot.X, tot.Y).h(tot)


def bn(xs):
    """Transferred b_n (shifted conventions) on inputs iota(class); returns the class coordinates."""
    tot = None
    for k in range(1, len(xs)):
        t = b2(phi(xs[:k]), phi(xs[k:]))
        tot = t if tot is None else tot + t
    return retract(tot.X, tot.Y).proj(tot), (tot.X, tot.Y, tot.n)


_LINES = {}


def L(a):
    if a not in _LINES:
        _LINES[a] = line(a)
    return _LINES[a]


def section(a, b, nb, coeff=Fraction(1)):
    return Mor(L(a), L(b), 0, {(0, 0): E.incl(a, b, 0, {nb: coeff})})


def relation(xs):
    """Shifted A-infinity relation on the classes xs (all inputs iota of classes); returns the defect."""
    n = len(xs)
    total = None
    for j in range(2, n):
        for i in range(0, n - j + 1):
            cls, (X, Y, deg) = bn(xs[i:i + j])
            if not any(cls):
                continue
            inner = retract(X, Y).iota(deg, cls)
            out, _ = bn(xs[:i] + [inner] + xs[i + j:])
            sgn = (-1) ** sum(x.n - 1 for x in xs[:i])
            out = [sgn * v for v in out]
            total = out if total is None else [u + v for u, v in zip(total, out)]
    return total or [0]


if __name__ == "__main__":
    Q = skyscraper_oo()
    for b in (0, 2, 4):
        print("Ext(O_oo, O(%d oo)):" % b, [retract(Q, L(b)).dim(n) for n in range(-1, 3)],
              " Ext(O(%d oo), O_oo):" % b, [retract(L(b), Q).dim(n) for n in range(-1, 3)])
    print("Ext(O_oo, O_oo):", [retract(Q, Q).dim(n) for n in range(-1, 3)])
    # Lemma 21 (1): m_3(X_a, s, ev_b) for the monomial sections s of O((b - a) oo); the pole order of b_n at oo
    # is n + 2[n odd], so s vanishes at oo iff its pole order is below c = b - a, simply iff it is c - 1.
    bad = 0
    for a, b in [(0, 2), (0, 4), (2, 6), (0, 6), (-2, 4)]:
        c = b - a
        X = retract(Q, L(a)).iota(1, [Fraction(1)])
        ev = retract(L(b), Q).iota(0, [Fraction(1)])
        for nb in E.cohom_basis(c, 0):
            pole = nb + 2 * (nb % 2)
            m3, _ = bn([X, section(a, b, nb), ev])
            if pole < c and (m3[0] != 0) != (pole == c - 1):
                bad += 1
    print("Lemma 21 (1), derivative at oo:", "holds" if bad == 0 else f"{bad} failures")
    # A-infinity relations through the skyscraper, n = 4 and 5
    rng = random.Random(3)
    bad = 0
    for _ in range(40):
        a = rng.choice([-2, 0, 2])
        ups = sorted(rng.sample([2, 4, 6], rng.choice([2, 3])))
        objs = [a] + [a + u for u in ups]
        X = retract(Q, L(objs[0])).iota(1, [Fraction(rng.randint(1, 3))])
        ev = retract(L(objs[-1]), Q).iota(0, [Fraction(rng.randint(1, 3))])
        secs = []
        for u, v in zip(objs, objs[1:]):
            basis = E.cohom_basis(v - u, 0)
            secs.append(Mor(L(u), L(v), 0, {(0, 0): E.incl(u, v, 0, {nb: Fraction(rng.randint(-2, 2)) or Fraction(1)
                                                                       for nb in basis})}))
        if any(relation([X] + secs + [ev])):
            bad += 1
    print("A-infinity relations with O_oo, n = 4 and 5:", "hold" if bad == 0 else f"{bad} failures")
