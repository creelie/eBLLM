"""Triage before the attack: a go or no-go on each candidate problem or route, decided from supplied
ratings before any search is run.

Uploaded by a second agent on Tubai's command.  Taken from the supplied-input opportunity comparison of
MontrealAI's AGI-Alpha-Agent (https://github.com/MontrealAI/AGI-Alpha-Agent-v0,
alpha_factory_v1/demos/cross_industry_alpha_factory/opportunity_comparison.py, Apache-2.0): strict
validation of the input, a weighted score in exact rational arithmetic rounded half up, hard
constraints that exclude a candidate with a stated reason, and the Pareto front of the eligible ones.
Here the four dimensions are read for mathematics:

    value        what settling it is worth (a named open problem, a table entry, a lemma);
    closability  how sure we are that it can be settled with an independently checkable certificate
                 (a proof, a Lean term, a finite exhaustive check), not merely attacked;
    effort       the expected cost in compute and in hours;
    risk         the chance that the effort ends with nothing that can be recorded.

A candidate whose closability is below ``min_closability`` or whose risk is above ``max_risk`` is a
no-go whatever its value: that is the rule that a long shot is not started unless it is asked for.
The ratings are judgements supplied by whoever fills the file; the triage makes them explicit,
comparable and reproducible.  It does not estimate a probability and it never runs an attack.
"""
from __future__ import annotations

import hashlib
import json
import re
from typing import Any, Dict, List

DIMENSIONS = ("value", "closability", "effort", "risk")
SCHEMA = "anaxia-triage-v1"
LIMITS = [
    "The ratings are supplied judgements, not measured facts.",
    "The score orders candidates; it is not a probability of closure.",
    "A go is permission to start a bounded attempt, not a claim that the problem will close.",
]


def _keys(v: Any, want: set, label: str) -> None:
    if not isinstance(v, dict) or set(v) != want:
        raise ValueError(f"{label}: expected exactly {', '.join(sorted(want))}")


def _rating(v: Any, label: str) -> None:
    if type(v) is not int or not 0 <= v <= 100:  # bools and other int subclasses are refused
        raise ValueError(f"{label}: expected an integer from 0 to 100")


def _text(v: Any, limit: int, label: str) -> None:
    if not isinstance(v, str) or not v.strip() or v != v.strip() or len(v) > limit:
        raise ValueError(f"{label}: expected trimmed non-empty text of at most {limit} characters")


def validate(data: Any) -> None:
    """Refuse unknown fields and coerced ratings before anything is computed."""
    _keys(data, {"schema", "weights", "constraints", "candidates"}, "input")
    if data["schema"] != SCHEMA:
        raise ValueError(f"schema must be {SCHEMA}")
    _keys(data["weights"], set(DIMENSIONS), "weights")
    for k in DIMENSIONS:
        _rating(data["weights"][k], f"weights.{k}")
    if not sum(data["weights"].values()):
        raise ValueError("weights must have a positive sum")
    _keys(data["constraints"], {"max_risk", "min_closability"}, "constraints")
    for k, v in data["constraints"].items():
        _rating(v, f"constraints.{k}")
    rows = data["candidates"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= 200:
        raise ValueError("candidates: expected 1 to 200")
    seen = set()
    for i, r in enumerate(rows):
        lab = f"candidates[{i}]"
        _keys(r, {"id", "problem", "certificate", "evidence", *DIMENSIONS}, lab)
        if not isinstance(r["id"], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,63}", r["id"]):
            raise ValueError(f"{lab}.id: 1 to 64 letters, digits, dots, underscores or hyphens")
        if r["id"] in seen:
            raise ValueError(f"duplicate candidate id {r['id']}")
        seen.add(r["id"])
        _text(r["problem"], 500, f"{lab}.problem")
        _text(r["certificate"], 300, f"{lab}.certificate")
        for k in DIMENSIONS:
            _rating(r[k], f"{lab}.{k}")
        if not isinstance(r["evidence"], list) or not 1 <= len(r["evidence"]) <= 10:
            raise ValueError(f"{lab}.evidence: 1 to 10 sources or notes")
        for e in r["evidence"]:
            _text(e, 500, f"{lab}.evidence")


def ratio(num: int, den: int) -> float:
    """num/den for non-negative integers, rounded half up to six places, exactly."""
    return ((2 * num * 1_000_000 + den) // (2 * den)) / 1_000_000


def dominates(a: tuple, b: tuple) -> bool:
    """a is at least as good as b everywhere and better somewhere (larger is better)."""
    return all(x >= y for x, y in zip(a, b)) and a != b


def pareto(points: Dict[str, tuple]) -> List[str]:
    return sorted(k for k, p in points.items() if not any(dominates(q, p) for j, q in points.items() if j != k))


def triage(data: Any) -> Dict[str, Any]:
    validate(data)
    w, c = data["weights"], data["constraints"]
    total = sum(w.values())
    rows, front = [], {}
    for r in data["candidates"]:
        good = {k: r[k] if k in ("value", "closability") else 100 - r[k] for k in DIMENSIONS}
        nums = {k: w[k] * good[k] for k in DIMENSIONS}
        why = []
        if r["closability"] < c["min_closability"]:
            why.append("closability below min_closability")
        if r["risk"] > c["max_risk"]:
            why.append("risk above max_risk")
        rows.append({**r, "evidence": list(r["evidence"]), "score": ratio(sum(nums.values()), total),
                     "contributions": {k: ratio(nums[k], total) for k in DIMENSIONS},
                     "go": not why, "no_go_reasons": why, "rank": None, "pareto_optimal": False})
        if not why:
            front[r["id"]] = tuple(good[k] for k in DIMENSIONS)
    on = set(pareto(front))
    for row in rows:
        row["pareto_optimal"] = row["id"] in on
    rows.sort(key=lambda x: (not x["go"], -x["score"] if x["go"] else 0, x["id"]))
    for i, row in enumerate(rows):
        if row["go"]:
            row["rank"] = i + 1
    digest = hashlib.sha256(json.dumps(data, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    return {"schema": "anaxia-triage-report-v1", "input_sha256": digest,
            "weights": {k: ratio(w[k], total) for k in DIMENSIONS}, "constraints": dict(c),
            "ranking": rows, "first": rows[0]["id"] if rows[0]["go"] else None, "limits": list(LIMITS)}


def table(report: Dict[str, Any]) -> str:
    out = [f"{'rank':>4}  {'go':<6} {'score':>8}  {'pareto':<6}  id / reason"]
    for r in report["ranking"]:
        out.append(f"{r['rank'] or '-':>4}  {'go' if r['go'] else 'no-go':<6} {r['score']:>8.3f}  "
                   f"{'yes' if r['pareto_optimal'] else '':<6}  {r['id']}"
                   + ("" if r["go"] else "  (" + "; ".join(r["no_go_reasons"]) + ")"))
    out.append("first: " + (report["first"] or "nothing passes the constraints: no attack is started"))
    return "\n".join(out)
