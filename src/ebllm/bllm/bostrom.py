"""Bostrom's notions of superintelligence made exact: kinetics, speed, collectives and quality.

Bostrom writes the rate of an intelligence explosion as optimization power over recalcitrance
(Superintelligence, Oxford University Press 2014, Ch. 4) and distinguishes speed, collective and
quality superintelligence (Ch. 3).  The functions below are the closed forms of the paper's section
"Superintelligence in the sense of Bostrom, made exact":

    kinetics(h, ...)          Proposition kinetics: a sound explosion with power O_0 (1+h)^n
    sound_explosion(...)      Corollary soundexplosion: is a cost/power sequence soundly singular?
    speed_throughput(W, ...)  Proposition speed: candidates certified by checking work W
    speed_tax(m, k, ...)      Proposition speed (ii): extra checking work per candidate for k times more
    best_collective(pi, Qs)   Proposition collective: the best mixture of proposer profiles
    quality_threshold(pi)     equation (quality): problems after which learning beats copying the need

None of these says that a system is a superintelligence; they price the parts of one.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Sequence, Tuple

from .gap import _normalise, optimal_cost, search_cost


def geometric_entropy(h: float) -> float:
    """Entropy (nats) of the geometric profile p_n = (1 - rho) rho^n with rho = 1/(1+h)."""
    if h <= 0:
        raise ValueError("h must be positive")
    return math.log((1 + h) / h) + math.log1p(h) / h


@dataclass
class Kinetics:
    proposing_time: float      # sum_n g / O_n
    run_once_time: float       # B = sum_n a / O_n
    entropy: float             # H of the geometric profile
    lower: float               # least checking time, lower bound
    upper: float               # least checking time, upper bound
    soundness_factor: float    # T*/B, lower bound

    @property
    def total_lower(self) -> float:
        return self.proposing_time + self.lower


def kinetics(h: float, a: float = 1.0, g: float = 0.0, O0: float = 1.0, eps: float = 0.5,
             theta: float = 0.01) -> Kinetics:
    """Proposition kinetics: O_n = O0 (1+h)^n, fixed costs g (propose) and a (one check run)."""
    L = math.log(1 / eps)
    B = a * (1 + h) / (O0 * h)
    H = geometric_entropy(h)
    lo = B / L * (H + math.log(1 / theta))
    return Kinetics(g * (1 + h) / (O0 * h), B, H, lo, lo + B, lo / B)


def sound_explosion(g: Sequence[float], a: Sequence[float], O: Sequence[float], tol: float = 1e-3
                    ) -> Tuple[float, float, float]:
    """Partial sums of sum g/O, sum b, sum b log(1/b) with b = a/O (Corollary soundexplosion).

    The explosion is singular when the first two converge and sound when the third does; on a
    finite prefix the function returns the three partial sums for the caller to judge.
    """
    s1 = s2 = s3 = 0.0
    for gn, an, On in zip(g, a, O):
        b = an / On
        s1 += gn / On
        s2 += b
        s3 += b * math.log(1 / b) if 0 < b < 1 else 0.0
    return s1, s2, s3


def speed_throughput(W: float, a: float = 1.0, eps: float = 0.5, theta: float = 0.01) -> Tuple[int, int]:
    """Bounds on m*(W), the most equal-cost candidates checking work W certifies at budget theta.

    Returns (certified, impossible): every m <= certified fits in W and no m >= impossible does,
    from (m a/L) log(m/theta) <= V*_m <= (m a/L)(log(m/theta) + L).
    """
    L = math.log(1 / eps)
    y = W * L / a

    def largest(f):
        lo, hi = 0, 1
        while f(hi) <= y:
            hi *= 2
        while hi - lo > 1:
            mid = (lo + hi) // 2
            lo, hi = (mid, hi) if f(mid) <= y else (lo, mid)
        return lo

    certified = largest(lambda m: m * (math.log(m / theta) + L) if m > 0 else 0.0)
    impossible = largest(lambda m: m * math.log(m / theta) if m > 0 else 0.0) + 1
    return certified, impossible


def speed_tax(k: float, a: float = 1.0, eps: float = 0.5) -> float:
    """Proposition speed (ii): k times more candidates cost (a/L) log k more per candidate, up to a."""
    return a / math.log(1 / eps) * math.log(k)


def best_collective(pi: Sequence[float], profiles: Sequence[Sequence[float]], iters: int = 20000,
                    step: float = 0.05) -> Tuple[List[float], float]:
    """Proposition collective: frequencies w minimising C(pi, sum_i w_i q_i), by exponentiated gradient
    (the problem is convex in w)."""
    pi = _normalise(pi)
    Q = [_normalise(q) for q in profiles]
    m, K = len(Q), len(pi)
    w = [1.0 / m] * m
    for _ in range(iters):
        q = [sum(w[i] * Q[i][j] for i in range(m)) for j in range(K)]
        grad = [-sum(pi[j] / q[j] ** 2 * Q[i][j] for j in range(K) if pi[j] > 0) for i in range(m)]
        top = max(-gr for gr in grad)
        w = [wi * math.exp(-step * gr / top) for wi, gr in zip(w, grad)]
        s = sum(w)
        w = [x / s for x in w]
    q = [sum(w[i] * Q[i][j] for i in range(m)) for j in range(K)]
    return w, search_cost(pi, q)


def collective_cost(pi: Sequence[float], profiles: Sequence[Sequence[float]],
                    weights: Sequence[float]) -> float:
    Q = [_normalise(q) for q in profiles]
    w = _normalise(weights)
    q = [sum(wi * qi[j] for wi, qi in zip(w, Q)) for j in range(len(pi))]
    return search_cost(pi, q)


def learning_constant(pi: Sequence[float]) -> float:
    """beta(pi) of Proposition learnrate."""
    pi = _normalise(pi)
    S = sum(math.sqrt(x) for x in pi)
    return sum(x ** -0.5 for x in pi if x > 0) / S - len(pi) / S ** 2


def quality_threshold(pi: Sequence[float]) -> float:
    """Equation (quality): the number of closed problems after which the learning selector's expected
    cost e^{H_1/2}(1 + beta/(4n)) is below the cost K of copying the need."""
    pi = _normalise(pi)
    K = len(pi)
    ratio = K / optimal_cost(pi)
    if ratio <= 1:
        return math.inf
    return learning_constant(pi) / (4 * (ratio - 1))
