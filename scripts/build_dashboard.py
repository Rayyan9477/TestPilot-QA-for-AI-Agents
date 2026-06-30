"""Render a self-contained TestPilot dashboard (dashboard/index.html) from the live pipeline
output — a demo visual and a Playwright-verifiable surface. Data is embedded (no fetch), so it
opens straight from the filesystem.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from testpilot.pipeline import route_failures  # noqa: E402


class _SeedHealLLM:
    def complete(self, prompt: str) -> str:
        cur = prompt.split("Current line:\n", 1)[1].split("\nReturn the corrected", 1)[0]
        m = re.search(r"The value '(.+?)' should be '(.+?)'", prompt)
        return cur.replace(m.group(1), m.group(2)) if m else cur


res = route_failures(
    (ROOT / "tests/fixtures/seed_all.json").read_text(),
    ROOT / "tests/fixtures/sample_repo",
    _SeedHealLLM(),
)
data = {"primary_category": res.primary_category, "actions": [a.__dict__ for a in res.actions]}

TEMPLATE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>TestPilot — on-call QA for AI agents</title>
<style>
  :root { --bg:#0b0f17; --panel:#121826; --line:#1f2a3d; --muted:#8aa0c0; --text:#e8eefc;
          --heal:#3b82f6; --quar:#f59e0b; --esc:#ef4444; }
  * { box-sizing:border-box; }
  body { margin:0; background:radial-gradient(1200px 600px at 70% -10%, #16203a 0%, var(--bg) 60%);
         color:var(--text); font:15px/1.5 ui-sans-serif,system-ui,Segoe UI,Roboto,Arial; }
  .wrap { max-width:1080px; margin:0 auto; padding:40px 24px 64px; }
  header h1 { margin:0; font-size:26px; letter-spacing:.2px; }
  header p { margin:6px 0 0; color:var(--muted); }
  .verdict { margin:28px 0; padding:18px 22px; border-radius:14px; border:1px solid var(--line);
             display:flex; align-items:center; gap:14px; background:var(--panel); }
  .verdict.blocked { border-color:#5b1c1c; background:linear-gradient(180deg,#1a1012,#121826); }
  .dot { width:12px; height:12px; border-radius:50%; box-shadow:0 0 0 4px rgba(239,68,68,.15); }
  .verdict .label { font-size:13px; color:var(--muted); text-transform:uppercase; letter-spacing:1px; }
  .verdict .val { font-size:20px; font-weight:700; }
  .verdict .tag { margin-left:auto; font-size:13px; color:#fca5a5; border:1px solid #5b1c1c;
                  padding:6px 12px; border-radius:999px; }
  .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(300px,1fr)); gap:16px; }
  .card { background:var(--panel); border:1px solid var(--line); border-left-width:4px;
          border-radius:14px; padding:18px; }
  .card.auto_heal { border-left-color:var(--heal); }
  .card.quarantine { border-left-color:var(--quar); }
  .card.escalate { border-left-color:var(--esc); }
  .card .top { display:flex; align-items:center; justify-content:space-between; gap:10px; }
  .badge { font-size:11px; font-weight:700; letter-spacing:.6px; text-transform:uppercase;
           padding:4px 9px; border-radius:7px; }
  .auto_heal .badge { background:rgba(59,130,246,.16); color:#93c5fd; }
  .quarantine .badge { background:rgba(245,158,11,.16); color:#fcd34d; }
  .escalate .badge { background:rgba(239,68,68,.16); color:#fca5a5; }
  .case { font-family:ui-monospace,Consolas,monospace; color:var(--muted); font-size:13px; }
  .summary { margin:12px 0 8px; font-weight:600; }
  pre { background:#0a0e17; border:1px solid var(--line); border-radius:10px; padding:12px;
        overflow:auto; font:12.5px/1.5 ui-monospace,Consolas,monospace; margin:8px 0 0; }
  pre .del { color:#fca5a5; } pre .add { color:#86efac; }
  .kv { color:var(--muted); font-size:13px; margin-top:8px; }
  footer { margin-top:34px; color:var(--muted); font-size:13px; border-top:1px solid var(--line); padding-top:16px; }
</style>
</head>
<body>
<div class="wrap">
  <header>
    <h1>TestPilot &mdash; the on-call QA engineer for AI agents</h1>
    <p>A failed Agent&nbsp;Evaluation run, triaged into governed actions. Never auto-fixes behavior.</p>
  </header>
  <div id="verdict" class="verdict"></div>
  <div id="grid" class="grid"></div>
  <footer>UiPath AgentHack &middot; Track&nbsp;3 &middot; Maestro orchestration &middot; coded agents on Automation Cloud &middot; governed by the AI&nbsp;Trust&nbsp;Layer</footer>
</div>
<script>
const DATA = __DATA__;
const esc = s => String(s).replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
function diffHtml(d){ return esc(d).split('\n').map(l =>
  l.startsWith('+')&&!l.startsWith('+++') ? '<span class="add">'+l+'</span>' :
  l.startsWith('-')&&!l.startsWith('---') ? '<span class="del">'+l+'</span>' : l).join('\n'); }

const v = document.getElementById('verdict');
const blocked = DATA.primary_category === 'BEHAVIORAL_REGRESSION';
v.className = 'verdict' + (blocked ? ' blocked' : '');
v.innerHTML = '<span class="dot" style="background:'+(blocked?'#ef4444':'#3b82f6')+'"></span>'
  + '<div><div class="label">Build verdict</div><div class="val" id="verdict-val">'+esc(DATA.primary_category)+'</div></div>'
  + (blocked ? '<span class="tag">RELEASE BLOCKED &middot; human must merge behavior</span>' : '');

const labels = {auto_heal:'Auto-heal &rarr; PR', quarantine:'Quarantine', escalate:'Escalate to human'};
document.getElementById('grid').innerHTML = DATA.actions.map(a => {
  let body = '';
  if (a.action === 'auto_heal') body = '<pre>'+diffHtml(a.detail.unified_diff)+'</pre>';
  else if (a.action === 'quarantine') body = '<div class="kv">retry policy: '+esc(JSON.stringify(a.detail.retry_policy))+'</div>';
  else if (a.action === 'escalate') body = '<pre>'+esc(a.detail.slack_text)+'</pre>';
  return '<div class="card '+a.action+'"><div class="top"><span class="badge">'+(labels[a.action]||a.action)
    + '</span><span class="case">'+esc(a.case_id)+'</span></div>'
    + '<div class="summary">'+esc(a.summary)+'</div>'
    + '<div class="case">'+esc(a.category)+'</div>' + body + '</div>';
}).join('');
</script>
</body>
</html>
"""

out = ROOT / "dashboard"
out.mkdir(exist_ok=True)
(out / "results.json").write_text(json.dumps(data, indent=2), encoding="utf-8")
(out / "index.html").write_text(TEMPLATE.replace("__DATA__", json.dumps(data)), encoding="utf-8")
print("dashboard written ->", (out / "index.html"))
print("verdict:", data["primary_category"], "| actions:", [a["action"] for a in data["actions"]])
