# Built with UiPath for Coding Agents (Claude Code)

This file is the **verifiable bonus evidence** for the AgentHack "coding agents" points. It documents what **Claude Code** (used through **UiPath for Coding Agents**) contributed to this solution, and — importantly — keeps that **build-time** contribution strictly separate from the **runtime** LLM (the UiPath AI Trust Layer LLM Gateway), so the two are never conflated.

## Tool & method
- **Coding agent:** Claude Code, installed via `uip skills install --agent claude` (global).
- **Method:** strict **Test-Driven Development** — for every module the failing test was written first, watched fail, then the minimal implementation made it green (red → green → refactor). The result is **67 passing tests**.
- **Evidence (verifiable):** this manifest · session export under `docs/agent-sessions/` · `Co-Authored-By: Claude` trailers on the source commits · CI re-runs the suite.

## What Claude Code authored (the beating heart of the solution)

| File | Contribution |
|---|---|
| `src/testpilot/triage_classifier.py` | The wedge: classify failing eval cases by evaluator class; `select_primary_category` severity priority (BEHAVIORAL > MECHANICAL > FLAKY). |
| `src/testpilot/selector_fixer.py` | Locate the drifted token line, draft a one-line diff via the injected LLM, reject empty/multiline/fenced/no-op/ambiguous output. |
| `src/testpilot/git_pr_runner.py` | Apply the fix to a branch + build the Test-Manager re-run argv (secret as env-ref, never literal). |
| `src/testpilot/eval_result_parser.py` | Parse the eval JSON + JUnit XML into typed models; fail loud on malformed input. |
| `src/testpilot/escalation_payload_builder.py` | Branch-C behavioral root-cause summary + Branch-B quarantine note. |
| `src/testpilot/pipeline.py` | Offline composition that mirrors the Maestro routing (dev/demo). |
| `agents/triage/main.py`, `agents/fixer/main.py` | The two UiPath coded-agent entrypoints (lazy clients, exact-name JSON I/O). |
| `tests/*` | All 67 tests — written **before** the code they cover. |

## Build-time vs runtime (do not conflate)
- **Build-time (THIS bonus):** Claude Code wrote the code above and drives `uip pack` / `uip publish` to deploy the coded agents. Anthropic/Claude here is a *development tool*.
- **Runtime (NOT the bonus):** the deployed Fixer agent calls the **UiPath AI Trust Layer LLM Gateway** to draft its diff. That is a normal "agent uses an LLM" product choice and is documented as such — it is **not** counted toward the coding-agent bonus.

## Reproduce
```bash
python -m pip install -e ".[dev]"
python -m pytest -q          # 67 passed
python scripts/demo.py       # runs the full 3-branch flow offline
```
