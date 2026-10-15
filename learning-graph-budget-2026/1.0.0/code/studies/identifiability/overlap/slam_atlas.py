"""The positivity atlas on Duolingo SLAM 2018: three courses, two grains, through atlas.audit() itself.

SLAM is the Duolingo release that the half-life one is not. atlas-duolingo.json read REVIEW order --
0 of 12,854,226 rows were first exposures -- and decided nothing. SLAM opens at each learner's first
session and runs 30 days, so the order in which a learner MET a word or construction is observed and
the estimand matches atlas.json's. It is written to its own file anyway, because the unit is a design
choice here rather than the corpus's own taxonomy, and two grains are reported side by side:

    construct  UD part of speech + morphological bundle -- nearer a grammar skill, 204-358 units
    word       lowercased token -- 2,093-2,866 units

A token is "passed" when the learner did not mark it wrong. Each course is its own row, since the three
courses share no learners and teach different languages.

CC BY-NC 4.0, Harvard Dataverse doi:10.7910/DVN/8SWHNO. Raw files stay in the scratchpad; only
out/atlas-slam.json is committed.

    SLAM_DIR=<dir with *.slam.20190204.*> python3 slam_atlas.py     (unset: the registry default)
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from atlas import audit  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from shared.corpus import Slam  # noqa: E402
from shared.paths import data_path  # noqa: E402

HERE = Path(__file__).resolve().parent
COURSES = ("en_es", "es_en", "fr_en")
GRAINS = ("construct", "word")


def main() -> None:
    # $SLAM_DIR: the directory holding the extracted *.slam.20190204.* files
    root = str(data_path("SLAM_DIR"))
    rows = []
    print("POSITIVITY ATLAS ON DUOLINGO SLAM 2018 -- first 30 days, learning order observed\n")
    for course in COURSES:
        for grain in GRAINS:
            c = Slam(root, course, grain)
            r = audit(f"slam-{course}-{grain}",
                      ((u, unit, o >= 0.5, t, False, False) for u, unit, t, o in c.events()), 20000)
            r.update(course=course, grain=grain, licence=c.licence)
            rows.append(r)
            if "skipped" in r:
                print(f"  {course} {grain:9s} skipped: {r['skipped']}")
                continue
            print(f"  {course} {grain:9s} {r['learners']:>5} learners {r['items']:>5} units  "
                  f"readable {100 * r['readable_frac']:5.1f}%  MDE {r['mde_median'] or float('nan'):.3f}  "
                  f"med.cell {r['median_identifying']:>4.0f}  supp {r['supported']:>4}  "
                  f"contra {r['contradicted']:>3} (-{r.get('downgraded_unfalsifiable', 0)} unfals)  "
                  f"decided {100 * r['decided_frac']:5.2f}%  background {r['drop_median'] or 0:+.3f}",
                  flush=True)
    out = HERE / "out" / "atlas-slam.json"
    out.write_text(json.dumps({"estimand": "learning order, first 30 days per learner",
                               "rows": rows}, indent=1))
    print(f"\n  -> {out.relative_to(HERE)}")


if __name__ == "__main__":
    main()
