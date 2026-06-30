"""Runtime LLM seam. The product calls the UiPath AI Trust Layer LLM Gateway (keyless,
governed) — but the client is injected behind a Protocol so the whole fixer is unit-tested
offline with FakeLLM, and the real gateway/bedrock clients are wired Day 1 (SYSTEM-DESIGN §6, §14.8).
"""
from __future__ import annotations

from typing import Protocol


class LLMClient(Protocol):
    def complete(self, prompt: str) -> str: ...


class FakeLLM:
    """Deterministic test double: returns a canned reply, zero network."""

    def __init__(self, reply: str) -> None:
        self._reply = reply

    def complete(self, prompt: str) -> str:  # noqa: ARG002 - prompt ignored by design
        return self._reply


def _extract_text(response: object) -> str:
    """Pull the assistant text out of a chat-completions response, tolerating both the dict
    and object response shapes the SDK may return."""
    try:
        if isinstance(response, dict):
            return response["choices"][0]["message"]["content"]
        return response.choices[0].message.content  # type: ignore[attr-defined]
    except (KeyError, IndexError, AttributeError, TypeError) as e:
        raise ValueError(f"unexpected LLM Gateway response shape: {e!r}") from e


class UiPathLLMGatewayClient:
    """Runtime client — routes through the UiPath AI Trust Layer LLM Gateway (keyless,
    governed) via ``sdk.llm.chat_completions``. Construction is side-effect-free (the SDK is
    built lazily) so entrypoints import safely with empty env; the live call is an integration
    seam validated on the tenant at S13 (SYSTEM-DESIGN §6/§14.8).

    NOTE: confirm the exact Gateway model id with ``uipath list-models`` on the tenant; any
    Gateway model works, and the demo narrative uses a Claude model.
    """

    def __init__(self, model: str = "anthropic.claude-sonnet-4-6", sdk: object | None = None) -> None:
        self._model = model
        self._sdk = sdk

    def _client(self) -> object:
        if self._sdk is not None:
            return self._sdk
        from uipath.platform import UiPath  # lazy: needs tenant env

        return UiPath()

    def complete(self, prompt: str) -> str:
        response = self._client().llm.chat_completions(
            [{"role": "user", "content": prompt}], model=self._model, max_tokens=512, temperature=0
        )
        return _extract_text(response)
