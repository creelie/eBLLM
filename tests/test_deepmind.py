import os
import subprocess
import tempfile
import unittest

from ebllm.bllm import deepmind as D
from ebllm.bllm.memory import Memory


class Manifest(unittest.TestCase):
    def test_every_repository_has_one_tag(self):
        rows = D.manifest()
        self.assertEqual(len(rows), 409)
        self.assertEqual(len({r["name"] for r in rows}), 409)
        self.assertTrue(all(r["tag"] in ("vendor", "related", "none") for r in rows))

    def test_pins_are_full_commits_with_a_reason(self):
        pins = D.pins()
        self.assertEqual(sum(r["tag"] == "vendor" for r in pins.values()), 22)
        for r in pins.values():
            self.assertRegex(r["commit"], r"^[0-9a-f]{40}$")
            self.assertTrue(r["why"])
        self.assertIn("formal-conjectures", pins)

    def test_unpinned_repository_is_refused(self):
        with self.assertRaises(KeyError):
            D.fetch("mujoco", tempfile.mkdtemp())

    def test_checkout_at_another_commit_is_refused(self):
        root = tempfile.mkdtemp()
        dest = os.path.join(root, "funsearch")
        os.makedirs(dest)
        env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t", GIT_COMMITTER_NAME="t",
                   GIT_COMMITTER_EMAIL="t@t")
        subprocess.run(["git", "init", "-q"], cwd=dest, check=True)
        subprocess.run(["git", "commit", "-q", "--allow-empty", "-m", "x"], cwd=dest, check=True, env=env)
        with self.assertRaises(RuntimeError):
            D.fetch("funsearch", root)


class Index(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = D.load_index()

    def test_counts(self):
        s = D.summary(self.index)
        fc = s["formal-conjectures"]
        self.assertGreater(fc["open"], 1400)
        self.assertGreater(fc["solved"], 2400)
        self.assertEqual(s["alphaevolve_repository_of_problems"]["construction-problem"], 68)

    def test_links_are_pinned(self):
        pins = D.pins()
        for it in self.index["items"]:
            self.assertIn(f"/blob/{pins[it['source']]['commit']}/", it["link"])

    def test_search_finds_the_cap_set_and_the_status(self):
        s = D.Search(self.index["items"])
        self.assertEqual(s("cap set", 1)[0]["source"], "funsearch")
        hit = s("Goldbach even integer sum of two primes", 1, status="open")[0]
        self.assertEqual(hit["name"], "goldbach")
        self.assertEqual(s("zzzz qqqq", 3), [])

    def test_tokenize_folds_spelling_and_plurals(self):
        self.assertEqual(D.tokenize("Colourings of graphs"), ["coloring", "graph"])

    def test_memory_receives_literature_and_nodes(self):
        m = Memory()
        n = D.load_into_memory(m, self.index)
        self.assertGreater(n["literature"], 4000)
        rows = m.db.execute("SELECT verdict FROM literature WHERE claim LIKE 'formal-conjectures:%goldbach'").fetchall()
        self.assertIn(("open",), rows)
        self.assertEqual(m.db.execute("SELECT count(*) FROM nodes WHERE problem='external'").fetchone()[0], n["nodes"])


if __name__ == "__main__":
    unittest.main()
