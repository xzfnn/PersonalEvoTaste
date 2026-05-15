from __future__ import annotations

from pathlib import Path

from personal_evotaste.cli import main


def test_cli_evolve_then_list(tmp_path: Path, capsys):
    mem = str(tmp_path / "m.yaml")
    assert main([
        "--memory", mem,
        "evolve",
        "--output", "flashy page",
        "--feedback", "Prefer calm monochrome brutalist typography",
        "--project", "acme",
    ]) == 0
    capsys.readouterr()

    assert main(["--memory", mem, "list"]) == 0
    captured = capsys.readouterr().out
    assert "Prefer" in captured


def test_cli_inject(tmp_path: Path, capsys):
    mem = str(tmp_path / "m.yaml")
    main([
        "--memory", mem,
        "evolve",
        "--output", "x",
        "--feedback", "Prefer four-space indentation",
        "--project", "p",
    ])
    capsys.readouterr()
    rc = main(["--memory", mem, "inject", "Write a function"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "Write a function" in out
    assert "PersonalEvoTaste" in out


def test_cli_reset(tmp_path: Path, capsys):
    mem = str(tmp_path / "m.yaml")
    main(["--memory", mem, "evolve", "--output", "x", "--feedback", "Prefer X", "--project", "p"])
    capsys.readouterr()
    assert main(["--memory", mem, "reset"]) == 0
    assert main(["--memory", mem, "list"]) == 0
    assert "no rules" in capsys.readouterr().out.lower()
