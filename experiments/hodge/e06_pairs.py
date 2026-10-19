"""Exact checks for Theorems 12 and 13, Lemma 15 and Corollary 16 of C8_chains.md, at A_0 = E_0^6.

  (A) For every weight vector h, every zeta, every j and every m != j, the entry M_mj of ev_Z(v) at the
      single coordinate Y = E_jm is h_{3+j}/h_m, nonzero; the same for zeta^(j).
  (B) The covectors a = f_j(zeta), b = f_j(zeta^(j)), n_k = f_k(zeta), r_k = f_k(-zeta) (k != j) form a basis
      of V^dual; W(zeta) lies in ker(a, n), W(zeta^(j)) in ker(b, n), W(Z_{-zeta}) in ker(b, r),
      W(Z_{-zeta^(j)}) in ker(a, r); W(T) + W(B) = V for T = Z_zeta, B = Z_{-zeta} and for
      T' = Z_{zeta^(j)}, B' = Z_{-zeta^(j)}.  So the T-side forms a ^ n_k lie in the summand
      N_{T'}^dual (x) W_{B'}^perp of the decomposition used for T'.
  (C) The threefolds that meet a general curve C_{zeta_j} x {y} or C_{-zeta_j} x {y} are Z_zeta and
      Z_{zeta^(j)} only, and C_{zeta_j} meets C_{-zeta_j} in 4 points.
  (D) Orbits: the X_e coefficient (e in {+-1}^3) of [Z_x] is zsign(x) times prod_{e_j = 1} x_j^2; the
      equations "the eight weight components of sum_x eps_x [Z_x] are those of N (alpha + alphabar)" imply
      w_c = N/4 for each of the four orbits c (the row w_c - N/4 lies in their span); random polarised
      configurations satisfy w_c = N/4 exactly, so N is divisible by 4.
  (E) theta_h X_e = 0 for the eight X_e and all weights (so the Weil classes are primitive), and each
      weight -2e, e in {+-1}^3, occurs in H^6(A_0) on X_e alone.

    python3 e06_pairs.py [trials]
"""
import itertools
import random
import sys
from fractions import Fraction

from e06_count import (ALPHA, C, CB, WEIL, ZERO, ONE, ZETAS, fadd, fmul, qmul, qconj, qscale, z_class, zsign,
                       zmeet)
from e06_ev import G, rank
from e06_weights import WEIGHTS, ev_matrix, exp_k, polarised, theta_h

NEG = lambda u: (-u[0], -u[1])


def g(q):
    return G(q[0], q[1])


def flip(z, j):
    return tuple(NEG(u) if i == j else u for i, u in enumerate(z))


def minus(z):
    return tuple(NEG(u) for u in z)


def covector(z, m):
    """f_m(zeta)(z) = z_m + zeta_m z_{3+m}, as a row vector on C^6."""
    v = [G(0)] * 6
    v[m] = G(1)
    v[3 + m] = g(z[m])
    return v


def tangent(z):
    """w_m = -zeta_m e_m + e_{3+m}, m = 0, 1, 2: a basis of W(zeta) = T_0 Z_zeta."""
    out = []
    for m in range(3):
        w = [G(0)] * 6
        w[m] = G(0) - g(z[m])
        w[3 + m] = G(1)
        out.append(w)
    return out


def pair(f, w):
    s = G(0)
    for x, y in zip(f, w):
        s = s + x * y
    return s


def check_A():
    n = 0
    for h in WEIGHTS:
        for z in ZETAS:
            for zz in [z] + [flip(z, j) for j in range(3)]:
                M = ev_matrix(zz, h)
                idx = [(m, j) for m in range(3) for j in range(3)]
                for j in range(3):
                    for m in range(3):
                        if m == j:
                            continue
                        col = idx.index((j, m))           # the coordinate Y_jm
                        entry = M[3 * m + j][col]          # row (m, j): the f_m component of ev(v) wbar_j
                        assert entry == G(Fraction(h[3 + j], h[m])) and entry, (h, z, j, m)
                        n += 1
    return n


def check_B():
    n = 0
    for z in ZETAS:
        for j in range(3):
            ks = [k for k in range(3) if k != j]
            a, b = covector(z, j), covector(flip(z, j), j)
            ns = [covector(z, k) for k in ks]
            rs = [covector(minus(z), k) for k in ks]
            assert b == covector(minus(z), j) or all(x == y for x, y in zip(b, covector(minus(z), j)))
            assert all(x == y for x, y in zip(a, covector(minus(flip(z, j)), j)))
            assert all(x == y for x, y in zip(ns[0], covector(flip(z, j), ks[0])))
            assert rank([a, b] + ns + rs) == 6
            kills = lambda fs, ws: all(not pair(f, w) for f in fs for w in ws)
            assert kills([a] + ns, tangent(z))
            assert kills([b] + ns, tangent(flip(z, j)))
            assert kills([b] + rs, tangent(minus(z)))
            assert kills([a] + rs, tangent(minus(flip(z, j))))
            assert rank(tangent(z) + tangent(minus(z))) == 6
            assert rank(tangent(flip(z, j)) + tangent(minus(flip(z, j)))) == 6
            # N_{T'}^dual = <b, n_k, n_l> and W_{B'}^perp = <a, r_k, r_l>: a ^ n_k is in the mixed summand
            NT1, WB1 = [b] + ns, [a] + rs
            assert rank(NT1) == 3 and rank(WB1) == 3 and rank(NT1 + WB1) == 6
            assert rank(WB1 + [a]) == 3 and all(rank(NT1 + [x]) == 3 for x in ns)
            # and they are dual to the right tangent spaces: b(w_j) = -2 zeta_j, a(w'_j) = 2 zeta_j
            assert pair(b, tangent(z)[j]) == G(0) - g(z[j]) - g(z[j])
            assert pair(a, tangent(flip(z, j))[j]) == g(z[j]) + g(z[j])
            n += 1
    return n


def check_C():
    n = 0
    for z in ZETAS:
        for j in range(3):
            others = [z2 for z2 in ZETAS if all(z2[m] == z[m] for m in range(3) if m != j)]
            assert sorted(map(ZETAS.index, others)) == sorted([ZETAS.index(z), ZETAS.index(flip(z, j))])
            # C_u cap C_{-u} has |u - (-u)|^2 = 4 points
            u = z[j]
            assert zmeet((u,), (NEG(u),))[1] == 4
            n += 1
    return n


def monomial(e):
    """X_e = prod_j (C_j if e_j = 1 else CB_j)."""
    f = C[0] if e[0] == 1 else CB[0]
    for j in (1, 2):
        f = fmul(f, C[j] if e[j] == 1 else CB[j])
    return f


ORBITS = [(1, 1, 1), (1, -1, -1), (-1, 1, -1), (-1, -1, 1)]


def label(z):
    return tuple(int(qmul(u, u)[0]) for u in z)


def coeff(form, mono):
    k, c0 = next(iter(mono.items()))
    c = form.get(k, ZERO)
    return qscale(qmul(c, qconj(c0)), Fraction(1) / (c0[0] ** 2 + c0[1] ** 2))


def check_D(trials, rng):
    E = list(itertools.product((1, -1), repeat=3))
    zc = {z: z_class(z) for z in ZETAS}
    # the X_e coefficients
    for z in ZETAS:
        assert label(z) in ORBITS
        for e in E:
            want = zsign(z)
            for j in range(3):
                if e[j] == 1:
                    want *= label(z)[j]
            assert coeff(zc[z], monomial(e)) == (Fraction(want), Fraction(0)), (z, e)
    assert all(sum(1 for z in ZETAS if label(z) == c) == 8 for c in ORBITS)
    # the orbits are those of the three coordinate negations
    for z in ZETAS:
        orb = {z}
        for _ in range(3):
            orb |= {flip(x, j) for x in orb for j in range(3)}
        assert {label(x) for x in orb} == {label(z)} and len(orb) == 8
    # the linear system in (eps_x)_x and N: rank unchanged when the rows w_c - N/4 are added
    weil = {e: coeff(WEIL, monomial(e)) for e in E}
    rows = []
    for e in E:
        row = [g(coeff(zc[z], monomial(e))) for z in ZETAS] + [G(0) - g(weil[e])]
        rows.append(row)
    r0 = rank(rows)
    for c in ORBITS:
        row = [G(zsign(z)) if label(z) == c else G(0) for z in ZETAS] + [G(Fraction(-1, 4))]
        assert rank(rows + [row]) == r0, c
    # random configurations with the polarised shape
    pos = 0
    for h in WEIGHTS:
        _, pw = theta_h(h)
        record = [(z, 0, 0 if zsign(z) == 1 else 1) for z in ZETAS]
        for t in range(trials):
            if t == 0:
                zs = record
            elif rng.random() < 0.6:
                d = rng.randint(-2, 2)
                zs = [(z, k + d, s) for z, k, s in record]
                for _ in range(rng.randint(0, 3)):
                    i = rng.randrange(len(zs))
                    z, k, s = zs[i]
                    zs[i] = (z, k + rng.choice((-1, 1)), s)
                if rng.random() < 0.5:   # add a cancelling pair at one threefold
                    z = rng.choice(ZETAS)
                    k = rng.randint(-2, 2)
                    zs = zs + [(z, k, 0), (z, k + rng.randint(-1, 1), 1)]
            else:
                zs = [(z, rng.randint(-2, 2), rng.randint(0, 3)) for z in rng.sample(ZETAS, rng.randint(1, 12))]
            lines = [(rng.randint(-3, 3), rng.randint(-2, 2)) for _ in range(rng.randint(0, 4))]
            ch = {}
            for z, k, s in zs:
                ch = fadd(ch, fmul(zc[z], exp_k(pw, k)), (Fraction((-1) ** (s % 2)), Fraction(0)))
            for l, s in lines:
                ch = fadd(ch, exp_k(pw, l), (Fraction((-1) ** (s % 2)), Fraction(0)))
            ok, N = polarised(ch, pw)
            if not ok or N == ZERO:
                continue
            pos += 1
            assert N[1] == 0
            w = {c: 0 for c in ORBITS}
            for z, _, s in zs:
                w[label(z)] += (-1) ** (s % 2) * zsign(z)
            assert all(Fraction(w[c]) == N[0] / 4 for c in ORBITS), (h, zs, w, N)
            assert N[0].denominator == 1 and N[0].numerator % 4 == 0
    return r0, pos


def check_E():
    E = list(itertools.product((1, -1), repeat=3))
    for h in WEIGHTS:
        t, _ = theta_h(h)
        assert not fmul(t, WEIL)
        for e in E:
            assert not fmul(t, monomial(e)), (h, e)
    # weights: dz_j +e_j, dz_{3+j} -e_j, dzbar_j -e_j, dzbar_{3+j} +e_j (generators 0..5 dz, 6..11 dzbar)
    def wt(i):
        j = i % 3
        sgn = {0: 1, 1: -1, 2: -1, 3: 1}[i // 3]
        v = [0, 0, 0]
        v[j] = sgn
        return v
    count = {}
    for gens in itertools.combinations(range(12), 6):
        if sum(1 for i in gens if i < 6) != 3:
            continue                                   # (3, 3)-forms
        w = [0, 0, 0]
        for i in gens:
            w = [x + y for x, y in zip(w, wt(i))]
        if all(abs(x) == 2 for x in w):
            count.setdefault(tuple(w), []).append(sum(1 << i for i in gens))
    assert len(count) == 8 and all(len(v) == 1 for v in count.values())
    for e in E:
        mono = monomial(e)
        key = next(iter(mono))
        assert [key] in count.values()
    return len(count)


def main():
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    rng = random.Random(12)
    print("(A) entries M_mj at Y = E_jm equal h_{3+j}/h_m, nonzero:", check_A(), "cases")
    print("(B) the basis a, b, n_k, n_l, r_k, r_l and the four kernels:", check_B(), "pairs (zeta, j)")
    print("(C) only Z_zeta and Z_zeta^(j) meet the general curves; C_u meets C_-u in 4 points:", check_C(),
          "pairs")
    r0, pos = check_D(trials, rng)
    print(f"(D) X_e coefficients zsign * prod x_j^2; rank of the eight equations {r0}; w_c = N/4 is in their span"
          f" for the four orbits; {pos} random polarised configurations over {len(WEIGHTS)} weights, all with"
          " w_c = N/4 and 4 | N")
    print("(E) theta_h X_e = 0 for the eight X_e and every weight; each weight -2e occurs on X_e alone:",
          check_E(), "weights")


if __name__ == "__main__":
    main()
