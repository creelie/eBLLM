"""The polarised shape at A_0 = E_0^6 in terms of the threefold pieces alone.

For pieces O_{Z_x} (x) L^{k_x} [s_x] (zeta_x in mu_4^3, prod zeta_x = +-1) and L^l [t], write
eps_x = (-1)^{s_x} and M_p(e) = sum_x eps_x k_x^p zeta_x^e for e in {-1, 0, 1}^3.  Then ch(E) has the polarised
shape N (alpha + alphabar) + sum_m c_m theta^m with N != 0 exactly when

  M_0(e) = 0 for every e other than +-(1, 1, 1), and N = M_0(1, 1, 1) != 0;
  M_1(e) = 0 for every e with at most two nonzero coordinates (e = 0 included);
  M_2(e) = 0 for every e with exactly one nonzero coordinate.

The line bundles never matter.  In particular sum_x eps_x = 0 and sum_x eps_x k_x = 0: the threefold pieces
at even shifts and at odd shifts are equal in number and in total twist.

This script checks the statement against the exact Chern character of e06_count.py on random configurations.

    python3 e06_chern.py [trials]
"""
import itertools, random, sys
from e06_count import ZETAS, Piece, fadd, polarised, ZERO, MU4, qmul, ONE

E_ALL = list(itertools.product((-1, 0, 1), repeat=3))


def zpow(z, e):
    out = ONE
    for u, k in zip(z, e):
        p = MU4.index(u) * k % 4
        out = qmul(out, MU4[p])
    return out


def moments(zs):
    """zs: list of (zeta, twist, shift).  Returns M[p][e] as Gaussian integers (pairs)."""
    M = {p: {} for p in range(3)}
    for p in range(3):
        for e in E_ALL:
            re = im = 0
            for z, k, s in zs:
                c = zpow(z, e)
                w = (-1) ** (s % 2) * k ** p
                re += w * c[0]
                im += w * c[1]
            M[p][e] = (re, im)
    return M


def criterion(zs):
    M = moments(zs)
    for e in E_ALL:
        nz = sum(1 for x in e if x)
        if e not in ((1, 1, 1), (-1, -1, -1)) and M[0][e] != (0, 0):
            return False
        if nz <= 2 and M[1][e] != (0, 0):
            return False
        if nz == 1 and M[2][e] != (0, 0):
            return False
    return M[0][(1, 1, 1)] != (0, 0)


def exact(zs, lines):
    ch = {}
    for z, k, s in zs:
        ch = fadd(ch, Piece("Z", z, k, s).ch())
    for l, t in lines:
        ch = fadd(ch, Piece("L", None, l, t).ch())
    ok, N, _ = polarised(ch)
    return ok and N != ZERO


def random_config(rng):
    mode = rng.random()
    if mode < 0.4:
        # perturb the base configuration (all 32 at one twist, balanced), which is polarised
        zs = [(z, 0, 0 if qmul(qmul(z[0], z[1]), z[2]) == ONE else 1) for z in ZETAS]
        for _ in range(rng.randint(0, 3)):
            i = rng.randrange(len(zs))
            z, k, s = zs[i]
            r = rng.random()
            if r < 0.3:
                zs[i] = (z, k + rng.choice((-1, 1)), s)
            elif r < 0.6:
                zs[i] = (z, k, s + 1)
            else:
                zs.pop(i)
        if rng.random() < 0.5:                       # shift every twist: still polarised iff it was
            d = rng.randint(-2, 2)
            zs = [(z, k + d, s) for z, k, s in zs]
    else:
        n = rng.randint(1, 10)
        zs = [(z, rng.randint(-2, 2), rng.randint(0, 3)) for z in rng.sample(ZETAS, n)]
    lines = [(rng.randint(-3, 3), rng.randint(-2, 2)) for _ in range(rng.randint(0, 5))]
    return zs, lines


def main():
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 3000
    rng = random.Random(1)
    agree = pos = 0
    for _ in range(trials):
        zs, lines = random_config(rng)
        a, b = criterion(zs), exact(zs, lines)
        assert a == b, (zs, lines, a, b)
        agree += 1
        pos += a
    print(f"{agree} configurations, criterion = exact Chern character test on all; {pos} polarised")


if __name__ == "__main__":
    main()
