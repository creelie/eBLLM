"""The barrier atlas: for each of the four target conjectures, the proved walls, the hypothesis each
rests on, the construction that would break it, and the routes proposed against it.

The atlas is data (``data/atlas.json``), read here and printed by ``anaxia barriers``.  It was
uploaded by a second agent on Tubai's command from a read-only study of the conjecture repositories,
so that every copy of the engine knows the same walls.  The machine-checked part of the same study
is ``barriers``: the walls that have predicates on library nodes live there as ``Barrier`` records
and prune composites; the atlas keeps the walls whose hypotheses are not yet expressed on library
nodes, and the routes, with a status for each.

Statuses are ``established`` (proved in the cited source and reread), ``conditional`` (rests on an
unproved or unrefereed input), ``proposed`` (a route stated in the atlas, untested) and ``open`` (no
known method).  A proposed route proves nothing; it says what to try and what a positive or negative
answer would settle.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

STATUSES = ("established", "conditional", "proposed", "open")

_PATH = Path(__file__).parent / "data" / "atlas.json"


def load(path: str | None = None) -> dict:
    with open(path or _PATH, encoding="utf-8") as f:
        return json.load(f)


def check(atlas: dict) -> List[str]:
    """Structural errors: every wall and route has an id, a status from STATUSES, and the fields
    its kind requires; ids are unique within a target."""
    errors = []
    for name, t in atlas.get("targets", {}).items():
        for key in ("statement", "verdict", "walls", "routes"):
            if key not in t:
                errors.append(f"{name}: missing {key}")
        seen = set()
        for w in t.get("walls", []):
            for key in ("id", "statement", "source", "hypothesis", "breaker", "status"):
                if key not in w:
                    errors.append(f"{name}: wall {w.get('id', '?')} missing {key}")
            if w.get("status") not in STATUSES:
                errors.append(f"{name}: wall {w.get('id', '?')} has status {w.get('status')!r}")
            if w.get("id") in seen:
                errors.append(f"{name}: duplicate id {w.get('id')}")
            seen.add(w.get("id"))
        for r in t.get("routes", []):
            for key in ("id", "text", "status"):
                if key not in r:
                    errors.append(f"{name}: route {r.get('id', '?')} missing {key}")
            if r.get("status") not in STATUSES:
                errors.append(f"{name}: route {r.get('id', '?')} has status {r.get('status')!r}")
            if r.get("id") in seen:
                errors.append(f"{name}: duplicate id {r.get('id')}")
            seen.add(r.get("id"))
    return errors


def counts(atlas: dict) -> Dict[str, Dict[str, int]]:
    """Per target: walls, routes, and how many of each status."""
    out = {}
    for name, t in atlas["targets"].items():
        row = {"walls": len(t["walls"]), "routes": len(t["routes"])}
        for s in STATUSES:
            row[s] = sum(1 for x in t["walls"] + t["routes"] if x["status"] == s)
        out[name] = row
    return out


def summary(atlas: dict, target: str | None = None) -> List[str]:
    lines = [atlas["title"]]
    for name, t in atlas["targets"].items():
        if target and name != target:
            continue
        lines.append("")
        lines.append(f"{name}: {t['verdict']}")
        for w in t["walls"]:
            lines.append(f"  wall {w['id']} [{w['status']}]: {w['statement']}")
            lines.append(f"      rests on: {w['hypothesis']}; breaker: {w['breaker']}")
        for r in t["routes"]:
            lines.append(f"  route {r['id']} [{r['status']}]: {r['text']}")
    return lines
