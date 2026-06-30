# TestPilot — Cloud Execution Runbook (S8–S12)
### The exact, ordered steps to run once your Agentic-trial tenant is live. Pairs with [SYSTEM-DESIGN.md](SYSTEM-DESIGN.md) (§14 binding) + [EXECUTION-PLAN.md](EXECUTION-PLAN.md).

> Everything offline is already done and validated: 76 tests green, both coded agents `uipath pack`-ed, triage proven to **execute under the real uipath runtime**. This runbook covers only the tenant-gated work.

Legend: `VERIFY` = confirm the exact UI label/flag on your tenant (versions drift).

---

## S0 prerequisites (do these first)
- [ ] Agentic trial provisioned; **Maestro, coded-agents-on-serverless, Agent Evaluations, Integration Service, Action Center, Test Manager** all enabled.
- [ ] **External Application** (confidential) registered with scopes: `OR.Folders OR.Execution TM.Projects TM.TestSets TM.TestExecutions`. Save ClientId/Secret to a **Credential Asset** (not the repo).
- [ ] A **fine-grained GitHub token** (single repo, contents + pull-requests write) stored as a Credential Asset / `GITHUB_TOKEN`.
- [ ] An unattended runtime / machine template exists in the target folder.

---

## S9 — Publish the two coded agents  *(fastest step; packaging already proven)*
```bash
uipath auth                                   # interactive; opens browser, writes .env token
python scripts/build_agents.py                # vendor testpilot + uipath init (regenerates entry-points.json)
cd agents/triage && uipath pack && uipath publish && cd ../..
cd agents/fixer  && uipath pack && uipath publish && cd ../..
```
- The entrypoint name is **`main`** (not `main.py`) — e.g. local test: `uipath run main -f input.json`.
- After publish, both agents appear in Orchestrator's package feed, selectable as Maestro **Service-task** agents.
- ✅ Verify: the published agent's `entry-points.json` matches the contract — already enforced by `tests/test_contract.py::test_real_generated_entrypoints_match_golden`.

---

## S8 — System-under-test agent + Agent Evaluations + seed
1. In **Studio Web**, build a tiny **SUT agent** (low-code Agent Builder) — any small agent with a tool call.
2. Attach an **Agent Evaluations** suite with evaluators spanning the classes: *Exact match* / *JSON similarity* (deterministic), *Semantic similarity*, *LLM-as-Judge (Faithfulness)* / *Trajectory*.
3. Seed a **mechanical drift** (rename a tool selector / output field) so a Deterministic evaluator fails reproducibly.
4. **Capture** the failing eval-result JSON → it must match the shape of `tests/fixtures/seed_all.json`. *(For a deterministic demo, you can drive triage straight from the seed file — the eval run is the "in production" framing.)*

---

## S10 — Maestro BPMN process (Studio Web)
Build: **Start → Triage (Service task) → Exclusive gateway → Branch A / B / C → 3 Ends.**

**Process variables** (all `String`; keep `classifications` a JSON string):
`evalResultsJson`, `classifications`, `primaryCategory`, `evalResultJson`, `repoUrl`, `fixBranch`, `sha`, `unifiedDiff`, `fileChanged`.

**Start:** `None`/manual (+ optional `Timer`). Set `evalResultsJson` default = the seeded JSON.

**Triage Service task** ("Start and wait for agent" → the published `testpilot-triage`). Map per [`tests/fixtures/maestro-mapping.json`](../tests/fixtures/maestro-mapping.json):
| Direction | Maestro var | Agent field |
|---|---|---|
| In | `evalResultsJson` | `eval_results_json` |
| Out | `classifications` | `classifications` |
| Out | `primaryCategory` | `primary_category` |

**Exclusive gateway** — JS-like expressions on `vars.<name>`, with an explicit **default flow → Error end** (`VERIFY` syntax):
- A: `vars.primaryCategory == "MECHANICAL_DRIFT"`
- B: `vars.primaryCategory == "FLAKY"`
- C: `vars.primaryCategory == "BEHAVIORAL_REGRESSION"`
- default → **Error end** (fail loud)

> Demo tip: run one instance per single-case seed (`seed_drift.json`, `seed_flaky.json`, `seed_regr.json`) to light each branch deterministically; `seed_all.json` selects **BEHAVIORAL_REGRESSION** (release blocked).

---

## S11 — Branch actions  *(two ways; pick per branch)*
You can wire each action as a **Maestro connector/User task**, OR do it **in-agent via the UiPath SDK** (simpler — the SDK is already a dependency). Methods confirmed from the SDK:

**Branch A — Fixer agent → re-run → PR → approval**
- Fixer Service task (`testpilot-fixer`): In `evalResultJson`←case EvalResult JSON, `repoUrl`←repo; Out `fixBranch`/`sha`/`unifiedDiff`/`fileChanged`.
- Open the PR with `build_pr_cmd(...)` → `gh pr create --repo … --base main --head <fixBranch> …` (gh auth via `GITHUB_TOKEN`). *(Or the Integration Service GitHub "Create Pull Request" activity — `VERIFY` it's selectable in Maestro.)*
- Test-Manager re-run with `build_rerun_cmd(...)` (see S12).
- **Approval:** `sdk.tasks.create(title=…, data=…, app_name=<approve-PR Action App>)` **or** a Maestro User task backed by an Action App; read the decision via the `hitlTask` output.

**Branch C — escalate (never auto-fix)**
- `escalation_payload_builder.build_regression_summary(...)` → Action Center task: `sdk.tasks.create(title=summary.title, data={"body": summary.body_markdown}, app_name=<review-regression Action App>)`.
- Slack: `sdk.connections.invoke_activity(<Slack Send-Message>, connection_id, {"text": summary.slack_text})` **or** the Integration Service Slack activity.

**Branch B — quarantine**
- `escalation_payload_builder.build_quarantine_note(...)` → `sdk.queues.create_item({"Name":"flaky-quarantine", …})` (or an API workflow).

**Action Apps:** build two trivial ones in UiPath Apps — *approve-PR* and *review-regression* — and reference them by name. `VERIFY` the app keys.

---

## S12 — End-to-end + durability
1. Run the Maestro instance from the seed → triage classifies → gateway routes → branch action fires.
2. **Test-Manager re-run** (the red→green proof) — use the exact verified flags (`VERIFY` against `uipcli --help`):
   ```
   uipcli test run <orchUrl> <tenant> --projectKey <PK> --testsetkey <TS> \
     -i ./params.json -A <org> -I <clientId> -S $UIPATH_CLIENT_SECRET \
     --applicationScope "OR.Folders OR.Execution TM.Projects TM.TestSets TM.TestExecutions" \
     -o <folder> --out junit --result_path ./out
   ```
   (This is exactly what `git_pr_runner.build_rerun_cmd(...)` emits.) Confirm JUnit flips red→green; or show `tests/fixtures/junit_red.xml`→`junit_green.xml` alongside the CLI call (decoupled from live timing).
3. **Durability:** open the Maestro **Execution Trail**; demonstrate **pause / resume / retry-from-failed-task** on a live instance.

---

## Stage verification gates
- **S9 done:** both agents published; contract test passes against the real `entry-points.json`.
- **S10 done:** an instance runs from the seed and the gateway routes each single-case seed to its branch.
- **S11 done:** Branch A opens a real PR + an approval task; Branch C opens an Action Center task + a Slack message; Branch B writes a quarantine item.
- **S12 done (M3):** all three branches + the durability controls demonstrated on the tenant.

Then → **S13** real-LLM smoke (the `UiPathLLMGatewayClient` is ready — set the model via `uipath list-models`), record the demo (S14), finish the deck + submit (S15–S16). Run the [COMPLIANCE-CHECKLIST](COMPLIANCE-CHECKLIST.md) §G before submitting.
