from __future__ import annotations

from pathlib import Path

import pytest

from packages.prompts.loader import PromptLoader, PromptNotFoundError


def test_prompt_loader_renders_variables():
    loader = PromptLoader(Path("prompts"))
    loaded = loader.load("chunk_summary", variables={"content": "hello"})

    assert loaded["name"] == "chunk_summary"
    assert "hello" in loaded["content"]
    assert loaded["version"].startswith("mtime-")


def test_prompt_loader_missing_prompt_raises():
    loader = PromptLoader(Path("prompts"))
    with pytest.raises(PromptNotFoundError):
        loader.load("does_not_exist")
