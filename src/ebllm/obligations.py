"""The obligation hypergraph of Definition 6.1 and the six-gate vector of Section 11."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

STATUSES = ("PASS", "FAIL", "UNK", "SCOPE", "COND")


@dataclass
class Obligation:
    name: str
    kind: str = "lemma"          # lemma, estimate, construction, example, formalization, ...
    weight: float = 1.0          # burden weight w(v) >= 0
    status: str = "UNK"          # one of STATUSES
    verifier: str = ""           # what discharged it: a Lean theorem name, a program, a referee

    def __post_init__(self):
        if self.status not in STATUSES:
            raise ValueError(f"unknown status {self.status}")
        if self.weight < 0:
            raise ValueError("weights are nonnegative")


@dataclass
class Bridge:
    """A hyperedge (v1, ..., vk => v0) with its scope loss."""
    premises: Tuple[str, ...]
    conclusion: str
    scope_loss: float = 0.0


@dataclass
class ObligationGraph:
    nodes: Dict[str, Obligation] = field(default_factory=dict)
    bridges: List[Bridge] = field(default_factory=list)

    def add(self, name: str, **kw) -> Obligation:
        ob = Obligation(name, **kw)
        self.nodes[name] = ob
        return ob

    def bridge(self, premises: Sequence[str], conclusion: str, scope_loss: float = 0.0) -> Bridge:
        for v in list(premises) + [conclusion]:
            if v not in self.nodes:
                raise KeyError(v)
        b = Bridge(tuple(premises), conclusion, scope_loss)
        self.bridges.append(b)
        return b

    def leaves(self) -> List[str]:
        """Terminal leaves: obligations that no bridge concludes."""
        concluded = {b.conclusion for b in self.bridges}
        return [v for v in self.nodes if v not in concluded]

    def mass(self, names) -> float:
        return sum(self.nodes[v].weight for v in names)

    def debt_mass(self) -> float:
        """DebtMass(C) = Mass({v : status(v) != PASS})."""
        return self.mass(v for v, ob in self.nodes.items() if ob.status != "PASS")

    def certified(self) -> set:
        """Theorem 6.3: a node is certified if it is a PASS leaf, or the conclusion of a bridge with
        zero scope loss all of whose premises are certified.  Computed as a least fixed point."""
        cert = {v for v in self.leaves() if self.nodes[v].status == "PASS"}
        changed = True
        while changed:
            changed = False
            for b in self.bridges:
                if b.conclusion not in cert and b.scope_loss == 0 and all(p in cert for p in b.premises):
                    cert.add(b.conclusion)
                    changed = True
        return cert

    def releasable(self, root: str) -> bool:
        return root in self.certified()

    def blockers(self, root: str) -> List[str]:
        """Leaves below `root` that are not PASS, and bridges with positive scope loss."""
        below, stack = set(), [root]
        while stack:
            v = stack.pop()
            if v in below:
                continue
            below.add(v)
            for b in self.bridges:
                if b.conclusion == v:
                    stack.extend(b.premises)
        out = [v for v in self.leaves() if v in below and self.nodes[v].status != "PASS"]
        out += [f"scope loss {b.scope_loss} on {b.premises} => {b.conclusion}"
                for b in self.bridges if b.conclusion in below and b.scope_loss > 0]
        return out


# ---------------------------------------------------------------- six-gate vector (Section 11)

GATES = ("orbit", "upper", "lower", "witness", "barrier", "formal")


def numerical_lift(g, defect: float = 0.0) -> float:
    """s_j = 1 if g_j = 1, 0 if g_j = 0, exp(-Delta_j) if g_j = '*' (an unresolved star)."""
    if g == 1:
        return 1.0
    if g == 0:
        return 0.0
    if g == "*":
        if defect < 0:
            raise ValueError("defects are nonnegative")
        return math.exp(-defect)
    raise ValueError(f"gate value must be 0, 1 or '*', got {g!r}")


def m_star(gates: Sequence, defects: Sequence[float], weights: Optional[Sequence[float]] = None) -> float:
    """Unresolved-gate mass M*(G) = sum_j w_j (1 - s_j)^2 (Definition 11.1)."""
    n = len(gates)
    w = list(weights) if weights is not None else [1.0 / n] * n
    if any(x <= 0 for x in w) or abs(sum(w) - 1) > 1e-12:
        raise ValueError("weights must be positive and sum to one")
    return sum(wj * (1 - numerical_lift(g, d)) ** 2 for wj, g, d in zip(w, gates, defects))


def gate_dist(gates, defects, weights=None) -> float:
    return math.sqrt(m_star(gates, defects, weights))
