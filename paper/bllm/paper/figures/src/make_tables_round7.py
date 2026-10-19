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
import math
import os
import re

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
    "3.0.4": "23467544", "3.0.5": "23469389", "3.1.0": "23484160",
}
# The stages in which the engine was built: the archived versions that changed it, with what each built.
STAGES = ("1.0.0", "2.0.0", "2.1.0", "3.0.0", "3.1.0")
ADDED = {
    "1.0.0": "the verified-release core: schedules of the entropy law, checks, a generator interface",
    "2.0.0": "the crossing network, boosters, memory, target points, agents, the five benchmarks and the "
             "searches of Erd\\H{o}s problem 1183",
    "2.1.0": "the Hodge agent, the container image, the command \\texttt{anaxia} and the Lean development of the paper",
    "3.0.0": "construction mode, the DeepMind intake, the tower $B^{n}$ of builders, the registry of sources",
    "3.1.0": "the learn-from-failure loop, its log and its skill memory, the screens, covers, descents and free sums of reflexive "
             "polytopes, the seed benchmark",
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


# Phrases of the log that are formulas, set as such before the text is escaped.
MATH = {
    "d = 2^j": r"$d=2^{j}$",
    "g_i = gcd(d, v_i)": r"$g_{i}=\gcd(d,v_{i})$",
    "sum g_i ceil(2(d/g_i)/(K+1)) < d": r"$\sum g_{i}\lceil 2(d/g_{i})/(K+1)\rceil<d$",
    "[-d, d]": r"$[-d,d]$",
    "K+1": r"$K+1$",
    "Erdős-Straus": r"Erd\H{o}s--Straus",
    "Nyman-Beurling": "Nyman--Beurling",
    "the square root of X": r"$\sqrt{X}$",
    "d-separated": r"$d$-separated",
    "divisible by d": r"divisible by $d$",
    "W(J)": r"$W(J)$",
    "E(N)": r"$E(N)$",
    "past c_0": r"past $c_{0}$",
    "Yang-Mills": "Yang--Mills",
    "g^(d)(8)": r"$g^{(d)}(8)$",
    "R^3": r"$\mathbb{R}^{3}$",
    "R^4": r"$\mathbb{R}^{4}$",
    "R^5": r"$\mathbb{R}^{5}$",
    "kappa contracted": r"$\kappa$ contracted",
    "inside W": r"inside $W$",
    "of m sets": r"of $m$ sets",
    "r + s >= m - 1": r"$r+s\ge m-1$",
    "m = 13": r"$m=13$",
    "values of m": r"values of $m$",
    "beta_W < 0.366": r"$\beta_{W}<0.366$",
    "beta_W <= 45/64": r"$\beta_{W}\le45/64$",
    "SU(3)": r"$\mathrm{SU}(3)$",
    "SU(N)": r"$\mathrm{SU}(N)$",
}


def tex(s):
    keep = {}
    for k, (raw, out) in enumerate(sorted(MATH.items(), key=lambda kv: -len(kv[0]))):
        if raw in s:
            s = s.replace(raw, f"@@{k}@@")
            keep[f"@@{k}@@"] = out
    s = _tex(s)
    for k, v in keep.items():
        s = s.replace(k, v)
    return s


def _tex(s):
    return (s.replace("\\", "\\textbackslash{}").replace("&", "\\&").replace("%", "\\%").replace("#", "\\#")
            .replace("_", "\\_").replace(">=", "$\\ge$").replace("\u2265", "$\\ge$").replace("->", "$\\to$")
            .replace("\u0151", "\\H{o}").replace("Kral'", "Kr\\'al'").replace("Erdos", "Erd\\H{o}s")
            .replace("E\\_0^6", "$E_0^6$").replace("sqrt 10", "$\\sqrt{10}$"))


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
    out["modRetryClosed"] = sum(1 for r in recs if r.get("change") and r.get("retry") == "closed")
    out["modRetryPartial"] = sum(1 for r in recs if r.get("change") and r.get("retry") == "partial")
    seed = json.load(open(os.path.join(REPO, "src", "ebllm", "construct", "data", "seed_summary.json"),
                          encoding="utf-8"))["numbers"]
    out.update({"seedBound": seed["bound"], "seedChain": seed["bound"] + 1, "seedLow": seed["low"],
                "seedDelta": seed["delta680_steps"], "seedTwo": seed["c2"], "seedThree": seed["c3"],
                "seedCount": fmt(seed["polytopes"]), "seedCountThree": fmt(seed["polytopes3"])})
    for run in runs:
        rs = run["records"]
        tag = "".join(w.capitalize() for w in re.split(r"[^A-Za-z]+", run["run"]) if w)
        out["mod" + tag + "Attempts"] = len(rs)
        out["mod" + tag + "Changes"] = sum(1 for r in rs if r.get("change"))
        out["mod" + tag + "Advanced"] = sum(1 for r in rs if r.get("change") and r.get("retry") in ("closed", "partial"))
    kinds = collections.Counter(r["change"]["kind"] for r in recs if r.get("change"))
    out["modTopKind"], out["modTopKindN"] = kinds.most_common(1)[0]
    own = [r for run in runs if run["run"] in OWN for r in run["records"]]
    other = [r for run in runs if run["run"] not in OWN for r in run["records"]]
    okinds = collections.Counter(r["change"]["kind"] for r in own if r.get("change"))
    out["modOwnTopKind"], out["modOwnTopKindN"] = okinds.most_common(1)[0]
    words = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
             "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen", "twenty")
    ocheck = collections.Counter(r["change"]["kind"] for r in other if r.get("change"))
    for k in ("representation", "strategy", "check"):
        out["modKind" + k.capitalize()] = words[kinds[k]] if kinds[k] < len(words) else kinds[k]
        out["modOwnKind" + k.capitalize()] = words[okinds[k]] if okinds[k] < len(words) else okinds[k]
        out["modOtherKind" + k.capitalize()] = words[ocheck[k]] if ocheck[k] < len(words) else ocheck[k]
    out["modOtherRuns"] = sum(1 for run in runs if run["run"] not in OWN)
    out["modOtherChanges"] = sum(1 for r in other if r.get("change"))
    out["modOtherChecks"] = sum(1 for r in other if r.get("change") and r["change"]["kind"] == "check")
    out["modOtherOverclaim"] = sum(1 for r in other if r.get("change") and r["diagnosis"] == "overclaim")
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
    for k, v in enumerate(STAGES):
        r = last[v]
        doi = DOI.get(v, "")
        d = "19 Oct"
        if r["label"] != "tree":
            from datetime import datetime, timezone
            d = datetime.fromisoformat(r["date"]).astimezone(timezone.utc).strftime("%d %b").lstrip("0")
        doi_cell = f"\\href{{https://doi.org/10.5281/zenodo.{doi}}}{{{doi}}}" if doi else "\\anaxiaDOIshort"
        body.append(f"\\rr {'I II III IV V'.split()[k]} ({v}) & \\rr {d} & \\rr {r['modules']} & "
                    f"\\rr {fmt(r['loc_total'])} & \\rr {r['tests']} & \\rr {r['lean_paper']}/{r['lean_engine']} & "
                    f"\\rr {ADDED[v]} & \\rr {doi_cell} \\\\")
    head = r"""% generated by figures/src/make_tables_round7.py; do not edit
\begin{table*}[t]
\caption{The five stages in which Anaxia was built, each read from the repository at the commit archived for it. Lines are non-blank lines of Python in the package; tests are test methods; Lean counts the theorems of the paper and of the engine. The last column gives the record number $N$ of the DOI \texttt{10.5281/zenodo.}$N$ under which the stage is archived.}
\label{tab:releases}
\centering
\footnotesize
\setlength{\tabcolsep}{3.5pt}
\begin{tabular}{@{}p{0.075\textwidth}p{0.05\textwidth}p{0.062\textwidth}p{0.055\textwidth}p{0.04\textwidth}p{0.055\textwidth}p{0.445\textwidth}p{0.07\textwidth}@{}}
\toprule
\rr Stage & \rr Date & \rr Modules & \rr Lines & \rr Tests & \rr Lean & \rr What it built & \rr Archive \\
\midrule
"""
    return head + "\n".join(body) + "\n\\bottomrule\n\\end{tabular}\n\\end{table*}\n"


# The runs of this engine; the other runs of the log were recorded by the attacks that used it.
OWN = ("construction", "seed", "hodge")


def modlog(runs):
    own = [r for r in runs if r["run"] in OWN]
    other = [r for r in runs if r["run"] not in OWN]
    cap_own = ("Every rule change in the runs of the engine itself in the log of the learn-from-failure loop "
               "(file \\texttt{modlog.json} of the package). A row is one failed attempt: the target, the attempt, "
               "the diagnosis, the rule that was changed with its old and new value, the measurement the change was "
               "meant to improve, and the outcome of the retry under the changed rules. Records of attempts that "
               "closed carry no change and are not listed; the runs of the other attacks are in "
               "Table~\\ref{tab:modlogother}.")
    cap_other = ("Every rule change in the runs that the other attacks of 19 October logged in the same format, "
                 "with the columns of Table~\\ref{tab:modlog}. A retry marked \\emph{not yet run} belongs to a "
                 "change that is in place and whose next attempt has not finished.")
    return modlog_table(own, cap_own, "tab:modlog") + "\n" + modlog_table(other, cap_other, "tab:modlogother")


# Width of each column as a fraction of the text width, and the characters of \\scriptsize that fit
# on one line of the narrowest text width the paper is set in (the JAIR version), to split the log
# into tables that each fit on a page.
COLS = (0.15, 0.03, 0.09, 0.415, 0.19, 0.06)
CHARS = 118
LINES = 70


def row_lines(cells):
    return max(math.ceil(len(re.sub(r"\\[a-zA-Z]+|[{}$]", "", c)) / max(1, int(w * CHARS) - 2))
               for c, w in zip(cells, COLS))


def split_rows(runs, budget):
    parts, cur, used = [], [], 0
    for run in runs:
        title = tex(run.get("title", run["run"]))
        head = f"\\multicolumn{{6}}{{@{{}}l}}{{\\emph{{{title}}}}} \\\\"
        first = True
        for r in run["records"]:
            c = r.get("change")
            if not c:
                continue
            retry = r.get("retry") or ("not yet built" if run["run"] in OWN else "not yet run")
            cells = [tex(r["target"]), str(r["attempt"]), tex(r["diagnosis"]),
                     f"{tex(c['kind'])}: {tex(c['old'])} $\\to$ {tex(c['new'])}", tex(c["improves"]), retry]
            n = row_lines(cells) + (1 if first or not cur else 0)
            if cur and used + n > budget:
                parts.append(cur)
                cur, used = [], 0
                n = row_lines(cells) + 1
            if first or not cur:
                cur.append(head if first else head.replace("}} \\\\", ", continued}} \\\\"))
            cur.append(" & ".join("\\rr " + x for x in cells) + " \\\\")
            used += n
            first = False
    if cur:
        parts.append(cur)
    return parts


def modlog_table(runs, caption, label):
    # as few tables as fit on a page each, then the rows spread evenly over them
    k = len(split_rows(runs, LINES))
    budget = 1
    while len(split_rows(runs, budget)) > k:
        budget += 1
    parts = split_rows(runs, budget)
    out = []
    for k, body in enumerate(parts):
        cap = caption if k == 0 else f"Table~\\ref{{{label}}}, continued."
        lab = label if k == 0 else f"{label}-{k + 1}"
        head = r"""% generated by figures/src/make_tables_round7.py; do not edit
\begin{table*}[t]
\caption{CAPTION}
\label{LABEL}
\centering
\scriptsize
\setlength{\tabcolsep}{3pt}
\begin{tabular}{@{}p{0.15\textwidth}p{0.03\textwidth}p{0.09\textwidth}p{0.415\textwidth}p{0.19\textwidth}p{0.06\textwidth}@{}}
\toprule
\rr Target & \rr Try & \rr Diagnosis & \rr Rule changed: old $\to$ new & \rr Meant to improve & \rr Retry \\
\midrule
"""
        head = head.replace("CAPTION", cap).replace("LABEL", lab)
        out.append(head + "\n".join(body) + "\n\\bottomrule\n\\end{tabular}\n\\end{table*}\n")
    return "\n".join(out)


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
