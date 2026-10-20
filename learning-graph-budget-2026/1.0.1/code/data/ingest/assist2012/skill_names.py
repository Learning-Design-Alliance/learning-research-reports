"""Write assist_skill_names.csv: one row per ASSISTments 2012-13 skill, `skill_id,skill name`, no header.

Three readers use it (studies/measurement/assist2012-direction/direction.py,
studies/measurement/residual-structure/residuals.py, studies/identifiability/core-vs-culture/invariance.py
and its human_codes.py). It had no committed generator until 2026-10-07; this rebuilds it from the
export by streaming the `skill_id` and `skill` columns, keeping the first non-empty name seen for each
id, sorted by numeric id. Rows with no skill id are skipped.

    python3 data/ingest/assist2012/skill_names.py $ASSIST_DIR/assist2012.zip $ASSIST_DIR/assist_skill_names.csv

ASSISTments terms: analysis only, no redistribution; the file stays outside the repository.
"""
import csv
import io
import sys
import zipfile


def main() -> None:
    src, dst = sys.argv[1], sys.argv[2]
    csv.field_size_limit(10_000_000)
    names: dict[str, str] = {}
    with zipfile.ZipFile(src) as z:
        (member,) = z.namelist()
        with z.open(member) as raw:
            for row in csv.DictReader(io.TextIOWrapper(raw, encoding="utf-8", errors="replace", newline="")):
                sid, name = (row.get("skill_id") or "").strip(), (row.get("skill") or "").strip()
                if sid and name and sid not in names:
                    names[sid] = name
    with open(dst, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        for sid in sorted(names, key=lambda s: (not s.isdigit(), int(s) if s.isdigit() else 0, s)):
            w.writerow([sid, names[sid]])
    print(f"{dst}: {len(names):,} skills")


if __name__ == "__main__":
    main()
