# Bonus evidence — UiPath for Coding Agents (Claude Code)

This documents the **build-time** use of *UiPath for Coding Agents* (the +2 coding-agents bonus). It is kept strictly separate from the **runtime** LLM (the AI Trust Layer LLM Gateway, which is the product feature — see `CLAUDE-GENERATED.md`).

## What was run

```bash
# 1. Install the UiPath coding-agents CLI (the `uip` command)
npm install -g @uipath/cli          # -> uip 1.196.0

# 2. Install UiPath skills for Claude Code (global) — UiPath for Coding Agents
uip skills install --agent claude
```

## Result (verified)

```json
{
  "Result": "Success",
  "Code": "SkillsInstall",
  "Data": { "Agents": ["claude"], "Installed": 21 }
}
```

**21 UiPath skills installed for Claude Code**, including the ones directly used to build this solution:
- `uipath-agents` — build/deploy coded + low-code agents
- `uipath-maestro-bpmn`, `uipath-maestro-case`, `uipath-maestro-flow` — orchestration
- `uipath-test` — agentic testing (Track 3)
- `uipath-human-in-the-loop` — Action Center HITL
- `uipath-solution`, `uipath-tasks`, `uipath-api-workflow`, `uipath-governance`, `uipath-review`, `uipath-platform`, …

## How Claude Code (via UiPath for Coding Agents) built the solution
- Authored the entire Python core **test-first (TDD)** — 83 tests, 100% coverage (see `CLAUDE-GENERATED.md` for the per-file map).
- Drove the **Python `uipath` CLI** to `uipath init` / `uipath pack` both coded agents into `.nupkg`, and validated the generated `entry-points.json` against the contract.
- Ran the triage agent under the real `uipath` runtime (`uipath run main`) to confirm execution.

## Build-time vs runtime (do not conflate)
- **Build-time (THIS bonus):** Claude Code + `uip skills` + the `uipath` CLI built/packaged the solution.
- **Runtime (NOT the bonus):** the deployed Fixer agent calls the **UiPath AI Trust Layer LLM Gateway** (`sdk.llm.chat_completions`) to draft its diff.
