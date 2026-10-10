"""Run ledgers and the Section 32 contract report."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Ledger:
    records: List[Dict[str, Any]] = field(default_factory=list)

    def append(self, **rec) -> None:
        self.records.append(rec)

    def dumps(self) -> str:
        return json.dumps(self.records, indent=2, default=str)

    def last(self) -> Dict[str, Any]:
        return self.records[-1] if self.records else {}


def contract_report(engine) -> str:
    """The items of the long-form verifier contract (Section 32) that a run can fill in."""
    pkg, g, pb = engine.package, engine.graph, engine.playbook
    last = engine.ledger.last()
    out = [f"# Run report: {pkg.name}", ""]
    out += ["## 1. Axiom base", "", pkg.axioms, ""]
    out += ["## 2. Definition ledger (obligations)", ""]
    cert = g.certified()
    out += [f"- `{ob.name}` ({ob.kind}, weight {ob.weight}): {ob.status}"
            + (f", verified by {ob.verifier}" if ob.verifier else "")
            + (", certified through its bridges" if ob.name in cert and ob.status != "PASS" else "")
            for ob in g.nodes.values()]
    out += ["", "## 3. Dependency graph", ""]
    out += [f"- {', '.join(b.premises)} ⇒ {b.conclusion}" + (f" (scope loss {b.scope_loss})" if b.scope_loss else "")
            for b in g.bridges] or ["- (no bridges)"]
    out += ["", "## 5. Residue ledger", ""]
    blockers = g.blockers(engine.root) if engine.root in g.nodes else []
    out += [f"- {x}" for x in blockers] or ["- none"]
    out += ["", "## 8. Playbook", ""]
    out += [f"- core failures: {len(pb.core())}, bullets: {len(pb.bullets)}, density {pb.density()}, "
            f"rejected updates: {pb.rejected}"]
    out += [f"- [{b.status}/{b.verifier}] {b.gate}: {b.claim}" for b in pb.bullets]
    out += ["", "## 14. Release label", ""]
    out += [f"**{last.get('label', 'none')}**; factors {last.get('factors', {})}; "
            f"blocking: {', '.join(last.get('blocking', [])) or 'none'}"]
    out += ["", "## 15. Human / referee checklist", ""]
    out += ["- [ ] every definition typed, with its axiom scope",
            "- [ ] proof, refutation and independence branches all considered",
            "- [ ] every bridge has zero or named scope loss",
            "- [ ] every unresolved star converted into a named residue",
            "- [ ] the label is one of THEOREM, COUNTEREXAMPLE, CONDITIONAL, INDEPENDENCE, CANDIDATE, BUJ, OPEN"]
    return "\n".join(out) + "\n"
