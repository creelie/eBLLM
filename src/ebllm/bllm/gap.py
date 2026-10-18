"""The gap law: how many proposals a proposer needs to reach the idea a problem calls for.

Ideas fall into K classes.  A problem needs an idea of class j with probability pi_j; a proposer
draws classes independently from a profile q until it draws the needed one.  The expected number
of draws is

    C(pi, q) = sum_j pi_j / q_j.

Theorem I of D. Bhattacharjee and U. Bhattacharya, "Bridging the gap between human and LLM
thinking through BLLM", gives the whole picture (proved in Lean, BLLM/Gap.lean):

    (i)   C(pi, q) >= (sum_j sqrt(pi_j))**2 = exp(H_1/2(pi)), with equality only at q = r,
          r_j = sqrt(pi_j) / sum_k sqrt(pi_k)        (square-root sampling)
    (ii)  C(pi, q) = exp(H_1/2(pi)) * (1 + chi2(r || q))   (the gap is a chi-squared divergence)
    (iii) every mixture q' = (1 - lam) q + lam r costs at most exp(H_1/2(pi)) / lam, whatever q is.

A proposer that copies the needs, q = pi, pays exactly K.  The functions below compute these
quantities, and `idea_gap_table` applies them to the measured distributions of human and LLM
research ideas in Z. Chen, Y. Zhao and A. Cohan, arXiv:2607.01233 (2026), bundled as
data/idea_gap.json.
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence

DATA = os.path.join(os.path.dirname(__file__), "data", "idea_gap.json")


def _normalise(v: Sequence[float]) -> List[float]:
    s = float(sum(v))
    if s <= 0 or any(x < 0 for x in v):
        raise ValueError("a profile needs nonnegative entries with a positive sum")
    return [x / s for x in v]


def search_cost(pi: Sequence[float], q: Sequence[float]) -> float:
    """Expected number of draws from q until the class needed (drawn from pi) appears."""
    pi, q = _normalise(pi), _normalise(q)
    tot = 0.0
    for a, b in zip(pi, q):
        if a > 0:
            if b <= 0:
                return math.inf
            tot += a / b
    return tot


def optimal_profile(pi: Sequence[float]) -> List[float]:
    """Square-root sampling r_j proportional to sqrt(pi_j): the unique minimiser of search_cost."""
    return _normalise([math.sqrt(x) for x in _normalise(pi)])


def optimal_cost(pi: Sequence[float]) -> float:
    """(sum_j sqrt(pi_j))**2, the least expected number of draws (Theorem I(i))."""
    return sum(math.sqrt(x) for x in _normalise(pi)) ** 2


def renyi_half(pi: Sequence[float]) -> float:
    """The Renyi entropy of order 1/2 in nats; exp of it is optimal_cost."""
    return math.log(optimal_cost(pi))


def chi2(r: Sequence[float], q: Sequence[float]) -> float:
    """chi2(r || q) = sum (r_j - q_j)**2 / q_j."""
    r, q = _normalise(r), _normalise(q)
    tot = 0.0
    for a, b in zip(r, q):
        if b <= 0:
            if a > 0:
                return math.inf
            continue
        tot += (a - b) ** 2 / b
    return tot


def mix(q: Sequence[float], r: Sequence[float], lam: float) -> List[float]:
    if not 0 <= lam <= 1:
        raise ValueError("lam must lie in [0, 1]")
    q, r = _normalise(q), _normalise(r)
    return [(1 - lam) * a + lam * b for a, b in zip(q, r)]


def mix_bound(pi: Sequence[float], lam: float) -> float:
    """Theorem I(iii): the cost of any mixture with weight lam on square-root sampling is at most this."""
    if not 0 < lam <= 1:
        raise ValueError("lam must lie in (0, 1]")
    return optimal_cost(pi) / lam


def steering_weight(pi: Sequence[float], q: Sequence[float], slack: float = 0.1, tol: float = 1e-9) -> float:
    """The least weight lam on square-root sampling for which the mixture costs at most
    (1 + slack) times the optimum.  The cost of the mixture decreases in lam on [0, 1] (it is
    convex with its minimum at lam = 1), so bisection finds it; Theorem I(iii) bounds it by
    1 / (1 + slack) for every q."""
    r = optimal_profile(pi)
    target = (1 + slack) * optimal_cost(pi)
    if search_cost(pi, q) <= target:
        return 0.0
    a, b = 0.0, 1.0
    while b - a > tol:
        m = (a + b) / 2
        if search_cost(pi, mix(q, r, m)) <= target:
            b = m
        else:
            a = m
    return b


def learning_curve(pi: Sequence[float], n: int, alpha: float = 0.5, trials: int = 2000,
                   seed: int = 1) -> float:
    """The mean ratio cost / optimum when square-root sampling uses needs estimated from n solved
    problems (counts with a Jeffreys prior alpha): how fast a selector that learns from the checks
    closes the gap."""
    import random
    rng = random.Random(seed)
    pi = _normalise(pi)
    opt = optimal_cost(pi)
    tot = 0.0
    for _ in range(trials):
        counts = [0] * len(pi)
        for _ in range(n):
            u, acc = rng.random(), 0.0
            for j, x in enumerate(pi):
                acc += x
                if u <= acc:
                    counts[j] += 1
                    break
            else:
                counts[-1] += 1
        tot += search_cost(pi, optimal_profile(estimate_needs(counts, alpha))) / opt
    return tot / trials


def estimate_needs(counts: Sequence[float], alpha: float = 0.5) -> List[float]:
    """The needs pi estimated from how many solved problems each class closed, with a Jeffreys
    prior alpha: what the spiking selector of `neuro` learns online."""
    return _normalise([c + alpha for c in counts])


@dataclass
class GapRow:
    source: str
    cost: float
    ratio: float          # cost / optimal cost
    chi2: float           # chi2(r || q): ratio - 1
    tvd: float            # total variation distance from the human profile
    half_cost: float      # cost of the 50/50 mixture with square-root sampling
    steer: float          # least weight on square-root sampling bringing the cost within 10%


def load_idea_gap(path: Optional[str] = None) -> dict:
    with open(path or DATA, encoding="utf-8") as fh:
        return json.load(fh)


def idea_gap_table(axis: str = "opportunity", data: Optional[dict] = None,
                   needs: str = "Human") -> List[GapRow]:
    """For every source of the data (the human papers and nine LLMs), the cost of finding the idea
    a human-written paper needed, when ideas are drawn from that source's profile.  The needs are
    the human profile: what a problem called for is what its authors used."""
    data = data or load_idea_gap()
    if axis not in data["axes"]:
        raise ValueError(f"axis is one of {sorted(data['axes'])}")
    pi = _normalise(data["shares"][needs][axis])
    r = optimal_profile(pi)
    opt = optimal_cost(pi)
    rows = []
    for src, sh in data["shares"].items():
        q = _normalise(sh[axis])
        c = search_cost(pi, q)
        rows.append(GapRow(src, c, c / opt, chi2(r, q), 0.5 * sum(abs(a - b) for a, b in zip(pi, q)),
                           search_cost(pi, mix(q, r, 0.5)), steering_weight(pi, q)))
    rows.append(GapRow("square-root sampling", opt, 1.0, 0.0,
                       0.5 * sum(abs(a - b) for a, b in zip(pi, r)), opt, 0.0))
    return rows


def format_table(rows: Sequence[GapRow], axis: str = "opportunity") -> str:
    out = [f"axis: {axis}   needs: the human profile   optimum (sum sqrt pi)^2 = {rows[-1].cost:.3f}",
           f"{'source':22s} {'cost':>7s} {'x opt':>6s} {'TVD':>6s} {'50/50':>7s} {'steer 10%':>9s}"]
    for g in rows:
        out.append(f"{g.source:22s} {g.cost:7.2f} {g.ratio:6.2f} {g.tvd:6.3f} {g.half_cost:7.2f} "
                   f"{g.steer:9.2f}")
    return "\n".join(out)


def bridge_simulation(pi: Sequence[float], q: Sequence[float], problems: int = 3000, lam: float = 0.5,
                      window: int = 500, seed: int = 5, selector=None) -> Dict[str, List[float]]:
    """A stream of problems, each needing an idea of class j drawn from pi.  Three proposers draw
    classes until the needed one appears: the LLM alone (profile q); BLLM, which draws from q with
    probability 1 - lam and otherwise lets a spiking selector (module `neuro`) choose the class and
    rewards the selector when the class closes the problem; and square-root sampling with the true
    needs, the optimum.  Returns the mean number of draws per problem in consecutive windows."""
    import random
    from .neuro import SpikingSelector
    rng = random.Random(seed)
    pi, q = _normalise(pi), _normalise(q)
    K = len(pi)
    sel = selector or SpikingSelector([str(j) for j in range(K)])
    r = optimal_profile(pi)

    def draw(p):
        u, acc = rng.random(), 0.0
        for j, x in enumerate(p):
            acc += x
            if u <= acc:
                return j
        return K - 1

    out = {"llm": [], "bllm": [], "optimum": []}
    acc = {k: 0 for k in out}
    for t in range(1, problems + 1):
        need = draw(pi)
        n = 1
        while draw(q) != need:
            n += 1
        acc["llm"] += n
        n = 1
        while True:
            k = draw(q) if rng.random() >= lam else sel.race(rng)
            if k == need:
                break
            n += 1
        sel.reward(need)                       # the checks keep the result: reward its class
        acc["bllm"] += n
        n = 1
        while draw(r) != need:
            n += 1
        acc["optimum"] += n
        if t % window == 0:
            for k in out:
                out[k].append(acc[k] / window)
                acc[k] = 0
    return out
