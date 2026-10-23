"""Command line, installed as `anaxia` (the engine's name) and as `ebllm`.

The VSI circuit: `anaxia controls`, `scan`, `axioms`, `counterexamples`, `run`.
BLLM: `anaxia demo`, `schedule`, `tasks`, `attack`, `gap`, `bridge`, `brain`, `providers`.
The image: `anaxia update` says whether a newer image is published on ghcr.io.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from fractions import Fraction

from . import __version__


def _verifier_from_spec(spec):
    from .verifiers import CommandVerifier, LeanAxiomVerifier
    if isinstance(spec, int):
        return spec
    if "cmd" in spec:
        return CommandVerifier(spec["cmd"], spec.get("expect"), spec.get("cwd"))
    if "lean" in spec:
        L = spec["lean"]
        return LeanAxiomVerifier(L["project"], L["imports"], L["theorems"])
    raise ValueError(f"unknown verifier spec {spec!r}")


def cmd_controls(args) -> int:
    from .controls import load_controls, table
    cs = load_controls()
    if args.json:
        print(json.dumps([dict(slug=c.slug, name=c.name, group=c.group, label=c.label.value,
                               blocking=c.blocking) for c in cs], indent=2))
    else:
        print(table(cs))
    return 0


def cmd_scan(args) -> int:
    from .verifiers.lean import scan_lean_sources
    hits = scan_lean_sources(args.paths, exclude=args.exclude)
    bad = 0
    for k, v in hits.items():
        print(f"{k:28s} {len(v)}")
        for line in v[:5]:
            print("    " + line)
        bad += len(v)
    print("scan: clean" if bad == 0 else "scan: FOUND ITEMS ABOVE")
    return 1 if bad else 0


def cmd_axioms(args) -> int:
    from .verifiers.lean import parse_axioms
    text = open(args.log, encoding="utf-8").read()
    reports = parse_axioms(text)
    ok = True
    for r in reports:
        extra = sorted(r.axioms - {"propext", "Classical.choice", "Quot.sound"})
        print(f"{r.theorem}: {sorted(r.axioms) or 'no axioms'}" + (f"  EXTRA {extra}" if extra else ""))
        ok &= not extra
    if args.expected is not None and len(reports) != args.expected:
        print(f"expected {args.expected} reports, found {len(reports)}")
        ok = False
    if "error" in text.lower() or "sorry" in text.lower():
        print("the log mentions an error or sorry")
        ok = False
    print("axioms: OK" if ok else "axioms: FAILED")
    return 0 if ok else 1


def cmd_counterexamples(args) -> int:
    from .playbook import Bullet, collapse_paper, collapse_v11
    from .sandtile import counterexample_conservative, counterexample_dissipative
    from .scope import compose, counterexample_superadditivity, loss
    st, h = counterexample_conservative()
    r = st.stabilize(h, max_topples=10000)
    print("Theorem 10.4 / Proposition 10.2, conservative: two sites, heights (1, 1), theta 1/2, Delta 1:")
    print(f"  bound {st.bound_theorem_10_4(h)}; stabilized within 10000 topplings: {r is not None}")
    st, h = counterexample_dissipative(Fraction(1, 100))
    hf, n, absorbed = st.stabilize(h)
    print("Theorem 10.4, dissipative: heights (2, 2), theta 1, Delta 2, share 99/100:")
    print(f"  bound {st.bound_theorem_10_4(h)}; topplings needed {n}")
    f, g = counterexample_superadditivity()
    print("Lemma 6.2: f = [0], g = [0, lost]:")
    print(f"  loss(f) = {loss(f)}, loss(g) = {loss(g)}, loss(g o f) = {loss(compose(g, f))} "
          f"< loss(f) + loss(g) = {loss(f) + loss(g)}")
    old = [Bullet("a", "formal", "gap a", "FAIL"), Bullet("b", "formal", "gap b", "FAIL")]
    new = [Bullet("a", "formal", "gap a", "PASS", "PASS"), old[1]]
    print("Collapse guard: resolving one of two core failures:")
    print(f"  paper Collapse = {collapse_paper(old, new)} (rejected for theta < 1/2), "
          f"v1.1 Collapse = {collapse_v11(old, new)}")
    return 0


def cmd_run(args) -> int:
    from .engine import Engine, Proposal
    from .ledger import contract_report
    from .obligations import ObligationGraph
    from .package import ConjecturePackage
    from .playbook import Playbook
    spec = json.load(open(args.spec, encoding="utf-8"))
    g = ObligationGraph()
    eng = Engine(ConjecturePackage.from_dict(spec["package"]), g,
                 {k: _verifier_from_spec(v) for k, v in spec.get("verifiers", {}).items()},
                 Playbook(theta=Fraction(spec.get("theta", 0))), root=spec.get("root", "main"),
                 kind=spec.get("kind", "proof"))
    prop = Proposal(obligations=spec.get("obligations", []),
                    bridges=[tuple(b) for b in spec.get("bridges", [])],
                    checks={k: _verifier_from_spec(v) for k, v in spec.get("checks", {}).items()},
                    model_ok=spec.get("model_ok", False))
    rec = eng.step(0, prop)
    print(contract_report(eng))
    if args.ledger:
        open(args.ledger, "w", encoding="utf-8").write(eng.ledger.dumps())
    return 0 if rec["label"] in ("THEOREM", "COUNTEREXAMPLE", "INDEPENDENCE") else 2


def cmd_demo(args) -> int:
    from .bllm.agents import DEMO_PROBLEMS, LEAN_PROBLEMS, default_agents
    from .bllm.checks import LeanCheck
    from .bllm.coordinator import Coordinator
    problems = list(DEMO_PROBLEMS) + (list(LEAN_PROBLEMS) if args.lean else [])
    co = Coordinator(default_agents(lean=args.lean), theta=args.theta,
                     lean=LeanCheck() if args.lean else None,
                     selector="spiking" if args.spiking else None)
    res = co.run(problems, mode=args.mode, rounds=args.rounds)
    print(f"mode {res.mode}: {len(res.solved)} of {len(problems)} problems closed in {res.rounds} rounds")
    print(f"{'agent':16s} {'proposed':>8s} {'kept':>5s} {'weak-rej':>8s} {'exact-rej':>9s} {'cost':>10s}")
    for name, st in res.stats.items():
        print(f"{name:16s} {st.proposed:8d} {st.kept:5d} {st.weak_rejected:8d} {st.strong_rejected:9d} {st.cost:10.1f}")
    print(f"total cost {res.total_cost:.1f}; exact checks alone would cost {res.strong_only_cost:.1f}")
    if res.mode == "certified":
        print(f"false-acceptance bound used {res.false_bound:.2e} of theta = {res.theta:g}; "
              f"observed false acceptances {sum(s.false_accepts for s in res.stats.values())}")
        print(f"schedule cost {res.schedule_cost:.1f} in [{res.schedule_lower:.1f}, {res.schedule_upper:.1f}] (Theorem A)")
    for pid, cid in res.solved.items():
        n = res.vault.notes[cid]
        print(f"  {pid}: {n.get('lhs', '')} = {n.get('rhs', '')}  [{n['move']}]")
    if args.vault:
        print("memory written to", res.vault.write(args.vault))
    return 0


def cmd_schedule(args) -> int:
    from .bllm.schedules import ceiling_schedule, cost, entropy_bounds, false_acceptance_bound
    costs = [float(x) for x in args.costs.split(",")]
    runs = ceiling_schedule(costs, args.eps, args.theta)
    lo, hi = entropy_bounds(costs, args.eps, args.theta)
    print("runs", runs)
    print(f"cost {cost(costs, runs):.4g} in [{lo:.4g}, {hi:.4g}]; false-acceptance bound "
          f"{false_acceptance_bound(runs, args.eps):.3g} <= theta = {args.theta:g}")
    return 0


def cmd_tasks(args) -> int:
    from .bllm.tasks import load_tasks, summary
    print(summary(load_tasks()))
    return 0


def cmd_attack(args) -> int:
    from .bllm.tasks import attack_plan, load_tasks
    t = load_tasks()
    if args.task not in t:
        print("known tasks:", ", ".join(t))
        return 2
    print(attack_plan(t[args.task]))
    return 0


def cmd_gap(args) -> int:
    from .bllm.gap import format_table, idea_gap_table, load_idea_gap
    d = load_idea_gap(args.data)
    for ax in ([args.axis] if args.axis else list(d["axes"])):
        print(format_table(idea_gap_table(ax, d), ax))
        print()
    print("source:", d["source"])
    return 0


def cmd_bridge(args) -> int:
    from .bllm.gap import (bridge_simulation, load_idea_gap, mix, optimal_cost, optimal_profile,
                           search_cost)
    d = load_idea_gap()
    pi, q = d["shares"]["Human"][args.axis], d["shares"][args.model][args.axis]
    out = bridge_simulation(pi, q, problems=args.problems, lam=args.lam, window=args.window, seed=args.seed)
    print(f"{args.model}, {args.axis} axis: draws per problem, by windows of {args.window} problems")
    for k, v in out.items():
        print(f"  {k:8s} " + " ".join(f"{x:6.2f}" for x in v))
    r = optimal_profile(pi)
    print(f"law: LLM {search_cost(pi, q):.2f}; BLLM with lam = {args.lam} tends to "
          f"{search_cost(pi, mix(q, r, args.lam)):.2f}; optimum {optimal_cost(pi):.2f}")
    return 0


def cmd_brain(args) -> int:
    from .bllm import neuro
    if args.kind == "worm":
        g = neuro.load_edge_list(args.path)
    elif args.kind == "fly":
        g = neuro.load_flywire_neuropils(args.path)
    else:
        somas = neuro.load_h01_somas(args.path)
        from collections import Counter
        print(f"{len(somas)} somas")
        for (k, v) in Counter((s["layer"], s["celltype"]) for s in somas).most_common(args.top):
            print(f"  {k[0]:12s} {k[1]:14s} {v}")
        return 0
    win, wout = g.degrees()
    z = g.processing_depth()
    print(f"{len(g.nodes)} nodes, {len(g.edges)} weighted edges, total weight {sum(g.edges.values()):.0f}")
    order = sorted(range(len(g.nodes)), key=lambda i: z[i])
    print("lowest processing depth (closest to the inputs):", ", ".join(g.nodes[i] for i in order[:args.top]))
    print("highest processing depth:", ", ".join(g.nodes[i] for i in order[-args.top:]))
    if args.reservoir:
        mc = neuro.memory_capacity(neuro.Reservoir(g))
        print("memory of a reservoir wired like it:", ", ".join(f"delay {k}: {v:.2f}" for k, v in mc.items()))
    return 0


def cmd_providers(args) -> int:
    from .bllm.proposers import PROVIDERS, available
    have = set(available())
    for p, s in PROVIDERS.items():
        print(f"{p:11s} {'ready' if p in have else 'set ' + s['key']:28s} {s['url']}")
    return 0


def cmd_fetch(args) -> int:
    from .bllm import deepmind as D
    rows = D.pins()
    if args.list or not (args.names or args.all):
        for r in D.manifest():
            if r.get("commit"):
                print(f"{r['name']:38s} {r['tag']:8s} {r['commit'][:12]}  {r['licence']:10s} {r['why']}")
        return 0
    names = sorted(n for n, r in rows.items() if r["tag"] == "vendor") if args.all else args.names
    for n in names:
        print(D.fetch(n, args.root))
    return 0


def cmd_intake(args) -> int:
    from .bllm import deepmind as D
    if args.rebuild:
        D.write_index(D.build_index(args.rebuild))
    if args.search:
        for h in D.search(args.search, args.k, source=args.source, status=args.status):
            print(f"{h['score']:7.3f}  {h['source']:28s} {h['status']:14s} {h['name']}")
            print(f"         {h['statement'][:150]}")
            print(f"         {h['link']}")
        return 0
    if args.memory:
        from .bllm.memory import Memory
        print(json.dumps(D.load_into_memory(Memory(args.memory))))
        return 0
    for src, c in sorted(D.summary().items()):
        print(f"{src:38s} " + ", ".join(f"{v} {k}" for k, v in sorted(c.items())))
    return 0


def cmd_sources(args) -> int:
    from .bllm import sources as S
    if args.action == "list":
        print(S.table())
        return 0
    if args.action == "show":
        for sid in args.text:
            print(json.dumps(S.get(sid), indent=1, ensure_ascii=False))
        return 0
    if args.action == "build":
        if args.openrefute:
            print(S.write_index(S.index_openrefute(args.openrefute)))
        if args.openai:
            print(S.write_index(S.index_openai(args.openai)))
        return 0
    if args.action == "summary":
        for src, c in sorted(S.summary(S.load_external()).items()):
            print(f"{src:14s} " + ", ".join(f"{v} {k}" for k, v in sorted(c.items())))
        return 0
    for h in S.check(" ".join(args.text), args.k, source=args.source, status=args.status):
        print(f"{h['score']:7.3f}  {h['source']:28s} {h['status']:14s} {h['name'][:80]}")
        print(f"         {h['statement'][:150]}")
        print(f"         {h['link']}")
    return 0


CONSTRUCT_TOOLS = {
    "build": "proof_builder", "assemble": "assemble", "cegar": "cegar_forcer", "book": "cegar_book",
    "hub": "cegar_hub", "algebra": "gadget_algebra", "steinberg": "steinberg_rebuild", "g1prime": "g1prime",
    "tower": "tower", "bench": "bench", "seed-intervals": "seed_intervals",
}


def cmd_construct(args) -> int:
    import importlib
    from . import construct as C
    rest = list(args.rest)
    if args.tool == "list":
        from .construct import graphcheck as gc
        for name in C.GADGETS:
            G, contacts = C.gadget(name)
            r = gc.report(G, contacts, "NAE", cyc_hi=7)
            print(f"{name:18s} n={r['n']:<3d} m={r['m']:<3d} cycles<=7 {r['cycles_<=7']}  "
                  f"distances {sorted(r['dist'].values())}  forces NAE {r['forces_NAE']}")
        return 0
    if args.tool == "check":
        from .construct import graphcheck as gc
        ap = argparse.ArgumentParser(prog="anaxia construct check")
        ap.add_argument("gadget", help="a stored gadget name (anaxia construct list) or a json file with edges")
        ap.add_argument("--forbid-max", type=int, default=6)
        a = ap.parse_args(rest)
        if os.path.exists(a.gadget):
            with open(a.gadget) as f:
                d = json.load(f)
            import networkx as nx
            G = nx.Graph(); contacts = d.get("contacts", [0, 1, 2])
            G.add_nodes_from(contacts); G.add_edges_from(tuple(e) for e in d["edges"])
        else:
            G, contacts = C.gadget(a.gadget)
        kind = "NAE" if len(contacts) == 3 else "NEQ"
        print(gc.report(G, contacts, kind, cyc_hi=a.forbid_max + 1))
        return 0
    # stored gadgets may be named instead of given as files where a tool reads gadget files
    rest = [os.path.join(C.DATA, r + ".json") if r in C.GADGETS and not os.path.exists(r) else r for r in rest]
    importlib.import_module(f".construct.{CONSTRUCT_TOOLS[args.tool]}", "ebllm").main(rest)
    return 0


def cmd_modlog(args) -> int:
    from .bllm import selfmod as S
    runs = S.load_log(args.log)
    errors = S.check_log(runs)
    if args.json:
        out = {run: dict(records=[r.as_dict() for r in recs], patterns=S.patterns(recs)) for run, recs in runs.items()}
        out["errors"] = errors
        print(json.dumps(out, indent=1))
        return 1 if errors else 0
    for line in S.summary(runs):
        print(line)
    if args.patterns:
        for run, recs in runs.items():
            p = S.patterns(recs)
            print(f"\n{run}: failure kind x rule kind (changes, retries that closed or advanced)")
            print(" " * 16 + "".join(f"{c[:13]:>14s}" for c in p["cols"]))
            for d, cr, wr in zip(p["rows"], p["count"], p["won"]):
                print(f"{d[:15]:16s}" + "".join(f"{f'{c}/{w}' if c else '.':>14s}" for c, w in zip(cr, wr)))
    if errors:
        print("inconsistent log:", *errors, sep="\n  ")
        return 1
    return 0


def cmd_barriers(args) -> int:
    from .bllm import atlas as A
    from .bllm import barriers as B
    atlas = A.load(args.atlas)
    errors = A.check(atlas)
    if args.json:
        print(json.dumps(dict(ledger=B.ledger(), atlas=atlas, counts=A.counts(atlas), errors=errors), indent=1))
        return 1 if errors else 0
    for line in A.summary(atlas, args.target):
        print(line)
    print()
    print("ledger (walls with predicates on library nodes, pruning before the checks):")
    for b in B.ledger():
        if args.target and b["problem"] != args.target:
            continue
        print(f"  {b['id']} [{b['status']}]: {b['statement']}")
        for h in b["hypotheses"]:
            print(f"      {h['id']}: {h['text']}; breakers: {', '.join(h['breakers']) or 'none (a gap)'}")
    for e in errors:
        print("error:", e)
    return 1 if errors else 0


def cmd_superstring(args) -> int:
    from .bllm import atlas as A
    from .bllm import superstring as S
    data = S.load(args.data)
    atlas = A.load()
    errors = S.check(data, atlas)
    if args.json:
        print(json.dumps(dict(run=S.run(data, args.target), roster=S.roster(data, args.target, args.zone), errors=errors), indent=1))
        return 1 if errors else 0
    if args.zone:
        for r in S.roster(data, args.target, args.zone):
            print(f"{r['target']}: {r['id']} [{r['move']}, {r['status']}]: {r['piece']}")
    else:
        for line in S.summary(data, args.target):
            print(line)
    for e in errors:
        print("error:", e)
    return 1 if errors else 0


def cmd_audit(args) -> int:
    from .bllm import audit as AU
    if args.golden:
        res = AU.golden(args.golden, args.folder or None, args.timeout)
        if args.json:
            print(json.dumps(res, indent=1))
        else:
            for r in res["results"]:
                print(f"  {r['status']:<7} {r['seconds']:>7.1f} s  {r['run']}")
                for line in r.get("detail") or []:
                    print("           ", line)
            print("tally:", ", ".join(f"{k} {v}" for k, v in sorted(res["tally"].items())) or "no runs found")
        return 0 if res["passed"] else 1
    names = [args.name] if args.name else AU.names()
    for n in names:
        print(json.dumps(AU.load(n), indent=1) if args.json else AU.report(n))
    return 0


def cmd_triage(args) -> int:
    import os
    from .bllm import triage as T
    path = args.file or os.path.join(os.path.dirname(T.__file__), "data", "triage.example.json")
    with open(path, encoding="utf-8") as f:
        rep = T.triage(json.load(f))
    print(json.dumps(rep, indent=1, ensure_ascii=False) if args.json else T.table(rep))
    return 0


def cmd_figcritic(args) -> int:
    from .bllm import figcritic as FC
    found = FC.review(args.folder)
    for f in found:
        print(f)
    print(f"{len(found)} finding(s)")
    return 1 if found else 0


def cmd_skills(args) -> int:
    from .bllm import selfmod as S
    from .bllm import skills as K
    runs = S.load_log(args.log)
    m = K.SkillMemory.from_log(runs)
    rep = m.report()
    nns = K.needed_not_sufficient(runs)
    if args.json:
        rep["needed_not_sufficient"] = [dict(run=run, target=r.target, attempt=r.attempt, diagnosis=r.diagnosis,
                                             kind=r.change.kind, retry=r.retry) for run, r in nns]
        print(json.dumps(rep, indent=1))
        return 0
    print(f"{rep['trajectories']} trajectories: " + ", ".join(f"{v} {k}" for k, v in sorted(rep["status"].items())))
    for e in rep["edges"]:
        print(f"  {e['status']:9s} {e['run']}: {e['target']} ({e['outcome']}); "
              + (", ".join(f"{d} -> {k}" for d, k, _ in e["changes"]) or "no change"))
    print("failure kind -> rule kind: finished trajectories that used it, of them closed or advanced")
    for p in rep["pairs"]:
        print(f"  {p['diagnosis']:15s} -> {p['kind']:15s} {p['good']}/{p['finished']}" + ("  pruned" if p["pruned"] else ""))
    print("changes whose own retry failed, inside a run that closed or advanced:")
    for run, r in nns:
        print(f"  {run}: {r.target} #{r.attempt}, {r.diagnosis} -> {r.change.kind} ({r.change.rule})")
    return 0


def main(argv=None) -> int:
    name = os.path.basename(sys.argv[0]) if argv is None else "anaxia"
    prog = "ebllm" if name.startswith("ebllm") else "anaxia"
    args_in = sys.argv[1:] if argv is None else list(argv)
    if os.environ.get("ANAXIA_IMAGE") == "1" and "update" not in args_in:
        from .update import notice
        line = notice()
        if line:
            print(line, file=sys.stderr)
    p = argparse.ArgumentParser(prog=prog, description="Anaxia, the BLLM engine: verifier-gated conjecture closure")
    p.add_argument("--version", action="version", version=f"{prog} {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("controls", help="list the closures, calibrations and open problems with their labels")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_controls)
    s = sub.add_parser("scan", help="scan Lean sources for sorry, axioms, native_decide and other escapes")
    s.add_argument("paths", nargs="+")
    s.add_argument("--exclude", action="append", default=[])
    s.set_defaults(func=cmd_scan)
    s = sub.add_parser("axioms", help="audit the output of #print axioms")
    s.add_argument("log")
    s.add_argument("expected", nargs="?", type=int)
    s.set_defaults(func=cmd_axioms)
    s = sub.add_parser("counterexamples", help="the counterexamples to Theorem 10.4, Lemma 6.2 and the collapse guard")
    s.set_defaults(func=cmd_counterexamples)
    s = sub.add_parser("run", help="run one engine step from a JSON spec and print the contract report")
    s.add_argument("spec")
    s.add_argument("--ledger")
    s.set_defaults(func=cmd_run)
    s = sub.add_parser("demo", help="BLLM: six subagents close the demo problems under the checks")
    s.add_argument("--mode", choices=["exact", "certified"], default="exact")
    s.add_argument("--rounds", type=int, default=4)
    s.add_argument("--theta", type=float, default=1e-3)
    s.add_argument("--lean", action="store_true", help="also tactic search on Lean goals (needs lean on PATH)")
    s.add_argument("--spiking", action="store_true", help="order the turns with the spiking selector")
    s.add_argument("--vault", help="write the memory as an Obsidian vault in this folder")
    s.set_defaults(func=cmd_demo)
    s = sub.add_parser("schedule", help="the entropy-law schedule for given check costs")
    s.add_argument("costs", help="comma-separated costs")
    s.add_argument("--eps", type=float, default=0.5)
    s.add_argument("--theta", type=float, default=1e-6)
    s.set_defaults(func=cmd_schedule)
    s = sub.add_parser("tasks", help="the stepwise records of solved and open problems")
    s.set_defaults(func=cmd_tasks)
    s = sub.add_parser("attack", help="the open steps of a task, their ladders and BLLM's plan")
    s.add_argument("task")
    s.set_defaults(func=cmd_attack)
    s = sub.add_parser("gap", help="the gap law on the human and LLM idea data of arXiv:2607.01233")
    s.add_argument("--axis", choices=["opportunity", "method"])
    s.add_argument("--data")
    s.set_defaults(func=cmd_gap)
    s = sub.add_parser("bridge", help="a stream of problems: LLM alone, BLLM with the spiking selector, optimum")
    s.add_argument("--model", default="Claude-Sonnet-4.6")
    s.add_argument("--axis", default="opportunity", choices=["opportunity", "method"])
    s.add_argument("--lam", type=float, default=0.5)
    s.add_argument("--problems", type=int, default=3000)
    s.add_argument("--window", type=int, default=500)
    s.add_argument("--seed", type=int, default=5)
    s.set_defaults(func=cmd_bridge)
    s = sub.add_parser("brain", help="load a connectome (worm, fly) or the H01 somas and describe it")
    s.add_argument("kind", choices=["worm", "fly", "h01"])
    s.add_argument("path")
    s.add_argument("--top", type=int, default=8)
    s.add_argument("--reservoir", action="store_true")
    s.set_defaults(func=cmd_brain)
    s = sub.add_parser("providers", help="the language-model connectors and which keys are set")
    s.set_defaults(func=cmd_providers)
    s = sub.add_parser("fetch", help="fetch a pinned third-party repository at its commit (fetch deepmind <name>)")
    s.add_argument("org", choices=["deepmind"])
    s.add_argument("names", nargs="*")
    s.add_argument("--all", action="store_true", help="every repository tagged vendor")
    s.add_argument("--list", action="store_true", help="the pinned repositories with commit, licence and use")
    s.add_argument("--root", help="where to put the checkouts (default $ANAXIA_THIRD_PARTY or ~/.cache/anaxia/deepmind)")
    s.set_defaults(func=cmd_fetch)
    s = sub.add_parser("intake", help="the index of what Anaxia takes from DeepMind: summary, search, memory")
    s.add_argument("org", choices=["deepmind"])
    s.add_argument("--search", help="rank index items against this text (the open-or-solved check)")
    s.add_argument("-k", type=int, default=10)
    s.add_argument("--source", help="only items of this repository")
    s.add_argument("--status", help="only items with this status, e.g. open")
    s.add_argument("--memory", help="write the index into this memory file")
    s.add_argument("--rebuild", metavar="ROOT", help="fetch the vendor repositories under ROOT and rebuild the index")
    s.set_defaults(func=cmd_intake)
    s = sub.add_parser("sources", help="what Anaxia takes from other AI mathematics work, and the open-or-settled check",
                       description="list: the registry; show ID: one entry; check TEXT: search the DeepMind, OpenRefute "
                                   "and OpenAI indexes; summary: the external indexes by status; build: rebuild them "
                                   "from local checkouts.")
    s.add_argument("action", choices=["list", "show", "check", "summary", "build"])
    s.add_argument("text", nargs="*")
    s.add_argument("-k", type=int, default=10)
    s.add_argument("--source", help="only items of this source, e.g. openrefute")
    s.add_argument("--status", help="only items with this status, e.g. refuted")
    s.add_argument("--openrefute", metavar="ROOT", help="a checkout of trureturing (build)")
    s.add_argument("--openai", metavar="ROOT", help="a checkout of the OpenAI manuscript collection (build)")
    s.set_defaults(func=cmd_sources)
    s = sub.add_parser("construct", help="construction mode: build planar colouring gadgets and check them from scratch",
                       description="steinberg: rebuild Steinberg's counterexample and check it; list/check: the stored "
                                   "gadgets; build: the goal-directed builder; assemble: gadget to whole graph; "
                                   "cegar, book, hub: exists-forall SAT searches; algebra: the typed gadget library; "
                                   "tower: the layer tower B^n (--depth n, --mesh); bench: tower depths and wirings "
                                   "against the crossing loop. "
                                   "Arguments after the tool go to it (anaxia construct build --help).")
    s.add_argument("tool", choices=["list", "check"] + sorted(CONSTRUCT_TOOLS))
    s.add_argument("rest", nargs=argparse.REMAINDER)
    s.set_defaults(func=cmd_construct)
    s = sub.add_parser("modlog", help="the learn-from-failure log: each failure, its diagnosis, the rule it changed, the retry")
    s.add_argument("--log", help="a log file in the format of the bundled data/modlog.json")
    s.add_argument("--patterns", action="store_true", help="also the failure-kind by rule-kind matrix")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_modlog)
    s = sub.add_parser("barriers", help="the barrier atlas: the proved walls of the four targets, their hypotheses, breakers and routes")
    s.add_argument("--target", choices=["hodge", "strings", "seed", "yang-mills"])
    s.add_argument("--atlas", help="an atlas file in the format of the bundled data/atlas.json")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_barriers)
    s = sub.add_parser("superstring", help="the attack chains: an attacker on every target, zone and piece, run to the end; where each target stops")
    s.add_argument("--target", choices=["hodge", "strings", "seed", "yang-mills"])
    s.add_argument("--zone", help="only the attackers of one zone (an atlas wall id, or frontier)")
    s.add_argument("--data", help="an attackers file in the format of the bundled data/attackers.json")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_superstring)
    s = sub.add_parser("skills", help="the skill memory: each run of the log as one hyperedge, strategies, patterns, pruning")
    s.add_argument("--log", help="a log file in the format of the bundled data/modlog.json")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_skills)
    s = sub.add_parser("audit", help="audits of published calculations: stages, findings by kind, and the golden-output runner")
    s.add_argument("name", nargs="?", help="a stored audit (default: all)")
    s.add_argument("--golden", metavar="DIR", help="run every check under DIR against its expected_output/ and compare")
    s.add_argument("--folder", action="append", help="with --golden, only this subfolder (repeatable)")
    s.add_argument("--timeout", type=float, default=3600.0)
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_audit)
    s = sub.add_parser("triage", help="go or no-go on candidate problems before any attack: constraints, score, Pareto front")
    s.add_argument("file", nargs="?", help="an anaxia-triage-v1 JSON file (default: the bundled example)")
    s.add_argument("--json", action="store_true")
    s.set_defaults(func=cmd_triage)
    s = sub.add_parser("figcritic", help="exact checks on SVG figures: canvas, overlap, captions, themes, alt text, reduced motion")
    s.add_argument("folder", nargs="?", default="docs/assets")
    s.set_defaults(func=cmd_figcritic)
    s = sub.add_parser("update", help="whether a newer image is published on ghcr.io, and how to pull it")
    s.add_argument("--pull", action="store_true", help="run docker pull when docker is on the path")
    s.add_argument("--timeout", type=float, default=5.0)
    s.set_defaults(func=lambda a: __import__("ebllm.update", fromlist=["cmd_update"]).cmd_update(a))
    args = p.parse_args(args_in)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
