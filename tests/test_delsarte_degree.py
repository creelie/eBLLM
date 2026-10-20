import unittest

from ebllm.construct import delsarte_degree as D


class TestDelsarteDegree(unittest.TestCase):
    def test_the_29_sextic_shapes_of_h8(self):
        rows = D.census([6])
        self.assertEqual(len(rows), 29)
        es = sorted(r["e"] for r in rows)
        self.assertEqual(es[0], 6)                       # the Fermat sextic itself
        self.assertEqual(es.count(24) + es.count(30), 6)
        self.assertEqual(max(es), 3750)
        self.assertIn(2604, es)                          # the loop sextic
        self.assertEqual([e for e in es if e % 2], [3125])  # the one odd e is out of every census
        self.assertTrue(all(r["closed_by"] == "open" for r in rows if not r["fermat"]))

    def test_klein_quartic_shape(self):
        # the Klein-type chain x^3 y + y^3 z + z^3 x has lattice degree 7
        A = [[3, 1, 0], [0, 3, 1], [1, 0, 3]]
        self.assertEqual(D.lattice_degree(A), (7, 7))

    def test_closed_by(self):
        self.assertEqual(D.closed_by(7), "published")       # Shioda, prime
        self.assertEqual(D.closed_by(25), "published")      # da Silva, coprime to 6
        self.assertEqual(D.closed_by(21), "published")
        self.assertEqual(D.closed_by(33), "jumagulov")
        self.assertEqual(D.closed_by(24), "open")
        self.assertEqual(D.closed_by(201), "open")

    def test_census_counts(self):
        rows = D.census(range(3, 41))
        s = D.summary(rows)
        self.assertEqual(s["shapes"], 1102)
        self.assertEqual(s["non_fermat_closed"], 51)
        nf = [r for r in rows if not r["fermat"] and r["closed_by"] != "open"]
        self.assertEqual(sum(1 for r in nf if r["closed_by"] == "published"), 37)
        self.assertEqual(sum(1 for r in nf if r["closed_by"] == "jumagulov"), 14)


if __name__ == "__main__":
    unittest.main()
