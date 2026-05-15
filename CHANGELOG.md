# Changelog

All notable changes to this project will be documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-05-15
### Added
- Editor/agent rule exporters for Cursor (`.cursorrules`), Windsurf
  (`.windsurfrules`), Claude (`CLAUDE.md`), GitHub Copilot
  (`.github/copilot-instructions.md`), Markdown and plain text.
- `PersonalEvoTaste.export_rules(...)` and `personal-evotaste export-rules`
  for deterministic rule-file generation.
- Single-level `undo()` API and `personal-evotaste undo` CLI command to
  recover from accidental evolution.
- `evolve(..., dry_run=True)` and `personal-evotaste evolve --dry-run` for
  previewing extracted/reinforced rules without mutating memory.
- Pluggable similarity strategies: `SimilarityStrategy`,
  `SequenceMatcherSimilarity`, `TokenCosineSimilarity`, and
  `EmbeddingCosineSimilarity`.
- Optional `semantic` extra for projects that want heavier embedding stacks.

### Changed
- Memory schema version bumped to `2` and now stores a one-level undo snapshot.
- Package version is now sourced dynamically from `personal_evotaste.version`.

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
