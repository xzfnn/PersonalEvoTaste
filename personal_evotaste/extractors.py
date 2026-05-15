"""Strategies for turning raw user feedback into a :class:`TasteRule`.

The default extractor is a deterministic heuristic so the library works
fully offline.  Power-users can plug an LLM-backed extractor (see
:class:`CallableExtractor`) without changing the core API.
"""
from __future__ import annotations

import re
from abc import ABC, abstractmethod
from difflib import SequenceMatcher
from typing import Callable, Iterable, List, Optional

from .exceptions import ExtractionError
from .models import TasteRule

_STOPWORDS = {
    "the", "a", "an", "is", "are", "was", "were", "of", "to", "and", "or",
    "but", "this", "that", "it", "i", "we", "you", "please", "could", "would",
    "should", "make", "do", "be", "more", "less", "very", "too", "really",
}

_SIMILARITY_THRESHOLD = 0.78


class RuleExtractor(ABC):
    """Abstract base class for rule extractors."""

    @abstractmethod
    def extract(
        self,
        *,
        agent_output: str,
        user_feedback: str,
        project: str = "",
        tags: Optional[Iterable[str]] = None,
    ) -> TasteRule: ...


class HeuristicExtractor(RuleExtractor):
    """A dependency-free extractor based on simple NLP heuristics."""

    _SENT_SPLIT = re.compile(r"(?<=[.!?。！？])\s+|\n+")

    def extract(
        self,
        *,
        agent_output: str,
        user_feedback: str,
        project: str = "",
        tags: Optional[Iterable[str]] = None,
    ) -> TasteRule:
        feedback = (user_feedback or "").strip()
        if not feedback:
            raise ExtractionError("user_feedback must not be empty")

        rule_text = self._summarise(feedback)
        return TasteRule(
            rule=rule_text,
            reason=feedback,
            project=project,
            tags=list(tags or []),
        )

    # ------------------------------------------------------------------
    def _summarise(self, feedback: str) -> str:
        # Pick the most informative sentence then trim it.
        sentences = [s.strip() for s in self._SENT_SPLIT.split(feedback) if s.strip()]
        if not sentences:
            sentences = [feedback]
        sentence = max(sentences, key=self._informativeness)
        sentence = re.sub(r"\s+", " ", sentence).strip(" .,!?。！？")
        if len(sentence) > 140:
            sentence = sentence[:137].rstrip() + "..."
        return f"Prefer: {sentence}"

    @staticmethod
    def _informativeness(text: str) -> int:
        tokens = re.findall(r"\w+", text.lower())
        return sum(1 for t in tokens if t not in _STOPWORDS)


class CallableExtractor(RuleExtractor):
    """Adapter that lets users plug a function (e.g. an LLM call)."""

    def __init__(self, fn: Callable[[str, str, str], str]) -> None:
        self._fn = fn

    def extract(
        self,
        *,
        agent_output: str,
        user_feedback: str,
        project: str = "",
        tags: Optional[Iterable[str]] = None,
    ) -> TasteRule:
        try:
            rule_text = self._fn(agent_output, user_feedback, project)
        except Exception as exc:  # pragma: no cover - user code
            raise ExtractionError(f"Custom extractor failed: {exc}") from exc
        if not rule_text:
            raise ExtractionError("Custom extractor returned an empty rule")
        return TasteRule(
            rule=rule_text.strip(),
            reason=user_feedback,
            project=project,
            tags=list(tags or []),
        )


# ---------------------------------------------------------------------------
# Deduplication helpers
# ---------------------------------------------------------------------------

def find_similar_rule(new_rule: TasteRule, existing: List[TasteRule]) -> Optional[TasteRule]:
    """Return the closest existing rule above the similarity threshold."""
    best: Optional[TasteRule] = None
    best_ratio = 0.0
    for r in existing:
        ratio = SequenceMatcher(None, r.rule.lower(), new_rule.rule.lower()).ratio()
        if ratio > best_ratio:
            best_ratio = ratio
            best = r
    if best is not None and best_ratio >= _SIMILARITY_THRESHOLD:
        return best
    return None
