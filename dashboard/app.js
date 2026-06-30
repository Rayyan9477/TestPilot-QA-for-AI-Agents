// TestPilot — Mission Control for Agent Trust. Self-contained, data-driven, no backend.
const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const SVGNS = "http://www.w3.org/2000/svg";
const reduced = matchMedia("(prefers-reduced-motion: reduce)").matches;
const el = (t, a = {}, ...kids) => { const n = document.createElement(t); for (const k in a) (k === "class") ? n.className = a[k] : (k.startsWith("data") || k === "title") ? n.setAttribute(k, a[k]) : n[k] = a[k]; kids.flat().forEach(c => n.append(c.nodeType ? c : document.createTextNode(c))); return n; };
const S = (t, a = {}) => { const n = document.createElementNS(SVGNS, t); for (const k in a) n.setAttribute(k, a[k]); return n; };
const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
const wait = ms => new Promise(r => setTimeout(r, reduced ? 0 : ms));

// seeded PRNG (mulberry32)
function rng(seed) { return () => { seed |= 0; seed = seed + 0x6D2B79F5 | 0; let t = Math.imul(seed ^ seed >>> 15, 1 | seed); t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; }; }
const R = rng(7);
const pick = a => a[Math.floor(R() * a.length)];

// deterministic SHA-style hash (cyrb53 → 16 hex)
function hash(str) { let h1 = 0xdeadbeef, h2 = 0x41c6ce57; for (let i = 0; i < str.length; i++) { const ch = str.charCodeAt(i); h1 = Math.imul(h1 ^ ch, 2654435761); h2 = Math.imul(h2 ^ ch, 1597334677); } h1 = Math.imul(h1 ^ h1 >>> 16, 2246822507) ^ Math.imul(h2 ^ h2 >>> 13, 3266489909); h2 = Math.imul(h2 ^ h2 >>> 16, 2246822507) ^ Math.imul(h1 ^ h1 >>> 13, 3266489909); return (h2 >>> 0).toString(16).padStart(8, "0") + (h1 >>> 0).toString(16).padStart(8, "0"); }

// ---------- DATA ----------
const CALLSIGNS = ["Claims-Triage", "Refund-Router", "KYC-Screener", "Support-Triage", "Invoice-Dispute", "Policy-RAG", "Checkout-Agent", "Onboarding", "Order-to-Cash", "Contract-Review", "Fraud-Watch", "Prior-Auth", "Dispatch", "Renewals", "Underwriting", "Collections", "Eligibility", "Appeals", "Intake-Bot", "Reconciler", "Pricing", "Sentiment", "Routing", "Forecaster"];
const EVALS = ["deterministic_exact", "json_similarity", "semantic_similarity", "llm_judge_faithfulness", "trajectory"];
const EVAL_SHORT = { deterministic_exact: "exact", json_similarity: "json-sim", semantic_similarity: "semantic", llm_judge_faithfulness: "faithful", trajectory: "trajectory" };
const bandOf = t => t >= 85 ? "NOMINAL" : t >= 70 ? "DRIFTING" : t >= 55 ? "QUARANTINED" : "REGRESSION";
const trend = base => { let v = clamp(base - 4 - Math.floor(R() * 6), 35, 99); return Array.from({ length: 90 }, (_, i) => { v = clamp(v + Math.floor(R() * 7) - 3, 35, 99); return { t: i, score: i === 89 ? base : v }; }); };

const agents = CALLSIGNS.map((cs, i) => { const trust = clamp(Math.round(62 + R() * 36 - (i % 5 === 2 ? 22 : 0)), 48, 98); return { id: "a" + i, callsign: cs, owner: "@" + ["mira", "dev", "sam", "lee", "ana", "kai"][i % 6], trust, band: bandOf(trust), breakdown: { faithfulness: clamp(trust + 4 - Math.floor(R() * 12), 30, 99), determinism: clamp(trust + 8 - Math.floor(R() * 10), 30, 99), trajectory: clamp(trust - Math.floor(R() * 14), 30, 99), flake: Math.floor(R() * 22), escalation: Math.floor(R() * 6) }, trend: trend(trust), spark: Array.from({ length: 16 }, () => 60 + Math.floor(R() * 40)) }; });
const A = name => agents.find(a => a.callsign === name) || agents[0];

// canonical hero incidents (match the real backend)
const HERO = {
  drift: { id: "inc-001", agent: "Claims-Triage", case_id: "drift-01", category: "MECHANICAL_DRIFT", lane: "auto_heal", evaluator: "deterministic_exact", score: 0, file: "UiTests/CheckoutTest.cs", old_line: '            var submit = app.FindElement("btn-signin");', new_line: '            var submit = app.FindElement("btn-login");', pr: "#42" },
  flaky: { id: "inc-002", agent: "Support-Triage", case_id: "flaky-01", category: "FLAKY", lane: "quarantine", evaluator: "semantic_similarity", score: 88, retry: { max_retries: 2, backoff: "exponential" } },
  regr: { id: "inc-003", agent: "Invoice-Dispute", case_id: "regr-01", category: "BEHAVIORAL_REGRESSION", lane: "escalate", evaluator: "llm_judge_faithfulness", score: 41, expected: "Cited policy LCD-12345 before answering", actual: "Answered without citing any policy", trajectory_diff: "step 3: expected lookup_policy, got summarize", expected_path: ["lookup_policy", "retrieve", "cite", "respond"], actual_path: ["retrieve", "summarize", "respond"], divergence: 1, rca: "Faithfulness dropped 100 → 41. The agent now answers refund questions WITHOUT first calling lookup_policy — it asserts a policy window not present in LCD-12345. This is a behavioral change, not a broken selector. Recommendation: a human reviews; auto-fix refused." }
};
const LANES = { MECHANICAL_DRIFT: "auto_heal", FLAKY: "quarantine", BEHAVIORAL_REGRESSION: "escalate" };

const incidents = [];
let day = 89, idc = 100;
[HERO.regr, HERO.drift, HERO.flaky].forEach((h, i) => incidents.push({ ...h, day: 89, mins: [3, 8, 22][i] }));
for (let i = 0; i < 60; i++) { const cat = pick(["MECHANICAL_DRIFT", "MECHANICAL_DRIFT", "FLAKY", "BEHAVIORAL_REGRESSION"]); incidents.push({ id: "inc-1" + i, agent: pick(CALLSIGNS), case_id: "case-" + (idc++), category: cat, lane: LANES[cat], evaluator: pick(EVALS), score: Math.floor(R() * 95), day: Math.floor(R() * 90) }); }

const kpis = { agents_monitored: agents.length, cases_triaged_today: 1284, auto_heals_merged: 207, bad_merges_prevented: 18, mtt_escalate: "2m41s" };
const STATIONS = ["Agent Evals", "Maestro", "Fixer / Test Cloud", "Integration Service", "Action Center", "AI Trust Layer"];

// ---------- LEDGER (hash-chained) ----------
let ledger = [];
function addBlock(actor, action, case_id, cls = "") {
  const prev = ledger.length ? ledger[ledger.length - 1].hash : "0".repeat(16);
  const idx = ledger.length;
  const t = "T+" + String(idx).padStart(3, "0");
  const h = hash(idx + actor + action + case_id + prev);
  ledger.push({ index: idx, t, actor, action, case_id, prev_hash: prev, hash: h, cls, verified: true });
  renderLedger(); flashStatus();
}
function verifyChain() { for (let i = 0; i < ledger.length; i++) { const b = ledger[i]; const prev = i ? ledger[i - 1].hash : "0".repeat(16); if (b.prev_hash !== prev || b.hash !== hash(b.index + b.actor + b.action + b.case_id + prev) || b.tampered) return false; } return true; }
["PR OPENED", "QUARANTINED", "REFUSED auto-fix", "HUMAN APPROVED"].forEach((a, i) => addBlock(i === 2 ? "TestPilot" : i === 3 ? "@mira" : "TestPilot", a, ["drift-01", "flaky-01", "regr-01", "drift-00"][i], a.includes("REFUSED") ? "refuse" : a.includes("APPROVED") ? "approve" : ""));

// ---------- RENDER ----------
function ring(score, sz = 46) { const g = S("svg", { width: sz, height: sz, viewBox: "0 0 46 46", class: "ring" }); const c = score >= 85 ? "var(--heal)" : score >= 70 ? "var(--quarantine)" : "var(--escalate)"; const circ = 2 * Math.PI * 19; g.append(S("circle", { cx: 23, cy: 23, r: 19, fill: "none", stroke: "var(--hairline)", "stroke-width": 4 })); const p = S("circle", { cx: 23, cy: 23, r: 19, fill: "none", stroke: c, "stroke-width": 4, "stroke-linecap": "round", "stroke-dasharray": circ, "stroke-dashoffset": circ * (1 - score / 100), transform: "rotate(-90 23 23)" }); g.append(p); const tx = S("text", { x: 23, y: 27, "text-anchor": "middle", fill: "var(--text)", "font-size": 13, "font-family": "var(--disp)", "font-weight": 700 }); tx.textContent = score; g.append(tx); return g; }

function renderKPIs() {
  $("#kpis").innerHTML = "";
  const tiles = [["AGENTS MONITORED", kpis.agents_monitored, "live"], ["CASES TRIAGED · TODAY", kpis.cases_triaged_today.toLocaleString(), ""], ["AUTO-HEALS MERGED", kpis.auto_heals_merged, "via PR"], ["BAD MERGES PREVENTED", kpis.bad_merges_prevented, "governance", "hero", "bad_merges"], ["MEAN TIME-TO-ESCALATE", kpis.mtt_escalate, ""]];
  tiles.forEach(([l, v, s, cls, key]) => { const t = el("div", { class: "kpi " + (cls || "") }, el("div", { class: "k-l" }, l), el("div", { class: "k-v num" }, "" + v), el("div", { class: "k-s" }, s || "")); if (key) t.querySelector(".k-v").dataset.kpi = key; $("#kpis").append(t); });
}
function bumpBadMerges() { kpis.bad_merges_prevented++; const n = $('[data-kpi="bad_merges"]'); if (!n) return; n.textContent = kpis.bad_merges_prevented; n.animate([{ transform: "scale(1.5)", filter: "brightness(2)" }, { transform: "scale(1)" }], { duration: 500, easing: "cubic-bezier(.2,1.5,.4,1)" }); }

function renderFleet(filter = "ALL") {
  const g = $("#fleetGrid"); g.innerHTML = "";
  agents.filter(a => filter === "ALL" || a.band === filter).forEach(a => {
    const tile = el("div", { class: "tile", "data-testid": "tile-" + a.id, title: a.callsign + " · trust " + a.trust });
    tile.append(ring(a.trust), el("div", { class: "cs mono" }, a.callsign), el("div", { class: "chip " + a.band }, a.band));
    tile.onclick = () => openAgent(a); g.append(tile);
  });
  const filt = $("#fleetFilters"); if (!filt.children.length) ["ALL", "DRIFTING", "REGRESSION"].forEach(f => { const b = el("button", { class: f === "ALL" ? "on" : "" }, f === "ALL" ? "ALL" : f === "DRIFTING" ? "DRIFT" : "REGR"); b.onclick = () => { $$("#fleetFilters button").forEach(x => x.classList.remove("on")); b.classList.add("on"); renderFleet(f); }; filt.append(b); });
}

function renderTrustGauge(val) {
  const sv = $("#trustGauge"); sv.innerHTML = ""; const cx = 110, cy = 116, r = 92;
  const arc = (a0, a1, color, w) => { const p = (a) => [cx + r * Math.cos(a), cy + r * Math.sin(a)]; const [x0, y0] = p(a0), [x1, y1] = p(a1); return S("path", { d: `M${x0} ${y0} A${r} ${r} 0 0 1 ${x1} ${y1}`, fill: "none", stroke: color, "stroke-width": w, "stroke-linecap": "round" }); };
  sv.append(arc(Math.PI, Math.PI * 1.33, "var(--escalate)", 8), arc(Math.PI * 1.33, Math.PI * 1.66, "var(--quarantine)", 8), arc(Math.PI * 1.66, Math.PI * 2, "var(--heal)", 8));
  const a = Math.PI + (val / 100) * Math.PI; const nx = cx + (r - 14) * Math.cos(a), ny = cy + (r - 14) * Math.sin(a);
  const needle = S("line", { x1: cx, y1: cy, x2: cx, y2: cy - 6, stroke: "var(--trust)", "stroke-width": 3, "stroke-linecap": "round" }); sv.append(needle, S("circle", { cx, cy, r: 5, fill: "var(--trust)" }));
  if (!reduced) needle.animate([{ x2: cx, y2: cy - 6 }, { x2: nx, y2: ny }], { duration: 1100, easing: "cubic-bezier(.2,1.5,.3,1)", fill: "forwards" }); else needle.setAttribute("x2", nx), needle.setAttribute("y2", ny);
  $("#trustVal").textContent = val; $("#sbTrust").textContent = val; $("#trustBand").textContent = bandOf(val);
}
function renderTrend() {
  const sv = $("#trustTrend"); sv.innerHTML = ""; const fleetTrend = agents[0].trend.map((p, i) => ({ x: i, y: Math.round(agents.reduce((s, a) => s + a.trend[i].score, 0) / agents.length) }));
  const W = 260, H = 44, max = 100, min = 40; const X = i => (i / 89) * W, Y = v => H - 4 - ((v - min) / (max - min)) * (H - 8);
  let d = fleetTrend.map((p, i) => (i ? "L" : "M") + X(i).toFixed(1) + " " + Y(p.y).toFixed(1)).join(" ");
  const path = S("path", { d, fill: "none", stroke: "var(--trust)", "stroke-width": 1.6 }); sv.append(S("path", { d: d + ` L${W} ${H} L0 ${H} Z`, fill: "rgba(34,211,238,.08)", stroke: "none" }), path);
  const dipI = 64; sv.append(S("circle", { cx: X(dipI), cy: Y(fleetTrend[dipI].y), r: 3, fill: "var(--escalate)" }));
  if (!reduced) { const len = path.getTotalLength(); path.style.strokeDasharray = len; path.animate([{ strokeDashoffset: len }, { strokeDashoffset: 0 }], { duration: 1400, fill: "forwards" }); }
}
function renderConstellation() {
  const sv = $("#constellation"); sv.innerHTML = ""; const cx = 100, cy = 88;
  const vol = { deterministic_exact: 38, json_similarity: 22, semantic_similarity: 30, llm_judge_faithfulness: 19, trajectory: 14 };
  const laneColor = { deterministic_exact: "var(--heal)", json_similarity: "var(--heal)", semantic_similarity: "var(--quarantine)", llm_judge_faithfulness: "var(--escalate)", trajectory: "var(--escalate)" };
  EVALS.forEach((e, i) => { const a = (i / EVALS.length) * Math.PI * 2 - Math.PI / 2; const x = cx + 64 * Math.cos(a), y = cy + 58 * Math.sin(a); sv.append(S("line", { x1: cx, y1: cy, x2: x, y2: y, stroke: "var(--hairline)", "stroke-width": 1 })); const node = S("circle", { cx: x, cy: y, r: 6 + vol[e] / 6, fill: laneColor[e], opacity: .85 }); node.style.filter = "drop-shadow(0 0 5px " + laneColor[e] + ")"; sv.append(node); const tx = S("text", { x, y: y + 18, "text-anchor": "middle", fill: "var(--text-faint)", "font-size": 7, "font-family": "var(--mono)" }); tx.textContent = EVAL_SHORT[e]; sv.append(tx); });
  sv.append(S("circle", { cx, cy, r: 16, fill: "none", stroke: "var(--trust)", "stroke-width": 1, opacity: .5 })); const c = S("text", { x: cx, y: cy + 3, "text-anchor": "middle", fill: "var(--trust)", "font-size": 8, "font-family": "var(--mono)" }); c.textContent = "ROUTER"; sv.append(c);
}

// firewall scaffold
const FW = { entry: [60, 180], gate: [300, 180], heal: [600, 74], quar: [600, 180], esc: [600, 286] };
function renderFirewall() {
  const sv = $("#firewall"); sv.innerHTML = "";
  const lane = (to, color, label) => { sv.append(S("path", { d: `M${FW.gate[0]} ${FW.gate[1]} C420 ${FW.gate[1]} 460 ${to[1]} ${to[0]} ${to[1]}`, fill: "none", stroke: color, "stroke-width": 2, opacity: .35 })); const bay = S("rect", { x: to[0] - 6, y: to[1] - 16, width: 34, height: 32, rx: 6, fill: "rgba(255,255,255,.02)", stroke: color, "stroke-width": 1, opacity: .6 }); sv.append(bay); const tx = S("text", { x: to[0] + 11, y: to[1] + 3, "text-anchor": "middle", fill: color, "font-size": 8, "font-family": "var(--mono)" }); tx.textContent = label; sv.append(tx); };
  // entry rail
  sv.append(S("line", { x1: 20, y1: FW.gate[1], x2: FW.gate[0], y2: FW.gate[1], stroke: "var(--hairline)", "stroke-width": 2 }));
  lane(FW.heal, "var(--heal)", "PR"); lane(FW.quar, "var(--quarantine)", "Q"); lane(FW.esc, "var(--escalate)", "ESC");
  // gateway
  const gp = `M${FW.gate[0]} ${FW.gate[1] - 30} L${FW.gate[0] + 30} ${FW.gate[1]} L${FW.gate[0]} ${FW.gate[1] + 30} L${FW.gate[0] - 30} ${FW.gate[1]} Z`;
  sv.append(S("path", { d: gp, fill: "rgba(34,211,238,.08)", stroke: "var(--trust)", "stroke-width": 1.5 }));
  const gt = S("text", { x: FW.gate[0], y: FW.gate[1] + 3, "text-anchor": "middle", fill: "var(--trust)", "font-size": 7.5, "font-family": "var(--mono)" }); gt.textContent = "ROUTER"; sv.append(gt);
  // membrane (between gate and heal lane)
  const mem = S("rect", { x: 402, y: 48, width: 8, height: 160, rx: 4, fill: "var(--escalate)", class: "membrane", id: "membrane" }); mem.style.transformOrigin = "406px 128px"; sv.append(mem);
  const ml = S("text", { x: 406, y: 40, "text-anchor": "middle", fill: "var(--escalate)", "font-size": 7, "font-family": "var(--mono)", id: "memLabel", opacity: .45 }); ml.textContent = "FIREWALL"; sv.append(ml);
}
const EVCOLOR = { deterministic_exact: "var(--heal)", json_similarity: "var(--heal)", semantic_similarity: "var(--quarantine)", llm_judge_faithfulness: "var(--escalate)", trajectory: "var(--escalate)" };
async function spawnPacket(inc) {
  const sv = $("#firewall"); const g = S("g", { class: "packet" }); const color = EVCOLOR[inc.evaluator] || "var(--trust)";
  const dot = S("circle", { r: 7, fill: color }); dot.style.color = color.startsWith("var") ? "#3DF5A0" : color;
  const tag = S("text", { x: 0, y: -11, "text-anchor": "middle", fill: "var(--text-muted)", "font-size": 6.5, "font-family": "var(--mono)" }); tag.textContent = EVAL_SHORT[inc.evaluator];
  g.append(dot, tag); g.style.transform = `translate(${FW.entry[0]}px,${FW.entry[1]}px)`; sv.append(g);
  let pos = [FW.entry[0], FW.entry[1]];
  const move = (x, y, ms, ease = "cubic-bezier(.4,0,.2,1)") => {
    if (reduced) { g.style.transform = `translate(${x}px,${y}px)`; pos = [x, y]; return Promise.resolve(); }
    const anim = g.animate([{ transform: `translate(${pos[0]}px,${pos[1]}px)` }, { transform: `translate(${x}px,${y}px)` }], { duration: ms, easing: ease, fill: "forwards" });
    pos = [x, y]; return anim.finished;
  };
  await move(FW.gate[0], FW.gate[1], 700);
  if (inc.category === "BEHAVIORAL_REGRESSION") {
    await move(405, 120, 360);                         // heads toward HEAL
    fireMembrane();
    if (!reduced) { g.animate([{ transform: "translate(405px,120px)" }, { transform: "translate(360px,180px)" }, { transform: `translate(${FW.esc[0]}px,${FW.esc[1]}px)` }], { duration: 900, easing: "cubic-bezier(.5,-0.4,.3,1)", fill: "forwards" }); pos = [FW.esc[0], FW.esc[1]]; }
    else { g.style.transform = `translate(${FW.esc[0]}px,${FW.esc[1]}px)`; pos = [FW.esc[0], FW.esc[1]]; }
    bumpBadMerges(); addBlock("TestPilot", "REFUSED auto-fix", inc.case_id, "refuse");
    toast("⛔ Behavioral regression REFUSED — escalated to a human", "bad");
    await wait(900);
  } else {
    const to = inc.lane === "auto_heal" ? FW.heal : inc.lane === "quarantine" ? FW.quar : FW.esc;
    await move(to[0], to[1], 700);
    if (inc.lane === "auto_heal") { kpis.auto_heals_merged++; toast("🛠 Auto-healed → PR opened", "good"); }
    if (inc.lane === "quarantine") toast("🔁 Quarantined with retry policy");
    await wait(400);
  }
  if (!reduced) g.animate([{ opacity: 1 }, { opacity: 0 }], { duration: 500, fill: "forwards" }).finished.then(() => g.remove()); else g.remove();
}
function fireMembrane() { const m = $("#membrane"), l = $("#memLabel"); if (!m) return; m.classList.remove("fire"); void m.getBoundingClientRect(); m.classList.add("fire"); if (l) l.animate([{ opacity: .4 }, { opacity: 1 }, { opacity: .4 }], { duration: 1000 }); lightStation(1); $(".firewall-wrap")?.classList.add("shake"); setTimeout(() => $(".firewall-wrap")?.classList.remove("shake"), 500); }

function laneCounts() { const c = { auto_heal: 0, quarantine: 0, escalate: 0 }; incidents.forEach(i => { if (c[i.lane] != null) c[i.lane]++; }); return c; }
function renderFirewallMeta() {
  const q = $("#fwQueue"); if (q) { q.innerHTML = ""; incidents.slice(0, 6).forEach(inc => { const dot = EVCOLOR[inc.evaluator] || "var(--trust)"; q.append(el("span", { class: "fchip", title: inc.agent + " · " + inc.case_id + " · " + EVAL_SHORT[inc.evaluator] }, el("i", { style: "background:" + dot }), inc.case_id)); }); }
  const s = $("#fwStats"); if (!s) return; s.innerHTML = ""; const cn = laneCounts();
  [["auto_heal", "AUTO-HEAL", "→ reviewable PR", cn.auto_heal, "var(--heal)"],
   ["quarantine", "QUARANTINE", "retry policy · no code change", cn.quarantine, "var(--quarantine)"],
   ["escalate", "ESCALATE", "human-only gate", cn.escalate, "var(--escalate)"]].forEach(([k, t, sub, n, c]) =>
    s.append(el("div", { class: "fw-stat " + k },
      el("div", { class: "fs-top" }, el("i", { style: "background:" + c }), el("span", { class: "fs-t" }, t)),
      el("div", { class: "fs-n num", style: "color:" + c }, "" + n),
      el("div", { class: "fs-s" }, sub))));
}
function renderConLegend() {
  const u = $("#conLegend"); if (!u) return; u.innerHTML = "";
  [["exact", "var(--heal)"], ["json-sim", "var(--heal)"], ["semantic", "var(--quarantine)"], ["faithful", "var(--escalate)"], ["trajectory", "var(--escalate)"]]
    .forEach(([l, c]) => u.append(el("span", { class: "cl" }, el("i", { style: "background:" + c }), l)));
}

function renderFeed() {
  const u = $("#feedList"); u.innerHTML = "";
  incidents.slice().sort((a, b) => (b.day - a.day) || 0).slice(0, 40).forEach(inc => u.append(feedRow(inc)));
}
function feedRow(inc, fresh) {
  const li = el("li", { class: inc.lane + (fresh ? " fresh" : "") });
  const v = inc.lane === "auto_heal" ? "HEAL" : inc.lane === "quarantine" ? "QUAR" : "ESC";
  li.append(el("span", { class: "t" }, "D-" + (89 - inc.day)), el("span", { class: "ag" }, inc.agent), el("span", { class: "cs" }, inc.case_id), el("span", { class: "v" }, v));
  li.onclick = () => inc.category === "BEHAVIORAL_REGRESSION" ? openEvidence(inc) : inc.lane === "auto_heal" ? openPR(inc) : openEvidence(inc);
  return li;
}
function renderInbox() {
  const u = $("#inboxList"); u.innerHTML = "";
  const pend = [HERO.regr, { ...HERO.drift, category: "MECHANICAL_DRIFT" }];
  pend.forEach(inc => {
    const c = el("div", { class: "card " + (inc.category === "BEHAVIORAL_REGRESSION" ? "esc" : "") });
    c.append(el("div", { class: "c-h" }, el("span", {}, inc.agent + " · " + inc.case_id), el("span", {}, inc.category === "BEHAVIORAL_REGRESSION" ? "REGRESSION" : "PR #42")));
    c.append(el("div", { class: "c-t" }, inc.category === "BEHAVIORAL_REGRESSION" ? "Faithfulness 100 → 41 — release blocked, human review" : "Auto-heal selector drift → reviewable PR"));
    const act = el("div", { class: "c-a" }); const ap = el("button", { class: "approve" }, "✓ Approve"); ap.onclick = () => { addBlock("@mira", "HUMAN APPROVED", inc.case_id, "approve"); toast("✓ Human approved " + inc.case_id, "good"); c.style.opacity = .4; updatePending(); }; act.append(ap, el("button", { class: "reqchg" }, "Request changes"));
    c.append(act); u.append(c);
  });
  updatePending();
}
function updatePending() { const n = $$("#inboxList .card").filter(c => c.style.opacity !== "0.4").length; $("#pendingCount").textContent = n + " pending"; $("#sbMid").textContent = n + " human gate(s) pending · " + kpis.bad_merges_prevented + " bad merges prevented"; }

function renderTimeline() {
  const t = $("#tlTrack"); t.innerHTML = "";
  incidents.forEach(inc => { const d = el("div", { class: "dot " + inc.lane }); d.style.left = (inc.day / 89 * 100) + "%"; t.append(d); });
}
function renderStations() {
  const s = $("#stations"); s.innerHTML = "";
  STATIONS.forEach((label, i) => { const st = el("div", { class: "station", "data-st": i }, el("div", { class: "dotind" }), label); s.append(st); });
}
function lightStation(i) { const st = $(`.station[data-st="${i}"]`); if (!st) return; st.classList.add("lit"); setTimeout(() => st.classList.remove("lit"), 1400); }
async function pulsePipeline() { for (let i = 0; i < STATIONS.length; i++) { lightStation(i); await wait(180); } }

function renderLedger() {
  const u = $("#ledgerList"); if (!u) return; u.innerHTML = "";
  ledger.forEach(b => { const li = el("li", { class: "block " + (b.tampered ? "broken" : "") });
    li.append(el("div", { class: "b-top" }, el("span", {}, "#" + String(b.index).padStart(3, "0") + " · " + b.t), el("span", {}, b.actor)),
      el("div", { class: "b-act " + b.cls }, b.action + " · " + b.case_id),
      el("div", { class: "hash" }, "prev ", el("b", {}, b.prev_hash.slice(0, 12)), " → ", el("b", {}, b.hash.slice(0, 12))));
    u.append(li); });
}
function flashStatus() { const ok = verifyChain(); $("#chainState").textContent = ok ? "VERIFIED" : "BROKEN"; $(".statusbar").classList.toggle("broken", !ok); if (window.__TP) window.__TP.chainOk = ok; }

// ---------- DRAWERS / OVERLAYS ----------
const show = id => { const o = $(id); o.hidden = false; };
const hide = o => { o.hidden = true; };
$$("[data-close]").forEach(b => b.onclick = e => hide(e.target.closest(".overlay")));
document.addEventListener("keydown", e => { if (e.key === "Escape") { $$(".overlay:not([hidden])").forEach(hide); $("#palette").hidden = true; endNarrate(); } });

function openPR(inc) {
  const h = HERO.drift; $("#prTitle").textContent = "PR " + h.pr + " · " + (inc.agent || h.agent);
  $("#prMeta").textContent = `branch fix/${h.case_id} → main · ${h.file} · authored by TestPilot`;
  const diff = $("#prDiff"); diff.innerHTML = "";
  const lines = [["", "--- a/" + h.file], ["", "+++ b/" + h.file], ["del", h.old_line], ["add", h.new_line]];
  show("#prTheater"); $("#prJunit").className = "junit red"; $("#prJunit").textContent = "JUnit: 1 failed";
  (async () => { for (const [c, tx] of lines) { const span = el("span", { class: c }, tx + "\n"); diff.append(span); await wait(180); } await wait(300); const j = $("#prJunit"); j.className = "junit"; j.textContent = "JUnit: re-run green ✓ (Test Cloud)"; })();
}
function openEvidence(inc) {
  const h = HERO.regr; show("#evidence"); $("#evTitle").textContent = "EVIDENCE · " + (inc.agent || h.agent) + " · " + (inc.case_id || h.case_id);
  // trajectory fork
  const sv = $("#evTraj"); sv.innerHTML = ""; const exp = h.expected_path, act = h.actual_path; const W = 420, y1 = 40, y2 = 110, step = W / 5;
  const drawPath = (path, y, color, dash) => { let d = ""; path.forEach((n, i) => { const x = 30 + i * step; d += (i ? "L" : "M") + x + " " + y; sv.append(S("circle", { cx: x, cy: y, r: 5, fill: color })); const tx = S("text", { x, y: y - 12, "text-anchor": "middle", fill: color, "font-size": 7.5, "font-family": "var(--mono)" }); tx.textContent = n; sv.append(tx); }); sv.append(S("path", { d, fill: "none", stroke: color, "stroke-width": 2, "stroke-dasharray": dash || "none" })); };
  drawPath(exp, y1, "var(--heal)", "4 4"); drawPath(act, y2, "var(--escalate)");
  const exL = S("text", { x: 8, y: y1 + 3, fill: "var(--heal)", "font-size": 7, "font-family": "var(--mono)" }); exL.textContent = "EXP"; sv.append(exL);
  const acL = S("text", { x: 8, y: y2 + 3, fill: "var(--escalate)", "font-size": 7, "font-family": "var(--mono)" }); acL.textContent = "ACT"; sv.append(acL);
  const dx = 30 + h.divergence * step; sv.append(S("circle", { cx: dx, cy: y2, r: 11, fill: "none", stroke: "var(--escalate)", "stroke-width": 1.5 }));
  const dl = S("text", { x: dx, y: y2 + 28, "text-anchor": "middle", fill: "var(--escalate)", "font-size": 7, "font-family": "var(--mono)" }); dl.textContent = "divergence"; sv.append(dl);
  // gauges
  const g = $("#evGauges"); g.innerHTML = ""; const scores = { exact: 100, "json-sim": 96, semantic: 74, faithful: 41, trajectory: 33 };
  Object.entries(scores).forEach(([k, v]) => { const c = v >= 80 ? "var(--heal)" : v >= 60 ? "var(--quarantine)" : "var(--escalate)"; const d = el("div", { class: "ev-g" }, el("div", { class: "gv num", style: "color:" + c }, "" + v), el("div", { class: "bar" }, el("i", { style: `width:${v}%;background:${c}` })), el("div", { class: "gl" }, k)); g.append(d); });
  $("#evCmp").innerHTML = ""; $("#evCmp").append(el("div", { class: "row" }, el("span", { class: "lab" }, "expected"), el("span", { class: "exp" }, h.expected)), el("div", { class: "row" }, el("span", { class: "lab" }, "actual"), el("span", { class: "act" }, h.actual)), el("div", { class: "row" }, el("span", { class: "lab" }, "trajectory"), el("span", {}, h.trajectory_diff)));
  typewriter($("#evRca"), h.rca);
}
function openAgent(a) {
  show("#agentDrawer"); $("#adName").textContent = a.callsign + " · trust " + a.trust + " · " + a.owner;
  const b = $("#adBody"); b.innerHTML = "";
  const gw = el("div", { class: "panel", style: "padding:12px;display:grid;place-items:center" }); gw.append(ring(a.trust, 84)); b.append(gw);
  const bd = el("div", { class: "panel", style: "padding:12px" }); bd.append(el("div", { class: "ev-sub" }, "TRUST BREAKDOWN"));
  Object.entries({ faithfulness: a.breakdown.faithfulness, determinism: a.breakdown.determinism, "trajectory adherence": a.breakdown.trajectory, "flake rate": 100 - a.breakdown.flake, "escalations (90d)": a.breakdown.escalation }).forEach(([k, v]) => { const c = v >= 80 ? "var(--heal)" : v >= 60 ? "var(--quarantine)" : "var(--escalate)"; bd.append(el("div", { class: "ev-cmp", style: "margin:6px 0" }, el("div", { class: "row" }, el("span", { class: "lab", style: "width:140px" }, k), el("span", { class: "num", style: "color:" + c }, "" + (k === "escalations (90d)" ? a.breakdown.escalation : v))))); });
  b.append(bd);
  const inc = el("div", { class: "panel", style: "padding:12px" }); inc.append(el("div", { class: "ev-sub" }, "RECENT INCIDENTS"));
  incidents.filter(i => i.agent === a.callsign).slice(0, 6).forEach(i => inc.append(feedRow(i))); if (!inc.querySelector("li")) inc.append(el("div", { class: "gl", style: "color:var(--text-faint);padding:6px" }, "no recent incidents — nominal"));
  b.append(inc);
}
function typewriter(node, text) { if (reduced) { node.textContent = text; return; } node.textContent = ""; let i = 0; const t = setInterval(() => { node.textContent += text[i++] || ""; if (i >= text.length) clearInterval(t); }, 14); }
function toast(msg, cls = "") { const t = $("#toast"); t.className = "toast " + cls; t.textContent = msg; t.hidden = false; clearTimeout(toast._t); toast._t = setTimeout(() => t.hidden = true, 2600); }

// deny
function deny() {
  fireMembrane(); const d = $("#denied"); d.hidden = false; document.body.classList.add("shake"); setTimeout(() => document.body.classList.remove("shake"), 500);
  bumpBadMerges(); addBlock("SYSTEM", "BLOCKED auto-merge attempt", "regr-01", "block"); updatePending();
  setTimeout(() => d.hidden = true, 1700);
}

// tamper
function tamper() { if (!ledger.length) return; const b = ledger[Math.floor(ledger.length / 2)]; b.tampered = !b.tampered; b.action = b.tampered ? b.action + " [ALTERED]" : b.action.replace(" [ALTERED]", ""); renderLedger(); flashStatus(); toast(b.tampered ? "⚠ Ledger tampered — chain broke" : "Chain restored", b.tampered ? "bad" : "good"); }

// command palette
function openPalette() { const p = $("#palette"); p.hidden = false; const inp = $("#palInput"); inp.value = ""; inp.focus(); fillPalette(""); }
function fillPalette(q) { const items = [{ l: "▶ Run PLAY DEMO", a: playDemo }, { l: "Open Governance Ledger", a: () => show("#ledgerPanel") }, { l: "Tamper demo (break chain)", a: tamper }, ...agents.map(a => ({ l: "Agent · " + a.callsign + " (trust " + a.trust + ")", a: () => openAgent(a) }))].filter(x => x.l.toLowerCase().includes(q.toLowerCase())); const u = $("#palList"); u.innerHTML = ""; items.slice(0, 8).forEach((it, i) => { const li = el("li", { class: i === 0 ? "sel" : "" }, it.l); li.onclick = () => { $("#palette").hidden = true; it.a(); }; u.append(li); }); }

// ---------- GUIDED DEMO NARRATOR (teleprompter) ----------
const NR_ACCENT = { heal: "var(--heal)", quar: "var(--quarantine)", esc: "var(--escalate)", trust: "var(--trust)", hero: "var(--hero)" };
const NR_TOTAL = 8;
function narrate(step, kicker, title, body, accent = "trust") {
  const n = $("#narrator"); n.hidden = false;
  n.style.setProperty("--nr", NR_ACCENT[accent] || accent);
  $("#nrStep").textContent = String(step).padStart(2, "0") + " / " + String(NR_TOTAL).padStart(2, "0");
  $("#nrKicker").textContent = kicker; $("#nrTitle").textContent = title; $("#nrBody").textContent = body;
  const d = $("#nrDots"); d.innerHTML = ""; for (let i = 1; i <= NR_TOTAL; i++) d.append(el("i", { class: i <= step ? "on" : "" }));
  n.classList.remove("in"); void n.offsetWidth; n.classList.add("in");
}
function endNarrate() { const n = $("#narrator"); if (n) { n.classList.remove("in"); n.hidden = true; } }

// ---------- AUTOPILOT (PLAY DEMO) ----------
let demoRunning = false;
async function playDemo() {
  if (demoRunning) return; demoRunning = true;
  const btn = $("#playDemo"); btn.textContent = "● RUNNING"; btn.classList.remove("cta");
  document.body.classList.add("demo-on");

  narrate(1, "The problem", "Everyone ships AI agents — almost no one governs them",
    "A silent behavioral regression looks green on the surface. Watch TestPilot triage one failed Agent-Evaluation run, live.", "hero");
  await wait(3400);

  narrate(2, "Incident", "A nightly eval run just went RED",
    "TestPilot wakes up and inspects every failing case, routing each by which evaluator class actually broke.", "trust");
  await pulsePipeline(); await wait(1500);

  narrate(3, "Case 1 · Mechanical drift", "A renamed selector — safe to auto-heal",
    "btn-signin → btn-login: a deterministic exact-match failure. TestPilot drafts the one-line fix and opens a reviewable GitHub PR.", "heal");
  await spawnPacket({ ...HERO.drift }); lightStation(2); lightStation(3); await wait(1600);

  narrate(4, "Case 2 · Flaky", "Passed on retry — genuine non-determinism",
    "No behavior changed and not a line of code is touched. TestPilot quarantines it with a retry policy so it can't block the build.", "quar");
  await spawnPacket({ ...HERO.flaky }); await wait(1600);

  narrate(5, "Case 3 · The dangerous one", "Faithfulness 100 → 41",
    "Invoice-Dispute stopped citing policy before answering. This is not a broken selector — the agent's behavior actually changed.", "esc");
  toast("⚠ Incoming: behavioral regression on Invoice-Dispute", "bad"); await wait(2800);

  narrate(6, "The firewall", "Behavior is a product decision, not a bug fix",
    "TestPilot REFUSES to auto-fix it, deflects it at the firewall, and escalates to a human. A bad merge is prevented.", "esc");
  await spawnPacket({ ...HERO.regr }); lightStation(4); await wait(1300);

  narrate(7, "The evidence", "What the human actually receives",
    "Expected vs actual tool-path, the exact divergence, every eval score, and a keyless AI root-cause — via the UiPath AI Trust Layer.", "trust");
  openEvidence(HERO.regr); await wait(4400); hide($("#evidence"));

  narrate(8, "The proof", "Every decision is hash-chained & tamper-evident",
    "Auto-heal, quarantine, refusal, human approval — all written to an append-only governance ledger you can audit and export.", "heal");
  show("#ledgerPanel"); await wait(4000);

  toast("✓ TestPilot — an on-call QA engineer for your AI agents", "good");
  endNarrate(); document.body.classList.remove("demo-on");
  btn.textContent = "▶ PLAY DEMO"; demoRunning = false;
}

// live injection
let liveTimer; let mode = "live";
function startLive() { clearInterval(liveTimer); if (mode !== "live") return; liveTimer = setInterval(() => { const inc = { agent: pick(CALLSIGNS), case_id: "case-" + (idc++), category: pick(["MECHANICAL_DRIFT", "FLAKY", "BEHAVIORAL_REGRESSION"]), lane: null, evaluator: pick(EVALS), day: 89 }; inc.lane = LANES[inc.category]; incidents.unshift(inc); const u = $("#feedList"); u.prepend(feedRow(inc, true)); if (u.children.length > 40) u.lastChild.remove(); kpis.cases_triaged_today++; }, 3200); }

// ---------- WIRING ----------
$("#playDemo").onclick = playDemo;
$("#denyBtn").onclick = deny;
$("#ledgerToggle").onclick = () => { const l = $("#ledgerPanel"); l.hidden = !l.hidden; };
$("#tamperBtn").onclick = tamper;
$("#exportBtn").onclick = () => { const blob = new Blob([JSON.stringify(ledger, null, 2)], { type: "application/json" }); const a = el("a", { href: URL.createObjectURL(blob), download: "governance-ledger.json" }); a.click(); };
$("#cmdkBtn").onclick = openPalette;
$("#palInput")?.addEventListener("input", e => fillPalette(e.target.value));
$("#palInput")?.addEventListener("keydown", e => { if (e.key === "Enter") { const s = $("#palList li.sel") || $("#palList li"); s?.click(); } });
$("#scrubber").oninput = e => { const day = +e.target.value; const visible = agents[0].trend[day].score ? Math.round(agents.reduce((s, a) => s + a.trend[day].score, 0) / agents.length) : 80; renderTrustGauge(visible); $("#sbMid").textContent = "REPLAY · day " + day + "/89"; };
$$("#modeToggle button").forEach(b => b.onclick = () => { $$("#modeToggle button").forEach(x => x.classList.remove("on")); b.classList.add("on"); mode = b.dataset.mode; $("#feedLed").style.background = mode === "live" ? "var(--heal)" : "var(--text-faint)"; mode === "live" ? startLive() : clearInterval(liveTimer); });
document.addEventListener("keydown", e => { if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === "k") { e.preventDefault(); openPalette(); } });

// ---------- BOOT ----------
async function boot() {
  const bs = $("#bootStations"); STATIONS.forEach(s => bs.append(el("div", { class: "bs" }, s)));
  $("#bootSkip").onclick = endBoot;
  if (reduced) { endBoot(); return; }
  for (const node of $$("#bootStations .bs")) { node.classList.add("on"); $("#bootStatus").textContent = "POWERING · " + node.textContent; await wait(380); }
  $("#bootStatus").textContent = "FLEET ONLINE"; await wait(500); endBoot();
}
let booted = false;
function endBoot() { if (booted) return; booted = true; $("#boot").classList.add("gone"); setTimeout(() => $("#boot").hidden = true, 600); renderTrustGauge(fleetTrust()); renderTrend(); }
function fleetTrust() { return Math.round(agents.reduce((s, a) => s + a.trust, 0) / agents.length); }

// ---------- INIT ----------
function init() {
  renderKPIs(); renderFleet(); renderConstellation(); renderConLegend(); renderFirewall(); renderFirewallMeta(); renderFeed(); renderInbox(); renderTimeline(); renderStations(); renderLedger(); flashStatus(); updatePending();
  $("#sbTrust").textContent = fleetTrust();
  $("#playDemo").classList.add("cta");   // "start here" affordance until first run
  startLive();
  window.__TP = { get badMerges() { return kpis.bad_merges_prevented; }, get ledger() { return ledger; }, chainOk: verifyChain(), spawnPacket, deny, tamper, playDemo, HERO, addBlock };
  boot();
}
init();
