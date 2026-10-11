#!/usr/bin/env python3
import argparse
from collections import Counter
import difflib
import json
from pathlib import Path
import re
import sys

FENCED = re.compile(r"^\s*(```|~~~)[^\n]*\n.*?^\s*\1\s*$", re.MULTILINE | re.DOTALL)
INLINE_CODE = re.compile(r"`[^`\n]+`")
LINK_TARGET = re.compile(r"\]\(([^)\s]+)")
URL = re.compile(r"https?://[^\s)>\]}\"']+")
LIST_MARKER = re.compile(r"^\s*\d+[.)]\s", re.MULTILINE)
NUMBER = re.compile(r"\d+(?:[.,]\d+)*")
ACRONYM = re.compile(r"\b[A-Z][A-Z0-9]+(?:-[A-Z0-9]+)*\b")
SENTENCE = re.compile(r"(?<=[.!?。])\s+|\n+")
HEDGE = re.compile(r"\b(?:not|no|never|none|nor|without|cannot|may|might|could|should|must|likely|unlikely"
                   r"|probably|possibly|perhaps|some|most|many|few|all|every|each|always|often|usually|rarely"
                   r"|only|almost)\b|n't\b|않|없|못|아니|(?<![가-힣])안(?=\s)|수\s?있|해야|아마|가능성|반드시"
                   r"|추정|일부|대부분|모든|모두|항상|자주|대개|거의|드물|오직|뿐", re.IGNORECASE)


def facts(text):
    blocks = [match.group(0).strip() for match in FENCED.finditer(text)]
    prose = FENCED.sub(" ", text)
    inline = INLINE_CODE.findall(prose)
    prose = INLINE_CODE.sub(" ", prose)
    targets = LINK_TARGET.findall(prose)
    urls = [url.rstrip(".,;:") for url in URL.findall(prose)]
    plain = LIST_MARKER.sub(" ", URL.sub(" ", LINK_TARGET.sub("](", prose)))
    numbers = [re.sub(r"(?<=\d),(?=\d{3}\b)", "", number) for number in NUMBER.findall(plain)]
    return {
        "code_blocks": Counter(blocks),
        "inline_code": Counter(inline),
        "urls": Counter(urls + [target for target in targets if not URL.fullmatch(target)]),
        "numbers": Counter(numbers),
        "acronyms": Counter(ACRONYM.findall(plain)),
    }, plain


def hedges(plain):
    return Counter(re.sub(r"\s+", " ", match.group(0).lower()) for match in HEDGE.finditer(plain))


def sentences(text):
    return [part.strip() for part in SENTENCE.split(FENCED.sub(" ", text)) if part.strip()]


def compare(original, rewrite):
    before, before_plain = facts(original)
    after, after_plain = facts(rewrite)
    blocking = {}
    for kind in ("code_blocks", "inline_code", "urls", "numbers"):
        if kind == "code_blocks":
            lost = sorted((before[kind] - after[kind]).elements())
            added = sorted((after[kind] - before[kind]).elements())
        else:
            lost, added = sorted(set(before[kind]) - set(after[kind])), sorted(set(after[kind]) - set(before[kind]))
        if lost or added:
            blocking[kind] = {"lost": lost, "added": added}
    warnings = {}
    for kind, old, new in (("acronyms", before["acronyms"], after["acronyms"]),
                           ("hedges", hedges(before_plain), hedges(after_plain))):
        lost, added = sorted((old - new).elements()), sorted((new - old).elements())
        if lost or added:
            warnings[kind] = {"lost": lost, "added": added}
    original_sentences = sentences(original)
    kept = set(sentences(rewrite))
    touched = sum(1 for sentence in original_sentences if sentence not in kept)
    stats = {
        "similarity": round(difflib.SequenceMatcher(None, original, rewrite, autojunk=False).ratio(), 3),
        "sentences_touched": f"{touched}/{len(original_sentences)}",
        "touched_ratio": round(touched / len(original_sentences), 3) if original_sentences else 0.0,
        "length_ratio": round(len(rewrite) / len(original), 3) if original else None,
    }
    return {"blocking": blocking, "warnings": warnings, "stats": stats}


def main():
    parser = argparse.ArgumentParser(description="Check that a rewrite kept the original's facts. Exits 1 when "
                                                 "code, URLs, or numbers were lost or added.")
    parser.add_argument("original", type=Path)
    parser.add_argument("rewrite", type=Path)
    parser.add_argument("--json", action="store_true", help="print machine-readable output")
    args = parser.parse_args()
    try:
        result = compare(args.original.read_text(encoding="utf-8"), args.rewrite.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError) as error:
        print(f"compare.py: {error}", file=sys.stderr)
        return 2
    if args.json:
        json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
        print()
    else:
        for kind, change in result["blocking"].items():
            print(f"BLOCK {kind}: lost {change['lost']} added {change['added']}")
        for kind, change in result["warnings"].items():
            print(f"CHECK {kind}: lost {change['lost']} added {change['added']}")
        stats = result["stats"]
        print(f"similarity {stats['similarity']}, sentences touched {stats['sentences_touched']}"
              f" ({stats['touched_ratio']:.0%}), length ratio {stats['length_ratio']}")
        if not result["blocking"]:
            print("No code, URL, or number changed.")
    return int(bool(result["blocking"]))


if __name__ == "__main__":
    raise SystemExit(main())
