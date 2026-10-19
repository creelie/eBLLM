import unittest

from ebllm.bllm import sources as S
from ebllm.bllm.checks import Candidate
from ebllm.bllm.vault import Vault

FIELDS = ("id", "group", "name", "kind", "reference", "doi", "url", "status", "taken", "where", "adds", "left",
          "weights")


class Registry(unittest.TestCase):
    def test_entries_are_complete_and_unique(self):
        rows = S.registry()
        self.assertEqual(len({r["id"] for r in rows}), len(rows))
        for r in rows:
            self.assertEqual(set(r), set(FIELDS), r["id"])
            self.assertTrue(r["reference"] and r["taken"] and r["status"], r["id"])
            if r["doi"]:
                self.assertRegex(r["doi"], r"^10\.\d{4,5}/\S+$")

    def test_no_model_weights_are_bundled(self):
        for r in S.registry():
            if r["group"] == "Provers and models":
                self.assertTrue(r["weights"].startswith(("not", "none")), r["id"])

    def test_the_groups_asked_for_are_there(self):
        groups = {r["group"] for r in S.registry()}
        for g in ("Google DeepMind", "OpenAI", "The Omega Institute", "Memory", "Provers and models"):
            self.assertIn(g, groups)


class Indexes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = S.load_external()

    def test_counts(self):
        s = S.summary(self.items)
        self.assertEqual(sum(s["openrefute"].values()), 782)
        self.assertEqual(s["openai-math"], {"unrefereed": 722})

    def test_openai_items_are_marked_unrefereed(self):
        self.assertTrue(all(i["status"] == "unrefereed" for i in self.items if i["source"] == "openai-math"))

    def test_resolution_reading(self):
        self.assertEqual(S.resolution("`theorem`; resolution `refuted`.", "theorem"), "refuted")
        self.assertEqual(S.resolution("`theorem`. Proved for every n.", "theorem"), "proved")
        self.assertEqual(S.resolution("blocked", "wall"), "open")

    def test_check_finds_a_refuted_conjecture(self):
        hit = S.check("sequential weak measurements projections pointer positions", 1)[0]
        self.assertEqual((hit["source"], hit["status"]), ("openrefute", "refuted"))
        self.assertEqual(hit["name"], "abbott-2019-sequential-weak-pointer-bound")


class VaultSearch(unittest.TestCase):
    def test_a_hit_brings_its_link_neighbours(self):
        v = Vault()
        a = Candidate(id="lemma-a", kind="identity", statement={"problem": "p", "lhs": "x", "rhs": "y"},
                      agent="t", move="cross", parents=(), rationale="triangle gadget with pendant edges")
        b = Candidate(id="gadget-b", kind="identity", statement={"problem": "p", "lhs": "x", "rhs": "z"},
                      agent="t", move="cross", parents=("lemma-a",), rationale="forcing gadget from the lemma")
        v.keep(a, "ok", 1.0)
        v.keep(b, "ok", 1.0)
        hits = v.search("forcing gadget", 5)
        self.assertEqual(hits[0]["id"], "gadget-b")
        self.assertEqual(hits[1]["id"], "lemma-a")
        self.assertEqual(hits[1]["found"], "linked to gadget-b")


if __name__ == "__main__":
    unittest.main()
