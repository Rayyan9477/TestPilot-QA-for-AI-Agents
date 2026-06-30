"""TDD — selector_fixer: the Branch-A heart. Locate the drifted token line, ask the
(injected) LLM for the corrected line, and emit a guaranteed one-line diff. Refuses to
open empty/garbage PRs. The LLM client is injected so tests run offline. (§6, §14.1/§14.4)
"""
from pathlib import Path

import pytest

from testpilot.models import EvalResult, EvaluatorType
from testpilot.llm import FakeLLM
from testpilot.selector_fixer import FixerError, draft_fix

FIX = Path(__file__).parent / "fixtures"
SAMPLE = FIX / "sample_repo"
CS = SAMPLE / "UiTests" / "CheckoutTest.cs"


def _drift_eval(actual="btn-signin", expected="btn-login"):
    return EvalResult(
        case_id="drift-01", evaluator_type=EvaluatorType.DETERMINISTIC_EXACT,
        evaluator_name="Exact match", score=0, expected=expected, actual=actual,
    )


def _original_drift_line():
    for line in CS.read_text(encoding="utf-8").splitlines():
        if "btn-signin" in line:
            return line
    raise AssertionError("fixture missing the drift line")


def _corrected_line():
    return _original_drift_line().replace("btn-signin", "btn-login")


def _one_line_diff(diff: str) -> bool:
    minus = [l for l in diff.splitlines() if l.startswith("-") and not l.startswith("---")]
    plus = [l for l in diff.splitlines() if l.startswith("+") and not l.startswith("+++")]
    return len(minus) == 1 and len(plus) == 1


def test_locates_and_corrects_the_drifted_line():
    fp = draft_fix(_drift_eval(), SAMPLE, FakeLLM(_corrected_line()))
    assert "btn-signin" in fp.old_line
    assert "btn-login" in fp.new_line
    assert fp.file_path.endswith("CheckoutTest.cs")


def test_diff_is_exactly_one_line():
    fp = draft_fix(_drift_eval(), SAMPLE, FakeLLM(_corrected_line()))
    assert _one_line_diff(fp.unified_diff)


def test_accepts_code_fenced_single_line():
    fp = draft_fix(_drift_eval(), SAMPLE, FakeLLM("```\n" + _corrected_line() + "\n```"))
    assert "btn-login" in fp.new_line


def test_rejects_multiline_output():
    with pytest.raises(FixerError):
        draft_fix(_drift_eval(), SAMPLE, FakeLLM("line one\nline two"))


def test_rejects_empty_output():
    with pytest.raises(FixerError):
        draft_fix(_drift_eval(), SAMPLE, FakeLLM(""))


def test_rejects_whitespace_only_output():
    with pytest.raises(FixerError):
        draft_fix(_drift_eval(), SAMPLE, FakeLLM("   \n  "))


def test_rejects_noop_output():
    with pytest.raises(FixerError):
        draft_fix(_drift_eval(), SAMPLE, FakeLLM(_original_drift_line()))


def test_token_absent_raises():
    with pytest.raises(FixerError):
        draft_fix(_drift_eval(actual="totally-not-present-xyz"), SAMPLE, FakeLLM("x"))


def test_no_actual_token_raises():
    ev = EvalResult(case_id="c", evaluator_type=EvaluatorType.DETERMINISTIC_EXACT,
                    evaluator_name="Exact match", score=0)
    with pytest.raises(FixerError):
        draft_fix(ev, SAMPLE, FakeLLM("x"))


def test_ambiguous_match_raises(tmp_path):
    (tmp_path / "a.cs").write_text('x = "dup-token";\n', encoding="utf-8")
    (tmp_path / "b.cs").write_text('y = "dup-token";\n', encoding="utf-8")
    ev = EvalResult(case_id="c", evaluator_type=EvaluatorType.DETERMINISTIC_EXACT,
                    evaluator_name="Exact match", score=0, expected="good", actual="dup-token")
    with pytest.raises(FixerError):
        draft_fix(ev, tmp_path, FakeLLM('z = "good";'))


def test_skips_unreadable_file_and_heals_the_readable_one(tmp_path):
    # a non-UTF-8 file must be skipped (not crash); the token is found in the good file
    (tmp_path / "bad.cs").write_bytes(b"\xff\xfe\x00\x01 btn-signin")
    (tmp_path / "good.cs").write_text('var x = "btn-signin";\n', encoding="utf-8")
    ev = EvalResult(case_id="c", evaluator_type=EvaluatorType.DETERMINISTIC_EXACT,
                    evaluator_name="Exact match", score=0, expected="btn-login", actual="btn-signin")
    fp = draft_fix(ev, tmp_path, FakeLLM('var x = "btn-login";'))
    assert fp.file_path == "good.cs" and "btn-login" in fp.new_line
