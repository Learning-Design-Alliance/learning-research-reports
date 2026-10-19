"""
Eedi NeurIPS 2020 (tasks 1-2) -> one slim TSV: user, question, correct, time, class, quiz.

    python3 data/ingest/eedi/slim.py <data.zip> <out.tsv>

Reads the answers straight from the zip; nothing is extracted. The task-1 answers are split three
ways by the challenge (train, public test, private test), all carrying IsCorrect, and all three are
read: a learner's timeline with the held-out answers removed has holes the challenge cut, not ones
the learner left. AnswerId is unique across the three, which is asserted.

PRIVACY: student_metadata_*.csv holds Gender, DateOfBirth and PremiumPupil (a disadvantage flag).
This script never opens it. None of the three is needed, and a column that is never loaded cannot
leak into a join.

Terms: confirmed with Eedi as research use (2026-09-24). No redistribution; the output stays in
the scratchpad and only aggregates are committed.
"""
from __future__ import annotations

import sys
import zipfile

import pandas as pd

ANSWERS = ["data/train_data/train_task_1_2.csv",
           "data/test_data/test_public_answers_task_1.csv",
           "data/test_data/test_private_answers_task_1.csv"]
META = "data/metadata/answer_metadata_task_1_2.csv"


def main() -> None:
    src, out = sys.argv[1], sys.argv[2]
    z = zipfile.ZipFile(src)
    cols = ["QuestionId", "UserId", "AnswerId", "IsCorrect"]
    parts = [pd.read_csv(z.open(n), usecols=cols, dtype="int64") for n in ANSWERS]
    for n, p in zip(ANSWERS, parts):
        print(f"  {n.rsplit('/', 1)[1]:36s} {len(p):>11,} answers")
    a = pd.concat(parts, ignore_index=True)
    assert a.AnswerId.is_unique, "AnswerId repeats across the task-1 splits"

    # AnswerId is written as a float ("11808339.0") in the metadata file and an int elsewhere
    m = pd.read_csv(z.open(META), usecols=["AnswerId", "DateAnswered", "GroupId", "QuizId"],
                    dtype={"AnswerId": "float64", "DateAnswered": "string",
                           "GroupId": "Int64", "QuizId": "Int64"})
    # 7 of 19,834,820 metadata rows carry no AnswerId at all; they cannot be joined to anything
    blank = int(m.AnswerId.isna().sum())
    m = m.dropna(subset=["AnswerId"])
    m["AnswerId"] = m.AnswerId.astype("int64")
    print(f"  {len(m):,} metadata rows ({blank} with a blank AnswerId, dropped)")
    a = a.merge(m, on="AnswerId", how="left", validate="one_to_one")
    missing = int(a.DateAnswered.isna().sum())
    print(f"  {len(a):,} answers, {a.UserId.nunique():,} learners, "
          f"{a.QuestionId.nunique():,} questions; {missing:,} without a timestamp (dropped)")
    a = a.dropna(subset=["DateAnswered"]).sort_values(["UserId", "DateAnswered", "AnswerId"])
    a[["UserId", "QuestionId", "IsCorrect", "DateAnswered", "GroupId", "QuizId"]].to_csv(
        out, sep="\t", index=False)
    print(f"  wrote {out}")


if __name__ == "__main__":
    main()
