# TestPilot — Submission Content (S14–S16, paste-ready)
### Demo narration · deck outline · Devpost description. Finalize once the cloud demo is recorded.

---

## 1. Demo video — shot list + narration (<5:00, the 6 beats)

> Record it RUNNING on Automation Cloud (no slides for the demo). No copyrighted music / third-party marks. English.

**[0:00–0:35] Hook + the rule.**
> "Everyone is shipping AI agents. Nobody can tell you when an agent has *silently regressed* — when its behavior drifted, not its code. Self-healing selectors is a solved problem. Governing *agent quality* is not."
Cut to a **red Agent-Evaluation run** in UiPath. State the rule on screen: *auto-fix only mechanical drift · quarantine only proven flakiness · never auto-fix a behavioral regression — that goes to a human.*

**[0:35–1:15] Triage on-platform.**
Start the **Maestro** process on the seeded failed-eval set. Show the **Triage agent** classifying each case by *which evaluator failed*, and the **exclusive gateway** lighting up. The novelty beat: *the system-under-test is an AI agent, and triage reasons over evaluator classes — not HTTP 200s.*

**[1:15–2:30] Branch A — governed self-heal.**
Flash the commit/session: *"this fixer was authored by Claude Code via UiPath for Coding Agents."* The **Fixer agent** drafts a one-line diff via the **LLM Gateway**, commits a branch, and **`uipcli test run`** flips the JUnit **red→green**. The **GitHub PR opens** — show the real PR page. *"A reviewable PR, not a silent runtime patch."*

**[2:30–3:25] Branch C — the guardrail (the memorable beat).**
Route the behavioral case. TestPilot does **not** touch the code. It opens an **Action Center** task — *"LLM-as-Judge faithfulness dropped to 41; trajectory diverged at tool-call step 3"* — and posts the same to **Slack**. Show the human approval gate. Say the line: *"A behavioral change in an agent is a product decision, not a bug fix. Only a human merges behavior."*

**[3:25–4:05] Branch B + durability.**
Flaky case **quarantined** with a retry policy. Then the **Maestro Execution Trail** — demonstrate **pause / resume / retry-from-failed-task** on a live instance. *"A real, durable on-call process, not a script."*

**[4:05–4:45] Bonus + close.**
Terminal: `uip login` → `uip skills install --agent claude` → Claude Code driving `uip`. Point to `/docs/agent-sessions/` + `CLAUDE-GENERATED.md`. Close:
> "TestPilot is the on-call QA engineer for AI agents — it heals what's mechanical, quarantines what's flaky, and escalates what's behavioral to a human, all governed on the UiPath platform."

---

## 2. Presentation deck — slide outline (drop into the provided template `bit.ly/3R0MsHU`)

1. **Title** — TestPilot: the on-call QA engineer for AI agents · Track 3 · your name.
2. **The problem** — enterprises ship agents with no governed way to catch *silent behavioral regressions*. Self-healing selectors is commodity; agent-quality governance is the gap.
3. **The wedge** — the SUT is itself a non-deterministic AI agent; *only a human merges behavior.*
4. **How it works** — the 3-bucket governance diagram (drift→auto-heal PR · flaky→quarantine · behavioral→human). [use the SYSTEM-DESIGN §4 diagram]
5. **On-platform architecture** — Maestro BPMN + Agent Builder + coded agents + Agent Evaluations + Test Cloud + Integration Service + Action Center + AI Trust Layer.
6. **Live demo** — (the 6 beats; screenshots as backup).
7. **Why it scores** — rubric map: Business Impact · Platform depth (+ coding-agent bonus) · Technical execution (76 TDD tests) · Completeness · Creativity.
8. **Built with UiPath for Coding Agents** — the two-column wall (build-time Claude Code vs runtime LLM Gateway).
9. **Roadmap** — Maestro *Case*, live webhook auto-trigger, per-case looping, real Test-Cloud robot, AI-Trust-Layer policy.
10. **Close** — the one-liner + repo link.

> Share the deck with **"access to all."**

---

## 3. Devpost project page — description (paste-ready)

**Inspiration.** Every enterprise is racing to ship AI agents. But agents fail differently from code: they regress in *behavior*, silently, with no compiler to catch it. Existing "self-healing test" tools only fix broken selectors on deterministic apps — none treat a non-deterministic agent as the thing under test.

**What it does.** TestPilot is an on-call QA engineer that runs on **UiPath Maestro** and triages a failed **Agent Evaluation** run. It classifies each failing case by *which evaluator class* failed and applies a policy-correct action: **mechanical drift** → auto-heal into a *reviewable GitHub PR*; **flaky non-determinism** → quarantine with a retry policy; **behavioral regression** → **never auto-fixed**, escalated to a human (Action Center + Slack) with an AI root-cause summary. The load-bearing policy: *a behavioral change in an agent is a product decision, not a bug fix — only a human merges behavior.*

**How we built it.** UiPath components: **Maestro** (BPMN agentic process, durable Execution Trail), **Agent Builder** (low-code triage agent), **Coded Agents** (Python fixer on serverless), **Agent Evaluations** (Deterministic / LLM-as-Judge / Trajectory), **Test Cloud / Test Manager** (coded test re-run), **Integration Service** (GitHub + Slack), **Action Center** (human approval), and the **AI Trust Layer LLM Gateway** (keyless runtime LLM). **Agent type: combination.** Built **test-first (TDD)** — 76 passing tests — with **Claude Code via UiPath for Coding Agents** (see `CLAUDE-GENERATED.md`).

**Challenges.** Designing a routing policy where a behavioral regression can *never* be auto-healed (enforced in two independent code paths), keeping the runtime LLM governed and keyless, and bundling shared code into serverless coded agents.

**What's next.** Maestro *Case*, a live test-run→Maestro auto-trigger, per-case looping, a real App-Testing-Robot run, and an AI-Trust-Layer governance policy.

**Try it.** `pip install -e ".[dev]" && pytest` (76 green) · `python scripts/demo.py` runs the full 3-branch flow offline.

_Repo: <link> · License: MIT · Test data is synthetic (no PHI)._

> Also paste the **"## Built with UiPath for Coding Agents (Claude Code)"** block here (from the README) so the bonus is documented in the Devpost description **and** the README.
