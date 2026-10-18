"""Totals per arm over the seeds of crossing_results.json: offspring, share passing, colourings not
seen before (by the phenotype key), optimal ones among them, and the frontier test."""
import json
import os
import statistics as st
import sys

here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, "crossing_results.json")))
arms = list(d["runs"][0]["arms"])
out = {}
for a in arms:
    rows = [r["arms"][a] for r in d["runs"]]
    tot = lambda key: [sum(g[key] for g in x["per_gen"]) for x in rows]
    off, pas, new, opt = tot("offspring"), tot("passed"), tot("new_colourings"), tot("new_optimal_colourings")
    ill = tot("ill_typed")
    out[a] = {"seeds": len(rows), "offspring": sum(off), "passed": sum(pas),
              "share_passed": round(sum(pas) / max(1, sum(off)), 3), "ill_typed": sum(ill),
              "new_colourings_mean": round(st.mean(new), 2), "new_colourings_sd": round(st.pstdev(new), 2),
              "new_colourings_per_seed": new, "new_optimal_mean": round(st.mean(opt), 2),
              "new_optimal_per_seed": opt,
              "passed_per_gen_mean": [round(st.mean(x["per_gen"][g]["passed"] for x in rows), 2)
                                      for g in range(len(rows[0]["per_gen"]))],
              "new_per_gen_mean": [round(st.mean(x["per_gen"][g]["new_colourings"] for x in rows), 2)
                                   for g in range(len(rows[0]["per_gen"]))]}
fr = d.get("frontier", {}).get("colourings", [])
out["frontier"] = [{"provenance": c["provenance"], "arms": c["arms"], "level": c["level"], "m": c["m"]}
                   for c in fr]
print(json.dumps(out, indent=1))
