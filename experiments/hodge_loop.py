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
BURST = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--burst=")), 0)  # every BURST-th round


def long_chains(mem, round_, seed, tries=300, depth=(3, 6)):
    """Random chains of three to six library nodes fed into one another (the 'explosion'): every typed
    chain not yet decided is checked and recorded with its verdict."""
    import random
    from ebllm.bllm.targets import cross
    rng = random.Random(seed)
    lib = list(H.LIB)
    out = dict(tried=tries, checked=0, survivors=0, rejected=0, stopped=0)
    for _ in range(tries):
        c = rng.choice(lib)
        for _ in range(rng.randint(*depth) - 1):
            nxt = cross(c, rng.choice(lib))
            if nxt is None:
                break
            c = nxt
        if len(c.parts) < 3 or mem.decided(c.parts):
            continue
        chk = H.check_hodge(c)
        out["checked"] += 1
        out[chk.outcome if chk.outcome in out else "stopped"] += 1
        if chk.outcome == "accepted":
            out["survivors"] += 1
        mem.record(c.parts, c.problem, chk.outcome, node=chk.node, statement=chk.statement,
                   reason=json.dumps(chk.measurement, default=str)[:400], survived=chk.outcome == "accepted",
                   round_=round_, arm="burst", proposer="long-chain")
    return out
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
    burst = BURST and r % BURST == 0
    if burst:
        # burst: a short high-volume round, many pairings at once and long random chains, refuter pruning as usual
        rows = [a.step(r, seed=r * 31 + i, llm=llm, generations=10, per_gen=40) for i, a in enumerate(agents)]
        chains = long_chains(mem, r, seed=r)
    else:
        rows = [a.step(r, seed=r * 31 + i, llm=llm, generations=6, per_gen=10) for i, a in enumerate(agents)]
        chains = dict(tried=0, checked=0, survivors=0)
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
               mode="burst" if burst else "steady", chains=chains, agents=rows, gaps=[a.gap() for a in agents], survivors=survivors, stopped=stopped, rejected=rejected,
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
