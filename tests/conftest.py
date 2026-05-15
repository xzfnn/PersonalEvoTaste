from __future__ import annotations

from pathlib import Path

import pytest

from personal_evotaste import PersonalEvoTaste


@pytest.fixture
def yaml_memory(tmp_path: Path) -> Path:
    return tmp_path / "memory.yaml"


@pytest.fixture
def taste(yaml_memory: Path) -> PersonalEvoTaste:
    return PersonalEvoTaste(memory_path=yaml_memory, decay=0.0)
