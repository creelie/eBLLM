import unittest

from ebllm.construct import multitime_sym as M

try:
    import numpy  # noqa: F401
    HAVE_NUMPY = True
except ImportError:
    HAVE_NUMPY = False


class TestMultitimeSym(unittest.TestCase):
    def test_certificate_checks(self):
        self.assertEqual(M.check(), [])

    def test_nishino_signatures_are_allowed_with_ten_residual_dimensions(self):
        for m in range(12):
            s, t = M.nishino(m)
            self.assertTrue(M.theory_allowed(s, t))
            self.assertIn(m, M.admissible_frames(s, t))
            self.assertEqual(s + t - 2 * m, 10)

    def test_the_claimed_families_are_excluded(self):
        for f in M.FAMILIES:
            self.assertTrue(M.theory_allowed(*M.family(f, 0)), f)
            for n in range(1, 7):
                s, t = M.family(f, n)
                self.assertTrue(M.majorana_weyl(s, t))
                self.assertEqual(min(M.residual_dimensions(s, t)), 8 + 8 * n)
                self.assertFalse(M.theory_allowed(s, t), (f, n))
        self.assertFalse(M.theory_allowed(27, 3))
        self.assertFalse(M.theory_allowed(19, 3))

    def test_main_theorem_is_s_minus_t_in_8_0_minus_8(self):
        for s in range(0, 40):
            for t in range(0, 40):
                allowed = M.theory_allowed(s, t)
                if allowed:
                    self.assertIn(s - t, (8, 0, -8), (s, t))
                # on the three lines every signature with a time and a space direction is reached
                expect = (abs(s - t) == 8 and min(s, t) >= 1) or (s == t >= 1)
                self.assertEqual(allowed, expect, (s, t))

    def test_vector_structures_live_in_three_four_six_ten(self):
        self.assertEqual(M.vector_structure_dimensions(400), [3, 4, 6, 10])
        self.assertEqual([M.weyl_dimension(d) for d in (3, 4, 6, 10)], [2, 2, 4, 16])

    def test_sym2_decomposition(self):
        self.assertEqual(M.sym2_forms(5), [5, 1])
        for r in range(2, 21):
            self.assertTrue(M.sym2_count_ok(r), r)

    def test_single_time_bound(self):
        self.assertEqual(M.single_time_bound(0), {"supercharges": 16, "log2_states": 4,
                                                  "vector_bosons": 8, "gaugino_states": 8})
        self.assertEqual(M.single_time_bound(1)["log2_states"], 64)
        self.assertEqual(M.single_time_bound(2)["log2_states"], 1024)

    def test_refuters_admit_what_the_checks_reject(self):
        ref = M.refuter()
        claimed = sorted(M.family(f, n) for f in M.FAMILIES for n in (1, 2))
        self.assertEqual(sorted(ref["mod8_rule"]), claimed)
        self.assertEqual(sorted(ref["complex_frames"]), claimed)
        # complex frames reach D' = 10 in (17,1) with k = 4 > min(s, t) = 1
        self.assertIn(4, M.complex_frames(17, 1))
        self.assertEqual(M.admissible_frames(17, 1), [])
        # a corrupted certificate is caught
        cert = M.certificate()
        cert["division_dimensions"] = [3, 4, 6, 10, 18]
        self.assertTrue(M.check(cert))

    @unittest.skipUnless(HAVE_NUMPY, "numpy is not installed")
    def test_fierz_identity_holds_only_in_ten_dimensions(self):
        for st in ((9, 1), (5, 5), (1, 9)):
            self.assertLess(M.fierz_residual(*st), 1e-12, st)
        for st in ((17, 1), (13, 5), (9, 9)):
            self.assertGreater(M.fierz_residual(*st), 0.1, st)

    def test_summary(self):
        s = M.summary()
        self.assertEqual(s["failures"], [])
        self.assertEqual(s["division_dimensions"], [3, 4, 6, 10])
        self.assertEqual(s["excluded_named"], {"27+3": False, "19+3": False})


if __name__ == "__main__":
    unittest.main()
