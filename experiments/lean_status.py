"""Lean status of the package: theorems, sorry and axiom declarations in lean/, and for every piece of
the frontier map whether its proof is in Lean here, in Lean elsewhere, or not in Lean.  Run from the
repository root: python3 experiments/lean_status.py"""
import json
import os
import re
import sys

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(root, "src"))
from ebllm.bllm import frontier  # noqa: E402


def scan(lean_dir):
    out = {"files": 0, "theorems": 0, "sorry": [], "axioms": []}
    for dp, dn, fn in os.walk(lean_dir):
        dn[:] = [d for d in dn if d not in (".lake", "build")]
        for f in fn:
            if not f.endswith(".lean"):
                continue
            p = os.path.join(dp, f)
            t = re.sub(r"--.*", "", re.sub(r"/-.*?-/", "", open(p).read(), flags=re.S))
            out["files"] += 1
            out["theorems"] += len(re.findall(r"^\s*(?:private\s+)?(?:theorem|lemma)\s", t, flags=re.M))
            rel = os.path.relpath(p, root)
            if re.search(r"\bsorry\b", t):
                out["sorry"].append(rel)
            out["axioms"] += [f"{rel}: {m}" for m in re.findall(r"^\s*axiom\s+(\S+)", t, flags=re.M)]
    return out


if __name__ == "__main__":
    s = scan(os.path.join(root, "lean"))
    pieces = []
    for t in frontier.targets().values():
        for p in t.pieces:
            pieces.append({"target": t.id, "piece": p.id, "status": p.status,
                           "in_lean": p.status in ("lean-here", "lean-external"), "lean": p.lean})
    s["pieces"] = pieces
    s["pieces_in_lean"] = sum(p["in_lean"] for p in pieces)
    print(json.dumps(s, indent=1))
