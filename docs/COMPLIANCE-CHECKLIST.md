# TestPilot — Requirements Compliance & Readiness Audit
### Cross-check of the official UiPath AgentHack rules (re-pulled) against our plan

**Verdict:** ✅ We are aligned and execution-ready. No architectural gaps. **9 packaging/process items** were easy to miss — all now folded into the plan below. **2 substantive emphases** (Studio Web anchoring + Test Cloud foregrounding for Track-3 fit) and **3 items only you can self-verify** (residence, account age, team lock).

Legend: ✅ covered · ⚠️ action folded in · 📌 your self-check · 🕓 later (finalist/live round)

---

## A. Mandatory submission artifacts

| Artifact | Required contents (exact) | Status | Where we handle it |
|---|---|---|---|
| **Devpost project page** | title · **track selection** · written description (what it does, business problem, how it works) · **screenshots/images** | ⚠️→✅ | Sprint **S16** (now explicit) |
| **Demo video** | **< 5 min** · YouTube/Vimeo/Youku · shows it **running** (not slides) · walk the **architecture** · explain **which agents + how orchestrated** · **show where humans fit** · **no copyrighted music / third-party trademarks** · English | ⚠️→✅ | S14 record + **S15** (constraints added) — our 6-beat script already covers running/architecture/orchestration/human |
| **Public GitHub repo** | all files to understand/run · **license MIT or Apache-2.0 visible at top of repo** | ✅ | LICENSE (MIT) at root → GitHub auto-detects; S1 |
| **README.md** | what it does + problem · **comprehensive UiPath components list** · **explicit agent-type declaration (coded / low-code / combination)** · **step-by-step setup** · prerequisites | ⚠️→✅ | **S15** — agent-type line + full setup added (we are a **combination**) |
| **Working solution on Automation Cloud** | "orchestration and agent logic must run **through the UiPath Platform**" · external services/LLMs welcome | ✅ | Maestro + serverless agents + Action Center + connectors (S9–S12); demo proves cloud execution |
| **Presentation deck** | **must use the provided template** (`bit.ly/3R0MsHU`) · host on Drive/OneDrive/Dropbox · **share "access to all"** | ⚠️→✅ | **S15** — provided-template mandate added |
| **Text description (submission form)** | features, functionality, business problem & how addressed | ⚠️→✅ | S16 (project-page text) |
| **Product feedback form** (optional, $1,500) | one rep completes `forms.office.com/e/KitjGLF5k1`; address Maestro/Test Cloud/etc. | ✅ | S16 |

---

## B. Judging — how we score (Phase 1 = "automated review", 5×5 + bonus)

| Criterion (1–5) | Our hook |
|---|---|
| Business Impact & Adoption | Unmet 2026 pain: governing AI-agent quality; reviewable PRs + human-gated behavior = enterprise-adoptable |
| **Platform Usage** (bonus lives here) | Maestro BPMN + low-code triage agent + Python coded fixer on serverless + **Agent Evaluations** + **Test Cloud/Test Manager** execution + Integration Service (GitHub/Slack) + Action Center + AI Trust Layer |
| Technical Execution | Durable case, exception branches, verified-doc'd, real failure handling, full TDD suite |
| Completeness | End-to-end prototype + repo+README + ≤5-min video + deck |
| Creativity & Innovation | Agent-tests-agent wedge + "never auto-fix behavior" policy |
| **Presentation** (Phase 2 only, replaces Completeness) | Live Zoom + Q&A — prep below 🕓 |

> **Phase 1 is an automated/initial review** → make README + Devpost description **explicit and structured** (clear component list, explicit agent-type line, explicit bonus evidence) so an automated pass scores us correctly.

**Coding-agents bonus — earning the full 2/2:** rules require *"meaningfully and substantively integrated"* + **≥1 evidence** (prompt log / session export / screenshots / README section) + independent verifiability, documented in **Devpost description OR README**.
- ✅ We exceed it: Claude Code **authors the fixer/classifier AND drives `uip pack`/`uip publish`**; evidence = `CLAUDE-GENERATED.md` + `/docs/agent-sessions/` export + `Co-Authored-By` trail + README section + on-camera `uip skills install`.
- ⚠️ Guard: keep build-time Claude Code (bonus) strictly separate from the runtime LLM Gateway (product) — the **two-column README wall** prevents a 2→1 downgrade.

---

## C. Substantive readiness emphases (don't gloss over)

1. **"Built using UiPath Studio Web" + runs on Automation Cloud** — disqualification trigger if not. ✅ Maestro is authored in **Studio Web**; the coded agents are created as **Studio Web / Automation Cloud coded-agent projects** and published to serverless (local Python authoring + `uip` publish is explicitly allowed — "you can incorporate pre-existing code"). **Action (S8–S10): anchor the agent + orchestration creation in Studio Web and say so in the README** so the requirement is unambiguous.
2. **Track-3 fit = genuinely uses Test Cloud.** Our re-run runs through **Test Manager (Test Cloud)** against a real coded test case. ⚠️ **Foreground Test Cloud in the demo + README** (the coded test executing, red→green via Test Manager) so judges see Track-3 alignment clearly — not just Agent Evaluations + Maestro. Prioritize the Test Cloud sales request (S0) to get the real App-Testing-Robot run as the strongest "uses Test Cloud" proof; the Test-Manager-on-Agentic-trial path is the compliant fallback.

---

## D. Eligibility & disqualification triggers

| Item | Status |
|---|---|
| **New project, built during May 15–Jun 29 window, in Studio Web** | ✅ repo + code created now (within window); git history proves it |
| **No UiPath financial/contract support pre-submission** | ✅ self-funded |
| **Original work / no third-party IP violation / English** | ✅ original; synthetic data; English |
| **License MIT/Apache visible at repo top** | ✅ MIT LICENSE at root |
| **Residence not excluded** (Brazil, Quebec, Russia, Crimea, Cuba, Iran, N. Korea, Sudan, Syria, OFAC) | 📌 **you confirm** |
| **Best First-Time Builder** (new-builder award) | 📌 not targeting — you're an experienced builder |
| **Team roster lock after Labs access** | ✅ solo → N/A |
| **One project / one track** (no multi-track of same project) | ✅ single Track-3 entry |
| **Max 2 prizes/project** (1 track + 1 special) | ✅ strategy: Track-3 placement **+** one special (Most Creative / Best Demo / Cross-Platform) — don't expect to stack multiple specials |
| **People's Choice** (Jul 3–30 voting; no manipulation) | ✅ optional, honest solicitation only |

---

## E. Key dates & post-submission obligations

- **Submission deadline:** **Jun 29, 2026, 11:45 pm EDT** (after this, no edits). 
- Judging/finalist selection: Jun 3 – Jul 14 · Public voting: Jul 3–30 · **Finalist live presentation ~Jul 23** · Winners ~Aug 4.
- 🕓 **Finalist obligation (mandatory to stay eligible):** publish the solution as a **Use Case on the UiPath Community Forum** after finalist announcement.
- 🕓 **Phase 2 = live Zoom presentation + Q&A** — prep the deck-driven talk + anticipate Q&A on the wedge, the never-auto-fix policy, and the platform usage.

---

## F. Gaps found in this audit → fixes applied
1. Deck must use the **provided template** + "access to all" → **S15**.
2. README must carry an **explicit agent-type declaration** (we are a *combination*) → **S15**.
3. Video constraints: **no copyrighted music / third-party trademarks**, English → **S15**.
4. **Devpost project-page text description + screenshots** is its own artifact → **S16**.
5. **Studio Web** anchoring made explicit → **S8–S10** + README note.
6. **Test Cloud foregrounding** for Track-3 fit → demo + README emphasis.
7. **Finalist Community-Forum** obligation captured → post-M5 note.
8. **Phase 2 live Q&A** prep captured → post-M5 note.
9. **Phase 1 automated review** → keep docs explicit/structured.

## G. Final pre-submission QA (day-of checklist)
- [ ] Repo public; MIT LICENSE detected at top; README complete (components · **agent type: combination** · setup · prerequisites · citations · bonus wall).
- [ ] Video < 5:00, on YouTube/Vimeo/Youku, shows it RUNNING on Automation Cloud, no copyrighted music/marks.
- [ ] Deck on the **provided template**, shared **access-to-all**, link in form.
- [ ] Devpost page: title · **Track 3** · text description (problem/how) · screenshots.
- [ ] Bonus evidence present in README **and** Devpost description (name + contribution + verifiable evidence).
- [ ] Working solution demonstrably on Automation Cloud (Maestro + agents + Test Cloud + Action Center on camera).
- [ ] Feedback form submitted.
- [ ] Submitted with buffer before **11:45 pm EDT Jun 29**.
