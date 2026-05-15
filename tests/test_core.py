from __future__ import annotations

from pathlib import Path

import pytest

from personal_evotaste import PersonalEvoTaste
from personal_evotaste.exceptions import ConfigurationError
from personal_evotaste.storage import YAMLStorage


def test_inject_taste_without_rules(taste):
    out = taste.inject_taste("base", context="ctx")
    assert "base" in out
    assert "No taste rules yet" in out


def test_evolve_adds_and_persists(yaml_memory: Path, taste):
    rule = taste.evolve(
        agent_output="flashy login page",
        user_feedback="Prefer calm monochrome brutalist typography",
        project_name="acme",
    )
    assert rule.id
    # Reload from disk to confirm persistence.
    fresh = PersonalEvoTaste(memory_path=yaml_memory)
    assert len(fresh.rules) == 1
    assert fresh.rules[0].project == "acme"


def test_evolve_deduplicates_and_reinforces(taste):
    r1 = taste.evolve("x", "Prefer calm monochrome brutalist typography", "p")
    r2 = taste.evolve("y", "Prefer calm monochrome brutalist typography!", "p")
    assert r1.id == r2.id
    assert r2.hits >= 2


def test_inject_taste_uses_top_rules(taste):
    taste.evolve("x", "Prefer four-space indentation everywhere", "p")
    taste.evolve("x", "Avoid one-letter variable names", "p")
    out = taste.inject_taste("Write a function")
    assert "PersonalEvoTaste" in out
    assert "Prefer" in out


def test_remove_rule_persists(yaml_memory: Path, taste):
    r = taste.evolve("x", "Prefer descriptive docstrings on public APIs", "p")
    assert taste.remove_rule(r.id) is True
    fresh = PersonalEvoTaste(memory_path=yaml_memory)
    assert fresh.rules == []


def test_reset(taste):
    taste.evolve("x", "Prefer descriptive docstrings", "p")
    taste.reset()
    assert taste.rules == []


def test_conflicting_args_raise(tmp_path: Path):
    with pytest.raises(ConfigurationError):
        PersonalEvoTaste(memory_path=tmp_path / "a.yaml", storage=YAMLStorage(tmp_path / "b.yaml"))


def test_invalid_decay_raises(tmp_path: Path):
    with pytest.raises(ConfigurationError):
        PersonalEvoTaste(memory_path=tmp_path / "a.yaml", decay=1.0)


def test_decay_applied(tmp_path: Path):
    t = PersonalEvoTaste(memory_path=tmp_path / "m.yaml", decay=0.5)
    t.evolve("x", "Prefer descriptive docstrings", "p")
    w_before = t.rules[0].weight
    t.evolve("x", "Use simple, declarative configuration files", "p")
    # The first rule should have decayed once.
    first = [r for r in t.rules if "docstring" in r.rule.lower()][0]
    assert first.weight < w_before
