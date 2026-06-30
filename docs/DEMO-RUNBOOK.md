# TestPilot — Demo Runbook (how & when to present what)

> Pair this with [`DEMO-SCRIPT.md`](DEMO-SCRIPT.md) (the word-for-word 3-minute speech).
> **Golden rule:** click slowly, talk over the motion, never race the animation.

---

## 1. Pre-flight (do this ~10 minutes before)

1. **Start the board** (from the repo root):
   ```bash
   python -m http.server 8139 --directory dashboard
   ```
   Open **http://localhost:8139/** in **Chrome/Edge**.
2. **Go fullscreen** (`F11`) at **1920×1080** (or share that resolution). The board is designed for a 16:9 wide screen.
3. **Turn OFF "reduce motion"** in your OS *for the demo machine* — the animations (the whole point) collapse to instant if reduce-motion is on.
   - Windows: Settings → Accessibility → Visual effects → **Animation effects = On**.
4. **Hard-refresh once** (`Ctrl+Shift+R`) so you start from a clean state (BAD MERGES PREVENTED = 18, chain VERIFIED).
5. Let the **boot sequence** finish (or click **SKIP**). You should see the full board, console clean.
6. Have a second tab open on the **GitHub repo** + the **README** (the `tp-demo.png` shot) as a fallback if the live board ever misbehaves.

**Reset between every practice run:** just hard-refresh (`Ctrl+Shift+R`). That resets the counters, the ledger, and the chain.

---

## 2. The set — know your four zones (so you can point)

| Zone | Where | What it proves |
|---|---|---|
| **KPI rail** (top) | the 5 big numbers | the headline: **BAD MERGES PREVENTED** (pink) |
| **Triage Firewall** (center-left) | router → 3 lanes | the core idea: behavior gets *deflected*, not merged |
| **Fleet Trust + Evaluators** (center-right) | gauge `74` + constellation | "we score *trust*, not just pass/fail" |
| **Live feed + Human Gate + Ledger** (right + status bar) | feed, "Try to auto-merge", CHAIN: VERIFIED | live triage + the human gate + the audit trail |

---

## 3. Run sheet (the 3-minute spine)

> The **▶ PLAY DEMO** autopilot does the risky middle for you and **narrates itself** (teleprompter at the bottom). You talk over it. It ends on the **Governance Ledger** — which sets up the two live "touch-it" moments perfectly.

| # | Time | You DO this | You SAY (see script) | What appears |
|---|---|---|---|---|
| 1 | 0:00–0:25 | Nothing — board is on screen | The hook + "on-call QA for AI agents" | Fleet of 24, trust 74, KPIs |
| 2 | 0:25 | **Click ▶ PLAY DEMO** (top-right, it's pulsing) | Narrate the 3 cases | Narrated story auto-plays |
| 3 | ~0:40 | (let it run) point at the PR lane | drift → **auto-heal → PR** | green packet → PR bay |
| 4 | ~0:55 | (let it run) | flaky → **quarantine** | amber packet → Q bay |
| 5 | ~1:10 | (let it run) point at the firewall | **the dangerous one → DEFLECTED** | red packet bounces off **FIREWALL** → ESC; **BAD MERGES PREVENTED ticks up**; REFUSED toast |
| 6 | ~1:25 | (let it run) | "here's what the human gets" | Evidence drawer: tool-path, scores, AI root-cause |
| 7 | ~1:45 | demo lands on the **Ledger** | "every decision is hash-chained…" | Governance Ledger panel open |
| 8 | ~1:55 | **Click TAMPER DEMO** (in the ledger), then click it again | "tamper-evident… broken… reverted" | CHAIN: **BROKEN** (red) → **VERIFIED** |
| 9 | ~2:20 | Press **Esc**, then click the red **"⛔ Try to auto-merge behavior"** | "the policy is code, not a slide… DENIED" | Giant **DENIED** stamp slams in |
| 10 | 2:40–3:00 | Gesture to the **UIPATH PIPELINE** strip | the stack + coding-agents bonus + close | — |

**If you have only 60 seconds:** do steps 2 → 5 (PLAY DEMO until the firewall deflection) → 9 (DENIED). That alone tells the whole story.

---

## 4. The two live "money" moments (don't skip these)

These are the moments judges *remember* because **you touch it live**:

- **TAMPER** → in the open ledger, the `TAMPER DEMO` button. One click breaks the chain (turns red, status bar reads **BROKEN**); a second click restores **VERIFIED**. *"You can't quietly edit history."*
- **DENIED** → the red **"Try to auto-merge behavior"** button (bottom of the Human Gate panel). A full-screen **DENIED** stamp slams in. *"Even I can't force a behavior change through."*

---

## 5. Fallbacks (if something goes sideways)

| If… | Do this |
|---|---|
| Animations look instant/jumpy | reduce-motion is ON — turn it off, refresh. Or just narrate the end states. |
| You clicked too far / state looks messy | **Hard-refresh** (`Ctrl+Shift+R`) — 2 seconds, fully resets. |
| PLAY DEMO already running and you want control | press **Esc** to clear overlays, then drive manually: click a red feed row → Evidence; press the DENY button; open ledger via the **CHAIN INTEGRITY** chip. |
| Board won't load at all | show the **README** `tp-demo.png` + `tp-board.png` and talk to them; run `npx playwright test` in `dashboard/` to prove it's real (3 green). |
| Judge asks "is this live data?" | Be honest: the **two coded agents are published to Automation Cloud**; the **Python core is real and TDD'd (83 tests)**; the dashboard renders a **deterministic synthetic fleet** so the demo is reproducible — going live is one `fetch()` swap. |

---

## 6. If you're *recording* (not presenting live)

- Use **▶ PLAY DEMO** end-to-end for a clean, narrated capture (the teleprompter does the explaining).
- After it lands on the ledger, do **TAMPER**, then **DENIED**.
- Record at 1080p, fullscreen, reduce-motion OFF. One take ≈ 75–90s of footage; add your voiceover from `DEMO-SCRIPT.md`.

---

## 7. Judge Q&A cheat-sheet (crisp answers)

- **"How does it know behavioral vs. flaky vs. mechanical?"** → by *which evaluator class* failed: deterministic exact/JSON = mechanical; passes-on-retry = flaky; LLM-judge faithfulness / trajectory failing *consistently* = behavioral. A severity-priority router; the fixer **refuses** anything non-mechanical (two independent checks, in code).
- **"What's the coding-agent bonus?"** → *build-time*: Claude Code via `uip skills install --agent claude` authored the agents **test-first** and drives `uip pack`/`publish`. That's separate from the *runtime* LLM (the fixer's root-cause via the AI Trust Layer).
- **"Is the governance real or a gimmick?"** → it's enforced in code + provable: the hash-chained ledger is tamper-evident (show TAMPER) and exportable for audit.
- **"Why is this different from self-healing tests?"** → self-healing selectors is a commodity. TestPilot's moat is **governing behavioral regressions** — the failure that looks green — with a **refusal policy** and a **cryptographic audit trail**.
- **"What UiPath products?"** → Maestro, Coded Agents on serverless, Agent Evaluations, Integration Service (GitHub + Slack), Action Center, AI Trust Layer LLM Gateway.

---

_One-line soul to land every time: **"A behavioral change in an agent is a product decision, not a bug fix — only a human merges behavior."**_
