"""Local composition harness: triage a failed-eval set and route each case to its governed
action, returning a structured result. This MIRRORS the Maestro BPMN routing for offline
dev/demo/rehearsal — production orchestration is the Maestro process, not this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .escalation_payload_builder import build_quarantine_note, build_regression_summary
from .eval_result_parser import parse_eval_results
from .llm import LLMClient
from .models import Category
from .selector_fixer import draft_fix
from .triage_classifier import classify, select_primary_category


@dataclass
class BranchAction:
    case_id: str
    category: str
    action: str       # "auto_heal" | "quarantine" | "escalate"
    summary: str
    detail: dict


@dataclass
class PipelineResult:
    primary_category: str  # the build verdict the Maestro gateway would route on
    actions: list


def route_failures(eval_results_json: str, repo_root: Path, llm: LLMClient) -> PipelineResult:
    repo_root = Path(repo_root)
    cases = parse_eval_results(eval_results_json)
    classifications = [classify(c) for c in cases]

    actions: list[BranchAction] = []
    for eval_result, cls in zip(cases, classifications):
        if cls.category is Category.MECHANICAL_DRIFT:
            fp = draft_fix(eval_result, repo_root, llm)
            actions.append(BranchAction(
                case_id=eval_result.case_id, category=cls.category.value, action="auto_heal",
                summary=f"heal drifted locator in {fp.file_path}",
                detail={"file": fp.file_path, "unified_diff": fp.unified_diff},
            ))
        elif cls.category is Category.FLAKY:
            note = build_quarantine_note(cls)
            actions.append(BranchAction(
                case_id=eval_result.case_id, category=cls.category.value, action="quarantine",
                summary="quarantine with retry policy", detail=note.model_dump(),
            ))
        else:  # BEHAVIORAL_REGRESSION — never auto-fixed
            summary = build_regression_summary(cls, eval_result)
            actions.append(BranchAction(
                case_id=eval_result.case_id, category=cls.category.value, action="escalate",
                summary=summary.title,
                detail={"slack_text": summary.slack_text, "body_markdown": summary.body_markdown},
            ))

    return PipelineResult(primary_category=select_primary_category(classifications).value, actions=actions)
