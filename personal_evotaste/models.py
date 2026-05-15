"""Typed data models for the PersonalEvoTaste memory.

Pydantic v2 is used so that we get JSON-schema generation, validation
and (de)serialisation for free.  These models form the on-disk contract
of the library - bumping any of them is a breaking change.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_id() -> str:
    return uuid.uuid4().hex[:12]


class TasteRule(BaseModel):
    """A single distilled preference of the developer.

    Rules carry a *weight* that decays over time and is reinforced every
    time similar feedback is received.  The weight is what drives ranking
    when injecting the taste into a prompt.
    """

    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=_new_id)
    rule: str = Field(..., min_length=1, description="Short imperative rule")
    reason: str = Field("", description="Why this rule exists")
    project: str = Field("", description="Project the rule originated from")
    tags: List[str] = Field(default_factory=list)
    weight: float = Field(1.0, ge=0.0, description="Importance score")
    hits: int = Field(1, ge=1, description="Times this rule was reinforced")
    created_at: datetime = Field(default_factory=_utcnow)
    updated_at: datetime = Field(default_factory=_utcnow)

    def reinforce(self, delta: float = 1.0) -> None:
        self.hits += 1
        self.weight += delta
        self.updated_at = _utcnow()


class FeedbackEvent(BaseModel):
    """Audit-trail entry for every ``evolve`` invocation."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(default_factory=_new_id)
    project: str = ""
    agent_output: str = ""
    user_feedback: str = ""
    rule_id: Optional[str] = None
    created_at: datetime = Field(default_factory=_utcnow)


class TasteMemory(BaseModel):
    """Top-level container persisted to disk."""

    model_config = ConfigDict(extra="ignore")

    version: int = 2
    taste_rules: List[TasteRule] = Field(default_factory=list)
    history: List[FeedbackEvent] = Field(default_factory=list)
    # Single-level undo snapshot of ``taste_rules`` + ``history`` taken
    # right before the most recent ``evolve``. ``None`` means there is
    # nothing to undo.
    undo_snapshot: Optional[Dict[str, Any]] = None

    # ---- helpers -----------------------------------------------------
    def find_rule(self, rule_id: str) -> Optional[TasteRule]:
        return next((r for r in self.taste_rules if r.id == rule_id), None)

    def remove_rule(self, rule_id: str) -> bool:
        for i, r in enumerate(self.taste_rules):
            if r.id == rule_id:
                self.taste_rules.pop(i)
                return True
        return False

    def top_rules(self, limit: int = 10, project: Optional[str] = None) -> List[TasteRule]:
        rules = self.taste_rules
        if project:
            rules = [r for r in rules if r.project == project or not r.project]
        return sorted(rules, key=lambda r: r.weight, reverse=True)[:limit]
