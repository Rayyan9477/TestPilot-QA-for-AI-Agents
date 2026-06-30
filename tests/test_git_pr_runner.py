"""TDD — git_pr_runner: apply a validated one-line fix to a branch and build the Test-Manager
re-run command. subprocess is injected (FakeCmdRunner) so tests need no git/network.

The runtime heal commit is attributed to TestPilot (LLM Gateway) — deliberately NOT
'Co-Authored-By: Claude', which is reserved for the build-time coding-agent bonus (§14.7).
The re-run secret is an env reference, never a literal (§14.6).
"""
import shutil
import sys
from pathlib import Path

import pytest

from testpilot.models import CommitResult, FixProposal
from testpilot.git_pr_runner import (
    GitPrError,
    SubprocessCmdRunner,
    apply_and_branch,
    build_pr_cmd,
    build_rerun_cmd,
)

FIX = Path(__file__).parent / "fixtures"
REL = "UiTests/CheckoutTest.cs"


class FakeCmdRunner:
    def __init__(self, sha="a" * 40):
        self.calls: list[list[str]] = []
        self._sha = sha

    def run(self, argv, cwd=None):
        self.calls.append(list(argv))
        return self._sha + "\n" if "rev-parse" in argv else ""


def _proposal(*, old=None):
    cs = (FIX / "sample_repo" / REL).read_text(encoding="utf-8")
    real = next(l for l in cs.splitlines() if "btn-signin" in l)
    old_line = old if old is not None else real
    new_line = real.replace("btn-signin", "btn-login")
    return FixProposal(file_path=REL, old_line=old_line, new_line=new_line,
                       unified_diff=f"--- a/{REL}\n+++ b/{REL}\n-{old_line}\n+{new_line}")


def _tmp_repo(tmp_path):
    dst = tmp_path / "repo"
    shutil.copytree(FIX / "sample_repo", dst)
    return dst


# --- apply_and_branch ----------------------------------------------------------------

def test_apply_changes_exactly_one_line(tmp_path):
    repo = _tmp_repo(tmp_path)
    target = repo / REL
    before = target.read_text(encoding="utf-8").splitlines()
    apply_and_branch(_proposal(), repo, "fix/drift-01", FakeCmdRunner())
    after = target.read_text(encoding="utf-8").splitlines()
    changed = [(a, b) for a, b in zip(before, after) if a != b]
    assert len(before) == len(after)
    assert len(changed) == 1
    assert "btn-login" in changed[0][1] and "btn-signin" not in changed[0][1]


def test_checkout_uses_the_given_branch(tmp_path):
    repo, runner = _tmp_repo(tmp_path), FakeCmdRunner()
    apply_and_branch(_proposal(), repo, "fix/drift-01", runner)
    checkout = [c for c in runner.calls if c[:3] == ["git", "checkout", "-b"]]
    assert checkout and checkout[0][3] == "fix/drift-01"


def test_commit_message_marks_testpilot_heal_not_claude(tmp_path):
    repo, runner = _tmp_repo(tmp_path), FakeCmdRunner()
    apply_and_branch(_proposal(), repo, "fix/drift-01", runner)
    commit = next(c for c in runner.calls if c[:2] == ["git", "commit"])
    msg = commit[commit.index("-m") + 1]
    assert "TestPilot" in msg and "CheckoutTest.cs" in msg
    assert "Co-Authored-By: Claude" not in msg  # bonus lane stays separate


def test_returns_commit_result(tmp_path):
    repo = _tmp_repo(tmp_path)
    res = apply_and_branch(_proposal(), repo, "fix/drift-01", FakeCmdRunner(sha="b" * 40))
    assert isinstance(res, CommitResult)
    assert res.branch == "fix/drift-01"
    assert res.sha == "b" * 40
    assert res.files_changed == [REL]


def test_apply_raises_when_old_line_absent(tmp_path):
    repo = _tmp_repo(tmp_path)
    with pytest.raises(GitPrError):
        apply_and_branch(_proposal(old="THIS LINE IS NOT IN THE FILE"), repo, "fix/x", FakeCmdRunner())


# --- build_rerun_cmd -----------------------------------------------------------------

def _cmd():
    return build_rerun_cmd(
        orch_url="https://cloud.uipath.com/org/tenant/orchestrator_", tenant="DefaultTenant",
        project_key="PK1", testset_key="TS1", params_file="./params.json",
        account="myorg", client_id="cid-123", folder="Shared", result_path="./out",
    )


def test_rerun_cmd_has_required_flag_set():
    argv = _cmd()
    for flag in ["--projectKey", "--testsetkey", "-i", "-A", "-I", "--applicationScope", "--out", "--result_path"]:
        assert flag in argv, f"missing {flag}"
    assert argv[argv.index("--out") + 1] == "junit"
    scopes = argv[argv.index("--applicationScope") + 1]
    for s in ["OR.Folders", "OR.Execution", "TM.Projects", "TM.TestSets", "TM.TestExecutions"]:
        assert s in scopes


def test_rerun_cmd_references_secret_via_env_never_literal():
    argv = _cmd()
    # The function takes no secret parameter, so a secret literal cannot appear; the
    # ClientSecret is supplied at runtime via this env reference.
    assert "$UIPATH_CLIENT_SECRET" in argv
    assert argv[argv.index("-S") + 1] == "$UIPATH_CLIENT_SECRET"


# --- build_pr_cmd (the Branch-A `gh pr create` step) ---------------------------------

def test_build_pr_cmd_structure():
    argv = build_pr_cmd(_proposal(), repo="owner/repo", branch="fix/drift-01")
    assert argv[:3] == ["gh", "pr", "create"]
    assert argv[argv.index("--head") + 1] == "fix/drift-01"
    assert argv[argv.index("--base") + 1] == "main"
    assert argv[argv.index("--repo") + 1] == "owner/repo"


def test_build_pr_cmd_title_and_body_carry_the_fix():
    argv = build_pr_cmd(_proposal(), repo="o/r", branch="fix/drift-01")
    title = argv[argv.index("--title") + 1]
    body = argv[argv.index("--body") + 1]
    assert "CheckoutTest.cs" in title
    assert "btn-login" in body  # the unified diff is embedded for human review


def test_build_pr_cmd_never_embeds_a_token():
    # gh authenticates via the GITHUB_TOKEN env var — never put a token on argv.
    argv = build_pr_cmd(_proposal(), repo="o/r", branch="b")
    assert all("ghp_" not in str(a) and "GITHUB_TOKEN" not in str(a) for a in argv)


def test_apply_raises_when_target_file_missing(tmp_path):
    repo = _tmp_repo(tmp_path)
    missing = FixProposal(file_path="UiTests/DoesNotExist.cs", old_line="a", new_line="b",
                          unified_diff="--- a\n+++ b\n-a\n+b")
    with pytest.raises(GitPrError):
        apply_and_branch(missing, repo, "fix/x", FakeCmdRunner())


def test_apply_raises_on_noop_proposal(tmp_path):
    repo = _tmp_repo(tmp_path)
    real = next(l for l in (FIX / "sample_repo" / REL).read_text().splitlines() if "btn-signin" in l)
    noop = FixProposal(file_path=REL, old_line=real, new_line=real,
                       unified_diff=f"--- a\n+++ b\n-{real}\n+{real}")
    with pytest.raises(GitPrError):
        apply_and_branch(noop, repo, "fix/x", FakeCmdRunner())


def test_subprocess_runner_executes_and_reports_failure():
    out = SubprocessCmdRunner().run([sys.executable, "-c", "print('hello-runner')"])
    assert "hello-runner" in out
    with pytest.raises(GitPrError):
        SubprocessCmdRunner().run([sys.executable, "-c", "import sys; sys.exit(3)"])
