"""Long-term memory shared by every proposer: one indexed SQLite store on disk.

Every attack writes what it learned and reads what earlier rounds learned:

  nodes        the construction nodes of the library, with what they give and need;
  events       every crossing and its offspring, the check, the refuter's verdict and its reason
               (refuted and rejected offspring are kept: they are the negative data);
  parts        an index from each library node to the events whose composite contains it;
  weights      the booster synapses, carried from one round to the next;
  blocks       every failed step on a benchmark, with the assumption that blocks it;
  literature   every literature check (claim, source, identifier, verdict);
  retrievals   what was retrieved before each attack, so the influence of memory can be audited;
  modlog       every attempt of the learn-from-failure loop (selfmod): its outcome, the diagnosis of a
               failure, the rule it changed and the outcome of the retry.

Retrieval before an attack on a composite (a set of library nodes) scores past events by the Jaccard
similarity of their node sets, multiplied by the booster weight of the synapse that produced them,
and returns the best k with their outcomes and reasons.  A composite whose exact node sequence is
already decided is not checked again.

The store is compact (one row per event, parts kept as a space-separated string) and indexed on the
node sequence and on each node, so lookups stay logarithmic as rounds accumulate.
"""
from __future__ import annotations

import json
import os
import sqlite3
import time
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

SCHEMA = """
CREATE TABLE IF NOT EXISTS nodes(id TEXT PRIMARY KEY, problem TEXT, gives TEXT, needs TEXT, source TEXT);
CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY, round INTEGER, arm TEXT, proposer TEXT,
    seq TEXT, problem TEXT, outcome TEXT, node TEXT, statement TEXT, reason TEXT, survived INTEGER,
    weight REAL, t REAL);
CREATE INDEX IF NOT EXISTS events_seq ON events(seq);
CREATE TABLE IF NOT EXISTS parts(event INTEGER, part TEXT);
CREATE INDEX IF NOT EXISTS parts_part ON parts(part);
CREATE TABLE IF NOT EXISTS weights(key TEXT PRIMARY KEY, value REAL);
CREATE TABLE IF NOT EXISTS blocks(target TEXT, step TEXT, assumption TEXT, source TEXT,
    PRIMARY KEY(target, step));
CREATE TABLE IF NOT EXISTS literature(claim TEXT PRIMARY KEY, source TEXT, ident TEXT, verdict TEXT);
CREATE TABLE IF NOT EXISTS retrievals(round INTEGER, proposer TEXT, query TEXT, hits TEXT);
CREATE TABLE IF NOT EXISTS modlog(id INTEGER PRIMARY KEY, target TEXT, attempt INTEGER, rules_version INTEGER,
    outcome TEXT, diagnosis TEXT, rule TEXT, kind TEXT, record TEXT, t REAL);
CREATE INDEX IF NOT EXISTS modlog_target ON modlog(target);
"""


class Memory:
    def __init__(self, path: Optional[str] = None):
        self.path = path
        if path:
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        self.db = sqlite3.connect(path or ":memory:")
        self.db.executescript(SCHEMA)
        self._decided: Dict[str, Tuple[str, int]] = {
            s: (o, v) for s, o, v in self.db.execute("SELECT seq, outcome, survived FROM events")}

    # -- writing ------------------------------------------------------------------------------
    def add_nodes(self, cons: Iterable) -> None:
        self.db.executemany("INSERT OR REPLACE INTO nodes VALUES (?,?,?,?,?)",
                            [(c.id, c.problem, c.gives, " ".join(sorted(c.needs)), c.source) for c in cons])

    def record(self, parts: Sequence[str], problem: str, outcome: str, node: str = "", statement: str = "",
               reason: str = "", survived: Optional[bool] = None, weight: float = 1.0, round_: int = 0,
               arm: str = "", proposer: str = "") -> int:
        seq = " ".join(parts)
        cur = self.db.execute("INSERT INTO events(round, arm, proposer, seq, problem, outcome, node, statement, "
                              "reason, survived, weight, t) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                              (round_, arm, proposer, seq, problem, outcome, node, statement, reason,
                               None if survived is None else int(survived), weight, time.time()))
        eid = cur.lastrowid
        self.db.executemany("INSERT INTO parts VALUES (?,?)", [(eid, p) for p in set(parts)])
        self._decided[seq] = (outcome, None if survived is None else int(survived))
        return eid

    def block(self, target: str, step: str, assumption: str, source: str = "") -> None:
        self.db.execute("INSERT OR REPLACE INTO blocks VALUES (?,?,?,?)", (target, step, assumption, source))

    def cite(self, claim: str, source: str, ident: str, verdict: str) -> None:
        self.db.execute("INSERT OR REPLACE INTO literature VALUES (?,?,?,?)", (claim, source, ident, verdict))

    def record_attempt(self, rec: dict) -> int:
        """One record of the learn-from-failure loop (see selfmod.Record.as_dict)."""
        ch = rec.get("change") or {}
        cur = self.db.execute("INSERT INTO modlog(target, attempt, rules_version, outcome, diagnosis, rule, kind, "
                              "record, t) VALUES (?,?,?,?,?,?,?,?,?)",
                              (rec["target"], rec["attempt"], rec.get("rules_version", 0), rec["outcome"],
                               rec.get("diagnosis", ""), ch.get("rule", ""), ch.get("kind", ""),
                               json.dumps(rec, sort_keys=True), time.time()))
        return cur.lastrowid

    def attempts(self, target: Optional[str] = None) -> List[dict]:
        q = "SELECT record FROM modlog" + (" WHERE target = ?" if target else "") + " ORDER BY id"
        return [json.loads(r) for (r,) in self.db.execute(q, (target,) if target else ())]

    def save_weights(self, w: Dict[str, float]) -> None:
        self.db.execute("DELETE FROM weights")
        self.db.executemany("INSERT INTO weights VALUES (?,?)", list(w.items()))

    def commit(self) -> None:
        self.db.commit()

    # -- reading ------------------------------------------------------------------------------
    def weights(self) -> Dict[str, float]:
        return dict(self.db.execute("SELECT key, value FROM weights"))

    def decided(self, parts: Sequence[str]) -> Optional[Tuple[str, int]]:
        return self._decided.get(" ".join(parts))

    def retrieve(self, parts: Sequence[str], k: int = 5, round_: int = 0, proposer: str = "",
                 log: bool = True) -> List[dict]:
        q = set(parts)
        if not q:
            return []
        marks = ",".join("?" * len(q))
        rows = self.db.execute(
            f"SELECT DISTINCT e.id, e.seq, e.outcome, e.node, e.reason, e.survived, e.weight FROM events e "
            f"JOIN parts p ON p.event = e.id WHERE p.part IN ({marks}) ORDER BY e.id DESC LIMIT 400",
            tuple(q)).fetchall()
        best: Dict[str, dict] = {}
        for eid, seq, outcome, node, reason, surv, w in rows:
            s = set(seq.split())
            sim = len(q & s) / len(q | s)
            score = sim * (w or 1.0)
            if seq not in best or score > best[seq]["score"]:
                best[seq] = dict(seq=seq, outcome=outcome, node=node, reason=reason[:160],
                                 survived=surv, sim=round(sim, 3), score=round(score, 3))
        hits = sorted(best.values(), key=lambda h: -h["score"])[:k]
        if log:
            self.db.execute("INSERT INTO retrievals VALUES (?,?,?,?)",
                            (round_, proposer, " ".join(parts), json.dumps([h["seq"] for h in hits])))
        return hits

    def prior(self, parts: Sequence[str], k: int = 5, **kw) -> Tuple[float, List[dict]]:
        """Multiplier for the chance of attacking a composite: up with similarity to past survivors,
        down with similarity to refuted, rejected or stopped composites.  Range [0.25, 3]."""
        hits = self.retrieve(parts, k=k, **kw)
        if not hits:
            return 1.0, hits
        good = sum(h["sim"] for h in hits if h["survived"] == 1)
        bad = sum(h["sim"] for h in hits if h["survived"] != 1)
        return max(0.25, min(3.0, 1.0 + good - 0.5 * bad)), hits

    def stats(self) -> dict:
        one = lambda q: self.db.execute(q).fetchone()[0]
        out = dict(events=one("SELECT COUNT(*) FROM events"),
                   distinct_composites=one("SELECT COUNT(DISTINCT seq) FROM events"),
                   survivors=one("SELECT COUNT(DISTINCT seq) FROM events WHERE survived = 1"),
                   refuted=one("SELECT COUNT(DISTINCT seq) FROM events WHERE survived = 0"),
                   blocks=one("SELECT COUNT(*) FROM blocks"), literature=one("SELECT COUNT(*) FROM literature"),
                   retrievals=one("SELECT COUNT(*) FROM retrievals"), weights=one("SELECT COUNT(*) FROM weights"),
                   attempts=one("SELECT COUNT(*) FROM modlog"))
        if self.path and os.path.exists(self.path):
            out["bytes"] = os.path.getsize(self.path)
        return out

    def export(self) -> dict:
        """Everything in the store as plain data (for the paper's tables and the redraw script)."""
        tabs = {}
        for t in ("nodes", "blocks", "literature", "weights"):
            cur = self.db.execute(f"SELECT * FROM {t}")
            cols = [d[0] for d in cur.description]
            tabs[t] = [dict(zip(cols, r)) for r in cur]
        cur = self.db.execute("SELECT seq, problem, outcome, node, reason, survived, COUNT(*) FROM events "
                              "GROUP BY seq ORDER BY MIN(id)")
        tabs["composites"] = [dict(seq=s, problem=p, outcome=o, node=n, reason=r, survived=v, times=c)
                              for s, p, o, n, r, v, c in cur]
        return tabs
