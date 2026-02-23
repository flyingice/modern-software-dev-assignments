import os
from unittest.mock import MagicMock, patch

import pytest
from ollama import RequestError, ResponseError

from ..app.services.extract import (
    OllamaServiceError,
    extract_action_items,
    extract_action_items_llm,
)


def test_extract_bullets_and_checkboxes():
    text = """
    Notes from meeting:
    - [ ] Set up database
    * implement API extract endpoint
    1. Write tests
    Some narrative sentence.
    """.strip()

    items = extract_action_items(text)
    assert "Set up database" in items
    assert "implement API extract endpoint" in items
    assert "Write tests" in items


# --- Tests for extract_action_items_llm ---


def test_extract_action_items_llm_empty_input():
    """Empty or whitespace-only input should return an empty list."""
    assert extract_action_items_llm("") == []
    assert extract_action_items_llm("   ") == []
    assert extract_action_items_llm("\n\n") == []


def test_extract_action_items_llm_bullet_list():
    """Bullet-style action items should be extracted."""
    text = """
    - Fix the login bug
    - Update the README
    - Add unit tests for the parser
    """
    items = extract_action_items_llm(text)
    assert len(items) == 3
    items_lower = [item.lower() for item in items]
    assert any("login" in item for item in items_lower)
    assert any("readme" in item for item in items_lower)
    assert any("unit test" in item or "parser" in item for item in items_lower)


def test_extract_action_items_llm_keyword_prefixed():
    """Lines prefixed with keywords like TODO or ACTION should be picked up."""
    text = """
    TODO: Refactor the database module
    ACTION: Deploy to staging
    NEXT: Review pull request #42
    """
    items = extract_action_items_llm(text)
    assert len(items) == 3
    items_lower = [item.lower() for item in items]
    assert any("refactor" in item and "database" in item for item in items_lower)
    assert any("deploy" in item and "staging" in item for item in items_lower)
    assert any("review" in item and "pull request" in item for item in items_lower)


def test_extract_action_items_llm_mixed_text():
    """Should extract action items from text that mixes narrative and tasks."""
    text = """
    Had a great team lunch. The weather was sunny.
    We need to migrate the database to PostgreSQL by Friday.
    John should update the API docs. The office plant looks healthy.
    """
    items = extract_action_items_llm(text)
    assert len(items) == 2
    items_lower = [item.lower() for item in items]
    assert any("migrate" in item and "postgresql" in item for item in items_lower)
    assert any("update" in item and "api" in item for item in items_lower)


def test_extract_action_items_llm_special_characters_and_numbers():
    """Input with special characters and numbers should be handled gracefully."""
    text = """
    1) Fix bug #1234 in the auth module!
    2) Update config.yaml — set timeout=30s
    3) Check logs @ /var/log/app.log & verify output
    """
    items = extract_action_items_llm(text)
    assert len(items) == 3
    items_lower = [item.lower() for item in items]
    assert any("bug" in item and "1234" in item for item in items_lower)
    assert any("config" in item and "timeout" in item for item in items_lower)
    assert any("log" in item and "verify" in item for item in items_lower)


def test_extract_action_items_llm_typos_in_input():
    """The LLM should still extract action items despite typos."""
    text = """
    - Updaet the documnetation
    - Refactr the databse layer
    - Implment user authentcation
    """
    items = extract_action_items_llm(text)
    assert len(items) == 3
    items_lower = [item.lower() for item in items]
    assert any("documentation" in item for item in items_lower)
    assert any("database" in item for item in items_lower)
    assert any("authentication" in item for item in items_lower)


def test_extract_action_items_llm_no_action_items():
    """Purely narrative text with no tasks should return an empty or minimal list."""
    text = "The sun was shining and the birds were singing. It was a lovely day."
    items = extract_action_items_llm(text)
    assert len(items) == 0


def test_extract_action_items_llm_returns_list_of_strings():
    """Return type should always be a list of strings."""
    text = "- Write tests\n- Fix bugs"
    items = extract_action_items_llm(text)
    assert len(items) == 2
    items_lower = [item.lower() for item in items]
    assert any("write" in item and "test" in item for item in items_lower)
    assert any("fix" in item and "bug" in item for item in items_lower)


# --- Error handling tests for extract_action_items_llm ---


@patch("week2.app.services.extract.chat")
def test_extract_action_items_llm_ollama_unreachable(mock_chat):
    """RequestError from ollama should be wrapped as OllamaServiceError."""
    mock_chat.side_effect = RequestError("connection refused")
    with pytest.raises(OllamaServiceError, match="unreachable"):
        extract_action_items_llm("some text")


@patch("week2.app.services.extract.chat")
def test_extract_action_items_llm_ollama_model_error(mock_chat):
    """ResponseError from ollama should be wrapped as OllamaServiceError."""
    mock_chat.side_effect = ResponseError("model not found", status_code=404)
    with pytest.raises(OllamaServiceError, match="Ollama error"):
        extract_action_items_llm("some text")


@patch("week2.app.services.extract.chat")
def test_extract_action_items_llm_malformed_response(mock_chat):
    """Invalid JSON from ollama should be wrapped as OllamaServiceError."""
    mock_response = MagicMock()
    mock_response.message.content = "not valid json"
    mock_chat.return_value = mock_response
    with pytest.raises(OllamaServiceError, match="Malformed"):
        extract_action_items_llm("some text")
