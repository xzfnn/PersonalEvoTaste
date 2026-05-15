from __future__ import annotations

import pytest

from personal_evotaste.exceptions import ConfigurationError
from personal_evotaste.exporters import SUPPORTED_FORMATS, render_rules
from personal_evotaste.models import TasteRule


@pytest.fixture
def rules():
    return [
        TasteRule(rule="Prefer monochrome brutalist typography", reason="Too loud", project="acme", weight=1.96, hits=2),
        TasteRule(rule="Avoid one-letter variable names", reason="Hard to read", project="acme"),
    ]


@pytest.mark.parametrize("fmt", SUPPORTED_FORMATS)
def test_render_supports_all_formats(fmt: str, rules):
    out = render_rules(rules, fmt=fmt)
    assert "monochrome" in out
    assert "Avoid one-letter variable names" in out
    assert out.endswith("\n")


def test_render_empty_returns_placeholder():
    out = render_rules([], fmt="markdown")
    assert "No taste rules" in out


def test_render_unknown_format_raises(rules):
    with pytest.raises(ConfigurationError):
        render_rules(rules, fmt="emacs")


@pytest.mark.parametrize("fmt", ["cursor", "windsurf", "claude", "copilot"])
def test_editor_headers_present(fmt: str, rules):
    out = render_rules(rules, fmt=fmt)
    # Each tool gets its own header; they must mention something tool-specific
    # or the generic "PersonalEvoTaste" attribution.
    assert "PersonalEvoTaste" in out or "preferences" in out.lower()


def test_export_via_facade(tmp_path):
    from personal_evotaste import PersonalEvoTaste

    taste = PersonalEvoTaste(memory_path=tmp_path / "m.yaml", decay=0.0)
    taste.evolve("x", "Prefer four-space indentation everywhere", "p")
    md = taste.export_rules(fmt="cursor")
    assert "four-space" in md
