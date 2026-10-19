import unittest
from fractions import Fraction

from ebllm.bllm import screens as S


class Liouville(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.x = 6000
        cls.h = round(cls.x ** 0.8)
        cls.lam = S.liouville(cls.x)

    def test_values(self):
        self.assertEqual(S.liouville(12)[1:], [1, -1, -1, 1, -1, 1, -1, -1, 1, 1, -1, -1])
        self.assertEqual(S.correlation(self.lam, 10, 1), sum(self.lam[n] * self.lam[n + 1] for n in range(1, 10)))

    def test_correlations_have_the_random_model_size(self):
        # the mean of C_k(x)^2 over h < k <= 2h is of order x, as for independent random signs
        m = S.mean_square_correlation(self.x, self.h, self.lam)
        self.assertTrue(0.3 * self.x < m < 3 * self.x, m)

    def test_the_collar_bound_is_rejected(self):
        # E_2(X, H) << X^2 / H bounds the mean square by X^2 / H^2, about 129 times too small here
        rejected, ratio = S.below_random_model(lambda x, h: x ** 2 / h ** 2, self.x, self.h, lam=self.lam)
        self.assertTrue(rejected)
        self.assertGreater(ratio, 100)

    def test_a_bound_of_the_random_model_size_passes(self):
        rejected, _ = S.below_random_model(lambda x, h: x, self.x, self.h, lam=self.lam)
        self.assertFalse(rejected)


class ErdosStraus(unittest.TestCase):
    def test_solutions_are_exact(self):
        for n in (5, 13, 73):
            for x, y, z in S.solutions(n):
                self.assertEqual(Fraction(1, x) + Fraction(1, y) + Fraction(1, z), Fraction(4, n))

    def test_type_one_solutions_exist(self):
        # the claim that every solution is of type II fails: 4/73 = 1/20 + 1/210 + 1/30660, and only 30660 = 73 * 420
        sol = S.solutions(73)
        self.assertIn((20, 210, 30660), sol)
        self.assertEqual(S.solution_type(73, (20, 210, 30660)), 1)
        self.assertIsNotNone(S.first_failure(lambda s: S.solution_type(73, s) == 2, sol))

    def test_the_divisor_claim_fails_at_97_and_7(self):
        # D = 2, k in {1, 2}: 101 and 113 are not divisible by 7
        self.assertFalse(S.divisor_in_progression(97, 7))
        self.assertTrue(S.divisor_in_progression(5, 3))  # 5 + 4 = 9
        self.assertEqual(S.first_failure(lambda c: S.divisor_in_progression(*c), [(5, 3), (97, 7)]), (97, 7))
        # for p = 97 no prime q = 3 mod 4 below 400 has such a divisor
        primes = [q for q in range(3, 400, 4) if all(q % d for d in range(2, q))]
        self.assertFalse(any(S.divisor_in_progression(97, q) for q in primes))


if __name__ == "__main__":
    unittest.main()
