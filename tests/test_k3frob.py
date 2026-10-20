import unittest

from ebllm.construct import k3frob as K


class TestK3Frob(unittest.TestCase):
    def test_prime_field_traces_rerun(self):
        for p in (5, 7, 11, 17, 19):
            self.assertEqual(K.trace_T(p), K.TRACES_P[p], p)

    def test_weil_and_picard_number(self):
        v = K.verdict(7)
        self.assertTrue(v["on_unit_circle"])          # consistency of the counts with the Weil conjectures
        self.assertEqual(v["rho_bound"], 16)          # rho(R13) = 16: T has rank 6

    def test_not_real_multiplication(self):
        self.assertFalse(K.verdict(7)["rm_by_sqrt13_possible"])

    def test_refuter_sees_a_split_polynomial(self):
        # a product of a cubic over Q(sqrt13) with its conjugate must be detected as split
        import math
        r = math.sqrt(13)
        g = [1, 1 + r, 2, 3 - r]
        h = [1, 1 - r, 2, 3 + r]
        prod = [sum(g[i] * h[k - i] for i in range(4) if 0 <= k - i < 4) for k in range(7)]
        self.assertTrue(K.splits_over_real_quadratic(7, prod))

    def test_p5_has_extra_algebraic_classes(self):
        self.assertGreater(K.verdict(5)["rho_bound"], 16)   # at p = 5 the reduction gains classes, so p = 5 decides nothing


if __name__ == "__main__":
    unittest.main()
