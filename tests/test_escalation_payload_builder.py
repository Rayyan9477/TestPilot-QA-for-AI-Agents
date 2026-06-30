"""TDD — escalation_payload_builder: Branch C (behavioral root-cause) + Branch B (quarantine).
Pure string/dict builders so the human-gate text is deterministic and reproducible on camera.
The never-auto-fix policy line is load-bearing; a behavioral case can never be quarantined.
"""
import pytest

from testpilot.models import Category, EvalResult, EvaluatorType
from testpilot.triage_classifier import classify
from testpilot.escalation_payload_builder import build_quarantine_note, build_regression_summary


def _regr_eval():
    return EvalResult(
        case_id="regr-01", evaluator_type=EvaluatorType.LLM_JUDGE_FAITHFULNESS,
        evaluator_name="Faithfulness", score=41, passed_on_retry=False, retry_count=3,
        expected="Cited policy LCD-12345", actual="Answered without citing policy",
        trajectory_diff="step 3: expected lookup_policy, got summarize",
    )


def _flaky_eval():
    return EvalResult(case_id="flaky-01", evaluator_type=EvaluatorType.SEMANTIC_SIMILARITY,
                      evaluator_name="Semantic similarity", score=88, passed_on_retry=True, retry_count=2)


def test_regression_summary_states_never_autofix_policy():
    ev = _regr_eval()
    s = build_regression_summary(classify(ev), ev)
    assert "product decision, not a bug fix" in s.body_markdown


def test_regression_summary_quotes_dropped_score_and_evaluator():
    ev = _regr_eval()
    s = build_regression_summary(classify(ev), ev)
    assert "41" in s.body_markdown and "Faithfulness" in s.body_markdown


def test_regression_summary_includes_trajectory_and_bounded_slack():
    ev = _regr_eval()
    s = build_regression_summary(classify(ev), ev)
    assert "step 3" in s.body_markdown
    assert 0 < len(s.slack_text) <= 4000


def test_regression_summary_rejects_non_behavioral():
    ev = EvalResult(case_id="d", evaluator_type=EvaluatorType.DETERMINISTIC_EXACT,
                    evaluator_name="Exact match", score=0, actual="x")
    with pytest.raises(ValueError):
        build_regression_summary(classify(ev), ev)


def test_quarantine_note_sets_retry_policy():
    note = build_quarantine_note(classify(_flaky_eval()))
    assert note.action == "quarantine"
    assert note.retry_policy["max_retries"] >= 1


def test_quarantine_refuses_behavioral_case():
    # a real regression must never be silently quarantined
    with pytest.raises(ValueError):
        build_quarantine_note(classify(_regr_eval()))
