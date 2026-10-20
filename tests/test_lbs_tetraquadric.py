import itertools
import unittest

try:
    import numpy as np
except ImportError:  # the scouts need numpy; the rest of the engine does not
    np = None

if np is not None:
    from ebllm.construct import lbs_tetraquadric as T


@unittest.skipUnless(np is not None, "numpy is not installed")
class TestTetraquadric(unittest.TestCase):
    def test_cohomology_matches_index_and_serre(self):
        for k in itertools.product(range(-2, 3), repeat=4):
            hh = T.h(k)
            self.assertEqual(hh[0] - hh[1] + hh[2] - hh[3], T.ind(k), k)
            self.assertEqual(hh, tuple(reversed(T.h(tuple(-x for x in k)))), k)
        self.assertEqual(T.h((0, 0, 0, 0)), (1, 0, 0, 1))

    def test_every_class_is_a_candidate(self):
        self.assertEqual(len(T.CLASSES), 10)
        for g, K, t in T.CLASSES:
            self.assertEqual(T.refute(K, g, t), [], K)

    def test_refuter(self):
        g, K, t = T.CLASSES[0]
        self.assertTrue(T.refute(K, 2 * g, t))                               # wrong group order
        bad = [list(k) for k in K]; bad[0][0] += 1
        self.assertIn("c1(V) != 0", T.refute(bad, g, t))
        self.assertTrue(T.refute([(3, -3, 3, -3), (-3, 3, -3, 3), (1, -1, 0, 0), (-1, 1, 0, 0), (0, 0, 0, 0)], 2))


if __name__ == "__main__":
    unittest.main()
