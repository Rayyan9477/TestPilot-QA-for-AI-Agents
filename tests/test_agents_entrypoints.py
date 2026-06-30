"""TDD/contract — the two UiPath coded-agent entrypoints. Loaded by file path (as the
platform loads them) to prove they import with empty env (no client construction at import,
§14.5) and that their dataclass I/O round-trips JSON with the exact contract field names.
"""
import dataclasses
import importlib.util
import json
import shutil
import sys
from pathlib import Path

import pytest

from testpilot.llm import FakeLLM

ROOT = Path(__file__).parent.parent
FIX = Path(__file__).parent / "fixtures"


def _load(name, rel):
    # Register in sys.modules before exec so @dataclass can resolve the module's namespace
    # (this is exactly what the UiPath runtime does when it imports main.py).
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


triage = _load("tp_triage_main", "agents/triage/main.py")
fixer = _load("tp_fixer_main", "agents/fixer/main.py")


class FakeCmdRunner:
    def __init__(self, sha="c" * 40):
        self.calls = []
        self._sha = sha

    def run(self, argv, cwd=None):
        self.calls.append(list(argv))
        return self._sha + "\n" if "rev-parse" in argv else ""


def _first_case_json(fixture):
    return json.dumps(json.loads((FIX / fixture).read_text())[0])


# --- triage entrypoint ---------------------------------------------------------------

def test_triage_seed_drift_primary_is_mechanical():
    out = triage.main(triage.Input(eval_results_json=(FIX / "seed_drift.json").read_text()))
    assert out.primary_category == "MECHANICAL_DRIFT"
    assert len(out.classifications) == 1
    assert out.classifications[0]["category"] == "MECHANICAL_DRIFT"


def test_triage_seed_all_primary_is_behavioral():
    out = triage.main(triage.Input(eval_results_json=(FIX / "seed_all.json").read_text()))
    assert out.primary_category == "BEHAVIORAL_REGRESSION"
    assert len(out.classifications) == 3


def test_triage_output_json_roundtrips_with_exact_names():
    out = triage.main(triage.Input(eval_results_json=(FIX / "seed_drift.json").read_text()))
    d = dataclasses.asdict(out)
    assert set(d.keys()) == {"classifications", "primary_category"}
    json.dumps(d)  # must be JSON-serializable for the Maestro boundary


def test_triage_empty_input_raises():
    with pytest.raises(ValueError):
        triage.main(triage.Input(eval_results_json=""))


# --- fixer entrypoint ----------------------------------------------------------------

def _corrected_line(repo):
    line = next(l for l in (repo / "UiTests" / "CheckoutTest.cs").read_text().splitlines() if "btn-signin" in l)
    return line.replace("btn-signin", "btn-login")


def test_fixer_returns_branch_and_diff(tmp_path):
    repo = tmp_path / "repo"
    shutil.copytree(FIX / "sample_repo", repo)
    out = fixer.main(
        fixer.Input(eval_result_json=_first_case_json("seed_drift.json"), repo_url="https://github.com/x/y"),
        repo_root=repo, llm=FakeLLM(_corrected_line(repo)), runner=FakeCmdRunner(),
    )
    assert out.branch == "fix/drift-01"
    assert "btn-login" in out.unified_diff
    assert out.file_changed.endswith("CheckoutTest.cs")


def test_fixer_refuses_behavioral_case(tmp_path):
    repo = tmp_path / "repo"
    shutil.copytree(FIX / "sample_repo", repo)
    with pytest.raises(ValueError):
        fixer.main(
            fixer.Input(eval_result_json=_first_case_json("seed_regr.json"), repo_url="x"),
            repo_root=repo, llm=FakeLLM("whatever"), runner=FakeCmdRunner(),
        )


def test_fixer_output_has_exact_field_names(tmp_path):
    repo = tmp_path / "repo"
    shutil.copytree(FIX / "sample_repo", repo)
    out = fixer.main(
        fixer.Input(eval_result_json=_first_case_json("seed_drift.json"), repo_url="x"),
        repo_root=repo, llm=FakeLLM(_corrected_line(repo)), runner=FakeCmdRunner(),
    )
    d = dataclasses.asdict(out)
    assert set(d.keys()) == {"branch", "sha", "unified_diff", "file_changed"}
    json.dumps(d)
