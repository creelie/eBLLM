import unittest
from math import gcd

from ebllm.construct import reformulate as F


def _divisors(n):
    return [d for d in range(1, n + 1) if n % d == 0]


def _phi(n):
    return sum(1 for k in range(1, n + 1) if gcd(k, n) == 1)


class DefinitionRepair(unittest.TestCase):
    U = list(range(1, 200))
    # "divisible only by 1 and itself" admits 1; the repair is "exactly two divisors"
    OLD = F.Definition("prime_old", lambda n: all(d in (1, n) for d in _divisors(n)))
    NEW = F.Definition("prime_new", lambda n: len(_divisors(n)) == 2)
    LIB = {
        "n > 1": lambda n: n > 1,
        "phi(n) = n - 1": lambda n: _phi(n) == n - 1,
        "n | ab implies n | a or n | b (a, b < 30)":
            lambda n: all(a * b % n or a % n == 0 or b % n == 0 for a in range(1, 30) for b in range(1, 30)),
        "odd or 2": lambda n: n % 2 == 1 or n == 2,
    }

    def test_a_repair_with_a_reason_gains_consequences(self):
        v = F.repair(self.OLD, self.NEW, self.U, self.LIB, {1: "1 is a unit: unique factorisation fails"})
        self.assertTrue(v.accepted)
        self.assertEqual(v.disagreements, [1])
        for q in ("phi(n) = n - 1", "n > 1"):
            self.assertIn(q, v.carried_new)
            self.assertNotIn(q, v.carried_old)

    def test_a_change_without_a_reason_is_refused(self):
        v = F.repair(self.OLD, self.NEW, self.U, self.LIB, {})
        self.assertFalse(v.accepted)
        self.assertEqual(v.unexplained, [1])

    def test_a_change_that_loses_consequences_is_refused(self):
        odd = F.Definition("odd", lambda n: n % 2 == 1)
        v = F.repair(self.NEW, odd, self.U, self.LIB, {x: "?" for x in self.U})
        self.assertFalse(v.accepted)
        self.assertTrue(v.reason.startswith("the new definition loses consequences"))

    def test_the_same_extension_with_fewer_clauses_is_accepted(self):
        long = F.Definition("prime_long", lambda n: n > 1 and len(_divisors(n)) == 2, 2)
        self.assertTrue(F.repair(long, self.NEW, self.U, self.LIB, {}).accepted)
        self.assertFalse(F.repair(self.NEW, long, self.U, self.LIB, {}).accepted)


class WitnessGate(unittest.TestCase):
    COND = F.Conditional("estimate", {"real": lambda x: isinstance(x, (int, float)),
                                      "bounded": lambda x: abs(x) <= 1},
                         {"nonzero": lambda x: x != 0})

    def test_no_witness(self):
        self.assertEqual(F.witness_gate(self.COND, None), (False, ["no witness exhibited"]))

    def test_a_degenerate_witness_is_not_enough(self):
        # the zero datum meets the hypotheses, so the implication would be empty without the check
        self.assertEqual(F.witness_gate(self.COND, 0), (False, ["nondegenerate:nonzero"]))

    def test_a_witness_meeting_everything_admits_the_result(self):
        self.assertEqual(F.witness_gate(self.COND, 0.5), (True, []))
        self.assertEqual(F.witness_gate(self.COND, 2), (False, ["bounded"]))


class Practice(unittest.TestCase):
    def test_rows_name_their_rules_and_sources(self):
        ids = [r["id"] for r in F.PRACTICE]
        self.assertEqual(len(ids), len(set(ids)))
        for r in F.PRACTICE:
            self.assertTrue(r["source"] and r["lemma"] and r["verdict"], r["id"])
            for rule in r["rule"].split():
                self.assertIn(rule, F.RULES, r["id"])
        # the interview is an anecdote, never a result
        self.assertEqual({r["verdict"] for r in F.PRACTICE if r["id"].startswith("k.meta.")}, {"anecdote", "criterion"})
        used = {x for r in F.PRACTICE for x in r["rule"].split()}
        self.assertEqual(used, set(F.RULES))


if __name__ == "__main__":
    unittest.main()
