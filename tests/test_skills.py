import contextlib
import io
import json
import unittest

from ebllm import cli
from ebllm.bllm import selfmod as S
from ebllm.bllm import skills as K

from test_selfmod import FIXES, toy_attempt, toy_diagnose, toy_propose


def rec(target, n, outcome, diagnosis="", kind=None, rule="r", new="v", retry=""):
    c = S.Change(rule, kind, "", new, "m") if kind else None
    return S.Record(target, n, 0, outcome, diagnosis=diagnosis, change=c, retry=retry)


class Trajectories(unittest.TestCase):
    def test_status(self):
        closed = [rec("a", 1, "failed", "generator", "strategy", retry="failed"),
                  rec("a", 2, "failed", "scale", "reduction", retry="closed"), rec("a", 3, "closed")]
        failed = [rec("b", 1, "failed", "generator", "reduction", retry="failed"),
                  rec("b", 2, "failed", "generator")]
        open_ = [rec("c", 1, "failed", "generator", "reduction")]
        stopped = [rec("d", 1, "stopped", "retrieval", "retrieval", retry="stopped"), rec("d", 2, "stopped", "retrieval")]
        got = [K.trajectory("x", t).status for t in (closed, failed, open_, stopped)]
        self.assertEqual(got, ["strategy", "pattern", "open", "stopped"])
        e = K.trajectory("x", closed)
        self.assertEqual(e.steps, ("generator", "scale"))
        self.assertEqual(e.pairs(), {("generator", "strategy"), ("scale", "reduction")})

    def test_whole_run_credit_beats_next_attempt(self):
        """A change needed but not sufficient: its own retry fails and the run closes.  The playbook, which
        sees only the next attempt, sinks the kind below untried ones; the skill memory puts it first."""
        log = []
        for i in range(3):
            log += [rec(f"x{i}", 1, "failed", "generator", "library", new=f"l{i}", retry="failed"),
                    rec(f"x{i}", 2, "failed", "scale", "reduction", new=f"q{i}", retry="closed"), rec(f"x{i}", 3, "closed")]
        pb = S.Playbook().learn(log)
        self.assertEqual(pb.rank("generator")[:3], ["strategy", "representation", "library"])
        m = K.SkillMemory().add("t", log)
        self.assertEqual(m.rank("generator", "", pb)[:2], ["library", "strategy"])
        self.assertEqual([x.change.kind for _, x in K.needed_not_sufficient({"t": log})], ["library"] * 3)

    def test_pruning(self):
        log = []
        for i in range(3):
            log += [rec(f"z{i}", 1, "failed", "generator", "reduction", rule="target", new="one gadget", retry="failed"),
                    rec(f"z{i}", 2, "failed", "generator")]
        m = K.SkillMemory().add("t", log)
        self.assertEqual(m.uses("generator", "reduction"), (3, 0))
        self.assertTrue(m.pruned("generator", "reduction"))
        self.assertEqual(m.rank("generator")[-1], "reduction")
        self.assertTrue(m.refused(S.Change("target", "reduction", "", "one gadget", "m")))
        self.assertFalse(m.refused(S.Change("target", "reduction", "", "two gadgets", "m")))
        two = K.SkillMemory().add("t", log[:4])
        self.assertFalse(two.pruned("generator", "reduction"))  # two uses are not enough

    def test_open_and_stopped_count_for_nothing(self):
        log = [rec("c", 1, "failed", "generator", "reduction"),
               rec("d", 1, "stopped", "generator", "reduction", retry="stopped"), rec("d", 2, "stopped", "generator")]
        m = K.SkillMemory().add("t", log)
        self.assertEqual(m.uses("generator", "reduction"), (0, 0))
        self.assertEqual(m.kappa("generator", "reduction", m.retrieve("generator")[0]), 0)

    def test_ending_in_a_stop_counts_for_nothing(self):
        """A check that rejects a false route on an open conjecture is followed by failures and then a stop;
        the run ended in a verdict on the target, so its changes are not patterns to avoid."""
        log = [rec("e", 1, "failed", "overclaim", "check", retry="failed"),
               rec("e", 2, "failed", "overclaim", "check", new="w", retry="stopped"), rec("e", 3, "stopped", "scale")]
        self.assertEqual(K.trajectory("x", log).status, "stopped")
        m = K.SkillMemory().add("t", log)
        self.assertEqual(m.uses("overclaim", "check"), (0, 0))


class LoopWithSkills(unittest.TestCase):
    def test_loop_writes_the_trajectory(self):
        m = K.SkillMemory()
        loop = S.FailLoop(toy_attempt, toy_diagnose, toy_propose,
                          S.RuleBook({"planarity": "kuratowski", "generation": "random"}), skills=m, area="toy")
        log = loop.run("toy")
        self.assertEqual(log[-1].outcome, "closed")
        self.assertEqual([e.status for e in m.edges], ["strategy"])
        self.assertEqual(m.edges[0].pairs(), {("filter-cost", "representation"), ("generator", "strategy")})
        self.assertEqual(m.rank("filter-cost", "toy")[0], "representation")
        self.assertEqual([x.change.kind for _, x in K.needed_not_sufficient({"toy": log})], ["representation"])

    def test_refused_change_is_not_applied(self):
        bad = [rec(f"z{i}", 1, "failed", "filter-cost", "representation", rule="planarity", new="book",
                   retry="failed") for i in range(3)]
        bad = [r for i in range(3) for r in (bad[i], rec(f"z{i}", 2, "failed", "filter-cost"))]
        m = K.SkillMemory().add("t", bad)
        loop = S.FailLoop(toy_attempt, toy_diagnose, toy_propose,
                          S.RuleBook({"planarity": "kuratowski", "generation": "random"}), skills=m)
        log = loop.run("toy")
        # the pruned kind goes to the end, so the strategy change is tried first; the planar frames are then
        # refused outright, and the loop stops without ever applying them
        self.assertEqual([r.change.kind for r in log if r.change], ["strategy"])
        self.assertIn("no change", log[-1].note)
        self.assertEqual(loop.book.get("planarity"), "kuratowski")


class BundledLog(unittest.TestCase):
    def test_bundled(self):
        runs = S.load_log()
        m = K.SkillMemory.from_log(runs)
        r = m.report()
        self.assertEqual(r["trajectories"], 29)
        self.assertEqual(r["status"], {"strategy": 18, "open": 7, "stopped": 3, "pattern": 1})
        self.assertFalse(any(p["pruned"] for p in r["pairs"]))
        nns = K.needed_not_sufficient(runs)
        self.assertEqual([(x.target, x.change.kind) for _, x in nns],
                         [("Steinberg gadget (k = 5)", "mode"), ("Steinberg gadget (k = 5)", "representation"),
                          ("Seed conjecture, uniform bound (d = 4)", "representation"),
                          ("Proportion of simple zeros on the line", "check"),
                          ("Proportion of simple zeros on the line", "check"),
                          ("Proportion of simple zeros on the line", "check"),
                          ("Union-closed sets conjecture", "retrieval"),
                          ("Lower bounds for g^(d)(8)", "representation")])
        pattern = [e for e in r["edges"] if e["status"] == "pattern"]
        self.assertEqual([(e["run"], e["target"]) for e in pattern], [("strings", "Geometric Selection Conjecture")])
        pb = S.Playbook().learn([x for rs in runs.values() for x in rs])
        # whole-run credit changes the choice after three diagnoses: after an overclaim the checks that ran
        # in runs that advanced go first, where the playbook, seeing their failed next attempts, picks scope
        differ = {"overclaim": (["check", "scope", "strategy"], ["scope", "check", "strategy"]),
                  "scale": (["strategy", "reduction", "budget"], ["reduction", "strategy", "representation"]),
                  "representation": (["representation", "check", "reduction"],
                                     ["representation", "reduction", "check"])}
        for d in S.KINDS:
            if d in differ:
                self.assertEqual((m.rank(d, "", pb)[:3], pb.rank(d)[:3]), differ[d], d)
            else:
                self.assertEqual(m.rank(d, "", pb)[:3], pb.rank(d)[:3], d)

    def test_cli(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = cli.main(["skills", "--json"])
        self.assertEqual(rc, 0)
        out = json.loads(buf.getvalue())
        self.assertEqual(out["trajectories"], 29)
        self.assertEqual(len(out["needed_not_sufficient"]), 8)


if __name__ == "__main__":
    unittest.main()
