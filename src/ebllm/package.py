"""The conjecture package C = (D, L, A, P, Q, E0, B0, R0) of Section 2."""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import List


@dataclass
class ConjecturePackage:
    """A conjecture as a typed object.

    domain      D, the mathematical domain
    language    L, the formal language (for example "Lean 4 + Mathlib")
    axioms      A, the axiom base relative to which a release is made
    hypothesis  P and conclusion Q of the target implication P => Q
    evidence    E0, the evidence bundle at the start
    barriers    B0, the known-barrier ledger (relativization, natural proofs, ...)
    residues    R0, the residue ledger at the start
    """

    name: str
    domain: str
    language: str = "Lean 4 + Mathlib"
    axioms: str = "Lean's type theory with propext, Classical.choice, Quot.sound"
    hypothesis: str = ""
    conclusion: str = ""
    evidence: List[str] = field(default_factory=list)
    barriers: List[str] = field(default_factory=list)
    residues: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "ConjecturePackage":
        keys = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in d.items() if k in keys})
