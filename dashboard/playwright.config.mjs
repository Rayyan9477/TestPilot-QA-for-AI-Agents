// Self-contained Playwright config for the Mission Control smoke test (tp.spec.mjs).
// Boots a static file server for this directory (or reuses one already on :8139),
// emulates reduced motion so the deterministic state assertions don't race animations.
import { defineConfig, devices } from "@playwright/test";

const PORT = 8139;

export default defineConfig({
  testDir: ".",
  testMatch: "tp.spec.mjs",
  fullyParallel: false,
  reporter: [["list"]],
  use: {
    baseURL: `http://localhost:${PORT}`,
    reducedMotion: "reduce",
    ...devices["Desktop Chrome"],
  },
  webServer: {
    command: `python -m http.server ${PORT}`,
    url: `http://localhost:${PORT}/index.html`,
    reuseExistingServer: true,
    timeout: 30_000,
  },
});
