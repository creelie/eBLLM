import contextlib
import io
import json
import os
import tempfile
import unittest

from ebllm import cli
from ebllm.bllm import selfmod as S
from ebllm.bllm.memory import Memory


def toy_attempt(target, book):
    """A target that needs two rule changes: planar by construction, then goal-directed generation."""
    if book.get("planarity") != "book":
        return "failed", "search", "99% of cuts were planarity cuts"
    if book.get("generation") != "goal":
        return "failed", "generator", "no survivor in 1000 candidates"
    return "closed", "", "found"


def toy_diagnose(outcome, part, evidence):
    return "filter-cost" if "planarity" in evidence else "generator"


FIXES = {
    "representation": S.Change("planarity", "representation", "kuratowski", "book", "share of cuts on planarity"),
    "strategy": S.Change("generation", "strategy", "random", "goal", "tries to a survivor"),
}


def toy_propose(diagnosis, ranked, book, log):
    for kind in ranked:
        c = FIXES.get(kind)
        if c is not None and book.get(c.rule) == c.old:
            return c
    return None


class RuleBookGuards(unittest.TestCase):
    def test_apply_versions_and_history(self):
        b = S.RuleBook({"planarity": "kuratowski"})
        b2 = b.apply(FIXES["representation"])
        self.assertEqual((b.version, b2.version), (0, 1))
        self.assertEqual(b.get("planarity"), "kuratowski")
        self.assertEqual(b2.get("planarity"), "book")

    def test_change_must_name_a_measurement_and_match_the_old_value(self):
        b = S.RuleBook({"planarity": "kuratowski"})
        with self.assertRaises(ValueError):
            b.apply(S.Change("planarity", "representation", "kuratowski", "book", ""))
        with self.assertRaises(ValueError):
            b.apply(S.Change("planarity", "representation", "frames", "book", "x"))
        with self.assertRaises(ValueError):
            b.apply(S.Change("planarity", "magic", "kuratowski", "book", "x"))


class Playbook(unittest.TestCase):
    def test_prior_order(self):
        p = S.Playbook()
        self.assertEqual(p.rank("filter-cost")[0], "representation")
        self.assertEqual(p.rank("rules-silent")[0], "library")
        with self.assertRaises(ValueError):
            p.rank("unknown")

    def test_log_overrides_prior(self):
        p = S.Playbook()
        c = S.Change("x", "budget", "a", "b", "seconds")
        recs = [S.Record("t", i, 0, "failed", diagnosis="filter-cost", change=c, retry="closed") for i in range(1, 6)]
        p.learn(recs)
        self.assertEqual(p.rank("filter-cost")[0], "budget")


class Loop(unittest.TestCase):
    def test_two_changes_then_closed(self):
        loop = S.FailLoop(toy_attempt, toy_diagnose, toy_propose,
                          S.RuleBook({"planarity": "kuratowski", "generation": "random"}))
        log = loop.run("toy")
        self.assertEqual([r.outcome for r in log], ["failed", "failed", "closed"])
        self.assertEqual([r.change.kind for r in log[:2]], ["representation", "strategy"])
        self.assertEqual([r.retry for r in log[:2]], ["failed", "closed"])
        self.assertEqual(S.check_log({"toy": log}), [])

    def test_stops_when_no_change_is_left(self):
        loop = S.FailLoop(toy_attempt, toy_diagnose, lambda *a: None, S.RuleBook({"planarity": "kuratowski"}))
        log = loop.run("toy")
        self.assertEqual(len(log), 1)
        self.assertIn("no change", log[0].note)

    def test_memory_keeps_every_attempt(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "m.sqlite")
            m = Memory(path)
            S.FailLoop(toy_attempt, toy_diagnose, toy_propose,
                       S.RuleBook({"planarity": "kuratowski", "generation": "random"}), memory=m).run("toy")
            m2 = Memory(path)
            recs = m2.attempts("toy")
            self.assertEqual(len(recs), 3)
            self.assertEqual(recs[0]["change"]["new"], "book")
            self.assertEqual(m2.stats()["attempts"], 3)


class BundledLog(unittest.TestCase):
    def test_consistent(self):
        runs = S.load_log()
        self.assertIn("construction", runs)
        self.assertEqual(S.check_log(runs), [])

    def test_construction_run(self):
        p = S.patterns(S.load_log()["construction"])
        self.assertEqual(p["changes"], 13)
        self.assertEqual(p["advanced"], 3)
        self.assertEqual(p["outcomes"]["closed"], 3)

    def test_seed_run(self):
        runs = S.load_log()
        self.assertIn("seed", runs)
        p = S.patterns(runs["seed"])
        self.assertEqual(p["changes"], 8)
        self.assertEqual(p["advanced"], 6)
        self.assertEqual(p["outcomes"]["closed"], 2)

    def test_hodge_run(self):
        runs = S.load_log()
        self.assertIn("hodge", runs)
        p = S.patterns(runs["hodge"])
        self.assertEqual(p["changes"], 3)
        self.assertEqual(p["advanced"], 2)
        self.assertEqual(p["outcomes"]["closed"], 0)

    def test_runs_of_other_attacks(self):
        runs = S.load_log()
        want = {"riemann": (6, 1, 0), "erdos-straus": (4, 2, 2), "union-closed": (2, 1, 0),
                "lonely-runner": (3, 2, 0), "strings": (2, 1, 1)}
        for run, (changes, advanced, closed) in want.items():
            p = S.patterns(runs[run])
            self.assertEqual((p["changes"], p["advanced"], p["outcomes"]["closed"]), (changes, advanced, closed), run)
        # an open conjecture is never recorded as closed
        for run, target in (("riemann", "Riemann hypothesis"), ("erdos-straus", "Erdős-Straus conjecture"),
                            ("union-closed", "Union-closed sets conjecture"),
                            ("strings", "Geometric Selection Conjecture")):
            self.assertNotIn("closed", {r.outcome for r in runs[run] if r.target == target}, target)

    def test_cli(self):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = cli.main(["modlog", "--json"])
        self.assertEqual(rc, 0)
        out = json.loads(buf.getvalue())
        self.assertEqual(out["errors"], [])


if __name__ == "__main__":
    unittest.main()
