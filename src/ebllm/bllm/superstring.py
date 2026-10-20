"""The superstring: one end-to-end attack chain per target, with an agent assigned to every target,
zone and piece, run to the end and stopped only at a certificate or at a named stop.

Uploaded by a second agent on Tubai's command.  Vocabulary:

    target   one of the four conjectures (hodge, strings, seed, yang-mills);
    zone     a wall of the atlas (``bllm/data/atlas.json``), or ``frontier`` for a first instance
             that no wall names;
    piece    the single finite or local question an attacker works on;
    attacker the engine agent assigned to one piece: its move (one of the six of ``agents``), its
             method, inputs, the certificate that would close the piece, and its stop rule.

The chain of a target is an ordered list of attackers ending in a ``bypass`` stage, the last step:
a search of everything the engine keeps (controls, tasks, atlas) for a result that already implies
the target.  ``run`` walks the chain: a stage is closed when its recorded status is one of the
closed statuses of ``frontier`` (lean-here, lean-external, proved, computed) or when the evidence
passed in carries a certificate of such a kind checked by someone other than its producer.  A
target is closed exactly when every stage of its chain is closed.  With the bundled data no target
is closed, and ``run`` says at which stage each one stops and what that stage needs.

The closure rule is the only rule: no stage closes on a claim, a conditional statement, an
unrefereed input or a certificate checked by its own producer.  That is what makes the agent
unable to record a false closure; it does not make the mathematics easier.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from .agents import MOVES
from .frontier import CLOSED, STATUSES

_PATH = Path(__file__).parent / "data" / "attackers.json"
ZONE_FRONTIER = "frontier"
INDEPENDENT = ("lean", "independent-check", "published")


def load(path: Optional[str] = None) -> dict:
    with open(path or _PATH, encoding="utf-8") as f:
        return json.load(f)


def check(data: dict, atlas: Optional[dict] = None) -> List[str]:
    """Structural errors: fields, statuses, moves, zones that exist in the atlas, chains made of
    known attackers and ending in a bypass stage."""
    errors = []
    for name, t in data.get("targets", {}).items():
        ids = set()
        walls = set()
        if atlas is not None:
            walls = {w["id"] for w in atlas["targets"].get(name, {}).get("walls", [])}
        for a in t.get("attackers", []):
            for key in ("id", "zone", "piece", "move", "method", "inputs", "certificate", "stop_rule", "status", "result", "source"):
                if key not in a:
                    errors.append(f"{name}: attacker {a.get('id', '?')} missing {key}")
            if a.get("status") not in STATUSES:
                errors.append(f"{name}: attacker {a.get('id', '?')} has status {a.get('status')!r}")
            if a.get("move") not in MOVES:
                errors.append(f"{name}: attacker {a.get('id', '?')} has move {a.get('move')!r}")
            if atlas is not None and a.get("zone") != ZONE_FRONTIER and a.get("zone") not in walls:
                errors.append(f"{name}: attacker {a.get('id', '?')} has zone {a.get('zone')!r} not in the atlas")
            if a.get("id") in ids:
                errors.append(f"{name}: duplicate attacker {a.get('id')}")
            ids.add(a.get("id"))
        chain = t.get("chain", [])
        for cid in chain:
            if cid not in ids:
                errors.append(f"{name}: chain names unknown attacker {cid}")
        if not chain:
            errors.append(f"{name}: empty chain")
        else:
            last = next((a for a in t["attackers"] if a["id"] == chain[-1]), None)
            if last is None or last.get("move") != "bypass":
                errors.append(f"{name}: chain does not end in a bypass stage")
        for g in t.get("gaps", []):
            for key in ("id", "zone", "papers_do", "missing", "attacker"):
                if key not in g:
                    errors.append(f"{name}: gap {g.get('id', '?')} missing {key}")
            if g.get("attacker") not in ids:
                errors.append(f"{name}: gap {g.get('id', '?')} names unknown attacker {g.get('attacker')}")
    return errors


def _independent(cert: dict) -> bool:
    return (cert.get("kind") in CLOSED and cert.get("checker") in INDEPENDENT
            and cert.get("checker") != cert.get("producer"))


def run(data: dict, target: Optional[str] = None, evidence: Optional[Dict[str, dict]] = None) -> Dict[str, dict]:
    """Walk each chain.  ``evidence`` maps attacker ids to certificates {kind, checker, producer, ref}.
    Returns, per target: the stages with their state, the first stop, and whether the target is closed."""
    evidence = evidence or {}
    out = {}
    for name, t in data["targets"].items():
        if target and name != target:
            continue
        by = {a["id"]: a for a in t["attackers"]}
        stages = []
        stop = None
        for cid in t["chain"]:
            a = by[cid]
            cert = evidence.get(cid)
            if cert is not None and _independent(cert):
                state, why = "closed", f"certificate {cert['kind']} checked by {cert['checker']}"
            elif cert is not None:
                state, why = "stopped", "certificate not independently checked (kind %r, checker %r)" % (
                    cert.get("kind"), cert.get("checker"))
            elif a["status"] in CLOSED:
                state, why = "closed", f"status {a['status']}: {a['result']}"
            else:
                state, why = "stopped", f"status {a['status']}: needs {a['certificate']}"
            stages.append(dict(id=cid, zone=a["zone"], move=a["move"], state=state, why=why))
            if state == "stopped" and stop is None:
                stop = cid
        closed = all(s["state"] == "closed" for s in stages)
        out[name] = dict(target=name, closed=closed, first_stop=stop, stages=stages,
                         verdict=("closed: every stage of the chain carries an independently checked certificate"
                                  if closed else f"open: stops at {stop}; " + next(s["why"] for s in stages if s["id"] == stop)))
    return out


def roster(data: dict, target: Optional[str] = None, zone: Optional[str] = None) -> List[dict]:
    rows = []
    for name, t in data["targets"].items():
        if target and name != target:
            continue
        for a in t["attackers"]:
            if zone and a["zone"] != zone:
                continue
            rows.append(dict(target=name, **a))
    return rows


def summary(data: dict, target: Optional[str] = None, evidence: Optional[Dict[str, dict]] = None) -> List[str]:
    lines = [data["title"], data["closure_rule"]]
    res = run(data, target, evidence)
    for name, t in data["targets"].items():
        if target and name != target:
            continue
        lines.append("")
        lines.append(f"{name}: {res[name]['verdict']}")
        lines.append("  gaps in the papers' attack strategy:")
        for g in t["gaps"]:
            lines.append(f"    {g['id']} [zone {g['zone']}]: they {g['papers_do']}; missing: {g['missing']} -> {g['attacker']}")
        lines.append("  chain:")
        for s in res[name]["stages"]:
            a = next(x for x in t["attackers"] if x["id"] == s["id"])
            lines.append(f"    {s['state']:7} {s['id']} [zone {s['zone']}, move {s['move']}]: {a['piece']}")
            lines.append(f"            method: {a['method']}; certificate: {a['certificate']}; stop: {a['stop_rule']}")
    return lines
