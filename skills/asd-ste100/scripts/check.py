#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import re
import sys

LEVELS = {"review": 1, "warn": 2, "error": 3}
LIMITS = {"en": {"procedure": 20, "descriptive": 25}, "ko": {"procedure": 20, "descriptive": 25}}
PARAGRAPH_SENTENCES = 6
FENCE = re.compile(r"^\s*(```|~~~)")
HEADING = re.compile(r"^\s{0,3}#{1,6}\s")
TABLE = re.compile(r"^\s*\|")
ITEM = re.compile(r"^(\s*)(?:([-*+])|(\d+)[.)])\s+(.*)$")
INLINE_CODE = re.compile(r"`[^`\n]*`")
URL = re.compile(r"https?://\S+")
HANGUL = re.compile(r"[가-힣]")
KO_BARE = r"(?:[A-Za-z0-9]+|[가-힣]*[가-힣](?<![은는이가을를에의로와과도만서고며면다요게지까데죠듯록함음]))"
KO_NOUN_CHAIN = re.compile(rf"(?<!\S){KO_BARE}(?:\s+{KO_BARE}){{3,}}(?!\S)")
QUOTED = re.compile(r'"[^"]*"|“[^”]*”|‘[^’]*’')
UNIT = (r"(?:mm|cm|km|m|in|ft|kg|g|lb|Nm|N|kPa|MPa|Pa|bar|psi|kV|mV|V|mA|A|kW|W|GHz|MHz|kHz|Hz|ms|min|s|h"
        r"|°C|°F|°|%|mL|ml|L|rpm|KB|MB|GB|TB|ohms?|Ω)")
COUNT_AS_ONE = [
    re.compile(r'"[^"]*"|“[^”]*”'),
    re.compile(r"\([^()]*\)"),
    re.compile(rf"\b\d+(?:[.,]\d+)?\s?{UNIT}(?![A-Za-z])"),
    re.compile(r"\bNo\.\s?\d+\b"),
    re.compile(r"\b[A-Z][A-Z0-9-]+(?:\s+[A-Z][A-Z0-9-]+)+\b"),
]
ABBREVIATION = re.compile(r"(?:\b(?:e\.g|i\.e|etc|vs|Fig|Figs|No|Nos|Ref|approx|Mr|Ms|Dr|Inc|Ltd|cf)|^\d+)\.$",
                          re.IGNORECASE)
SENTENCE_END = re.compile(r"(?:(?<=[.!?])|(?<=[.!?][\"'”’)\]]))\s+(?=[\"'“‘(\[`]?[A-Z0-9가-힣`])")

IMPERATIVES = set("""
add adjust align apply attach calibrate change check choose clean clear click close connect copy create cut
delete disconnect do download drain drill enable disable enter examine fill find fit flush get give go hold
inspect install keep let lift loosen lower lubricate make measure monitor mount move note open paint pour press
pull push put raise read record refer release remove repeat replace reset restart return rotate run save select
send set start stop tap test tighten touch turn type unlock lock update upload use verify wait wipe write
""".split())
STOP = set("""
a an the this that these those and or but if when then than to of in on at by for with from into onto over
under after before during until while as is are was were be been being am do does did has have had will can
could may might must should would shall not no it its they them their he she his her we our you your i my
which who whom whose what where why how there here all each every some any more most other such only also
very so too out up down off away back
""".split()) | IMPERATIVES

RULES = []
IRREGULAR = ("built|chosen|done|drawn|driven|eaten|fallen|found|given|gone|held|hidden|kept|known|laid|left|lost|made|"
             "paid|put|read|run|said|seen|sent|set|shown|shut|spent|split|spread|struck|taken|told|thrown|worn|written")
APPROVED_ING = {"lighting", "opening", "routing", "servicing", "mating", "missing", "remaining", "something", "during"}
NOT_ING = {"thing", "things", "string", "strings", "ring", "rings", "king", "spring", "springs", "bring", "sing",
           "wing", "wings", "ceiling", "nothing", "anything", "everything", "evening", "morning", "swing", "sling",
           "warning", "warnings", "housing", "housings", "bearing", "bearings", "fitting", "fittings", "coupling",
           "couplings", "casing", "piping", "tubing", "wiring", "building", "buildings", "setting", "settings",
           "seating", "lining", "railing", "drawing", "drawings", "marking", "markings", "reading", "readings"}
SUBSTITUTES = {
    "utilize": "use", "utilise": "use", "employ": "use", "commence": "start", "initiate": "start",
    "terminate": "stop", "cease": "stop", "prior to": "before", "subsequent to": "after", "in the event of": "if",
    "ensure": "make sure", "verify": "make sure, examine", "assist": "help", "facilitate": "help", "attempt": "try",
    "obtain": "get", "however": "but", "indicate": "show", "modify": "change", "alter": "change",
    "acceptable": "permitted", "avoid": "prevent", "both": "the two", "fit": "install", "further": "more",
    "have to": "the imperative, or must", "insert": "put", "main": "primary", "need": "necessary",
    "perform": "do", "portion": "part", "press": "push", "reach": "get", "repeat": "do ... again",
    "rotate": "turn", "therefore": "thus, as a result", "once": "one time, when", "enough": "sufficient",
}


def rule(lang, level, rule_id, pattern, hint, kinds=("procedure", "descriptive"), flags=re.IGNORECASE):
    RULES.append((lang, level, rule_id, re.compile(pattern, flags), hint, kinds))


rule("en", "error", "auxiliary-construction",
     rf"\b(?:can|must|will|could|should|may|might|shall|would)\s+(?:not\s+)?be\s+(?:[a-z]+ed|{IRREGULAR})\b",
     "no modal + be + participle; use the imperative or name the actor: 'You can adjust it' (3.4)")
rule("en", "error", "modal", r"\b(?:may|might|should|shall|would)\b(?! \d)",
     "not approved; use can (possible), must (required), or possibly (uncertain), and keep any uncertainty (3.1)")
rule("en", "warn", "modal-could", r"\bcould\b", "could is approved only as the past of can (3.1)")
rule("en", "error", "progressive", r"\b(?:am|is|are|was|were|be|been|being)\s+(?:not\s+)?(?!(?:"
     + "|".join(sorted(NOT_ING | APPROVED_ING)) + r")\b)[a-z]+ing\b", "no progressive tenses (3.2)")
rule("en", "error", "perfect", rf"\b(?:has|have|had)\s+(?:not\s+)?(?:been\s+)?(?:[a-z]+ed|{IRREGULAR})\b",
     "no perfect tenses; use the simple past or simple present (3.2)")
rule("en", "warn", "passive-procedure",
     rf"\b(?:is|are|was|were|be)\s+(?:[a-z]+ly\s+)?(?:[a-z]+ed|{IRREGULAR})\b",
     "procedures use the imperative and active voice; a state such as 'the valve is closed' is permitted (3.3, 3.6)",
     kinds=("procedure",))
rule("en", "warn", "passive-descriptive",
     rf"\b(?:is|are|was|were|be)\s+(?:[a-z]+ly\s+)?(?:[a-z]+ed|{IRREGULAR})\b(?:\s+by\b)?",
     "passive only when the agent is unknown; a state (participle as adjective) is permitted (3.3, 3.6)",
     kinds=("descriptive",))
rule("en", "error", "semicolon", r";", "no semicolons; make two sentences (8.1)")
rule("en", "error", "contraction", r"\b[a-z]+(?:n't|'re|'ve|'ll|'d|'m)\b|\b(?:it|that|there|what|here)'s\b",
     "no contractions (4.2)")
rule("en", "warn", "latin-abbreviation", r"\b(?:e\.g|i\.e|etc|viz|cf)\.", "write 'for example' or list the items (GR-6)")
rule("en", "warn", "gendered-pronoun", r"\b(?:he|she|him|her|his|hers|he/she|s/he)\b",
     "use you, the operator, or another neutral noun (GR-7)")
rule("en", "warn", "unapproved-word",
     r"\b(?:" + "|".join(re.escape(word).replace(r"\ ", r"\s+") for word in sorted(SUBSTITUTES, key=len, reverse=True))
     + r")\b", "common unapproved word; see the suggested alternative and confirm in the Dictionary")
rule("en", "review", "ing-form", r"\b(?!(?:" + "|".join(sorted(NOT_ING | APPROVED_ING)) + r")\b)[a-z]{3,}ing\b",
     "-ing forms only as a technical noun or its modifier (3.5)")
rule("en", "review", "two-instructions",
     r"\b(?:and|then)\s+(?:then\s+)?(?:" + "|".join(sorted(IMPERATIVES)) + r")\s+(?:the|a|an|it|all|this|these)\b",
     "possibly two instructions; split them unless the actions happen at the same time (5.2)", kinds=("procedure",))
rule("en", "review", "condition-after-command", r"^\s*(?:" + "|".join(sorted(IMPERATIVES)) + r")\b[^.!?]*?\b(?:if|when|unless)\b",
     "put the condition first, followed by a comma (5.4)", kinds=("procedure",))

rule("ko", "warn", "ko-double-passive", r"되어(?:지|진|졌|집)|(?:보여|쓰여|불려|믿겨|나뉘어)(?:지|진|졌|집)",
     "이중 피동; 능동문이나 단순 피동으로 쓴다")
rule("ko", "warn", "ko-vague", r"적절(?:히|한)|필요\s?시|필요한\s?경우|가능한\s?한|가급적|적당(?:히|한)|어느\s?정도|충분(?:히|한)|약간",
     "모호어; 수치, 조건, 대상으로 바꾼다")
rule("ko", "warn", "ko-soft-instruction",
     r"(?:하시면|하면)\s?됩니다|(?:하는|해 주시는)\s?것이\s?좋습니다|것\s?같습니다|해\s?주시기\s?바랍니다|권장(?:합니다|드립니다)",
     "절차는 명령으로 쓴다: '확인하세요'", kinds=("procedure",))
rule("ko", "warn", "ko-etc", r"(?<![가-힣])등(?:을|이|의|에|으로|과|도)?(?=[\s.,])", "항목을 모두 쓰거나 범위를 규칙으로 쓴다")
rule("ko", "warn", "ko-empty-verb", r"(?:수행|진행|실시)(?:하|되|합|됩|했|됐|함|됨|해|돼)",
     "빈 한자어 동사; 실제 동작을 쓴다: '초기화를 수행합니다'는 '초기화합니다'")
rule("ko", "warn", "ko-needless-passive", r"요구됩니다|요구된다|(?:개선|향상|감소|증가|발전|변화)시(?:키|켜|킨|킵|켰)|에\s?의(?:해|하여|한)\s",
     "불필요한 피동·사동; 행위자를 주어로 쓴다")
rule("ko", "warn", "ko-noun-instruction", r"(?:할|하지\s?말|않을)\s?것(?:\.|$)",
     "명사형 지시; '하세요', '하지 마세요'로 쓴다", kinds=("procedure",))
rule("ko", "review", "ko-translationese", r"(?:을|를)\s?통(?:해|하여)|에\s?(?:대한|대해)|에\s?있어(?:서)?|(?:을|를)\s?필요로",
     "번역투일 수 있다; 더 직접적인 구조로 쓸 수 있는지 본다")
rule("ko", "review", "ko-tilde-range", r"\d\s?~\s?\d",
     "범위의 끝값 포함 여부가 분명한지 확인한다: '3 이상 5 이하'")
rule("ko", "error", "semicolon", r";", "세미콜론 대신 문장을 나눈다")
ORDERED = sorted(RULES, key=lambda item: -LEVELS[item[1]])


def is_korean(text):
    return len(HANGUL.findall(text)) * 3 > len(re.findall(r"[A-Za-z]", text))


def words(sentence, korean):
    cleaned = URL.sub("X", INLINE_CODE.sub("X", sentence))
    for pattern in COUNT_AS_ONE:
        cleaned = pattern.sub("X", cleaned)
    if korean:
        return [token for token in cleaned.split() if re.search(r"\w", token)]
    return [token for token in re.split(r"\s+", cleaned) if re.search(r"\w", token)]


def sentences(text):
    parts = []
    for part in SENTENCE_END.split(text):
        if parts and ABBREVIATION.search(parts[-1]):
            parts[-1] += " " + part
        else:
            parts.append(part)
    return [part.strip() for part in parts if part.strip()]


def kind_of(sentence, block_kind, korean):
    if block_kind == "procedure":
        return "procedure"
    if korean:
        return "procedure" if re.search(r"(?:하세요|하십시오|십시오|세요|하라|해라)[.!]?$", sentence) else "descriptive"
    first = re.sub(r"^[^A-Za-z]+", "", sentence).split(" ", 1)[0].lower()
    return "procedure" if first in IMPERATIVES else "descriptive"


def noun_clusters(sentence):
    run = []
    found = []
    for token in re.findall(r"[A-Za-z][A-Za-z0-9-]*|[^\sA-Za-z]", INLINE_CODE.sub(" , ", sentence)):
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9-]*", token) and token.lower() not in STOP and not token.lower().endswith("ly"):
            run.append(token)
            continue
        if len(run) >= 4:
            found.append(" ".join(run))
        run = []
    if len(run) >= 4:
        found.append(" ".join(run))
    return found


def check_sentence(sentence, kind, korean):
    hits = []
    lang = "ko" if korean else "en"
    count = len(words(sentence, korean))
    limit = LIMITS[lang][kind]
    if count > limit:
        unit = "eojeol" if korean else "words"
        hits.append(("error", f"{kind}-length", f"{count} {unit}",
                     f"{kind} sentences stay within {limit} {unit}; split it, do not delete words to fit"))
    spans = []
    for rule_lang, level, rule_id, pattern, hint, kinds in ORDERED:
        if rule_lang not in (lang, "any") or kind not in kinds:
            continue
        for match in pattern.finditer(QUOTED.sub(lambda quote: " " * len(quote.group(0)), INLINE_CODE.sub(" ", sentence))):
            start, end = match.span()
            if any(start < other_end and other_start < end for other_start, other_end in spans):
                continue
            spans.append((start, end))
            text = match.group(0).strip()
            if rule_id == "unapproved-word":
                hint = f"write '{SUBSTITUTES[re.sub(r'\s+', ' ', text.lower())]}' instead; confirm in the Dictionary"
            hits.append((level, rule_id, text, hint))
    if korean:
        for chain in KO_NOUN_CHAIN.findall(QUOTED.sub(" ", INLINE_CODE.sub(" ", sentence))):
            hits.append(("review", "ko-noun-chain", chain.strip(),
                         "명사가 넷 이상 이어진다; 조사나 어미로 관계를 밝힌다"))
    else:
        for cluster in noun_clusters(sentence):
            hits.append(("review", "noun-cluster", cluster,
                         "possible noun cluster over 3 words; break it with a preposition or name it once"))
    return hits, count


def blocks(lines):
    fenced = False
    front_matter = False
    current = None
    for number, line in enumerate(lines, 1):
        line = re.sub(r"^\s*>\s?", "", line)
        if number == 1 and line.strip() == "---":
            front_matter = True
            continue
        if front_matter:
            front_matter = line.strip() != "---"
            continue
        if FENCE.match(line):
            fenced = not fenced
            current = None
            continue
        if fenced or not line.strip() or HEADING.match(line) or TABLE.match(line):
            if current:
                yield current
            current = None
            continue
        item = ITEM.match(line)
        if item:
            if current:
                yield current
            current = {"line": number, "kind": "procedure" if item.group(3) else "list", "text": item.group(4)}
            continue
        text = line.strip()
        if current is None:
            current = {"line": number, "kind": "paragraph", "text": text}
        else:
            current["text"] += " " + text
    if current:
        yield current


def check_text(path, text, mode):
    findings = []
    stats = {"sentences": 0, "longest": 0}
    for block in blocks(text.splitlines()):
        if re.match(r"^(?:Contents|목차)\s*:", block["text"]):
            continue
        korean = is_korean(block["text"])
        parts = sentences(block["text"])
        block_kind = "procedure" if mode == "procedure" or block["kind"] == "procedure" else None
        if mode == "descriptive":
            block_kind = "descriptive"
        for sentence in parts:
            kind = block_kind or kind_of(sentence, None, korean)
            hits, count = check_sentence(sentence, kind, korean)
            stats["sentences"] += 1
            stats["longest"] = max(stats["longest"], count)
            for level, rule_id, match, hint in hits:
                findings.append({"path": path, "line": block["line"], "level": level, "rule": rule_id,
                                 "match": match, "hint": hint, "sentence": sentence})
        if block["kind"] == "paragraph" and len(parts) > PARAGRAPH_SENTENCES and block_kind != "procedure":
            findings.append({"path": path, "line": block["line"], "level": "error", "rule": "paragraph-length",
                             "match": f"{len(parts)} sentences",
                             "hint": f"descriptive paragraphs stay within {PARAGRAPH_SENTENCES} sentences",
                             "sentence": parts[0]})
    return findings, stats


def main():
    parser = argparse.ArgumentParser(description="Check text against STE-style writing rules. A clean report is "
                                                 "not a compliance claim: vocabulary meaning needs the Dictionary.")
    parser.add_argument("paths", nargs="*", help="files to check; '-' or nothing reads stdin")
    parser.add_argument("--mode", choices=("auto", "procedure", "descriptive"), default="auto",
                        help="text type; auto treats numbered steps and imperative sentences as procedure")
    parser.add_argument("--min", choices=LEVELS, default="review", help="lowest level to report")
    parser.add_argument("--fail-on", choices=LEVELS, help="exit 1 when a finding at or above this level remains")
    parser.add_argument("--json", action="store_true", help="print machine-readable output")
    args = parser.parse_args()
    findings = []
    totals = {"sentences": 0, "longest": 0}
    try:
        for target in args.paths or ["-"]:
            text = sys.stdin.read() if target == "-" else Path(target).read_text(encoding="utf-8")
            found, stats = check_text(target, text, args.mode)
            findings += found
            totals["sentences"] += stats["sentences"]
            totals["longest"] = max(totals["longest"], stats["longest"])
    except (OSError, UnicodeDecodeError) as error:
        print(f"check.py: {error}", file=sys.stderr)
        return 2
    findings = [hit for hit in findings if LEVELS[hit["level"]] >= LEVELS[args.min]]
    counts = {level: sum(1 for hit in findings if hit["level"] == level) for level in LEVELS}
    if args.json:
        json.dump({"summary": dict(totals, counts=counts), "findings": findings}, sys.stdout,
                  ensure_ascii=False, indent=2)
        print()
    else:
        for hit in findings:
            print(f"{hit['path']}:{hit['line']}: {hit['level']} {hit['rule']}: {hit['match']!r} | {hit['hint']}")
        print(f"{len(findings)} findings (error {counts['error']}, warn {counts['warn']}, review {counts['review']})"
              f" in {totals['sentences']} sentences; longest sentence {totals['longest']}")
    threshold = LEVELS[args.fail_on] if args.fail_on else None
    return int(threshold is not None and any(LEVELS[hit["level"]] >= threshold for hit in findings))


if __name__ == "__main__":
    raise SystemExit(main())
