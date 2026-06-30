"""TDD — pipeline.route_failures: the offline composition that mirrors the Maestro routing
(triage -> per-case branch action). This is a local dev/demo harness; production routing is
the Maestro BPMN process. It proves the whole flow runs end-to-end with no cloud/network.
"""
from pathlib import Path

from testpilot.llm import FakeLLM
from testpilot.pipeline import route_failures

FIX = Path(__file__).parent / "fixtures"
SAMPLE = FIX / "sample_repo"


def _corrected():
    line = next(l for l in (SAMPLE / "UiTests" / "CheckoutTest.cs").read_text().splitlines() if "btn-signin" in l)
    return line.replace("btn-signin", "btn-login")


def test_routes_all_three_branches_with_build_verdict():
    res = route_failures((FIX / "seed_all.json").read_text(), SAMPLE, FakeLLM(_corrected()))
    by_id = {a.case_id: a for a in res.actions}
    assert len(res.actions) == 3
    assert by_id["drift-01"].action == "auto_heal"
    assert "btn-login" in by_id["drift-01"].detail["unified_diff"]
    assert by_id["flaky-01"].action == "quarantine"
    assert by_id["regr-01"].action == "escalate"
    assert "product decision, not a bug fix" in by_id["regr-01"].detail["body_markdown"]
    # any behavioral regression dominates the build verdict
    assert res.primary_category == "BEHAVIORAL_REGRESSION"


def test_drift_only_seed_heals_and_verdict_is_mechanical():
    res = route_failures((FIX / "seed_drift.json").read_text(), SAMPLE, FakeLLM(_corrected()))
    assert res.primary_category == "MECHANICAL_DRIFT"
    assert [a.action for a in res.actions] == ["auto_heal"]


def test_regr_only_seed_never_heals():
    res = route_failures((FIX / "seed_regr.json").read_text(), SAMPLE, FakeLLM("unused"))
    assert res.primary_category == "BEHAVIORAL_REGRESSION"
    assert res.actions[0].action == "escalate"  # never auto_heal
