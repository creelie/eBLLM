"""The coordinator: subagents propose, cascades check, memory keeps, the budget is split by law.

Two modes.

exact       every candidate meets r weak runs and then an exact check (expansion, evaluation at
            d + 1 points, the Lean kernel).  Only correct candidates are kept, whatever r is;
            r is tuned for each agent by the optimal-cascade rule so that the exact check is
            paid, up to a logarithmic premium, only on the correct proposals.

certified   candidates are accepted on weak evidence alone, with a guaranteed bound theta on the
            expected number of false acceptances over the whole run.  Round n receives the budget
            theta * w_n of the online law (Theorem G), so the bound holds however many rounds
            follow; inside a round the budget is split among the agents in proportion to their
            checking cost (Theorem H) and each agent uses the ceiling schedule (Theorem A).
            Every acceptance is then audited with the exact check, and the report states the
            observed number of false acceptances next to the bound.

In exact mode the agents take turns; with `selector="spiking"` the order of the turns in every
round is drawn by a SpikingSelector (module `neuro`), a circuit of leaky integrate-and-fire neurons
that is rewarded each time the checks keep a problem's first result, and so learns to call first
the agents that close problems, in proportion to the square root of how often they did (the
optimum of the gap law, Theorem I).  The selector only orders the turns; it never decides a result.

Candidates of kind "claim" (natural-language steps) have no check: they are recorded as
proposals, never as results.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from .agents import Agent, Problem, default_agents
from .checks import (Candidate, Check, ExactIdentityCheck, InterpolationCheck, LeanCheck,
                     RandomIdentityCheck, SmallPrimeCheck)
from .schedules import (cascade_cost, ceiling_schedule, entropy_bounds, optimal_cascade,
                        proportional_budgets)
from .vault import Vault


@dataclass
class AgentStats:
    proposed: int = 0
    weak_rejected: int = 0
    strong_rejected: int = 0
    kept: int = 0
    unchecked: int = 0
    cost: float = 0.0
    strong_only_cost: float = 0.0
    weak_runs: int = 0
    false_accepts: int = 0
    budget: float = 0.0
    bound: float = 0.0


@dataclass
class RunResult:
    mode: str
    stats: Dict[str, AgentStats]
    solved: Dict[str, str]
    rounds: int
    theta: float
    vault: Vault
    schedule_lower: float = 0.0
    schedule_upper: float = 0.0
    schedule_cost: float = 0.0
    false_bound: float = 0.0
    cascades: Dict[str, int] = field(default_factory=dict)
    turns: List[str] = field(default_factory=list)

    @property
    def total_cost(self) -> float:
        return sum(s.cost for s in self.stats.values())

    @property
    def strong_only_cost(self) -> float:
        return sum(s.strong_only_cost for s in self.stats.values())


class Coordinator:
    def __init__(self, agents: Optional[Sequence[Agent]] = None, weak: Optional[Check] = None,
                 theta: float = 1e-3, lean: Optional[LeanCheck] = None, seed: int = 20261018,
                 selector=None):
        self.agents = list(agents) if agents is not None else default_agents()
        if selector == "spiking":
            from .neuro import SpikingSelector
            selector = SpikingSelector([a.name for a in self.agents])
        self.selector = selector
        self.weak = weak or SmallPrimeCheck()
        self.strong = {"identity": ExactIdentityCheck(), "univariate": InterpolationCheck()}
        if lean is not None:
            self.strong["lean"] = lean
        self.theta = theta
        self.rng = random.Random(seed)

    # -- helpers -----------------------------------------------------------------------------
    def _weak_applies(self, c: Candidate) -> bool:
        return self.weak.applies(c)

    def _strong(self, c: Candidate) -> Optional[Check]:
        return self.strong.get(c.kind)

    def run(self, problems: Sequence[Problem], mode: str = "exact", rounds: int = 3,
            vault: Optional[Vault] = None, per_agent_cap: int = 5000) -> RunResult:
        if mode not in ("exact", "certified"):
            raise ValueError("mode is 'exact' or 'certified'")
        vault = vault or Vault()
        for p in problems:
            vault.add_problem(p.id, p.title, (p.lean or p.target) + "   [" + p.shape + "]", p.notes)
        stats = {a.name: AgentStats() for a in self.agents}
        solved: Dict[str, str] = {}
        res = RunResult(mode, stats, solved, 0, self.theta, vault)
        total_round_cost, first_round_cost, used = 0.0, None, 0.0
        sched_costs, sched_runs = [], []
        for rnd in range(rounds):
            res.rounds = rnd + 1
            if mode == "exact":
                # agents take turns, so a result kept by one is in memory for the next
                proposed_any = False
                order = (self.selector.order(self.rng) if self.selector is not None
                         else range(len(self.agents)))
                for k in order:
                    a = self.agents[k]
                    before = len(solved)
                    batch = {a.name: self._proposals(a, problems, solved, vault)[:per_agent_cap]}
                    proposed_any |= bool(batch[a.name])
                    self._exact_round(batch, stats, solved, vault, res)
                    res.turns.append(a.name)
                    if self.selector is not None and len(solved) > before:
                        self.selector.reward(k, len(solved) - before)
                if not proposed_any:
                    break
            else:
                batch: Dict[str, List[Candidate]] = {
                    a.name: self._proposals(a, problems, solved, vault)[:per_agent_cap] for a in self.agents}
                if not any(batch.values()):
                    break
                # online budget for this round (Theorem G), split by cost among agents (Theorem H)
                rc = {k: sum(self.weak.cost_of(c) for c in v if self._weak_applies(c)) for k, v in batch.items()}
                rc = {k: v for k, v in rc.items() if v > 0}
                if not rc:
                    break
                a_n = sum(rc.values())
                total_round_cost += a_n
                first_round_cost = first_round_cost or a_n
                u = math.log(total_round_cost / first_round_cost)
                w = (a_n / total_round_cost) / (2 * (1 + u) ** 2)
                theta_n = self.theta * w
                shares = proportional_budgets(rc, theta_n)
                for name, cands in batch.items():
                    if name not in shares:
                        continue
                    stats[name].budget += shares[name]
                    cs = [c for c in cands if self._weak_applies(c)]
                    costs = [self.weak.cost_of(c) for c in cs]
                    runs = ceiling_schedule(costs, self.weak.soundness, min(1.0, shares[name]))
                    sched_costs += costs
                    sched_runs += runs
                    b = sum(self.weak.soundness ** r for r in runs)
                    stats[name].bound += b
                    used += b
                    self._certified(cs, runs, stats[name], solved, vault)
            if all(p.id in solved for p in problems):
                break
        if mode == "certified" and sched_costs:
            res.schedule_lower, res.schedule_upper = entropy_bounds(sched_costs, self.weak.soundness, self.theta)
            res.schedule_cost = sum(a * r for a, r in zip(sched_costs, sched_runs))
            res.false_bound = used
        return res

    def _proposals(self, a: Agent, problems, solved, vault) -> List[Candidate]:
        out: List[Candidate] = []
        for p in problems:
            if p.id in solved or p.kind not in getattr(a, "kinds", ("identity",)):
                continue
            got = a.propose(p, vault, self.rng, vault.all_residues())
            out += got
            if got and a.focus:
                break
        return out

    def _exact_round(self, batch, stats, solved, vault, res):
        for a in self.agents:
            cands = batch.get(a.name, [])
            st = stats[a.name]
            if not cands:
                continue
            idc = [c for c in cands if self._weak_applies(c) and self._strong(c)]
            if idc:
                b = sum(self.weak.cost_of(c) for c in idc) / len(idc)
                cst = sum(self._strong(c).cost_of(c) for c in idc) / len(idc)
                r = optimal_cascade(b, cst, a.expected_wrong, self.weak.soundness).weak_runs
            else:
                r = 0
            res.cascades[a.name] = r
            for c in cands:
                if c.kind == "lean" and c.statement.get("problem") in solved:
                    continue                    # a kernel check is expensive: stop at the first proof
                st.proposed += 1
                strong = self._strong(c)
                if strong is None:
                    st.unchecked += 1
                    vault.propose_unchecked(c, "no exact check exists for this kind of step")
                    continue
                st.strong_only_cost += strong.cost_of(c)
                rejected = False
                if self._weak_applies(c):
                    for j in range(r):
                        v = self.weak.run(c, self.rng)
                        st.cost += v.cost
                        st.weak_runs += 1
                        if not v.passed:
                            st.weak_rejected += 1
                            vault.record_failure(c, f"{self.weak.name}: {v.detail}")
                            rejected = True
                            break
                if rejected:
                    continue
                v = strong.run(c, self.rng)
                st.cost += v.cost
                if v.passed:
                    st.kept += 1
                    vault.keep(c, f"{strong.name}: {v.detail}", v.cost)
                    pid = c.statement.get("problem")
                    solved.setdefault(pid, c.id)
                else:
                    st.strong_rejected += 1
                    vault.record_failure(c, f"{strong.name}: {v.detail}")

    def _certified(self, cands, runs, st, solved, vault):
        for c, r in zip(cands, runs):
            st.proposed += 1
            ok = True
            for _ in range(r):
                v = self.weak.run(c, self.rng)
                st.cost += v.cost
                st.weak_runs += 1
                if not v.passed:
                    ok = False
                    break
            strong = self._strong(c)
            if strong is not None:
                st.strong_only_cost += strong.cost_of(c)
            if not ok:
                st.weak_rejected += 1
                vault.record_failure(c, f"{self.weak.name}: rejected")
                continue
            audit = strong.run(c, self.rng) if strong is not None else None
            if audit is not None and not audit.passed:
                st.false_accepts += 1
                vault.record_failure(c, "accepted on weak evidence; the audit found it false")
                continue
            st.kept += 1
            vault.keep(c, f"{r} weak runs (audit: {audit.detail if audit else 'none'})", 0.0)
            solved.setdefault(c.statement.get("problem"), c.id)
