import random
import unittest

from ebllm.construct import gsc_mirror_fixed as G


class TestGscMirrorFixed(unittest.TestCase):
    def test_mirror_swaps_hodge_numbers_and_is_an_involution(self):
        v = G.standard_embedding(1, 101)
        m = v.mirror()
        self.assertEqual((m.h11, m.h21, m.c3), (101, 1, 200))
        self.assertEqual(m.mirror(), v)

    def test_index_formula(self):
        # the quintic: chi = -200, 100 net families; its Z5 quotient: 20; Z5 x Z5: 4
        self.assertEqual(G.net_families(G.standard_embedding(1, 101)), 100)
        self.assertEqual(G.net_families(G.standard_embedding(1, 101, 5)), 20)
        self.assertEqual(G.net_families(G.standard_embedding(1, 101, 25)), 4)
        # the Tian-Yau quotient: three families
        self.assertEqual(G.net_families(G.standard_embedding(6, 9)), 3)
        with self.assertRaises(ValueError):
            G.index(G.Vacuum(1, 1, 3))
        with self.assertRaises(ValueError):
            G.index(G.standard_embedding(1, 101, 3))

    def test_lemma_every_mirror_fixed_vacuum_has_zero_families(self):
        self.assertEqual(G.c2_fails_at_fixed_points(G.sample_vacua()), [])
        rng = random.Random(11)
        for _ in range(500):
            h = rng.randrange(1, 500)
            q = rng.choice([1, 2, 3, 4, 5, 7])
            self.assertEqual(G.net_families(G.standard_embedding(h, h, q)), 0)

    def test_corollary_three_families_are_never_mirror_fixed(self):
        vs = G.sample_vacua()
        self.assertTrue(G.gsc_clause_is_empty(vs))
        self.assertGreater(sum(1 for v in vs if v.standard_type and G.net_families(v) == 3), 0)

    def test_refuter_off_standard_vacua_are_outside_the_lemma(self):
        # a self-mirror threefold with a three-family bundle off the standard embedding lies outside
        # L^mu: the lemma does not call it fixed, and it keeps its three families
        v = G.Vacuum(19, 19, -6, 1, False)
        self.assertFalse(v.is_mirror_fixed())
        self.assertEqual(G.net_families(v), 3)
        # and a would-be fixed point with nonzero c_3 on a standard component is caught
        bad = G.Vacuum(19, 19, -6, 1, True)
        self.assertEqual(G.c2_fails_at_fixed_points([bad]), [(bad, 3)])

    def test_summary(self):
        s = G.summary()
        self.assertEqual(s["offenders"], [])
        self.assertTrue(s["clause_empty"])
        self.assertEqual(s["families_at_fixed_points"], [0])
        self.assertIn("proved", s["label"])


if __name__ == "__main__":
    unittest.main()
