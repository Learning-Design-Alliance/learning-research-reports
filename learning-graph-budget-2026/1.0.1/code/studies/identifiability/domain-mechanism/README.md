# Does the short-lived part of the prerequisite drop differ by domain?

Pre-registered in `domains.py` (commit 3ae985d), before any real corpus was read. The floor passed
(`out/floor.json`). Output: `out/domains.json`. Run 2026-09-25. This answers Paper 1 §6.4 question 2
as far as the corpora in hand allow.

**Short answer.** The drop shrinks with lag in 12 of 13 domains, and in the thirteenth it is
unresolved. No corpus shows domains differing by the pre-registered 0.03, and none is tight enough
to call invariant. The programme verdict is **MIXED**: every corpus reads UNRESOLVED.

## Per domain (D = drop 7+ days after A minus drop within a day; negative = decays)

| corpus | domain | items | pairs readable in both bands | early | late | D [95% CI] | verdict |
| --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| XES3G5M | geometry | 61 | 261 | +0.159 | +0.103 | −0.056 [−0.081, −0.032] | DECAYS |
| | word problems | 146 | 159 | +0.184 | +0.116 | −0.069 [−0.094, −0.043] | DECAYS |
| | number theory | 38 | 56 | +0.110 | +0.076 | −0.034 [−0.061, −0.004] | DECAYS |
| | combinatorics | 98 | 51 | +0.197 | +0.136 | −0.061 [−0.109, −0.011] | DECAYS |
| | travel | 23 | 48 | +0.154 | +0.129 | −0.025 [−0.114, +0.043] | UNRESOLVED |
| | counting | 71 | 197 | +0.149 | +0.086 | −0.063 [−0.090, −0.038] | DECAYS |
| | computation | 125 | 107 | +0.173 | +0.116 | −0.057 [−0.092, −0.021] | DECAYS |
| Eedi | Algebra | 73 | 1,957 | +0.182 | +0.139 | −0.043 [−0.051, −0.034] | DECAYS |
| | Data and Statistics | 34 | 784 | +0.148 | +0.125 | −0.023 [−0.035, −0.012] | DECAYS |
| | Geometry and Measure | 79 | 1,896 | +0.157 | +0.122 | −0.035 [−0.043, −0.025] | DECAYS |
| | Number | 77 | 2,252 | +0.166 | +0.118 | −0.048 [−0.055, −0.040] | DECAYS |
| EdNet | Listening | 58 | 971 | +0.067 | +0.039 | −0.028 [−0.049, −0.009] | DECAYS |
| | Reading | 82 | 2,520 | +0.067 | +0.048 | −0.019 [−0.028, −0.010] | DECAYS |

## Spread between domains

| corpus | spread R | null 97.5th | R 95% CI | verdict |
| --- | ---: | ---: | --- | --- |
| XES3G5M | 0.044 | 0.106 | [0.032, 0.129] | UNRESOLVED: well inside the null; too few pairs per module to bound it |
| Eedi | 0.025 | 0.021 | [0.012, 0.039] | UNRESOLVED: beats the null, but under the 0.03 bar |
| EdNet | 0.009 | 0.020 | [0.001, 0.031] | UNRESOLVED: inside the null; upper bound just over 0.03 |

## What it says

1. **Decay is not a property of one domain.** Every domain with enough pairs shows it, across
   seven kinds of competition maths, four school maths strands and both TOEIC sections. So the
   corpus-wide LAG-DEPENDENT verdict is not driven by one domain.
2. **How much it decays may vary a little, but not by much.** Eedi's strands differ by more than
   arbitrary item groups do (Number and Algebra decay about twice as much as Data and Statistics),
   but the gap is 0.025, under the pre-registered material bar. EdNet's two sections are close to
   level. XES3G5M cannot say either way.
3. **What this does not settle.** Domains differ in difficulty, pacing and learners, so even a larger
   spread would describe the estimand, not a mechanism. Load and conjunctive structure were out of
   scope (see `domains.py`), and a construction-heavy or procedural domain is still untested. Eedi's
   lags run between latest answers.

## Running it

```
python3 domains.py floor
python3 domains.py real [--corpora xes3g5m,eedi,ednet] [--out out/domains.json]
```

Raw exports stay in the scratchpad; only aggregates are committed.
