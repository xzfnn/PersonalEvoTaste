# Architecture

PersonalEvoTaste is intentionally small. The goal is to provide a *durable,
typed memory of developer taste* that any LLM agent can consume, without
forcing users to adopt a particular model or framework.

## Components

```
┌────────────────────┐
│ PersonalEvoTaste   │   high-level façade
│   .inject_taste()  │
│   .evolve()        │
└────────┬───────────┘
         │ uses
         ▼
┌────────────────────┐    ┌──────────────────────┐
│ RuleExtractor      │    │ BaseStorage          │
│ (Heuristic / LLM)  │    │ (YAML / JSON / SQLite│
└────────────────────┘    │  / custom)           │
                          └──────────┬───────────┘
                                     │
                                     ▼
                          ┌──────────────────────┐
                          │ TasteMemory (pydantic│
                          │  rules + history)    │
                          └──────────────────────┘
```

## Why a façade?

`PersonalEvoTaste` owns the *policy* (decay, deduplication, persistence
cadence) while extractors and storage own the *mechanism*. This lets users
swap any one piece without forking the project.

## Rule lifecycle

1. **Extract** — `RuleExtractor.extract()` distils a `TasteRule` from
   `(agent_output, user_feedback, project)`.
2. **Decay** — every existing rule's weight is multiplied by `(1 - decay)`.
3. **Deduplicate** — if a near-duplicate exists (string similarity ≥ 0.78),
   we *reinforce* it instead of adding a new one.
4. **Persist** — `BaseStorage.save()` writes atomically.
5. **Audit** — a `FeedbackEvent` is appended to `memory.history`.

## Ranking & injection

`inject_taste()` selects the top-N rules by weight, optionally filtered by
project. This naturally surfaces durable, repeatedly-reinforced preferences
while letting stale ones fade out via decay.

## Storage contract

`BaseStorage` requires only `load()` and `save()`. The shipped file-based
backends use a *temporary sibling + atomic replace* pattern so a crash in the
middle of a write cannot corrupt the memory file. `SQLiteStorage` relies on
SQLite's own transactional guarantees.

## Forward compatibility

`TasteMemory.version` is persisted on disk. Breaking schema changes must
bump this field and ship a migration helper.
