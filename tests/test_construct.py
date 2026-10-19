import contextlib
import io
import os
import unittest

try:
    import networkx as nx
    import pysat  # noqa: F401
except ImportError:  # construction mode needs networkx and python-sat; CI installs both
    if os.environ.get("CI"):
        raise
    raise unittest.SkipTest("networkx and python-sat are not installed")

from ebllm import cli
from ebllm import construct as C
from ebllm.construct import assemble, graphcheck as gc, proof_builder as pb, steinberg_rebuild as S


def roles(G, a, bc):
    nx.set_node_attributes(G, {v: ("a" if v == a else "bc" if v in bc else "") for v in G}, "r")
    return G


class Steinberg(unittest.TestCase):
    def test_gadget_G1(self):
        r = gc.report(S.G1(), ["a", "b", "c"], "NAE")
        self.assertTrue(r["planar_face"])
        self.assertEqual(r["cycles_<=8"], [3, 6, 7, 8])
        self.assertEqual(sorted(r["dist"].values()), [3, 3, 4])
        self.assertTrue(r["forces_NAE"])

    def test_counterexample_is_planar_without_4_5_cycles_and_not_3_colourable(self):
        G = S.G_final()
        self.assertEqual((G.number_of_nodes(), G.number_of_edges()), (166, 300))
        self.assertTrue(nx.check_planarity(G)[0])
        self.assertEqual(sorted(gc.cycle_lengths_present(G, 6)), [3, 6])
        for name in S.SOLVERS:
            self.assertFalse(S.sat_colourable(G, name), name)

    def test_backtracking_and_sat_agree(self):
        for name in C.GADGETS:
            G, contacts = C.gadget(name)
            self.assertEqual(gc.forces(G, contacts, "NAE"), not pb.contacts_can_share(G, contacts), name)


class StoredResults(unittest.TestCase):
    def test_the_rediscovered_gadget_is_steinbergs(self):
        H, contacts = C.gadget("rediscovered_n15")
        self.assertTrue(nx.is_isomorphic(roles(S.G1(), "a", "bc"), roles(H, 0, (1, 2)),
                                         node_match=lambda x, y: x["r"] == y["r"]))

    def test_the_lemma_run_rediscovers_G2(self):
        H, contacts = C.gadget("G2_rediscovered_n42")
        G = S.G2("", "A", "B", "C")
        self.assertTrue(nx.is_isomorphic(roles(G, None, ("A", "B", "C")), roles(H, None, (0, 1, 2)),
                                         node_match=lambda x, y: x["r"] == y["r"]))

    def test_level_two_gadget(self):
        H, contacts = C.gadget("level2_n48")
        r = gc.report(H, contacts, "NAE", cyc_hi=5)
        self.assertEqual((r["n"], r["m"]), (48, 82))
        self.assertEqual(r["cycles_<=5"], [3])
        self.assertEqual(sorted(r["dist"].values()), [4, 5, 5])
        self.assertTrue(r["planar_face"] and r["forces_NAE"])

    def test_assembly_of_the_rediscovered_gadget_is_a_counterexample(self):
        H, _ = C.gadget("rediscovered_n15")
        G = assemble.final(H)
        self.assertTrue(nx.check_planarity(G)[0])
        self.assertFalse({4, 5} & gc.cycle_lengths_present(G, 5))
        self.assertFalse(S.sat_colourable(G, "cadical153"))

    def test_minimise_keeps_a_minimal_gadget(self):
        G = nx.convert_node_labels_to_integers(S.G1(), ordering="sorted", label_attribute="old")
        contacts = [v for v, d in G.nodes(data=True) if d["old"] in ("a", "b", "c")]
        self.assertEqual(pb.minimise(G, contacts, {4, 5}).number_of_nodes(), 15)


class Builder(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("ANAXIA_SLOW"), "set ANAXIA_SLOW=1 for the 11-second rediscovery run")
    def test_rediscovery_from_the_rules(self):
        out = os.path.join(os.environ.get("TMPDIR", "/tmp"), "anaxia_pb_test")
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            pb.main(["--forbid", "4", "5", "--dist", "0,1,3", "0,2,3", "1,2,4", "--max-n", "40",
                     "--tries", "116", "--seed", "1", "--out", out])
        self.assertIn("try 116 FORCER n=15", buf.getvalue())

    def test_the_forcing_argument_closes_on_G1(self):
        # gamma (the shared colour) spreads from the contacts by the forward rules; on G1 the
        # builder's status reaches a contradiction that SAT confirms
        G = nx.convert_node_labels_to_integers(S.G1(), ordering="sorted", label_attribute="old")
        contacts = [v for v, d in G.nodes(data=True) if d["old"] in ("a", "b", "c")]
        gam, non, side, comp = pb.status(G, contacts)
        self.assertTrue(set(contacts) <= gam)
        self.assertTrue(non)
        self.assertFalse(pb.contacts_can_share(G, contacts))


class Command(unittest.TestCase):
    def test_list_and_check(self):
        with contextlib.redirect_stdout(io.StringIO()) as buf:
            cli.main(["construct", "list"])
            cli.main(["construct", "check", "rediscovered_n15", "--forbid-max", "5"])
        out = buf.getvalue()
        self.assertIn("rediscovered_n15   n=15", out)
        self.assertIn("'forces_NAE': True", out)


if __name__ == "__main__":
    unittest.main()
