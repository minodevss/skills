import ast
from pathlib import Path
import re
import sys

import yaml

ROOT = Path(__file__).resolve().parents[1]
FIELDS = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}


def validate(skill_file):
    text = skill_file.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("Frontmatter must start on the first line")
    frontmatter, delimiter, body = text[4:].partition("\n---\n")
    if not delimiter:
        raise ValueError("Frontmatter must have a closing delimiter")
    fields = yaml.safe_load(frontmatter)
    if not isinstance(fields, dict) or set(fields) - FIELDS:
        raise ValueError("Frontmatter must use portable Agent Skills fields")
    name = fields.get("name")
    if not isinstance(name, str) or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError("Name must use lowercase letters, digits, and single hyphens")
    if len(name) > 64 or name != skill_file.parent.name:
        raise ValueError("Name must match the directory and contain at most 64 characters")
    description = fields.get("description")
    if not isinstance(description, str) or not 1 <= len(description.strip()) <= 1024:
        raise ValueError("Description must contain 1–1024 characters")
    if "\n" in description:
        raise ValueError("Keep the discovery description on one line")
    if not body.strip() or len(text.splitlines()) > 500:
        raise ValueError("Keep SKILL.md nonempty and within 500 lines")
    compatibility = fields.get("compatibility", "")
    if not isinstance(compatibility, str) or len(compatibility) > 500:
        raise ValueError("Compatibility must be a string of at most 500 characters")
    metadata = fields.get("metadata", {})
    if not isinstance(metadata, dict) or any(not isinstance(k, str) or not isinstance(v, str)
                                             for k, v in metadata.items()):
        raise ValueError("Metadata must map strings to strings")
    for optional in ("license", "allowed-tools"):
        if optional in fields and not isinstance(fields[optional], str):
            raise ValueError(f"{optional} must be a string")
    if fields.get("license") == "MIT":
        bundled = skill_file.parent / "LICENSE"
        if not bundled.is_file() or bundled.read_bytes() != (ROOT / "LICENSE").read_bytes():
            raise ValueError("Bundle the repository MIT license with the skill")
    for relative in re.findall(r"\]\(((?:scripts|references|assets)/[^)]+)\)", body):
        target = (skill_file.parent / relative).resolve()
        if not target.is_relative_to(skill_file.parent.resolve()) or not target.is_file():
            raise ValueError(f"Missing or out-of-skill resource: {relative}")
    for script in skill_file.parent.rglob("*.py"):
        ast.parse(script.read_text(encoding="utf-8"), filename=str(script))
    return name


def main():
    files = sorted((ROOT / "skills").rglob("SKILL.md"))
    if not files:
        print("No skills found", file=sys.stderr)
        return 1
    names = set()
    failed = False
    for skill_file in files:
        try:
            name = validate(skill_file)
            if name in names:
                raise ValueError("Skill name is duplicated")
            names.add(name)
            print(f"Validated {skill_file.relative_to(ROOT)}")
        except (ValueError, OSError, SyntaxError, yaml.YAMLError) as error:
            print(f"{skill_file.relative_to(ROOT)}: {error}", file=sys.stderr)
            failed = True
    return int(failed)


if __name__ == "__main__":
    raise SystemExit(main())
