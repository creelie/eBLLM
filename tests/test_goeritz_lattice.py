import unittest
from collections import Counter

from ebllm.construct import goeritz_lattice as G
from ebllm.construct import pinch as P

TREFOIL = [[1, 5, 2, 4], [3, 1, 4, 6], [5, 3, 6, 2]]
K8_18 = [[6, 2, 7, 1], [8, 3, 9, 4], [16, 11, 1, 12], [2, 14, 3, 13], [4, 15, 5, 16], [10, 6, 11, 5],
         [12, 7, 13, 8], [14, 10, 15, 9]]


class TestGoeritzLattice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.lower = G.lower_bounds()
        cls.certs = G.certificates()

    def test_small_knots(self):
        self.assertIsNone(G.lower_bound(TREFOIL, 1, 3)["bound"])          # gamma_4(3_1) = 1
        self.assertEqual(G.lower_bound(K8_18, 1, 45)["bound"], 3)          # Jabuka-Kelly: gamma_4(8_18) = 3
        sigma, Pp, Pm = G.forms(TREFOIL)
        self.assertEqual(abs(sigma), 2)
        self.assertEqual(len(Pp) + len(Pm), 3)

    def test_the_refuter_contradicts_the_trefoil(self):
        self.assertEqual(G.lower_bound(TREFOIL, 1, 3, sign=-1)["bound"], 2)

    def test_complement_norm(self):
        self.assertEqual(G.complement_norm([[1, 1, 0], [-1, 0, 1]]), 3)   # A_2 in Z^3
        self.assertEqual(sorted({G.complement_norm(v) for v in G.embeddings([[2, -1], [-1, 2]], 3)}), [3])

    def test_the_382_lower_bounds(self):
        self.assertEqual(len(self.lower), 382)
        self.assertEqual(Counter(d["bound"] for d in self.lower), {2: 360, 3: 22})
        small = [d for d in self.lower if len(d["pd"]) <= 12]
        self.assertEqual([d["knot"] for d in small if G.check_lower_bound(d)], [])

    def test_the_84_pinch_certificates(self):
        self.assertEqual(len(self.certs), 84)
        self.assertEqual(Counter(c["bound"] for c in self.certs), {1: 55, 2: 29})
        lb = {d["knot"]: d["bound"] for d in self.lower}
        for c in self.certs:
            lo, hi = c["knotinfo_range"]
            lo = max(lo, lb.get(c["knot"], lo))
            self.assertTrue(P.is_pinch(c["diagram"], c["crossing"], c["smoothing"]))
            self.assertEqual(P.bound(c["target_slice"], c["target_gamma4"]), c["bound"])
            self.assertTrue(lo <= c["bound"] < hi)


if __name__ == "__main__":
    unittest.main()
