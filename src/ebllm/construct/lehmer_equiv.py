"""Lehmer's totient problem as a statement about one divisor, with its companion equation.

Lehmer asked in 1932 whether a composite n can satisfy phi(n) | n - 1.  Write a composite
solution as n = A q with q its largest prime factor, S the set of its other prime factors
(all odd, and n is squarefree), A = prod S, B = prod (p - 1) over S and M = (n - 1)/phi(n).
Then n - 1 = M phi(n) reads q D = M B - 1 with D = M B - A, and the problem is equivalent to
the following assertion (Bhattacharjee, Lehmer's totient problem with fewer than sixteen prime
factors, Proposition 9.1, https://github.com/creelie/eLhmr):

    for no finite set S of odd primes and no integer M >= 2 is D = M B - A positive, a divisor
    of A - 1, and (M B - 1)/D a prime larger than every element of S.

Two constraints on D follow from the same algebra and are what this module checks:

    (q - 1) D = A - 1      since q D = D + A - 1; so q - 1 divides A - 1 and D = (A - 1)/(q - 1),
                           and the assertion says that 1 + (A - 1)/(M B - A) is never a prime
                           above S;
    D odd, D = -A (mod 2^|S|)   since 2^|S| divides B while A is odd; so D >= 3, and the cases
                           D = 1 (which would make q = A) and D = 2 are both out.

The companion equation phi(n) | n + 1 has the same shape with the sign changed, q D = M B + 1,
and there D = 1 is allowed: it gives q = M B + 1, and with M = 2 and S the first Fermat primes
the chain 15, 255, 65535, 4294967295 of its known solutions (``companion_chain``).

What this settles: nothing new about the conjecture.  The reformulation turns every candidate
(S, M) into one primality question, and the two constraints cut the candidates by a factor of
2^|S| and remove D in {1, 2}; they are congruences, and congruences cannot force a number never
to be prime, which is the wall recorded in the modlog.  The refuter (``search``) enumerates
small sets S and small M and finds no Lehmer solution, as the published bounds require
(omega(n) >= 16), while the same search on the companion equation returns the Fermat chain, so
the equations are implemented and not merely declared.  Everything here uses the standard
library only.
"""
from __future__ import annotations

import itertools
from math import prod
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

FERMAT_PRIMES = (3, 5, 17, 257, 65537)


def is_prime(m: int) -> bool:
    if m < 2:
        return False
    if m % 2 == 0:
        return m == 2
    d = 3
    while d * d <= m:
        if m % d == 0:
            return False
        d += 2
    return True


def totient_squarefree(primes: Iterable[int]) -> int:
    return prod(p - 1 for p in primes)


def divisor_data(S: Sequence[int], M: int, sign: int = -1) -> Dict[str, int]:
    """A, B, D and the candidate q for n = A q with n + sign = M phi(n) (sign = -1 is Lehmer)."""
    if sign not in (-1, 1):
        raise ValueError("sign must be -1 (phi(n) | n - 1) or +1 (phi(n) | n + 1)")
    if len(set(S)) != len(S) or any(p % 2 == 0 or not is_prime(p) for p in S):
        raise ValueError("S must be a set of distinct odd primes")
    if M < 2:
        raise ValueError("M must be at least 2")
    A = prod(S)
    B = totient_squarefree(S)
    D = M * B - A
    num = M * B - 1 if sign == -1 else M * B + 1
    q = num // D if D > 0 and num % D == 0 else 0
    return {"A": A, "B": B, "D": D, "numerator": num, "q": q}


def check(S: Sequence[int], M: int, sign: int = -1) -> Dict[str, bool]:
    """The conditions of the assertion for (S, M), each checked on its own.

    ``solution`` is True exactly when n = A q is a composite solution of phi(n) | n + sign.
    For sign = -1 the two constraints ``d_odd`` and ``d_residue`` hold for every (S, M), and
    ``identity`` says (q - 1) D = A - 1 whenever D > 0 divides the numerator.
    """
    d = divisor_data(S, M, sign)
    A, B, D, q = d["A"], d["B"], d["D"], d["q"]
    k = len(S)
    divides = D > 0 and d["numerator"] % D == 0
    # q D = M B + sign = D + A + sign, so (q - 1) D = A + sign whenever q is defined
    out = {
        "d_positive": D > 0,
        "d_divides": divides,
        "q_prime_above_S": q > max(S) and is_prime(q),
        "d_odd": D % 2 == 1,
        "d_residue": D % (1 << k) == (-A) % (1 << k),
        "identity": (not divides) or (q - 1) * D == A + sign,
    }
    out["solution"] = out["d_positive"] and out["d_divides"] and out["q_prime_above_S"]
    if out["solution"]:
        n = A * q
        phi = B * (q - 1)
        assert (n + sign) % phi == 0 and (n + sign) // phi == M
    return out


def solution_from(S: Sequence[int], M: int, sign: int = -1) -> Optional[int]:
    """n = A q when (S, M) gives a solution of phi(n) | n + sign, else None."""
    r = check(S, M, sign)
    if not r["solution"]:
        return None
    d = divisor_data(S, M, sign)
    return d["A"] * d["q"]


def search(primes: Sequence[int], max_size: int, M_range: Iterable[int], sign: int = -1) -> List[Tuple[Tuple[int, ...], int, int]]:
    """Every (S, M, n) with S a subset of ``primes`` of size at most ``max_size`` that solves the equation."""
    found = []
    Ms = list(M_range)
    for k in range(1, max_size + 1):
        for S in itertools.combinations(primes, k):
            for M in Ms:
                n = solution_from(S, M, sign)
                if n is not None:
                    found.append((S, M, n))
    return found


def companion_chain(length: int = 4) -> List[int]:
    """The solutions 15, 255, 65535, 4294967295 of phi(n) | n + 1 from D = 1 on the Fermat primes."""
    out = []
    for k in range(1, length + 1):
        S = FERMAT_PRIMES[:k]
        n = solution_from(S, 2, sign=1)
        if n is None:
            raise AssertionError(f"the Fermat construction failed at {S}")
        out.append(n)
    return out


def constraints_hold(primes: Sequence[int], max_size: int, M_range: Iterable[int]) -> bool:
    """``d_odd``, ``d_residue`` and ``identity`` on every (S, M) of the search space (Lehmer sign)."""
    Ms = list(M_range)
    for k in range(1, max_size + 1):
        for S in itertools.combinations(primes, k):
            for M in Ms:
                r = check(S, M, -1)
                if not (r["d_odd"] and r["d_residue"] and r["identity"]):
                    return False
    return True
