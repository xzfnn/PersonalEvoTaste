"""End-to-end demo: evolve a few rules and inject them into a prompt.

Run with:
    python examples/demo.py
"""
from __future__ import annotations

from pathlib import Path

from personal_evotaste import PersonalEvoTaste

MEMORY = Path(__file__).with_name("demo_memory.yaml")


def main() -> None:
    # Use a local file so the demo is reproducible and easy to clean up.
    if MEMORY.exists():
        MEMORY.unlink()

    taste = PersonalEvoTaste(memory_path=MEMORY)

    print("== 1) Inject before any rules ==")
    print(taste.inject_taste("Generate a login page", context="brutalist minimal project"))

    print("\n== 2) Evolve from feedback ==")
    taste.evolve(
        agent_output="A flashy gradient login page with neon buttons",
        user_feedback="Too loud. Prefer calm monochrome brutalist typography.",
        project_name="acme-landing",
    )
    taste.evolve(
        agent_output="def f(x): return x",
        user_feedback="Avoid one-letter variable names; prefer descriptive identifiers.",
        project_name="acme-landing",
    )
    # Reinforce the first rule with a near-duplicate phrasing.
    taste.evolve(
        agent_output="...",
        user_feedback="prefer calm monochrome brutalist typography!",
        project_name="acme-landing",
    )

    print("\n== 3) Current top rules ==")
    for r in taste.top_rules():
        print(f"  - w={r.weight:.2f} hits={r.hits} :: {r.rule}")

    print("\n== 4) Inject after evolution ==")
    print(taste.inject_taste("Generate a signup page", context="acme-landing"))

    print(f"\nMemory persisted to: {MEMORY}")


if __name__ == "__main__":
    main()