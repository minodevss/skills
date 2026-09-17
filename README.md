# Skills

A collection of [Agent Skills](https://agentskills.io/), installable with the [skills CLI](https://skills.sh/docs).

## Install

```sh
npx skills add minodevss/skills
```

Use `--skill <name>` to select a skill, `-g` for a global installation, or `--list` to list available skills.

## Skills

| Name | Description |
| --- | --- |
| [commit](skills/commit/SKILL.md) | Atomic commits, pushes, pull requests, and merges after verification. |
| [devin-maxxing](skills/devin-maxxing/SKILL.md) | Parallel implementation and review with Devin CLI and free SWE-2 Max models. |

Requirements and usage are documented in each skill.

## Add a skill

1. Create `skills/<name>/SKILL.md` with `name` and `description` frontmatter. The name must match its directory.
2. Keep runtime scripts, references, and assets inside the skill directory. Include a `LICENSE` file; installed skills must work independently of this repository.
3. Add the skill to the table above and place tests in `tests/`.
4. Run the checks below.

Repository-wide validation tools belong in `scripts/`. Skill-specific scripts belong in `skills/<name>/scripts/`.

## Validate

Requires Python 3.10 or later.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/validate_skills.py
.venv/bin/python -m unittest discover -s tests -v
```

Check local discovery:

```sh
DISABLE_TELEMETRY=1 npx skills add . --list
```

## License

[MIT](LICENSE).
