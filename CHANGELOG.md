# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-05-15
### Added
- First public release.
- `PersonalEvoTaste` façade with `inject_taste` and `evolve` APIs.
- Pydantic-based `TasteRule`, `FeedbackEvent`, `TasteMemory` models.
- Pluggable storage backends: `YAMLStorage`, `JSONStorage`, `SQLiteStorage`
  with atomic / transactional writes.
- Pluggable rule extractors: `HeuristicExtractor` (default, dependency-free)
  and `CallableExtractor` (adapter for LLM-based extraction).
- Similarity-based rule deduplication, weight reinforcement and decay.
- `personal-evotaste` command-line interface.
- pytest test suite, GitHub Actions CI, ruff + mypy configuration.
