import math
import unittest
from fractions import Fraction

from ebllm.construct import theophys as T


class TestTheoPhysEval(unittest.TestCase):
    def test_pi_series_converges_to_pi(self):
        for lam in (Fraction(1), Fraction(3, 2), Fraction(5), Fraction(21, 2), Fraction(30)):
            self.assertLess(abs(float(T.pi_partial(40, lam)) - math.pi), 2e-5, lam)
        self.assertLess(abs(float(T.pi_partial(40, Fraction(21, 2))) - math.pi), 1e-11)

    def test_large_parameter_limit_is_madhava_leibniz(self):
        for n in range(1, 40):
            self.assertEqual(T.leibniz_limit_exact(n), T.leibniz_term(n))
        # and the finite-l term approaches it
        self.assertLess(abs(float(T.pi_term(7, Fraction(10 ** 9)) - T.leibniz_term(7))), 1e-6)

    def test_refuter_leibniz_is_far_slower(self):
        lei = abs(float(T.leibniz_partial(40)) - math.pi)
        self.assertGreater(lei, 1e-2)
        self.assertLess(T.pi_errors([Fraction(21, 2)], 40)[Fraction(21, 2)], lei * 1e-9)

    def test_gegenbauer_value_at_minus_one(self):
        for d in (4, 5, 7, 10):
            lam = Fraction(d - 3, 2)
            for j in range(6):
                self.assertEqual(T.gegenbauer(j, lam, Fraction(-1)), T.gegenbauer_at_minus_one(j, lam))

    def test_hidden_zero_relations_of_the_problem(self):
        self.assertEqual(T.partial_wave_weights(1, 4), [1, -1])          # c0 = c1
        self.assertEqual(T.partial_wave_weights(2, 4), [1, -1, 1])       # c0 - c1 + c2 = 0
        self.assertEqual(T.solve_last_alpha([1], 1), 1)                  # alpha0 = alpha1
        a0, a1 = Fraction(3), Fraction(5)
        a2 = T.solve_last_alpha([a0, a1], 2)
        self.assertEqual(a1 - a0 / 2, 2 * a2)
        c = [Fraction(7), Fraction(-2), Fraction(5)]
        c3 = T.solve_last_coefficient(c, 7)
        self.assertEqual(c3, Fraction(13, 4))
        self.assertEqual(T.residue_at(c + [c3], 7, Fraction(-1)), 0)
        self.assertEqual(T.solve_last_alpha([5, -1, 2], 3), Fraction(26, 27))
        self.assertEqual(T.xi(), Fraction(11219, 27))

    def test_refuter_residue_without_the_zero(self):
        for d in (4, 7):
            self.assertNotEqual(T.residue_at([0, 0, 1], d, Fraction(-1)), 0)

    def test_check_is_clean(self):
        self.assertEqual(T.check(), [])


if __name__ == "__main__":
    unittest.main()
