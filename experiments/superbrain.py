"""The five-benchmark test, run by the whole package with memory on and off.

    python3 experiments/superbrain.py [seeds] [rounds] [--llm]

Arms (each over the same seeds and rounds):
  full            boosters, long-term memory, retrieval before every attack, the proposer committee
  full-noretrieve boosters and memory (decided composites are skipped), no retrieval steering
  boosted         boosters carried between rounds, no memory
  unboosted       uniform over typed crossings, nothing carried
  random          uniform over all pairs
  full+llm        as full, with the local open-weight model in the committee (--llm, fewer seeds)

Per round: checks, checks spent on composites already decided in an earlier round of the same seed
(wasted), new distinct survivors, cumulative distinct survivors, refuted, and the share of runs that
reach the candidate range beta_W < 1/3.  The persistent store of the seed-0 full run is written to
experiments/memory/brain.sqlite; everything else to experiments/superbrain/.
"""
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
from ebllm.bllm import superbrain as S  # noqa: E402
from ebllm.bllm.memory import Memory  # noqa: E402

args = [a for a in sys.argv[1:] if not a.startswith("--")]
SEEDS = int(args[0]) if args else 60
ROUNDS = int(args[1]) if len(args) > 1 else 5
OUT = os.path.join(HERE, "superbrain")
os.makedirs(OUT, exist_ok=True)
STORE = os.path.join(HERE, "memory", "brain.sqlite")

ARMS = [("full", dict(arm="full", memory=True, retrieval=True)),
        ("full-noretrieve", dict(arm="full", memory=True, retrieval=False)),
        ("boosted", dict(arm="boosted", memory=False)),
        ("unboosted", dict(arm="unboosted", memory=False)),
        ("random", dict(arm="random", memory=False))]
llm = None
if "--llm" in sys.argv:
    llm = S.LocalModel()
    if llm.model is not None:
        ARMS.append(("full+llm", dict(arm="full", memory=True, retrieval=True, llm=True)))


def run_arm(name, spec, seeds):
    rows = [dict(round=r + 1, checks=0, wasted=0, new=0, cum=0, refuted=0, hit=0, llm_calls=0) for r in range(ROUNDS)]
    for s in range(seeds):
        if spec.get("memory"):
            path = STORE if (name == "full" and s == 0) else None
            if path and os.path.exists(path):
                os.remove(path)
            mem = Memory(path)
        else:
            mem = None
        w, decided, known = {}, set(), set()
        for r in range(ROUNDS):
            rec = S.attack(spec["arm"], memory=mem, weights=w, seed=1000 * r + s, round_=r + 1,
                           retrieval=spec.get("retrieval", True), llm=llm if spec.get("llm") else None)
            if spec["arm"] in ("full", "boosted"):
                w = rec["weights"]
            # wasted: composites checked again although a previous round of this seed decided them
            seqs = rec.get("checked_seqs", [])
            rows[r]["wasted"] += sum(1 for q in seqs if q in decided) / seeds
            decided.update(seqs)
            new = set(rec["survivors"]) - known
            known |= new
            rows[r]["checks"] += rec["checks"] / seeds
            rows[r]["new"] += len(new) / seeds
            rows[r]["cum"] += len(known) / seeds
            rows[r]["refuted"] += len(rec["refuted"]) / seeds
            rows[r]["hit"] += ("YM.window.lower" in rec["first"]) / seeds
            rows[r]["llm_calls"] += rec["llm_calls"] / seeds
        if mem is not None and name == "full" and s == 0:
            json.dump(mem.export(), open(os.path.join(OUT, "memory_export.json"), "w"), indent=1, default=str)
            json.dump(mem.stats(), open(os.path.join(OUT, "memory_stats.json"), "w"), indent=1)
    for x in rows:
        x["hit_se"] = round(math.sqrt(x["hit"] * (1 - x["hit"]) / seeds), 4)
        x["cum_per_check"] = round(x["cum"] / max(1e-9, sum(y["checks"] for y in rows[:x["round"]])), 4)
        for k in ("checks", "wasted", "new", "cum", "refuted", "hit", "llm_calls"):
            x[k] = round(x[k], 4)
    return rows


t0 = time.time()
result = dict(seeds=SEEDS, rounds=ROUNDS, arms={})
for name, spec in ARMS:
    n = min(SEEDS, 8) if spec.get("llm") else SEEDS
    result["arms"][name] = dict(seeds=n, rows=run_arm(name, spec, n))
    print(name, json.dumps(result["arms"][name]["rows"][-1]), flush=True)
sc = S.scores()
result.update(scores=sc, superbrain=S.superbrain(sc), seconds=round(time.time() - t0, 1),
              time=time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime()))
json.dump(result, open(os.path.join(OUT, "round.json"), "w"), indent=1, default=str)
hist = os.path.join(OUT, "history.json")
h = json.load(open(hist)) if os.path.exists(hist) else []
h.append(dict(time=result["time"], seeds=SEEDS, rounds=ROUNDS,
              final={k: v["rows"][-1] for k, v in result["arms"].items()},
              passed=result["superbrain"]["passed"]))
json.dump(h, open(hist, "w"), indent=1)
print(json.dumps(result["superbrain"]))
