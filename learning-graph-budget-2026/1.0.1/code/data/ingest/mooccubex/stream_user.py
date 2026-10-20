"""Stream MOOCCubeX user.json and keep ONLY what a course-order study needs.

PRIVACY: user.json carries `name`, `gender`, `year_of_birth` and `school`. NONE of it is written.
This keeps the pseudonymous id (needed as a join key), the course sequence and the enrolment times,
and discards every demographic field at the door -- they are not needed for any question here, and
the way to not misuse an attribute is to not hold it.

Also drops learners with fewer than 2 enrolments (no order to read) and courses outside the set that
has concept membership, since a course with no concepts cannot be decomposed.
"""
import json, sys, time

keep_courses = set(open(sys.argv[1], encoding="utf-8").read().split())
out = open(sys.argv[2], "w", encoding="utf-8")
seen = kept = 0
t0 = time.time()
for line in sys.stdin:
    seen += 1
    line = line.strip().rstrip(",")
    if not line or line[0] != "{":
        continue
    try:
        d = json.loads(line)
    except Exception:
        continue
    order = d.get("course_order") or []
    times = d.get("enroll_time") or []
    # user.json stores course_order as BARE INTEGERS (682129) while concept-course.txt and
    # course.json use the C_-prefixed form (C_682129). The first run compared the two directly and
    # kept 0 of 3,330,294 users -- a silent join failure that looked like an empty result.
    pairs = [(f"C_{c}", t) for c, t in zip(order, times) if f"C_{c}" in keep_courses]
    if len(pairs) < 2:
        continue
    kept += 1
    out.write(json.dumps({"u": d.get("id"), "c": [p[0] for p in pairs],
                          "t": [p[1] for p in pairs]}, ensure_ascii=False) + "\n")
    if seen % 500000 == 0:
        print(f"  {seen:,} users seen, {kept:,} kept, {time.time()-t0:.0f}s", flush=True)
out.close()
print(f"DONE {seen:,} seen, {kept:,} kept ({100*kept/max(seen,1):.1f}%), {time.time()-t0:.0f}s",
      flush=True)
