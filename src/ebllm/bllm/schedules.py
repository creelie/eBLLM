"""Check schedules with a guaranteed bound on false acceptances.

Every schedule here gives the i-th candidate r_i independent runs of a check of soundness eps, so
an incorrect candidate is kept with probability at most eps**r_i.  A schedule is theta-sound when
sum_i eps**r_i <= theta.  The functions implement the closed forms of D. Bhattacharjee and
U. Bhattacharya, "Beyond the LLM: BLLM and the entropy law of sound recursive self-improvement":

    entropy_bounds        Theorem A: (A/L)(H + log 1/theta) <= V* <= that + A
    ceiling_schedule      the schedule attaining the upper bound of Theorem A
    huffman_schedule      Theorem C: exact optimum for eps = 1/D, theta = D**-k
    renyi_allocation      Theorem D: checks whose cost is a * delta**-s
    OnlineScheduler       Theorem G: runs fixed on arrival, sound for every future
    proportional_budgets  Theorem H: the split of the budget among subagents that loses nothing
    split_price           Theorem H(ii): the exact cost of any other split
    optimal_cascade       weak runs before one exact check
    amplified_runs        Theorem F: runs per generation in a branching takeoff
    singularity_regime    Theorem E and its corollaries: is a singular chain possible, and a sound one
"""
from __future__ import annotations

import heapq
import math
from dataclasses import dataclass, field
from typing import Dict, List, Sequence, Tuple


def entropy(p: Sequence[float]) -> float:
    """Shannon entropy in nats."""
    return -sum(x * math.log(x) for x in p if x > 0)


def _check(costs: Sequence[float], eps: float, theta: float) -> None:
    if not costs or any(a <= 0 for a in costs):
        raise ValueError("costs must be a nonempty sequence of positive numbers")
    if not 0 < eps < 1:
        raise ValueError("eps must lie in (0, 1)")
    if not 0 < theta <= 1:
        raise ValueError("theta must lie in (0, 1]")


def entropy_bounds(costs: Sequence[float], eps: float, theta: float) -> Tuple[float, float]:
    """The lower and upper bounds of Theorem A on the least cost of a theta-sound schedule."""
    _check(costs, eps, theta)
    A = float(sum(costs))
    L = math.log(1 / eps)
    lo = A / L * (entropy([a / A for a in costs]) + math.log(1 / theta))
    return lo, lo + A


def ceiling_schedule(costs: Sequence[float], eps: float, theta: float) -> List[int]:
    """r_i = ceil(log(A / (theta a_i)) / L): theta-sound, cost within A of the optimum."""
    _check(costs, eps, theta)
    A = float(sum(costs))
    L = math.log(1 / eps)
    return [max(0, math.ceil(math.log(A / (theta * a)) / L - 1e-12)) for a in costs]


def false_acceptance_bound(runs: Sequence[int], eps: float) -> float:
    return sum(eps ** r for r in runs)


def cost(costs: Sequence[float], runs: Sequence[int]) -> float:
    return sum(a * r for a, r in zip(costs, runs))


def huffman_schedule(costs: Sequence[float], D: int, k: int) -> List[int]:
    """Theorem C: for eps = 1/D and theta = D**-k the optimal schedule is r_i = l_i + k with
    (l_i) the lengths of a D-ary Huffman code for the cost profile."""
    if D < 2 or k < 0:
        raise ValueError("need D >= 2 and k >= 0")
    n = len(costs)
    if n == 1:
        return [k]
    pad = 0
    while (n + pad - 1) % (D - 1):
        pad += 1
    heap = [(float(a), i, [i]) for i, a in enumerate(costs)]
    heap += [(0.0, n + j, []) for j in range(pad)]
    heapq.heapify(heap)
    depth, counter = [0] * n, n + pad
    while len(heap) > 1:
        tot, members = 0.0, []
        for _ in range(D):
            x, _, m = heapq.heappop(heap)
            tot += x
            members += m
        for i in members:
            depth[i] += 1
        heapq.heappush(heap, (tot, counter, members))
        counter += 1
    return [d + k for d in depth]


def renyi_allocation(costs: Sequence[float], s: float, theta: float) -> Tuple[List[float], float]:
    """Theorem D: for checks costing a_i * delta_i**-s, the optimal false acceptance probabilities
    delta_i = theta a_i**(1/(1+s)) / S and the least cost theta**-s S**(1+s), S = sum a_i**(1/(1+s))."""
    if s <= 0:
        raise ValueError("s must be positive")
    S = sum(a ** (1 / (1 + s)) for a in costs)
    return [theta * a ** (1 / (1 + s)) / S for a in costs], theta ** (-s) * S ** (1 + s)


@dataclass
class OnlineScheduler:
    """Theorem G.  Candidates arrive one at a time; the n-th gets
        r_n = ceil((1/L) log(1 / (theta w_n))),  w_n = (a_n/S_n) / (2 (1 + log(S_n/a_1))**2),
    computed from a_1, ..., a_n only.  The weights sum to less than 1 whatever comes next, so the
    expected number of false acceptances over the whole life of the system is at most theta."""
    eps: float
    theta: float
    total: float = 0.0
    first: float = 0.0
    spent_budget: float = 0.0
    history: List[Tuple[float, int]] = field(default_factory=list)

    def runs(self, a: float) -> int:
        if a <= 0:
            raise ValueError("costs must be positive")
        if not self.history:
            self.first = a
        self.total += a
        u = math.log(self.total / self.first)
        w = (a / self.total) / (2 * (1 + u) ** 2)
        L = math.log(1 / self.eps)
        r = max(0, math.ceil(math.log(1 / (self.theta * w)) / L - 1e-12))
        self.spent_budget += self.eps ** r
        self.history.append((a, r))
        return r

    def guarantee(self) -> float:
        """The upper bound (6) of Theorem G on the cost so far."""
        A, L = self.total, math.log(1 / self.eps)
        p = [a / A for a, _ in self.history]
        return A / L * (entropy(p) + math.log(1 / self.theta) + math.log(2)
                        + 2 * math.log1p(math.log(A / self.first))) + A

    def cost(self) -> float:
        return sum(a * r for a, r in self.history)


def proportional_budgets(group_costs: Dict[str, float], theta: float) -> Dict[str, float]:
    """Theorem H(iii): give subagent k the budget theta * A_k / A.  Each subagent then computes,
    from its own costs and this one number, exactly the optimal schedule of the whole system."""
    A = sum(group_costs.values())
    return {k: theta * v / A for k, v in group_costs.items()}


def split_price(group_costs: Dict[str, float], budgets: Dict[str, float], eps: float, theta: float) -> float:
    """Theorem H(ii): (A/L)(D(P || q) + log(theta / Theta)), the excess of the subagents' lower
    bounds over the flat one for an arbitrary split of the budget."""
    A = sum(group_costs.values())
    Th = sum(budgets.values())
    if Th > theta * (1 + 1e-12):
        raise ValueError("the budgets exceed theta")
    L = math.log(1 / eps)
    D = sum((v / A) * math.log((v / A) / (budgets[k] / Th)) for k, v in group_costs.items())
    return A / L * (D + math.log(theta / Th))


@dataclass(frozen=True)
class Cascade:
    weak_runs: int
    expected_cost: float
    lower_bound: float
    strong_alone: float


def cascade_cost(r: int, b: float, c: float, rho: float, eps: float) -> float:
    """E(r) = b r + c (1 - rho) + c rho eps**r for a fraction rho of incorrect candidates."""
    return b * r + c * (1 - rho) + c * rho * eps ** r


def optimal_cascade(b: float, c: float, rho: float, eps: float) -> Cascade:
    """Weak checks of cost b and soundness eps before one exact check of cost c.  The cascade keeps
    exactly the correct candidates for every r; for b <= c rho L the best r is within one of
    ceil((1/L) log(c rho L / b)) and its cost lies between M and M + b,
    M = c (1 - rho) + (b/L)(1 + log(c rho L / b))."""
    L = math.log(1 / eps)
    if b >= c * rho * L:
        return Cascade(0, cascade_cost(0, b, c, rho, eps), c, c)
    r0 = math.ceil(math.log(c * rho * L / b) / L)
    best = min(range(max(0, r0 - 2), r0 + 3), key=lambda r: cascade_cost(r, b, c, rho, eps))
    M = c * (1 - rho) + b / L * (1 + math.log(c * rho * L / b))
    return Cascade(best, cascade_cost(best, b, c, rho, eps), M, c)


def amplified_runs(generation: int, m: float, eps: float) -> int:
    """Theorem F: r_k = ceil(k log(2m) / L) keeps the expected number of errors of a branching
    takeoff with mean offspring m finite; fewer than k log(m) / L runs cannot."""
    return math.ceil(generation * math.log(2 * m) / math.log(1 / eps))


@dataclass
class Regime:
    singular: bool   # sum a_n < infinity: a chain with every step checked reaches its asymptote
    sound: bool      # a singular chain can also keep only finitely many errors
    reason: str


def singularity_regime(p: float, beta: float = 0.0, s: float = 0.0) -> Regime:
    """Costs a_n = n**-p * (log n)**-beta and checks of order s (s = 0: exponential checks).

    A singular chain needs sum a_n < oo, that is p > 1, or p = 1 and beta > 1.  A sound one needs,
    with exponential checks, the entropy sum a_n log(1/a_n) < oo as well (Theorem E), and with checks
    of order s > 0 the sum of a_n**(1/(1+s)) < oo (Corollary on the phase diagram)."""
    def finite(q: float, b: float) -> bool:          # sum n**-q (log n)**-b
        return q > 1 or (q == 1 and b > 1)
    singular = finite(p, beta)
    if not singular:
        return Regime(False, False, "the costs do not sum: no singular chain at all")
    if s == 0:
        sound = p > 1 or beta > 2                       # a_n log(1/a_n) ~ (log n)**(1-beta)/n at p = 1
        why = "entropy finite" if sound else "costs sum but their entropy diverges: the soundness gap"
    else:
        sound = finite(p / (1 + s), beta / (1 + s))
        why = (f"sum a_n^(1/(1+s)) finite" if sound
               else f"needs p > 1 + s = {1 + s:g}: singular chains exist and every one is unsound")
    return Regime(True, sound, why)


def partial_entropy_sums(a, N: int):
    """Partial sums of a_n and of a_n log(1/a_n) for n <= N, for a callable cost law a(n)."""
    S = E = 0.0
    for n in range(1, N + 1):
        x = a(n)
        if x > 0:
            S += x
            E += x * math.log(1 / x)
    return S, E
