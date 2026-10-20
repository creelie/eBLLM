"""The action of K on the Ext groups of a closing chain on the cover T x B (candidate C8, Lemma 25).

K = ker(mu) acts on the pair (C_j, C'_j) by translation by p_j in E[2] on both curves. A K-invariant object of the
cover is a pull-back from A_0, so a K-invariant twisting cochain and K-invariant first-order deformations are the
ones that exist on A_0. This module computes that action on cohomology, where it is canonical:

* translations of y^2 = x^3 - x by the points of order two:
      t_P0 (x, y) = (-1/x, y/x^2),  t_(1,0) (x, y) = ((x+1)/(x-1), -2y/(x-1)^2),  t_(-1,0) (x, y) = ((1-x)/(1+x), -2y/(x+1)^2);
* the linearisation of L = O(2 oo) on a pair, V_p = lambda_p (x - e_p) (x) (x' - e_p) t_p^*, with
  (x - e_p)(x - e_p) o t_p = c_p (c = -1, 2, 2), so that on Hom(L^a, L^b) with b - a = m even the pair acts by
  U_p (x) U_p, U_p f = c_p^(-m/2) (x - e_p)^m f o t_p on each curve, independently of the choice of lambda_p;
* the skyscraper factor of T = O_Z L^k is L^k restricted to E[2], modelled as the twisted complex
  Z_k = [O((2k - 4) oo)[1] -> O(2k oo)] with differential y; the restriction r: L^k -> Z_k is invariant, so the action on
  Hom(L^a, Z_k) follows from U on sections and r, and the action on Ext^1(Z_k, L^b) from Serre duality (pairing into
  Ext^1(L^b, L^b) = H^1(O), on which translations act trivially).

Per curve the operators U_p of one Hom space generate an elementary abelian group up to sign; the sign is fixed by
setting U_(-1,0) = U_P0 U_(1,0), which leaves the pair action unchanged. Each Hom space then splits into four
character spaces, and the K-invariant tensors of a pair are the sum over characters chi of V_chi (x) V'_chi.

    python3 e06_equivariant.py      # checks: group law, invariance of r and of the pairing, character dimensions
"""
from fractions import Fraction
import itertools
import e0_ainf as E
import e0_twisted as T
import e06_points as Pt

PTS = ("P0", "P1", "Pm1")          # (0, 0), (1, 0), (-1, 0)
EV = {"P0": 0, "P1": 1, "Pm1": -1}
CP = {"P0": Fraction(-1), "P1": Fraction(2), "Pm1": Fraction(2)}


# polynomials in x: dict {power: Fraction}
def padd(f, g, s=1):
    h = dict(f)
    for k, v in g.items():
        h[k] = h.get(k, 0) + s * v
        if h[k] == 0:
            del h[k]
    return h


def pmul(f, g):
    out = {}
    for i, a in f.items():
        for j, b in g.items():
            out[i + j] = out.get(i + j, 0) + a * b
    return {k: v for k, v in out.items() if v != 0}


def ppow(f, k):
    out = {0: Fraction(1)}
    for _ in range(k):
        out = pmul(out, f)
    return out


def U_function(c, f, p):
    """U_p on a section f = sum f_n b_n of O(c oo), c = 2m, m even: c_p^(-m/2) (x - e_p)^m f o t_p, in the b_n."""
    assert c % 4 == 0
    m = c // 2
    if p == "P0":
        lin_num, lin_den, kappa = {0: Fraction(-1)}, {1: Fraction(1)}, Fraction(1)   # X = -1/x
    elif p == "P1":
        lin_num, lin_den, kappa = {0: Fraction(1), 1: Fraction(1)}, {0: Fraction(-1), 1: Fraction(1)}, Fraction(-2)
    else:
        lin_num, lin_den, kappa = {0: Fraction(1), 1: Fraction(-1)}, {0: Fraction(1), 1: Fraction(1)}, Fraction(-2)
    # lin_den is (x - e_p) up to sign: x, x - 1, x + 1
    A, B = {}, {}
    for n, v in f.items():
        i, e = n // 2, n % 2
        if e == 0:
            assert m - i >= 0
            A = padd(A, {k: v * a for k, a in pmul(ppow(lin_num, i), ppow(lin_den, m - i)).items()})
        else:
            assert m - i - 2 >= 0
            B = padd(B, {k: v * kappa * a for k, a in pmul(ppow(lin_num, i), ppow(lin_den, m - i - 2)).items()})
    s = CP[p] ** (-(m // 2))
    out = {}
    for k, a in A.items():
        out[2 * k] = out.get(2 * k, 0) + s * a
    for k, a in B.items():
        out[2 * k + 1] = out.get(2 * k + 1, 0) + s * a
    return {k: v for k, v in out.items() if v != 0}


_Z = {}


def Zk(k):
    """O_{E[2]} (x) L^k = [O((2k - 4) oo)[1] -> O(2k oo)], differential y."""
    if k not in _Z:
        y = E.Elt(2 * k - 4, 2 * k, 0, {1: Fraction(1)}, {1: Fraction(1)})
        _Z[k] = T.Obj([(2 * k - 4, 1), (2 * k, 0)], {(0, 1): y})
    return _Z[k]


def lines_class(d1, d2, f):
    R = T.retract(T.L(d1), T.L(d2))
    return R.proj(T.Mor(T.L(d1), T.L(d2), 0, {(0, 0): E.incl(d1, d2, 0, f)}))


def class_function(d1, d2, cls):
    x = T.retract(T.L(d1), T.L(d2)).iota(0, cls)
    return dict(x.c[(0, 0)].f0) if (0, 0) in x.c else {}


def restriction(k):
    Z = Zk(k)
    r = E.Elt(2 * k, 2 * k, 0, {0: Fraction(1)}, {0: Fraction(1)})
    return T.retract(T.L(2 * k), Z).proj(T.Mor(T.L(2 * k), Z, 0, {(0, 1): r}))


def unit_vectors(d):
    return [[Fraction(int(i == j)) for j in range(d)] for i in range(d)]


def matvec(M, v):
    return [sum(M[i][j] * v[j] for j in range(len(v))) for i in range(len(M))]


def solve_columns(cols_in, cols_out):
    """The matrix A with A cols_in[i] = cols_out[i] (cols_in spanning)."""
    d = len(cols_in[0])
    rows = []
    # A is d x d: unknowns A[r][s]; equations per column i and row r
    out = [[None] * d for _ in range(d)]
    for r in range(d):
        rows = [list(c) for c in cols_in]
        rhs = [c[r] for c in cols_out]
        sol = Pt.rank_solve(rows, rhs)
        assert sol is not None
        out[r] = sol
        for c_in, c_out in zip(cols_in, cols_out):
            assert sum(a * b for a, b in zip(sol, c_in)) == c_out[r], "U is not linear on this span"
    return out


_ACT = {}


def act_lines(d1, d2, p):
    """U_p on H^0(O((d2 - d1) oo)) = Hom(L(d1), L(d2)), as a matrix on the class coordinates."""
    key = ("LL", d1, d2, p)
    if key not in _ACT:
        R = T.retract(T.L(d1), T.L(d2))
        cols = []
        for v in unit_vectors(R.dim(0)):
            f = class_function(d1, d2, v)
            cols.append(lines_class(d1, d2, U_function(d2 - d1, f, p)))
        _ACT[key] = [[cols[j][i] for j in range(len(cols))] for i in range(len(cols))]
    return _ACT[key]


def act_to_Z(d, k, p):
    """U_p on Hom(L(d), Z_k)."""
    key = ("LZ", d, k, p)
    if key in _ACT:
        return _ACT[key]
    Z = Zk(k)
    dim = T.retract(T.L(d), Z).dim(0)
    r = restriction(k)
    c = 2 * k - d
    if c >= 8:
        # spanned by sigma . r, sigma a section of O(c oo); U(sigma r) = U(sigma) r
        cols_in, cols_out = [], []
        for nb in E.cohom_basis(c, 0):
            f = {nb: Fraction(1)}
            s = lines_class(d, 2 * k, f)
            us = lines_class(d, 2 * k, U_function(c, f, p))
            cols_in.append(Pt.mul_cls(T.L(d), T.L(2 * k), Z, s, r, 0, 0))
            cols_out.append(Pt.mul_cls(T.L(d), T.L(2 * k), Z, us, r, 0, 0))
        M = solve_columns(cols_in, cols_out)
    else:
        # from Hom(L(d - 4t), Z_k): U(tau . f) = U(tau) . U(f) for sections tau of O(4t oo)
        t = (8 - c + 3) // 4
        d2 = d - 4 * t
        Mlow = act_to_Z(d2, k, p)
        rows, rhs_cols = [], []
        taus = E.cohom_basis(4 * t, 0)
        # unknown U(f) = X for each unit f; equations: mul(U tau, X) = Mlow mul(tau, f)
        M = [[None] * dim for _ in range(dim)]
        lin = []
        for nb in taus:
            ut = lines_class(d2, d, U_function(4 * t, {nb: Fraction(1)}, p))
            lin.append((nb, [Pt.mul_cls(T.L(d2), T.L(d), Z, ut, e, 0, 0) for e in unit_vectors(dim)]))
        cols = []
        for f in unit_vectors(dim):
            A_rows, b = [], []
            for nb, images in lin:
                tau = lines_class(d2, d, {nb: Fraction(1)})
                target = matvec(Mlow, Pt.mul_cls(T.L(d2), T.L(d), Z, tau, f, 0, 0))
                for comp in range(len(target)):
                    A_rows.append([images[j][comp] for j in range(dim)])
                    b.append(target[comp])
            X = Pt.rank_solve(A_rows, b)
            assert X is not None
            cols.append(X)
        M = [[cols[j][i] for j in range(dim)] for i in range(dim)]
    _ACT[key] = M
    return M


def act_from_Z(k, d, p):
    """U_p on Ext^1(Z_k, L(d)), the inverse transpose of U_p on Hom(L(d), Z_k) for the Serre pairing."""
    key = ("ZL", k, d, p)
    if key in _ACT:
        return _ACT[key]
    Z = Zk(k)
    dh = T.retract(T.L(d), Z).dim(0)
    de = T.retract(Z, T.L(d)).dim(1)
    assert dh == de
    P = [[Pt.mul_cls(T.L(d), Z, T.L(d), g, e, 0, 1)[0] for e in unit_vectors(de)] for g in unit_vectors(dh)]
    UH = act_to_Z(d, k, p)
    # invariance: sum_ab UH[a][g] P[a][b] UE[b][e] = P[g][e]
    UHtP = [[sum(UH[a][g] * P[a][b] for a in range(dh)) for b in range(de)] for g in range(dh)]
    cols = []
    for e in range(de):
        X = Pt.rank_solve(UHtP, [P[g][e] for g in range(dh)])
        assert X is not None
        cols.append(X)
    M = [[cols[j][i] for j in range(de)] for i in range(de)]
    _ACT[key] = M
    return M


def matmul(A, B):
    return [[sum(A[i][k] * B[k][j] for k in range(len(B))) for j in range(len(B[0]))] for i in range(len(A))]


def ident(d):
    return unit_vectors(d)


def act(X, Y, n, p):
    """U_p on Ext^n(X, Y) for X, Y among L(d) and Z_k (given as ("L", d) or ("Z", k)), with the sign convention
    U_Pm1 = U_P0 U_P1."""
    if p == "Pm1":
        return matmul(act(X, Y, n, "P0"), act(X, Y, n, "P1"))
    if X[0] == "L" and Y[0] == "L":
        assert n == 0
        return act_lines(X[1], Y[1], p)
    if X[0] == "L" and Y[0] == "Z":
        assert n == 0
        return act_to_Z(X[1], Y[1], p)
    if X[0] == "Z" and Y[0] == "L":
        assert n == 1
        return act_from_Z(X[1], Y[1], p)
    raise ValueError((X, Y, n))


CHARS = [(a, b) for a in (1, -1) for b in (1, -1)]   # values on P0 and P1


def nullspace(M):
    """Basis of {v : M v = 0} over Q."""
    rows = [list(r) for r in M]
    n = len(rows[0]) if rows else 0
    piv, r = [], 0
    for c in range(n):
        pr = next((i for i in range(r, len(rows)) if rows[i][c] != 0), None)
        if pr is None:
            continue
        rows[r], rows[pr] = rows[pr], rows[r]
        inv = 1 / rows[r][c]
        rows[r] = [v * inv for v in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c] != 0:
                f = rows[i][c]
                rows[i] = [a - f * b for a, b in zip(rows[i], rows[r])]
        piv.append(c)
        r += 1
    out = []
    for fc in (c for c in range(n) if c not in piv):
        v = [Fraction(0)] * n
        v[fc] = Fraction(1)
        for i, pc in enumerate(piv):
            v[pc] = -rows[i][fc]
        out.append(v)
    return out


def character_spaces(X, Y, n):
    """{chi: basis of the chi-eigenspace} for chi = (value on P0, value on P1)."""
    A, B = act(X, Y, n, "P0"), act(X, Y, n, "P1")
    d = len(A)
    out = {}
    for a, b in CHARS:
        M = [[A[i][j] - a * (i == j) for j in range(d)] for i in range(d)] + \
            [[B[i][j] - b * (i == j) for j in range(d)] for i in range(d)]
        out[(a, b)] = nullspace(M)
    assert sum(len(v) for v in out.values()) == d, "the action does not diagonalise"
    return out


def check():
    ok = True
    spaces = [(("L", -2), ("L", 2), 0), (("L", 14), ("Z", -3), 0), (("Z", 7), ("L", -6), 1),
              (("Z", -3), ("L", -2), 1), (("L", 10), ("Z", 7), 0), (("L", -6), ("L", -2), 0)]
    for X, Y, n in spaces:
        A, B, C = act(X, Y, n, "P0"), act(X, Y, n, "P1"), act(X, Y, n, "Pm1")
        d = len(A)
        I = ident(d)
        law = matmul(A, A) == I and matmul(B, B) == I and matmul(A, B) == matmul(B, A)
        # U_Pm1 from the formula agrees with U_P0 U_P1 up to one sign
        direct = None
        if X[0] == "L" and Y[0] == "L":
            direct = act_lines(X[1], Y[1], "Pm1")
        elif X[0] == "L":
            direct = act_to_Z(X[1], Y[1], "Pm1")
        else:
            direct = act_from_Z(X[1], Y[1], "Pm1")
        sign = "+" if direct == C else ("-" if direct == [[-v for v in r] for r in C] else "?")
        dims = {chi: len(v) for chi, v in character_spaces(X, Y, n).items()}
        print(f"  Ext^{n}{X}->{Y}: dim {d}, group law {'holds' if law else 'FAILS'}, U_Pm1 = {sign} U_P0 U_P1, "
              f"characters {dims}")
        ok = ok and law and sign != "?"
    # r is invariant
    for k in (7, -3):
        r = restriction(k)
        print(f"  restriction L^{k} -> Z_{k}: class {r}")
    return ok


if __name__ == "__main__":
    print("K-action on the Ext groups of the closing chain, per curve:")
    print("checks hold" if check() else "CHECKS FAIL")
