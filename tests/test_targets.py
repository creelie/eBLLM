"""Tests of the headline targets: the gauge counts, the typed crossing and the per-step closure."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from ebllm.bllm import targets as T  # noqa: E402


class GaugeCounts(unittest.TestCase):
    def test_partner_counts(self):
        counts = {g: T.gauge_count(g) for g in T.GAUGES}
        self.assertEqual(counts["plain"]["neighbours"], [18])
        self.assertEqual(counts["temporal"]["neighbours"], [14])
        self.assertEqual(counts["one-per-plaquette"]["neighbours"], [12])
        self.assertEqual(counts["one-per-plaquette"]["fixed_per_plaquette"], [1])
        self.assertTrue(all(c["forest"] for c in counts.values()))

    def test_forest_bound(self):
        self.assertEqual(T.forest_lower_bound(4), 12)


class Crossing(unittest.TestCase):
    def test_ill_typed_cross_is_none(self):
        lib = {c.id: c for c in T.LIBRARY}
        self.assertIsNone(T.cross(lib["ym.dobrushin"], lib["h.markman"]))

    def test_network_finds_one_third(self):
        r = T.run("network", generations=4, per_gen=200, seed=0)
        nodes = {v["node"] for v in r["accepted"].values()}
        self.assertIn("YM.window.lower", nodes)

    def test_finite_subgroup_rejected(self):
        finite = [c for c in T.all_checks() if "finite subgroup" in c["statement"]]
        self.assertTrue(finite)
        self.assertTrue(all(c["outcome"] == "rejected" for c in finite))


class Closure(unittest.TestCase):
    def test_headline_shares(self):
        tree = T.headline_tree()
        r = T.run("network", generations=4, per_gen=200, seed=0)
        T.apply(tree, r["accepted"])
        ym, h = T.closure(tree, "YM"), T.closure(tree, "H")
        self.assertEqual((ym["proved"], ym["leaves"]), (3, 8))
        self.assertEqual((h["proved"], h["leaves"]), (2, 10))
        self.assertIn("YM.lean", ym["blocked"])


if __name__ == "__main__":
    unittest.main()
