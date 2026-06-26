"""TDD — triage_classifier: the wedge.

Classifies a failing agent-evaluation case by WHICH evaluator class failed, and selects
the build's primary_category by severity priority (BEHAVIORAL > MECHANICAL > FLAKY) so a
build containing a behavioral regression can never be routed to auto-heal.
"""
import pytest

from testpilot.models import EvalResult, EvaluatorType, Category
from testpilot.triage_classifier import classify, select_primary_category


def _eval(evaluator_type, *, score=0, passed_on_retry=False, retry_count=1, case_id="c1"):
    return EvalResult(
        case_id=case_id,
        evaluator_type=evaluator_type,
        evaluator_name="x",
        score=score,
        passed_on_retry=passed_on_retry,
        retry_count=retry_count,
    )


# --- classify: evaluator class -> category --------------------------------------------

def test_deterministic_exact_fail_is_mechanical():
    c = classify(_eval(EvaluatorType.DETERMINISTIC_EXACT, score=0))
    assert c.category is Category.MECHANICAL_DRIFT


def test_json_similarity_fail_is_mechanical():
    c = classify(_eval(EvaluatorType.JSON_SIMILARITY, score=62))
    assert c.category is Category.MECHANICAL_DRIFT


def test_semantic_passed_on_retry_is_flaky():
    c = classify(_eval(EvaluatorType.SEMANTIC_SIMILARITY, score=88, passed_on_retry=True, retry_count=2))
    assert c.category is Category.FLAKY


def test_llm_judge_consistent_fail_is_behavioral():
    c = classify(_eval(EvaluatorType.LLM_JUDGE_FAITHFULNESS, score=41, passed_on_retry=False, retry_count=3))
    assert c.category is Category.BEHAVIORAL_REGRESSION


def test_trajectory_divergence_is_behavioral():
    c = classify(_eval(EvaluatorType.TRAJECTORY, score=33))
    assert c.category is Category.BEHAVIORAL_REGRESSION
    assert "trajectory" in c.reason.lower()


def test_llm_judge_passed_on_retry_is_flaky_not_behavioral():
    # Guards the never-auto-fix-behavior rule against false positives: a behavioral-class
    # evaluator that recovers on retry is genuine flakiness, not a real regression.
    c = classify(_eval(EvaluatorType.LLM_JUDGE_FAITHFULNESS, score=90, passed_on_retry=True))
    assert c.category is Category.FLAKY


def test_deterministic_triage_confidence_is_one():
    c = classify(_eval(EvaluatorType.DETERMINISTIC_EXACT))
    assert c.confidence == 1.0


def test_unknown_evaluator_raises():
    # Defensive guard: a corrupted/future evaluator value must never be silently routed to
    # auto-fix. model_construct bypasses validation to simulate the corrupted input.
    bogus = EvalResult.model_construct(
        case_id="c1", evaluator_type="__bogus__", evaluator_name="x",
        score=0, passed_on_retry=False, retry_count=1,
    )
    with pytest.raises(ValueError):
        classify(bogus)


# --- select_primary_category: severity priority BEHAVIORAL > MECHANICAL > FLAKY -------

def _cls(category):
    sample = {
        Category.MECHANICAL_DRIFT: _eval(EvaluatorType.DETERMINISTIC_EXACT),
        Category.FLAKY: _eval(EvaluatorType.SEMANTIC_SIMILARITY, passed_on_retry=True),
        Category.BEHAVIORAL_REGRESSION: _eval(EvaluatorType.TRAJECTORY),
    }[category]
    return classify(sample)


def test_primary_behavioral_wins_over_mechanical_and_flaky():
    cats = [_cls(Category.MECHANICAL_DRIFT), _cls(Category.FLAKY), _cls(Category.BEHAVIORAL_REGRESSION)]
    assert select_primary_category(cats) is Category.BEHAVIORAL_REGRESSION


def test_primary_mechanical_over_flaky():
    cats = [_cls(Category.FLAKY), _cls(Category.MECHANICAL_DRIFT)]
    assert select_primary_category(cats) is Category.MECHANICAL_DRIFT


def test_primary_flaky_only():
    assert select_primary_category([_cls(Category.FLAKY)]) is Category.FLAKY


def test_primary_empty_raises():
    with pytest.raises(ValueError):
        select_primary_category([])
