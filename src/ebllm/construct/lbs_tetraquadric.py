"""SU(5) line-bundle vacua on the tetraquadric X = P1^4[2,2,2,2] (h11 = 4, chi = -128): the strings attack
off the standard embedding past (C3).

Exact checks, in this order (Anderson, Gray, Lukas, Palti 1106.4804, 1202.1757):
  (C1) c1(V) = 0; anomaly c2(TX).J_i - c2(V).J_i = 24 + 2 sum_a e2(k_a without i) >= 0; polystability:
       one Kahler point t > 0 where every slope mu(L_a) = 4 sum_i k_ai e2(t without i) vanishes;
  (C2) ind(V) = sum_a (2 e3(k_a) + 2 sum k_a) = -3|G|;
  spectrum upstairs, from exact line-bundle cohomology (Koszul sequence on (P1)^4, Bott-Kunneth, generic
  rank of multiplication by a random (2,2,2,2) polynomial over F_32003): h^*(L_a) = (0, h1, 0, 0) (no
  anti-10s), h^0 = h^3 = 0 on every L_a + L_b, and at least one 5 (Higgs pair) from h^2(L_a + L_b).
(C3) at the group level: a freely acting G of order 2 or 4 exists on X, and a Wilson line diag(1,1,1,-1,-1)
in G breaks SU(5) to the Standard Model group. For the free Z2 that swaps the two coordinates of every P1
(no factor permuted), every line bundle is equivariant. NOT checked here: the G-representation on the
cohomology (which fixes the downstairs spectrum, the doublet-triplet split (C6) and vector-like exotics (C5));
that needs the equivariant cohomology, as in AGLP's database. Label: candidate.

The scan over line bundles with entries in [-2, 2] gives 372 sums passing (C1), (C2) and the index screens,
228 passing the exact upstairs spectrum, and 10 classes up to permuting the four P1 factors (CLASSES).
"""
import math
import itertools
import random

import numpy as np

P = 32003
rnd = random.Random(12345)
MONO = list(itertools.product(range(3), repeat=4))            # exponent of x_i in factor i; y_i exponent = 2 - a_i
COEF = {m: rnd.randrange(1, P) for m in MONO}

def basis(n):
    """Per-factor basis of H^*(P1, O(n)) as (degree, list of (exp_x, exp_y))."""
    if n >= 0: return 0, [(i, n - i) for i in range(n + 1)]
    if n <= -2: return 1, [(-i, n + i) for i in range(1, -n)]
    return None, []

def cohom_A(m):
    """(degree, basis list of 4-tuples of (ex, ey)) of H^*(A, O(m))."""
    deg = 0; bs = []
    for n in m:
        d, b = basis(n)
        if d is None: return None, []
        deg += d; bs.append(b)
    return deg, list(itertools.product(*bs))

def valid(e, kind):
    ex, ey = e
    return (ex >= 0 and ey >= 0) if kind == 0 else (ex <= -1 and ey <= -1)

def rank_mod(rows, ncols):
    rows = [dict(r) for r in rows if r]
    rank = 0; piv = {}
    for r in rows:
        r = {c: v % P for c, v in r.items() if v % P}
        while r:
            c = min(r)
            if c in piv:
                pr = piv[c]; f = r[c]
                for cc, vv in pr.items():
                    r[cc] = (r.get(cc, 0) - f * vv) % P
                    if r[cc] == 0: del r[cc]
            else:
                inv = pow(r[c], P - 2, P); r = {cc: vv * inv % P for cc, vv in r.items()}
                piv[c] = r; rank += 1; break
    return rank

def mult_rank(m):
    """Rank of p: H^q(A, O(m-2)) -> H^q(A, O(m)) (0 if the degrees differ)."""
    dN, bN = cohom_A(tuple(x - 2 for x in m)); dK, bK = cohom_A(m)
    if dN is None or dK is None or dN != dK or not bN or not bK: return 0
    kinds = [basis(x - 2)[0] for x in m]
    if kinds != [basis(x)[0] for x in m]: return 0
    idx = {b: i for i, b in enumerate(bK)}
    rows = []
    for b in bN:
        row = {}
        for mono, c in COEF.items():
            img = []
            ok = True
            for f in range(4):
                e = (b[f][0] + mono[f], b[f][1] + 2 - mono[f])
                if not valid(e, kinds[f]): ok = False; break
                img.append(e)
            if ok:
                j = idx[tuple(img)]; row[j] = (row.get(j, 0) + c) % P
        rows.append(row)
    return rank_mod(rows, len(bK))

def h(k):
    """(h0, h1, h2, h3) of O_X(k)."""
    k = tuple(k); out = [0, 0, 0, 0, 0]
    dN, bN = cohom_A(tuple(x - 2 for x in k)); dK, bK = cohom_A(k)
    r = mult_rank(k)
    # coker in degree dK contributes to h^{dK}; ker in degree dN contributes to h^{dN - 1}
    if dK is not None and bK: out[dK] += len(bK) - r
    if dN is not None and bN and dN >= 1: out[dN - 1] += len(bN) - r
    assert out[4] == 0, (k, out)
    return tuple(out[:4])



def ind(k):
    return 2 * sum(math.prod(c) for c in itertools.combinations(k, 3)) + 2 * sum(k)


def _add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def s_of_t(t):
    return np.array([sum(math.prod(c) for c in itertools.combinations([t[j] for j in range(4) if j != i], 2)) for i in range(4)])


def kahler_point(K, t0, iters=60):
    """Refine t0 to a Kahler point where all five slopes vanish (Gauss-Newton in log t); None if it fails."""
    A = np.array(K, dtype=float); u = np.log(np.array(t0, dtype=float))
    for _ in range(iters):
        t = np.exp(u); s = s_of_t(t); F = A @ s / np.max(s)
        if np.max(np.abs(F)) < 1e-12:
            return t
        J = np.zeros((len(K), 4)); h_ = 1e-7
        for i in range(4):
            du = np.zeros(4); du[i] = h_
            tt = np.exp(u + du); J[:, i] = (A @ s_of_t(tt) / np.max(s_of_t(tt)) - F) / h_
        step = np.linalg.lstsq(J, -F, rcond=None)[0]
        u = u + step
    t = np.exp(u)
    return t if np.max(np.abs(A @ s_of_t(t))) < 1e-9 * np.max(s_of_t(t)) else None


def refute(K, group_order, t0=(1, 1, 1, 1)):
    """Every reason the line-bundle sum K is not a three-family candidate on X/G (empty list: candidate)."""
    K = [tuple(k) for k in K]
    why = []
    if len(K) != 5:
        return ["SU(5) needs five line bundles"]
    if any(sum(k[i] for k in K) for i in range(4)):
        why.append("c1(V) != 0")
        return why
    for i in range(4):
        if 24 + 2 * sum(sum(math.prod(c) for c in itertools.combinations([k[j] for j in range(4) if j != i], 2)) for k in K) < 0:
            why.append(f"anomaly fails along J_{i + 1}")
    if sum(ind(k) for k in K) != -3 * group_order:
        why.append(f"index {sum(ind(k) for k in K)} != -3|G| = {-3 * group_order}")
    if kahler_point(K, t0) is None:
        why.append("no Kahler point with all slopes zero found from t0")
    hs = [h(k) for k in K]
    if any(x[0] or x[2] or x[3] for x in hs):
        why.append("some L_a has h0, h2 or h3: anti-10s or unstable")
    pairs = [h(_add(K[a], K[b])) for a in range(5) for b in range(a + 1, 5)]
    if any(x[0] or x[3] for x in pairs):
        why.append("some L_a + L_b has h0 or h3")
    if not any(x[2] for x in pairs):
        why.append("no 5 upstairs: no Higgs pair")
    return why


CLASSES = [[2, [[-2, 1, 1, -1], [-1, -1, 1, 1], [-1, -1, 1, 1], [2, 0, -2, 1], [2, 1, -1, -2]], [1.6545, 0.9076, 0.9076, 1.6545]], [4, [[-2, 1, 0, -1], [-1, -1, 1, 1], [-1, -1, 1, 1], [2, 0, -2, 1], [2, 1, 0, -2]], [0.238, 0.0151, 0.0716, 0.0502]], [2, [[-1, 0, 0, 1], [-1, 0, 0, 1], [-1, 0, 0, 1], [1, -2, 1, -1], [2, 2, -1, -2]], [1.0775, 1.0775, 0.2694, 1.0775]], [2, [[-1, -1, 1, 0], [-1, 0, 0, 1], [-1, 0, 0, 1], [1, -1, 0, 0], [2, 2, -1, -2]], [1.0775, 1.0775, 0.2694, 1.0775]], [2, [[-1, 0, 1, 0], [-1, 0, 1, 0], [0, -2, 0, 1], [1, 1, -2, 0], [1, 1, 0, -1]], [1.4149, 1.4149, 1.4149, 0.3537]], [4, [[-1, 0, 1, 0], [-1, 1, 0, 0], [0, -2, 1, 1], [1, 0, -2, 1], [1, 1, 0, -2]], [1.0, 1.0, 1.0, 1.0]], [4, [[-1, 0, 0, 1], [-1, 0, 0, 1], [0, -2, 1, 1], [1, 1, -2, -1], [1, 1, 1, -2]], [1.4322, 2.7296, 6.1753, 1.4322]], [4, [[-1, -1, 1, 1], [-1, 1, 0, 0], [0, -2, 1, 1], [1, 1, -2, 0], [1, 1, 0, -2]], [1.0, 1.0, 1.0, 1.0]], [4, [[-1, 0, 1, 0], [-1, 1, -2, 0], [0, -1, 0, 1], [0, -1, 0, 1], [2, 1, 1, -2]], [5.6774, 1.2221, 5.6774, 1.2221]], [4, [[-1, 0, 1, 0], [-1, 1, -2, 0], [0, -1, 0, 1], [1, -1, -1, 1], [1, 1, 2, -2]], [5.6774, 1.2221, 5.6774, 1.2221]]]
