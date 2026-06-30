"""UiPath coded agent — Triage. Maestro invokes this as a Service task.

Thin glue over the unit-tested pure modules: parse the seeded failed-eval JSON, classify
every case by evaluator class, and emit the build's primary_category (severity priority)
that the Maestro exclusive gateway switches on. No client construction at import (§14.5).
"""
from __future__ import annotations

from dataclasses import dataclass

from testpilot.eval_result_parser import parse_eval_results
from testpilot.triage_classifier import classify, select_primary_category


@dataclass
class Input:
    eval_results_json: str


@dataclass
class Output:
    classifications: list  # list[dict] — one per case, JSON-safe
    primary_category: str  # the bucket the Maestro gateway routes on


def main(input: Input) -> Output:
    if not (input.eval_results_json or "").strip():
        raise ValueError("triage received empty eval_results_json")
    cases = parse_eval_results(input.eval_results_json)
    classifications = [classify(c) for c in cases]
    primary = select_primary_category(classifications)
    return Output(
        classifications=[c.model_dump(mode="json") for c in classifications],
        primary_category=primary.value,
    )
