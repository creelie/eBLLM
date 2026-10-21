import copy
import unittest
from collections import Counter

from ebllm.construct import pinch as P

TREFOIL = [[1, 5, 2, 4], [3, 1, 4, 6], [5, 3, 6, 2]]
FIGURE_EIGHT = [[4, 2, 5, 1], [8, 6, 1, 5], [6, 3, 7, 4], [2, 7, 3, 8]]
K8_18 = [[6, 2, 7, 1], [8, 3, 9, 4], [16, 11, 1, 12], [2, 14, 3, 13], [4, 15, 5, 16], [10, 6, 11, 5],
         [12, 7, 13, 8], [14, 10, 15, 9]]


class TestPinch(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certs = P.certificates()

    def test_the_139_certificates_pass(self):
        self.assertEqual(len(self.certs), 139)
        self.assertEqual([c["knot"] for c in self.certs if P.check_certificate(c)], [])
        self.assertEqual(Counter(c["bound"] for c in self.certs), {1: 76, 2: 63})
        self.assertEqual(len({c["knot"] for c in self.certs}), 139)

    def test_the_refuter_breaks_every_certificate(self):
        self.assertTrue(all(P.refute(c) for c in self.certs))

    def test_corrupted_certificates_fail(self):
        c = copy.deepcopy(self.certs[0])
        c["bound"] -= 1
        self.assertIsNotNone(P.check_certificate(c))
        c = copy.deepcopy(next(x for x in self.certs if x["bound"] == 2))
        c["target_slice"] = True
        self.assertIsNotNone(P.check_certificate(c))
        c = copy.deepcopy(self.certs[0])
        c["diagram"] = c["diagram"][1:]
        self.assertIsNotNone(P.check_certificate(c))

    def test_exactly_one_smoothing_is_a_pinch(self):
        for pd in (TREFOIL, FIGURE_EIGHT, K8_18):
            for i in range(len(pd)):
                self.assertEqual(P.is_pinch(pd, i, 0) + P.is_pinch(pd, i, 1), 1)

    def test_alexander_colourings(self):
        self.assertEqual(P.alexander_colourings(TREFOIL, 3, 2), 2)       # Fox 3-colourings
        self.assertEqual(P.alexander_colourings(TREFOIL, 5, 2), 1)       # only the constants
        self.assertEqual(P.alexander_colourings(FIGURE_EIGHT, 5, 4), 2)  # Fox 5-colourings
        self.assertEqual(P.alexander_colourings(K8_18, 3, 2), 3)         # mu(8_18) = 3


if __name__ == "__main__":
    unittest.main()
