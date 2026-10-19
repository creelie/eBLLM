"""Bench of the layer tower against the crossing loop on the same targets.

Every configuration (depth 1, 2, 3; ladder or mesh) runs on every target and
seed with the same budget of exact SAT checks, and so does the typed crossing
loop of gadget_algebra (random planar frames filled with library gadgets), whose
checks are counted the same way: one per colour pattern it asks the solver
about. A run reaches the goal when a gadget with the goal's contact profile
passes the independent gate of tower.meets. The summary gives, per target and
configuration, the seeds that reached the goal, the median checks to the goal
over all seeds (a seed that does not reach it counts as its whole budget, so
the median is a censored one and is marked as such), the gadgets found on the
way and the time.
"""
from __future__ import annotations

import argparse
import json
import multiprocessing as mp
import os
import random
import statistics
import time

import networkx as nx
from pysat.solvers import Solver

from . import gadget_algebra as ga
from . import tower as T

BUDGETS = {"steinberg-g1": 10000, "steinberg-g2": 25000, "erdos-k6": 20000}
# the crossing loop is cheap per check, so it also gets a run limited by time
# only, longer than any tower run on the target
SECONDS = {"steinberg-g1": 120, "steinberg-g2": 400, "erdos-k6": 400}
CONFIGS = [(d, w) for d in (1, 2, 3) for w in ("ladder", "mesh")]


def crossing(target, budget, seed, seconds=None):
    """The crossing loop on the same target, counted in the same checks."""
    tg = T.TARGETS[target]
    forbid = set(tg.forbid)
    rng = random.Random(seed)
    lib = ga.Library(ga.seeds(forbid))
    a = argparse.Namespace(max_hidden=6, max_slots=5, max_edges=5)
    rec = {"target": target, "depth": 0, "wiring": "crossing", "seed": seed, "budget": budget,
           "goal_at": None, "found": [], "children": 0, "rejected": 0}
    checks, t0 = 0, time.time()
    while checks < budget and (seconds is None or time.time() - t0 < seconds):
        nv, outer, slots, edges = ga.random_child(lib, rng, a)
        rec["children"] += 1
        if not ga.frame_planar(nv, outer, slots, edges):
            continue
        G = ga.build_child(nv, outer, slots, edges)
        if G.number_of_nodes() > 300 or ga.has_forbidden_cycle(G, forbid):
            continue
        terms = [("f", v) for v in outer]
        if not terms:
            checks += 1
            cls, _ = ga.colour_cnf(G)
            s = Solver(name="cadical153", bootstrap_with=cls)
            col = s.solve()
            s.delete()
            if not col:
                rec["found"].append((checks, "0-terminal", G.number_of_nodes(), G.number_of_edges(), "x"))
            continue
        if not nx.is_connected(G):
            continue
        g = ga.make(G, terms, "")
        checks += len(ga.PATTERNS[len(terms)])
        if len(g.rel) == len(ga.PATTERNS[len(terms)]) or min(g.dist) < 2 or not lib.offer(g):
            continue
        if len(g.terms) != 3 or (0, 0, 0) in g.rel:
            continue
        m = {t: i for i, t in enumerate(g.terms)}
        rest = iter(range(3, g.size + 3))
        H = nx.relabel_nodes(g.G, {v: m[v] if v in m else next(rest) for v in g.G.nodes()})
        if not T.meets(H, tg.forbid, (0, 0, 0)):
            rec["rejected"] += 1
            continue
        rec["found"].append((checks, list(g.dist), g.size, H.number_of_edges(), "x"))
        if T.covers(T.distances(H), tg.goal):
            rec["goal_at"] = checks
            break
    rec.update(checks=checks, seconds=time.time() - t0, tries=rec["children"])
    return rec


def job(spec):
    target, depth, wiring, seed, budget = spec
    if wiring == "crossing":
        return crossing(target, budget, seed)
    if wiring == "crossing-time":
        r = crossing(target, 10 ** 12, seed, SECONDS[target])
        r.update(wiring="crossing-time", budget=budget)
        return r
    r = T.run(target, depth, wiring == "mesh", budget, seed)
    r["budget"] = budget
    return r


def summarise(rows):
    out = {}
    for r in rows:
        key = f'{r["target"]}|{r["wiring"]}|{r["depth"]}'
        out.setdefault(key, []).append(r)
    summary = []
    for key, rs in sorted(out.items()):
        target, wiring, depth = key.split("|")
        budget = rs[0]["budget"]
        to_goal = [r["goal_at"] if r["goal_at"] is not None else max(budget, r["checks"]) for r in rs]
        reached = sum(r["goal_at"] is not None for r in rs)
        summary.append({
            "target": target, "wiring": wiring, "depth": int(depth), "budget": budget,
            "seeds": len(rs), "reached": reached,
            "median_checks_to_goal": statistics.median(to_goal),
            "censored": reached < len(rs),
            "gadgets_found_mean": statistics.mean(len(r["found"]) for r in rs),
            "checks_per_gadget": (sum(r["checks"] for r in rs) / max(1, sum(len(r["found"]) for r in rs))),
            "seconds_mean": statistics.mean(r["seconds"] for r in rs),
        })
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(prog="anaxia construct bench",
                                 description="tower depths and wirings against the crossing loop")
    ap.add_argument("--targets", nargs="+", default=sorted(BUDGETS), choices=sorted(T.TARGETS))
    ap.add_argument("--seeds", default="1,2,3,4,5")
    ap.add_argument("--jobs", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument("--budget", type=int, default=0, help="checks per run (0: the target's default)")
    ap.add_argument("--out", default="tower_bench.jsonl")
    a = ap.parse_args(argv)
    seeds = [int(s) for s in a.seeds.split(",")]
    specs = []
    for tg in a.targets:
        b = a.budget or BUDGETS.get(tg, 20000)
        for s in seeds:
            specs.append((tg, 0, "crossing", s, b))
            specs.append((tg, 0, "crossing-time", s, b))
            specs.extend((tg, d, w, s, b) for d, w in CONFIGS)
    done = set()
    rows = []
    if os.path.exists(a.out):
        with open(a.out) as f:
            for line in f:
                r = json.loads(line)
                rows.append(r)
                done.add((r["target"], r["depth"], r["wiring"], r["seed"], r["budget"]))
    todo = [s for s in specs if s not in done]
    with mp.Pool(a.jobs) as pool, open(a.out, "a") as f:
        for r in pool.imap_unordered(job, todo):
            rows.append(r)
            f.write(json.dumps(r) + "\n")
            f.flush()
            print(json.dumps({k: r[k] for k in ("target", "wiring", "depth", "seed", "goal_at", "checks")}
                             | {"found": len(r["found"]), "seconds": round(r["seconds"], 1)}), flush=True)
    keep = {(s[0], s[1], s[2], s[3], s[4]) for s in specs}
    rows = [r for r in rows if (r["target"], r["depth"], r["wiring"], r["seed"], r["budget"]) in keep]
    for row in summarise(rows):
        print(json.dumps(row))
    return rows


if __name__ == "__main__":
    main()
