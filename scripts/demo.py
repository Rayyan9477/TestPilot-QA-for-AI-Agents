"""Local demo / rehearsal harness — runs the full TestPilot triage+routing offline over a
seeded failed-eval set and prints what it decided for each branch. No tenant, no network.

    python scripts/demo.py [seed.json] [repo_root]

This MIRRORS the Maestro routing for rehearsal; production orchestration is the Maestro BPMN.
The deterministic seed LLM below swaps actual->expected so the dry-run needs no cloud LLM.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from testpilot.pipeline import route_failures  # noqa: E402


class _SeedHealLLM:
    """Deterministic offline stand-in for the LLM Gateway: reconstructs the corrected line
    by swapping the drifted value for the expected one, both read from the fixer's prompt."""

    def complete(self, prompt: str) -> str:
        current = prompt.split("Current line:\n", 1)[1].split("\nReturn the corrected", 1)[0]
        m = re.search(r"The value '(.+?)' should be '(.+?)'", prompt)
        if not m:
            return current
        return current.replace(m.group(1), m.group(2))


def main(argv):
    seed = Path(argv[1]) if len(argv) > 1 else ROOT / "tests/fixtures/seed_all.json"
    repo = Path(argv[2]) if len(argv) > 2 else ROOT / "tests/fixtures/sample_repo"

    result = route_failures(seed.read_text(), repo, _SeedHealLLM())

    tag = {"auto_heal": "[HEAL ]", "quarantine": "[QUAR ]", "escalate": "[ESCAL]"}
    print(f"\nTestPilot triaged {len(result.actions)} failing eval case(s) from {seed.name}\n")
    for a in result.actions:
        print(f"  {tag.get(a.action, '[?]')} {a.case_id:<9} {a.category:<22} -> {a.summary}")
        if a.action == "auto_heal":
            for line in a.detail["unified_diff"].splitlines():
                print(f"          {line}")
        elif a.action == "escalate":
            print(f"          slack: {a.detail['slack_text']}")
        elif a.action == "quarantine":
            print(f"          retry: {a.detail['retry_policy']}")
    print(f"\n  BUILD VERDICT (Maestro gateway routes on): {result.primary_category}")
    if result.primary_category == "BEHAVIORAL_REGRESSION":
        print("  -> RELEASE BLOCKED: a behavioral regression must be merged by a human.\n")
    else:
        print()


if __name__ == "__main__":
    main(sys.argv)
