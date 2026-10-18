"""Adhikari-Cao weak-coupling thresholds for the finite subgroups of SU(2).

Adhikari and Cao (Ann. Probab. 53 (2025) 140-174, arXiv:2202.10375, Theorem 1.1) prove exponential
decay of correlations of Wilson loop functions for lattice gauge theory in four dimensions with a
finite gauge group G and action beta * sum_p Re(chi(1) - chi(sigma_p)), whenever

    beta >= (114 + 4 log |G|) / Delta_G,   Delta_G = min_{g != 1} Re(chi(1) - chi(g)).

With chi the character of the defining 2-dimensional representation, their beta is half of the
Wilson coupling beta_W used in the strong-coupling paper (weight exp((beta_W / 2) sum_p Re Tr U_p)),
so the threshold in Wilson units is 2 * beta.  This script generates each group as unit quaternions,
computes Delta_G exactly from the element orders, and prints the window between the strong-coupling
range beta_W < 2/9 (proved for SU(2) Haar measure) and the Adhikari-Cao range.
"""
import itertools
import math
from fractions import Fraction


def qmul(a, b):
    a0, a1, a2, a3 = a
    b0, b1, b2, b3 = b
    return (a0*b0 - a1*b1 - a2*b2 - a3*b3, a0*b1 + a1*b0 + a2*b3 - a3*b2,
            a0*b2 - a1*b3 + a2*b0 + a3*b1, a0*b3 + a1*b2 - a2*b1 + a3*b0)


def key(q):
    return tuple(round(x, 9) for x in q)


def generate(gens):
    elems = {key((1.0, 0.0, 0.0, 0.0)): (1.0, 0.0, 0.0, 0.0)}
    frontier = list(elems.values())
    while frontier:
        new = []
        for x in frontier:
            for g in gens:
                y = qmul(x, g)
                if key(y) not in elems:
                    elems[key(y)] = y
                    new.append(y)
        frontier = new
    return list(elems.values())


def delta(group):
    # trace of the SU(2) matrix of the quaternion q is 2 q0, so Re(chi(1) - chi(g)) = 2 - 2 q0
    return min(2 - 2 * q[0] for q in group if key(q) != key((1.0, 0, 0, 0)))


phi = (1 + 5 ** 0.5) / 2
c = math.cos
GROUPS = {
    "binary tetrahedral 2T": [(0.5, 0.5, 0.5, 0.5), (0, 1.0, 0, 0)],
    "binary octahedral 2O": [(0.5, 0.5, 0.5, 0.5), (2 ** -0.5, 2 ** -0.5, 0, 0)],
    "binary icosahedral 2I": [(0.5, 0.5, 0.5, 0.5), (phi / 2, 0.5, 1 / (2 * phi), 0)],
}
for n in (3, 6, 12, 24, 60):
    GROUPS[f"binary dihedral Dic{n}"] = [(c(math.pi / n), math.sin(math.pi / n), 0, 0), (0, 0, 1.0, 0)]
for n in (24, 120, 1000):
    GROUPS[f"cyclic Z{n}"] = [(c(2 * math.pi / n), math.sin(2 * math.pi / n), 0, 0)]


def main():
    rows = []
    for name, gens in GROUPS.items():
        G = generate(gens)
        d = delta(G)
        beta_ac = (114 + 4 * math.log(len(G))) / d
        rows.append((name, len(G), d, beta_ac, 2 * beta_ac))
    print(f"{'group':26s} {'|G|':>5s} {'Delta_G':>9s} {'beta_AC':>10s} {'beta_W':>10s}")
    for r in rows:
        print(f"{r[0]:26s} {r[1]:5d} {r[2]:9.5f} {r[3]:10.1f} {r[4]:10.1f}")
    orders = {r[0]: r[1] for r in rows}
    checks = [orders["binary tetrahedral 2T"] == 24, orders["binary octahedral 2O"] == 48,
              orders["binary icosahedral 2I"] == 120,
              abs(dict((r[0], r[2]) for r in rows)["binary icosahedral 2I"] - (2 - 2 * c(math.pi / 5))) < 1e-9]
    print(f"{sum(checks)} checks passed, {len(checks) - sum(checks)} failed")
    print("strong coupling (SU(2) Haar): beta_W < 2/9 = %.4f" % (2 / 9))
    return rows


if __name__ == "__main__":
    main()
