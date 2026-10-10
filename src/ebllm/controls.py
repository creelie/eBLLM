"""The controls ledger: closures made with this project, external calibration theorems and open
problems, each with its verifier factors.  The label is computed by the release algebra, never
stored, so a factor change is the only way to change a label.

`required` lists the verifiers the label depends on: all eight for new results, and the
classical ones (proof, risk, literature, referee) for theorems proved before formal tools.
A new result that has not been refereed stays a CANDIDATE however strong the rest is.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from importlib import resources
from typing import Dict, List, Optional

from .release import Label, blocking_factors, emit


@dataclass
class Control:
    slug: str
    name: str
    group: str               # closure, partial, calibration, open
    kind: str
    target: str
    result: str
    factors: Dict[str, int]
    required: List[str]
    authors: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    notes: Dict[str, str] = field(default_factory=dict)
    links: Dict[str, Optional[str]] = field(default_factory=dict)
    barriers: List[str] = field(default_factory=list)
    model_ok: bool = True
    improving_machinery: bool = True

    @property
    def label(self) -> Label:
        return emit(self.factors, kind=self.kind, conditions=self.conditions, model_ok=self.model_ok,
                     improving_machinery=self.improving_machinery, required=self.required)

    @property
    def blocking(self) -> List[str]:
        return blocking_factors(self.factors, self.required)


def load_controls() -> List[Control]:
    out = []
    folder = resources.files("ebllm") / "controls"
    for entry in sorted(folder.iterdir(), key=lambda p: p.name):
        if entry.name.endswith(".json"):
            d = json.loads(entry.read_text(encoding="utf-8"))
            out.append(Control(**d))
    order = {"closure": 0, "partial": 1, "calibration": 2, "open": 3}
    return sorted(out, key=lambda c: (order.get(c.group, 9), c.slug))


def table(controls: List[Control]) -> str:
    lines = ["| control | group | label | blocking verifiers |", "|---|---|---|---|"]
    for c in controls:
        lines.append(f"| {c.name} | {c.group} | {c.label.value} | {', '.join(c.blocking) or '—'} |")
    return "\n".join(lines)
