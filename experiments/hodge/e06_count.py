"""Counting bounds for the convolutions at the CM point A_0 = E_0^6 of Bhattacharjee-Bhattacharya 2026
(doi:10.5281/zenodo.23439578, Lemma lem:cmext, Lemma lem:cmmeet, Appendix app:cmpoint).

Pieces: O_{Z_zeta} (x) L^k [s] for the 32 abelian threefolds Z_zeta = C_{zeta_1} x C_{zeta_2} x C_{zeta_3},
zeta in mu_4^3 with prod zeta = +-1, and L^l [t].  The polarised criterion asks dim Ext^2(E, E) = 57.

Two lower bounds for dim Ext^2(E, E), both valid for every order of the pieces and every twisted
differential:

  (1) C^2 - C^1 - C^3, where C^j is the dimension of the total-degree-j part of the E_1 page
      sum_{a,b} Ext^k(P_a, P_b), total degree k + s_b - s_a (every differential of every page lowers the
      degree-2 part by at most the ranks it uses, and those ranks sum to at most C^1 + C^3);
  (2) the safe classes: a class in Ext^k(P_a, P_b) of total degree 2 can be hit only from a class of total
      degree 1 in a block (a'', b'') with a ~> a'' and b'' ~> b in the graph of possible Maurer-Cartan
      components (u -> v when Ext^{1 + s_u - s_v}(P_u, P_v) != 0), and can map only into a block (a', b')
      of total degree 3 with a' ~> a and b ~> b'; a class with neither survives to E_infinity.

Dimensions of the groups between pieces come from Table tab:cmext (exact).  For two threefolds meeting
along a curve or a surface (lem:cmmeet) only the E_2 page of the local-to-global spectral sequence is
known; its dimensions are used as upper bounds for C^1 and C^3 and the degree-2 classes of those blocks
are not counted as safe, so both bounds stay valid.

The Chern character is computed exactly in the Hodge ring of A_0 (exterior algebra on dz_j, dzbar_j with
Gaussian rational coefficients) and each configuration is kept only when ch(E) has the polarised shape
N (alpha + alphabar) + sum c_m theta^m with N != 0.

    python3 e06_count.py            # the base check and the four open families in small windows
"""
from __future__ import annotations

import itertools
import json
import sys
from fractions import Fraction
from math import comb, factorial
from typing import Dict, List, Tuple

# -- Gaussian rationals and the exterior algebra on 12 generators ---------------------------------------
Q = Tuple[Fraction, Fraction]           # x + i y
ZERO: Q = (Fraction(0), Fraction(0))
ONE: Q = (Fraction(1), Fraction(0))
I: Q = (Fraction(0), Fraction(1))


def qadd(a: Q, b: Q) -> Q:
    return (a[0] + b[0], a[1] + b[1])


def qmul(a: Q, b: Q) -> Q:
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def qscale(a: Q, r: Fraction) -> Q:
    return (a[0] * r, a[1] * r)


def qconj(a: Q) -> Q:
    return (a[0], -a[1])


Form = Dict[int, Q]                      # bitmask of generators -> coefficient; generators 0..5 dz_j, 6..11 dzbar_j


def wedge_sign(m1: int, m2: int) -> int:
    """Sign of reordering the generators of m1 then m2 into increasing order."""
    s = 0
    for i in range(12):
        if m2 >> i & 1:
            s += bin(m1 >> (i + 1)).count("1")
    return -1 if s % 2 else 1


def fmul(f: Form, g: Form) -> Form:
    out: Form = {}
    for m1, c1 in f.items():
        for m2, c2 in g.items():
            if m1 & m2:
                continue
            c = qmul(c1, c2)
            if wedge_sign(m1, m2) < 0:
                c = (-c[0], -c[1])
            m = m1 | m2
            out[m] = qadd(out.get(m, ZERO), c)
    return {m: c for m, c in out.items() if c != ZERO}


def fadd(f: Form, g: Form, cg: Q = ONE) -> Form:
    out = dict(f)
    for m, c in g.items():
        out[m] = qadd(out.get(m, ZERO), qmul(c, cg))
    return {m: c for m, c in out.items() if c != ZERO}


def fscale(f: Form, c: Q) -> Form:
    return {m: qmul(v, c) for m, v in f.items() if qmul(v, c) != ZERO}


def gen2(p: int, q: int) -> Form:
    """(i/2) dz_p ^ dzbar_q, p, q in 0..5."""
    return {(1 << p) | (1 << (6 + q)): (Fraction(0), Fraction(1, 2))}


A = [gen2(j, j) for j in range(3)]
B = [gen2(3 + j, 3 + j) for j in range(3)]
C = [gen2(j, 3 + j) for j in range(3)]
CB = [gen2(3 + j, j) for j in range(3)]
THETA: Form = {}
for j in range(3):
    THETA = fadd(fadd(THETA, A[j]), B[j])
MU4: List[Q] = [ONE, I, (Fraction(-1), Fraction(0)), (Fraction(0), Fraction(-1))]
ALPHA = fmul(fmul(C[0], C[1]), C[2])
ALPHABAR = fmul(fmul(CB[0], CB[1]), CB[2])
WEIL = fadd(ALPHA, ALPHABAR)
THETA_POW = [{0: ONE}]
for _ in range(6):
    THETA_POW.append(fmul(THETA_POW[-1], THETA))


def curve_class(j: int, zeta: Q) -> Form:
    return fadd(fadd(fadd(A[j], B[j]), fscale(C[j], qconj(zeta))), fscale(CB[j], zeta))


def z_class(zeta: Tuple[Q, Q, Q]) -> Form:
    f = curve_class(0, zeta[0])
    for j in (1, 2):
        f = fmul(f, curve_class(j, zeta[j]))
    return f


def exp_theta(k: int) -> Form:
    f: Form = {}
    for m in range(7):
        f = fadd(f, THETA_POW[m], (Fraction(k ** m, factorial(m)), Fraction(0)))
    return f


def degree(m: int) -> int:
    return bin(m).count("1")


def polarised(ch: Form) -> Tuple[bool, Q, List[Q]]:
    """Is ch = N (alpha + alphabar) + sum_m c_m theta^m ?  Returns (yes, N, c)."""
    n = ch.get(next(iter(ALPHA)), ZERO)
    n = qscale(n, Fraction(1) / Fraction(next(iter(ALPHA.values()))[1]) if False else Fraction(1))
    # N is the coefficient of alpha in ch divided by the coefficient of alpha in WEIL
    key = next(iter(ALPHA))
    N = (Fraction(0), Fraction(0))
    wk = WEIL[key]
    ck = ch.get(key, ZERO)
    # divide ck by wk (Gaussian rationals)
    den = wk[0] ** 2 + wk[1] ** 2
    N = qscale(qmul(ck, qconj(wk)), Fraction(1) / den)
    rest = fadd(ch, WEIL, (-N[0], -N[1]))
    cs = []
    for m in range(7):
        part = {b: c for b, c in rest.items() if degree(b) == 2 * m}
        tp = THETA_POW[m]
        if not part:
            cs.append(ZERO)
            continue
        b0, c0 = next(iter(tp.items()))
        if b0 not in part:
            return False, N, cs
        den0 = c0[0] ** 2 + c0[1] ** 2
        lam = qscale(qmul(part[b0], qconj(c0)), Fraction(1) / den0)
        if fadd(part, tp, (-lam[0], -lam[1])):
            return False, N, cs
        cs.append(lam)
    return True, N, cs


# -- the pieces and their Ext groups --------------------------------------------------------------------
ZETAS = [z for z in itertools.product(MU4, repeat=3)
         if qmul(qmul(z[0], z[1]), z[2]) in (ONE, (Fraction(-1), Fraction(0)))]
assert len(ZETAS) == 32
CHI_Z = 8                                   # chi_{Z_zeta} = 8 (lem:cmcurves (iii))


def zsign(z) -> int:
    return 1 if qmul(qmul(z[0], z[1]), z[2]) == ONE else -1


def zmeet(z, z2) -> Tuple[int, int]:
    """(d, D): d = number of shared coordinates, D = number of components of Z cap Z'."""
    d, D = 0, 1
    for u, v in zip(z, z2):
        if u == v:
            d += 1
        else:
            diff = (u[0] - v[0], u[1] - v[1])
            D *= int(diff[0] ** 2 + diff[1] ** 2)
    return d, D


class Piece:
    def __init__(self, kind: str, zeta, twist: int, shift: int):
        self.kind, self.zeta, self.twist, self.shift = kind, zeta, twist, shift

    def ch(self) -> Form:
        f = exp_theta(self.twist)
        if self.kind == "Z":
            f = fmul(z_class(self.zeta), f)
        return fscale(f, (Fraction((-1) ** (self.shift % 2)), Fraction(0)))

    def __repr__(self):
        if self.kind == "L":
            return f"L^{self.twist}[{self.shift}]"
        return f"O_Z{''.join('1i-j'[MU4.index(u)] for u in self.zeta)}L^{self.twist}[{self.shift}]"


def ext_dims(p: Piece, q: Piece) -> Tuple[Dict[int, int], bool]:
    """Dimensions of Ext^k(p, q) by degree k (table tab:cmext and lem:cmmeet).  The flag says whether the
    numbers are exact (True) or E_2 upper bounds (False)."""
    m = q.twist - p.twist
    if p.kind == "L" and q.kind == "L":
        if m > 0:
            return {0: m ** 6}, True
        if m < 0:
            return {6: m ** 6}, True
        return {k: comb(6, k) for k in range(7)}, True
    if p.kind == "Z" and q.kind == "L":
        if m > 0:
            return {3: CHI_Z * m ** 3}, True
        if m < 0:
            return {6: CHI_Z * (-m) ** 3}, True
        return {k: comb(3, k - 3) for k in range(3, 7)}, True
    if p.kind == "L" and q.kind == "Z":
        if m > 0:
            return {0: CHI_Z * m ** 3}, True
        if m < 0:
            return {3: CHI_Z * (-m) ** 3}, True
        return {k: comb(3, k) for k in range(4)}, True
    # two threefolds
    if p.zeta == q.zeta:
        if m > 0:
            return {k: comb(3, k) * CHI_Z * m ** 3 for k in range(4)}, True
        if m < 0:
            return {k: comb(3, k - 3) * CHI_Z * (-m) ** 3 for k in range(3, 7)}, True
        return {k: comb(6, k) for k in range(7)}, True
    d, D = zmeet(p.zeta, q.zeta)
    if d == 0:
        return {3: D}, True
    c = 3 - d
    # lem:cmmeet: E_2^{p,q} = H^p(W, O_W^{C(d, q-c)} (x) L^m|_W); W = D translates of an abelian d-fold with
    # (theta|_W)^d / d! = 2^d; ample: H^0 only, chi = (2m)^d; anti-ample: H^d only; trivial: all H^p.
    out: Dict[int, int] = {}
    if m > 0:
        for q_ in range(c, 4):
            out[q_] = out.get(q_, 0) + D * comb(d, q_ - c) * (2 * m) ** d
    elif m < 0:
        for q_ in range(c, 4):
            out[q_ + d] = out.get(q_ + d, 0) + D * comb(d, q_ - c) * (2 * (-m)) ** d
    else:
        for q_ in range(c, 4):
            for p_ in range(d + 1):
                out[p_ + q_] = out.get(p_ + q_, 0) + D * comb(d, q_ - c) * comb(d, p_)
    return out, False


def bounds(pieces: List[Piece]) -> dict:
    n = len(pieces)
    tot: Dict[int, int] = {}
    deg2_exact = {}                     # (a, b) -> exact dimension of total-degree-2 classes
    edge = [[False] * n for _ in range(n)]
    for a, pa in enumerate(pieces):
        for b, pb in enumerate(pieces):
            dims, exact = ext_dims(pa, pb)
            for k, dim in dims.items():
                t = k + pb.shift - pa.shift
                tot[t] = tot.get(t, 0) + dim
                if t == 2 and exact:
                    deg2_exact[(a, b)] = deg2_exact.get((a, b), 0) + dim
                if t == 1 and a != b:
                    edge[a][b] = True
    # reachability a ~> b (including a == b)
    reach = [[a == b or edge[a][b] for b in range(n)] for a in range(n)]
    for k in range(n):
        for a in range(n):
            if reach[a][k]:
                ra, rk = reach[a], reach[k]
                for b in range(n):
                    if rk[b]:
                        ra[b] = True
    deg1 = set()
    deg3 = set()
    for a, pa in enumerate(pieces):
        for b, pb in enumerate(pieces):
            dims, _ = ext_dims(pa, pb)
            for k in dims:
                t = k + pb.shift - pa.shift
                if t == 1:
                    deg1.add((a, b))
                if t == 3:
                    deg3.add((a, b))
    safe = 0
    for (a, b), dim in deg2_exact.items():
        hit = any(reach[a][a2] and reach[b2][b] and (a2, b2) != (a, b) for (a2, b2) in deg1)
        out = any(reach[a2][a] and reach[b][b2] and (a2, b2) != (a, b) for (a2, b2) in deg3)
        if not hit and not out:
            safe += dim
    c1, c2, c3 = tot.get(1, 0), tot.get(2, 0), tot.get(3, 0)
    return dict(C1=c1, C2=c2, C3=c3, euler=c2 - c1 - c3, safe=safe, lower=max(c2 - c1 - c3, safe))


def configuration_ch(pieces: List[Piece]) -> Tuple[bool, int]:
    ch: Form = {}
    for p in pieces:
        ch = fadd(ch, p.ch())
    ok, N, _ = polarised(ch)
    return ok and N != ZERO, int(N[0]) if N[1] == 0 and N[0].denominator == 1 else 0


def base(twist: int = 0, shift0: int = 0) -> List[Piece]:
    """The thirty-two threefolds at one twist, shifts of the parity of prod zeta."""
    return [Piece("Z", z, twist, shift0 + (0 if zsign(z) == 1 else 1)) for z in ZETAS]


def run() -> dict:
    out = {}
    print("sanity: S(1) - S(-1) = 32 (alpha + alphabar):",
          fadd({}, sum_classes(), ONE) == fscale(WEIL, (Fraction(32), Fraction(0))))
    print("sanity: theta . weil = 0:", fmul(THETA, WEIL) == {})
    # (0) the 35 pieces of prop:separated, three line bundles at twists above the threefolds
    for ls, ts in [((1, 2, 3), (0, 0, 0)), ((1, 2, 3), (2, 3, 4)), ((1, 2, 3), (-3, -2, -1))]:
        pcs = base() + [Piece("L", None, l, t) for l, t in zip(ls, ts)]
        ok, N = configuration_ch(pcs)
        b = bounds(pcs)
        print("base35", ls, ts, "polarised" if ok else "NOT polarised", "N =", N, b)
        out[f"base35 L{ls} shifts{ts}"] = dict(polarised=ok, N=N, **b)
    # (a) four to six line bundles: twists in 1..4, shifts in a window; exhaustive over small windows
    best = None
    count = 0
    for nL in (4, 5):
        for ls in itertools.combinations(range(1, 5), nL):
            for ts in itertools.product(range(-3, 4), repeat=nL):
                pcs = base() + [Piece("L", None, l, t) for l, t in zip(ls, ts)]
                ok, N = configuration_ch(pcs)
                if not ok:
                    continue
                count += 1
                b = bounds(pcs)
                if best is None or b["lower"] < best[0]:
                    best = (b["lower"], ls, ts, b)
    print(f"(a) >= 4 line bundles, twists 1..4, shifts -3..3: {count} polarised configurations; least lower bound",
          best)
    out["family_a"] = dict(count=count, least=best)
    # (b) a sheaf at two shifts: one extra copy of Z_zeta at shift s + delta
    best = None
    count = 0
    for z in ZETAS[:4]:
        for delta in (-3, -2, -1, 1, 2, 3):
            for ls, ts in [((1, 2, 3), (0, 0, 0)), ((1, 2, 3), (1, 2, 3))]:
                pcs = base() + [Piece("Z", z, 0, (0 if zsign(z) == 1 else 1) + delta)] + \
                      [Piece("L", None, l, t) for l, t in zip(ls, ts)]
                ok, N = configuration_ch(pcs)
                if not ok:
                    continue
                count += 1
                b = bounds(pcs)
                if best is None or b["lower"] < best[0]:
                    best = (b["lower"], repr(pcs[32]), ls, ts, b)
    print(f"(b) a sheaf at two shifts: {count} polarised configurations; least lower bound", best)
    out["family_b"] = dict(count=count, least=best)
    # (c) one threefold at three twists 0 < k' < k'' (needs the extra twists to cancel in ch: pairs with shifts)
    best = None
    count = 0
    z = ZETAS[0]
    for k1, k2 in itertools.combinations(range(1, 4), 2):
        for s1, s2 in itertools.product(range(-2, 3), repeat=2):
            for s1b, s2b in itertools.product(range(-2, 3), repeat=2):
                extra = [Piece("Z", z, k1, s1), Piece("Z", z, k1, s1b), Piece("Z", z, k2, s2), Piece("Z", z, k2, s2b)]
                pcs = base() + extra + [Piece("L", None, l, 0) for l in (1, 2, 3)]
                ok, N = configuration_ch(pcs)
                if not ok:
                    continue
                count += 1
                b = bounds(pcs)
                if best is None or b["lower"] < best[0]:
                    best = (b["lower"], [repr(e) for e in extra], b)
    print(f"(c) a threefold at three twists (pairs cancelling in ch): {count} polarised configurations; least", best)
    out["family_c"] = dict(count=count, least=best)
    # (d) two threefolds meeting along a surface at the same shift: Z_zeta' moved next to Z_zeta by a
    #     cancelling pair (Z_zeta' at s and s+1 both added, one of them at the shift of Z_zeta)
    best = None
    count = 0
    z = ZETAS[0]
    partners = [z2 for z2 in ZETAS if zmeet(z, z2)[0] == 2]
    for z2 in partners:
        s = 0 if zsign(z) == 1 else 1
        for delta in (1, -1):
            extra = [Piece("Z", z2, 0, s), Piece("Z", z2, 0, s + delta)]
            pcs = base() + extra + [Piece("L", None, l, 0) for l in (1, 2, 3)]
            ok, N = configuration_ch(pcs)
            if not ok:
                continue
            count += 1
            b = bounds(pcs)
            if best is None or b["lower"] < best[0]:
                best = (b["lower"], [repr(e) for e in extra], b)
    print(f"(d) a partner meeting along a surface at the same shift: {count} polarised configurations; least", best)
    out["family_d"] = dict(count=count, least=best)
    return out


def sum_classes() -> Form:
    f: Form = {}
    for z in ZETAS:
        f = fadd(f, z_class(z), (Fraction(zsign(z)), Fraction(0)))
    return f


if __name__ == "__main__":
    res = run()
    json.dump(res, open(sys.argv[1] if len(sys.argv) > 1 else "e06_count.json", "w"), indent=1, default=str)
