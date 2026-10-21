import copy
import json
import os
import unittest

from ebllm.bllm import triage as T

EXAMPLE = os.path.join(os.path.dirname(T.__file__), "data", "triage.example.json")


class TestTriage(unittest.TestCase):
    def setUp(self):
        with open(EXAMPLE) as f:
            self.data = json.load(f)

    def test_example_ranks_and_excludes(self):
        rep = T.triage(self.data)
        by = {r["id"]: r for r in rep["ranking"]}
        self.assertFalse(by["hodge-f2"]["go"])
        self.assertIn("closability below min_closability", by["hodge-f2"]["no_go_reasons"])
        self.assertFalse(by["diophantine-h22"]["go"])
        self.assertEqual(rep["first"], "bridge-index-13-rest")
        self.assertTrue(all(r["rank"] is None for r in rep["ranking"] if not r["go"]))

    def test_constraints_beat_value(self):
        d = copy.deepcopy(self.data)
        d["candidates"][0]["value"] = 100
        d["candidates"][0]["closability"] = d["constraints"]["min_closability"] - 1
        rep = T.triage(d)
        self.assertFalse(next(r for r in rep["ranking"] if r["id"] == d["candidates"][0]["id"])["go"])

    def test_nothing_passes_means_no_attack(self):
        d = copy.deepcopy(self.data)
        d["constraints"]["min_closability"] = 100
        rep = T.triage(d)
        self.assertIsNone(rep["first"])
        self.assertIn("no attack is started", T.table(rep))

    def test_exact_rounding_and_reproducibility(self):
        self.assertEqual(T.ratio(1, 3), 0.333333)
        self.assertEqual(T.ratio(2, 3), 0.666667)
        self.assertEqual(T.ratio(1, 8), 0.125)
        self.assertEqual(T.triage(self.data), T.triage(copy.deepcopy(self.data)))

    def test_pareto_front(self):
        pts = {"a": (5, 5), "b": (4, 4), "c": (6, 1), "d": (5, 5)}
        self.assertEqual(T.pareto(pts), ["a", "c", "d"])

    def test_refuses_coerced_or_unknown_input(self):
        for mutate in (lambda d: d["candidates"][0].__setitem__("value", True),
                       lambda d: d["candidates"][0].__setitem__("value", 50.0),
                       lambda d: d["candidates"][0].__setitem__("hype", 1),
                       lambda d: d["weights"].update(value=0, closability=0, effort=0, risk=0),
                       lambda d: d["candidates"].append(copy.deepcopy(d["candidates"][0])),
                       lambda d: d.__setitem__("schema", "v0")):
            d = copy.deepcopy(self.data)
            mutate(d)
            with self.assertRaises(ValueError):
                T.triage(d)


if __name__ == "__main__":
    unittest.main()
