"""Certificate first: replace a statement by one explicit object whose finitely checkable properties
imply it, search for the object in a structured space, and check the properties exactly.

This is the strategy of Cohn and Elkies (Ann. of Math. 157, 2003), who reduced the optimality of a
sphere packing to one auxiliary function with sign conditions on it and its Fourier transform, and
of Viazovska (Ann. of Math. 185, 2017), who built that function in dimension 8 from modular forms.
Its oldest exact instance is the linear programming bound of Delsarte, Goethals and Seidel for
spherical codes, with the certificates of Levenshtein and of Odlyzko and Sloane (J. Combin. Theory
Ser. A 26, 1979) that prove the kissing numbers 240 in dimension 8 and 196560 in dimension 24:

    a polynomial f with f(t) <= 0 on [-1, s] and nonnegative Gegenbauer coefficients f_k, f_0 > 0,
    bounds the size of every code with inner products in [-1, s] by f(1) / f_0.

`gegenbauer_coefficients` expands f exactly over the rationals, `check_kissing_certificate` checks
the three conditions exactly (the sign condition by Sturm sequences), and `search_kissing` searches
the structured family (t + 1) (t - s) prod (t - a_i)^2 with roots on a rational grid, which is
where the optimal certificates live.  Everything is exact rational arithmetic.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass
from fractions import Fraction
from typing import List, Optional, Sequence, Tuple

Poly = List[Fraction]          # coefficients, lowest degree first


def pmul(a: Poly, b: Poly) -> Poly:
    out = [Fraction(0)] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            out[i + j] += x * y
    return out


def padd(a: Poly, b: Poly) -> Poly:
    n = max(len(a), len(b))
    return [(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0) for i in range(n)]


def pscale(a: Poly, c) -> Poly:
    return [c * x for x in a]


def peval(a: Poly, t) -> Fraction:
    acc = Fraction(0)
    for x in reversed(a):
        acc = acc * t + x
    return acc


def ptrim(a: Poly) -> Poly:
    a = list(a)
    while len(a) > 1 and a[-1] == 0:
        a.pop()
    return a


def from_roots(roots: Sequence[Fraction], lead=Fraction(1)) -> Poly:
    p: Poly = [Fraction(lead)]
    for r in roots:
        p = pmul(p, [-Fraction(r), Fraction(1)])
    return p


def gegenbauer(n: int, kmax: int) -> List[Poly]:
    """Gegenbauer polynomials for the sphere S^{n-1}, normalised by G_k(1) = 1:
    G_0 = 1, G_1 = t, (k + n - 2) G_{k+1} = (2k + n - 2) t G_k - k G_{k-1}."""
    G = [[Fraction(1)], [Fraction(0), Fraction(1)]]
    for k in range(1, kmax):
        nxt = padd(pscale(pmul([Fraction(0), Fraction(1)], G[k]), Fraction(2 * k + n - 2)),
                   pscale(G[k - 1], Fraction(-k)))
        G.append(pscale(nxt, Fraction(1, k + n - 2)))
    return G[:kmax + 1]


def gegenbauer_coefficients(f: Poly, n: int) -> List[Fraction]:
    f = ptrim([Fraction(x) for x in f])
    d = len(f) - 1
    G = gegenbauer(n, max(d, 1))
    rest, coeffs = list(f), [Fraction(0)] * (d + 1)
    for k in range(d, -1, -1):
        lead = G[k][k]
        c = rest[k] / lead if k < len(rest) else Fraction(0)
        coeffs[k] = c
        rest = padd(rest, pscale(G[k], -c))
    assert all(x == 0 for x in rest)
    return coeffs


def _pdiv(a: Poly, b: Poly) -> Tuple[Poly, Poly]:
    a, b = ptrim(a), ptrim(b)
    q = [Fraction(0)] * max(1, len(a) - len(b) + 1)
    r = list(a)
    while len(r) >= len(b) and any(r):
        c = r[-1] / b[-1]
        k = len(r) - len(b)
        q[k] = c
        r = ptrim(padd(r, pscale([Fraction(0)] * k + b, -c)))
        if len(r) < len(b) or (len(r) == 1 and r[0] == 0):
            break
    return q, r


def _deriv(a: Poly) -> Poly:
    return [i * a[i] for i in range(1, len(a))] or [Fraction(0)]


def sturm_roots(f: Poly, lo: Fraction, hi: Fraction) -> int:
    """Number of distinct real roots of f in (lo, hi], by Sturm's theorem."""
    f = ptrim(f)
    seq = [f, ptrim(_deriv(f))]
    while len(seq[-1]) > 1 or seq[-1][0] != 0:
        _, r = _pdiv(seq[-2], seq[-1])
        if len(r) == 1 and r[0] == 0:
            break
        seq.append(pscale(r, -1))

    def changes(t):
        s = [peval(p, t) for p in seq]
        s = [x for x in s if x != 0]
        return sum(1 for a, b in zip(s, s[1:]) if (a > 0) != (b > 0))
    return changes(lo) - changes(hi)


def _pgcd(a: Poly, b: Poly) -> Poly:
    a, b = ptrim(a), ptrim(b)
    while not (len(b) == 1 and b[0] == 0):
        _, r = _pdiv(a, b)
        a, b = b, ptrim(r)
    return pscale(a, 1 / a[-1])


def squarefree(f: Poly) -> Poly:
    """f / gcd(f, f'): the same real roots, each simple."""
    f = ptrim(f)
    if len(f) <= 2:
        return f
    g = _pgcd(f, _deriv(f))
    if len(g) == 1:
        return f
    q, r = _pdiv(f, g)
    assert all(x == 0 for x in r)
    return ptrim(q)


def nonpositive_on(f: Poly, lo: Fraction, hi: Fraction) -> bool:
    """Exact: f <= 0 on [lo, hi].  The distinct roots of f in [lo, hi] are isolated by bisection with
    Sturm sequences of the square-free part (so multiple roots are counted once and every Sturm count
    is valid, also at endpoints that are roots); f has constant sign between consecutive roots, so
    one rational test point in each gap, together with the endpoints, decides the sign."""
    f = ptrim(f)
    lo, hi = Fraction(lo), Fraction(hi)
    g = squarefree(f)
    if len(g) == 1:
        return g[0] <= 0 if f == g else all(peval(f, t) <= 0 for t in (lo, hi))
    roots: List[Tuple[Fraction, Fraction]] = []        # isolating intervals (a, b], one root each
    stack = [(lo, hi)]
    while stack:
        a, b = stack.pop()
        k = sturm_roots(g, a, b)
        if k == 0:
            continue
        if k == 1:
            roots.append((a, b))
            continue
        m = (a + b) / 2
        stack.extend([(a, m), (m, b)])
    tests = [lo, hi]
    for a, b in roots:                                  # shrink each interval until it is short
        while b - a > Fraction(1, 2 ** 20) and peval(g, b) != 0:
            m = (a + b) / 2
            a, b = (a, m) if sturm_roots(g, a, m) == 1 else (m, b)
        tests.extend([a, b])
    pts = sorted(set(tests))
    tests.extend((x + y) / 2 for x, y in zip(pts, pts[1:]))
    tests = [t for t in tests if lo <= t <= hi]
    return all(peval(f, t) <= 0 for t in tests)


@dataclass
class KissingCertificate:
    n: int
    s: Fraction
    f: Poly
    coefficients: List[Fraction]
    bound: Fraction
    valid: bool
    reasons: List[str]


def check_kissing_certificate(f: Poly, n: int, s=Fraction(1, 2)) -> KissingCertificate:
    """Delsarte's linear programming bound: f <= 0 on [-1, s], f_0 > 0, f_k >= 0  =>  N <= f(1)/f_0."""
    f = [Fraction(x) for x in f]
    c = gegenbauer_coefficients(f, n)
    reasons = []
    if c[0] <= 0:
        reasons.append("f_0 <= 0")
    if any(x < 0 for x in c[1:]):
        reasons.append("a Gegenbauer coefficient is negative")
    if not nonpositive_on(f, Fraction(-1), Fraction(s)):
        reasons.append(f"f is positive somewhere on [-1, {s}]")
    bound = peval(f, 1) / c[0] if c[0] > 0 else Fraction(10 ** 18)
    return KissingCertificate(n, Fraction(s), f, c, bound, not reasons, reasons)


def odlyzko_sloane(n: int) -> Poly:
    """The classical certificates: dimension 8 (240) and dimension 24 (196560)."""
    h, q = Fraction(1, 2), Fraction(1, 4)
    if n == 8:
        return from_roots([-1, -h, -h, 0, 0, h])
    if n == 24:
        return from_roots([-1, -h, -h, -q, -q, 0, 0, q, q, h])
    raise ValueError("certificates are given for n = 8 and n = 24")


def search_kissing(n: int, double_roots: int, s=Fraction(1, 2), grid: int = 4,
                   limit: Optional[int] = None) -> Optional[KissingCertificate]:
    """Search (t + 1)(t - s) prod_i (t - a_i)^2 with a_i in {j/grid : -grid < j < grid}, keeping the
    best valid certificate.  The structure builds the sign condition in: the double roots cannot
    make f positive, and (t + 1)(t - s) <= 0 on [-1, s]."""
    pts = [Fraction(j, grid) for j in range(-grid + 1, grid)]
    best = None
    for k, combo in enumerate(itertools.combinations_with_replacement(pts, double_roots)):
        if limit is not None and k >= limit:
            break
        roots = [Fraction(-1), Fraction(s)] + [a for a in combo for _ in (0, 1)]
        cert = check_kissing_certificate(from_roots(roots), n, s)
        if cert.valid and (best is None or cert.bound < best.bound):
            best = cert
    return best
