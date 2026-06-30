"""Branch-A heart: locate the drifted token line in the repo, ask the injected LLM for the
corrected line, validate it is a single real change, and emit a one-line unified diff.

Refuses to open empty/garbage PRs: missing token, ambiguous token, empty/whitespace/
multi-line/no-op LLM output all raise FixerError (SYSTEM-DESIGN §6, §14.1/§14.4).
"""
from __future__ import annotations

from pathlib import Path

from .llm import LLMClient
from .models import EvalResult, FixProposal

# Text files we are willing to repair. Keeps the search away from binaries.
_SEARCH_EXT = {".cs", ".vb", ".py", ".js", ".ts", ".json", ".xml", ".txt", ".html"}


class FixerError(Exception):
    """The fixer refuses to produce a PR (no token / ambiguous / bad LLM output)."""


def _find_unique_line(repo_root: Path, token: str) -> tuple[Path, str]:
    matches: list[tuple[Path, str]] = []
    for path in sorted(repo_root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in _SEARCH_EXT:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for line in text.splitlines():
            if token in line:
                matches.append((path, line))
    if not matches:
        raise FixerError(f"drift token {token!r} not found in repo — refusing to open an empty PR")
    if len(matches) > 1:
        raise FixerError(f"drift token {token!r} is ambiguous ({len(matches)} matches) — refusing to guess")
    return matches[0]


def _clean(raw: str) -> str:
    """Trim surrounding newlines / a ``` fence / trailing whitespace, but PRESERVE leading
    indentation so the corrected line keeps the source's formatting."""
    s = raw.strip("\r\n")
    if s.lstrip().startswith("```"):
        lines = s.splitlines()
        if lines and lines[0].lstrip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        s = "\n".join(lines).strip("\r\n")
    return s.rstrip()


def _build_prompt(rel_path: str, eval_result: EvalResult, old_line: str) -> str:
    return (
        "You repair a single drifted locator/field string in a UiPath coded test.\n"
        "Return ONLY the corrected line — no prose, no code fences, no extra lines.\n"
        f"File: {rel_path}\n"
        f"The value {eval_result.actual!r} should be {eval_result.expected!r}.\n"
        f"Current line:\n{old_line}\n"
        "Return the corrected single line."
    )


def draft_fix(eval_result: EvalResult, repo_root: Path, llm: LLMClient) -> FixProposal:
    repo_root = Path(repo_root)
    token = eval_result.actual
    if not token:
        raise FixerError("eval case has no `actual` drift token to locate")

    path, old_line = _find_unique_line(repo_root, token)
    rel = str(path.relative_to(repo_root)).replace("\\", "/")

    new_line = _clean(llm.complete(_build_prompt(rel, eval_result, old_line)))

    if not new_line.strip():
        raise FixerError("LLM returned an empty fix")
    if "\n" in new_line:
        raise FixerError("LLM returned a multi-line fix — refusing (one-line diffs only)")
    if new_line == old_line:
        raise FixerError("LLM fix is a no-op — refusing to open an empty PR")

    unified_diff = f"--- a/{rel}\n+++ b/{rel}\n-{old_line}\n+{new_line}"
    return FixProposal(file_path=rel, old_line=old_line, new_line=new_line, unified_diff=unified_diff)
