"""A control has to be the size of the thing it controls for.

Twice in one study a control cut was built too small to do its job, and both times it passed
inspection because it was *semantically* right — it removed text that carried none of the construct,
which is the hard part — while being far too little text to rule out the confound it existed to
rule out.

    explanation-object pilot   control removed 147 characters; the treatments removed up to 971.
                               It showed that removing 147 characters is harmless and said nothing
                               about removing 971. Corrected mid-study with a 582-character version.

    explanation-object n=20    control removed 64 characters on average; the treatments removed 410
                               and 343 and 1358. Same mistake, three hours later, in the next
                               script, after the first one had been written up as a lesson.

Writing the lesson down did not prevent repeating it, so it is an assertion now rather than a habit.
The check is arithmetic and takes a second: compare the size of each control perturbation against
the size of the treatment perturbations it is meant to control for.

**`covers` is the part worth reading.** A single ratio hides the case this study actually had, where
one treatment (removing every Evidence span) was three times larger than anything available to
control it. That treatment is not controlled, whatever the median says, and a write-up that does not
admit it is overclaiming. So the report names uncovered treatments individually and the caller has
to say something about them.
"""

from __future__ import annotations

__all__ = ["ControlTooSmall", "check_control_scale"]

#: a control smaller than this fraction of the median treatment is not testing the confound
MIN_RATIO = 0.5


class ControlTooSmall(AssertionError):
    """Raised when a control perturbation is too small to rule out what it is there to rule out."""


def check_control_scale(sizes: dict[str, float], controls, *, min_ratio: float = MIN_RATIO,
                        strict: bool = True) -> dict:
    """Is each control big enough to stand in for the treatments?

    `sizes` maps every condition to the magnitude of its perturbation in whatever unit the study
    perturbs in — characters removed, items dropped, tokens added. `controls` names which of them
    are controls.

    Compared against the MEDIAN treatment rather than the largest, because requiring a control as
    big as the biggest treatment is often impossible: in `explanation-object` nothing but the
    evidence spans themselves ran to 1358 characters. The largest treatments are then reported as
    uncovered instead of quietly failing the whole check.
    """
    controls = set(controls)
    missing = controls - set(sizes)
    if missing:
        raise ControlTooSmall(f"no size recorded for control(s): {', '.join(sorted(missing))}")
    treat = {k: float(v) for k, v in sizes.items() if k not in controls}
    ctrl = {k: float(v) for k, v in sizes.items() if k in controls}
    if not treat or not ctrl:
        raise ControlTooSmall("need at least one treatment and one control to compare")

    ordered = sorted(treat.values())
    mid = len(ordered) // 2
    median = ordered[mid] if len(ordered) % 2 else (ordered[mid - 1] + ordered[mid]) / 2
    biggest = max(ctrl.values())

    ratios = {k: (v / median if median else float("inf")) for k, v in ctrl.items()}
    ok = any(r >= min_ratio for r in ratios.values())
    covers = {k: biggest >= min_ratio * v for k, v in treat.items()}
    uncovered = sorted(k for k, v in covers.items() if not v)

    lines = [f"control scale: median treatment {median:.0f}, "
             + ", ".join(f"{k} {ctrl[k]:.0f} ({ratios[k]:.2f}x)" for k in sorted(ctrl))]
    if uncovered:
        lines.append(f"   NOT COVERED by any control at {min_ratio:g}x: "
                     + ", ".join(f"{k} {treat[k]:.0f}" for k in uncovered)
                     + " -- say so in the write-up rather than implying otherwise")
    report = "\n".join(lines)

    if strict and not ok:
        raise ControlTooSmall(
            f"every control is under {min_ratio:g}x the median treatment perturbation "
            f"({median:.0f}). " + ", ".join(f"{k}={ctrl[k]:.0f}" for k in sorted(ctrl))
            + ". A control this small shows only that a small change is harmless and cannot rule "
              "out that a large one moves the instrument by size alone.")
    return dict(ok=ok, median_treatment=median, ratios=ratios, covers=covers,
                uncovered=uncovered, report=report)
