"""The verifier release algebra of Section 6.

Rel(Y | A) is the product of the verifier factors V_chi in {0, 1} for
chi in {proof, formal, code, trace, sim, risk, lit, human}.  A label is emitted from the
factors and the shape of the claim; nothing else (confidence, presentation, context) can
raise it.  Theorem 2.2, Theorem 3.1 and Theorem 21.3 of the paper are the statement that a
single zero factor blocks release; `lean/EBLLM/Release.lean` proves this.
"""
from __future__ import annotations

from enum import Enum
from typing import Mapping

VERIFIERS = ("proof", "formal", "code", "trace", "sim", "risk", "lit", "human")


class Label(str, Enum):
    THEOREM = "THEOREM"
    COUNTEREXAMPLE = "COUNTEREXAMPLE"
    CONDITIONAL = "CONDITIONAL"
    INDEPENDENCE = "INDEPENDENCE"
    CANDIDATE = "CANDIDATE"
    BUJ = "BUJ"  # barrier-unresolved judgment: no candidate and no improving machinery
    OPEN = "OPEN"  # no candidate yet, but a repair route is open: the run continues

    def __str__(self) -> str:  # pragma: no cover - cosmetic
        return self.value


def release_product(factors: Mapping[str, int], required=VERIFIERS) -> int:
    """Return Rel = prod V_chi over the required verifiers.  A missing factor counts as 0."""
    rel = 1
    for chi in required:
        v = factors.get(chi, 0)
        if v not in (0, 1):
            raise ValueError(f"verifier factor {chi} must be 0 or 1, got {v!r}")
        rel *= v
    return rel


def emit(factors: Mapping[str, int], *, kind: str = "proof", conditions=(), model_ok: bool = False,
         improving_machinery: bool = True, required=VERIFIERS) -> Label:
    """The transition rule of Section 6.1.

    kind                "proof" or "refutation" (a released refutation is a COUNTEREXAMPLE)
                        or "independence"
    conditions          named hypotheses the result still depends on (unproved inputs)
    model_ok            V_model: the generator produced a complete candidate argument
    improving_machinery whether any repair route is still open (otherwise BUJ)
    """
    rel = release_product(factors, required)
    if rel == 1:
        if conditions:
            return Label.CONDITIONAL
        if kind == "refutation":
            return Label.COUNTEREXAMPLE
        if kind == "independence":
            return Label.INDEPENDENCE
        return Label.THEOREM
    if model_ok:
        return Label.CANDIDATE
    return Label.OPEN if improving_machinery else Label.BUJ


def blocking_factors(factors: Mapping[str, int], required=VERIFIERS):
    """The verifiers whose factor is 0 (or missing): the residue a second attempt must discharge."""
    return [chi for chi in required if factors.get(chi, 0) != 1]
