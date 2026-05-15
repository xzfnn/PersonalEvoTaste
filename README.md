<div align="center">

# 🧬 PersonalEvoTaste

**Teach your AI coding agent *your* taste — and watch it evolve.**

[![CI](https://github.com/xzfnn/PersonalEvoTaste/actions/workflows/ci.yml/badge.svg)](https://github.com/xzfnn/PersonalEvoTaste/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/personal-evotaste.svg)](https://pypi.org/project/personal-evotaste/)
[![Python](https://img.shields.io/pypi/pyversions/personal-evotaste.svg)](https://pypi.org/project/personal-evotaste/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

</div>

---

## ✨ What is it?

LLM agents are great at writing *generic* code — but they have **zero memory of your personal preferences**:
indentation tastes, library choices, naming conventions, the brutalist UI you love, the verbose
docstrings you hate. Every new chat resets to zero.

**PersonalEvoTaste** is a small, dependency-light library that gives an AI agent a **persistent,
self-evolving memory of your taste**. Feed it the agent's output + your feedback, and it distils,
deduplicates, reinforces and decays rules over time — then re-injects the top ones into the next
prompt.

```
        ┌──────────────┐  feedback   ┌──────────────────┐  rules   ┌────────────┐
agent → │ your review  │ ──────────► │ PersonalEvoTaste │ ───────► │ next prompt│
        └──────────────┘             └──────────────────┘          └────────────┘
                                              ▲  decay/reinforce        │
                                              └─────────────────────────┘
```

## 🚀 Features

- **🧠 Typed memory** — Pydantic v2 models, JSON-schema-friendly, versioned on disk.
- **🔌 Pluggable storage** — YAML / JSON / SQLite out of the box; bring-your-own backend.
- **🔬 Pluggable extractors** — deterministic heuristic by default; plug an LLM with `CallableExtractor`.
- **♻️ Self-evolution** — automatic deduplication, reinforcement on repetition, time decay.
- **⚖️ Ranked injection** — top-N rules by weight, optionally filtered per project.
- **🖥️ Zero-dep CLI** — `personal-evotaste evolve / inject / list / remove / reset / export`.
- **🧪 Tested & typed** — pytest suite, ruff, mypy, CI on Python 3.9 → 3.12.
- **💾 Crash-safe writes** — atomic file replacement, SQLite transactions.

## 📦 Installation

```bash
pip install personal-evotaste
# or from source
pip install -e ".[dev]"
```

## ⚡ Quickstart

```python
from personal_evotaste import PersonalEvoTaste

taste = PersonalEvoTaste(memory_path="my_taste.yaml")

# 1. Inject your evolving taste into any prompt
prompt = taste.inject_taste(
    "Generate a login page",
    context="brutalist minimal project",
)
# → send `prompt` to your LLM of choice

# 2. After reviewing the agent's output, teach it
taste.evolve(
    agent_output="A flashy gradient login page with neon buttons",
    user_feedback="Too loud. I want calmer, monochrome, brutalist typography.",
    project_name="acme-landing",
)

# 3. Next time, the rule is already in the prompt — and reinforced if you repeat yourself
print(taste.inject_taste("Generate a signup page"))
```

## 🖥️ CLI

```bash
# Add a rule from feedback
personal-evotaste evolve \
  --output "A flashy gradient login page" \
  --feedback "Too loud. Prefer calm monochrome brutalist typography." \
  --project acme-landing

# Inject taste into a prompt
personal-evotaste inject "Generate a signup page" --context "acme-landing"

# Inspect the memory
personal-evotaste list
personal-evotaste export > snapshot.json
```

Memory backend is auto-selected from the file extension: `.yaml` / `.json` / `.sqlite3`.

## 🔌 Plugging an LLM extractor

```python
from personal_evotaste import PersonalEvoTaste, CallableExtractor

def summarise_with_llm(agent_output: str, feedback: str, project: str) -> str:
    # call OpenAI / Anthropic / a local model here and return one short rule
    ...

taste = PersonalEvoTaste(
    memory_path="my_taste.yaml",
    extractor=CallableExtractor(summarise_with_llm),
)
```

## 🧱 Architecture

```
personal_evotaste/
├── models.py        # Pydantic models: TasteRule, FeedbackEvent, TasteMemory
├── storage.py       # BaseStorage + YAML / JSON / SQLite backends (atomic writes)
├── extractors.py    # RuleExtractor strategies + similarity-based deduplication
├── core.py          # PersonalEvoTaste façade (evolve / inject / ranking / decay)
├── cli.py           # argparse-based CLI (zero extra deps)
├── exceptions.py    # Typed error hierarchy
└── logging_config.py
```

See [`docs/architecture.md`](docs/architecture.md) for the design rationale.

## 🤝 Contributing

PRs, issues and ideas are very welcome — see [CONTRIBUTING.md](CONTRIBUTING.md) and our
[Code of Conduct](CODE_OF_CONDUCT.md). If PersonalEvoTaste helps you, a ⭐ on GitHub goes a long way.

## 📜 License

MIT © PersonalEvoTaste Contributors. See [LICENSE](LICENSE).
