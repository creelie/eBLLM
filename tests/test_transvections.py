import copy
import unittest
from collections import Counter

from ebllm.construct import transvections as T

# KnotInfo PD codes of knots with bridge index 3: none of them may get a certificate of rank 4
THREE_BRIDGE = {
    "8_5": [[1, 7, 2, 6], [3, 9, 4, 8], [5, 12, 6, 13], [7, 3, 8, 2], [9, 15, 10, 14], [11, 1, 12, 16],
            [13, 4, 14, 5], [15, 11, 16, 10]],
    "9_35": [[2, 12, 3, 11], [4, 16, 5, 15], [6, 14, 7, 13], [8, 18, 9, 17], [10, 4, 11, 3], [12, 2, 13, 1],
             [14, 6, 15, 5], [16, 10, 17, 9], [18, 8, 1, 7]],
    "10_120": [[2, 10, 3, 9], [4, 18, 5, 17], [6, 12, 7, 11], [8, 4, 9, 3], [10, 16, 11, 15], [12, 20, 13, 19],
               [14, 8, 15, 7], [16, 2, 17, 1], [18, 14, 19, 13], [20, 6, 1, 5]],
}


class TestTransvections(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.certs = T.certificates()
        cls.by = {c["name"]: c for c in cls.certs}

    def test_the_243_certificates_verify(self):
        self.assertEqual(len(self.certs), 243)
        self.assertEqual([c["name"] for c in self.certs if T.check_certificate(c)], [])
        self.assertEqual(Counter(c["group"] for c in self.certs),
                         {"Sp(4,3) transvections": 67, "Sp(4,5) transvections": 161, "O(4,5) reflections": 15})
        self.assertTrue(all(c["name"].startswith("13") for c in self.certs))

    def test_the_open_list_completes_the_536(self):
        rest = T.still_open()
        self.assertEqual(len(rest), 293)
        self.assertFalse(set(rest) & set(self.by))
        self.assertEqual(len(set(rest) | set(self.by)), 536)

    def test_corrupted_certificates_fail(self):
        c = self.by["13a_69"]
        changed = copy.deepcopy(c)
        changed["matrices"][0][0][1] = (changed["matrices"][0][0][1] + 1) % 3
        self.assertIsNotNone(T.check_certificate(changed))
        three = dict(c, wirtinger_seeds=c["wirtinger_seeds"][:3])
        self.assertIsNotNone(T.check_certificate(three))
        flipped = copy.deepcopy(c)
        a, b, cc, d = flipped["pd"][0]
        flipped["pd"][0] = [a, d, cc, b]
        self.assertIsNone(T.check_pd(flipped["pd"]))
        self.assertIsNotNone(T.check_certificate(flipped))
        identity = dict(c, matrices=[[[int(i == j) for j in range(4)] for i in range(4)]] * len(c["matrices"]))
        self.assertIsNotNone(T.check_certificate(identity))
        self.assertIsNotNone(T.check_certificate(dict(c, field=9)))

    def test_the_search_rediscovers_and_its_output_verifies(self):
        for name in ("13a_69", next(n for n, c in self.by.items() if c["field"] == 5 and c["group"].startswith("Sp"))):
            c = self.by[name]
            found = T.search_sp4(c["pd"], c["field"])
            self.assertIsNotNone(found, name)
            self.assertIsNone(T.check_certificate(found), name)

    def test_three_bridge_knots_get_no_certificate(self):
        for name, pd in THREE_BRIDGE.items():
            self.assertIsNone(T.check_pd(pd))
            self.assertIsNotNone(T.wirtinger_seeds(pd, 3), name)   # the diagram itself has Wirtinger number 3
            self.assertIsNone(T.wirtinger_seeds(pd, 2), name)
            for p in (3, 5):
                self.assertIsNone(T.search_sp4(pd, p), (name, p))

    def test_the_lemma(self):
        form = lambda x, y: (x[0] * y[1] - x[1] * y[0]) % 5
        t1, t2 = T.transvection([1, 0], form, 5), T.transvection([0, 1], form, 5)
        self.assertEqual(T.meridional_rank_lower_bound([t1, t2], 5), 2)
        self.assertEqual(T.meridional_rank_lower_bound([t1, t1], 5), 1)
        with self.assertRaises(ValueError):
            T.meridional_rank_lower_bound([[[1, 0], [0, 1]]], 5)
        r = T.reflection([1, 1, 0, 0], [[int(i == j) for j in range(4)] for i in range(4)], 5)
        self.assertEqual(T.mat_mul(r, r, 5), [[int(i == j) for j in range(4)] for i in range(4)])
        self.assertEqual(T.meridional_rank_lower_bound([r], 5), 1)


if __name__ == "__main__":
    unittest.main()
