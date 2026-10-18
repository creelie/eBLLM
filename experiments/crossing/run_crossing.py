"""Run the crossing chain reaction on Erdos 1183 in four arms (network, select, random, blind) and
test every distinct optimal colouring the arms found at n = 10 to 14.  Level colourings are tested
exactly with levelmono; the others with findmono, n <= 12, under a time limit.  Writes
crossing_results.json next to this file."""
import json
import os
import sys
import time

here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(here, "..", "..", "src"))
sys.path.insert(0, os.path.join(here, "..", "erdos1183"))
from ebllm.bllm import crossing as X  # noqa: E402
import levelmono  # noqa: E402

gens = int(sys.argv[1]) if len(sys.argv) > 1 else 6
per = int(sys.argv[2]) if len(sys.argv) > 2 else 40
seeds = [int(s) for s in (sys.argv[3].split(",") if len(sys.argv) > 3 else ["0"])]
novel = len(sys.argv) > 4 and sys.argv[4] == "novel"
outname = "crossing_results_novel.json" if novel else "crossing_results.json"
t0 = time.time()
report = {"novel": novel, "generations": gens, "per_gen": per, "seeds": seeds, "runs": [], "frontier": {}}
optimal = {}
for sd in seeds:
    out = X.run(generations=gens, per_gen=per, seed=sd, log=lambda s: print(s, flush=True), novel=novel)
    run = {"seed": sd, "arms": {}}
    for arm, d in out["arms"].items():
        cols = d["colourings"]
        run["arms"][arm] = {"per_gen": d["per_gen"], "survivors": len(d["survivors"]),
                            "distinct_colourings": len(cols),
                            "distinct_optimal": sum(r.score == 0 for r in cols)}
        for r in cols:
            if r.score == 0:
                k = X.phenotype(r.genome)
                optimal.setdefault(k, {"genome": r.genome, "arms": set()})["arms"].add(arm)
    report["runs"].append(run)
    json.dump(report, open(os.path.join(here, outname), "w"), indent=1, default=str)

fm = X.FindMono(os.path.join(here, "..", "erdos1183", "findmono4k"), timeout=120)
rows = []
for k, o in optimal.items():
    g, row = o["genome"], {"genome": repr(o["genome"]), "provenance": X.provenance(o["genome"]),
                           "arms": sorted(o["arms"]), "level": X.is_level(o["genome"]), "m": {}}
    for n in range(10, 15):
        if row["level"]:
            c, pc = X.colouring(g, n), X.popcounts(n)
            pat = [int(c[pc == j][0]) for j in range(n + 1)]
            row["pattern_" + str(n)] = "".join(map(str, pat))
            row["m"][n] = levelmono.maxmono(pat, X.f_exact(n) + 2)
        elif n <= 12:
            row["m"][n] = fm.maxmono(n, X.red_mask(g, n), X.f_exact(n) + 2)
    rows.append(row)
    print("frontier", row["provenance"], row["arms"], row["level"], row["m"], flush=True)
fm.close()
report["frontier"] = {"chain_bound": {n: X.f_exact(n) for n in range(10, 15)}, "colourings": rows}
json.dump(report, open(os.path.join(here, outname), "w"), indent=1, default=str)
print(f"done in {time.time() - t0:.0f}s", flush=True)
