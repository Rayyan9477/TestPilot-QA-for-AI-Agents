"""Domain model — the single source of truth.

JSON field names are contract-frozen: they must match the Maestro Output>Response
mappings byte-for-byte (see docs/SYSTEM-DESIGN.md §2/§3).
"""
from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class EvaluatorType(str, Enum):
    DETERMINISTIC_EXACT = "deterministic_exact"        # exact-match -> mechanical
    JSON_SIMILARITY = "json_similarity"                # output-schema field drift -> mechanical
    SEMANTIC_SIMILARITY = "semantic_similarity"        # fuzzy text -> flaky-capable
    LLM_JUDGE_FAITHFULNESS = "llm_judge_faithfulness"  # behavior -> behavioral
    TRAJECTORY = "trajectory"                          # tool-path -> behavioral


class Category(str, Enum):
    MECHANICAL_DRIFT = "MECHANICAL_DRIFT"
    FLAKY = "FLAKY"
    BEHAVIORAL_REGRESSION = "BEHAVIORAL_REGRESSION"


class EvalResult(BaseModel):
    case_id: str
    evaluator_type: EvaluatorType
    evaluator_name: str
    score: int = Field(ge=0, le=100)
    passed_on_retry: bool = False
    retry_count: int = 1
    expected: str | None = None
    actual: str | None = None
    trajectory_diff: str | None = None


class Classification(BaseModel):
    case_id: str
    category: Category
    reason: str
    confidence: float = Field(ge=0.0, le=1.0)


class JUnitReport(BaseModel):
    tests: int
    failures: int
    cases: list[dict]  # [{"name": str, "passed": bool}]


class FixProposal(BaseModel):
    file_path: str       # repo-relative; resolves under repo_root
    old_line: str
    new_line: str
    unified_diff: str    # exactly one '-' and one '+' content line


class CommitResult(BaseModel):
    branch: str
    sha: str
    files_changed: list[str]


class RootCauseSummary(BaseModel):
    title: str
    body_markdown: str
    slack_text: str = Field(max_length=4000)


class QuarantineNote(BaseModel):
    case_id: str
    action: str = "quarantine"
    retry_policy: dict
