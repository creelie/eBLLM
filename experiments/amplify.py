"""The amplified headline round: second-generation library, refuter, boosters, gap numbers, and the full
export of the construction graph.  Writes experiments/amplify/*.json and appends a round to
experiments/headline_rounds.json.

    python3 experiments/amplify.py [seeds] [--replace]   (--replace rewrites the last amplified round)
"""
import json
import os
import sys
import time
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
from ebllm.bllm import boosters as B  # noqa: E402
from ebllm.bllm import targets as T  # noqa: E402

args = [a for a in sys.argv[1:] if not a.startswith("--")]
seeds = int(args[0]) if args else 200
OUT = os.path.join(HERE, "amplify")
os.makedirs(OUT, exist_ok=True)


def dump(name, obj):
    with open(os.path.join(OUT, name), "w") as fh:
        fh.write(B.to_json(obj))


# 1. every closed composite of the second library up to depth four, with check and refuter
pool = list(B.LIBRARY2)
seen = {c.parts for c in pool}
rows, best = [], dict(B.KNOWN_BEST)
for depth in range(1, 5):
    new = []
    for a in pool:
        for b in pool:
            c = B.cross(a, b)
            if c and c.parts not in seen:
                seen.add(c.parts)
                new.append(c)
                row = dict(depth=depth, child=c.id, a=a.id, b=b.id, parts=list(c.parts), gives=c.gives,
                           closed=c.closed)
                if c.closed:
                    r = B.check2(c)
                    row.update(outcome=r.outcome, node=r.node, statement=r.statement, measurement=r.measurement)
                    if r.outcome == "accepted":
                        ok, why = B.refute(c, r, best)
                        row.update(survived=ok, refuter=why)
                rows.append(row)
    pool += new
import gzip  # noqa: E402
with gzip.open(os.path.join(OUT, "composites.json.gz"), "wt") as fh:
    json.dump(rows, fh, separators=(",", ":"), default=str)
closed = [r for r in rows if r["closed"]]
summary = {}
for r in closed:
    k = r["outcome"] if r["outcome"] != "accepted" else ("survived" if r["survived"] else "refuted")
    summary[k] = summary.get(k, 0) + 1

# 2. the arms with boosters, within one round and across rounds
arms = {syn: B.compare_boosters(seeds=seeds, generations=8, per_gen=6, synapse=syn) for syn in ("head", "edge")}
dump("arms.json", arms)
rounds = B.compare_rounds(seeds=max(50, seeds * 3 // 4), rounds=4, generations=8, per_gen=6, synapse="head")
dump("rounds.json", rounds)

# 3. one traced run per arm, and the synapses of a boosted run over four rounds
traces = [B.run_boosted(arm, generations=8, per_gen=6, seed=0) for arm in ("boosted", "unboosted", "random")]
w, snaps = {}, []
for r in range(4):
    rec = B.run_boosted("boosted", generations=8, per_gen=6, seed=1000 * r, weights=w)
    w = rec["weights"]
    snaps.append(dict(round=r + 1, weights=dict(w), fired=[x for x in rec["crossings"] if x.get("boost")]))
    traces.append(rec)
dump("synapses.json", snaps)
dump("graph.json", B.graph_export(traces))

# 4. gap numbers and the pattern-transfer data
best_ym = max((Fraction(r["measurement"]["range"].split("< ")[1].split()[0]) for r in closed
               if r.get("survived") and r["measurement"].get("range", "").startswith("beta_W")), default=Fraction(0))
gaps = B.gap_numbers(best_ym)
dump("gaps.json", gaps)
dump("fermat_orbit.json", B.fermat_orbit())

# 5. the round record
path = os.path.join(HERE, "headline_rounds.json")
hist = json.load(open(path)) if os.path.exists(path) else []
tree = T.headline_tree()
T.apply(tree, {r["statement"]: dict(node=r["node"]) for r in closed if r.get("survived")})
rec = dict(round=len(hist) + 1, time=time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()), kind="amplified",
           composites=len(rows), closed=len(closed), outcomes=summary,
           closure_after={x: T.closure(tree, x) for x in ("YM", "H")}, gaps=gaps,
           arms={syn: {a: dict(found=v["found_one_third"], runs=v["runs"], survivors=v["survivors"],
                               refuted=v["refuted"], mean_generation=v["mean_generation_one_third"])
                       for a, v in arms[syn].items()} for syn in arms},
           rounds=rounds)
if "--replace" in sys.argv and hist and hist[-1].get("kind") == "amplified":
    rec["round"] = hist[-1]["round"]
    hist[-1] = rec
else:
    hist.append(rec)
json.dump(hist, open(path, "w"), indent=1, default=str)
print(json.dumps(dict(composites=len(rows), closed=len(closed), outcomes=summary, gaps=gaps["yang_mills"],
                      closure={x: (rec["closure_after"][x]["proved"], rec["closure_after"][x]["leaves"])
                               for x in ("YM", "H")}), indent=1))
print(json.dumps(rec["arms"], indent=1))
print(json.dumps(rounds, indent=1))
