"""Command line: `ebllm controls`, `ebllm scan`, `ebllm axioms`, `ebllm counterexamples`, `ebllm run`."""
from __future__ import annotations

import argparse
import json
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


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="ebllm", description="verifier-gated conjecture closure")
    p.add_argument("--version", action="version", version=f"ebllm {__version__}")
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
    args = p.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
