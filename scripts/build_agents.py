"""Vendor the shared `testpilot` package into each coded-agent project and run the UiPath
toolchain so the agents are deployable to serverless. Run this before `uipath publish`.

    python scripts/build_agents.py           # vendor + uipath init (generate entry-points.json)
    python scripts/build_agents.py --pack     # also `uipath pack` into a .nupkg

The vendored copy keeps a single source of truth in src/testpilot while ensuring the shared
code is bundled into each published package (serverless cannot reach the repo's src/).
"""
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src" / "testpilot"
UIPATH = ROOT / ".venv" / "Scripts" / "uipath.exe"
if not UIPATH.exists():
    UIPATH = Path(shutil.which("uipath") or "uipath")

AGENTS = ["triage", "fixer"]


def build(agent: str, do_pack: bool) -> None:
    adir = ROOT / "agents" / agent
    vendor = adir / "testpilot"
    if vendor.exists():
        shutil.rmtree(vendor)
    shutil.copytree(SRC, vendor, ignore=shutil.ignore_patterns("__pycache__"))
    print(f"[{agent}] vendored testpilot -> {vendor.relative_to(ROOT)}")
    subprocess.run([str(UIPATH), "init"], cwd=adir, check=True)
    print(f"[{agent}] uipath init OK")
    if do_pack:
        subprocess.run([str(UIPATH), "pack"], cwd=adir, check=True)
        print(f"[{agent}] uipath pack OK")


if __name__ == "__main__":
    pack = "--pack" in sys.argv
    for name in AGENTS:
        build(name, pack)
    print("All agents built." + (" Packed to .nupkg." if pack else ""))
