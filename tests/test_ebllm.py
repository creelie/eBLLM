import itertools
import json
import os
import random
import subprocess
import sys
import tempfile
import unittest
from fractions import Fraction

from ebllm import Label, VERIFIERS, emit, release_product
from ebllm.accuracy import accuracy26, monotone_step, monotone_step_paper
from ebllm.controls import load_controls
from ebllm.engine import Engine, Proposal
from ebllm.failures import FailureTensor, route_second_attempt
from ebllm.kappa import Operator, count_raw_words, kappa_select, words
from ebllm.obligations import ObligationGraph, gate_dist, m_star, numerical_lift
from ebllm.package import ConjecturePackage
from ebllm.playbook import Bullet, Playbook, collapse_paper, collapse_v11, core, density
from ebllm.sandtile import (SandTile, abelian_check, counterexample_conservative,
                            counterexample_dissipative)
from ebllm.scope import (compose, counterexample_superadditivity, is_injective_where_defined,
                         loss, pulled_back_loss)
from ebllm.verifiers import CommandVerifier, parse_axioms, scan_lean_sources


class ReleaseAlgebra(unittest.TestCase):
    def test_product_over_all_assignments(self):
        for bits in itertools.product((0, 1), repeat=len(VERIFIERS)):
            f = dict(zip(VERIFIERS, bits))
            self.assertEqual(release_product(f), int(all(bits)))

    def test_one_zero_blocks(self):  # Theorems 2.2, 3.1, 21.3
        for chi in VERIFIERS:
            f = {c: 1 for c in VERIFIERS}
            f[chi] = 0
            self.assertEqual(release_product(f), 0)
            self.assertNotIn(emit(f, model_ok=True), (Label.THEOREM, Label.COUNTEREXAMPLE))

    def test_labels(self):
        ones = {c: 1 for c in VERIFIERS}
        self.assertEqual(emit(ones), Label.THEOREM)
        self.assertEqual(emit(ones, kind="refutation"), Label.COUNTEREXAMPLE)
        self.assertEqual(emit(ones, conditions=["GRH"]), Label.CONDITIONAL)
        self.assertEqual(emit({}, model_ok=True), Label.CANDIDATE)
        self.assertEqual(emit({}, improving_machinery=False), Label.BUJ)
        self.assertEqual(emit({}), Label.OPEN)

    def test_missing_factor_counts_as_zero(self):
        self.assertEqual(release_product({"proof": 1}), 0)

    def test_bad_factor(self):
        with self.assertRaises(ValueError):
            release_product({c: 2 for c in VERIFIERS})


class Obligations(unittest.TestCase):
    def graph(self):
        g = ObligationGraph()
        for n in ("a", "b", "c", "main"):
            g.add(n)
        g.bridge(["a", "b"], "c")
        g.bridge(["c"], "main")
        return g

    def test_release_soundness(self):  # Theorem 6.3
        g = self.graph()
        self.assertFalse(g.releasable("main"))
        g.nodes["a"].status = "PASS"
        self.assertFalse(g.releasable("main"))
        self.assertEqual(g.blockers("main"), ["b"])
        g.nodes["b"].status = "PASS"
        self.assertTrue(g.releasable("main"))

    def test_scope_loss_blocks(self):
        g = ObligationGraph()
        g.add("a", status="PASS")
        g.add("main")
        g.bridge(["a"], "main", scope_loss=0.1)
        self.assertFalse(g.releasable("main"))

    def test_debt_monotone_release(self):  # Corollary 6.4, on random graphs
        rng = random.Random(3)
        for _ in range(200):
            g = self.graph()
            for n in g.nodes.values():
                n.status = rng.choice(["PASS", "FAIL", "UNK"])
                n.weight = rng.choice([0.0, 1.0, 2.5])
            if g.releasable("main"):
                leaves_debt = sum(g.nodes[v].weight for v in g.leaves() if g.nodes[v].status != "PASS")
                self.assertEqual(leaves_debt, 0)

    def test_gates(self):
        self.assertEqual(numerical_lift(1), 1.0)
        self.assertEqual(numerical_lift(0), 0.0)
        self.assertAlmostEqual(numerical_lift("*", 0.0), 1.0)
        self.assertEqual(m_star([1] * 6, [0] * 6), 0.0)
        self.assertGreater(gate_dist([1, 1, "*", 1, 1, 1], [0, 0, 0.5, 0, 0, 0]), 0)


class PlaybookGuards(unittest.TestCase):
    def setUp(self):
        self.a = Bullet("a", "formal", "gap a", "FAIL")
        self.b = Bullet("b", "formal", "gap b", "FAIL")
        self.c = Bullet("c", "upper", "gap c", "UNK")

    def test_paper_guard_counts_resolution_as_collapse(self):
        old = [self.a, self.b]
        resolved = [Bullet("a", "formal", "gap a", "PASS", "PASS"), self.b]
        self.assertEqual(collapse_paper(old, resolved), Fraction(1, 2))
        self.assertEqual(collapse_v11(old, resolved), 0)
        pb = Playbook([self.a, self.b], theta=Fraction(1, 3), rule="paper")
        self.assertFalse(pb.apply_delta(resolve=["a"]))   # the success cannot be recorded
        pb = Playbook([self.a, self.b], theta=Fraction(0), rule="v1.1")
        self.assertTrue(pb.apply_delta(resolve=["a"]))
        self.assertEqual(set(pb.core()), {"b"})

    def test_v11_theta_zero_never_erases(self):
        rng = random.Random(5)
        for _ in range(300):
            pool = [Bullet(str(i), "g", "x", rng.choice(["FAIL", "UNK", "PASS"]),
                           rng.choice(["UNK", "FAIL", "PASS"])) for i in range(6)]
            pb = Playbook(pool[:4], theta=Fraction(0))
            before = set(pb.core())
            pb.apply_delta(add=pool[4:], resolve=[str(rng.randrange(6))], remove=[str(rng.randrange(6))])
            after_ids = {b.id for b in pb.bullets}
            for bid in before:
                b = next(x for x in pb.bullets if x.id == bid) if bid in after_ids else None
                self.assertIsNotNone(b)  # never deleted

    def test_fixed_theta_lapses_when_core_grows(self):
        # theta = 1/3 < 1/|Core| holds for |Core| = 2 but not for |Core| = 3
        pb = Playbook([self.a, self.b, self.c], theta=Fraction(1, 3), rule="paper")
        self.assertTrue(pb.apply_delta(remove=["c"]))   # an unresolved failure is erased
        self.assertNotIn("c", pb.core())

    def test_density_drops_without_progress(self):  # Proposition 30.4's "genuine progress"
        old = [self.a, self.b]
        padded = old + [Bullet("z", "misc", "an unrelated true remark", "PASS", "PASS")]
        self.assertLess(density(padded), density(old))
        self.assertEqual(set(core(padded)), set(core(old)))


class SandTiles(unittest.TestCase):
    def test_conservative_never_stabilizes(self):
        st, h = counterexample_conservative()
        self.assertIsNone(st.stabilize(h, max_topples=20000))
        self.assertIsNone(st.stabilize(h, order="random", max_topples=20000))
        self.assertEqual(st.bound_theorem_10_4(h), 4)

    def test_dissipative_exceeds_bound(self):
        for k in (10, 100, 1000):
            st, h = counterexample_dissipative(Fraction(1, k))
            hf, n, absorbed = st.stabilize(h, max_topples=10 * k)
            self.assertEqual(n, k)
            self.assertGreater(n, st.bound_theorem_10_4(h))
            self.assertEqual(sum(h) - sum(hf), absorbed)   # Definition 10.1 balance

    def test_abelian(self):
        self.assertTrue(abelian_check(trials=40))


class Scope(unittest.TestCase):
    def test_counterexample(self):
        f, g = counterexample_superadditivity()
        self.assertLess(loss(compose(g, f)), loss(f) + loss(g))

    def test_decomposition_and_union_bound(self):
        for na in range(0, 4):
            for nb in range(1, 4):
                for f in itertools.product([None] + list(range(nb)), repeat=na):
                    for g in itertools.product([None] + list(range(nb)), repeat=nb):
                        h = compose(g, f)
                        self.assertEqual(loss(h), loss(f) + pulled_back_loss(g, f))
                        if is_injective_where_defined(f):
                            self.assertLessEqual(loss(h), loss(f) + loss(g))


class Misc(unittest.TestCase):
    def test_accuracy(self):
        self.assertEqual(accuracy26(0, 0, 0, 0, 0, 3, 1, 0, 0), 1)
        self.assertEqual(accuracy26(1, 0, 0, 0, 0, 1, 0, 0, 0), Fraction(1, 2))
        prev = dict(R=3, Mstar=1, MapDef=0, NMDef=1)
        self.assertTrue(monotone_step(prev, dict(R=2, Mstar=1, MapDef=0, Collapse=0, NMDef=1)))
        self.assertFalse(monotone_step(prev, dict(R=3, Mstar=1, MapDef=0, Collapse=1, NMDef=1)))
        # Proposition 21.1 as printed is not an "iff": with Collapse 1/2 at step t, the score rises
        # although the printed condition fails
        base = (3, 1, 0, 1)
        p = dict(R=2, Mstar=0, MapDef=0, Collapse=Fraction(1, 2), NMDef=0)
        n = dict(R=2, Mstar=0, MapDef=0, Collapse=Fraction(1, 4), NMDef=0)
        a_t = accuracy26(p["R"], p["Mstar"], p["MapDef"], p["Collapse"], p["NMDef"], *base)
        a_t1 = accuracy26(n["R"], n["Mstar"], n["MapDef"], n["Collapse"], n["NMDef"], *base)
        self.assertGreater(a_t1, a_t)
        self.assertTrue(monotone_step(p, n))
        self.assertFalse(monotone_step_paper(p, n))

    def test_failure_tensor(self):
        F = FailureTensor()
        F.record(24, "formal")
        F.record(24, "formal")
        F.record(3, "upper")
        self.assertEqual(F.dominant(), (24, "formal", 2))
        self.assertEqual(route_second_attempt({"formal": 2.0, "upper": 1.0}, {"formal": 0.1, "upper": 0.9}), "upper")

    def test_kappa(self):
        ops = [Operator("d", "form", "form"), Operator("int", "form", "number"), Operator("abs", "number", "number")]
        ws = list(words(ops, 3))
        self.assertLessEqual(len(ws), count_raw_words(len(ops), 3))
        self.assertTrue(all(w[i].dst == w[i + 1].src for w in ws for i in range(len(w) - 1)))
        best = kappa_select(ops, 3, gain=lambda w: len(w) - 2.5, cmv=lambda w: True)
        self.assertEqual(len(best), 3)
        self.assertIsNone(kappa_select(ops, 3, gain=lambda w: -1, cmv=lambda w: True))

    def test_controls(self):
        cs = load_controls()
        self.assertGreaterEqual(len(cs), 20)
        by = {c.slug: c for c in cs}
        self.assertEqual(by["fermat"].label, Label.THEOREM)
        self.assertEqual(by["morley-tran-8.6"].label, Label.CANDIDATE)
        self.assertEqual(by["morley-tran-8.6"].blocking, ["human"])
        for c in cs:
            if c.group == "open":
                self.assertEqual(c.label, Label.OPEN)
            if c.group in ("closure", "partial"):
                self.assertNotEqual(c.label, Label.THEOREM)   # nothing unrefereed is released

    def test_scan_and_axioms(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "A.lean")
            with open(p, "w") as fh:
                fh.write("-- sorry in a comment\ntheorem t : True := by\n  sorry\naxiom bad : False\n")
            hits = scan_lean_sources([d])
            self.assertEqual(len(hits["sorry"]), 1)
            self.assertEqual(len(hits["axiom declaration"]), 1)
            with open(p, "w") as fh:
                fh.write("/-! A doc comment that mentions\nsorry and native_decide /- nested -/ sorry -/\n"
                         "def s := \"-- not a comment, sorry\"\ntheorem t : True := trivial -- sorry\n"
                         "example : 'a' = 'a' := by native_decide\n")
            hits = scan_lean_sources([d])
            self.assertEqual(hits["sorry"], [f"{p}:3: def s := \"-- not a comment, sorry\""])
            self.assertEqual(len(hits["native_decide"]), 1)
            self.assertTrue(hits["native_decide"][0].startswith(f"{p}:5: "))
        log = ("'t' depends on axioms: [propext, Classical.choice, Quot.sound]\n"
               "'u' does not depend on any axioms\n'v' depends on axioms: [sorryAx]\n")
        rs = parse_axioms(log)
        self.assertEqual([r.standard for r in rs], [True, True, False])

    def test_command_verifier(self):
        self.assertEqual(CommandVerifier([sys.executable, "-c", "print('ok 42')"], expect=r"ok \d+")(), 1)
        self.assertEqual(CommandVerifier([sys.executable, "-c", "import sys; sys.exit(1)"])(), 0)
        self.assertEqual(CommandVerifier([sys.executable, "-c", "print('no')"], expect="yes")(), 0)

    def test_engine(self):
        g = ObligationGraph()
        g.add("lemma")
        g.add("main")
        g.bridge(["lemma"], "main")
        ones = {c: 1 for c in VERIFIERS}
        eng = Engine(ConjecturePackage("toy", "arithmetic"), g, ones)
        rec = eng.step(0, Proposal(checks={"lemma": 0}))
        self.assertEqual(rec["label"], "OPEN")
        self.assertEqual(len(eng.playbook.core()), 1)
        rec = eng.step(1, Proposal(checks={"lemma": 1}, model_ok=True))
        self.assertEqual(rec["label"], "THEOREM")
        self.assertEqual(len(eng.playbook.core()), 0)    # the resolution was recorded

    def test_cli(self):
        env = dict(os.environ, PYTHONPATH=os.pathsep.join(sys.path))
        out = subprocess.run([sys.executable, "-m", "ebllm", "counterexamples"], capture_output=True,
                             text=True, env=env)
        self.assertEqual(out.returncode, 0)
        self.assertIn("topplings needed 100", out.stdout)


if __name__ == "__main__":
    unittest.main()
