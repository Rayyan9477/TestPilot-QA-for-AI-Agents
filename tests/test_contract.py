"""Contract test — guards the silent Maestro<->agent name-match trap (the docs' #1 risk).

Introspects the live entrypoint dataclasses and asserts their field names exactly match the
documented Maestro mapping (maestro-mapping.json) and the golden entry-points snapshot. If
anyone renames a field without updating the mapping, this fails BEFORE recording. At S9 the
real published entry-points.json is diffed against the golden snapshot (§14.4).
"""
import dataclasses
import importlib.util
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
FIX = Path(__file__).parent / "fixtures"


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


triage = _load("ctr_triage_main", "agents/triage/main.py")
fixer = _load("ctr_fixer_main", "agents/fixer/main.py")

MAPPING = json.loads((FIX / "maestro-mapping.json").read_text())
GOLDEN = json.loads((FIX / "golden-entry-points.json").read_text())


def _fields(dc) -> set:
    return {f.name for f in dataclasses.fields(dc)}


def test_triage_input_fields_match_mapping():
    assert _fields(triage.Input) == set(MAPPING["triage"]["input"])


def test_triage_output_fields_match_mapping():
    assert _fields(triage.Output) == set(MAPPING["triage"]["output"])


def test_fixer_input_fields_match_mapping():
    assert _fields(fixer.Input) == set(MAPPING["fixer"]["input"])


def test_fixer_output_fields_match_mapping():
    assert _fields(fixer.Output) == set(MAPPING["fixer"]["output"])


def test_maestro_vars_are_camelcase():
    # A snake_case Maestro var is the symptom of a copy-paste from the agent side — forbid it.
    for name, agent in MAPPING.items():
        if name.startswith("_"):  # skip metadata keys like _comment
            continue
        for var in {**agent["input"], **agent["output"]}.values():
            assert "_" not in var, f"Maestro var {var!r} must be camelCase"


def test_golden_entrypoints_match_live_dataclasses():
    assert set(GOLDEN["triage"]["output"]) == _fields(triage.Output)
    assert set(GOLDEN["fixer"]["output"]) == _fields(fixer.Output)
    assert set(GOLDEN["triage"]["input"]) == _fields(triage.Input)
    assert set(GOLDEN["fixer"]["input"]) == _fields(fixer.Input)


def test_real_generated_entrypoints_match_golden():
    # Closes the S9 loop OFFLINE: the schema uipath ACTUALLY generates (scripts/build_agents.py)
    # must match the golden the Maestro mapping is built from. Skips if not yet generated.
    for agent in ("triage", "fixer"):
        ep_path = ROOT / "agents" / agent / "entry-points.json"
        if not ep_path.exists():
            pytest.skip(f"{agent}/entry-points.json not generated (run scripts/build_agents.py)")
        ep = json.loads(ep_path.read_text())["entryPoints"][0]
        assert set(ep["input"]["properties"]) == set(GOLDEN[agent]["input"])
        assert set(ep["output"]["properties"]) == set(GOLDEN[agent]["output"])
        assert set(ep["input"]["required"]) == set(GOLDEN[agent]["input"])
        assert set(ep["output"]["required"]) == set(GOLDEN[agent]["output"])
