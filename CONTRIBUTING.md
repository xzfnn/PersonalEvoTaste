# Contributing to PersonalEvoTaste

Thanks for your interest in improving PersonalEvoTaste! ❤️ This project follows a
"small, focused, well-tested" philosophy — please keep PRs scoped and discuss large
changes in an issue first.

## Development setup

```bash
git clone https://github.com/your-org/PersonalEvoTaste.git
cd PersonalEvoTaste
python -m venv .venv
. .venv/Scripts/activate     # Windows
# . .venv/bin/activate       # macOS / Linux
pip install -e ".[dev]"
```

## Running the toolchain

```bash
make test        # pytest + coverage
make lint        # ruff check
make format      # ruff format
make typecheck   # mypy
```

## Conventions

- **Python 3.9+** compatible (use `from __future__ import annotations`).
- Public API additions require type hints, a docstring, and tests.
- Keep storage formats backward compatible — bump `TasteMemory.version` on breaking changes.
- Conventional commits are appreciated (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`).
- One logical change per PR; include `Closes #<issue>` when relevant.

## Reporting bugs

Please open an issue using the bug template and include:

- A minimal reproduction (ideally a failing test).
- Python version and OS.
- The contents (sanitised) of your memory file if relevant.

## Code of Conduct

Participation is governed by the [Contributor Covenant](CODE_OF_CONDUCT.md).
