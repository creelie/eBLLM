"""Free quotients of the one-parameter Calabi-Yau complete intersections, by one integer invariant.

Let X be a simply connected Calabi-Yau threefold with Pic X = Z and L ample. An automorphism g of prime
order p with no fixed points lifts to every power of the ample generator (H^2(Z/p, C*) = 0), Kodaira
vanishing kills the higher cohomology, and the holomorphic Lefschetz formula of Atiyah and Bott says
that the trace of every nontrivial power of g on H^0(X, kL) is zero. So H^0(X, kL) is a multiple of
the regular representation and p divides

    chi(X, kL) = k^3 L^3 / 6 + k c2.L / 12        for every k >= 1.

The greatest common divisor of these values is g_X = gcd(chi(L), chi(2L), chi(3L)) (write the
polynomial in the binomial basis), so every prime dividing the order of a group acting freely on X
divides g_X. For a free quotient by H the net number of families is |chi(X)| / (2|H|), so three families
need |H| = |chi(X)|/6, which is ruled out when that is not an integer or has a prime factor outside g_X.

``ONE_PARAMETER`` lists the thirteen hypergeometric one-parameter complete intersections that are
quasi-smooth and miss the singular points of the weighted projective space (Doran-Morgan; the
fourteenth, X_{2,12} in P(1,1,1,1,4,6), is not quasi-smooth). Used in the strings paper, Proposition
on free quotients; the archive check is code/checks/free_quotients.py of creelie/strings.
"""
from fractions import Fraction
from math import gcd, prod

ONE_PARAMETER = {
    "X5": ((5,), (1, 1, 1, 1, 1)),
    "X6": ((6,), (1, 1, 1, 1, 2)),
    "X8": ((8,), (1, 1, 1, 1, 4)),
    "X10": ((10,), (1, 1, 1, 2, 5)),
    "X3,3": ((3, 3), (1,) * 6),
    "X4,2": ((4, 2), (1,) * 6),
    "X3,2,2": ((3, 2, 2), (1,) * 7),
    "X2,2,2,2": ((2, 2, 2, 2), (1,) * 8),
    "X4,4": ((4, 4), (1, 1, 1, 1, 2, 2)),
    "X6,6": ((6, 6), (1, 1, 2, 2, 3, 3)),
    "X4,3": ((4, 3), (1, 1, 1, 1, 1, 2)),
    "X6,4": ((6, 4), (1, 1, 1, 2, 2, 3)),
    "X6,2": ((6, 2), (1, 1, 1, 1, 1, 3)),
}


def chern_numbers(degrees, weights):
    """(L^3, c2.L, chi) of a Calabi-Yau complete intersection in P(weights), L = O(1)."""
    if sum(degrees) != sum(weights) or len(weights) - len(degrees) != 4:
        raise ValueError("needs a Calabi-Yau threefold complete intersection")
    c = [Fraction(1), Fraction(0), Fraction(0), Fraction(0)]
    for w in weights:
        c = [c[i] + (w * c[i - 1] if i else 0) for i in range(4)]
    for d in degrees:
        c = [sum(c[i] * (-d) ** (k - i) for i in range(k + 1)) for k in range(4)]
    deg = Fraction(prod(degrees), prod(weights))
    assert c[1] == 0
    return deg, c[2] * deg, c[3] * deg


def euler_values(L3, c2L, ks=(1, 2, 3)):
    """chi(X, kL) by Riemann-Roch on a Calabi-Yau threefold."""
    return tuple(Fraction(k ** 3 * L3, 6) + Fraction(k * c2L, 12) for k in ks)


def g_invariant(degrees, weights):
    """g_X = gcd of chi(X, kL) over k >= 1."""
    L3, c2L, _ = chern_numbers(degrees, weights)
    vals = euler_values(L3, c2L)
    if any(v.denominator != 1 for v in vals):
        raise ValueError("chi(kL) is not an integer: not a smooth Calabi-Yau")
    return gcd(gcd(int(vals[0]), int(vals[1])), int(vals[2]))


def _primes(n):
    out, p = set(), 2
    while p * p <= n:
        while n % p == 0:
            out.add(p)
            n //= p
        p += 1
    if n > 1:
        out.add(n)
    return out


def free_order_allowed(degrees, weights, order):
    """False when no group of this order can act freely (a prime of the order does not divide g_X)."""
    return _primes(order) <= _primes(g_invariant(degrees, weights))


def three_families_possible(degrees, weights):
    """Whether a free quotient could carry three net families: needs |H| = |chi|/6 allowed."""
    _, _, chi = chern_numbers(degrees, weights)
    six = Fraction(abs(chi), 6)
    return six.denominator == 1 and free_order_allowed(degrees, weights, int(six))
