"""The Hodge-only attack loop: five agents, one per target point of Bhattacharjee-Bhattacharya 2026
(doi:10.5281/zenodo.23439578), each round = channel bundle -> attack by all proposers -> refuter ->
boosters and memory -> gap measurement.  Checkpoints every round to the run directory and refreshes
HANDOFF.md there.

    EBLLM_RUN_DIR=/mnt/project-files/ai-paper/hodge-attack python3 experiments/hodge_loop.py [rounds] [--llm]
    (stops early if <run dir>/STOP exists)
"""
import json, os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "src"))
from ebllm.bllm import superbrain as S, hodge as H  # noqa: E402
from ebllm.bllm.memory import Memory  # noqa: E402

args = [a for a in sys.argv[1:] if not a.startswith("--")]
ROUNDS = int(args[0]) if args else 10
OUT = os.environ.get("EBLLM_RUN_DIR", os.path.join(HERE, "hodge"))
os.makedirs(os.path.join(OUT, "rounds"), exist_ok=True)
H.install()
mem = Memory(os.path.join(OUT, "memory", "hodge.sqlite"))
llm = S.LocalModel() if "--llm" in sys.argv else None
agents = [H.HodgeAgent(t, mem) for t in H.TARGETS]
state_path = os.path.join(OUT, "state.json")
hist = json.load(open(state_path))["rounds"] if os.path.exists(state_path) else []
start = len(hist)
for r in range(start + 1, start + ROUNDS + 1):
    if os.path.exists(os.path.join(OUT, "STOP")):
        break
    t = time.time()
    rows = [a.step(r, seed=r * 31 + i, llm=llm, generations=6, per_gen=10) for i, a in enumerate(agents)]
    mem.commit()
    survivors = {}
    for s, o, n, reason, seq in mem.db.execute(
            "SELECT statement, outcome, node, reason, seq FROM events WHERE round = ? AND outcome = 'accepted'", (r,)):
        survivors[seq] = dict(node=n, statement=s[:200], reason=reason)
    stopped = mem.db.execute("SELECT COUNT(*) FROM events WHERE round = ? AND outcome = 'stopped'", (r,)).fetchone()[0]
    rejected = mem.db.execute("SELECT COUNT(*) FROM events WHERE round = ? AND outcome = 'rejected'", (r,)).fetchone()[0]
    refuted = mem.db.execute("SELECT COUNT(*) FROM events WHERE round = ? AND survived = 0", (r,)).fetchone()[0]
    new_nonknown = [v for v in survivors.values() if "known" not in v["reason"]]
    rec = dict(round=r, time=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), seconds=round(time.time() - t, 2),
               agents=rows, gaps=[a.gap() for a in agents], survivors=survivors, stopped=stopped, rejected=rejected,
               refuted=refuted, new_non_known_survivors=new_nonknown,
               target_points_reached=[a.target for a in agents if any(h["target_reached"] for h in a.history)],
               f2_moved=False, f3prime_moved=False)
    hist.append(rec)
    json.dump(rec, open(os.path.join(OUT, "rounds", f"round_{r:03d}.json"), "w"), indent=1, default=str)
    json.dump(dict(rounds=hist, memory=mem.stats(), targets=H.TARGETS,
                   distances={a.target: a.dist for a in agents}), open(state_path, "w"), indent=1, default=str)
    print(json.dumps(dict(round=r, checks=sum(x["checks"] for x in rows), survivors=len(survivors),
                          new_non_known=len(new_nonknown), stopped=stopped, rejected=rejected, refuted=refuted,
                          reached=rec["target_points_reached"])), flush=True)
    if rec["target_points_reached"] or new_nonknown:
        open(os.path.join(OUT, "ATTENTION"), "a").write(json.dumps(rec, default=str) + "\n")
