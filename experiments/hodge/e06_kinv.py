"""K-invariant sections on one pair of curves C x C' of the model of Lemma 19 (candidate C8).

On the j-th pair, mu_j: C x C' -> E_0^2, (t, t') -> (-zeta t + zeta t', t + t'), has kernel K_j = {(p, p) : p in
E_0[2]}, and mu_j^* O(oo x E + E x oo) = O(Delta + Delta^-) (diagonal and antidiagonal). The function
x(t) - x(t') has divisor Delta + Delta^- - 2(oo x E) - 2(E x oo), so

    G = F (x(t) - x(t'))^l

identifies sections F of O(l (Delta + Delta^-)) with sections G of O(2l oo) x O(2l oo), the external products of
the line bundles O(2l oo) of e0_ainf. The sections of L^l on E_0^2 are the F invariant under K_j, i.e. the G with

    G(t + p, t' + p) (x(t) - x(t'))^l = G(t, t') (x(t + p) - x(t' + p))^l,      p in E_0[2].

Translations by the points of order two of y^2 = x^3 - x:
    p = (0, 0):  (x, y) -> (-1/x, y/x^2);   p = (1, 0): ((x+1)/(x-1), -2y/(x-1)^2);
    p = (-1, 0): ((1-x)/(1+x), -2y/(x+1)^2).
G is written in the basis b_a(t) b_b(t') (b_n = x^i y^e, n = 2i + e). The identity splits by the parities
(e_a, e_b) and is a rational identity in x(t), x(t'), so it is imposed at random rational values.

    python3 e06_kinv.py
"""
from fractions import Fraction
import random, sys
import e0_ainf as E0
from e0_twisted import kernel

TRANS = {
    "P0": (lambda x: -1 / x, lambda x: 1 / x ** 2),
    "P1": (lambda x: (x + 1) / (x - 1), lambda x: -2 / (x - 1) ** 2),
    "P-1": (lambda x: (1 - x) / (1 + x), lambda x: -2 / (x + 1) ** 2),
}


def on_curve(x, y):
    return y * y == x ** 3 - x


def sections(c):
    """Basis indices n of H^0(O(c oo)) (pole order n + 2[n odd] <= c)."""
    return E0.cohom_basis(c, 0)


def invariant_sections(l, gens=("P0", "P1"), samples=None, seed=0):
    """Basis of the K-invariant G in H^0(O(2l oo)) x H^0(O(2l oo)), as dicts {(a, b): coefficient}."""
    rng = random.Random(seed)
    V = sections(2 * l)
    basis = [(a, b) for a in V for b in V]
    rows = []
    samples = samples or 4 * len(basis)
    for p in gens:
        r, s = TRANS[p]
        for _ in range(samples):
            x1 = Fraction(rng.randint(2, 60), rng.randint(1, 13))
            x2 = Fraction(rng.randint(-60, -2), rng.randint(1, 13))
            if x2 == -1 or x1 == 1:
                continue
            rx1, rx2 = r(x1), r(x2)
            for ea in (0, 1):
                for eb in (0, 1):
                    row = {}
                    for (a, b) in basis:
                        if a % 2 != ea or b % 2 != eb:
                            continue
                        ia, ib = a // 2, b // 2
                        lhs = rx1 ** ia * s(x1) ** ea * rx2 ** ib * s(x2) ** eb * (x1 - x2) ** l
                        rhs = x1 ** ia * x2 ** ib * (rx1 - rx2) ** l
                        v = lhs - rhs
                        if v:
                            row[(a, b)] = v
                    if row:
                        rows.append(row)
    # kernel of the map g -> (row . g)
    cols = []
    for bidx in basis:
        cols.append({ri: row[bidx] for ri, row in enumerate(rows) if bidx in row})
    return kernel(cols, basis)


def check_translations():
    """The translation formulas on a few points of y^2 = x^3 - x over Q(i)-free test: compare x-coordinates
    of p + q and q + p on the curve over F_101."""
    P = 101
    pts = [(x, y) for x in range(P) for y in range(P) if (y * y - x ** 3 + x) % P == 0]

    def add(A, B):
        if A is None:
            return B
        if B is None:
            return A
        (x1, y1), (x2, y2) = A, B
        if x1 == x2 and (y1 + y2) % P == 0:
            return None
        lam = ((y2 - y1) * pow(x2 - x1, -1, P)) % P if x1 != x2 else ((3 * x1 * x1 - 1) * pow(2 * y1, -1, P)) % P
        x3 = (lam * lam - x1 - x2) % P
        return (x3, (lam * (x1 - x3) - y1) % P)

    ok = True
    for name, e in (("P0", 0), ("P1", 1), ("P-1", P - 1)):
        r, s = TRANS[name]
        for (x, y) in pts:
            if x in (0, 1, P - 1):
                continue
            Q = add((x, y), (e, 0))
            X = Fraction(x)
            rx, sx = r(X), s(X)
            want = (rx.numerator * pow(rx.denominator, -1, P) % P, y * sx.numerator * pow(sx.denominator, -1, P) % P)
            ok &= Q == want
    return ok


if __name__ == "__main__":
    ok = check_translations()
    print("translation formulas on y^2 = x^3 - x over F_101:", "agree" if ok else "DISAGREE")
    for l in (1, 2, 3):
        inv = invariant_sections(l)
        inv3 = invariant_sections(l, gens=("P0", "P1", "P-1"), seed=1)
        print(f"l = {l}: K-invariant sections of O(2l oo) x O(2l oo): {len(inv)} (expected l^2 = {l * l});"
              f" with all three translations: {len(inv3)}")
        ok &= len(inv) == l * l == len(inv3)
    sys.exit(0 if ok else 1)
