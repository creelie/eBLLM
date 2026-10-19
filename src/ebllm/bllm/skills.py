"""Skill memory: a change is judged by the whole run it belongs to, not only by the attempt after it.

The playbook of ``selfmod`` scores a change by the outcome of the very next attempt.  That misses
changes that are needed but not sufficient: on Steinberg's gadget the new mode and the planar frames
were both followed by failed attempts, and both were needed for the attempt that closed.  The skill
memory keeps the log as a hypergraph, after HyperSkill (Xu, Yang and Huang, arXiv:2608.16114):

    a hyperedge per trajectory, meaning the records of one target in one run, binding
        steps     the diagnoses met along the way,
        changes   the changes made, each with the diagnosis it answered,
        outcome   the best outcome reached (closed, then partial, then failed or stopped),
        lesson    the evidence of the last record;
    the changes of a trajectory that closed or advanced are strategies, the changes of a trajectory
    that ran to its end and only failed are patterns to avoid; a trajectory whose last change has
    not been tried yet is open and counts for neither, and so does one that stopped, since a stop
    says that no checkable step exists, which is a verdict on the target and not on the changes.

For a diagnosis d on a target of area a (the run it belongs to) the memory retrieves along two
paths, the trajectories that met d and the trajectories of area a, and ranks the rule kinds by
    first   whether the pair (d, kind) is pruned,
    then    kappa(d, kind) = strategies minus patterns among the retrieved trajectories that met d
            and changed a rule of that kind in answer to d (HyperSkill's co-occurrence count),
    then    the number of strategies of that kind among the trajectories of area a,
    then    the playbook score, and the name.
A pair is pruned once it has been used in at least ``min_uses`` finished trajectories and fewer than
the fraction ``prune_below`` of them closed or advanced (HyperSkill's rule with N_min = 3 and
tau = 0.2); a pruned kind moves to the end of the ranking, and an exact change (rule and value) that
is pruned in the same way is refused by the loop.  HyperSkill also merges skills that are close in
an embedding space; changes here are exact (rule, value) pairs, so equal ones are already one node
and nothing is merged.

The memory is a function of the log and is rebuilt from it, so it has no store of its own.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Set, Tuple

from .selfmod import KINDS, RULE_KINDS, Change, Playbook, Record

GOOD = ("closed", "partial")
ORDER = {"closed": 3, "partial": 2, "failed": 1, "stopped": 1}


@dataclass
class Edge:
    run: str
    target: str
    steps: Tuple[str, ...]
    changes: Tuple[Tuple[str, Change], ...]   # (diagnosis answered, change)
    outcome: str
    status: str                               # strategy, pattern, stopped or open
    lesson: str = ""

    def pairs(self) -> Set[Tuple[str, str]]:
        return {(d, c.kind) for d, c in self.changes}

    def kinds(self) -> Set[str]:
        return {c.kind for _, c in self.changes}


def trajectory(run: str, records: List[Record]) -> Edge:
    """The hyperedge of the records of one target, in the order of their attempts."""
    outcomes = [r.outcome for r in records] + [r.retry for r in records if r.retry]
    best = max(outcomes, key=lambda o: ORDER.get(o, 0))
    last = records[-1]
    if best in GOOD:
        status = "strategy"
    elif last.change is not None and not last.retry:
        status = "open"
    elif best == "stopped":
        status = "stopped"
    else:
        status = "pattern"
    return Edge(run, records[0].target, tuple(r.diagnosis for r in records if r.diagnosis),
                tuple((r.diagnosis, r.change) for r in records if r.change is not None),
                best, status, last.evidence)


@dataclass
class SkillMemory:
    min_uses: int = 3
    prune_below: float = 0.2
    edges: List[Edge] = field(default_factory=list)

    def add(self, run: str, records: Iterable[Record]) -> "SkillMemory":
        by_target: Dict[str, List[Record]] = {}
        for r in records:
            by_target.setdefault(r.target, []).append(r)
        for recs in by_target.values():
            self.edges.append(trajectory(run, sorted(recs, key=lambda r: r.attempt)))
        return self

    @staticmethod
    def from_log(runs: Dict[str, List[Record]], **kw) -> "SkillMemory":
        m = SkillMemory(**kw)
        for run, recs in runs.items():
            m.add(run, recs)
        return m

    def uses(self, diagnosis: str, kind: str) -> Tuple[int, int]:
        """(finished trajectories that changed a rule of this kind in answer to this diagnosis, of them good)."""
        n = w = 0
        for e in self.edges:
            if e.status in ("strategy", "pattern") and (diagnosis, kind) in e.pairs():
                n += 1
                w += e.status == "strategy"
        return n, w

    def utility(self, diagnosis: str, kind: str) -> Optional[float]:
        n, w = self.uses(diagnosis, kind)
        return w / n if n else None

    def pruned(self, diagnosis: str, kind: str) -> bool:
        n, w = self.uses(diagnosis, kind)
        return n >= self.min_uses and w < self.prune_below * n

    def refused(self, change: Change) -> bool:
        """An exact change (rule and value) used in at least min_uses finished trajectories, nearly all bad."""
        n = w = 0
        for e in self.edges:
            if e.status in ("strategy", "pattern") and any(c.key() == change.key() for _, c in e.changes):
                n += 1
                w += e.status == "strategy"
        return n >= self.min_uses and w < self.prune_below * n

    def retrieve(self, diagnosis: str, area: str = "") -> Tuple[List[Edge], List[Edge]]:
        """The two paths: trajectories that met the diagnosis, and trajectories of the same area."""
        return ([e for e in self.edges if diagnosis in e.steps],
                [e for e in self.edges if area and e.run == area])

    def kappa(self, diagnosis: str, kind: str, met: List[Edge]) -> int:
        k = 0
        for e in met:
            if (diagnosis, kind) in e.pairs():
                k += {"strategy": 1, "pattern": -1}.get(e.status, 0)
        return k

    def rank(self, diagnosis: str, area: str = "", playbook: Optional[Playbook] = None) -> List[str]:
        if diagnosis not in KINDS:
            raise ValueError(f"unknown failure kind {diagnosis!r}")
        playbook = playbook or Playbook()
        met, same = self.retrieve(diagnosis, area)
        near = {k: sum(e.status == "strategy" and k in e.kinds() for e in same) for k in RULE_KINDS}
        return sorted(RULE_KINDS, key=lambda k: (self.pruned(diagnosis, k), -self.kappa(diagnosis, k, met),
                                                 -near[k], -playbook.score(diagnosis, k), k))

    def report(self) -> dict:
        status: Dict[str, int] = {}
        for e in self.edges:
            status[e.status] = status.get(e.status, 0) + 1
        pairs = sorted({p for e in self.edges for p in e.pairs()})
        table = []
        for d, k in pairs:
            n, w = self.uses(d, k)
            table.append(dict(diagnosis=d, kind=k, finished=n, good=w, pruned=self.pruned(d, k)))
        return dict(trajectories=len(self.edges), status=status, pairs=table,
                    edges=[dict(run=e.run, target=e.target, outcome=e.outcome, status=e.status,
                                steps=list(e.steps), changes=[(d, c.kind, c.rule) for d, c in e.changes])
                           for e in self.edges])


def needed_not_sufficient(runs: Dict[str, List[Record]]) -> List[Tuple[str, Record]]:
    """The changes the playbook counts as failures (their retry neither closed nor advanced) that belong to a
    trajectory which closed or advanced: the credit the skill memory gives and the playbook does not."""
    out = []
    for run, recs in runs.items():
        by_target: Dict[str, List[Record]] = {}
        for r in recs:
            by_target.setdefault(r.target, []).append(r)
        for rs in by_target.values():
            if trajectory(run, sorted(rs, key=lambda r: r.attempt)).status != "strategy":
                continue
            out += [(run, r) for r in rs if r.change is not None and r.retry and r.retry not in GOOD]
    return out
