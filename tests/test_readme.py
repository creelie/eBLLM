"""The README is also the page of the image on ghcr.io, so it must agree with the package it describes."""
import os
import re
import unittest

from ebllm import __version__

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
README = os.path.join(ROOT, "README.md")


def read(*parts):
    with open(os.path.join(ROOT, *parts), encoding="utf-8") as f:
        return f.read()


def lean_counts():
    paper = sum(1 for line in read("paper", "bllm", "lean", "axioms.txt").splitlines()
                if "depends on axioms" in line)
    engine = sum(1 for line in read("lean", "Audit.lean").splitlines() if line.startswith("#print axioms"))
    return paper, engine


@unittest.skipUnless(os.path.exists(README), "README.md is not shipped with the installed package")
class TestReadme(unittest.TestCase):
    def setUp(self):
        self.text = read("README.md")

    def test_names_the_current_release(self):
        self.assertIn(f"## New in {__version__}", self.text)

    def test_lean_counts_match_the_audits(self):
        paper, engine = lean_counts()
        self.assertIn(f"Lean%204-{paper + engine}%20theorems", self.text)
        self.assertIn(f"anaxia axioms audit.log {engine} ", self.text)
        self.assertIn(f"axiom audit of all {engine} theorems", self.text)
        self.assertIn(f"({engine} theorems, Lean core)", self.text)
        self.assertIn(f"({paper} theorems, Mathlib)", self.text)

    def test_every_archived_version_doi_is_listed(self):
        cff = read("CITATION.cff")
        dois = re.findall(r"value: (10\.5281/zenodo\.\d+)", cff)
        self.assertTrue(dois)
        for doi in dois:
            self.assertIn(f"[{doi}](https://doi.org/{doi})", self.text, doi)

    def test_links_and_images_are_absolute(self):
        # the package page renders the README away from the repository, where relative paths break
        for m in re.finditer(r'(?:src|srcset|href)="([^"]+)"', self.text):
            self.assertTrue(m.group(1).startswith(("https://", "#")), m.group(1))
        for m in re.finditer(r"\]\(([^)]+)\)", self.text):
            self.assertTrue(m.group(1).startswith(("https://", "#")), m.group(1))

    def test_names_no_tool_as_contributor(self):
        self.assertNotIn("Co-Authored-By", self.text)
        self.assertNotIn("Generated with", self.text)


if __name__ == "__main__":
    unittest.main()
