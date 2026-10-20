import unittest

from ebllm.bllm import atlas as A
from ebllm.bllm import superstring as S
from ebllm.bllm.frontier import CLOSED


class TestSuperstring(unittest.TestCase):
    def setUp(self):
        self.data = S.load()
        self.atlas = A.load()

    def test_bundled_data_is_well_formed(self):
        self.assertEqual(S.check(self.data, self.atlas), [])
        self.assertEqual(set(self.data["targets"]), {"hodge", "strings", "seed", "yang-mills"})

    def test_every_chain_ends_in_a_bypass_and_every_gap_has_an_attacker(self):
        for name, t in self.data["targets"].items():
            by = {a["id"]: a for a in t["attackers"]}
            self.assertEqual(by[t["chain"][-1]]["move"], "bypass", name)
            self.assertTrue(t["gaps"], name)
            for g in t["gaps"]:
                self.assertIn(g["attacker"], by, g["id"])

    def test_no_target_is_closed_by_the_bundled_data(self):
        res = S.run(self.data)
        for name, r in res.items():
            self.assertFalse(r["closed"], name)
            self.assertIsNotNone(r["first_stop"], name)
            self.assertTrue(r["verdict"].startswith("open: stops at "), name)
        self.assertEqual(res["hodge"]["first_stop"], "h.semiregular-jacobian")
        self.assertEqual(res["strings"]["first_stop"], "s.definition-repair")
        self.assertEqual(res["seed"]["first_stop"], "seed.farm-finisher")
        self.assertEqual(res["yang-mills"]["first_stop"], "ym.cube4-certifier")

    def test_a_bypass_stage_never_closes_on_its_own(self):
        for t in self.data["targets"].values():
            last = next(a for a in t["attackers"] if a["id"] == t["chain"][-1])
            self.assertNotIn(last["status"], CLOSED)

    def test_a_self_checked_certificate_does_not_close(self):
        chain = self.data["targets"]["seed"]["chain"]
        ev = {cid: dict(kind="computed", checker="farm", producer="farm", ref="x") for cid in chain}
        r = S.run(self.data, "seed", ev)["seed"]
        self.assertFalse(r["closed"])
        self.assertEqual(r["first_stop"], chain[0])
        ev = {cid: dict(kind="claimed", checker="lean", producer="farm", ref="x") for cid in chain}
        self.assertFalse(S.run(self.data, "seed", ev)["seed"]["closed"])

    def test_independent_certificates_on_every_stage_close(self):
        chain = self.data["targets"]["seed"]["chain"]
        ev = {cid: dict(kind="lean-here", checker="lean", producer="farm", ref="x") for cid in chain}
        r = S.run(self.data, "seed", ev)["seed"]
        self.assertTrue(r["closed"])
        self.assertIsNone(r["first_stop"])
        # one stage short: still open, and the verdict names it
        del ev[chain[2]]
        r = S.run(self.data, "seed", ev)["seed"]
        self.assertFalse(r["closed"])
        self.assertEqual(r["first_stop"], chain[2])

    def test_check_reports_a_chain_that_does_not_end_in_a_bypass(self):
        bad = {"targets": {"x": {"gaps": [], "chain": ["a"], "attackers": [dict(
            id="a", zone="frontier", piece="", move="construction", method="", inputs=[], certificate="",
            stop_rule="", status="open", result="", source="")]}}}
        self.assertTrue(any("bypass" in e for e in S.check(bad)))
        bad["targets"]["x"]["attackers"][0]["zone"] = "nowhere"
        self.assertTrue(any("zone" in e for e in S.check(bad, self.atlas)))

    def test_roster_and_summary(self):
        rows = S.roster(self.data, zone="frontier")
        self.assertTrue(rows and all(r["zone"] == "frontier" for r in rows))
        text = "\n".join(S.summary(self.data, "hodge"))
        self.assertIn("stops at h.semiregular-jacobian", text)
        self.assertIn("h.bypass-last", text)


if __name__ == "__main__":
    unittest.main()
