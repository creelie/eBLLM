"""Tests of BLLM: schedules, checks, agents, coordinator, gap law, spiking selector, connectomes, tasks."""
import io
import json
import math
import os
import random
import tempfile
import unittest
from contextlib import redirect_stdout

from ebllm.bllm import gap, neuro, schedules
from ebllm.bllm.agents import DEMO_PROBLEMS, LEAN_PROBLEMS, LeanTacticAgent, ModelAgent, default_agents
from ebllm.bllm.checks import Candidate, ExactIdentityCheck, LeanCheck, SmallPrimeCheck
from ebllm.bllm.coordinator import Coordinator
from ebllm.bllm.proposers import ModelProposer, ScriptedProposer, extract_json_list
from ebllm.bllm.tasks import load_tasks, validate
from ebllm.bllm.vault import Vault
from ebllm.cli import main


class TestSchedules(unittest.TestCase):
    def test_ceiling_sound_and_within_bounds(self):
        costs = [1, 2, 3, 5, 8, 13]
        for eps in (0.5, 0.1):
            for th in (1e-2, 1e-6):
                r = schedules.ceiling_schedule(costs, eps, th)
                self.assertLessEqual(schedules.false_acceptance_bound(r, eps), th * (1 + 1e-9))
                lo, hi = schedules.entropy_bounds(costs, eps, th)
                self.assertTrue(lo - 1e-9 <= schedules.cost(costs, r) <= hi + 1e-9)

    def test_huffman_is_optimal_by_brute_force(self):
        costs, D, k = [5, 3, 2, 1, 1], 2, 1
        r = schedules.huffman_schedule(costs, D, k)
        self.assertLessEqual(sum(D ** -x for x in r), D ** -k + 1e-12)
        best = min(schedules.cost(costs, rr) for rr in __import__("itertools").product(range(1, 7), repeat=5)
                   if sum(D ** -x for x in rr) <= D ** -k + 1e-12)
        self.assertEqual(schedules.cost(costs, r), best)

    def test_online_bound(self):
        s = schedules.OnlineScheduler(0.5, 1e-3)
        rng = random.Random(1)
        for _ in range(500):
            s.runs(rng.uniform(0.1, 10))
        self.assertLess(s.spent_budget, 1e-3)
        self.assertLessEqual(s.cost(), s.guarantee() + 1e-9)

    def test_regimes(self):
        self.assertTrue(schedules.singularity_regime(2).sound)
        self.assertFalse(schedules.singularity_regime(1, 1.5).sound)
        self.assertTrue(schedules.singularity_regime(1, 2.5).sound)
        self.assertFalse(schedules.singularity_regime(1.5, s=1).sound)


class TestChecksAndAgents(unittest.TestCase):
    def test_exact_and_weak(self):
        good = Candidate("g", "identity", dict(lhs="(x+y)^2", rhs="x^2+2*x*y+y^2"))
        bad = Candidate("b", "identity", dict(lhs="(x+y)^2", rhs="x^2+y^2"))
        rng = random.Random(0)
        self.assertTrue(ExactIdentityCheck().run(good, rng).passed)
        self.assertFalse(ExactIdentityCheck().run(bad, rng).passed)
        self.assertTrue(all(SmallPrimeCheck().run(good, rng).passed for _ in range(20)))

    def test_demo_closes_everything_in_both_modes(self):
        for mode in ("exact", "certified"):
            res = Coordinator().run(DEMO_PROBLEMS, mode=mode, rounds=4)
            self.assertEqual(len(res.solved), len(DEMO_PROBLEMS))
            for pid, cid in res.solved.items():
                n = res.vault.notes[cid]
                d = ExactIdentityCheck().run(Candidate("x", "identity", dict(lhs=n["lhs"], rhs=n["rhs"])), random.Random(0))
                self.assertTrue(d.passed, pid)
            if mode == "certified":
                self.assertLessEqual(res.false_bound, res.theta)

    def test_bypass_keeps_the_shape(self):
        res = Coordinator().run(DEMO_PROBLEMS, rounds=4)
        n = res.vault.notes[res.solved["brahmagupta2"]]
        self.assertEqual(n["move"], "bypass")
        self.assertEqual(n["rhs"].count(")^2"), 2)

    def test_spiking_selector_orders_turns(self):
        co = Coordinator(selector="spiking")
        res = co.run(DEMO_PROBLEMS, rounds=4)
        self.assertEqual(len(res.solved), len(DEMO_PROBLEMS))
        self.assertEqual(sum(co.selector.counts), len(DEMO_PROBLEMS))

    def test_model_agent_with_scripted_proposer(self):
        reply = 'Here: [{"kind": "identity", "rhs": "(x-y)*(x+y)", "rationale": "difference of squares"},' \
                ' {"kind": "identity", "rhs": "x^2+y^2"}, {"kind": "claim", "text": "obvious"}]'
        from ebllm.bllm.agents import Problem
        p = Problem("dos", "difference of squares", "x^2-y^2", "product")
        ag = ModelAgent(move="construction", proposer=ScriptedProposer([reply]))
        res = Coordinator([ag]).run([p], rounds=1)
        self.assertIn("dos", res.solved)
        st = res.stats[ag.name]
        self.assertEqual((st.kept, st.weak_rejected + st.strong_rejected, st.unchecked), (1, 1, 1))

    def test_proposer_requests(self):
        seen = {}

        def opener(req, timeout):
            seen["url"], seen["body"] = req.full_url, json.loads(req.data)
            return json.dumps({"content": [{"type": "text", "text": "[]"}]}).encode()
        os.environ["ANTHROPIC_API_KEY"] = "test"
        try:
            pr = ModelProposer("anthropic", opener=opener)
            self.assertEqual(pr.complete("hi"), "[]")
        finally:
            del os.environ["ANTHROPIC_API_KEY"]
        self.assertTrue(seen["url"].endswith("/v1/messages"))
        self.assertEqual(seen["body"]["messages"][0]["content"], "hi")
        self.assertEqual(extract_json_list('{"a": 1}\n{"b": 2}'), [{"a": 1}, {"b": 2}])

    def test_lean_tactic_candidates(self):
        ag = LeanTacticAgent()
        c = ag.propose(LEAN_PROBLEMS[0], Vault(), random.Random(0), [])
        self.assertTrue(all(x.kind == "lean" and ":= by" in x.statement["source"] for x in c))
        bad = Candidate("n", "lean", dict(theorem="t", source="theorem t : True := by native_decide"))
        self.assertFalse(LeanCheck().run(bad, random.Random(0)).passed)

    def test_vault_round_trip(self):
        res = Coordinator().run(DEMO_PROBLEMS[:3], rounds=2)
        with tempfile.TemporaryDirectory() as d:
            res.vault.write(d)
            self.assertTrue(os.path.exists(os.path.join(d, "BLLM index.md")))
            self.assertEqual(Vault.load(d).notes.keys(), res.vault.notes.keys())


class TestGapLaw(unittest.TestCase):
    def setUp(self):
        self.data = gap.load_idea_gap()
        self.pi = self.data["shares"]["Human"]["opportunity"]

    def test_lower_bound_and_equality(self):
        rng = random.Random(3)
        opt = gap.optimal_cost(self.pi)
        self.assertAlmostEqual(gap.search_cost(self.pi, gap.optimal_profile(self.pi)), opt, places=12)
        for _ in range(200):
            q = [rng.random() for _ in self.pi]
            self.assertGreaterEqual(gap.search_cost(self.pi, q), opt - 1e-12)

    def test_chi2_identity_and_mixture_bound(self):
        rng = random.Random(4)
        r = gap.optimal_profile(self.pi)
        opt = gap.optimal_cost(self.pi)
        for _ in range(100):
            q = [rng.random() + 1e-3 for _ in self.pi]
            self.assertAlmostEqual(gap.search_cost(self.pi, q), opt * (1 + gap.chi2(r, q)), places=9)
            lam = rng.uniform(0.05, 1)
            self.assertLessEqual(gap.search_cost(self.pi, gap.mix(q, r, lam)), gap.mix_bound(self.pi, lam) + 1e-9)

    def test_copying_the_needs_costs_K(self):
        self.assertAlmostEqual(gap.search_cost(self.pi, self.pi), len(self.pi))

    def test_measured_gap(self):
        rows = {g.source: g for g in gap.idea_gap_table("opportunity", self.data)}
        self.assertAlmostEqual(rows["Claude-Sonnet-4.6"].tvd, 0.351, delta=0.002)   # Table 1 of arXiv:2607.01233
        self.assertAlmostEqual(rows["Human"].ratio, 7 / gap.optimal_cost(self.pi))
        for name, g in rows.items():
            if name not in ("Human", "square-root sampling"):
                self.assertTrue(1.9 < g.ratio < 4.3, name)
                self.assertLess(g.half_cost / rows["square-root sampling"].cost, 1.35)
                self.assertLess(g.steer, 1 / 1.1)

    def test_learning_converges(self):
        a = gap.learning_curve(self.pi, 10, trials=300)
        b = gap.learning_curve(self.pi, 400, trials=300)
        self.assertGreater(a, b)
        self.assertLess(b, 1.01)

    def test_bridge_simulation(self):
        q = self.data["shares"]["GPT-OSS-120B"]["opportunity"]
        out = gap.bridge_simulation(self.pi, q, problems=1500, window=1500, lam=0.5)
        self.assertLess(out["bllm"][0], 0.5 * out["llm"][0])


class TestNeuro(unittest.TestCase):
    def test_selector_samples_square_root(self):
        s = neuro.SpikingSelector(list("abcd"))
        for k, c in enumerate([30, 10, 3, 0]):
            for _ in range(c):
                s.reward(k)
        for x, y in zip(s.probabilities(), s.target()):
            self.assertAlmostEqual(x, y, places=12)
        rng = random.Random(2)
        f = [0] * 4
        for _ in range(3000):
            f[s.race(rng)] += 1
        for x, y in zip(f, s.target()):
            self.assertLess(abs(x / 3000 - y), 0.03)
        self.assertAlmostEqual(sum(s.rates()), s.rho0)

    def test_order_is_a_permutation(self):
        s = neuro.SpikingSelector(list("abcde"))
        self.assertEqual(sorted(s.order(random.Random(0))), list(range(5)))

    def _worm(self, d):
        path = os.path.join(d, "edges.csv")
        rows = ["Source,Target,Weight,Type", "ASHL,AVAL,5,chemical", "AVAL,DA01,4,chemical",
                "AVAL,AVAR,2,electrical", "AVAR,AVAL,2,electrical", "AWCL,AIYL,6,chemical",
                "AIYL,AVAR,3,chemical", "AVAR,DA01,2,chemical", "DA01,mu_body,7,chemical"]
        open(path, "w").write("\n".join(rows) + "\n")
        return neuro.load_edge_list(path)

    def test_processing_depth_orders_sensory_before_motor(self):
        with tempfile.TemporaryDirectory() as d:
            g = self._worm(d)
            z, i = g.processing_depth(), g.index
            self.assertLess(z[i["ASHL"]], z[i["AVAL"]])
            self.assertLess(z[i["AVAL"]], z[i["DA01"]])
            self.assertLess(z[i["DA01"]], z[i["mu_body"]])
            self.assertAlmostEqual(sum(z), 0, places=6)

    def test_reservoir_remembers(self):
        with tempfile.TemporaryDirectory() as d:
            g = self._worm(d)
        mc = neuro.memory_capacity(neuro.Reservoir(g), delays=(1,), steps=300, washout=50)
        self.assertGreater(mc[1], 0.3)

    def test_flywire_csv_and_h01(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "fw.csv")
            open(p, "w").write("pre_pt_root_id,post_pt_root_id,neuropil,syn_count\n1,2,AL_L,10\n1,3,LH_L,3\n"
                               "2,3,LH_L,20\n3,4,MB_CA_L,8\n1,4,AL_L,2\n")
            g = neuro.load_flywire_neuropils(p)
            self.assertEqual(g.edges[(g.index["AL_L"], g.index["LH_L"])], 20.0)
            self.assertEqual(g.edges[(g.index["LH_L"], g.index["MB_CA_L"])], 8.0)
            self.assertEqual(len(g.edges), 2)
            h = os.path.join(d, "h01.csv")
            open(h, "w").write("x,y,z,celltype,layer\n1000,2000,30,PYRAMIDAL,Layer 3\n5,5,5,ASTROCYTE,Layer 1\n")
            s = neuro.load_h01_somas(h)
            self.assertEqual(len(s), 2)
            self.assertAlmostEqual(s[0]["x"], 8.0)


class TestTasks(unittest.TestCase):
    def test_all_tasks_validate(self):
        t = load_tasks()
        self.assertGreaterEqual(len(t), 14)
        self.assertEqual({k for k, v in t.items() if v["status"] == "open"}, {"hodge", "yangmills"})
        self.assertEqual(t["fermat"]["formal"]["fork"], "https://github.com/creelie/fermats-last-theorem-machine")

    def test_validation_refuses_unsupported_proof(self):
        t = json.loads(json.dumps(load_tasks()["hodge"]))
        t["steps"][3]["status"] = "proved"
        with self.assertRaises(ValueError):
            validate(t)

    def test_cli(self):
        for argv in (["tasks"], ["attack", "yangmills"], ["gap"], ["schedule", "1,2,3"], ["providers"],
                     ["bridge", "--problems", "200", "--window", "200"]):
            buf = io.StringIO()
            with redirect_stdout(buf):
                self.assertEqual(main(argv), 0)
            self.assertTrue(buf.getvalue())


class TestFrontierAndWitnesses(unittest.TestCase):
    """The frontier report and the witnesses of Erdos problem 1183."""

    def test_frontier_diagonalised_targets(self):
        from ebllm.bllm import frontier
        m = {r["target"]: r for r in frontier.report()}
        assert m["B"]["open"] == ["B.3.gt", "B.general"]
        assert m["Chowla"]["open"] == ["C.even.log", "C.k3.ord", "C.full"]
        assert m["Chowla"]["counts"]["claimed"] == 1
        assert m["E1183"]["closure_pct"] == 0.0
        for t in frontier.targets().values():
            for p in t.pieces:
                assert p.status != "open" or p.missing

    def test_erdos1183_witnesses_match_chain_bound(self):
        import os
        path = os.path.join(os.path.dirname(__file__), "..", "experiments", "erdos1183", "witnesses.txt")
        rows = [l.split() for l in open(path) if l.strip() and not l.startswith("#")]
        for n, s, _ in rows:
            assert int(s) - 1 == (int(n) + 2) // 2  # no colouring forces size s, the chain bound forces s - 1

    def test_level_witnesses_attain_the_values(self):
        import os
        import sys
        here = os.path.join(os.path.dirname(__file__), "..", "experiments", "erdos1183")
        sys.path.insert(0, here)
        from levelmono import has_mono
        from ebllm.bllm.frontier import ERDOS_1183_VALUES
        for line in open(os.path.join(here, "level_witnesses.txt")):
            if line.startswith("#") or not line.strip():
                continue
            n, f, w = line.split()
            n, f = int(n), int(f)
            assert len(w) == n + 1 and ERDOS_1183_VALUES[n] == f
            if n <= 14:
                pat = [int(c) for c in w]
                assert has_mono(pat, f) and not has_mono(pat, f + 1)


if __name__ == "__main__":
    unittest.main()
