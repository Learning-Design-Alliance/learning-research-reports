"""Derive mohler_en.csv, the file every Mohler mode reads, from the published parquet.

Reads the `cleaned` open-ended split (sentence ends marked `<STOP>`, which the harness loader strips) of nkazi/MohlerASAG (CC BY 4.0; registry id `mohler-asag`):
    python3 analyses/mohler_to_csv.py $MOHLER_DIR/cleaned-oe-00001.parquet $MOHLER_DIR/mohler_en.csv
Columns and row order are the parquet's; scores are written as Python floats ("3.0", "7.5").
"""
import csv, sys
import pyarrow.parquet as pq

src, out = sys.argv[1], sys.argv[2]
t = pq.read_table(src).to_pylist()
cols = ["id", "question", "instructor_answer", "student_answer", "score_grader_1", "score_grader_2", "score_avg"]
with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(cols)
    for r in t:
        w.writerow([r[c] for c in cols])
