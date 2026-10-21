"""The exact constructions of TheoPhysEval (arXiv:2610.16733), as construction-mode objects.

"TheoPhysEval: Assessing AI agents at autonomous theoretical physics problem solving" (A. R.
Chandra, A. Mahajan, A. Sanyal, M. Wang, S. Raju and others, arXiv:2610.16733v1, 9 October 2026)
is a benchmark, not a theorem: fifty unpublished "turn-the-crank" problems from eleven areas of
theoretical physics, each with a numerical answer, run on five agents with and without web
search.  The best agent solves 49 of 50 with search and 46 without, which the authors read as
memorisation of the literature.  The paper proves nothing new and settles no open problem; its
own words are that none of its problems is a breakthrough open problem.

Two of its problems carry an exact mathematical construction that the engine can state and check
in rational arithmetic, and those are what this module holds, each with a check and a refuter:

    pi_series       the parametric series for pi from the Euler beta function (problem 9a, eq. A63;
                    the series of Saha and Sinha, PRL 132 (2024) 221601),
                        pi = 4 + sum_{n>=1} (1/n!) (1/(n+l) - 4/(2n+1)) ((2n+1)^2/(4(n+l)) - n)_{n-1},
                    with (x)_k the rising factorial.  The check: the partial sums approach pi for
                    every l > 0 tried, faster as l grows to about 10, and the l -> infinity limit
                    of each term is the Madhava-Leibniz term 4(-1)^n/(2n+1), proved here exactly
                    as an identity of the limit.  The refuter is that limit itself: the Leibniz
                    series has error about 1/(2N) after N terms, far worse than the finite-l series
                    at the same N, so the parameter is doing real work.
    hidden_zero     the hidden zero of a four-point residue at backward scattering (problem 9b).
                    With R_k(z) = sum_j c_j C_j^{lam}(z), lam = (d-3)/2, z = 1 + 2t/k, the zero at
                    t = -k is z = -1, and C_j^{lam}(-1) = (-1)^j (2 lam)_j / j!, so
                        sum_j (-1)^j (2 lam)_j / j! c_j = 0,
                    and for the Taylor coefficients of the pole R_k(t)/(k - s),
                    alpha_{n,m} = r_m / k^{n+1}, so sum_m (-k)^m alpha_{n,m} = 0 for every n.
                    The check reproduces the d = 4 and k = 1, 2 relations of the problem and solves
                    the d = 7, k = 3 case exactly (c_3 = 13/4, alpha_{n,3} = 26/27,
                    Xi = 108 c_3 + 67 alpha_{n,3} = 11219/27).  The refuter: a residue without the
                    zero (a single Gegenbauer polynomial) violates the relation.

Neither construction bears on the open targets of the engine.  Nothing in the paper concerns the
Hodge conjecture or the (F2), (F3') inputs, Lehmer's totient problem, or the non-perturbative
definition of the brane-gas theory (problem 1d, a retarded Green function supported on the
hyperboloid lambda + d^2 = 0, is a classical non-local electrodynamics and says nothing about
reflection positivity of an entire form factor).  The modlog run ``theophyseval`` records the
check as a stopped literature attempt.  Everything uses the standard library only.
"""
from __future__ import annotations

import math
from fractions import Fraction
from typing import Dict, List, Sequence

ARXIV = "2610.16733"
TITLE = "TheoPhysEval: Assessing AI agents at autonomous theoretical physics problem solving"


def rising(x: Fraction, k: int) -> Fraction:
    """The rising factorial (x)_k = x (x+1) ... (x+k-1), with (x)_0 = 1."""
    p = Fraction(1)
    for i in range(k):
        p *= x + i
    return p


# --------------------------------------------------------------------------- pi from the beta function
def pi_term(n: int, lam: Fraction) -> Fraction:
    """The n-th term (n >= 1) of the parametric series for pi, exactly."""
    lam = Fraction(lam)
    if n < 1 or lam <= 0:
        raise ValueError("n >= 1 and lambda > 0")
    x = Fraction((2 * n + 1) ** 2) / (4 * (n + lam)) - n
    return (1 / (n + lam) - Fraction(4, 2 * n + 1)) * rising(x, n - 1) / math.factorial(n)


def pi_partial(N: int, lam: Fraction) -> Fraction:
    """4 + the first N terms of the series."""
    return 4 + sum((pi_term(n, lam) for n in range(1, N + 1)), Fraction(0))


def leibniz_term(n: int) -> Fraction:
    """The l -> infinity limit of pi_term(n, l): 4 (-1)^n / (2n + 1)."""
    return Fraction(4 * (-1) ** n, 2 * n + 1)


def leibniz_limit_exact(n: int) -> Fraction:
    """The limit of pi_term(n, l) as l -> infinity, from the formula itself: 1/(n+l) -> 0 and
    (x)_{n-1} -> (-n)_{n-1} = (-1)^{n-1} n!, so the term tends to (-4/(2n+1)) (-n)_{n-1} / n!."""
    return Fraction(-4, 2 * n + 1) * rising(Fraction(-n), n - 1) / math.factorial(n)


def leibniz_partial(N: int) -> Fraction:
    return 4 + sum((leibniz_term(n) for n in range(1, N + 1)), Fraction(0))


def pi_errors(lams: Sequence[Fraction], N: int) -> Dict[Fraction, float]:
    """|partial sum - pi| after N terms for each lambda."""
    return {Fraction(l): abs(float(pi_partial(N, l)) - math.pi) for l in lams}


# --------------------------------------------------------------------------- hidden zeros
def gegenbauer_at_minus_one(j: int, lam: Fraction) -> Fraction:
    """C_j^lam(-1) = (-1)^j (2 lam)_j / j!."""
    return (-1) ** j * rising(2 * Fraction(lam), j) / math.factorial(j)


def gegenbauer(j: int, lam: Fraction, z: Fraction) -> Fraction:
    """C_j^lam(z) by the three-term recurrence, exactly."""
    lam, z = Fraction(lam), Fraction(z)
    if j == 0:
        return Fraction(1)
    c0, c1 = Fraction(1), 2 * lam * z
    for m in range(1, j):
        c0, c1 = c1, (2 * (m + lam) * z * c1 - (m + 2 * lam - 1) * c0) / (m + 1)
    return c1


def partial_wave_weights(k: int, d: int) -> List[Fraction]:
    """The weights w_j of the hidden-zero relation sum_j w_j c_j = 0 at mass level k in dimension d."""
    lam = Fraction(d - 3, 2)
    return [gegenbauer_at_minus_one(j, lam) for j in range(k + 1)]


def residue_at(cs: Sequence[Fraction], d: int, z: Fraction) -> Fraction:
    lam = Fraction(d - 3, 2)
    return sum((Fraction(c) * gegenbauer(j, lam, z) for j, c in enumerate(cs)), Fraction(0))


def solve_last_coefficient(cs: Sequence[Fraction], d: int) -> Fraction:
    """The c_k that puts the zero at z = -1, given c_0 .. c_{k-1}."""
    w = partial_wave_weights(len(cs), d)
    return -sum((wi * Fraction(c) for wi, c in zip(w, cs)), Fraction(0)) / w[-1]


def solve_last_alpha(alphas: Sequence[Fraction], k: int) -> Fraction:
    """alpha_{n,k} from sum_m (-k)^m alpha_{n,m} = 0, given alpha_{n,0} .. alpha_{n,k-1}."""
    m = len(alphas)
    return -sum((Fraction(-k) ** i * Fraction(a) for i, a in enumerate(alphas)), Fraction(0)) / Fraction(-k) ** m


def xi() -> Fraction:
    """The answer of problem 9b: Xi = 108 c_3 + 67 alpha_{n,3} at d = 7, k = 3."""
    c3 = solve_last_coefficient([7, -2, 5], 7)
    a3 = solve_last_alpha([5, -1, 2], 3)
    return 108 * c3 + 67 * a3


CONSTRUCTIONS = (
    {"id": "tpe.pi-series", "gives": "parametric-pi-series", "needs": ("euler-beta",),
     "note": "pi = 4 + sum (1/n!)(1/(n+l) - 4/(2n+1))((2n+1)^2/(4(n+l)) - n)_{n-1}; l -> oo is Madhava-Leibniz"},
    {"id": "tpe.hidden-zero", "gives": "hidden-zero-partial-wave-relation", "needs": ("gegenbauer-basis",),
     "note": "sum_j (-1)^j (2 lam)_j / j! c_j = 0 and sum_m (-k)^m alpha_{n,m} = 0"},
)


def check() -> List[str]:
    """The conditions that fail (none when the constructions are right)."""
    bad = []
    if abs(float(pi_partial(40, Fraction(21, 2))) - math.pi) > 1e-11:
        bad.append("pi series at l = 21/2 does not reach pi")
    if any(leibniz_limit_exact(n) != leibniz_term(n) for n in range(1, 30)):
        bad.append("l -> infinity limit is not Madhava-Leibniz")
    if partial_wave_weights(2, 4) != [1, -1, 1]:
        bad.append("d = 4 hidden-zero weights")
    if xi() != Fraction(11219, 27):
        bad.append("Xi")
    return bad
