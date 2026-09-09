from unittest.mock import patch

import pytest
from rich.console import Console

from lobster.cli_internal.commands.heavy import chat_commands


class _QueryClient:
    def __init__(self):
        self.answers = []

    def query(self, text, stream=False):
        question = {"data": {"component": "text_input", "fallback_prompt": "Name?"}}
        if stream:
            return iter(
                [
                    {"type": "content_delta", "delta": "Before question"},
                    {"type": "interrupt", **question},
                ]
            )
        return {"success": False, "interrupts": [question]}

    def resume_from_interrupt(self, response, stream=True):
        self.answers.append(response)
        yield {"type": "complete", "success": True, "response": "Finished"}


@pytest.mark.parametrize("stream", [True, False])
def test_classic_chat_prompts_and_resumes(stream):
    client = _QueryClient()
    console = Console(record=True)
    with patch("builtins.input", return_value="Alice") as prompt:
        if stream:
            result = chat_commands._display_streaming_response(client, "hello", console)
        else:
            result = chat_commands._query_classic(client, "hello")

    prompt.assert_called_once_with("\nName?: ")
    assert client.answers == [{"answer": "Alice"}]
    assert result["success"] is True
    assert result["response"] == "Finished"
