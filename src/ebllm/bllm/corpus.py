"""How conjectures get solved: the moves of recorded solutions, read from public corpora.

Three sources, none vendored; each is read from a local clone whose path the caller passes:

* OpenAI's mathematics manuscript collection (github.com/openai/math, Apache-2.0): 722
  manuscripts in 372 result families from about 4,000 posed problems, with a Lean catalogue
  (`lean/formalization.yaml`) naming the manuscripts whose main result is formalised.
* Google DeepMind's AlphaProof Nexus results (github.com/google-deepmind, Apache-2.0 code,
  CC-BY prose): the Erdős problems attempted (`erdos_problems_attempted.txt`) and the Lean proofs
  found (`APNOutputs/`).
* Hand-labelled solutions whose moves are known from their papers: classical proofs (Fermat,
  Wiles, Perelman, Viazovska, Witten) and the six Hexagon preprints of Bhattacharjee and
  Bhattacharya.

`classify` labels a title and abstract with the moves it names by keyword rules; it is a reading
aid, not a semantic analysis, and its counts measure what the abstracts say about method.
"""
from __future__ import annotations

import json
import os
import re
from collections import Counter
from typing import Dict, List, Optional, Sequence

MOVES = ("reduction", "lift", "certificate", "construction", "counterexample", "flow-surgery",
         "descent", "physics-first")

RULES = {
    "counterexample": r"counterexample|disprov|refut|negative answer|is false|fails? (?:for|in|to)",
    "certificate": r"certificate|computer-assisted|computer assisted|linear programming|semidefinite|"
                   r"sum[- ]of[- ]squares|interval arithmetic|exact value|rigorous(?:ly)? (?:numer|comput)|"
                   r"verified by (?:a )?comput|explicit (?:bound|constant)",
    "construction": r"\bconstruct|we exhibit|explicit (?:example|family|construction|graph|group)|"
                    r"we give an? (?:explicit )?example",
    "reduction": r"reduc|equivalent to|is equivalent|conditional|assuming|we deduce|as a consequence|"
                 r"follows? from|implies",
    "lift": r"special case|\blift|deform|speciali[sz]|bootstrap|propagat|base case|from the case|"
            r"extends? (?:to|from)|upgrade",
    "flow-surgery": r"\bflow|surgery|ricci|heat (?:equation|kernel)|gradient|parabolic|monotonicity formula|"
                    r"evolution equation",
    "descent": r"descent|induction|inductive|minimal counterexample|iterat",
    "physics-first": r"quantum|spin glass|gibbs|ising|potts|field theor|hamiltonian|statistical mechanic|"
                     r"free energy|partition function|replica|magneti[sz]|gauge theor|vlasov|fermion",
}
_RX = {k: re.compile(v, re.I) for k, v in RULES.items()}


def classify(text: str) -> List[str]:
    return [m for m in MOVES if _RX[m].search(text)]


def _norm(s: str) -> str:
    s = re.sub(r"\$[^$]*\$", "", s)
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


# -- OpenAI collection -----------------------------------------------------------------------------
def read_openai(root: str) -> Dict[str, object]:
    text = open(os.path.join(root, "CONTENTS.md"), encoding="utf-8").read()
    fam_rx = re.compile(r"^\*\*(\d{3})\. (.+?)\.\*\* (.*)$", re.M)
    man_rx = re.compile(r"^&emsp;\[(.+?)\]\((preprints/.+?\.pdf)\)[^\n]*\n\s*\n(.+?)\n", re.M)
    families = {m.group(1): dict(title=m.group(2), summary=m.group(3)) for m in fam_rx.finditer(text)}
    starts = sorted((m.start(), m.group(1)) for m in fam_rx.finditer(text))
    manuscripts = []
    for m in man_rx.finditer(text):
        fam = None
        for pos, f in starts:
            if pos < m.start():
                fam = f
        manuscripts.append(dict(family=fam, title=m.group(1), path=m.group(2), abstract=m.group(3)))
    yaml = open(os.path.join(root, "lean", "formalization.yaml"), encoding="utf-8").read()
    src = yaml.split("\nsources:", 1)[1].split("\nrelated_formalizations:", 1)[0]
    formal_titles = {_norm(t) for t in re.findall(r'title: "(.+?)"', src)}
    status = yaml.split("\nstatus:", 1)[1].split("\nautomation:", 1)[0]
    main_files = re.findall(r"file: (\S+)", status)
    for d in manuscripts:
        d["formalized"] = _norm(d["title"]) in formal_titles
        d["moves"] = classify(d["title"] + " " + d["abstract"])
    lines = []
    for f in main_files:
        folder = os.path.join(root, "lean", os.path.dirname(f))
        n = 0
        for dirpath, _, names in os.walk(folder):
            for name in names:
                if name.endswith(".lean"):
                    with open(os.path.join(dirpath, name), encoding="utf-8", errors="replace") as h:
                        n += sum(1 for _ in h)
        lines.append(n)
    return dict(families=families, manuscripts=manuscripts, main_result_files=main_files,
                lean_lines=lines, formal_titles=len(formal_titles))


# -- AlphaProof Nexus ------------------------------------------------------------------------------
def read_alphaproof(root: str) -> Dict[str, object]:
    attempted = [x.strip() for x in open(os.path.join(root, "erdos_problems_attempted.txt")) if x.strip()]
    out = {}
    for folder in sorted(os.listdir(os.path.join(root, "APNOutputs"))):
        files = []
        for dirpath, _, names in os.walk(os.path.join(root, "APNOutputs", folder)):
            for name in names:
                if name.endswith(".lean"):
                    with open(os.path.join(dirpath, name), encoding="utf-8", errors="replace") as h:
                        files.append((name[:-5], sum(1 for _ in h)))
        out[folder] = files
    solved = {n for n, _ in out.get("ErdosProblems", [])}
    return dict(attempted=attempted, outputs=out, erdos_solved=sorted(solved),
                erdos_solved_attempted=sorted(solved & set(attempted)))


# -- hand-labelled solutions ---------------------------------------------------------------------
LABELLED = [
    dict(name="Fermat, n = 4", source="Weil 1984", moves=["descent"], lean=True),
    dict(name="Fermat's Last Theorem (Wiles, Taylor-Wiles)", source="Wil95; TW95",
         moves=["lift", "reduction"], lean=True),
    dict(name="Poincare conjecture (Perelman)", source="Per02; Per03a; Per03b",
         moves=["flow-surgery", "reduction"], lean=False),
    dict(name="Sphere packing in dimension 8 (Viazovska)", source="Via17; CE03",
         moves=["certificate", "construction"], lean=True),
    dict(name="Kissing numbers 240 and 196560 (Levenshtein; Odlyzko-Sloane)", source="Lev79; OS79",
         moves=["certificate"], lean=False),
    dict(name="Jones polynomial from Chern-Simons theory (Witten)", source="Wit89",
         moves=["physics-first"], lean=False),
    dict(name="Polya-Vinogradov with log log q", source="hexagon:2610.00256",
         moves=["reduction"], lean=True),
    dict(name="Dense algebraic loci of Hodge classes (not a closure)", source="hexagon:2610.00315",
         moves=["reduction", "lift", "construction"], lean=True),
    dict(name="Golomb-Welch, no lattice tiling of Z^35 and Z^805 by Lee balls of radius 3",
         source="hexagon:2610.00317", moves=["reduction", "certificate"], lean=True),
    dict(name="Kourovka 20.71(b)", source="hexagon:2610.00318", moves=["construction"], lean=True),
    dict(name="Odd antiholes are strongly chromatic-choosable", source="hexagon:2610.00319",
         moves=["descent"], lean=True),
    dict(name="sl(2) weight system at c = -3/32 is a graph 4-invariant", source="hexagon:2610.00320",
         moves=["physics-first", "construction"], lean=True),
]


def move_statistics(manuscripts: Sequence[dict]) -> Dict[str, dict]:
    """Per move: manuscripts naming it, how many have a formalised main result, the rate."""
    out = {}
    for m in MOVES:
        sel = [d for d in manuscripts if m in d["moves"]]
        f = sum(1 for d in sel if d["formalized"])
        out[m] = dict(manuscripts=len(sel), formalized=f, rate=round(f / len(sel), 4) if sel else None)
    return out


def summarise(openai_root: Optional[str] = None, alphaproof_root: Optional[str] = None) -> dict:
    out: Dict[str, object] = dict(moves=list(MOVES), labelled=LABELLED,
                                  labelled_counts=dict(Counter(m for d in LABELLED for m in d["moves"])))
    if openai_root:
        o = read_openai(openai_root)
        man = o["manuscripts"]
        lines = sorted(o["lean_lines"])
        out["openai"] = dict(
            source="github.com/openai/math (Apache-2.0), read from the fork creelie/math01-openAI",
            problems_posed_about=4000, families=len(o["families"]), manuscripts=len(man),
            formalized_manuscripts=sum(d["formalized"] for d in man),
            catalogue_titles=o["formal_titles"], main_results=len(o["main_result_files"]),
            unlabelled=sum(1 for d in man if not d["moves"]),
            moves=move_statistics(man),
            lean_lines_per_main_result=dict(min=lines[0], median=lines[len(lines) // 2], max=lines[-1],
                                            total=sum(lines)) if lines else None)
    if alphaproof_root:
        a = read_alphaproof(alphaproof_root)
        out["alphaproof"] = dict(
            source="AlphaProof Nexus results (Google DeepMind; Apache-2.0 code, CC-BY prose), "
                   "read from the fork creelie/alphaproof-nexus-results",
            erdos_attempted=len(a["attempted"]), erdos_solved=len(a["erdos_solved"]),
            erdos_solved_in_attempted=len(a["erdos_solved_attempted"]),
            outputs={k: dict(files=len(v), lines=sum(n for _, n in v)) for k, v in a["outputs"].items()})
    return out


if __name__ == "__main__":
    import sys
    print(json.dumps(summarise(*sys.argv[1:3]), indent=1))


# -- Erdős problems ---------------------------------------------------------------------------------
# Sources: T. Tao et al., the Erdős problem database github.com/teorth/erdosproblems (data/problems.yaml,
# data/statistics_history.csv, and its wiki page "AI contributions to Erdős problems", frozen 30 Jun
# 2026), and T. F. Bloom, erdosproblems.com, whose problem pages carry the history of each solution.
SETTLED = ("proved", "disproved", "solved")

ERDOS_STRATEGIES = {
    "probabilistic": r"probabilistic|random (?:construction|graph|set|subset|colou?ring)|local lemma|"
                     r"second moment|first moment|alteration|random greedy",
    "density-increment": r"density increment|regularity lemma|szemer[eé]di|\broth\b|hypergraph removal",
    "fourier": r"fourier|exponential sum|circle method|character sum|large sieve|sieve",
    "entropy": r"entropy",
    "lp-sdp-certificate": r"linear programming|semidefinite|flag algebra|sum of squares|\bcertificate",
    "computer-search": r"computer|computation|exhaustive|sat solver|computer search|computed|verified up to",
    "construction": r"\bconstruct|construction|we exhibit|explicit example",
    "counterexample": r"counterexample|disprov|the answer is no|is false",
    "induction-descent": r"induction|inductive|descent",
    "known-machinery": r"application of|as a consequence of|follows from|follows immediately|corollary of|"
                       r"machinery|using the (?:\w+ ){0,3}theorem",
    "polynomial-method": r"polynomial method|nullstellensatz|slice rank|cap set",
}
_ERX = {k: re.compile(v, re.I) for k, v in ERDOS_STRATEGIES.items()}
# AI systems named in a problem's commentary (the page credits the solver of each result)
AI_SYSTEMS = re.compile(r"\bGPT[- ]?\d|\bo[34](?:-\w+)?\b|Gemini|AlphaProof|AlphaEvolve|Aristotle|Claude|"
                        r"Seed[- ]?Prover|DeepMind|Grok|Kimina|Goedel[- ]Prover", re.I)


def read_erdos_db(root: str) -> dict:
    import csv
    import yaml as _yaml
    probs = _yaml.safe_load(open(os.path.join(root, "data", "problems.yaml"), encoding="utf-8"))
    rows = list(csv.DictReader(open(os.path.join(root, "data", "statistics_history.csv"), encoding="utf-8")))
    return dict(problems=probs, history=rows)


def _page_text(path: str) -> str:
    import html as _html
    t = open(path, encoding="utf-8", errors="replace").read()
    t = re.sub(r"<script.*?</script>|<style.*?</style>", " ", t, flags=re.S)
    s = re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", t)))
    s = s.split(" Random ", 1)[-1]
    return s.split("This page was last edited", 1)[0].split("Additional thanks", 1)[0]


def erdos_strategies(text: str) -> List[str]:
    return [k for k in ERDOS_STRATEGIES if _ERX[k].search(text)]


def read_ai_wiki(path: str) -> List[dict]:
    """Rows of the tables of the wiki page "AI contributions to Erdős problems"."""
    rows, section = [], ""
    for line in open(path, encoding="utf-8"):
        m = re.match(r"### (\d\([a-d]\))\. (.+)", line)
        if m:
            section = m.group(1)
        m = re.match(r"\| \[\[(\d+)\]\]\([^)]*\) \| (.*?) \| (.*?) \| (.*)", line)
        if m:
            out = m.group(4)
            color = ("full" if "🟢" in out else "partial" if "🟡" in out else
                     "incorrect" if "🔴" in out else "unverified" if "⚪" in out else "other")
            rows.append(dict(problem=int(m.group(1)), systems=m.group(2).strip(), date=m.group(3).strip(),
                             outcome=color, lean="(Lean)" in out, section=section, text=out.strip()))
    return rows


def summarise_erdos(db_root: str, wiki_page: Optional[str] = None, pages: Optional[str] = None) -> dict:
    db = read_erdos_db(db_root)
    probs = db["problems"]
    st = Counter(p["status"]["state"] for p in probs)
    inf = Counter(p["informal_status"]["state"] for p in probs)
    settled = [p for p in probs if p["informal_status"]["state"] in SETTLED]
    lean = [p for p in probs if p["formal_status"]["state"] != "unformalized"]
    tags = Counter(t for p in settled for t in p.get("tags", []))
    prize_settled = sum(1 for p in settled if p["prize"] not in ("no", "", None))
    first, last = db["history"][0], db["history"][-1]
    monthly = {}
    for r in db["history"]:
        monthly[r["date"][:7]] = dict(solved=int(r["total_solved"]), lean_solved=int(r["lean_solved"]),
                                      statements=int(r["lean_formalized"]), total=int(r["total_problems"]))
    out = dict(source="github.com/teorth/erdosproblems (data/problems.yaml) and erdosproblems.com",
               measured_at=last["date"], problems=len(probs), status=dict(st), informal=dict(inf),
               settled=len(settled), lean_solutions=len(lean),
               settled_with_lean=sum(1 for p in settled if p["formal_status"]["state"] != "unformalized"),
               open_with_lean=sum(1 for p in lean if p["informal_status"]["state"] == "open"),
               statements_formalized=sum(1 for p in probs if p["formalized"]["state"] == "yes"),
               prizes=sum(1 for p in probs if p["prize"] not in ("no", "", None)), prize_settled=prize_settled,
               settled_by_tag=dict(tags.most_common(15)), history_months=monthly,
               history_first=first["date"])
    if wiki_page:
        rows = read_ai_wiki(wiki_page)
        by = Counter(r["outcome"] for r in rows)
        lean_by = Counter(r["outcome"] for r in rows if r["lean"])
        sec = {}
        for r in rows:
            sec.setdefault(r["section"], Counter())[r["outcome"]] += 1
        full_problems = sorted({r["problem"] for r in rows if r["outcome"] == "full"})
        out["ai_wiki"] = dict(source="github.com/teorth/erdosproblems/wiki/AI-contributions-to-Erdős-problems "
                                     "(frozen 30 Jun 2026)",
                              entries=len(rows), outcomes=dict(by), lean_outcomes=dict(lean_by),
                              by_section={k: dict(v) for k, v in sorted(sec.items())},
                              problems=len({r["problem"] for r in rows}),
                              full_solution_problems=len(full_problems))
    if pages:
        per, cnt, cnt_lean, cnt_ai = {}, Counter(), Counter(), Counter()
        lean_ids = {p["number"] for p in lean}
        for p in settled:
            f = os.path.join(pages, f"{p['number']}.html")
            if not os.path.exists(f):
                continue
            text = _page_text(f)
            s = erdos_strategies(text)
            ai = bool(AI_SYSTEMS.search(text))
            per[p["number"]] = dict(status=p["informal_status"]["state"], strategies=s,
                                    lean=p["number"] in lean_ids, tags=p.get("tags", []), ai_named=ai)
            if ai:
                cnt_ai.update(s or ["unlabelled"])
            cnt.update(s or ["unlabelled"])
            if p["number"] in lean_ids:
                cnt_lean.update(s or ["unlabelled"])
        out["strategies"] = dict(pages=len(per), counts=dict(cnt.most_common()),
                                 lean_counts=dict(cnt_lean.most_common()),
                                 ai_named=sum(1 for v in per.values() if v["ai_named"]),
                                 ai_named_lean=sum(1 for v in per.values() if v["ai_named"] and v["lean"]),
                                 ai_counts=dict(cnt_ai.most_common()), per_problem=per)
    return out
