import os
import tempfile
import unittest
from pathlib import Path

from ebllm.bllm import figcritic as FC

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ASSETS = os.path.join(ROOT, "docs", "assets")
STILL = "<style>@media (prefers-reduced-motion:reduce){*{animation:none}}</style>"


def write(body, w=400, h=100, label="a figure", extra=""):
    f = tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False)
    f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{label}" {extra}>'
            f'{body}</svg>')
    f.close()
    return f.name


def t(x, y, s, size=14, anchor="start"):
    return f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}">{s}</text>'


class TestFigCritic(unittest.TestCase):
    @unittest.skipUnless(os.path.isdir(ASSETS), "the README figures are not shipped with the package")
    def test_readme_figures_pass(self):
        self.assertEqual(FC.review(ASSETS), [])

    def test_a_clean_figure_passes(self):
        self.assertEqual(FC.critique(write(t(10, 50, "fits easily") + t(390, 80, "right", anchor="end"))), [])

    def test_refuter_catches_each_rule(self):
        cases = {
            "runs past the canvas": write(t(300, 50, "this label is far too long for the canvas")),
            "outside the canvas height": write(t(10, 180, "low")),
            "caption inside": write(t(10, 50, "Figure 3: overview")),
            "overlap": write(t(10, 50, "first label here") + t(60, 50, "second label")),
            "aria-label": write(t(10, 50, "x"), label=""),
            "reduced-motion": write("<style>@keyframes a{to{opacity:0}}</style>" + t(10, 50, "x")),
            "under a minute": write(STILL + "<style>@keyframes a{to{opacity:0}}.m{animation:a 90s infinite}</style>" + t(10, 50, "x")),
            "empty label": write(t(10, 50, " ")),
            "not well-formed": write("<text>"),
        }
        for want, path in cases.items():
            found = " ".join(FC.critique(path))
            self.assertIn(want, found, want)

    def test_translated_groups_are_placed(self):
        inside = write('<g transform="translate(300,0)">' + t(0, 50, "short") + "</g>")
        outside = write('<g transform="translate(350,0)">' + t(0, 50, "a longer label") + "</g>")
        self.assertEqual(FC.critique(inside), [])
        self.assertTrue(FC.critique(outside))

    def test_themes_must_carry_the_same_text(self):
        d = tempfile.mkdtemp()
        for theme, n in (("light", "64"), ("dark", "65")):
            with open(os.path.join(d, f"fig-{theme}.svg"), "w") as f:
                f.write(Path(write(t(10, 50, n))).read_text())
        self.assertTrue(any("differ at label" in x for x in FC.review(d)))


if __name__ == "__main__":
    unittest.main()
