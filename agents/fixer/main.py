"""UiPath coded agent — Fixer (Branch A only). Maestro invokes this for a MECHANICAL_DRIFT
case. Drafts the one-line diff (via the injected/lazy LLM Gateway) and commits a branch;
the re-run and PR are offloaded downstream to respect the 15-min serverless cap.

Guardrail: refuses any non-mechanical case in code — behavior is NEVER auto-fixed (§14.2).
LLM/Cmd clients are built lazily inside main() so import is side-effect-free (§14.5).
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from testpilot.git_pr_runner import SubprocessCmdRunner, apply_and_branch
from testpilot.models import Category, EvalResult
from testpilot.selector_fixer import draft_fix
from testpilot.triage_classifier import classify


@dataclass
class Input:
    eval_result_json: str
    repo_url: str


@dataclass
class Output:
    branch: str
    sha: str
    unified_diff: str
    file_changed: str


def _default_llm():
    from testpilot.llm import UiPathLLMGatewayClient

    return UiPathLLMGatewayClient()


def main(input: Input, *, repo_root=None, llm=None, runner=None) -> Output:
    eval_result = EvalResult.model_validate_json(input.eval_result_json)

    category = classify(eval_result).category
    if category is not Category.MECHANICAL_DRIFT:
        raise ValueError(
            f"fixer refuses {category.value}: behavior is never auto-fixed — escalate to a human"
        )

    repo_root = Path(repo_root or os.environ.get("UIPATH_REPO_ROOT", "."))
    llm = llm or _default_llm()
    runner = runner or SubprocessCmdRunner()

    proposal = draft_fix(eval_result, repo_root, llm)
    commit = apply_and_branch(proposal, repo_root, f"fix/{eval_result.case_id}", runner)
    return Output(
        branch=commit.branch,
        sha=commit.sha,
        unified_diff=proposal.unified_diff,
        file_changed=proposal.file_path,
    )
