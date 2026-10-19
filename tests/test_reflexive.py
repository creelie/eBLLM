import unittest
from collections import Counter

from ebllm.construct import reflexive as R


class TestReflexive(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.polygons = R.reflexive_polygons()

    def test_facets_and_duality(self):
        square = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        self.assertTrue(R.is_reflexive(square))
        self.assertEqual(R.dual(square), [(-1, 0), (0, -1), (0, 1), (1, 0)])
        self.assertEqual(sorted(R.dual(R.dual(square))), sorted(square))
        self.assertFalse(R.is_reflexive([(-2, -2), (2, -2), (2, 2), (-2, 2)]))  # facets at height 2
        self.assertFalse(R.is_reflexive([(0, 0), (1, 0), (0, 1)]))  # origin on the boundary

    def test_cube_in_three_dimensions(self):
        cube = [p for p in __import__("itertools").product((-1, 1), repeat=3)]
        self.assertTrue(R.is_reflexive(cube))
        self.assertEqual(len(R.lattice_points(cube)), 27)
        self.assertEqual(len(R.lattice_points(R.dual(cube))), 7)  # the octahedron

    def test_sixteen_polygons_with_the_classical_point_counts(self):
        self.assertEqual(len(self.polygons), 16)
        # boundary points 3, ..., 9 occur 1, 3, 2, 4, 2, 3, 1 times
        self.assertEqual(sorted(Counter(len(p) - 1 for p in self.polygons).items()),
                         [(3, 1), (4, 3), (5, 2), (6, 4), (7, 2), (8, 3), (9, 1)])
        for p in self.polygons:  # b(P) + b(P*) = 12
            self.assertEqual(len(p) + len(R.lattice_points(R.dual(p))), 14)

    def test_search_is_closed(self):
        minimal = [p for p in self.polygons if R.is_minimal(p)]
        self.assertEqual(sorted(len(p) for p in minimal), [4, 5, 5])
        tops = sorted(R._canonical2(R.lattice_points(R.dual(p))) for p in minimal)
        start = sorted(R._canonical2(R.lattice_points(t)) for t in
                       ([(-1, -1), (2, -1), (-1, 2)], [(-1, -1), (1, -1), (1, 1), (-1, 1)],
                        [(-1, -1), (3, -1), (-1, 1)]))
        self.assertEqual(tops, start)

    def test_descents_in_the_plane(self):
        # the fewest steps to a minimal polygon is at most 5, and 5 occurs once, at the
        # 10-point triangle; the longest descent has 6 steps, the pair-chain bound
        shortest = [R.shortest_descent(p) for p in self.polygons]
        longest = [R.longest_descent(p) for p in self.polygons]
        self.assertEqual(max(shortest), 5)
        self.assertEqual(shortest.count(5), 1)
        self.assertEqual(max(longest), 6)
        pairs = [(len(p), len(R.lattice_points(R.dual(p)))) for p in self.polygons]
        self.assertEqual(R.pair_chain_bound(pairs), 6)

    def test_every_step_loses_a_point_and_its_dual_gains_one(self):
        for p in self.polygons:
            n, m = len(p), len(R.lattice_points(R.dual(p)))
            for q in R.descent_steps(p):
                self.assertLess(len(q), n)
                self.assertGreater(len(R.lattice_points(R.dual(q))), m)

    def test_pair_chain_bound(self):
        self.assertEqual(R.pair_chain_bound([]), 0)
        self.assertEqual(R.pair_chain_bound([(5, 1)]), 0)
        # equal first entries never chain, and the second entry must rise strictly
        self.assertEqual(R.pair_chain_bound([(9, 1), (9, 2), (8, 2), (7, 3), (6, 3)]), 2)
        self.assertEqual(R.pair_chain_bound([(10, 1), (9, 5), (8, 2), (7, 3), (6, 4)]), 3)


if __name__ == "__main__":
    unittest.main()
