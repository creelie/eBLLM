"""The diagonal classes ev_Z(v), v in T D, at A_0 = E_0^6.

T D is the tangent space at A_0 of the deformations of the polarised abelian sixfold with its action of
K = Q(i) (i on z_1, z_2, z_3, -i on z_4, z_5, z_6): the maps v: Vbar -> V, v(e_l bar) = sum_k v_kl e_k, that are
K-linear (v_kl = 0 unless one of k, l is at most 3 and the other at least 4) and preserve theta (v_kl = v_lk).
It has dimension 9, coordinates Y_mj = v_{3+m, j}.

For Z = Z_zeta, W = T_0 Z is spanned by w_j = -zeta_j e_j + e_{3+j}, and V/W has the coordinates
f_m(z) = z_m + zeta_m z_{3+m}.  The class ev_Z(v) in H^1(Z, N_Z) = Hom(Wbar, V/W) is the matrix
f_m(v(w_j bar)) = Y_jm - zeta_m zetabar_j Y_mj.  Its kernel is the diagonal of Y and one line in each pair
(m, j), so ev_Z has rank 3 on T D for every zeta: no threefold piece has a vanishing diagonal class.

    python3 e06_ev.py
"""
import itertools
from fractions import Fraction


class G:
    """An element a + b i of Q(i), exact."""
    __slots__ = ("a", "b")

    def __init__(self, a, b=0):
        self.a, self.b = Fraction(a), Fraction(b)

    def __add__(self, o): return G(self.a + o.a, self.b + o.b)
    def __sub__(self, o): return G(self.a - o.a, self.b - o.b)
    def __mul__(self, o): return G(self.a * o.a - self.b * o.b, self.a * o.b + self.b * o.a)
    def conj(self): return G(self.a, -self.b)
    def inv(self):
        n = self.a * self.a + self.b * self.b
        return G(self.a / n, -self.b / n)
    def __eq__(self, o): return self.a == o.a and self.b == o.b
    def __bool__(self): return bool(self.a) or bool(self.b)


ONE, I = G(1), G(0, 1)
MU4 = [ONE, I, G(-1), G(0, -1)]
ZETAS = [z for z in itertools.product(MU4, repeat=3) if (z[0] * z[1] * z[2]) * (z[0] * z[1] * z[2]) == ONE]


def rank(rows):
    """Rank over Q(i) by Gaussian elimination."""
    rows = [list(r) for r in rows]
    r, ncol = 0, len(rows[0])
    for c in range(ncol):
        p = next((i for i in range(r, len(rows)) if rows[i][c]), None)
        if p is None:
            continue
        rows[r], rows[p] = rows[p], rows[r]
        inv = rows[r][c].inv()
        rows[r] = [x * inv for x in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c]:
                f = rows[i][c]
                rows[i] = [x - f * y for x, y in zip(rows[i], rows[r])]
        r += 1
    return r


def ev_matrix(zeta):
    """The 9 x 9 matrix of Y -> (Y_jm - zeta_m conj(zeta_j) Y_mj)_{m, j}."""
    idx = [(m, j) for m in range(3) for j in range(3)]
    rows = []
    for (m, j) in idx:
        row = [G(0)] * 9
        row[idx.index((j, m))] = row[idx.index((j, m))] + ONE
        row[idx.index((m, j))] = row[idx.index((m, j))] - zeta[m] * zeta[j].conj()
        rows.append(row)
    return rows


def main():
    assert len(ZETAS) == 32
    ranks = {rank(ev_matrix(z)) for z in ZETAS}
    joint = rank([r for z in ZETAS for r in ev_matrix(z)])
    same = [z for z in ZETAS if z[0] * z[1] * z[2] == ONE]
    joint_same = rank([r for z in same for r in ev_matrix(z)])
    print("rank of ev_Z on T D, over the 32 threefolds:", sorted(ranks))
    print("rank of (ev_Z)_Z on T D for the 16 of one sign:", joint_same, "; for all 32:", joint)
    assert ranks == {3}


if __name__ == "__main__":
    main()
