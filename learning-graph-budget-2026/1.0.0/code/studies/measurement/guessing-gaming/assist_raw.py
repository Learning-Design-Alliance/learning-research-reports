"""Stream the ASSISTments 2012-13 export from its zip into compact per-problem-log columns.

Used by rapid.py, gaming.py and hint_rescore.py. Reads data_path("ASSIST_DIR") / "assist2012.zip"
(2012-2013-data-with-predictions-4-final.csv inside, about 3 GB) in chunks; nothing is extracted and
nothing is written. answer_text is never read. The `actions` field is parsed for the type and time
of each action only (start-relative milliseconds); the answer strings it also carries are discarded
in the parser and never stored.

Encodings read from the export's first rows (2026-09-27): first_action 0 = attempt, 1 = hint,
2 = scaffolding request; problem_type in {algebra, choose_1, choose_n, fill_in_1, open_response,
rank}; original 1 = main problem, 0 = scaffolding; answer_id is almost always empty.
"""

from __future__ import annotations

import hashlib
import re
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from shared.paths import data_path  # noqa: E402

MEMBER = "2012-2013-data-with-predictions-4-final.csv"
PTYPES = ["choose_1", "choose_n", "fill_in_1", "algebra", "rank", "open_response"]
TUTOR = ["tutor", "test", "pre_test", "post_test"]
IDS = ["problem_log_id", "problem_id", "user_id", "assignment_id", "template_id", "student_class_id",
       "teacher_id", "school_id"]
USE = IDS + ["skill_id", "start_time", "end_time", "problem_type", "original", "correct", "bottom_hint",
             "hint_count", "attempt_count", "ms_first_response", "first_action", "tutor_mode", "actions"]
ACT = re.compile(r"- - (hint|answer|scaffold)\s*\n\s*- (\d+)")


def h(u, mod: int, salt: str = "") -> int:
    return int(hashlib.sha256((salt + str(u)).encode()).hexdigest()[:8], 16) % mod


def parse_actions(s):
    """-> (answers, hints, ms of first answer, ms of first hint, ms of last hint, ms of last answer,
    answers before the last hint). Missing times are nan."""
    if not isinstance(s, str):
        return 0, 0, np.nan, np.nan, np.nan, np.nan, 0
    na = nh = before = 0
    fa = fh = lh = la = np.nan
    for kind, ms in ACT.findall(s):
        t = float(ms)
        if kind == "answer":
            na += 1
            la = t
            if na == 1:
                fa = t
        elif kind == "hint":
            nh += 1
            lh = t
            before = na
            if nh == 1:
                fh = t
    return na, nh, fa, fh, lh, la, before


def load(mod: int = 1, keep: int = 0, salt: str = "", dedupe: bool = True, chunksize: int = 250_000,
         with_skill_rows: bool = False, max_chunks: int | None = None) -> pd.DataFrame:
    """One row per problem log (dedupe) or per (log, skill) row as exported (with_skill_rows).
    mod/keep: keep learners with sha256(salt + user_id) % mod == keep."""
    z = zipfile.ZipFile(data_path("ASSIST_DIR") / "assist2012.zip")
    parts, seen_users = [], {}
    dt = {c: "float64" for c in IDS + ["skill_id", "correct", "bottom_hint", "hint_count", "attempt_count",
                                       "ms_first_response", "first_action", "original"]}
    dt.update({c: "object" for c in ("start_time", "end_time", "problem_type", "tutor_mode", "actions")})
    with z.open(MEMBER) as f:
        for i, ch in enumerate(pd.read_csv(f, usecols=USE, dtype=dt, chunksize=chunksize)):
            if mod > 1:
                us = ch.user_id.to_numpy()
                for u in pd.unique(us):
                    if u not in seen_users:
                        seen_users[u] = h(int(u), mod, salt) == keep
                ch = ch[[seen_users[u] for u in us]]
            acts = [parse_actions(s) for s in ch.actions.to_numpy()]
            A = np.array(acts, dtype=float).reshape(-1, 7)
            st = pd.to_datetime(ch.start_time, format="ISO8601", errors="coerce")
            en = pd.to_datetime(ch.end_time, format="ISO8601", errors="coerce")
            out = pd.DataFrame({c: ch[c].to_numpy() for c in IDS})
            out["problem_log_id"] = out.problem_log_id.fillna(-1).astype(np.int64)
            for c in IDS[1:]:
                out[c] = out[c].fillna(-1).astype(np.int32)
            out["skill_id"] = ch.skill_id.to_numpy(np.float32)
            secs = (st - pd.Timestamp("1970-01-01")).dt.total_seconds()
            out["ts"] = secs.fillna(-1).to_numpy().astype(np.int64)
            out["dur_s"] = ((en - st).dt.total_seconds()).to_numpy(np.float32)
            out["ptype"] = pd.Categorical(ch.problem_type, categories=PTYPES).codes.astype(np.int8)
            out["tutor"] = pd.Categorical(ch.tutor_mode, categories=TUTOR).codes.astype(np.int8)
            for c in ("original", "first_action"):
                out[c] = ch[c].fillna(-1).to_numpy().astype(np.int8)
            for c in ("correct", "bottom_hint", "ms_first_response"):
                out[c] = ch[c].to_numpy(np.float32)
            for c in ("hint_count", "attempt_count"):
                out[c] = ch[c].fillna(-1).to_numpy().astype(np.int32)
            for j, c in enumerate(("n_answer_act", "n_hint_act", "t_first_answer", "t_first_hint", "t_last_hint",
                                   "t_last_answer", "answers_before_last_hint")):
                out[c] = A[:, j].astype(np.float32)
            parts.append(out)
            if max_chunks and i + 1 >= max_chunks:
                break
            if (i + 1) % 4 == 0:
                print(f"   read {(i + 1) * chunksize:,} rows", flush=True)
    a = pd.concat(parts, ignore_index=True)
    del parts
    if dedupe and not with_skill_rows:
        a = a.drop_duplicates("problem_log_id").reset_index(drop=True)
    return a
