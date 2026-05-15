from __future__ import annotations

import pytest

from personal_evotaste.exceptions import ExtractionError
from personal_evotaste.extractors import (
    CallableExtractor,
    HeuristicExtractor,
    find_similar_rule,
)
from personal_evotaste.models import TasteRule


def test_heuristic_picks_most_informative_sentence():
    ex = HeuristicExtractor()
    rule = ex.extract(
        agent_output="...",
        user_feedback="Too loud. Prefer calm monochrome brutalist typography.",
        project="acme",
    )
    assert "monochrome" in rule.rule.lower() or "brutalist" in rule.rule.lower()
    assert rule.project == "acme"


def test_heuristic_rejects_empty():
    ex = HeuristicExtractor()
    with pytest.raises(ExtractionError):
        ex.extract(agent_output="x", user_feedback="   ")


def test_callable_extractor():
    ex = CallableExtractor(lambda o, f, p: f"Prefer: {f[:10]}")
    rule = ex.extract(agent_output="x", user_feedback="be quieter", project="p")
    assert rule.rule.startswith("Prefer:")
    assert rule.project == "p"


def test_callable_extractor_empty_raises():
    ex = CallableExtractor(lambda o, f, p: "")
    with pytest.raises(ExtractionError):
        ex.extract(agent_output="x", user_feedback="y")


def test_find_similar_rule_threshold():
    existing = [TasteRule(rule="Prefer monochrome brutalist typography")]
    near = TasteRule(rule="prefer monochrome brutalist typography!")
    far = TasteRule(rule="Use neon gradients everywhere")
    assert find_similar_rule(near, existing) is existing[0]
    assert find_similar_rule(far, existing) is None
