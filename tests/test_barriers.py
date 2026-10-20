import unittest

from ebllm.bllm import barriers as B
from ebllm.bllm import targets as T
from ebllm.bllm.boosters import LIBRARY2


def compose(*ids):
    lib = {c.id: c for c in LIBRARY2}
    out = lib[ids[0]]
    for i in ids[1:]:
        out = T.cross(out, lib[i]) or T.cross(lib[i], out)
        assert out is not None, i
    return out


class TestBarriers(unittest.TestCase):
    def test_forest_ceiling_applies_to_the_single_link_route(self):
        c = compose("ym.dobrushin", "ym.quarter", "ym.vmf", "ym.maxtree")
        self.assertTrue(c.closed)
        self.assertEqual(B.blocking(c).id, "ym.forest-ceiling")

    def test_blocks_break_the_single_site_hypothesis(self):
        c = T.Con("x", "yang-mills", "range", frozenset(), "", ("ym.dobrushin", "ym.quarter", "ym.maxtree", "ym.blocks"))
        self.assertIsNone(B.blocking(c))
        self.assertEqual(B.BARRIERS[0].failing(c), ["single-site"])

    def test_bypass_search_proposes_breakers_and_reports_gaps(self):
        c = compose("ym.dobrushin", "ym.quarter", "ym.vmf", "ym.maxtree")
        rep = B.bypass_search([c], LIBRARY2)
        self.assertEqual(rep.pruned, {c.id: "ym.forest-ceiling"})
        self.assertIn("ym.blocks", {b.breaker for b in rep.bypasses})
        self.assertIn(("ym.forest-ceiling", "quarter-influence"), {(g[0], g[1]) for g in rep.gaps})

    def test_a_hodge_barrier_with_no_breaker_reports_the_needed_construction(self):
        c = compose("h.rmclasses", "h.buskin")
        self.assertEqual(B.blocking(c).id, "hodge.hk-carriers-trivial")
        rep = B.bypass_search([c], LIBRARY2)
        self.assertTrue(rep.gaps)
        self.assertTrue(all(g[0] == "hodge.hk-carriers-trivial" for g in rep.gaps))

    def test_surgery_barrier_waits_for_a_surgery_node(self):
        plain = T.Con("h", "hodge", "coniveau", frozenset(), "", ("h.block", "h.characters"))
        self.assertIsNone(B.blocking(plain))
        moved = T.Con("m", "hodge", "coniveau", frozenset(), "", ("h.block", "h.characters", "h.blowup"))
        self.assertEqual(B.blocking(moved).id, "hodge.surgery-relocates")

    def test_other_problems_are_untouched(self):
        c = T.Con("h", "hodge", "weil4", frozenset(), "", ("h.markman",))
        self.assertIsNone(B.blocking(c))

    def test_every_breaker_names_a_library_node(self):
        ids = {c.id for c in LIBRARY2}
        for b in B.BARRIERS:
            for h in b.hypotheses:
                for node, _ in h.breakers:
                    self.assertIn(node, ids, (b.id, h.id, node))


if __name__ == "__main__":
    unittest.main()
