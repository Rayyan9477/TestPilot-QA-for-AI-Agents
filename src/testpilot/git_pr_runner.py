"""Apply a validated FixProposal to a branch and build the Test-Manager re-run command.

subprocess is injected behind CmdRunner so the unit tests run with no git/network. The
runtime heal commit is attributed to TestPilot (the fix was drafted via the UiPath LLM
Gateway) and is deliberately kept separate from the build-time Claude Code bonus (§14.7).
The re-run ClientSecret is referenced from the environment, never embedded in argv (§14.6).
"""
from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Protocol

from .models import CommitResult, FixProposal

_TM_SCOPES = "OR.Folders OR.Execution TM.Projects TM.TestSets TM.TestExecutions"


class GitPrError(Exception):
    """The runner refuses to apply/commit (target line missing, no-op, etc.)."""


class CmdRunner(Protocol):
    def run(self, argv: list[str], cwd: Path | None = None) -> str: ...


class SubprocessCmdRunner:
    """Real adapter used at runtime (thin I/O seam; unit tests inject a fake instead)."""

    def run(self, argv: list[str], cwd: Path | None = None) -> str:
        proc = subprocess.run(argv, cwd=cwd, capture_output=True, text=True)
        if proc.returncode != 0:
            raise GitPrError(f"command failed ({argv[:3]}...): {proc.stderr.strip()}")
        return proc.stdout


def _commit_message(proposal: FixProposal) -> str:
    return (
        f"fix(test): TestPilot auto-heal of drifted locator in {proposal.file_path}\n\n"
        "Mechanical drift repaired via the UiPath AI Trust Layer LLM Gateway.\n"
        f"- {proposal.old_line.strip()}\n"
        f"+ {proposal.new_line.strip()}\n"
    )


def apply_and_branch(
    proposal: FixProposal, repo_root: Path, branch: str, runner: CmdRunner
) -> CommitResult:
    repo_root = Path(repo_root)
    target = repo_root / proposal.file_path
    try:
        text = target.read_text(encoding="utf-8")
    except OSError as e:
        raise GitPrError(f"cannot read target file {proposal.file_path}: {e}") from e

    if proposal.old_line not in text:
        raise GitPrError("old line not present in target file — refusing to apply")
    new_text = text.replace(proposal.old_line, proposal.new_line, 1)
    if new_text == text:
        raise GitPrError("applying the fix changed nothing — refusing to commit")
    target.write_text(new_text, encoding="utf-8")

    runner.run(["git", "checkout", "-b", branch], cwd=repo_root)
    runner.run(["git", "add", proposal.file_path], cwd=repo_root)
    runner.run(["git", "commit", "-m", _commit_message(proposal)], cwd=repo_root)
    sha = runner.run(["git", "rev-parse", "HEAD"], cwd=repo_root).strip()
    return CommitResult(branch=branch, sha=sha, files_changed=[proposal.file_path])


def build_pr_cmd(proposal: FixProposal, repo: str, branch: str, base: str = "main") -> list[str]:
    """Build the `gh pr create` argv for the Branch-A reviewable PR. gh authenticates via the
    GITHUB_TOKEN env var (a fine-grained, single-repo token) — never embed a token on argv."""
    title = f"TestPilot: heal drifted locator in {proposal.file_path}"
    body = (
        "Auto-healed mechanical drift (a single-line locator change).\n\n"
        f"```diff\n{proposal.unified_diff}\n```\n\n"
        "This is a reviewable PR — a human merges. Behavioral changes are never auto-fixed."
    )
    return [
        "gh", "pr", "create",
        "--repo", repo,
        "--base", base,
        "--head", branch,
        "--title", title,
        "--body", body,
    ]


def build_rerun_cmd(
    *,
    orch_url: str,
    tenant: str,
    project_key: str,
    testset_key: str,
    params_file: str,
    account: str,
    client_id: str,
    folder: str,
    result_path: str = "./out",
) -> list[str]:
    """Build the Test-Manager test-set re-run argv. NOTE: exact flag surface is verified
    Day-1 against the installed CLI `--help`; tests assert flag-set membership, not order.
    The ClientSecret is supplied at runtime via $UIPATH_CLIENT_SECRET — never a literal."""
    return [
        "uipcli", "test", "run", orch_url, tenant,
        "--projectKey", project_key,
        "--testsetkey", testset_key,
        "-i", params_file,
        "-A", account,
        "-I", client_id,
        "-S", "$UIPATH_CLIENT_SECRET",
        "--applicationScope", _TM_SCOPES,
        "-o", folder,
        "--out", "junit",
        "--result_path", result_path,
    ]
