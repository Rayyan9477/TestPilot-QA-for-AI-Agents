"""Branch C (behavioral root-cause) and Branch B (quarantine) payloads.

Pure builders so the human-gate text is deterministic and reproducible on camera. The
never-auto-fix policy line is load-bearing; a behavioral case can never be quarantined,
and a non-behavioral case can never produce a regression summary (SYSTEM-DESIGN §2/§14).
"""
from __future__ import annotations

from .models import Category, Classification, EvalResult, QuarantineNote, RootCauseSummary

_NEVER_AUTOFIX = "A behavioral change in an agent is a product decision, not a bug fix"


def build_regression_summary(
    case: Classification, eval_result: EvalResult, trajectory_diff: str | None = None
) -> RootCauseSummary:
    if case.category is not Category.BEHAVIORAL_REGRESSION:
        raise ValueError(f"regression summary is only for behavioral regressions, got {case.category.value}")

    trajectory = trajectory_diff or eval_result.trajectory_diff
    title = f"Behavioral regression in case {case.case_id} ({eval_result.evaluator_name})"

    lines = [
        f"**{title}**",
        "",
        f"{_NEVER_AUTOFIX} - only a human merges behavior.",
        "",
        f"- Evaluator: {eval_result.evaluator_name} ({eval_result.evaluator_type.value})",
        f"- Score dropped to {eval_result.score}.",
    ]
    if eval_result.expected is not None or eval_result.actual is not None:
        lines.append(f"- Expected: {eval_result.expected!r}")
        lines.append(f"- Actual:   {eval_result.actual!r}")
    if trajectory:
        lines.append(f"- Trajectory: {trajectory}")
    body = "\n".join(lines)

    slack = f"{title} - {_NEVER_AUTOFIX}. Score {eval_result.score}."
    if trajectory:
        slack += f" {trajectory}"
    return RootCauseSummary(title=title, body_markdown=body, slack_text=slack[:4000])


def build_quarantine_note(case: Classification) -> QuarantineNote:
    if case.category is not Category.FLAKY:
        raise ValueError(
            f"quarantine is only for flaky cases, got {case.category.value} - "
            "a real regression must never be silently quarantined"
        )
    return QuarantineNote(
        case_id=case.case_id,
        action="quarantine",
        retry_policy={"max_retries": 2, "backoff": "exponential"},
    )
