# TestPilot — Next Steps (final handoff)

Everything that can be built and verified is **done**. This file is your checklist to finish + submit.

## ✅ Status snapshot (verified)
- **Code:** 8 modules + 2 coded agents + pipeline. **83 tests, 100% coverage.** Strict TDD.
- **On UiPath Automation Cloud:** both coded agents **published** to `DefaultTenant` (`testpilot-triage`, `testpilot-fixer`) — confirmed by `uipath publish` ("Package published successfully").
- **Bonus (+2) earned:** `uip skills install --agent claude` installed 21 UiPath skills for Claude Code (evidence in `docs/agent-sessions/uip-skills-install.md`).
- **Demo visual:** `dashboard/index.html` (+ `dashboard/testpilot-dashboard.png`) — Playwright-verified to render the verdict + all 3 branches.
- **Docs:** plan, system design, execution plan, compliance checklist, cloud runbook, submission content — all in `docs/`.

---

## Step 0 — Confirm the submission window
The stated deadline was **Jun 29, 2026, 11:45 pm EDT**. Check the Devpost page / your email for the current window or any extension. If it's closed, this is still a complete, portfolio-grade build you can submit late if the organizers allow, or showcase as-is.

## Step 1 — 🔴 Push the code to your public GitHub repo (required artifact)
The repo must contain the code to be a valid submission. Two ways:

**Option A — I push it for you:** reply with `push to github.com/<owner>/<repo>` and your go-ahead, and I'll commit + push in one shot. *(Secrets are gitignored; I'll add the `Co-Authored-By: Claude` trailer for the bonus trail.)*

**Option B — you push it** (from this machine, in `d:/Repo/UiPath AgentHack`):
```bash
git add -A
git commit -m "TestPilot: on-call QA engineer for AI agents (UiPath AgentHack, Track 3)"
git branch -M main
git remote add origin https://github.com/<owner>/<repo>.git
# authenticate with the fine-grained token (or run `gh auth login` instead):
git push -u "https://x-access-token:<YOUR_GITHUB_TOKEN>@github.com/<owner>/<repo>.git" main
```
- `.env`, `.venv`, `.uipath/`, `*.nupkg`, vendored `testpilot/` are all gitignored — **no secrets get pushed**.
- Confirm the **LICENSE (MIT)** shows at the top of the repo page.

## Step 2 — Record the demo video (< 5 min)
Show it **running**; narrate the 6 beats from [docs/SUBMISSION-CONTENT.md](docs/SUBMISSION-CONTENT.md). Easiest capture:
1. Open **`dashboard/index.html`** (or run `python scripts/demo.py`) → shows triage → 3 governed branches → **RELEASE BLOCKED**.
2. In your UiPath cloud: **Orchestrator → Tenant Processes Feed** showing `testpilot-triage` + `testpilot-fixer` = "runs on Automation Cloud."
3. Terminal: `uip skills install --agent claude` (bonus) + `pytest` (83 green).
Upload to **YouTube/Vimeo (unlisted)** — no copyrighted music/marks.

## Step 3 — Presentation deck
Fill the **provided template** (`bit.ly/3R0MsHU`) using the slide outline in [docs/SUBMISSION-CONTENT.md](docs/SUBMISSION-CONTENT.md). Host on Drive/OneDrive/Dropbox, shared **"access to all."**

## Step 4 — Submit on Devpost
- Project page: **Track 3**, paste the description from [docs/SUBMISSION-CONTENT.md](docs/SUBMISSION-CONTENT.md), add screenshots (use `dashboard/testpilot-dashboard.png`).
- Add links: repo, video, deck.
- Bonus block must appear in the README **and** the Devpost description (it's in both).
- Complete the **feedback form** (`forms.office.com/e/KitjGLF5k1`) — the $1,500 award.
- **Submit**, then verify all links open. Run the [COMPLIANCE-CHECKLIST](docs/COMPLIANCE-CHECKLIST.md) §G first.

## Stretch (if time) — Maestro orchestration
For the full on-platform story, build the Maestro BPMN that wires the agents per [docs/CLOUD-RUNBOOK.md](docs/CLOUD-RUNBOOK.md) (Start → Triage → gateway → Branch A PR + Branch C escalate). The agents are already published, so this is the wiring step.

---

## 🔐 Security (do this regardless)
- **Rotate the GitHub token** you shared in chat (it's exposed in the transcript). On the tenant, store the rotated token as a **Credential Asset** (`GITHUB_TOKEN`) for the fixer.
- The UiPath auth token sits in the local (gitignored) `.env` — fine locally; don't share it.

## Reference index
[README](README.md) · [PLAN](docs/TESTPILOT-PLAN.md) · [SYSTEM-DESIGN](docs/SYSTEM-DESIGN.md) · [EXECUTION-PLAN](docs/EXECUTION-PLAN.md) · [COMPLIANCE-CHECKLIST](docs/COMPLIANCE-CHECKLIST.md) · [CLOUD-RUNBOOK](docs/CLOUD-RUNBOOK.md) · [SUBMISSION-CONTENT](docs/SUBMISSION-CONTENT.md) · [CLAUDE-GENERATED](CLAUDE-GENERATED.md)
