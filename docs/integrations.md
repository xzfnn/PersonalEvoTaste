# Editor & agent integrations

PersonalEvoTaste turns evolved memory into the rule files that modern AI
coding assistants already understand. After you have evolved a few rules,
run one command to drop them into the right file and your agent will start
respecting your taste in every new chat.

## Quick reference

| Tool                | Target file                              | Command                                                        |
| ------------------- | ---------------------------------------- | -------------------------------------------------------------- |
| Cursor              | `.cursorrules`                           | `personal-evotaste export-rules -f cursor   -o .cursorrules`   |
| Windsurf / Codeium  | `.windsurfrules`                         | `personal-evotaste export-rules -f windsurf -o .windsurfrules` |
| Claude Code         | `CLAUDE.md`                              | `personal-evotaste export-rules -f claude   -o CLAUDE.md`      |
| GitHub Copilot      | `.github/copilot-instructions.md`        | `personal-evotaste export-rules -f copilot  -o .github/copilot-instructions.md` |
| Anything else       | Markdown / plain text                    | `personal-evotaste export-rules -f markdown` / `-f text`       |

All commands accept `--project NAME` to scope the export to one project and
`--limit N` to keep the file focused on your top rules.

## Recommended workflow

1. **Use the agent normally.** When it produces something off-taste, give it
   feedback in chat as usual.
2. **Persist the lesson** with one command:
   ```bash
   personal-evotaste evolve \
     --output  "<what the agent produced>" \
     --feedback "<what you told it>" \
     --project my-app
   ```
3. **Sync the rule file** so the next session benefits:
   ```bash
   personal-evotaste export-rules -f cursor -o .cursorrules
   ```
4. **Commit it.** The export is deterministic, so diffs are clean and
   reviewable.

## Tip: a one-liner git hook

Drop this into `.git/hooks/pre-commit` (and `chmod +x`) to keep your rule
file always in sync with the memory:

```bash
#!/usr/bin/env bash
personal-evotaste export-rules -f cursor -o .cursorrules
git add .cursorrules
```

## Programmatic use

```python
from personal_evotaste import PersonalEvoTaste

taste = PersonalEvoTaste(memory_path="my_taste.yaml")
Path(".cursorrules").write_text(taste.export_rules(fmt="cursor"))
```

The `render_rules` helper is also exported if you want to render a custom
list of rules without going through the full façade.
