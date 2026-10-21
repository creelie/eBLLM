import unittest

from ebllm.construct import genus_four_prym as G


class TestGenusFourPrym(unittest.TestCase):
    def test_the_multiplication_map_is_an_isomorphism(self):
        for lam, p in ((2, 101), (5, 103), (7, 109)):
            r = G.check(lam, p)
            self.assertTrue(r["isomorphism"], r)
            self.assertGreaterEqual(r["points"], 9)

    def test_the_refuter_fails(self):
        r = G.refute()
        self.assertEqual(r["rank"], 5)
        self.assertFalse(r["isomorphism"])


if __name__ == "__main__":
    unittest.main()
