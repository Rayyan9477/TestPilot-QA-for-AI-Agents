"""TDD — eval_result_parser: decouple the brittle external JSON/XML shapes from the typed
models so format drift can never silently mis-route a case. (SYSTEM-DESIGN §14.3)
"""
import json
from pathlib import Path

import pytest

from testpilot.models import EvaluatorType, JUnitReport
from testpilot.eval_result_parser import ParseError, is_green, parse_eval_results, parse_junit

FIX = Path(__file__).parent / "fixtures"


# --- parse_eval_results --------------------------------------------------------------

def test_parse_seed_all_yields_three_cases_in_order():
    cases = parse_eval_results((FIX / "seed_all.json").read_text())
    assert [c.case_id for c in cases] == ["drift-01", "flaky-01", "regr-01"]
    assert cases[0].evaluator_type is EvaluatorType.DETERMINISTIC_EXACT


def test_parse_accepts_already_parsed_list():
    raw = json.loads((FIX / "seed_drift.json").read_text())
    cases = parse_eval_results(raw)
    assert len(cases) == 1 and cases[0].case_id == "drift-01"


def test_parse_derives_type_from_name_when_type_absent():
    cases = parse_eval_results([{"case_id": "x", "evaluator_name": "Exact match", "score": 0}])
    assert cases[0].evaluator_type is EvaluatorType.DETERMINISTIC_EXACT


def test_parse_trusts_explicit_type_over_name():
    cases = parse_eval_results(
        [{"case_id": "x", "evaluator_type": "trajectory", "evaluator_name": "Exact match", "score": 0}]
    )
    assert cases[0].evaluator_type is EvaluatorType.TRAJECTORY


def test_parse_unknown_name_without_type_raises():
    with pytest.raises(ParseError):
        parse_eval_results([{"case_id": "x", "evaluator_name": "Mystery", "score": 0}])


def test_parse_malformed_json_raises():
    with pytest.raises(ParseError):
        parse_eval_results("{not json")


def test_parse_non_array_raises():
    # an object, not an array — never silently treat as zero failures
    with pytest.raises(ParseError):
        parse_eval_results('{"case_id": "x"}')


# --- parse_junit / is_green ----------------------------------------------------------

def test_parse_junit_red_is_not_green():
    r = parse_junit((FIX / "junit_red.xml").read_text())
    assert r.failures == 1
    assert is_green(r) is False


def test_parse_junit_green_is_green():
    r = parse_junit((FIX / "junit_green.xml").read_text())
    assert is_green(r) is True
    assert r.cases[0]["passed"] is True


def test_parse_junit_counts_error_as_failure():
    xml = ('<testsuites tests="1" failures="0"><testsuite>'
           '<testcase name="t"><error message="boom"/></testcase></testsuite></testsuites>')
    assert is_green(parse_junit(xml)) is False


def test_parse_junit_accepts_single_testsuite_root():
    r = parse_junit('<testsuite name="s" tests="1"><testcase name="t"/></testsuite>')
    assert r.tests == 1 and is_green(r) is True


def test_parse_junit_missing_testsuite_raises():
    with pytest.raises(ParseError):
        parse_junit("<root/>")


def test_parse_junit_malformed_xml_raises():
    with pytest.raises(ParseError):
        parse_junit("<not closed")


def test_is_green_false_for_empty_suite():
    assert is_green(JUnitReport(tests=0, failures=0, cases=[])) is False


def test_parse_list_with_non_dict_item_raises():
    with pytest.raises(ParseError):
        parse_eval_results([123])


def test_parse_case_with_invalid_field_raises():
    # valid dict + valid evaluator, but a field that fails model validation (score > 100)
    with pytest.raises(ParseError):
        parse_eval_results([{"case_id": "x", "evaluator_type": "trajectory", "evaluator_name": "T", "score": 999}])
