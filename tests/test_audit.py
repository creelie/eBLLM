import os
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path

from ebllm.bllm import audit as AU


def tree(spec):
    """A temporary folder of check scripts and stored outputs, from {relative path: text}."""
    d = tempfile.mkdtemp()
    for rel, body in spec.items():
        p = Path(d, rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(textwrap.dedent(body))
    return d


class TestAudit(unittest.TestCase):
    def test_bundled_audit_counts_and_verdict(self):
        a = AU.load("desitter-scalar-self-mass")
        v = AU.verdict(AU.findings_of(a))
        self.assertEqual(v["counts"], {"substantive": 4, "absorbable": 6, "typo": 23, "confirmed": 31, "conclusion": 10})
        self.assertTrue(v["conclusion_survives"])
        self.assertEqual(len(a["stages"]), 9)
        self.assertNotIn("closed", v["label"].replace("closure", ""))
        rr = a["rerun"]
        self.assertEqual(rr["passed"], rr["runs"])

    def test_only_a_substantive_finding_changes_a_conclusion(self):
        with self.assertRaises(ValueError):
            AU.Finding("X1", "typo", changes_conclusion=True)
        with self.assertRaises(ValueError):
            AU.Finding("X2", "rumour")
        v = AU.verdict([AU.Finding("S9", "substantive", changes_conclusion=True), AU.Finding("C1", "typo")])
        self.assertFalse(v["conclusion_survives"])
        self.assertEqual(v["changed_by"], ["S9"])

    def test_normalisation_ignores_layout_and_timing_only(self):
        self.assertEqual(AU.compare("a  \r\nb\n\nelapsed: 1.2 s\n\n", "a\nb\n"), [])
        self.assertTrue(AU.compare("x = 1\n", "x = -1\n"))
        self.assertTrue(AU.compare("time steps: 3\n", ""))  # not a pure timing line

    def test_golden_runner_passes_a_faithful_tree(self):
        d = tree({"01_a/check.py": "print('ok 2')\n", "01_a/expected_output/check.txt": "ok 2\n",
                  "01_a/kexp.py": "import sys; print(int(sys.argv[1]) ** 2)\n",
                  "01_a/expected_output/kexp_N3.txt": "9\n", "01_a/expected_output/kexp_N4.txt": "16\n",
                  "01_a/helper.py": "X = 1\n"})
        res = AU.golden(d)
        self.assertTrue(res["passed"], res)
        self.assertEqual(res["tally"], {"PASS": 4})

    def test_golden_runner_refutes_drift_noise_and_orphans(self):
        d = tree({"01_a/check.py": "print('ok 3')\n", "01_a/expected_output/check.txt": "ok 2\n",
                  "01_a/helper.py": "print('noise')\n",
                  "01_a/expected_output/gone.txt": "1\n"})
        res = AU.golden(d)
        self.assertFalse(res["passed"])
        status = {r["run"]: r["status"] for r in res["results"]}
        self.assertEqual(status["01_a/check.py"], "FAIL")
        self.assertEqual(status["01_a/helper.py"], "FAIL")
        self.assertEqual(status["01_a/gone.py"], "ERROR")

    def test_empty_tree_does_not_pass(self):
        self.assertFalse(AU.golden(tempfile.mkdtemp())["passed"])


if __name__ == "__main__":
    unittest.main()
