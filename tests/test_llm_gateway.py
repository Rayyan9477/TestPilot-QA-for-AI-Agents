"""TDD — UiPathLLMGatewayClient: the runtime LLM for the fixer, on the UiPath AI Trust Layer
LLM Gateway (keyless, governed) via sdk.llm.chat_completions. The SDK is injected so the
message-building and response-parsing are unit-tested offline; the live call is an integration
seam validated on the tenant at S13 (SYSTEM-DESIGN §14.8).
"""
import pytest

from testpilot.llm import UiPathLLMGatewayClient, _extract_text


class _FakeSDK:
    class _LLM:
        def __init__(self):
            self.calls = []

        def chat_completions(self, messages, model=None, **kwargs):
            self.calls.append({"messages": messages, "model": model, "kwargs": kwargs})
            return {"choices": [{"message": {"content": 'var x = "btn-login";'}}]}

    def __init__(self):
        self.llm = self._LLM()


def test_complete_sends_user_message_and_returns_text():
    sdk = _FakeSDK()
    client = UiPathLLMGatewayClient(model="m1", sdk=sdk)
    out = client.complete("repair this line")
    assert out == 'var x = "btn-login";'
    call = sdk.llm.calls[0]
    assert call["messages"] == [{"role": "user", "content": "repair this line"}]
    assert call["model"] == "m1"


def test_extract_text_from_dict_choices():
    assert _extract_text({"choices": [{"message": {"content": "X"}}]}) == "X"


def test_extract_text_from_object_choices():
    class Resp:
        class _Choice:
            class _Msg:
                content = "Y"

            message = _Msg()

        choices = [_Choice()]

    assert _extract_text(Resp()) == "Y"


def test_extract_text_raises_on_unknown_shape():
    with pytest.raises(ValueError):
        _extract_text({"unexpected": "shape"})


def test_construction_is_side_effect_free():
    # Must not touch the network/env at import or construction (entrypoints import it lazily).
    UiPathLLMGatewayClient(model="anything")


def test_client_constructs_uipath_lazily_when_no_sdk(monkeypatch):
    # With no injected sdk, _client() builds the UiPath SDK lazily (the real-tenant path).
    import uipath.platform as platform

    sentinel = object()
    monkeypatch.setattr(platform, "UiPath", lambda: sentinel)
    assert UiPathLLMGatewayClient(model="m")._client() is sentinel
