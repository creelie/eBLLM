"""Screens: rejection rules for claimed proof steps, each taken from a recorded failure on an open problem.

A screen tests a claimed step on cases where the truth can be computed exactly and rejects the step at
the first case that contradicts it.  A step that passes a screen is not proved; a step that fails one
is false, and the case is its counterexample.  Every screen below comes with the failure it records.

Riemann hypothesis, Liouville correlations.  Write C_h(X) = sum over n <= X - h of lambda(n) lambda(n+h)
for the Liouville function lambda.  If lambda behaved like independent random signs, each C_h(X)
would have size about sqrt(X), so the mean of C_h(X)^2 over the shifts H < h <= 2H would be about
X.  The exact values agree with this model (``mean_square_correlation``).  A route claimed that
E_2(X, H) = sum over H < h <= 2H of C_h(X - h)^2 is at most X^(2+eps) / H; on average over the H
shifts that bounds C_h^2 by X^2 / H^2, below the true size X as soon as H > sqrt(X).  The rule:
a claimed bound on the correlations per shift that is below the random-model size sqrt(X) is
rejected (``below_random_model``).

Erdos-Straus conjecture, 4/n = 1/x + 1/y + 1/z.  For a prime p, a solution is of type I when p
divides exactly one of x, y, z and of type II when it divides exactly two (Elsholtz and Tao).  A
lemma claiming that every solution is of type II fails at 4/73 = 1/20 + 1/210 + 1/30660, and a
claim that a divisor k of (q + 1)/4 with q | p + 4k^2 always exists fails at p = 97, q = 7.  The
rules: a normal form is tested against every solution of small cases (``solutions``,
``solution_type``), and every claimed existence of a parameter is tested on small cases
(``first_failure``).
"""
from __future__ import annotations

from math import isqrt
from operator import mul
from typing import Callable, Iterable, List, Optional, Tuple


def first_failure(claim: Callable[[object], bool], cases: Iterable[object]) -> Optional[object]:
    """The first case on which the claim is false, or None if it holds on all of them."""
    for c in cases:
        if not claim(c):
            return c
    return None


# -- Liouville correlations --------------------------------------------------------------------------
def liouville(n: int) -> List[int]:
    """lambda(0..n) with lambda(0) = 0, by a smallest-prime-factor sieve: Omega(m) = Omega(m / p) + 1."""
    spf = list(range(n + 1))
    for p in range(2, isqrt(n) + 1):
        if spf[p] == p:
            for m in range(p * p, n + 1, p):
                if spf[m] == m:
                    spf[m] = p
    lam = [0] * (n + 1)
    if n >= 1:
        lam[1] = 1
    for m in range(2, n + 1):
        lam[m] = -lam[m // spf[m]]
    return lam


def correlation(lam: List[int], x: int, h: int) -> int:
    """C_h(x) = sum over 1 <= n <= x - h of lambda(n) lambda(n + h)."""
    return sum(map(mul, lam[1:x - h + 1], lam[1 + h:x + 1]))


def mean_square_correlation(x: int, h: int, lam: Optional[List[int]] = None) -> float:
    """The mean of C_k(x)^2 over the shifts h < k <= 2h."""
    lam = lam or liouville(x)
    return sum(correlation(lam, x, k) ** 2 for k in range(h + 1, 2 * h + 1)) / h


def below_random_model(bound_sq: Callable[[int, int], float], x: int, h: int, slack: float = 4.0,
                       lam: Optional[List[int]] = None) -> Tuple[bool, float]:
    """Reject a claimed bound on the mean of C_k(x)^2 over h < k <= 2h when it is below the exact mean
    divided by `slack`; returns (rejected, exact mean / claimed bound)."""
    exact = mean_square_correlation(x, h, lam)
    ratio = exact / bound_sq(x, h)
    return ratio > slack, ratio


# -- Erdos-Straus --------------------------------------------------------------------------------------
def solutions(n: int) -> List[Tuple[int, int, int]]:
    """Every x <= y <= z with 4/n = 1/x + 1/y + 1/z, in exact integers."""
    out = []
    for x in range(n // 4 + 1, 3 * n // 4 + 1):
        a, b = 4 * x - n, n * x            # 4/n - 1/x = a/b
        if a <= 0:
            continue
        for y in range(max(x, -(-b // a)), 2 * b // a + 1):
            c, d = a * y - b, b * y        # a/b - 1/y = c/d
            if c > 0 and d % c == 0 and d // c >= y:
                out.append((x, y, d // c))
    return out


def solution_type(p: int, s: Tuple[int, int, int]) -> int:
    """How many of the denominators the prime p divides (1 for type I, 2 for type II)."""
    return sum(1 for t in s if t % p == 0)


def divisor_in_progression(p: int, q: int) -> bool:
    """Whether some divisor k of (q + 1)/4 has q | p + 4k^2 (q = 3 mod 4)."""
    d = (q + 1) // 4
    return any(d % k == 0 and (p + 4 * k * k) % q == 0 for k in range(1, d + 1))
