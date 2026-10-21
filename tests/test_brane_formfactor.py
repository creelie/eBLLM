import unittest
from fractions import Fraction

from ebllm.construct import brane_formfactor as B


class TestBraneFormFactor(unittest.TestCase):
    def test_ein_series_and_continued_fraction_agree(self):
        self.assertAlmostEqual(B.ein(1.0), 0.7965995992970531, places=14)
        self.assertAlmostEqual((B.ein(5.00001) - B.ein(4.99999)) / 2e-5, (1 - 2.718281828459045 ** -5) / 5, places=6)
        self.assertAlmostEqual(B.ein(30.0), 3.4011973816621555 + B.EULER, places=10)   # log 30 + gamma

    def test_cell_model_response_obeys_the_conditions_and_the_obvious_factor_has_resonances(self):
        self.assertEqual(B.response_conditions(), [])
        self.assertTrue(any(s.startswith("(S1)") for s in B.response_conditions(B.no_resonance_factor)))
        for w in B.resonances(3):
            self.assertLess(abs(B.no_resonance_factor(w)), 1e-12)
            self.assertGreater(abs(w.imag), 0.0)      # off the real axis: a complex pole of the propagator

    def test_form_factor_grows_like_a_power_with_the_euler_constant(self):
        for n in (4, 6):
            for z in (10.0, 30.0, -30.0):
                self.assertAlmostEqual(B.asymptotic_ratio(z, n), 1.0, places=9)
        self.assertEqual(B.polynomial_zeros_count([1.0, 0.0, 1.0]), 2)
        self.assertEqual(B.polynomial_zeros_count([1.0]), 0)

    def test_power_counting_threshold_is_four(self):
        self.assertEqual(B.power_table()[4], [4, -2, -8, -14, -20])
        self.assertEqual(B.power_table()[3], [4, 0, -4, -8, -10])
        for n in range(4, 12):
            self.assertTrue(B.finite_beyond_one_loop(n))
            self.assertTrue(B.finite_beyond_one_loop(n, m_sigma=n - 2))   # every fine graining allowed by (G)
            self.assertEqual(B.omega_bar(n, 1), 4)
        for n in range(0, 4):
            self.assertFalse(B.finite_beyond_one_loop(n))

    def test_merging_lemma_survives_exhaustive_search(self):
        self.assertIsNone(B.merging_lemma_counterexample(L_max=6))
        self.assertEqual(B.max_excess(3, 12, 5), 3)       # the star (8, 2, 2): one vertex takes every extra line

    def test_pole_matrix_and_tuning(self):
        self.assertEqual(B.det3(B.POLE_MATRIX), Fraction(-24))
        for b in ((1, 2, 3), (Fraction(7, 3), Fraction(-1, 2), 0), (0, 0, 1)):
            self.assertEqual(B.poles_after_tuning(b, B.tuning(*b)), (0, 0, 0))
        self.assertNotEqual(B.poles_after_tuning((1, 2, 3), (0, 0, 0)), (0, 0, 0))

    def test_vacuum_energy_and_the_mellin_identity(self):
        self.assertAlmostEqual(B.zero_point_energy(4, 1.0), 12 / (64 * 3.141592653589793 ** 2))
        self.assertAlmostEqual(B.cosmological_constant(4, 1.0, 1.0),
                               32 * 3.141592653589793 * B.zero_point_energy(4, 1.0) / 4)
        self.assertAlmostEqual(B.mellin_ein(-0.5) / B.gamma_over_s(-0.5), 1.0, places=6)
        self.assertAlmostEqual(B.mellin_ein(-0.25) / B.gamma_over_s(-0.25), 1.0, places=3)

    def test_free_euclidean_graviton_is_not_reflection_positive(self):
        self.assertGreater(B.time_slice_covariance(1.0), B.time_slice_covariance(4.0), 0.0)
        w = B.reflection_positivity_witness(4)
        self.assertIsNotNone(w)
        self.assertLess(w[1], -5e-7)
        self.assertTrue(11.0 <= w[0] <= 15.0)

    def test_breakdown_energy_lies_between_1_4_and_1_9(self):
        for r in (1e-2, 1e-10, 1e-20, 1e-40):
            self.assertTrue(1.4 <= B.breakdown_energy(r) <= 1.9, r)
        self.assertLess(B.breakdown_energy(1e-2), B.breakdown_energy(1e-40))

    def test_check_and_the_typed_chain(self):
        self.assertEqual(B.check(4), [])
        self.assertTrue(B.check(3)[0].startswith("power counting"))
        gives = {c["gives"] for c in B.CONSTRUCTIONS}
        for c in B.CONSTRUCTIONS:
            for need in c["needs"]:
                self.assertTrue(need in gives or need == "cell-model", need)
        self.assertEqual(B.CONSTRUCTIONS[-1]["gives"], "perturbative-uv-finiteness")


if __name__ == "__main__":
    unittest.main()
