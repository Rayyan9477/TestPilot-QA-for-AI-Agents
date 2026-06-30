"""Generate a realistic, DETERMINISTIC synthetic dataset for the TestPilot UI — a fleet of
monitored AI agents with eval history, trust trends, and triage incidents. Superset shape so
any UI direction can use it. Writes dashboard/fleet.json. (No real data; demo-reproducible.)
"""
import datetime
import json
import pathlib
import random

ROOT = pathlib.Path(__file__).resolve().parent.parent
rng = random.Random(7)
NOW = datetime.datetime(2026, 6, 30, 12, 0, 0)

AGENTS = [
    ("agent-claims-triage", "Claims Triage Agent", "Coded · Maestro", "Revenue Cycle", 92, "healthy"),
    ("agent-prior-auth", "Prior-Auth Assistant", "Agent Builder", "Revenue Cycle", 74, "watch"),
    ("agent-invoice-dispute", "Invoice Dispute Agent", "Coded · LangGraph", "Finance Ops", 61, "blocked"),
    ("agent-support-router", "Support Router", "Agent Builder", "Customer Care", 88, "healthy"),
    ("agent-contract-review", "Contract Review Agent", "Coded · LlamaIndex", "Legal", 79, "watch"),
    ("agent-onboarding", "HR Onboarding Agent", "Maestro Case", "People Ops", 95, "healthy"),
    ("agent-order-to-cash", "Order-to-Cash Agent", "Maestro BPMN", "Finance Ops", 84, "healthy"),
    ("agent-kyc", "KYC Verification Agent", "Coded · OpenAI", "Risk & Compliance", 67, "blocked"),
]
EVALS = ["deterministic_exact", "json_similarity", "semantic_similarity", "llm_judge_faithfulness", "trajectory"]


def trust_history(base, days=30):
    pts, v = [], base - rng.randint(2, 8)
    for d in range(days):
        v = max(35, min(99, v + rng.randint(-3, 4)))
        t = (NOW - datetime.timedelta(days=days - 1 - d)).strftime("%Y-%m-%d")
        pts.append({"t": t, "score": v})
    pts[-1]["score"] = base
    return pts


agents = []
for aid, name, typ, owner, trust, status in AGENTS:
    evaluators = {e: round(min(0.99, max(0.40, trust / 100 + rng.uniform(-0.08, 0.06))), 2) for e in EVALS}
    agents.append({"id": aid, "name": name, "type": typ, "owner": owner, "trustScore": trust,
                   "status": status, "trustHistory": trust_history(trust), "evaluators": evaluators})

# Three HERO incidents — match the real pipeline output exactly (the demo spine).
incidents = [
    {"id": "inc-001", "agentId": "agent-claims-triage", "agentName": "Claims Triage Agent", "case_id": "drift-01",
     "category": "MECHANICAL_DRIFT", "evaluator": "deterministic_exact", "score": 0, "action": "auto_heal",
     "summary": "Heal drifted locator in UiTests/CheckoutTest.cs", "status": "PR open · awaiting human approval",
     "detail": {"file": "UiTests/CheckoutTest.cs", "pr": "#42",
                "unified_diff": "--- a/UiTests/CheckoutTest.cs\n+++ b/UiTests/CheckoutTest.cs\n-            var submit = app.FindElement(\"btn-signin\");\n+            var submit = app.FindElement(\"btn-login\");"},
     "ts": (NOW - datetime.timedelta(minutes=8)).isoformat()},
    {"id": "inc-002", "agentId": "agent-support-router", "agentName": "Support Router", "case_id": "flaky-01",
     "category": "FLAKY", "evaluator": "semantic_similarity", "score": 88, "action": "quarantine",
     "summary": "Quarantined — passed on retry (non-deterministic)", "status": "quarantined",
     "detail": {"retry_policy": {"max_retries": 2, "backoff": "exponential"}},
     "ts": (NOW - datetime.timedelta(minutes=22)).isoformat()},
    {"id": "inc-003", "agentId": "agent-invoice-dispute", "agentName": "Invoice Dispute Agent", "case_id": "regr-01",
     "category": "BEHAVIORAL_REGRESSION", "evaluator": "llm_judge_faithfulness", "score": 41, "action": "escalate",
     "summary": "Behavioral regression: Faithfulness 100 → 41 — RELEASE BLOCKED", "status": "escalated · human review",
     "detail": {"trajectory_diff": "step 3: expected lookup_policy, got summarize",
                "expected": "Cited policy LCD-12345 before answering",
                "actual": "Answered without citing any policy",
                "slack_text": "Behavioral regression in Invoice Dispute Agent - a behavioral change in an agent is a product decision, not a bug fix. Score 41."},
     "ts": (NOW - datetime.timedelta(minutes=3)).isoformat()},
]

cats = ["MECHANICAL_DRIFT", "FLAKY", "BEHAVIORAL_REGRESSION"]
act = {"MECHANICAL_DRIFT": "auto_heal", "FLAKY": "quarantine", "BEHAVIORAL_REGRESSION": "escalate"}
blurb = {"MECHANICAL_DRIFT": "Selector/schema drift auto-healed to a PR",
         "FLAKY": "Flaky eval quarantined with retry policy",
         "BEHAVIORAL_REGRESSION": "Behavioral regression escalated to a human"}
for i in range(16):
    a = rng.choice(AGENTS)
    c = rng.choice(cats)
    incidents.append({"id": f"inc-1{i:02d}", "agentId": a[0], "agentName": a[1], "case_id": f"case-{rng.randint(100, 999)}",
                      "category": c, "evaluator": rng.choice(EVALS), "score": rng.randint(0, 95), "action": act[c],
                      "summary": blurb[c], "status": "resolved", "detail": {},
                      "ts": (NOW - datetime.timedelta(hours=rng.randint(1, 72))).isoformat()})
incidents.sort(key=lambda x: x["ts"], reverse=True)

fleet = {"agents": len(AGENTS), "monitored": len(AGENTS), "autoHealRate": 0.78, "mttrMinutes": 6.2,
         "escalations7d": 4, "blockedReleases7d": 2, "prsOpened7d": 11, "evalsRun7d": 1284}
data = {"generatedFor": "TestPilot — agent QA fleet", "now": NOW.isoformat(),
        "fleet": fleet, "agents": agents, "incidents": incidents}

out = ROOT / "dashboard" / "fleet.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(data, indent=2), encoding="utf-8")
print("wrote", out.name, "| agents:", len(agents), "| incidents:", len(incidents))
