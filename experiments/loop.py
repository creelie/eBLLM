"""The continuous attack loop: target point -> channel bundle -> attack by all proposers -> refuter
(and Lean for any new statement) -> boosters and memory -> next round, for five autonomous agents, one
per target point, against the single-loop control (one attack over all five libraries, no channel,
no target weights).  Checkpoints every round to experiments/loop/ and refreshes the handoff state.

    python3 experiments/loop.py [rounds] [--llm]       (stops early if experiments/loop/STOP exists)
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
from ebllm.bllm import superbrain as S, attackflow as A  # noqa: E402
from ebllm.bllm.memory import Memory  # noqa: E402

args = [a for a in sys.argv[1:] if not a.startswith("--")]
ROUNDS = int(args[0]) if args else 100
BASE = os.environ.get("EBLLM_RUN_DIR", HERE)
OUT = os.path.join(BASE, "loop")
os.makedirs(OUT, exist_ok=True)
os.makedirs(os.path.join(BASE, "memory"), exist_ok=True)
mem = Memory(os.path.join(BASE, "memory", "loop.sqlite"))
ctl_mem = Memory(None)
llm = S.LocalModel() if "--llm" in sys.argv else None
agents = [A.TargetAgent(b, mem) for b in A.TARGET_POINTS]
ctl_w, ctl_known = {}, set()
state_path = os.path.join(OUT, "state.json")
hist = json.load(open(state_path))["rounds"] if os.path.exists(state_path) else []
start = len(hist)
for r in range(start + 1, start + ROUNDS + 1):
    if os.path.exists(os.path.join(OUT, "STOP")):
        break
    t = time.time()
    rows = [a.step(r, seed=r * 31 + i, llm=llm) for i, a in enumerate(agents)]
    trades = {a.bench: a.trade([o for o in agents if o is not a]) for a in agents}
    ctl = S.attack("boosted", memory=None, weights=ctl_w, seed=r * 31, round_=r, generations=6, per_gen=40)
    ctl_w = ctl["weights"]
    ctl_known |= set(ctl["survivors"])
    mem.commit()
    sc = S.scores()
    passed = [a.bench for a in agents if any(h["target_reached"] for h in a.history)]
    rec = dict(round=r, time=time.strftime("%H:%M:%S", time.gmtime()), seconds=round(time.time() - t, 2),
               agents=rows, trades=trades,
               agents_total=dict(checks=sum(x["checks"] + x.get("sub", {}).get("checks", 0) for x in rows),
                                 known=sum(x["known"] for x in rows)),
               control=dict(checks=ctl["checks"], known=len(ctl_known)),
               target_points_reached=passed, passed=[s["benchmark"] for s in sc if s["passed"]])
    hist.append(rec)
    json.dump(dict(rounds=hist, memory=mem.stats(), scores=sc,
                   target_points={k: v[2] for k, v in A.TARGET_POINTS.items()},
                   distances={a.bench: a.dist for a in agents}), open(state_path, "w"), indent=1, default=str)
    print(json.dumps(dict(round=r, agents=rec["agents_total"], control=rec["control"], passed=rec["passed"],
                          reached=passed)), flush=True)
    if rec["passed"]:
        open(os.path.join(OUT, "PASSED"), "w").write(json.dumps(rec["passed"]))
