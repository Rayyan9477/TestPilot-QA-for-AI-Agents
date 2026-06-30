"""Parse the seeded/captured agent-evaluation payload and JUnit XML into typed models.

Decouples brittle external shapes from the classifier so format drift can never silently
mis-route a case. The evaluator_type is trusted when present; a label->enum table is used
only as a fallback when it is absent (SYSTEM-DESIGN §14.3).
"""
from __future__ import annotations

import json
import xml.etree.ElementTree as ET

from .models import EvalResult, EvaluatorType, JUnitReport


class ParseError(Exception):
    """Raised when external eval/JUnit input is malformed — never return an empty
    success that would look like 'no failures'."""


_NAME_TO_TYPE = {
    "exact match": EvaluatorType.DETERMINISTIC_EXACT,
    "json similarity": EvaluatorType.JSON_SIMILARITY,
    "semantic similarity": EvaluatorType.SEMANTIC_SIMILARITY,
    "faithfulness": EvaluatorType.LLM_JUDGE_FAITHFULNESS,
    "trajectory": EvaluatorType.TRAJECTORY,
}


def parse_eval_results(raw: str | list | dict) -> list[EvalResult]:
    if isinstance(raw, str):
        try:
            data = json.loads(raw)
        except (json.JSONDecodeError, ValueError) as e:
            raise ParseError(f"invalid eval JSON: {e}") from e
    else:
        data = raw

    if not isinstance(data, list):
        raise ParseError("eval results must be a JSON array of cases")

    out: list[EvalResult] = []
    for i, item in enumerate(data):
        if not isinstance(item, dict):
            raise ParseError(f"eval case #{i} is not an object")
        item = dict(item)
        if not item.get("evaluator_type"):
            name = str(item.get("evaluator_name", "")).strip().lower()
            mapped = _NAME_TO_TYPE.get(name)
            if mapped is None:
                raise ParseError(
                    f"cannot map evaluator_name {item.get('evaluator_name')!r} to a known type"
                )
            item["evaluator_type"] = mapped.value
        item.setdefault("evaluator_name", item["evaluator_type"])
        try:
            out.append(EvalResult(**item))
        except Exception as e:  # pydantic ValidationError or bad field
            raise ParseError(f"invalid eval case #{i}: {e}") from e
    return out


def _local(tag: str) -> str:
    return tag.split("}")[-1]  # strip an XML namespace, if any


def parse_junit(xml: str) -> JUnitReport:
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as e:
        raise ParseError(f"invalid JUnit XML: {e}") from e

    if _local(root.tag) not in ("testsuites", "testsuite"):
        raise ParseError(f"not a JUnit document (root <{root.tag}>)")

    cases: list[dict] = []
    for el in root.iter():
        if _local(el.tag) != "testcase":
            continue
        failed = any(_local(child.tag) in ("failure", "error") for child in el)
        cases.append({"name": el.get("name", ""), "passed": not failed})

    failures = sum(1 for c in cases if not c["passed"])
    return JUnitReport(tests=len(cases), failures=failures, cases=cases)


def is_green(report: JUnitReport) -> bool:
    """Green only if there is at least one test and none failed (errors count as failures)."""
    return report.failures == 0 and report.tests > 0
