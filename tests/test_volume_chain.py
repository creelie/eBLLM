import random
import unittest

from ebllm.construct import reflexive as R
from ebllm.construct import volume_chain as V


SIMPLEX = [(1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1), (-1, -1, -1, -1)]
CROSS = [tuple(s if i == j else 0 for i in range(4)) for j in range(4) for s in (1, -1)]


class TestVolumeChain(unittest.TestCase):
    def test_volumes_of_two_reflexive_4_polytopes(self):
        self.assertEqual(V.normalised_volume4(SIMPLEX), 5)
        self.assertEqual(V.normalised_volume4(CROSS), 16)

    def test_volume_falls_and_dual_volume_rises_from_the_cube_to_the_cross_polytope(self):
        cube = [tuple(x) for x in __import__("itertools").product((-1, 1), repeat=4)]
        self.assertEqual(sorted(R.dual(CROSS)), sorted(cube))
        self.assertEqual(V.normalised_volume4(cube), 384)
        self.assertLess(V.normalised_volume4(CROSS), V.normalised_volume4(cube))
        self.assertGreater(V.normalised_volume4(R.dual(CROSS)), V.normalised_volume4(R.dual(cube)))

    def test_three_key_chain_matches_the_brute_force(self):
        rng = random.Random(1)
        for _ in range(60):
            rows = [(rng.randint(0, 12), rng.randint(0, 12), rng.randint(0, 12)) for _ in range(rng.randint(1, 40))]
            self.assertEqual(V.chain_bound3(rows), V.chain_bound_brute(rows, (-1, 1, -1)))

    def test_more_keys_never_lengthen_the_chain(self):
        rng = random.Random(2)
        for _ in range(40):
            rows = [(rng.randint(0, 9), rng.randint(0, 9), rng.randint(0, 30)) for _ in range(30)]
            self.assertLessEqual(V.chain_bound3(rows), R.pair_chain_bound([r[:2] for r in rows]))


if __name__ == "__main__":
    unittest.main()
