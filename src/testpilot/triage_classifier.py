"""The wedge: classify a failing agent-eval case by evaluator class, and pick the build's
primary_category by severity priority so a behavioral regression can never be auto-healed.
"""
from __future__ import annotations

from .models import Category, Classification, EvalResult, EvaluatorType

_MECHANICAL = {EvaluatorType.DETERMINISTIC_EXACT, EvaluatorType.JSON_SIMILARITY}
_BEHAVIORAL_CLASS = {
    EvaluatorType.SEMANTIC_SIMILARITY,
    EvaluatorType.LLM_JUDGE_FAITHFULNESS,
    EvaluatorType.TRAJECTORY,
}

# Higher = more severe. The release gate: any behavioral regression dominates the build.
_SEVERITY = {
    Category.BEHAVIORAL_REGRESSION: 3,
    Category.MECHANICAL_DRIFT: 2,
    Category.FLAKY: 1,
}


def classify(eval_result: EvalResult) -> Classification:
    """Map one failing eval case to exactly one Category. Deterministic and total:
    an unrecognised evaluator raises rather than risk silently routing it to auto-fix."""
    et = eval_result.evaluator_type

    if et in _MECHANICAL:
        return Classification(
            case_id=eval_result.case_id,
            category=Category.MECHANICAL_DRIFT,
            reason=f"{et.value} evaluator failed (score {eval_result.score}) — selector/output-schema drift",
            confidence=1.0,
        )

    if et in _BEHAVIORAL_CLASS:
        if eval_result.passed_on_retry:
            return Classification(
                case_id=eval_result.case_id,
                category=Category.FLAKY,
                reason=f"{et.value} passed on retry ({eval_result.retry_count}x) — non-deterministic flake",
                confidence=1.0,
            )
        if et is EvaluatorType.TRAJECTORY:
            reason = (
                f"trajectory evaluator diverged (score {eval_result.score}) — "
                "behavioral regression; never auto-fixed"
            )
        else:
            reason = (
                f"{et.value} failed consistently (score {eval_result.score}) — "
                "behavioral regression; never auto-fixed"
            )
        return Classification(
            case_id=eval_result.case_id,
            category=Category.BEHAVIORAL_REGRESSION,
            reason=reason,
            confidence=1.0,
        )

    raise ValueError(f"unhandled evaluator type: {et!r} — refusing to classify (fail loud)")


def select_primary_category(classifications: list[Classification]) -> Category:
    """The build's routing verdict: the most severe category present.
    BEHAVIORAL_REGRESSION > MECHANICAL_DRIFT > FLAKY."""
    if not classifications:
        raise ValueError("no classifications to select a primary category from")
    return max((c.category for c in classifications), key=lambda cat: _SEVERITY[cat])
