# TestPilot — the on-call QA engineer for AI agents

> Built for the **UiPath AgentHack** (Track 3 · UiPath Test Cloud).

TestPilot runs on **UiPath Maestro** and treats AI agents as first-class software-under-test. It triages a failed **Agent Evaluation** run into three governed actions:

- **Mechanical drift** (a tool selector / output-schema field changed) → **auto-heal** into a *reviewable GitHub PR*.
- **Flaky** non-determinism → **quarantine** with a retry policy.
- **Behavioral regression** (the agent's behavior actually changed) → **never auto-fixed** — escalate to a human (Action Center + Slack) with an AI root-cause summary.

The load-bearing policy: **a behavioral change in an agent is a product decision, not a bug fix — only a human merges behavior.**

See [`docs/TESTPILOT-PLAN.md`](docs/TESTPILOT-PLAN.md) and [`docs/SYSTEM-DESIGN.md`](docs/SYSTEM-DESIGN.md).

## Built with UiPath for Coding Agents (Claude Code)  ·  vs runtime LLM

| Build-time — **BONUS** (UiPath for Coding Agents) | Runtime — **PRODUCT** (not the bonus) |
|---|---|
| Claude Code via `uip skills install --agent claude` authored the coded fixer/classifier and drove `uip pack`/`uip publish`. Evidence: `docs/agent-sessions/`, `CLAUDE-GENERATED.md`, `Co-Authored-By` commit trail. | The fixer drafts its one-line diff via the **UiPath AI Trust Layer LLM Gateway** (keyless, governed). This is an "agent uses an LLM" design choice — **not** the coding-agent bonus. |

## Develop

```bash
python -m venv .venv && ./.venv/Scripts/python -m pip install -e ".[dev,runtime]"
./.venv/Scripts/python -m pytest
```

_License: MIT. Test data is synthetic — no PHI, no customer data._
