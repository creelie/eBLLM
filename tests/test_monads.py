import unittest

from ebllm.construct import monads as M


class TestMonads(unittest.TestCase):
    def test_invariants_of_the_su5_dwork_monad(self):
        inv = M.invariants("P4[5]", (1,) * 5 + (2,) * 5, (3,) * 5)
        self.assertEqual(inv, {"c1": 0, "c2V": 50, "anomaly_slack": 0, "index": -75, "rank": 5})

    def test_quintic_three_family_list_matches_the_literature(self):
        # Braun 0909.5682 and Anderson-Gray-He-Lukas 0911.1569: exactly two, one on X/Z5, one on X/(Z5 x Z5)
        ok = {(r["B"], r["C"], r["group_order"]) for r in M.three_family_quintic() if r["equivariant_screen"]}
        self.assertEqual(ok, {((1,) * 6, (2,) * 3, 5), ((1,) * 5 + (2,) * 5, (3,) * 5, 25)})

    def test_scan_counts(self):
        self.assertEqual(len(M.scan("P4[5]")), 43)
        self.assertEqual(sum(len(M.scan(X)) for X in M.CICY), 77)

    def test_refuter_rejects_bad_vacua(self):
        self.assertEqual(M.refute("P4[5]", (1,) * 5 + (2,) * 5, (3,) * 5, 25), [])
        self.assertTrue(M.refute("P4[5]", (1, 1, 1, 2, 3), (4, 4), 25))      # fails the Heisenberg screen
        self.assertTrue(M.refute("P4[5]", (1, 1, 1), (2,), 5))               # c1 != 0
        self.assertTrue(M.refute("P4[5]", (1,) * 6, (2,) * 3, 25))           # index -15 is not -75
        self.assertTrue(M.refute("P4[5]", (1, 1, 1, 1, 1, 3), (2, 3, 3), 5))       # b_i >= c_j: not positive


if __name__ == "__main__":
    unittest.main()
