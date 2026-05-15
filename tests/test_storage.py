from __future__ import annotations

from pathlib import Path

import pytest

from personal_evotaste.exceptions import StorageError
from personal_evotaste.models import TasteMemory, TasteRule
from personal_evotaste.storage import (
    JSONStorage,
    SQLiteStorage,
    YAMLStorage,
    storage_from_path,
)


@pytest.mark.parametrize(
    "backend_cls, filename",
    [
        (YAMLStorage, "m.yaml"),
        (JSONStorage, "m.json"),
        (SQLiteStorage, "m.sqlite3"),
    ],
)
def test_roundtrip(tmp_path: Path, backend_cls, filename: str):
    storage = backend_cls(tmp_path / filename)
    mem = TasteMemory(taste_rules=[TasteRule(rule="Prefer brutalist UI", project="x")])
    storage.save(mem)

    loaded = storage.load()
    assert len(loaded.taste_rules) == 1
    assert loaded.taste_rules[0].rule == "Prefer brutalist UI"
    assert loaded.taste_rules[0].project == "x"


def test_load_missing_file_returns_empty_memory(tmp_path: Path):
    storage = YAMLStorage(tmp_path / "nope.yaml")
    mem = storage.load()
    assert mem.taste_rules == []
    assert mem.history == []


def test_storage_factory(tmp_path: Path):
    assert isinstance(storage_from_path(tmp_path / "a.yaml"), YAMLStorage)
    assert isinstance(storage_from_path(tmp_path / "a.json"), JSONStorage)
    assert isinstance(storage_from_path(tmp_path / "a.sqlite3"), SQLiteStorage)
    with pytest.raises(StorageError):
        storage_from_path(tmp_path / "a.txt")
