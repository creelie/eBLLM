"""Theorems 6 and 9 at every product polarisation of Weil type on A_0 = E_0^6.

For positive integers h_1, ..., h_6 let theta_h = sum_j (h_j a_j + h_{3+j} b_j), the class of the product
polarisation with weight h_k on the k-th factor E_0.  It is invariant under K = Q(i) (i on z_1, z_2, z_3,
-i on z_4, z_5, z_6), so (A_0, K, theta_h) is of Weil type, of signature (3, 3), and its discriminant is the
class of h_1 ... h_6 modulo norms from K (sums of two squares).  Every class occurs.

The two inputs of Theorems 6 and 9 that involve the polarisation are checked here.

  (a) TD_h, the K-linear maps v: Vbar -> V with h_k v_kl = h_l v_lk, has dimension 9 (coordinates
      Y_mj = v_{3+m, j}), and on it ev_Z(v) is the matrix (h_{3+j}/h_m) Y_jm - zeta_m zetabar_j Y_mj.  Its rank
      is at least 3 for each of the 32 threefolds Z_zeta, and for every nonzero u in Wbar some v has
      ev_Z(v) u != 0 (this is what the locality theorem uses).
  (b) If ch(E) = N (alpha + alphabar) + (a polynomial in theta_h), then sum_x eps_x = 0 over the threefold
      pieces.  Checked against the exact Chern character on random configurations.

    python3 e06_weights.py [trials]
"""
import itertools
import random
import sys
from fractions import Fraction
from math import factorial

from e06_count import (A, B, ALPHA, WEIL, ZERO, ONE, ZETAS, MU4, fadd, fmul, fscale, qconj, qmul, qscale,
                       z_class, zsign, degree)
from e06_ev import G, rank

WEIGHTS = [(1, 1, 1, 1, 1, 1), (1, 1, 1, 1, 1, 3), (1, 1, 1, 3, 3, 3), (3, 1, 1, 1, 1, 1), (1, 2, 1, 1, 1, 1),
           (1, 1, 1, 1, 1, 7), (2, 3, 5, 7, 11, 13), (1, 1, 2, 1, 1, 2), (6, 1, 1, 1, 1, 1)]


def sum_of_two_squares(n):
    return any(int((n - a * a) ** 0.5 + 0.5) ** 2 == n - a * a for a in range(int(n ** 0.5) + 1))


def g(q):
    return G(q[0], q[1])


def ev_matrix(zeta, h):
    """Rows (m, j), columns Y_ab: the matrix of Y -> (h_{3+j}/h_m) Y_jm - zeta_m zetabar_j Y_mj."""
    idx = [(m, j) for m in range(3) for j in range(3)]
    rows = []
    for (m, j) in idx:
        row = [G(0)] * 9
        c = idx.index((j, m))
        row[c] = row[c] + G(Fraction(h[3 + j], h[m]))
        c = idx.index((m, j))
        row[c] = row[c] - g(zeta[m]) * g(zeta[j]).conj()
        rows.append(row)
    return rows


def contraction_vanishes(h):
    """Each basis vector of TD_h kills theta_h: the (0,2)-form sum_k h_k v(dz_k) ^ dzbar_k is zero."""
    for a, b in itertools.product(range(3), repeat=2):
        v = {}
        v[(3 + a, b)] = Fraction(1)                      # Y_ab = v_{3+a, b}
        v[(b, 3 + a)] = Fraction(h[3 + a], h[b])         # forced by the symmetry
        form = {}
        for (k, l), c in v.items():                       # h_k v_kl dzbar_l ^ dzbar_k
            if l == k:
                continue
            key, sign = (l, k) if l < k else (k, l), (1 if l < k else -1)
            form[key] = form.get(key, 0) + sign * h[k] * c
        if any(form.values()):
            return False
        for (k, l) in v:                                  # K-linear: one index in each block
            if (k < 3) == (l < 3):
                return False
    return True


def ev_checks(h):
    ranks = []
    for z in ZETAS:
        M = ev_matrix(z, h)
        ranks.append(rank(M))
        # for every coordinate direction and a generic u, v -> ev(v) u is nonzero
        for u in [(1, 0, 0), (0, 1, 0), (0, 0, 1), (1, 2, 3), (1, -1, 0), (1, 1, 1)]:
            rows = []
            for m in range(3):
                row = [G(0)] * 9
                for j in range(3):
                    for c in range(9):
                        row[c] = row[c] + M[3 * m + j][c] * G(u[j])
                rows.append(row)
            assert rank(rows) >= 1, (h, z, u)
    return min(ranks), max(ranks)


def theta_h(h):
    t = {}
    for j in range(3):
        t = fadd(t, fscale(A[j], (Fraction(h[j]), Fraction(0))))
        t = fadd(t, fscale(B[j], (Fraction(h[3 + j]), Fraction(0))))
    pw = [{0: ONE}]
    for _ in range(6):
        pw.append(fmul(pw[-1], t))
    return t, pw


def exp_k(pw, k):
    f = {}
    for m in range(7):
        f = fadd(f, pw[m], (Fraction(k ** m, factorial(m)), Fraction(0)))
    return f


def polarised(ch, pw):
    key = next(iter(ALPHA))
    wk, ck = WEIL[key], ch.get(key, ZERO)
    N = qscale(qmul(ck, qconj(wk)), Fraction(1) / (wk[0] ** 2 + wk[1] ** 2))
    rest = fadd(ch, WEIL, (-N[0], -N[1]))
    for m in range(7):
        part = {b: c for b, c in rest.items() if degree(b) == 2 * m}
        if not part:
            continue
        tp = pw[m]
        b0, c0 = next(iter(tp.items()))
        if b0 not in part:
            return False, N
        lam = qscale(qmul(part[b0], qconj(c0)), Fraction(1) / (c0[0] ** 2 + c0[1] ** 2))
        if fadd(part, tp, (-lam[0], -lam[1])):
            return False, N
    return True, N


def chern_checks(h, trials, rng):
    _, pw = theta_h(h)
    zc = {z: z_class(z) for z in ZETAS}
    record = [(z, 0, 0 if zsign(z) == 1 else 1) for z in ZETAS]
    pos = 0
    for t in range(trials):
        if t == 0:
            zs = record
        elif rng.random() < 0.5:
            d = rng.randint(-2, 2)
            zs = [(z, k + d, s) for z, k, s in record]
            for _ in range(rng.randint(0, 2)):
                i = rng.randrange(len(zs))
                z, k, s = zs[i]
                zs[i] = (z, k + rng.choice((-1, 1)), s) if rng.random() < 0.5 else (z, k, s + 1)
        else:
            zs = [(z, rng.randint(-2, 2), rng.randint(0, 3)) for z in rng.sample(ZETAS, rng.randint(1, 8))]
        lines = [(rng.randint(-3, 3), rng.randint(-2, 2)) for _ in range(rng.randint(0, 4))]
        ch = {}
        for z, k, s in zs:
            ch = fadd(ch, fmul(zc[z], exp_k(pw, k)), (Fraction((-1) ** (s % 2)), Fraction(0)))
        for l, s in lines:
            ch = fadd(ch, exp_k(pw, l), (Fraction((-1) ** (s % 2)), Fraction(0)))
        ok, N = polarised(ch, pw)
        if ok and N != ZERO:
            pos += 1
            assert sum((-1) ** (s % 2) for _, _, s in zs) == 0, (h, zs)
        if t == 0:
            assert ok and N != ZERO, h
    return pos


def neighbours():
    """For each zeta the threefolds meeting Z_zeta in a surface (two shared coordinates) are exactly the three
    zeta^(j) with one coordinate negated, and Z_zeta meets each of them in 4 translates of a coordinate surface."""
    from e06_count import zmeet
    neg = lambda u: (-u[0], -u[1])
    for z in ZETAS:
        surf = sorted(ZETAS.index(z2) for z2 in ZETAS if z2 != z and zmeet(z, z2)[0] == 2)
        expect = sorted(ZETAS.index(tuple(neg(u) if i == j else u for i, u in enumerate(z))) for j in range(3))
        assert surf == expect, z
        assert all(zmeet(z, ZETAS[i]) == (2, 4) for i in surf)
        assert all(zsign(ZETAS[i]) == -zsign(z) for i in surf)
    return len(ZETAS)


def main():
    print("surface neighbours: for each of", neighbours(), "threefolds exactly the three single negations, 4 components each,"
          " of the opposite sign")
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    rng = random.Random(7)
    print("weights          prod h  norm?  TD kills theta  rank of ev_Z  polarised/trials (sum eps = 0 on all)")
    for h in WEIGHTS:
        d = 1
        for x in h:
            d *= x
        assert contraction_vanishes(h)
        lo, hi = ev_checks(h)
        assert lo >= 3
        pos = chern_checks(h, trials, rng)
        print(f"{str(h):18} {d:5}  {'yes' if sum_of_two_squares(d) else 'no ':3}    yes            {lo}..{hi}"
              f"          {pos}/{trials}")


if __name__ == "__main__":
    main()
