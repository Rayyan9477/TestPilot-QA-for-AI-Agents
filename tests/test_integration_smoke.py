"""Integration smoke — the regression guard for the on-camera 3-branch story. Drives the
seeded failed-eval set through parser -> classifier -> the correct action per branch:
  A drift -> FixProposal (+ applied to a branch)   B flaky -> QuarantineNote   C regr -> RootCauseSummary
and confirms the build verdict is BEHAVIORAL (release blocked). Composes already-unit-tested
modules, so it stays green; it exists to catch a future break in the wiring (§14.4).
"""
import shutil
from pathlib import Path

from testpilot.eval_result_parser import is_green, parse_eval_results, parse_junit
from testpilot.escalation_payload_builder import build_quarantine_note, build_regression_summary
from testpilot.git_pr_runner import apply_and_branch
from testpilot.llm import FakeLLM
from testpilot.models import Category, FixProposal, QuarantineNote, RootCauseSummary
from testpilot.selector_fixer import draft_fix
from testpilot.triage_classifier import classify, select_primary_category

FIX = Path(__file__).parent / "fixtures"


class _FakeCmdRunner:
    def __init__(self, sha="e" * 40):
        self.calls = []
        self._sha = sha

    def run(self, argv, cwd=None):
        self.calls.append(list(argv))
        return self._sha + "\n" if "rev-parse" in argv else ""


def _seed():
    cases = parse_eval_results((FIX / "seed_all.json").read_text())
    return {c.case_id: c for c in cases}, {c.case_id: classify(c) for c in cases}


def test_three_branches_each_produce_their_payload(tmp_path):
    repo = tmp_path / "repo"
    shutil.copytree(FIX / "sample_repo", repo)
    evals, clss = _seed()

    # Branch A — mechanical drift -> a one-line FixProposal applied to a branch
    drift_line = next(l for l in (repo / "UiTests" / "CheckoutTest.cs").read_text().splitlines() if "btn-signin" in l)
    proposal = draft_fix(evals["drift-01"], repo, FakeLLM(drift_line.replace("btn-signin", "btn-login")))
    assert isinstance(proposal, FixProposal) and "btn-login" in proposal.new_line
    commit = apply_and_branch(proposal, repo, "fix/drift-01", _FakeCmdRunner())
    assert commit.branch == "fix/drift-01"

    # Branch B — flaky -> quarantine note
    note = build_quarantine_note(clss["flaky-01"])
    assert isinstance(note, QuarantineNote) and note.action == "quarantine"

    # Branch C — behavioral regression -> human root-cause summary (never auto-fixed)
    summary = build_regression_summary(clss["regr-01"], evals["regr-01"])
    assert isinstance(summary, RootCauseSummary)
    assert "product decision, not a bug fix" in summary.body_markdown

    # Build verdict — any behavioral regression blocks the release
    assert select_primary_category(list(clss.values())) is Category.BEHAVIORAL_REGRESSION


def test_applied_fix_heals_source_and_rerun_would_be_green(tmp_path):
    repo = tmp_path / "repo"
    shutil.copytree(FIX / "sample_repo", repo)
    evals, _ = _seed()
    cs = repo / "UiTests" / "CheckoutTest.cs"
    drift_line = next(l for l in cs.read_text().splitlines() if "btn-signin" in l)

    proposal = draft_fix(evals["drift-01"], repo, FakeLLM(drift_line.replace("btn-signin", "btn-login")))
    apply_and_branch(proposal, repo, "fix/drift-01", _FakeCmdRunner())

    healed = cs.read_text()
    assert "btn-signin" not in healed and "btn-login" in healed     # drift healed in source
    # The Test-Manager re-run flip is driven from fixtures (decoupled from live timing, §14.5)
    assert is_green(parse_junit((FIX / "junit_green.xml").read_text())) is True
    assert is_green(parse_junit((FIX / "junit_red.xml").read_text())) is False
