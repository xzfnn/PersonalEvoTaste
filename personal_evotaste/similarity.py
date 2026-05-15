"""Similarity strategies used to deduplicate evolving taste rules.

The default strategy intentionally stays lightweight.  Projects that need
semantic similarity can plug an embedding function without forcing heavy
machine-learning dependencies on everyone.
"""
from __future__ import annotations

import math
import re
from abc import ABC, abstractmethod
from collections import Counter
from difflib import SequenceMatcher
from typing import Callable, Iterable, List, Optional, Sequence

from .models import TasteRule

_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def _tokens(text: str) -> List[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text)]


class SimilarityStrategy(ABC):
    """Contract for rule similarity backends."""

    threshold: float

    @abstractmethod
    def score(self, left: str, right: str) -> float:
        """Return a similarity score in ``[0, 1]``."""

    def find_similar(self, new_rule: TasteRule, existing: Iterable[TasteRule]) -> Optional[TasteRule]:
        best: Optional[TasteRule] = None
        best_score = 0.0
        for rule in existing:
            score = self.score(rule.rule, new_rule.rule)
            if score > best_score:
                best_score = score
                best = rule
        if best is not None and best_score >= self.threshold:
            return best
        return None


class SequenceMatcherSimilarity(SimilarityStrategy):
    """Character-level similarity using :class:`difflib.SequenceMatcher`."""

    def __init__(self, threshold: float = 0.78) -> None:
        self.threshold = threshold

    def score(self, left: str, right: str) -> float:
        return SequenceMatcher(None, left.lower(), right.lower()).ratio()


class TokenCosineSimilarity(SimilarityStrategy):
    """Bag-of-words cosine similarity with zero external dependencies."""

    def __init__(self, threshold: float = 0.74) -> None:
        self.threshold = threshold

    def score(self, left: str, right: str) -> float:
        a = Counter(_tokens(left))
        b = Counter(_tokens(right))
        if not a or not b:
            return 0.0
        dot = sum(a[t] * b[t] for t in a.keys() & b.keys())
        norm_a = math.sqrt(sum(v * v for v in a.values()))
        norm_b = math.sqrt(sum(v * v for v in b.values()))
        if norm_a == 0.0 or norm_b == 0.0:
            return 0.0
        return dot / (norm_a * norm_b)


class EmbeddingCosineSimilarity(SimilarityStrategy):
    """Cosine similarity over user-provided embeddings.

    ``embed`` should return a vector for a piece of text.  This adapter is
    deliberately dependency-free: you can pass OpenAI embeddings,
    sentence-transformers, a local model, or any in-house vectorizer.
    """

    def __init__(self, embed: Callable[[str], Sequence[float]], threshold: float = 0.86) -> None:
        self.embed = embed
        self.threshold = threshold

    def score(self, left: str, right: str) -> float:
        return _cosine(self.embed(left), self.embed(right))


def _cosine(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right) or not left:
        return 0.0
    dot = sum(a * b for a, b in zip(left, right))
    norm_a = math.sqrt(sum(a * a for a in left))
    norm_b = math.sqrt(sum(b * b for b in right))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    value = dot / (norm_a * norm_b)
    return max(0.0, min(1.0, value))


def find_similar_rule(
    new_rule: TasteRule,
    existing: List[TasteRule],
    strategy: Optional[SimilarityStrategy] = None,
) -> Optional[TasteRule]:
    """Backward-compatible helper for finding similar rules."""
    return (strategy or SequenceMatcherSimilarity()).find_similar(new_rule, existing)
