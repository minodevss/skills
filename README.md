# Skills

Agent skills by [minodevss](https://github.com/minodevss), packaged in the
[Agent Skills](https://agentskills.io/) format and installable with the
[skills CLI](https://skills.sh/docs).

## Install

```sh
npx skills add minodevss/skills --skill devin-maxxing
```

Add `-g` to install globally, or `-a claude-code` to select a specific agent.
List the available skills without installing:

```sh
npx skills add minodevss/skills --list
```

## Available skills

| Skill | Purpose |
| --- | --- |
| [devin-maxxing](skills/devin-maxxing/SKILL.md) | Put free SWE-2 Max capacity to work through parallel implementation, competing designs, adversarial review, and verified integration. |

### devin-maxxing

Requires an authenticated Devin CLI, Python 3.10+, and macOS or Linux.
The runner checks that the exact requested model is advertised as **Free**
before every launch or resume. It stops if pricing cannot be verified and
never silently switches models.

Ask your agent to use it:

> Use devin-maxxing to implement this feature with parallel Devin workers,
> then integrate and verify the result.

> devin-maxxing으로 독립 작업을 병렬 구현하고, 반례 검토와 최종 검증까지 해줘.

Workers use `--permission-mode dangerous` for unattended execution. This
bypasses interactive CLI approval prompts, so each assignment must have an
explicit scope and authorization boundary. Do not combine it with
`--sandbox`. Free model availability and service limits can change.

Run the bundled preflight without starting a worker:

```sh
python3 skills/devin-maxxing/scripts/run_task.py --check
```

Prompts, logs, and exports stay outside the repository, under
`$XDG_STATE_HOME/devin-maxxing` or `~/.local/state/devin-maxxing` by default.
The workflow is independent of programming language or framework.

## Repository layout

```text
skills/
  devin-maxxing/
    SKILL.md
    LICENSE
    scripts/
      run_task.py
tests/
  test_devin_maxxing.py
scripts/
  validate_skills.py
```

Each installable skill is self-contained under `skills/<name>/`. Repository
tests and validation tooling are kept outside the installed skill payload.
No package manifest or plugin marketplace configuration is required.

## Development

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
.venv/bin/python scripts/validate_skills.py
.venv/bin/python -m unittest discover -s tests -v
```

Validate CLI discovery against a local checkout:

```sh
DISABLE_TELEMETRY=1 npx skills add . --list
```

The tests use a synthetic Devin executable in temporary directories. They
exercise pricing guards, exact-session resume, duplicate-run protection,
and timeout cleanup without starting real agents or spending model tokens.
They do not measure the quality of real worker output.

## License

[MIT](LICENSE). Each skill includes its license so it travels with an installation.
