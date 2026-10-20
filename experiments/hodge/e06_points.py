"""The skyscraper of the four points of order two of E_0, and its splitting into the four points (candidate C8).

O_{E[2]} = [O(-4 oo)[1] -> O] with delta = y, a section of O(4 oo) with divisor E[2] - 4 oo. Hom(O_{E[2]}, O_{E[2]})
is the algebra of functions on E[2]; its four primitive idempotents e_q (rational, since E[2] is rational) cut a
morphism into its components at the four points: f e_q for f into O_{E[2]}, e_q g for g out of it.

    python3 e06_points.py      # the algebra, its unit and its four idempotents
"""
from fractions import Fraction
import itertools
import e0_twisted as T
import e0_ainf as E


def skyscraper_E2():
    y = E.Elt(-4, 0, 0, {1: Fraction(1)}, {1: Fraction(1)})
    return T.Obj([(-4, 1), (0, 0)], {(0, 1): y})


Z = skyscraper_E2()


def mul_cls(X, Y, W, a, b, na, nb):
    """Class of the product of the classes a in Ext^na(X, Y) and b in Ext^nb(Y, W)."""
    A = T.retract(X, Y).iota(na, a)
    B = T.retract(Y, W).iota(nb, b)
    return T.retract(X, W).proj(T.mu(A, B))


def rank_solve(rows, rhs):
    """A solution of the consistent rational system rows x = rhs (Gaussian elimination), or None."""
    m, n = len(rows), len(rows[0])
    A = [list(r) + [b] for r, b in zip(rows, rhs)]
    piv = []
    r = 0
    for c in range(n):
        p = next((i for i in range(r, m) if A[i][c] != 0), None)
        if p is None:
            continue
        A[r], A[p] = A[p], A[r]
        inv = 1 / A[r][c]
        A[r] = [v * inv for v in A[r]]
        for i in range(m):
            if i != r and A[i][c] != 0:
                f = A[i][c]
                A[i] = [u - f * v for u, v in zip(A[i], A[r])]
        piv.append(c)
        r += 1
    if any(all(v == 0 for v in A[i][:n]) and A[i][n] != 0 for i in range(m)):
        return None
    x = [Fraction(0)] * n
    for i, c in enumerate(piv):
        x[c] = A[i][n]
    return x


class FunctionsOnE2:
    def __init__(self):
        self.d = T.retract(Z, Z).dim(0)
        d = self.d
        self.basis = [[Fraction(int(i == j)) for j in range(d)] for i in range(d)]
        self.table = [[mul_cls(Z, Z, Z, self.basis[a], self.basis[b], 0, 0) for b in range(d)] for a in range(d)]
        rows, rhs = [], []
        for b in range(d):
            for c in range(d):
                rows.append([self.table[a][b][c] for a in range(d)])
                rhs.append(self.basis[b][c])
        self.unit = rank_solve(rows, rhs)
        assert self.unit is not None
        self.idem = self._idempotents()

    def mult(self, u, v):
        out = [Fraction(0)] * self.d
        for a in range(self.d):
            for b in range(self.d):
                if u[a] and v[b]:
                    out = [o + u[a] * v[b] * t for o, t in zip(out, self.table[a][b])]
        return out

    def _idempotents(self):
        d = self.d
        for g in itertools.product(range(-2, 3), repeat=d):
            g = [Fraction(v) for v in g]
            # the eigenvalues of multiplication by g are its values on the four points: find lambda with
            # g - lambda not invertible, among the rational roots of the minimal polynomial
            pw = [self.unit]
            for _ in range(d):
                pw.append(self.mult(pw[-1], g))
            c = rank_solve([[pw[i][k] for i in range(d)] for k in range(d)], pw[d])
            if c is None:
                continue
            # x^d = sum c_i x^i; rational roots: search numerators and denominators of small height
            poly = [-ci for ci in c] + [Fraction(1)]
            roots = set()
            for num in range(-60, 61):
                for den in range(1, 9):
                    lam = Fraction(num, den)
                    if sum(a * lam ** i for i, a in enumerate(poly)) == 0:
                        roots.add(lam)
            if len(roots) != d:
                continue
            idem = []
            for lam in sorted(roots):
                e = self.unit
                for mu in roots:
                    if mu != lam:
                        gm = [gi - mu * ui for gi, ui in zip(g, self.unit)]
                        e = [v / (lam - mu) for v in self.mult(e, gm)]
                idem.append(e)
            if any(all(v == 0 for v in e) for e in idem):
                continue                    # g took a value twice: its powers were dependent
            return idem
        raise RuntimeError("no generic element found")


if __name__ == "__main__":
    A = FunctionsOnE2()
    print("dim Hom(O_E2, O_E2) =", A.d, " unit:", A.unit)
    for e in A.idem:
        assert A.mult(e, e) == e
    for e, f in itertools.combinations(A.idem, 2):
        assert all(v == 0 for v in A.mult(e, f))
    assert [sum(v) for v in zip(*A.idem)] == A.unit
    print("four orthogonal idempotents adding up to the unit:", A.idem)
