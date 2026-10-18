"""Stepwise records of hard problems: how each solved one was proved, step by step, and where the
open ones stand, with the ladder of weaker statements and the plan BLLM follows on each open step.

Every record is a JSON file of the folder tasks/ with fields id, title, status, statement,
how_it_was_proved, formal (the system and repository of a formal proof, where one exists),
sources, steps (each proved, partial or open, with its evidence: lean, formal, published or none,
and the moves that found it) and open (the open steps).  The records state only what the cited
sources prove; a step is "proved" only when a published or machine-checked proof exists.
"""
from __future__ import annotations

import glob
import json
import os
from typing import Dict, List

FOLDER = os.path.join(os.path.dirname(__file__), "tasks")
STATUSES = ("proved", "partial", "open")
EVIDENCE = ("lean", "formal", "published", "none")


def load_tasks(folder: str = FOLDER) -> Dict[str, dict]:
    out = {}
    for f in sorted(glob.glob(os.path.join(folder, "*.json"))):
        with open(f, encoding="utf-8") as fh:
            d = json.load(fh)
        validate(d)
        out[d["id"]] = d
    return out


def validate(d: dict) -> None:
    for k in ("id", "title", "status", "statement", "steps", "open", "sources"):
        if k not in d:
            raise ValueError(f"task {d.get('id', '?')}: missing {k}")
    keys = {s["key"] for s in d["sources"]}
    ids = {s["id"] for s in d["steps"]}
    for s in d["steps"]:
        if s["status"] not in STATUSES or s["evidence"] not in EVIDENCE:
            raise ValueError(f"task {d['id']}: bad step {s['id']}")
        if s["status"] == "proved" and s["evidence"] == "none":
            raise ValueError(f"task {d['id']}: step {s['id']} is proved with no evidence")
        if s["source"] not in keys:
            raise ValueError(f"task {d['id']}: step {s['id']} cites the unknown source {s['source']}")
    for o in d["open"]:
        if o["step"] not in ids:
            raise ValueError(f"task {d['id']}: open entry for the unknown step {o['step']}")
        for r in o["ladder"]:
            if r["source"] not in keys:
                raise ValueError(f"task {d['id']}: ladder cites the unknown source {r['source']}")
    opened = {s["id"] for s in d["steps"] if s["status"] == "open"}
    if opened - {o["step"] for o in d["open"]}:
        raise ValueError(f"task {d['id']}: open steps without a plan: {sorted(opened - {o['step'] for o in d['open']})}")


def summary(tasks: Dict[str, dict]) -> str:
    lines = [f"{'task':14s} {'status':34s} proved/partial/open  formal"]
    for t in tasks.values():
        c = [sum(s["status"] == x for s in t["steps"]) for x in STATUSES]
        f = t.get("formal", {}).get("system", "")
        lines.append(f"{t['id']:14s} {t['status'][:34]:34s} {c[0]:3d} {c[1]:3d} {c[2]:3d}         {f}")
    return "\n".join(lines)


def attack_plan(t: dict) -> str:
    """The open steps of a task, each with its ladder from the strongest proved rung up, and BLLM's plan."""
    src = {s["key"]: s for s in t["sources"]}
    out = [f"# {t['title']}", "", t["statement"], ""]
    for s in t["steps"]:
        mark = {"proved": "[x]", "partial": "[~]", "open": "[ ]"}[s["status"]]
        out.append(f"{mark} {s['statement']}  ({s['evidence']}; {s['source']}; moves: {', '.join(s['moves'])})")
    for o in t["open"]:
        out += ["", f"## open step: {o['step']}"]
        for r in o["ladder"]:
            out.append(f"  {'proved' if r['status'] == 'proved' else 'open  '}  {r['statement']}  [{r['source']}]")
        out += ["", "  plan: " + o["bllm_plan"]]
    out += ["", "## sources"] + [f"- {k}: {v['cite']} {v.get('url', '')}" for k, v in src.items()]
    return "\n".join(out)
