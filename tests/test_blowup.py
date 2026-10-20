import random
import unittest

from ebllm.construct import blowup as B


class TestBlowUp(unittest.TestCase):
    def test_blowup_formula_on_known_cases(self):
        # P^2 at a point: h^{1,1} goes from 1 to 2
        self.assertEqual(B.blowup_hodge({(0, 0): 1, (1, 1): 1, (2, 2): 1}, {(0, 0): 1}, 2), {(0, 0): 1, (1, 1): 2, (2, 2): 1})
        # a point on a threefold: one new (1,1) and one new (2,2)
        self.assertEqual(B.blowup_hodge({(0, 0): 1, (1, 1): 1, (2, 2): 1, (3, 3): 1}, {(0, 0): 1}, 3),
                         {(0, 0): 1, (1, 1): 2, (2, 2): 2, (3, 3): 1})
        # a curve of genus g in a threefold: h^{2,1} and h^{1,2} grow by g
        out = B.blowup_hodge({(0, 0): 1, (1, 1): 1, (2, 2): 1, (3, 3): 1}, {(0, 0): 1, (1, 0): 3, (0, 1): 3, (1, 1): 1}, 2)
        self.assertEqual((out[(2, 1)], out[(1, 2)], out[(1, 1)], out[(2, 2)]), (3, 3, 2, 2))
        with self.assertRaises(ValueError):
            B.blowup_hodge({}, {}, 1)

    def test_a_blowup_never_lowers_a_defect(self):
        rng = random.Random(3)
        for _ in range(200):
            defX = {k: rng.randrange(4) for k in range(1, 5)}
            defZ = {k: rng.randrange(3) for k in range(0, 3)}
            c = rng.randrange(2, 5)
            out = B.defect_transfer(defX, defZ, c)
            for k, v in defX.items():
                self.assertGreaterEqual(out.get(k, 0), v)
            self.assertEqual(sum(out.values()), sum(defX.values()) + (c - 1) * sum(defZ.values()))

    def test_harmless_centres(self):
        self.assertTrue(B.centre_is_harmless(0))
        self.assertTrue(B.centre_is_harmless(2))
        self.assertTrue(B.centre_is_harmless(3, abelian=True))
        self.assertFalse(B.centre_is_harmless(3))
        self.assertFalse(B.centre_is_harmless(4, abelian=True))

    def test_hilbert_symbol_product_formula(self):
        rng = random.Random(5)
        for _ in range(300):
            a = rng.choice([-1, 1]) * rng.randrange(1, 400)
            b = rng.choice([-1, 1]) * rng.randrange(1, 400)
            prod = 1
            for v in B.places(1, [a, b]) + [p for p in B._primes_dividing(a * b)]:
                pass
            plc = sorted(set(B._primes_dividing(2 * a * b))) + ["inf"]
            for v in plc:
                prod *= B.hilbert_symbol(a, b, v)
            self.assertEqual(prod, 1, (a, b))
            self.assertEqual(B.hilbert_symbol(a, b, 3), B.hilbert_symbol(b, a, 3))

    def test_norms_from_imaginary_quadratic_fields(self):
        # Q(i): sums of two squares
        self.assertEqual([x for x in range(1, 30) if B.is_norm(x, 1)], [1, 2, 4, 5, 8, 9, 10, 13, 16, 17, 18, 20, 25, 26, 29])
        # Q(sqrt-3): a^2 - ab + b^2
        self.assertEqual([x for x in range(1, 30) if B.is_norm(x, 3)], [1, 3, 4, 7, 9, 12, 13, 16, 19, 21, 25, 27, 28])
        # Q(sqrt-7): a^2 + ab + 2b^2
        self.assertEqual([x for x in range(1, 30) if B.is_norm(x, 7)], [1, 2, 4, 7, 8, 9, 11, 14, 16, 18, 22, 23, 25, 28, 29])

    def test_closure_of_the_trivial_discriminant_is_trivial(self):
        cands = [2, 3, 5, 6, 7, 10, 11, 13, 15, 21]
        for d in (1, 2, 3, 7, 11):
            r = B.blowup_discriminants(d, [1], cands)
            self.assertEqual(r["span_size"], 1)
            self.assertEqual(r["follow"], [x for x in cands if B.is_norm(x, d)])

    def test_one_more_certificate_buys_its_subgroup(self):
        cands = [2, 3, 5, 6, 7, 10, 11, 13, 15, 21]
        r = B.one_more(1, [1], 3, cands)
        self.assertEqual(r["gained"], [3, 6, 15])          # 3, 3*2, 3*5: the coset of 3 by the norms
        self.assertEqual(r["still_open"], [7, 11, 21])
        # 11 is a third independent class: Q^*/N(K^*) has one coordinate per prime
        self.assertEqual(B.one_more(1, [1, 3], 7, cands)["still_open"], [11])
        self.assertEqual(B.one_more(1, [1, 3, 7], 11, cands)["still_open"], [])


if __name__ == "__main__":
    unittest.main()
