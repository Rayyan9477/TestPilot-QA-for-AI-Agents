// TestPilot — Mission Control · Playwright smoke test.
//
// Asserts the three load-bearing behaviors of the governed quality gate, driving the app
// through its `window.__TP` debug hooks (no brittle pixel/timing assertions):
//
//   1. A BEHAVIORAL_REGRESSION packet is DEFLECTED at the Triage Firewall — never auto-merged.
//      It ticks "BAD MERGES PREVENTED", writes a "REFUSED auto-fix" block, and the chain stays VERIFIED.
//   2. Press-to-be-DENIED (a human trying to force an auto-merge of behavior) is BLOCKED and logged.
//   3. The hash-chained governance ledger is tamper-evident: altering a block breaks the chain;
//      reverting restores it.
//
// Run it (self-contained — the config below boots a static server, or reuses one on :8139):
//   cd dashboard
//   npm init -y && npm i -D @playwright/test && npx playwright install chromium
//   npx playwright test
//
// The whole policy soul in one assertion: only a human merges behavior.

import { test, expect } from "@playwright/test";

const snapshot = (page) =>
  page.evaluate(() => {
    const led = window.__TP.ledger;
    return {
      badMerges: window.__TP.badMerges,
      len: led.length,
      last: led[led.length - 1],
      chainState: document.querySelector("#chainState").textContent.trim(),
      chainOk: window.__TP.chainOk,
    };
  });

test.beforeEach(async ({ page }) => {
  await page.goto("/index.html");
  await page.waitForFunction(() => !!window.__TP && Array.isArray(window.__TP.ledger));
});

test("behavioral regression is DEFLECTED at the firewall — never auto-merged", async ({ page }) => {
  const before = await snapshot(page);

  // Fire the canonical behavioral-regression incident through the Triage Firewall.
  await page.evaluate(() => window.__TP.spawnPacket({ ...window.__TP.HERO.regr }));

  const after = await snapshot(page);
  expect(after.badMerges).toBe(before.badMerges + 1); // "BAD MERGES PREVENTED" ticked up
  expect(after.len).toBe(before.len + 1); // exactly one new governance block
  expect(after.last.action).toBe("REFUSED auto-fix"); // the refusal is recorded, not narrated
  expect(after.last.case_id).toBe("regr-01");
  expect(after.chainState).toBe("VERIFIED"); // ledger still cryptographically intact
  expect(after.chainOk).toBeTruthy();
});

test("press-to-be-DENIED records a BLOCKED block and prevents the merge", async ({ page }) => {
  const before = await snapshot(page);

  await page.getByTestId("btn-deny").click(); // "Try to auto-merge behavior"

  const after = await snapshot(page);
  expect(after.badMerges).toBe(before.badMerges + 1);
  expect(after.len).toBe(before.len + 1);
  expect(after.last.action).toContain("BLOCKED");
  expect(after.chainState).toBe("VERIFIED");
  expect(after.chainOk).toBeTruthy();

  // The DENIED stamp is shown to the operator.
  await expect(page.getByTestId("denied-stamp")).toBeVisible();
});

test("tampering with the ledger breaks the hash chain; reverting restores it", async ({ page }) => {
  await page.evaluate(() => window.__TP.tamper());
  let s = await snapshot(page);
  expect(s.chainState).toBe("BROKEN");
  expect(s.chainOk).toBeFalsy();

  await page.evaluate(() => window.__TP.tamper());
  s = await snapshot(page);
  expect(s.chainState).toBe("VERIFIED");
  expect(s.chainOk).toBeTruthy();
});
