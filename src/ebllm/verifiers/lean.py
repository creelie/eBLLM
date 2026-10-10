"""The formal verifier: a static scan of Lean sources and an audit of `#print axioms`.

These are the checks used for the Lean proofs recorded in this project (sphere packing in
dimensions 8 and 24, the Navier-Stokes blowup proof, the Poincare formalization, the Morley
counterexample): a proof counts only if the kernel accepts it and it depends on no axiom beyond
propext, Classical.choice and Quot.sound.  `sorryAx` reveals a sorry; `Lean.ofReduceBool`
reveals native_decide.
"""
from __future__ import annotations

import os
import re
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence

STANDARD_AXIOMS = frozenset({"propext", "Classical.choice", "Quot.sound"})

SCAN_PATTERNS = {
    "sorry": r"(^|[^A-Za-z_.])sorry([^A-Za-z_]|$)",
    "admit": r"(^|[;(]|by)\s*admit\s*($|[;)])",
    "axiom declaration": r"^\s*(@\[[^]]*\]\s*)?(private |public |protected |noncomputable )*axiom\s",
    "native_decide": r"native_decide",
    "ofReduceBool": r"ofReduceBool|ofReduceNat",
    "implemented_by / extern": r"implemented_by|@\[extern",
    "unsafe": r"(^|\s)unsafe\s",
    "opaque": r"^\s*(private |public |protected )*opaque\s",
    "debug / skipKernelTC": r"set_option\s+debug|skipKernelTC",
    "environment commands": r"run_cmd|run_elab|run_meta|addDecl|modifyEnv",
    "bv_decide": r"bv_decide",
}


def _lean_files(paths: Iterable[str]) -> List[Path]:
    out = []
    for p in paths:
        p = Path(p)
        if p.is_dir():
            out.extend(sorted(p.rglob("*.lean")))
        elif p.suffix == ".lean":
            out.append(p)
    return out


def strip_comments(text: str) -> str:
    """Blank out Lean comments (`-- ...` and nested `/- ... -/`, doc comments included), keeping
    newlines so that line numbers survive.  String and character literals are respected."""
    out, i, n, depth = [], 0, len(text), 0
    ident = re.compile(r"[A-Za-z0-9_.']")
    while i < n:
        c, nxt = text[i], text[i + 1] if i + 1 < n else ""
        if depth:
            if c == "/" and nxt == "-":
                depth, i = depth + 1, i + 2
                out.append("  ")
            elif c == "-" and nxt == "/":
                depth, i = depth - 1, i + 2
                out.append("  ")
            else:
                out.append("\n" if c == "\n" else " ")
                i += 1
        elif c == "/" and nxt == "-":
            depth, i = 1, i + 2
            out.append("  ")
        elif c == "-" and nxt == "-":
            j = text.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
        elif c == '"':
            j = i + 1
            while j < n and text[j] != '"':
                j += 2 if text[j] == "\\" else 1
            out.append(text[i:j + 1])
            i = j + 1
        elif c == "'" and (i == 0 or not ident.match(text[i - 1])):
            m = re.match(r"'(\\.|[^\\'])'", text[i:])
            k = len(m.group(0)) if m else 1
            out.append(text[i:i + k])
            i += k
        else:
            out.append(c)
            i += 1
    return "".join(out)


def scan_lean_sources(paths: Iterable[str], exclude: Sequence[str] = ()) -> Dict[str, List[str]]:
    """Return {pattern label: [file:line: text, ...]}.  Comments are blanked out first (see
    `strip_comments`); an empty result for every label means the scan is clean."""
    regs = {k: re.compile(v) for k, v in SCAN_PATTERNS.items()}
    hits: Dict[str, List[str]] = {k: [] for k in SCAN_PATTERNS}
    excl = {str(Path(e)) for e in exclude}
    for f in _lean_files(paths):
        if str(f) in excl:
            continue
        raw = f.read_text(encoding="utf-8", errors="replace")
        for i, (line, orig) in enumerate(zip(strip_comments(raw).splitlines(), raw.splitlines()), 1):
            for k, r in regs.items():
                if r.search(line):
                    hits[k].append(f"{f}:{i}: {orig.strip()}")
    return hits


@dataclass
class AxiomReport:
    theorem: str
    axioms: frozenset

    @property
    def standard(self) -> bool:
        return self.axioms <= STANDARD_AXIOMS


def parse_axioms(text: str) -> List[AxiomReport]:
    """Parse the output of `#print axioms` (one report per theorem)."""
    out = []
    pat = re.compile(r"'([^']+)' (depends on axioms: \[([^\]]*)\]|does not depend on any axioms)")
    for m in pat.finditer(text):
        ax = frozenset(a.strip() for a in (m.group(3) or "").split(",") if a.strip())
        out.append(AxiomReport(m.group(1), ax))
    return out


@dataclass
class LeanAxiomVerifier:
    """Run `lake env lean` on a file that imports `imports` and prints the axioms of `theorems`,
    in the Lake project at `project`.  The factor is 1 iff Lean succeeds, every theorem is
    reported, and every theorem uses only the standard axioms."""
    project: str
    imports: Sequence[str]
    theorems: Sequence[str]
    lake: str = "lake"
    timeout: int = 3600
    last_output: str = field(default="", repr=False)

    def source(self) -> str:
        lines = [f"import {m}" for m in self.imports] + [""]
        lines += [f"#print axioms {t}" for t in self.theorems]
        return "\n".join(lines) + "\n"

    def __call__(self) -> int:
        with tempfile.NamedTemporaryFile("w", suffix=".lean", delete=False, dir=self.project) as fh:
            fh.write(self.source())
            name = fh.name
        try:
            proc = subprocess.run([self.lake, "env", "lean", os.path.basename(name)], cwd=self.project,
                                  capture_output=True, text=True, timeout=self.timeout)
        finally:
            os.unlink(name)
        self.last_output = proc.stdout + proc.stderr
        if proc.returncode != 0:
            return 0
        reports = {r.theorem: r for r in parse_axioms(self.last_output)}
        if set(reports) != set(self.theorems):
            return 0
        return int(all(r.standard for r in reports.values()))
