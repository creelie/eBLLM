"""Numbers and tables of the paper that are read from the package, so that the text cannot go stale.

Reads data/brain/anatomy.json and data/brain/growth.json (collect_brain.py) and the learn-from-failure
log src/ebllm/bllm/data/modlog.json, and writes three files that main.tex inputs:

    sections/gen_numbers.tex    macros: modules, lines, imports, tests, Lean theorems, log counts;
    sections/gen_releases.tex   the table of releases (tab:releases);
    sections/gen_modlog.tex     the table of every rule change of the log (tab:modlog).

    python3 collect_brain.py <UTC time> && python3 make_tables_round7.py
"""
import collections
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data", "brain")
REPO = os.path.abspath(os.path.join(HERE, *[".."] * 5))
SECTIONS = os.path.abspath(os.path.join(HERE, "..", "..", "sections"))
MODLOG = os.path.join(REPO, "src", "ebllm", "bllm", "data", "modlog.json")
TREE_VERSION = "3.1.0"

# Version DOIs of the archived releases (concept DOI 10.5281/zenodo.23286641).
DOI = {
    "1.0.0": "23286642", "2.0.0": "23455686", "2.0.1": "23456124", "2.1.0": "23462639",
    "3.0.0": "23464390", "3.0.1": "23464490", "3.0.2": "23466863", "3.0.3": "23467113",
    "3.0.4": "23467544", "3.0.5": "23469389", "3.1.0": "",
}
ADDED = {
    "1.0.0": "the verified-release core: schedules of the entropy law, checks, a generator interface",
    "2.0.0": "the crossing network, boosters, memory, target points, agents, the five benchmarks",
    "2.0.1": "the value $f(20)=12$ of Erd\\H{o}s problem 1183",
    "2.1.0": "the Hodge agent, the container image, the command \\texttt{anaxia}, this paper and its Lean development",
    "3.0.0": "construction mode, the DeepMind intake, the tower $B^{n}$ of builders, the registry of sources",
    "3.0.1": "paper: the version DOI of 3.0.0",
    "3.0.2": "paper: compiles on TeX Live 2026; plain abstract",
    "3.0.3": "paper: compact figures",
    "3.0.4": "paper: layout of the appendices",
    "3.0.5": "paper: wording of the abstract",
    "3.1.0": "the learn-from-failure loop and its log; reflexive lattice polytopes",
}
NAMES = {
    "core": "Core", "laws": "Laws", "proposers": "Proposers", "crossing": "Crossing", "memory": "Memory",
    "knowledge": "Knowledge", "benchmarks": "Benchmarks", "construction": "Construction",
    "interface": "Interface",
}


def load(p):
    with open(p) as f:
        return json.load(f)


def fmt(n):
    return f"{n:,}".replace(",", "{,}")


def tex(s):
    return (s.replace("\\", "\\textbackslash{}").replace("&", "\\&").replace("%", "\\%").replace("#", "\\#")
            .replace("_", "\\_").replace(">=", "$\\ge$").replace("\u2265", "$\\ge$").replace("->", "$\\to$")
            .replace("\u0151", "\\H{o}").replace("Kral'", "Kr\\'al'").replace("Erdos", "Erd\\H{o}s"))


def numbers(anat, rows, runs):
    mods = anat["modules"]
    sof = {m["module"]: m["subsystem"] for m in mods}
    imports = sum(len(m["imports"]) for m in mods)
    within = sum(1 for m in mods for t in m["imports"] if sof.get(t) == m["subsystem"])
    indeg = collections.Counter(t for m in mods for t in m["imports"])
    hub, hubn = indeg.most_common(1)[0]
    tree = [r for r in rows if r["label"] == "tree"][-1]
    first = rows[0]
    out = {
        "brainModules": len(mods), "brainImports": imports, "brainWithin": within, "brainBetween": imports - within,
        "brainLines": fmt(sum(m["loc"] for m in mods)), "brainTests": tree["tests"],
        "brainLeanPaper": tree["lean_paper"], "brainLeanEngine": tree["lean_engine"],
        "brainCommands": tree["commands"], "brainFigures": tree["figures"], "brainLibrary": tree["library"],
        "brainRegistry": tree["registry"], "brainFirstLines": fmt(first["loc_total"]),
        "brainFirstModules": first["modules"], "brainFirstTests": first["tests"],
        "brainHub": hub.replace("_", "\\_"), "brainHubIn": hubn,
        "brainGrowth": f"{sum(m['loc'] for m in mods) / first['loc_total']:.1f}",
    }
    for s in NAMES:
        ms = [m for m in mods if m["subsystem"] == s]
        out["brainMod" + NAMES[s]] = len(ms)
        out["brainLoc" + NAMES[s]] = fmt(sum(m["loc"] for m in ms))
    recs = [r for run in runs for r in run["records"]]
    out["modRuns"] = len(runs)
    out["modTargets"] = len({(run["run"], r["target"]) for run in runs for r in run["records"]})
    out["modAttempts"] = len(recs)
    out["modChanges"] = sum(1 for r in recs if r.get("change"))
    out["modBuilt"] = sum(1 for r in recs if r.get("change") and r.get("retry"))
    out["modAdvanced"] = sum(1 for r in recs if r.get("change") and r.get("retry") in ("closed", "partial"))
    out["modClosed"] = sum(1 for r in recs if r["outcome"] == "closed")
    seed = json.load(open(os.path.join(REPO, "src", "ebllm", "construct", "data", "seed_summary.json"),
                          encoding="utf-8"))["numbers"]
    out.update({"seedBound": seed["bound"], "seedChain": seed["bound"] + 1, "seedLow": seed["low"],
                "seedDelta": seed["delta680_steps"], "seedTwo": seed["c2"], "seedThree": seed["c3"],
                "seedCount": fmt(seed["polytopes"]), "seedCountThree": fmt(seed["polytopes3"])})
    for run in runs:
        rs = run["records"]
        tag = "".join(w.capitalize() for w in run["run"].split())
        out["mod" + tag + "Attempts"] = len(rs)
        out["mod" + tag + "Changes"] = sum(1 for r in rs if r.get("change"))
        out["mod" + tag + "Advanced"] = sum(1 for r in rs if r.get("change") and r.get("retry") in ("closed", "partial"))
    kinds = collections.Counter(r["change"]["kind"] for r in recs if r.get("change"))
    out["modTopKind"], out["modTopKindN"] = kinds.most_common(1)[0]
    lines = ["% generated by figures/src/make_tables_round7.py; do not edit"]
    for k, v in out.items():
        lines.append(f"\\newcommand{{\\{k}}}{{{v}}}")
    return "\n".join(lines) + "\n"


def releases(rows):
    last = {}
    for r in rows:
        if r.get("release") == "tree":
            last[TREE_VERSION] = dict(r, version=TREE_VERSION)
        elif r.get("release"):
            last[r["release"]] = r
    body = []
    for v, r in last.items():
        doi = DOI.get(v, "")
        d = r["date"][:10] if r["label"] != "tree" else "19 Oct"
        if r["label"] != "tree":
            from datetime import datetime, timezone
            t = datetime.fromisoformat(r["date"]).astimezone(timezone.utc)
            d = t.strftime("%d %b, %H:%M").lstrip("0")
        doi_cell = f"\\href{{https://doi.org/10.5281/zenodo.{doi}}}{{{doi}}}" if doi else "\\anaxiaDOIshort"
        body.append(f"\\rr {v} & \\rr {d} & \\rr {r['modules']} & \\rr {fmt(r['loc_total'])} & \\rr {r['tests']} & "
                    f"\\rr {r['lean_paper']}/{r['lean_engine']} & \\rr {ADDED.get(v, '')} & \\rr {doi_cell} \\\\")
    head = r"""% generated by figures/src/make_tables_round7.py; do not edit
\begin{table*}[t]
\caption{Every release of Anaxia, read from the repository at the tagged commit of each release. Lines are non-blank lines of Python in the package; tests are test methods; Lean counts the theorems of the paper and of the engine. Times are UTC. The DOI column gives the record number of the version DOI \texttt{10.5281/zenodo.}$N$.}
\label{tab:releases}
\centering
\footnotesize
\setlength{\tabcolsep}{3.5pt}
\begin{tabular}{@{}p{0.058\textwidth}p{0.085\textwidth}p{0.062\textwidth}p{0.055\textwidth}p{0.04\textwidth}p{0.055\textwidth}p{0.427\textwidth}p{0.07\textwidth}@{}}
\toprule
\rr Release & \rr Merged & \rr Modules & \rr Lines & \rr Tests & \rr Lean & \rr What it added & \rr DOI \\
\midrule
"""
    return head + "\n".join(body) + "\n\\bottomrule\n\\end{tabular}\n\\end{table*}\n"


def modlog(runs):
    body = []
    for run in runs:
        body.append(f"\\multicolumn{{6}}{{@{{}}l}}{{\\emph{{{tex(run.get('title', run['run']))}}}}} \\\\")
        for r in run["records"]:
            c = r.get("change")
            if not c:
                continue
            retry = r.get("retry") or "not yet built"
            body.append(f"\\rr {tex(r['target'])} & \\rr {r['attempt']} & \\rr {tex(r['diagnosis'])} & "
                        f"\\rr {tex(c['kind'])}: {tex(c['old'])} $\\to$ {tex(c['new'])} & \\rr {tex(c['improves'])} & "
                        f"\\rr {retry} \\\\")
    head = r"""% generated by figures/src/make_tables_round7.py; do not edit
\begin{table*}[t]
\caption{Every rule change in the log of the learn-from-failure loop (file \texttt{modlog.json} of the package). A row is one failed attempt: the target, the attempt, the diagnosis, the rule that was changed with its old and new value, the measurement the change was meant to improve, and the outcome of the retry under the changed rules. Records of attempts that closed carry no change and are not listed.}
\label{tab:modlog}
\centering
\scriptsize
\setlength{\tabcolsep}{3pt}
\begin{tabular}{@{}p{0.15\textwidth}p{0.03\textwidth}p{0.09\textwidth}p{0.415\textwidth}p{0.19\textwidth}p{0.06\textwidth}@{}}
\toprule
\rr Target & \rr Try & \rr Diagnosis & \rr Rule changed: old $\to$ new & \rr Meant to improve & \rr Retry \\
\midrule
"""
    return head + "\n".join(body) + "\n\\bottomrule\n\\end{tabular}\n\\end{table*}\n"


def main():
    anat = load(os.path.join(DATA, "anatomy.json"))
    rows = load(os.path.join(DATA, "growth.json"))["rows"]
    runs = load(MODLOG)["runs"]
    with open(os.path.join(SECTIONS, "gen_numbers.tex"), "w") as f:
        f.write(numbers(anat, rows, runs))
    with open(os.path.join(SECTIONS, "gen_releases.tex"), "w") as f:
        f.write(releases(rows))
    with open(os.path.join(SECTIONS, "gen_modlog.tex"), "w") as f:
        f.write(modlog(runs))
    print("wrote", SECTIONS)


if __name__ == "__main__":
    main()
