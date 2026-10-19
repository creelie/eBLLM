import unittest

from ebllm.bllm import superbrain as S


class TestBenchmarks(unittest.TestCase):
    def test_six_benchmarks_one_passed(self):
        rows = S.scores()
        self.assertEqual([r["benchmark"] for r in rows], ["YM", "H", "B", "Chowla", "E1183", "MP"])
        self.assertEqual([r["benchmark"] for r in rows if r["passed"]], ["MP"])
        for r in rows:
            self.assertEqual(r["pass_line"], S.PASS_LINES[r["benchmark"]])

    def test_superbrain_is_not_claimed(self):
        verdict = S.superbrain(S.scores())
        self.assertFalse(verdict["superbrain"])
        self.assertEqual(verdict["of"], 6)
        self.assertTrue(verdict["statement"].endswith("so it is not claimed"))

    def test_the_passed_row_names_what_stays_open(self):
        mp = S.scores()[-1]
        self.assertIn("348", mp["partial"]["closed"])
        self.assertIn("sharp constant", mp["blocking"])


if __name__ == "__main__":
    unittest.main()
