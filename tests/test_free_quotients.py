import unittest

from ebllm.construct import free_quotients as F


class TestFreeQuotients(unittest.TestCase):
    def test_quintic_numbers(self):
        self.assertEqual(F.chern_numbers((5,), (1,) * 5), (5, 50, -200))
        self.assertEqual(F.euler_values(5, 50), (5, 15, 35))
        self.assertEqual(F.g_invariant((5,), (1,) * 5), 5)

    def test_known_free_actions_pass(self):
        # Z/5 x Z/5 acts freely on the Dwork quintic, and Z/3 x Z/3 on the bicubic
        self.assertTrue(F.free_order_allowed((5,), (1,) * 5, 25))
        self.assertTrue(F.free_order_allowed((3, 3), (1,) * 6, 9))

    def test_refuter_rejects_impossible_orders(self):
        self.assertFalse(F.free_order_allowed((5,), (1,) * 5, 2))
        self.assertFalse(F.free_order_allowed((6,), (1, 1, 1, 1, 2), 2))

    def test_seven_families_admit_no_free_action(self):
        trivial = sorted(k for k, (d, w) in F.ONE_PARAMETER.items() if F.g_invariant(d, w) == 1)
        self.assertEqual(trivial, sorted(["X6", "X10", "X3,2,2", "X6,6", "X4,3", "X6,4", "X6,2"]))

    def test_no_free_quotient_has_three_families(self):
        for k, (d, w) in F.ONE_PARAMETER.items():
            self.assertFalse(F.three_families_possible(d, w), k)

    def test_not_calabi_yau_is_rejected(self):
        with self.assertRaises(ValueError):
            F.chern_numbers((4,), (1,) * 5)


if __name__ == "__main__":
    unittest.main()
