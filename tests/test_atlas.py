import unittest

from ebllm.bllm import atlas as A
from ebllm.bllm import barriers as B


class TestAtlas(unittest.TestCase):
    def setUp(self):
        self.atlas = A.load()

    def test_bundled_atlas_is_well_formed(self):
        self.assertEqual(A.check(self.atlas), [])
        self.assertEqual(set(self.atlas["targets"]), {"hodge", "strings", "seed", "yang-mills"})

    def test_every_target_has_walls_and_routes(self):
        for name, row in A.counts(self.atlas).items():
            self.assertGreater(row["walls"], 0, name)
            self.assertGreater(row["routes"], 0, name)

    def test_the_walls_with_predicates_are_in_the_ledger(self):
        ledger = {b.id for b in B.BARRIERS}
        for want in ("ym.forest-ceiling", "ym.no-convexity", "hodge.chain-multipliers", "hodge.hk-carriers-trivial"):
            self.assertIn(want, ledger)
        atlas_ids = {f"{'ym' if t == 'yang-mills' else t}.{w['id']}" for t, tt in self.atlas["targets"].items() for w in tt["walls"]}
        for b in B.BARRIERS:
            self.assertIn(b.id, atlas_ids, b.id)

    def test_nothing_unrefereed_is_established(self):
        for t in self.atlas["targets"].values():
            for x in t["walls"] + t["routes"]:
                text = (x.get("statement", "") + x.get("text", "") + x.get("source", "")).lower()
                if "unrefereed" in text:
                    self.assertNotEqual(x["status"], "established", x["id"])

    def test_check_reports_a_bad_status(self):
        bad = {"targets": {"x": {"statement": "", "verdict": "", "walls": [
            {"id": "w", "statement": "", "source": "", "hypothesis": "", "breaker": "", "status": "proved"}], "routes": []}}}
        self.assertTrue(any("status" in e for e in A.check(bad)))


if __name__ == "__main__":
    unittest.main()
