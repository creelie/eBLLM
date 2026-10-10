"""Module 26: the context playbook (Section 18) with two collapse guards.

A bullet records one lesson of an attempt: the gate it concerns, the claim, whether it failed,
and what verified it.  Core(P) is the set of bullets recording unresolved failures.

`collapse_paper` is the guard of the paper,

    Collapse(P, P') = 1 - |Core(P) & Core(P')| / |Core(P)|,

which counts a failure that was *resolved* (its verifier now passes, so it leaves the core)
exactly like a failure that was *deleted*.  Under the hypothesis of Theorem 30.1,
theta < 1/|Core(P)|, it therefore rejects every update that resolves a core failure, so the
engine could never record the success of a repair, and Corollary 30.2's "the core shrinks only
when a failure is resolved" never happens.  It is also undefined when the core is empty, and
the hypothesis theta < 1/|Core(P_t)| fails as soon as the core outgrows 1/theta.

`collapse_v11` is the guard of circuit v1.1 (docs/CIRCUIT-v1.1.md): it counts only core
bullets that disappear from the playbook without having been discharged by a verifier.  With
theta = 0 no unresolved failure can ever be erased, and resolutions are always accepted;
`lean/EBLLM/Playbook.lean` proves both facts.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from fractions import Fraction
from typing import Dict, Iterable, List, Optional


@dataclass(frozen=True)
class Bullet:
    id: str
    gate: str
    claim: str
    status: str = "UNK"        # PASS, FAIL or UNK: the outcome of the step the bullet records
    verifier: str = "UNK"      # PASS when an external verifier discharged it
    helpful: int = 0
    harmful: int = 0
    source: str = ""

    @property
    def is_core(self) -> bool:
        return self.status in ("FAIL", "UNK") and self.verifier != "PASS"


def core(bullets: Iterable[Bullet]) -> Dict[str, Bullet]:
    return {b.id: b for b in bullets if b.is_core}


def collapse_paper(old: Iterable[Bullet], new: Iterable[Bullet]) -> Fraction:
    """The paper's guard.  Returns 0 when the old core is empty (the paper leaves it undefined)."""
    c_old, c_new = core(old), core(new)
    if not c_old:
        return Fraction(0)
    kept = len(set(c_old) & set(c_new))
    return 1 - Fraction(kept, len(c_old))


def collapse_v11(old: Iterable[Bullet], new: Iterable[Bullet]) -> Fraction:
    """The v1.1 guard: the fraction of old core failures that vanish from the playbook without
    a verifier having discharged them.  A bullet whose verifier became PASS is a resolution,
    not a loss; a bullet still present (in any status) is not lost."""
    c_old = core(old)
    if not c_old:
        return Fraction(0)
    new_by_id = {b.id: b for b in new}
    lost = 0
    for bid in c_old:
        b = new_by_id.get(bid)
        if b is None:
            lost += 1
    return Fraction(lost, len(c_old))


def density(bullets: List[Bullet]) -> Fraction:
    """rho_crit(P) = |Core(P)| / |P| (Definition 30.3); 0 for the empty playbook."""
    return Fraction(len(core(bullets)), len(bullets)) if bullets else Fraction(0)


@dataclass
class Playbook:
    bullets: List[Bullet] = field(default_factory=list)
    theta: Fraction = Fraction(0)
    rule: str = "v1.1"                  # "v1.1" or "paper"
    archive: List[Bullet] = field(default_factory=list)
    rejected: int = 0

    def _collapse(self, new: List[Bullet]) -> Fraction:
        return collapse_v11(self.bullets, new) if self.rule == "v1.1" else collapse_paper(self.bullets, new)

    def propose(self, new: List[Bullet]) -> bool:
        """Curator step: accept the whole new playbook if the guard allows it."""
        if self._collapse(new) > self.theta:
            self.rejected += 1
            return False
        kept = {b.id for b in new}
        self.archive.extend(b for b in self.bullets if b.id not in kept)
        self.bullets = list(new)
        return True

    def apply_delta(self, add: Iterable[Bullet] = (), resolve: Iterable[str] = (),
                    remove: Iterable[str] = ()) -> bool:
        """Localized delta update: append bullets, mark bullets verified, remove bullets."""
        resolve, remove = set(resolve), set(remove)
        new = []
        for b in self.bullets:
            if b.id in remove:
                continue
            new.append(replace(b, status="PASS", verifier="PASS") if b.id in resolve else b)
        ids = {b.id for b in new}
        for b in add:
            if b.id not in ids:
                new.append(b)
                ids.add(b.id)
        return self.propose(new)

    def core(self) -> Dict[str, Bullet]:
        return core(self.bullets)

    def density(self) -> Fraction:
        return density(self.bullets)

    def retrieve(self, gate: str, k: int = 5) -> List[Bullet]:
        """Simple retrieval: bullets of the same gate first, then by helpful - harmful."""
        pool = self.bullets + self.archive
        return sorted(pool, key=lambda b: (b.gate != gate, -(b.helpful - b.harmful)))[:k]

    def to_list(self) -> List[dict]:
        return [b.__dict__ for b in self.bullets]
