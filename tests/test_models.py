from __future__ import annotations

import pytest
from pydantic import ValidationError

from personal_evotaste.models import TasteMemory, TasteRule


def test_taste_rule_defaults():
    r = TasteRule(rule="Prefer monochrome UI")
    assert r.weight == 1.0
    assert r.hits == 1
    assert r.id and len(r.id) == 12


def test_taste_rule_rejects_empty():
    with pytest.raises(ValidationError):
        TasteRule(rule="")


def test_taste_rule_reinforce():
    r = TasteRule(rule="x")
    before = r.updated_at
    r.reinforce(delta=0.5)
    assert r.hits == 2
    assert r.weight == pytest.approx(1.5)
    assert r.updated_at >= before


def test_memory_top_rules_sorted_by_weight():
    mem = TasteMemory(taste_rules=[
        TasteRule(rule="a", weight=0.5),
        TasteRule(rule="b", weight=2.0),
        TasteRule(rule="c", weight=1.0),
    ])
    assert [r.rule for r in mem.top_rules()] == ["b", "c", "a"]


def test_memory_remove_rule():
    r = TasteRule(rule="x")
    mem = TasteMemory(taste_rules=[r])
    assert mem.remove_rule(r.id) is True
    assert mem.remove_rule(r.id) is False
