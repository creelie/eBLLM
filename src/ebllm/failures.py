"""The failure decomposition tensor (Definition 21.2) and second-attempt routing (Section 28)."""
from __future__ import annotations

from typing import List, Optional, Tuple

from .obligations import GATES

N_MODULES = 26


class FailureTensor:
    def __init__(self, modules: int = N_MODULES, gates=GATES):
        self.gates = tuple(gates)
        self.F = [[0] * len(self.gates) for _ in range(modules)]

    def record(self, module: int, gate: str) -> None:
        """Module `module` (1..26) failed gate `gate` at one step."""
        self.F[module - 1][self.gates.index(gate)] += 1

    def dominant(self) -> Optional[Tuple[int, str, int]]:
        """(i*, j*) = argmax F_ij, with ties broken by the smallest module then gate index."""
        best = None
        for i, row in enumerate(self.F):
            for j, c in enumerate(row):
                if c and (best is None or c > best[2]):
                    best = (i + 1, self.gates[j], c)
        return best

    def by_gate(self) -> List[Tuple[str, int]]:
        return [(g, sum(row[j] for row in self.F)) for j, g in enumerate(self.gates)]


def route_second_attempt(defects: dict, repairability: dict) -> Optional[str]:
    """Route2(C) = argmax_j Delta_j * Repairability_j over gates with positive defect."""
    cands = [(defects[g] * repairability.get(g, 0.0), g) for g in defects if defects[g] > 0]
    if not cands:
        return None
    return max(cands)[1]
