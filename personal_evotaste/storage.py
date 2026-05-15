"""Pluggable persistence layer.

Three backends are shipped out of the box:

* :class:`YAMLStorage`   - human-friendly, the default.
* :class:`JSONStorage`   - portable, useful for Web/API integrations.
* :class:`SQLiteStorage` - durable, supports concurrent reads.

Custom backends only need to implement :class:`BaseStorage`.
"""
from __future__ import annotations

import json
import sqlite3
import tempfile
from abc import ABC, abstractmethod
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Union

import yaml

from .exceptions import StorageError
from .logging_config import get_logger
from .models import TasteMemory

PathLike = Union[str, Path]
logger = get_logger("storage")


class BaseStorage(ABC):
    """Abstract storage contract."""

    @abstractmethod
    def load(self) -> TasteMemory: ...

    @abstractmethod
    def save(self, memory: TasteMemory) -> None: ...


# ---------------------------------------------------------------------------
# File-based helpers
# ---------------------------------------------------------------------------

@contextmanager
def _atomic_write(path: Path) -> Iterator[Path]:
    """Write to a temporary sibling then ``replace`` for crash safety."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", dir=str(path.parent))
    tmp = Path(tmp_name)
    try:
        import os
        os.close(fd)
        yield tmp
        tmp.replace(path)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise


class YAMLStorage(BaseStorage):
    def __init__(self, path: PathLike = "personal_taste_memory.yaml") -> None:
        self.path = Path(path)

    def load(self) -> TasteMemory:
        if not self.path.exists():
            return TasteMemory()
        try:
            raw = yaml.safe_load(self.path.read_text(encoding="utf-8")) or {}
            return TasteMemory.model_validate(raw)
        except Exception as exc:  # pragma: no cover - defensive
            raise StorageError(f"Failed to load YAML memory at {self.path}: {exc}") from exc

    def save(self, memory: TasteMemory) -> None:
        data = memory.model_dump(mode="json")
        try:
            with _atomic_write(self.path) as tmp:
                tmp.write_text(
                    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
                    encoding="utf-8",
                )
        except Exception as exc:
            raise StorageError(f"Failed to save YAML memory at {self.path}: {exc}") from exc


class JSONStorage(BaseStorage):
    def __init__(self, path: PathLike = "personal_taste_memory.json") -> None:
        self.path = Path(path)

    def load(self) -> TasteMemory:
        if not self.path.exists():
            return TasteMemory()
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            return TasteMemory.model_validate(raw)
        except Exception as exc:
            raise StorageError(f"Failed to load JSON memory at {self.path}: {exc}") from exc

    def save(self, memory: TasteMemory) -> None:
        try:
            with _atomic_write(self.path) as tmp:
                tmp.write_text(
                    memory.model_dump_json(indent=2),
                    encoding="utf-8",
                )
        except Exception as exc:
            raise StorageError(f"Failed to save JSON memory at {self.path}: {exc}") from exc


class SQLiteStorage(BaseStorage):
    """Stores the whole memory snapshot in a single row.

    The schema is intentionally minimal: it avoids ORM complexity while
    still giving us crash-safe writes via SQLite's transactions.
    """

    _SCHEMA = """
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            payload TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
    """

    def __init__(self, path: PathLike = "personal_taste_memory.sqlite3") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(self._SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.path))

    def load(self) -> TasteMemory:
        try:
            with self._connect() as conn:
                row = conn.execute("SELECT payload FROM memory WHERE id = 1").fetchone()
            if not row:
                return TasteMemory()
            return TasteMemory.model_validate_json(row[0])
        except Exception as exc:
            raise StorageError(f"Failed to load SQLite memory at {self.path}: {exc}") from exc

    def save(self, memory: TasteMemory) -> None:
        payload = memory.model_dump_json()
        from datetime import datetime, timezone
        try:
            with self._connect() as conn:
                conn.execute(
                    "INSERT INTO memory (id, payload, updated_at) VALUES (1, ?, ?)"
                    " ON CONFLICT(id) DO UPDATE SET payload=excluded.payload,"
                    " updated_at=excluded.updated_at",
                    (payload, datetime.now(timezone.utc).isoformat()),
                )
        except Exception as exc:
            raise StorageError(f"Failed to save SQLite memory at {self.path}: {exc}") from exc


def storage_from_path(path: PathLike) -> BaseStorage:
    """Best-effort factory: pick a backend based on the file extension."""
    p = Path(path)
    suffix = p.suffix.lower()
    if suffix in {".yml", ".yaml"}:
        return YAMLStorage(p)
    if suffix == ".json":
        return JSONStorage(p)
    if suffix in {".sqlite", ".sqlite3", ".db"}:
        return SQLiteStorage(p)
    raise StorageError(f"Cannot infer storage backend from suffix {suffix!r}")
