import unittest

from ebllm.construct import lehmer_equiv as L

SMALL_PRIMES = [p for p in range(3, 60) if L.is_prime(p)]


class TestLehmerEquiv(unittest.TestCase):
    def test_companion_equation_gives_the_fermat_chain(self):
        chain = L.companion_chain(4)
        self.assertEqual(chain, [15, 255, 65535, 4294967295])
        for n in chain:
            primes = [p for p in L.FERMAT_PRIMES if n % p == 0]
            self.assertEqual((n + 1) % L.totient_squarefree(primes), 0)
        r = L.check((3, 5), 2, sign=1)
        self.assertEqual(L.divisor_data((3, 5), 2, sign=1)["D"], 1)   # D = 1 is allowed here
        self.assertTrue(r["identity"])

    def test_the_two_constraints_hold_on_every_candidate(self):
        self.assertTrue(L.constraints_hold(SMALL_PRIMES[:8], 4, range(2, 8)))
        r = L.check((5, 7, 11, 13), 2)
        self.assertEqual(L.divisor_data((5, 7, 11, 13), 2)["D"], 755)
        self.assertTrue(r["d_odd"] and r["d_residue"])
        self.assertFalse(r["solution"])

    def test_refuter_finds_no_lehmer_number_in_the_search_space(self):
        # omega(n) >= 16 is proved, so a hit here would be a bug in the equations
        self.assertEqual(L.search(SMALL_PRIMES, 4, range(2, 8), sign=-1), [])
        hits = L.search(list(L.FERMAT_PRIMES[:3]), 3, range(2, 4), sign=1)
        self.assertEqual(sorted(n for _, _, n in hits), [15, 255, 65535])

    def test_d_equal_one_is_impossible_for_lehmer(self):
        # D = 1 would give q = A, which is composite for |S| >= 2 and equal to the element of S for |S| = 1
        for S in ((3,), (3, 5), (7, 11, 13)):
            for M in range(2, 40):
                d = L.divisor_data(S, M)
                if d["D"] == 1:
                    self.assertFalse(L.check(S, M)["q_prime_above_S"])

    def test_inputs_are_validated(self):
        with self.assertRaises(ValueError):
            L.divisor_data((2, 3), 2)
        with self.assertRaises(ValueError):
            L.divisor_data((3, 5), 1)
        with self.assertRaises(ValueError):
            L.divisor_data((3, 5), 2, sign=0)


if __name__ == "__main__":
    unittest.main()
