from __future__ import annotations

from personal_evotaste.models import TasteRule
from personal_evotaste.similarity import (
    EmbeddingCosineSimilarity,
    SequenceMatcherSimilarity,
    TokenCosineSimilarity,
    find_similar_rule,
)


def test_sequence_matcher_similarity_finds_near_duplicate():
    strategy = SequenceMatcherSimilarity(threshold=0.75)
    existing = [TasteRule(rule="Prefer calm monochrome brutalist typography")]
    new = TasteRule(rule="prefer calm monochrome brutalist typography!")
    assert strategy.find_similar(new, existing) is existing[0]


def test_token_cosine_similarity_scores_shared_tokens():
    strategy = TokenCosineSimilarity(threshold=0.5)
    assert strategy.score("prefer calm monochrome UI", "calm monochrome interface") >= 0.5
    assert strategy.score("prefer calm monochrome UI", "ship faster builds") < 0.5


def test_embedding_cosine_similarity():
    vectors = {
        "a": [1.0, 0.0],
        "b": [1.0, 0.0],
        "c": [0.0, 1.0],
    }
    strategy = EmbeddingCosineSimilarity(lambda text: vectors[text], threshold=0.9)
    assert strategy.score("a", "b") == 1.0
    assert strategy.score("a", "c") == 0.0


def test_backward_compatible_find_similar_rule():
    existing = [TasteRule(rule="Prefer descriptive identifiers")]
    new = TasteRule(rule="Prefer descriptive identifiers!")
    assert find_similar_rule(new, existing) is existing[0]
