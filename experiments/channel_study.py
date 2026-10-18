"""Channel on against channel off: five target agents per seed, with the attack channel and target weights,
with target weights only, and with neither, each over the same rounds and seeds, without the local model.

    python3 experiments/channel_study.py [seeds] [rounds]
Writes experiments/channel/study.json.
"""
import gc, json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
from ebllm.bllm import attackflow as A  # noqa: E402
from ebllm.bllm.memory import Memory  # noqa: E402

seeds = int(sys.argv[1]) if len(sys.argv) > 1 else 20
rounds = int(sys.argv[2]) if len(sys.argv) > 2 else 5
ARMS = {"channel+target": (True, True), "target only": (False, True), "neither": (False, False)}
out = {a: [] for a in ARMS}
t0 = time.time()
for arm, (ch, tw) in ARMS.items():
    for s in range(seeds):
        mem = Memory(None)
        agents = [A.TargetAgent(b, mem, channel=ch, target_weight=tw) for b in A.TARGET_POINTS]
        rows = []
        for r in range(1, rounds + 1):
            st = [a.step(r, seed=1000 * s + r * 31 + i) for i, a in enumerate(agents)]
            rows.append(dict(round=r, checks=sum(x["checks"] + x.get("sub", {}).get("checks", 0) for x in st),
                             known=sum(x["known"] for x in st), refuted=sum(x["refuted"] for x in st),
                             reached=any(x["target_reached"] for x in st)))
        out[arm].append(rows)
        mem.db.close()
        del agents, mem
        gc.collect()
    print(arm, round(time.time() - t0, 1), flush=True)
summary = {}
for arm, runs in out.items():
    summary[arm] = [dict(round=r + 1,
                         checks=sum(run[r]["checks"] for run in runs) / len(runs),
                         known=sum(run[r]["known"] for run in runs) / len(runs),
                         refuted=sum(run[r]["refuted"] for run in runs) / len(runs),
                         reached=sum(run[r]["reached"] for run in runs)) for r in range(rounds)]
BASE = os.environ.get("EBLLM_RUN_DIR", HERE)
os.makedirs(os.path.join(BASE, "channel"), exist_ok=True)
json.dump(dict(seeds=seeds, rounds=rounds, summary=summary, runs=out, seconds=round(time.time() - t0, 1)),
          open(os.path.join(BASE, "channel", "study.json"), "w"), indent=1)
for arm, rows in summary.items():
    print(arm, json.dumps(rows[-1]), "total checks", round(sum(r["checks"] for r in rows), 1))
