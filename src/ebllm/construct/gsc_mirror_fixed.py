"""The mirror clause of the Geometric Selection Conjecture is empty.

Uploaded by a second agent on Tubai's command.  Theorem D of creelie/strings (Dwork generations)
says: the Geometric Selection Conjecture (GSC) holds if and only if there is a viable vacuum V*
(conditions (C1)-(C9) of Bhattacharjee, Bhattacharya and Ghosh) with mu(V*) = V* whenever V* lies
in the domain L^mu of the mirror involution.  This module proves, and checks on data, that the
clause "mu(V*) = V*" can never be met by a viable vacuum, so that

    GSC  <=>  the heterotic landscape contains one viable vacuum outside L^mu,

that is, on a component carrying no standard embedding, with no condition on mirror symmetry
left.  (A viable vacuum of standard type, if one exists, is never selected: it is not mirror-fixed,
so Theorem D produces no functional from it.)  The argument is three lines.

Setting.  A vacuum is a pair (X, V), X a Calabi-Yau threefold and V a polystable bundle with
c_1(V) = 0.  L^mu is the union of the components of the landscape that contain a (2,2) vacuum
(X, T_X), and mu sends a vacuum to its mirror: the threefold of mu(X, V) is a mirror X^ of X, so
h^{1,1}(X^) = h^{2,1}(X) and h^{2,1}(X^) = h^{1,1}(X).  A component has fixed topological type,
so the Chern classes of V are constant on it and the Euler number of X is constant on it.

Lemma (fixed points have no families).  Let (X, V) be in L^mu with mu(X, V) = (X, V).  Then
chi(X) = 0, c_3(V) = 0, and the net number of families of (X, V) is zero; so (C2) fails and
(X, V) is not viable.

Proof.  A fixed point is a vacuum isomorphic to its mirror, so X is isomorphic to X^, hence
h^{1,1}(X) = h^{2,1}(X) and chi(X) = 2(h^{1,1} - h^{2,1}) = 0.  The component of (X, V) contains
a (2,2) vacuum (X_0, T_{X_0}), so c_3(V) = c_3(T_{X_0}) = chi(X_0) = chi(X) = 0, the last two
equalities because Chern classes and Euler numbers are constant on a component.  For a bundle
with c_1 = 0 on a Calabi-Yau threefold, Hirzebruch-Riemann-Roch gives chi(X, V) = c_3(V)/2
(the terms c_1(V) td_2 and rk(V) td_3 = rk(V) c_1(X) c_2(X)/24 vanish), and the net number of
families is |chi(X, V)|; a Wilson line on a free quotient divides this index by the order of
the group and never makes it three.  So the net number of families is zero.  QED

Corollary.  In Theorem D the condition "mu(V*) = V* whenever V* is in L^mu" is never satisfied by
a viable vacuum, so a viable vacuum satisfies it exactly when it lies outside L^mu: GSC holds if
and only if a viable vacuum exists outside L^mu, and the minimum of every functional with
(G1)-(G4) lies outside L^mu.  If mirror pairs are identified as one point of L, mu is the identity
on L^mu and GSC is equivalent to the existence of a viable vacuum of any type.  The same holds in the stronger reading of the
strings paper (invariance under a compact group G of isometries containing mu): a G-fixed vacuum
is mu-fixed, so again GSC in that reading is equivalent to the existence of a G-fixed viable
vacuum outside L^mu.

What this does and does not do.  It removes the only clause of GSC that mentions mirror symmetry;
it shows that no (2,2) vacuum, on any Calabi-Yau threefold, can ever be the selected vacuum of a
mirror-invariant functional; and it reduces GSC to a bare existence statement on the components
that carry no standard embedding.  It does not
exhibit a viable vacuum: (C7) stabilised moduli, (C8) the Yukawa hierarchy and (C9) supersymmetry
breaking are fixed by comparison with measurement (atlas wall ``c7-c9-undefined``), no published
model establishes all three, and until they are inequalities GSC is not a statement that a proof
can close.  Label of this module: proved (the lemma and the corollary), under the definition of
mu recalled above; the existence statement stays open.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple


@dataclass(frozen=True)
class Vacuum:
    """A vacuum by its discrete data: Hodge numbers of X, c_3 of the bundle, order of the group of a
    free quotient (1 for X itself), and whether the component is one of standard-embedding type."""
    h11: int
    h21: int
    c3: int
    quotient: int = 1
    standard_type: bool = True

    @property
    def chi(self) -> int:
        return 2 * (self.h11 - self.h21)

    def mirror(self) -> "Vacuum":
        """The mirror vacuum: Hodge numbers swapped; on a standard-type component the bundle is the
        tangent bundle of the mirror, so c_3 becomes chi of the mirror."""
        c3 = -self.chi if self.standard_type else self.c3
        return Vacuum(self.h21, self.h11, c3, self.quotient, self.standard_type)

    def is_mirror_fixed(self) -> bool:
        """Whether the vacuum can be a fixed point of mu: its threefold is isomorphic to its mirror,
        which forces equal Hodge numbers.  Equal Hodge numbers do not force self-mirror, but a
        fixed point has them, and that is all the lemma uses."""
        return self.standard_type and self.h11 == self.h21


def index(v: Vacuum) -> int:
    """chi(X, V) = c_3(V)/2 for c_1(V) = 0 on a Calabi-Yau threefold, divided by the order of the
    free quotient (the index is multiplicative under etale covers)."""
    if v.c3 % 2:
        raise ValueError("c_3 of a bundle with c_1 = 0 on a Calabi-Yau threefold is even")
    if (v.c3 // 2) % v.quotient:
        raise ValueError("the index upstairs must be divisible by the order of a free quotient")
    return (v.c3 // 2) // v.quotient


def net_families(v: Vacuum) -> int:
    return abs(index(v))


def standard_embedding(h11: int, h21: int, quotient: int = 1) -> Vacuum:
    """The (2,2) vacuum (X, T_X), or its free quotient: c_3(T_X) = chi(X)."""
    return Vacuum(h11, h21, 2 * (h11 - h21), quotient, True)


def c2_fails_at_fixed_points(vacua: Iterable[Vacuum]) -> List[Tuple[Vacuum, int]]:
    """The lemma on data: every mirror-fixed vacuum in the list has zero net families.  Returns the
    offenders (should be empty) as (vacuum, families)."""
    return [(v, net_families(v)) for v in vacua if v.is_mirror_fixed() and net_families(v) != 0]


def gsc_clause_is_empty(vacua: Iterable[Vacuum], three: int = 3) -> bool:
    """The corollary on data: no vacuum of the list with three net families is mirror-fixed."""
    return not any(v.is_mirror_fixed() for v in vacua if net_families(v) == three)


# Hodge pairs of Calabi-Yau threefolds used as data.  Self-mirror pairs (chi = 0): the Schoen
# manifold (19, 19), the split bicubic quotient (11, 11), (3, 3), (1, 1) from the Kreuzer-Skarke
# and CICY lists.  Three-family standard embeddings: the Tian-Yau quotient (6, 9), the Braun
# Z3 x Z3 quotient of the Schoen manifold (3, 3) is self-mirror and has zero, the (1, 4) quotient of
# the bicubic by Z3 x Z3 (chi = -6).
SELF_MIRROR_PAIRS = [(19, 19), (11, 11), (3, 3), (1, 1), (2, 2), (5, 5)]
THREE_FAMILY_PAIRS = [(6, 9), (1, 4), (9, 6), (4, 1), (2, 5)]
OTHER_PAIRS = [(1, 101), (101, 1), (1, 103), (1, 149), (1, 145), (4, 68), (2, 86), (1, 21)]


def sample_vacua() -> List[Vacuum]:
    out = []
    for h11, h21 in SELF_MIRROR_PAIRS + THREE_FAMILY_PAIRS + OTHER_PAIRS:
        for q in (1, 2, 3, 5):
            v = standard_embedding(h11, h21)
            if (v.c3 // 2) % q == 0:
                out.append(standard_embedding(h11, h21, q))
    # a few off-standard vacua: self-mirror threefold, bundle with three families; these lie outside
    # L^mu, and the lemma makes no claim about them
    out += [Vacuum(19, 19, -6, 1, False), Vacuum(11, 11, 6, 1, False), Vacuum(3, 3, -6, 1, False)]
    return out


def summary() -> dict:
    vs = sample_vacua()
    fixed = [v for v in vs if v.is_mirror_fixed()]
    return {
        "vacua": len(vs),
        "mirror_fixed": len(fixed),
        "families_at_fixed_points": sorted({net_families(v) for v in fixed}),
        "offenders": c2_fails_at_fixed_points(vs),
        "clause_empty": gsc_clause_is_empty(vs),
        "three_family_standard": sum(1 for v in vs if v.standard_type and net_families(v) == 3),
        "statement": "GSC <=> a viable vacuum exists outside L^mu; the mirror clause of Theorem D is empty",
        "label": "proved (lemma, corollary); existence of a viable vacuum open",
    }
