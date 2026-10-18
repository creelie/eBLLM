"""One headline round: the crossing network aimed at the open steps of Yang-Mills and Hodge, its
controls, and the per-step closure of both trees.  Appends to experiments/headline_rounds.json.

    python3 experiments/headline.py
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
from ebllm.bllm import targets as T  # noqa: E402

out_path = os.path.join(HERE, "headline_rounds.json")
rounds = json.load(open(out_path)) if os.path.exists(out_path) else []
tree = T.headline_tree()
before = {r: T.closure(tree, r) for r in ("YM", "H")}
net = T.run("network", generations=5, per_gen=200)
changes = T.apply(tree, net["accepted"])
after = {r: T.closure(tree, r) for r in ("YM", "H")}
checks = T.all_checks()
residues = {}
for c in checks:
    if c["outcome"] != "accepted":
        residues.setdefault(c["node"], set()).add(c["statement"])
rec = dict(round=len(rounds) + 1, time=time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()),
           arms=T.compare(seeds=5, generations=5, per_gen=40),
           accepted={k: v for k, v in net["accepted"].items()},
           changes=changes, closure_before=before, closure_after=after,
           residues={k: sorted(v) for k, v in residues.items()},
           gauges={g: T.gauge_count(g) for g in T.GAUGES})
rounds.append(rec)
json.dump(rounds, open(out_path, "w"), indent=1)
for r in ("YM", "H"):
    a = after[r]
    print(f"{r}: {a['proved']}/{a['leaves']} leaves proved ({100 * a['share']:.1f}%); open {a['open']}; "
          f"blocked {a['blocked']}")
print("changes:", changes)
print("arms:", json.dumps(rec["arms"]))
for k, v in rec["residues"].items():
    print(k, "|", " / ".join(v))
