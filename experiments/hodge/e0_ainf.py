"""Exact A-infinity products of line bundles on E_0: y^2 = x^3 - x (candidate C8, Lemmas 20 and 21).

The curve has the points of order two oo, P0 = (0, 0), (1, 0), (-1, 0). Cover it by U0 = E - {oo} and
U1 = E - {P0}; then U01 = E - {oo, P0} has the basis b_n = x^i y^e (n = 2i + e, i in Z, e in {0, 1}) of its
functions, with

    ord_P0(b_n) = n,     ord_oo(b_n) = -n - 2[n odd].

Both orders are injective in n, so every space of sections below is spanned by basis elements:

    Gamma(U0, O(c oo)) = <b_n : n >= 0>,     Gamma(U1, O(c oo)) = <b_n : ord_oo(b_n) >= -c>.

Hom(O(a oo), O(b oo)) is the Cech complex of O(c oo), c = b - a: degree 0 pairs (f0, f1), degree 1 one
function g on U01, d(f0, f1) = f1 - f0, products by the ordered Cech cup product (strictly associative).
The homotopy h and the projection p are diagonal in the basis, so the transferred products are computed exactly.

Conventions: shifted degrees, b_1 = d, b_2(x, y) = (-1)^{|x|} x y, and the transferred b_n is p b_2(phi_k,
phi_{n-k}) summed over k with phi_1 = i, phi_m = h b_2(...) as in `phi`. The A-infinity relations are checked in
`check_relations`.

    python3 e0_ainf.py
"""
from fractions import Fraction
from functools import lru_cache
import itertools, random, sys


# functions on U01: dict {n: coeff}, b_n = x^i y^e
def bn_ie(n):
    return (n // 2, n % 2)


def ord_oo(n):
    return -n - 2 * (n % 2)


def fadd(f, g, s=1):
    h = dict(f)
    for k, v in g.items():
        h[k] = h.get(k, 0) + s * v
        if h[k] == 0:
            del h[k]
    return h


def fscale(f, s):
    return {k: s * v for k, v in f.items()} if s else {}


def fmul(f, g):
    out = {}
    for n, a in f.items():
        i, e = bn_ie(n)
        for m, b in g.items():
            j, f2 = bn_ie(m)
            if e + f2 < 2:
                terms = [(2 * (i + j) + e + f2, 1)]
            else:  # y^2 = x^3 - x
                terms = [(2 * (i + j + 3), 1), (2 * (i + j + 1), -1)]
            for k, s in terms:
                out[k] = out.get(k, 0) + a * b * s
    return {k: v for k, v in out.items() if v != 0}


class Elt:
    """A cochain of Hom(O(a oo), O(b oo)): deg 0 -> (f0, f1), deg 1 -> g."""
    __slots__ = ("a", "b", "deg", "f0", "f1", "g")

    def __init__(self, a, b, deg, f0=None, f1=None, g=None):
        self.a, self.b, self.deg = a, b, deg
        self.f0, self.f1, self.g = f0 or {}, f1 or {}, g or {}

    def iszero(self):
        return not (self.f0 or self.f1 or self.g)

    def __add__(self, o):
        assert (self.a, self.b, self.deg) == (o.a, o.b, o.deg)
        return Elt(self.a, self.b, self.deg, fadd(self.f0, o.f0), fadd(self.f1, o.f1), fadd(self.g, o.g))

    def scale(self, s):
        return Elt(self.a, self.b, self.deg, fscale(self.f0, s), fscale(self.f1, s), fscale(self.g, s))

    def check(self):
        c = self.b - self.a
        assert all(n >= 0 for n in self.f0), "f0 not regular on U0"
        assert all(ord_oo(n) >= -c for n in self.f1), "f1 not a section on U1"


def mu(x, y):
    """Cech cup product x then y (x: a -> b, y: b -> c)."""
    assert x.b == y.a
    a, c = x.a, y.b
    if x.iszero() or y.iszero() or x.deg not in (0, 1) or y.deg not in (0, 1):
        return Elt(a, c, x.deg + y.deg)
    if x.deg == 0 and y.deg == 0:
        return Elt(a, c, 0, fmul(x.f0, y.f0), fmul(x.f1, y.f1))
    if x.deg == 0 and y.deg == 1:
        return Elt(a, c, 1, g=fmul(x.f0, y.g))
    if x.deg == 1 and y.deg == 0:
        return Elt(a, c, 1, g=fmul(x.g, y.f1))
    return Elt(a, c, 2)


def b2(x, y):
    r = mu(x, y)
    return r.scale(-1) if x.deg % 2 else r


def dd(x):
    if x.deg == 0:
        return Elt(x.a, x.b, 1, g=fadd(x.f1, x.f0, -1))
    return Elt(x.a, x.b, x.deg + 1)


def h(x, sign=1):
    """Homotopy on degree 1: b_n -> (-b_n, 0) if only in V0, (0, b_n) if in V1."""
    c = x.b - x.a
    if x.deg != 1:
        return Elt(x.a, x.b, x.deg - 1)
    f0, f1 = {}, {}
    for n, v in x.g.items():
        in0, in1 = n >= 0, ord_oo(n) >= -c
        if in1:
            f1[n] = f1.get(n, 0) + sign * v
        elif in0:
            f0[n] = f0.get(n, 0) - sign * v
    return Elt(x.a, x.b, 0, f0, f1)


def proj(x):
    """p: cochains -> cohomology, returned as a dict {n: coeff} (basis of H^0 or H^1)."""
    c = x.b - x.a
    if x.deg == 0:
        return {n: v for n, v in x.f0.items() if ord_oo(n) >= -c}
    if x.deg == 1:
        return {n: v for n, v in x.g.items() if n < 0 and ord_oo(n) < -c}
    return {}


def incl(a, b, deg, cls):
    if deg == 0:
        return Elt(a, b, 0, dict(cls), dict(cls))
    return Elt(a, b, 1, g=dict(cls))


def cohom_basis(c, deg, span=40):
    if deg == 0:
        return [n for n in range(0, span) if ord_oo(n) >= -c]
    return [n for n in range(-span, 0) if ord_oo(n) < -c]


HSIGN = -1


def phi(xs):
    """phi_1 = incl, phi_m = h(sum_k b_2(phi_k, phi_{m-k}))."""
    if len(xs) == 1:
        return xs[0]
    tot = None
    for k in range(1, len(xs)):
        t = b2(phi(xs[:k]), phi(xs[k:]))
        tot = t if tot is None else tot + t
    return h(tot, HSIGN)


def bn(xs):
    """Transferred b_n on cochain representatives incl(cls)."""
    if len(xs) == 1:
        return Elt(xs[0].a, xs[0].b, xs[0].deg + 1)
    tot = None
    for k in range(1, len(xs)):
        t = b2(phi(xs[:k]), phi(xs[k:]))
        tot = t if tot is None else tot + t
    return tot


def random_class(a, b, deg, rng):
    basis = cohom_basis(b - a, deg)
    if not basis:
        return None
    return {n: Fraction(rng.randint(-3, 3)) for n in basis if rng.random() < 0.8} or {basis[0]: Fraction(1)}


def check_relations(trials=200, seed=1):
    """Shifted A-infinity relations on cohomology up to n = 5 for random chains of line bundles."""
    rng = random.Random(seed)
    worst = 0
    for _ in range(trials):
        n = rng.randint(3, 5)
        degs = [0, 1, 2, 3, 4, 5, 6]
        objs = [0]
        xs = []
        ok = True
        for _i in range(n):
            a = objs[-1]
            b = a + rng.randint(-3, 3)
            deg = 0 if b > a else (1 if b < a else rng.randint(0, 1))
            cls = random_class(a, b, deg, rng)
            if cls is None:
                ok = False
                break
            xs.append(incl(a, b, deg, cls))
            objs.append(b)
        if not ok:
            continue
        # sum over i, j: b_{n-j+1}(x_1..x_i, b_j(x_{i+1}..x_{i+j}), ..)
        total = {}
        for j in range(2, n):
            for i in range(0, n - j + 1):
                inner = bn(xs[i:i + j])
                cls = proj(inner)
                if not cls:
                    continue
                inner_c = incl(inner.a, inner.b, inner.deg, cls)
                outer = bn(xs[:i] + [inner_c] + xs[i + j:])
                s = 1 - 2 * (sum(x.deg - 1 for x in xs[:i]) % 2)
                for k, v in proj(outer).items():
                    total[k] = total.get(k, 0) + s * v
        total = {k: v for k, v in total.items() if v != 0}
        if total:
            return False, (objs, [x.deg for x in xs], total)
    return True, None


if __name__ == "__main__":
    for hs in (-1, 1):
        HSIGN = hs
        ok, info = check_relations()
        print("HSIGN", hs, "A-infinity relations up to n = 5:", "hold" if ok else f"fail {info}")
