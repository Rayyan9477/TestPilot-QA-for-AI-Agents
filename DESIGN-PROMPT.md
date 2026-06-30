# DESIGN PROMPT — TestPilot: Mission Control for Agent Trust

You are building a **self-contained, static, data-driven web app** (no backend) that is **beautiful, cinematic, animated, and Playwright-verifiable**, deployable to static hosting. It must visually tell a governance story for a **<5-minute hackathon demo video**. Build it as a single-page app: `index.html` + `app.js` (vanilla ES modules or Alpine via CDN — your choice, but no build step required) + `styles.css` + a `data/` folder of synthetic JSON. Use **CSS / SVG / Web Animations API** for all motion. Respect `prefers-reduced-motion`.

---

## 1. PRODUCT & BRAND SOUL (read this first — it is load-bearing)

**TestPilot is an on-call QA engineer FOR AI AGENTS.** It treats AI agents as software-under-test. It watches a **FLEET of ~24 production AI agents** stream UiPath Agent-Evaluation runs, and the instant one fails it **triages the failure into one of three GOVERNED lanes**:

- **MECHANICAL_DRIFT** — a tool selector / output-schema field changed; a *Deterministic* evaluator fails → **AUTO-HEAL** into a reviewable GitHub PR (never auto-merged).
- **FLAKY** — a behavioral-class evaluator passes on retry → **QUARANTINE** with a retry policy.
- **BEHAVIORAL_REGRESSION** — an LLM-as-Judge faithfulness / trajectory evaluator fails consistently → **NEVER auto-fixed**; **ESCALATE** to a human (Action Center + Slack) with an AI root-cause summary.

**THE BRAND SOUL — the single sentence the entire UI must dramatize:**
> **"A behavioral change in an agent is a product decision, not a bug fix — only a human merges behavior."**

The signature visual moment is a behavioral regression being **physically REFUSED** by the auto-fixer and handed to a human. Runs on UiPath: **Maestro BPMN orchestration + coded agents on serverless + Agent Evaluations + Integration Service (GitHub/Slack) + Action Center + AI Trust Layer (governed LLM Gateway).** Every one of those six products must appear as a **labeled, lit station** so judges can see platform depth.

**Positioning:** a 24/7 governed **mission-control / ops room** for an agent fleet — the feeling of standing in a NORAD/air-traffic control room watching a governed AI immune system work.

---

## 2. THE VISUAL SYSTEM (follow exactly — anti-generic is a hard requirement)

**Theme:** *Governed Ops Room* — dark, cinematic, instrument-grade mission control crossed with a flight black-box. The screen must feel **powered on** and **forensic**. NOT a generic SaaS dashboard.

**Palette (exact hex — use as CSS custom properties):**
| Token | Hex | Use |
|---|---|---|
| `--bg-base` | `#0A0E14` | page base |
| `--bg-panel-deep` | `#0D1117` | deep panels |
| `--panel-ink` | `#10172A` | instrument panels |
| `--panel-raised` | `#121826` | raised cards |
| `--hairline` | `#1E2E47` | 1px borders |
| `--grid-line` | `#15233B` | engineering grid overlay |
| `--text` | `#E8EEFC` | primary text |
| `--text-muted` | `#8AA0C0` | secondary |
| `--text-faint` | `#5A6E8C` | tertiary |
| `--heal` | `#3DF5A0` | AUTO-HEAL / pass / expected path |
| `--heal-blue` | `#3B82F6` | secondary heal accent |
| `--quarantine` | `#FFB638` | QUARANTINE |
| `--escalate` | `#FF4D5E` | ESCALATE / regression |
| `--alarm` | `#FF3B47` | the human-merge gate / DENIED only |
| `--trust` | `#22D3EE` | trust / telemetry / wires |
| `--hero-magenta` | `#FF3D9A` | **BAD MERGES PREVENTED metric ONLY** |
| `--verified` | `#39FF8C` | ledger "CHAIN VERIFIED" seal |

**Color discipline (enforced):** Color = signal, never decoration; glow luminance encodes status. `--hero-magenta` is used in **exactly one place** (the BAD MERGES PREVENTED KPI). `--alarm`/`--escalate` red is reserved for behavioral regression + the human gate so **red always means "a human must decide."** Trust gauges use a green→amber→red instrument gradient.

**Typography (Google Fonts — NO Inter / Roboto / Arial):**
- **Display:** `Space Grotesk` — big condensed headers, agent callsigns, KPI numerals, Trust Score; tight letter-spacing.
- **Mono:** `JetBrains Mono` — case IDs, unified diffs, ledger hashes, the live feed, all timestamps. The "instrument readout / flight-log" feel.
- **Body:** `Chivo` — supporting labels/body.
- **Numerals are tabular mono throughout.** Use mono liberally for all evidence/IDs/diffs.

**Background treatment:** near-black base with (1) a faint engineering grid overlay (`--grid-line`, low opacity); (2) subtle film-grain/noise; (3) a slow-drifting radial gradient mesh in deep teal/cyan; (4) a slow radar-sweep arc over the fleet grid + a faint scanline. A corner-bracket / registration-mark HUD motif frames key panels.

**Motion principles:** orchestrated, physics-based, high-craft — never decorative jitter.
- Packet flight along SVG bezier lanes with easing.
- **The firewall membrane SLAM is the signature beat** (heavy spring).
- Gauge needles overshoot + settle; KPI numbers count up; sparklines + SVG tracks draw in via `stroke-dashoffset`.
- Ledger blocks stamp in with a settle; the **DENIED stamp drops with a heavy spring + brief screen-shake**.
- Staggered reveals; camera push-in on the trajectory divergence step.
- **`prefers-reduced-motion` → all motion collapses to instant state changes** (the demo must still tell the full story).

**Layout system:** an **unexpected asymmetric command board**, NOT a 12-col card grid:
- slim **TOP KPI rail**
- **LEFT fleet rail** (~24 tiles)
- dominant **CENTER situation board** (Triage Firewall + Fleet Trust gauge + Evaluator Constellation)
- **RIGHT rail** (live feed top + Action Center inbox bottom)
- **BOTTOM transport** (On-Call Timeline + Replay Scrubber) docked above the **Platform Station Map**
- a persistent **bottom governance status bar** (CHAIN INTEGRITY VERIFIED · pending gates · fleet trust)
- Drawers slide over; modals overlay. Bento clusters for the SRE scoreboard.

---

## 3. SCREENS / SECTIONS (build every one)

1. **Cold-Open Boot Splash** — a 6-second "BOOTING MISSION CONTROL" sequence: the six UiPath stations power on one by one, the fleet grid fades up, the Fleet Trust gauge sweeps to value. Skippable; auto-dismisses. Doubles as the video intro.
2. **Top KPI Command Rail (persistent)** — count-up tiles: AGENTS MONITORED · CASES TRIAGED TODAY · AUTO-HEALS MERGED · **BAD MERGES PREVENTED (magenta)** · MTT-ESCALATE. Plus the LIVE/REPLAY toggle, the time-scrubber handle, a ⌘K hint, and the **▶ PLAY DEMO** button.
3. **Left Rail — Fleet Grid** — ~24 breathing agent trust-tiles (SVG trust-ring + sparkline + status chip: NOMINAL / DRIFTING / QUARANTINED / REGRESSION), a slow radar-sweep, status-band filter; click → Agent Detail Drawer.
4. **Center Situation Board (the star)** — the **Triage Firewall** lane-router, flanked by the giant **Fleet Trust Index** gauge and the **Evaluator Constellation**.
5. **Right Rail** — **Live Triage Feed** ticker (top, scrolling verdicts, click-to-replay) + **Action Center HITL inbox** (bottom, Approve / Request-changes + the **press-to-be-DENIED** control).
6. **Bottom Transport** — **On-Call Timeline + Replay Scrubber** (90 days) above the **Platform Station Map** (six lit UiPath stations).
7. **Agent Detail Drawer (slide-over)** — per-agent flight strip: Trust Score gauge + auditable breakdown, 90-day trust trend with incident bands, eval-case table, open PRs, quarantines, escalations, embedded trajectory-diff.
8. **Evidence Drawer (modal) = Triage Replay Theater** — scrubbable animated trajectory with expected-GREEN vs actual-RED fork at the divergence step, five evaluator instrument gauges, expected-vs-actual text, judge rationale + confidence, the governed decision + the exact policy that fired.
9. **PR Diff Theater (overlay)** — GitHub-style card: one-line unified diff typing in red→green, a JUnit red→green re-run badge, branch + CI checks, an **AWAITING HUMAN APPROVAL** gate (never auto-merged).
10. **Governance Ledger (full-width panel/tab)** — hash-chained append-only blocks (each showing its SHA linking to the prior block), a live **CHAIN INTEGRITY: VERIFIED** seal, a tamper-demo toggle that breaks the chain red, and JSON/CSV export.

---

## 4. HERO FEATURE — THE TRIAGE FIREWALL (build and polish this first)

The animated centerpiece. Failed eval **packets** enter from the left tagged with their failing evaluator (`deterministic_exact`, `json_similarity`, `semantic_similarity`, `llm_judge_faithfulness`, `trajectory`). They hit a central **GATEWAY** that X-rays the evaluator-class signature, then route into one of three lit SVG bezier lanes:

- **AUTO-HEAL (green):** packet zips into a CI lane; a JUnit build bar flips **red→green**; a **PR Diff Theater** card materializes and stamps OPEN (awaiting human).
- **QUARANTINE (amber):** a retry counter ticks; the second attempt goes green; the case slides into a holding bay with its retry-policy chip.
- **ESCALATE (red):** packet routes to the human lane; an Action Center task + Slack card materialize with an AI root-cause summary.

**THE MONEY SHOT:** a **BEHAVIORAL_REGRESSION** packet (`llm_judge_faithfulness`, consistent fail) accelerates toward the AUTO-HEAL lane — and a red **GOVERNANCE FIREWALL membrane SLAMS down and DEFLECTS it** (heavy spring + flash). On-board text fires: **"Behavior is a product decision, not a bug fix — auto-fix REFUSED."** The packet reroutes to ESCALATE, a new immutable ledger block records the refusal, and the **BAD MERGES PREVENTED** counter increments with a satisfying tick.

Clicking any packet freezes time and opens the **Evidence Drawer** (Triage Replay Theater).

---

## 5. SIGNATURE INTERACTION — PRESS-TO-BE-DENIED (the climax)

In the Action Center inbox, a red **"Try to auto-merge behavior"** button. When pressed, it triggers a **hard governance refusal**: the firewall flashes, a stamped **DENIED** overlay drops with screen-shake, and a new **ledger block** records the blocked attempt with the policy quote. It literalizes "only a human merges behavior" as a button you can watch **fail by design**. This is the demo's emotional peak — make it feel heavy and inevitable.

---

## 6. GOVERNANCE LEDGER (hash-chained, tamper-evident)

Append-only. Every governed decision is a block: `{ index, t, actor, action, case_id, prev_hash, hash }`, where `hash` is a deterministic SHA-style digest over the block fields **computed client-side** (so the tamper-demo can break and re-verify the chain). Actions include `REFUSED auto-fix`, `QUARANTINED`, `PR OPENED`, `HUMAN APPROVED`, `BLOCKED auto-merge attempt`. Show each block's `prev_hash → hash` link, a live **CHAIN INTEGRITY: VERIFIED** seal in `--verified`, a **tamper-demo toggle** that mutates one block and visibly breaks the chain red, and a JSON/CSV export. Style it like a forensic flight log in JetBrains Mono.

---

## 7. SYNTHETIC DATA MODEL (generate it; reproducible via a seeded PRNG)

Generate `data/fleet.json` + `incidents.json` + `ledger.json`. Field names below **must match** these shapes (they mirror the real backend contract — keep them byte-exact so the demo is credible):

```
Agent { id, callsign, team, oncall_owner, trust_score(0-100), trust_band(NOMINAL|DRIFTING|QUARANTINED|REGRESSION),
        trust_breakdown { faithfulness, determinism, trajectory_adherence, flake_rate, escalation_history },
        trust_trend [{ t, score }]  // 90 daily points,
        eval_pass_rate_sparkline [number], open_prs, quarantined_count, open_escalations }

EvalResult { case_id, evaluator_type(deterministic_exact|json_similarity|semantic_similarity|llm_judge_faithfulness|trajectory),
             evaluator_name, score(0-100), passed_on_retry(bool), retry_count, expected|null, actual|null,
             trajectory_diff|null }   // e.g. "step 3: expected lookup_policy, got summarize"

Classification { case_id, category(MECHANICAL_DRIFT|FLAKY|BEHAVIORAL_REGRESSION), reason, confidence(0..1) }

Incident { id, t, agent_id, case_id, evaluator_type, lane(auto_heal|quarantine|escalate), verdict, severity,
           replay { expected_path:[lookup_policy,retrieve,summarize,respond], actual_path:[...], divergence_index } }

FixProposal { case_id, file_path, old_line, new_line, unified_diff }   // exactly one '-' and one '+' content line
JUnitReport { tests, failures, cases:[{name,passed}] }
QuarantineNote { case_id, action:"quarantine", retry_policy { max_retries, backoff:"exponential" } }
RootCauseSummary { case_id, title, body_markdown, slack_text(<=4000), confidence, attribution:"via AI Trust Layer · keyless" }
LedgerBlock { index, t, actor, action, case_id, prev_hash, hash, verified }
FleetKPIs { agents_monitored, cases_triaged_today, auto_heals_merged, bad_merges_prevented, mtt_escalate,
            auto_heal_rate, escalation_rate, flake_rate }
PlatformStation { id, label, order, lit }   // labels: Agent Evals, Maestro, Fixer/Test Cloud, Integration Service, Action Center, AI Trust Layer
DemoScript [{ t_offset, action, caption, target_testid }]
```

**Seed the hero incident from this exact canon** (so the centerpiece matches the real pipeline):
- `drift-01` — MECHANICAL_DRIFT, file `UiTests/CheckoutTest.cs`, diff `app.FindElement("btn-signin")` → `app.FindElement("btn-login")`.
- `flaky-01` — FLAKY, quarantine, `retry_policy { max_retries: 2, backoff: "exponential" }`.
- `regr-01` — BEHAVIORAL_REGRESSION, evaluator Faithfulness (`llm_judge_faithfulness`), **score 41**, expected "Cited policy LCD-12345 before answering", actual "Answered without citing any policy", trajectory "**step 3: expected lookup_policy, got summarize**", slack/body quoting the brand line.

~24 agents with callsigns like Invoice-Extractor, Refund-Router, KYC-Screener, Support-Triage, Policy-RAG-Agent, Checkout-Agent, etc.

---

## 8. DEMO-ON-RAILS & NAVIGATION

- **▶ PLAY DEMO** runs a deterministic, captioned ~90-second autopilot over `DemoScript`, hands-free, hitting every beat: cold-open → fleet at cruise → alarm → firewall triages all three lanes → the **deflection + DENIED** → ledger block writes → return to green. Pausable.
- **Command Palette (⌘K)** — jump to any agent / incident / lane / ledger block, trigger Run-Triage or PLAY DEMO, filter the fleet.
- **LIVE/REPLAY toggle** — LIVE drips new synthetic verdicts in on a timer; REPLAY drives everything deterministically from the scrubber.
- **On-Call Timeline scrubber** — scrub the 90-day timeline; the whole board animates to that moment (rewind to "the day Refund-Router regressed").

---

## 9. ACCEPTANCE CRITERIA (the build is done when ALL hold)

1. App loads as a single static page with **no backend**, all data from local JSON; deployable to static hosting as-is.
2. Fonts are **Space Grotesk / JetBrains Mono / Chivo** — **no Inter/Roboto/Arial anywhere**. The exact palette above is used; `--hero-magenta` appears **only** on BAD MERGES PREVENTED.
3. The **Triage Firewall** animates packets through all three lanes, and the **BEHAVIORAL_REGRESSION deflection** visibly slams the membrane, fires the policy text, reroutes to ESCALATE, and **increments BAD MERGES PREVENTED**.
4. The **press-to-be-DENIED** button drops a DENIED stamp and **writes a new ledger block**; the ledger **chain verifies** (and the tamper-demo visibly breaks it red).
5. All **six UiPath stations** are labeled and light up as packets traverse.
6. Clicking any packet/feed line opens the **Evidence Drawer** with the GREEN-vs-RED trajectory fork and evaluator gauges.
7. **▶ PLAY DEMO** runs the full sequence hands-free and deterministically; the Command Palette (⌘K) works.
8. Every interactive element + demo beat has a **stable `data-testid`**; a Playwright smoke test can run PLAY DEMO and assert the deflection counter, the DENIED ledger block, and chain verification.
9. **`prefers-reduced-motion`** collapses all motion to instant state changes while preserving the full story.
10. The whole thing is **memorable in one glance** as a governed agent-trust command center, and narratable in **under 5 minutes**.

Make it bold, distinctive, atmospheric, and cinematic. Ship the most ambitious version you can while keeping it a clean single-page static app.