"""The Section 22 core loop.

    parse C -> open proof / refutation branches -> obligation graph -> generator proposes ->
    verifiers project -> failed gates become residue bullets -> playbook delta (collapse guard)
    -> emit a label

The generator is pluggable: a person, a script, or a language model.  The engine never trusts
it: obligations change status only through verifiers, and the label comes only from the
release algebra.  A run that ends with Rel = 0 has produced a residue ledger, not a proof.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Union

from .ledger import Ledger
from .obligations import ObligationGraph
from .package import ConjecturePackage
from .playbook import Bullet, Playbook
from .release import VERIFIERS, blocking_factors, emit

Verifier = Union[int, Callable[[], int]]


@dataclass
class Proposal:
    """What a generator offers at one step."""
    obligations: List[dict] = field(default_factory=list)       # new obligations (Obligation kwargs)
    bridges: List[tuple] = field(default_factory=list)          # (premises, conclusion, scope_loss)
    checks: Dict[str, Verifier] = field(default_factory=dict)   # obligation name -> verifier
    model_ok: bool = False                                      # a complete candidate argument exists
    lessons: List[Bullet] = field(default_factory=list)         # playbook bullets to add


@dataclass
class Engine:
    package: ConjecturePackage
    graph: ObligationGraph
    verifiers: Dict[str, Verifier]
    playbook: Playbook = field(default_factory=Playbook)
    root: str = "main"
    kind: str = "proof"
    required: Sequence[str] = VERIFIERS
    ledger: Ledger = field(default_factory=Ledger)
    model_ok: bool = False

    @staticmethod
    def _run(v: Verifier) -> int:
        r = v() if callable(v) else v
        return 1 if r == 1 else 0

    def step(self, t: int, proposal: Optional[Proposal]) -> dict:
        resolved, lessons = [], []
        if proposal is not None:
            for ob in proposal.obligations:
                if ob["name"] not in self.graph.nodes:
                    self.graph.add(**ob)
            for prem, concl, *loss in proposal.bridges:
                self.graph.bridge(prem, concl, loss[0] if loss else 0.0)
            for name, v in proposal.checks.items():
                ob = self.graph.nodes[name]
                ok = self._run(v)
                ob.status = "PASS" if ok else "FAIL"
                bid = f"{self.package.name}:{name}"
                if ok:
                    resolved.append(bid)
                else:
                    lessons.append(Bullet(bid, gate=ob.kind, claim=f"{name} failed its verifier",
                                          status="FAIL", verifier="FAIL", source=f"step {t}"))
            lessons.extend(proposal.lessons)
            self.model_ok = self.model_ok or proposal.model_ok
        known = {b.id for b in self.playbook.bullets}
        accepted = self.playbook.apply_delta(add=lessons, resolve=[r for r in resolved if r in known])
        factors = {chi: self._run(v) for chi, v in self.verifiers.items()}
        if self.root in self.graph.nodes and not self.graph.releasable(self.root):
            factors["proof"] = 0          # the obligation graph does not certify the root
        label = emit(factors, kind=self.kind, model_ok=self.model_ok, required=self.required)
        rec = dict(t=t, label=label.value, factors=factors,
                   blocking=blocking_factors(factors, self.required),
                   debt_mass=self.graph.debt_mass(), core=len(self.playbook.core()),
                   density=str(self.playbook.density()), accepted=accepted)
        self.ledger.append(**rec)
        return rec

    def run(self, generator: Callable[["Engine", int], Optional[Proposal]], steps: int) -> dict:
        rec = {}
        for t in range(steps):
            rec = self.step(t, generator(self, t))
            if rec["label"] in ("THEOREM", "COUNTEREXAMPLE", "INDEPENDENCE"):
                break
        return rec
