"""Command line interface for PersonalEvoTaste.

Implemented with :mod:`argparse` so it works with zero extra dependencies.
"""
from __future__ import annotations

import argparse
import json
import sys
from typing import List, Optional

from .core import PersonalEvoTaste
from .version import __version__


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="personal-evotaste",
        description="Developer personal-taste memory & self-evolution engine.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--memory",
        "-m",
        default="personal_taste_memory.yaml",
        help="Path to the memory file (default: %(default)s).",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    p_inject = sub.add_parser("inject", help="Print a prompt with taste rules injected.")
    p_inject.add_argument("prompt", help="Base prompt text.")
    p_inject.add_argument("--context", default="", help="Optional project context.")
    p_inject.add_argument("--project", default=None, help="Filter rules by project.")
    p_inject.add_argument("--limit", type=int, default=10)

    p_evolve = sub.add_parser("evolve", help="Distill a new rule from feedback.")
    p_evolve.add_argument("--output", required=True, help="Agent output that was reviewed.")
    p_evolve.add_argument("--feedback", required=True, help="The user feedback to learn from.")
    p_evolve.add_argument("--project", default="", help="Project name for context.")
    p_evolve.add_argument("--tag", action="append", default=[], help="Add a tag (repeatable).")

    p_list = sub.add_parser("list", help="List currently stored rules.")
    p_list.add_argument("--limit", type=int, default=20)
    p_list.add_argument("--project", default=None)
    p_list.add_argument("--json", action="store_true", help="Emit JSON instead of text.")

    p_rm = sub.add_parser("remove", help="Remove a rule by id.")
    p_rm.add_argument("rule_id")

    sub.add_parser("reset", help="Wipe the memory (irreversible).")
    sub.add_parser("export", help="Print the full memory as JSON.")

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    taste = PersonalEvoTaste(memory_path=args.memory)

    if args.command == "inject":
        print(taste.inject_taste(args.prompt, args.context, project=args.project, limit=args.limit))
        return 0

    if args.command == "evolve":
        rule = taste.evolve(
            agent_output=args.output,
            user_feedback=args.feedback,
            project_name=args.project,
            tags=args.tag,
        )
        print(f"OK rule_id={rule.id} weight={rule.weight:.2f} hits={rule.hits}")
        print(f"    {rule.rule}")
        return 0

    if args.command == "list":
        rules = taste.top_rules(limit=args.limit, project=args.project)
        if args.json:
            print(json.dumps([r.model_dump(mode="json") for r in rules], ensure_ascii=False, indent=2))
            return 0
        if not rules:
            print("(no rules yet)")
            return 0
        for r in rules:
            project = f" [{r.project}]" if r.project else ""
            print(f"{r.id}  w={r.weight:5.2f}  hits={r.hits:3d}{project}  {r.rule}")
        return 0

    if args.command == "remove":
        ok = taste.remove_rule(args.rule_id)
        print("removed" if ok else "not found")
        return 0 if ok else 1

    if args.command == "reset":
        taste.reset()
        print("memory cleared")
        return 0

    if args.command == "export":
        print(json.dumps(taste.export_dict(), ensure_ascii=False, indent=2))
        return 0

    parser.error(f"Unknown command: {args.command}")
    return 2  # pragma: no cover


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
