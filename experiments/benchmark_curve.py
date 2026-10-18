"""Run the Hodge and Yang-Mills benchmark under five policies and record the learning curve.

    python experiments/benchmark_curve.py [MODEL.gguf] --seeds 200 --out benchmark_curve.json

Policies: uniform (every untried move equally likely), router-openai (the corpus prior of the
Lean-formalised OpenAI manuscripts), router (that prior averaged with the Lean-solved share of the
settled Erdos problems using each move; both routers are potentiated by accepted steps and
depressed by failures), model (the language model's profile over the eight moves alone) and bllm (router and model mixed with weight 1/2).  The
model's profile at a node is the softmax of its next-token logits over the letters A-H of the moves,
computed once per node.  For each seed the curve records the attempt at which each accepted step was
first found and the number of attempts spent on moves with no checkable formulation at their node.
The state of the BLLM-led run of seed 1 and its Obsidian vault are written next to the output.
"""
import argparse, json, os, random, statistics, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from ebllm.bllm import benchmark as bm
from ebllm.bllm.corpus import MOVES

HERE = os.path.dirname(os.path.abspath(__file__))
DESCRIBE = {
    "reduction": "reduce it to a known theorem or a simpler statement",
    "lift": "prove a special case and lift or deform it",
    "certificate": "find one explicit object whose finite checks imply it",
    "construction": "construct the required object explicitly",
    "counterexample": "look for a counterexample",
    "flow-surgery": "run a geometric flow and repair singularities",
    "descent": "infinite descent or induction on a size",
    "physics-first": "take the answer from physics and then prove it",
}
LET = "ABCDEFGH"


def prompt(node):
    opts = "\n".join(f"{LET[i]}. {DESCRIBE[m]}" for i, m in enumerate(MOVES))
    return ("Mathematics problem: " + node.statement + ".\nWhich strategy is most likely to make "
            "checkable progress?\n" + opts + "\nAnswer with one letter.\nAnswer:")


def run(policy, seed, cfg, stats, profile, harvest=None):
    b = bm.Benchmark.new(stats, None if policy == "router-openai" else harvest)
    rng = random.Random(seed)
    uniform = lambda node, moves: [1.0 / len(moves)] * len(moves)
    model = lambda node, moves: profile.get(node.statement, [1.0 / len(moves)] * len(moves))
    kw = {"uniform": dict(mix=uniform, lam=1.0), "router": {}, "router-openai": {}, "model": dict(mix=model, lam=1.0),
          "bllm": dict(mix=model, lam=0.5)}[policy]
    found, wasted, n = {}, 0, 0
    while not b.exhausted() and b.round < 60:
        b.step(cfg, rng, **kw)
    for i, a in enumerate([a for a in b.attempts if a.round > 0], 1):
        if a.outcome == "accepted" and a.node not in found:
            found[a.node] = i
        if "no checkable formulation" in a.residual:
            wasted += 1
        n = i
    return dict(found=found, wasted=wasted, attempts=n, rounds=b.round), b


ap = argparse.ArgumentParser()
ap.add_argument("model", nargs="?")
ap.add_argument("--seeds", type=int, default=200)
ap.add_argument("--out", default=os.path.join(HERE, "benchmark_curve.json"))
args = ap.parse_args()
stats = json.load(open(os.path.join(HERE, "..", "src", "ebllm", "bllm", "data", "solution_moves.json")))
harvest = json.load(open(os.path.join(HERE, "..", "src", "ebllm", "bllm", "data", "erdos_harvest.json")))
cfg = {"fermat_max": 36, "registry": os.environ.get("LEAN_MILLENNIUM")}
profile = {}
if args.model:
    from ebllm.bllm.brain import LocalBrain
    brain = LocalBrain(args.model)
    tree = bm.build_tree()
    extra = ["X^4_110: the class 2_* xi_55 left by the census and its Galois conjugates",
             "a finite-box gauge-invariant mixing certificate at one coupling in the window",
             "a lift of the two-dimensional gap through a family of theories interpolating in dimension"]
    stmts = [n.statement for n in tree.values()] + extra
    b0 = bm.Benchmark.new(stats, harvest)
    while not b0.exhausted() and b0.round < 60:
        b0.step(cfg, random.Random(0))
    stmts = sorted(set(stmts) | {n.statement for n in b0.tree.values()})
    for s in stmts:
        profile[s] = brain.letter_profile(prompt(bm.Node("x", "", s)), LET)
out = {"model": os.path.basename(args.model) if args.model else None, "profile": profile, "policies": {}}
for pol in (["uniform", "router-openai", "router"] + (["model", "bllm"] if profile else [])):
    rows = [run(pol, s, cfg, stats, profile, harvest)[0] for s in range(1, args.seeds + 1)]
    steps = sorted({k for r in rows for k in r["found"]})
    summ = {"seeds": len(rows), "attempts_mean": statistics.mean(r["attempts"] for r in rows),
            "wasted_mean": statistics.mean(r["wasted"] for r in rows),
            "rounds_mean": statistics.mean(r["rounds"] for r in rows)}
    for st in steps:
        xs = [r["found"].get(st) for r in rows]
        summ["first_" + st] = {"mean": statistics.mean(x for x in xs if x), "found_in": sum(1 for x in xs if x)}
    both = [max(r["found"].values()) for r in rows if len(r["found"]) == len(steps)]
    summ["both_mean"] = statistics.mean(both)
    out["policies"][pol] = summ
    print(pol, json.dumps(summ), flush=True)
res, b = run("bllm" if profile else "router", 1, cfg, stats, profile, harvest)
b.save(os.path.join(HERE, "benchmark_state.json"))
b.write_vault(os.path.join(HERE, "vault"))
out["report"] = b.report()
json.dump(out, open(args.out, "w"), indent=1)
print("saved", args.out)
