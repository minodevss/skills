---
name: asd-ste100
description: Writes and rewrites technical text by the rules of ASD-STE100 Simplified Technical English (Issue 9) - one instruction per sentence, imperative steps, short sentences, simple verb forms, approved-word discipline, and clear warnings - and applies the same discipline to Korean. Use when writing or editing procedures, maintenance or operating instructions, manuals, safety warnings, troubleshooting steps, error messages, or docs that translators or non-native readers will use, and when the user asks for STE, Simplified Technical English, ASD-STE100, or controlled language, or says STE로 써줘, 절차서 STE로 바꿔줘, 저 규격대로 써줘, 번역하기 쉬운 매뉴얼로. Not for explaining ideas to beginners, marketing or narrative prose, or general editing with no controlled-language requirement.
license: MIT
---

# ASD-STE100 Simplified Technical English

ASD-STE100 is a controlled language for technical documentation. Issue 9 (January 2025) is current. It has two parts: 53 writing rules in nine sections, and a Dictionary of 875 approved words. Each approved word has one meaning and one part of speech. The goal is text with exactly one reading, for a reader whose first language is not English and for a translator.

ASD owns the standard and its trademark. This skill is not affiliated with or endorsed by ASD. It restates the rules in its own words and does not contain the Dictionary. The official copy is free at asd-ste100.org.

## Meaning comes first

The rules serve the meaning. Do not change what a sentence claims to make it fit a rule.

- Keep each fact, number, condition, limit, and hedge. Strict STE rewrites can lose facts, and a lost fact is a worse defect than a long sentence.
- If the original is ambiguous, STE forces a choice. Make the choice and name it in the report. Example: "should disconnect" becomes "must disconnect" only when the source makes it a requirement.
- For real uncertainty, write `can` or `possibly`. Do not delete the uncertainty.
- When no approved word fits, try these steps in order:
  1. Rebuild the sentence.
  2. Use a phrase of approved words.
  3. Use a legitimate technical noun or verb.
  4. Keep the word and flag it.

A rewrite is wrong if it has one of these changes:

- A near synonym that changes the meaning ("lost" becomes "decreased")
- A dropped object or condition
- A dropped hedge or limit

## Modes

Strict mode applies to procedures, safety instructions, maintenance text, troubleshooting, and error messages. Use all the rules, including word choice. Report each word that you did not confirm.

Plain mode applies to READMEs, API docs, release notes, commit messages, and your own replies. Use the sentence and verb rules. Treat the word rules as advice.

Use strict mode when the user asks for STE on a procedure or a manual. Otherwise use plain mode.

## The rules that do most of the work

1. One instruction per sentence (5.2). Two actions can share a sentence only when they happen at the same time.
2. Keep sentences short (5.1, 6.3, 6.6, 8.4):
   - Procedure, warning, or caution: 20 words or fewer in each sentence.
   - Description or note: 25 words or fewer in each sentence.
   - Descriptive paragraph: 6 sentences or fewer.
   - A list item is a sentence with the same limit.

   Split a long sentence. Do not delete small words to make it shorter.
3. Use the imperative in a procedure (4.1, 5.3): "Remove the cover." Use `must` only for safety or an important condition.
4. Use the active voice (3.6). In a description, use the passive only when the agent is unknown. STE permits a participle that describes a state, as in "The valve is closed" (3.3).
5. Use only these verb forms (3.2): infinitive, imperative, simple present, simple past, and `will` for the future. A past participle can also be an adjective. Do not use progressive or perfect tenses. Do not use a modal with `be` and a participle (3.4). Write "You can adjust the gap", not "The gap can be adjusted".
6. Write one word for one meaning, and one meaning for one word (1.3, 1.11, 6.2). Do not call one thing a setting here and an option there.
7. A multi-word noun has 3 words or fewer (2.1): "the expiry value of the user authentication token".
8. Keep articles and the small words (4.2). Do not use contractions or semicolons (4.2, 8.1).
9. Put the condition first, then a comma, then the action (5.4): "If the light comes on, stop the engine."
10. A note gives information only (5.5). It contains no instruction and no limit. The procedure must work when you remove all notes.

Read [references/rules.md](references/rules.md) for every rule by section, the word-count conventions, and what STE does not regulate.

## Word choice

The Dictionary decides which words are approved, and you cannot see it. Some simple words are not approved. `check` and `test` are approved only as nouns, `enough` is not approved (`sufficient` is), and `about` means only "concerned with" (`approximately` is approved for quantities).

| Not approved | Write |
|---|---|
| utilize, employ | use |
| commence, initiate | start |
| terminate, cease | stop |
| prior to | before |
| subsequent to | after |
| in the event of | if |
| ensure, verify | make sure (that) |
| assist, facilitate | help |
| obtain | get |
| however | but |
| indicate | show |
| modify, alter | change |
| perform | do |
| may | can, or possibly |
| should, shall | must, or an if clause |
| check, test (verbs) | make sure, examine, "do a test of" |

Read [references/word-choice.md](references/word-choice.md) for the longer table and the meaning traps (`follow`, `since`, `while`, `as`, `turn`, `see`). It also lists the approved `-ing` words and tells what to do when you cannot check a word.

## Procedures, descriptions, and safety

A procedure is a sequence of numbered steps, with one action per step. Put the purpose in a sentence before the steps. Put a result in its own sentence: "The light goes off."

A description tells how something works. Use the simple present. Start each paragraph with its topic sentence and keep to that topic.

A safety instruction has a signal word, a command or a condition, and the risk (7.1 to 7.3).

- WARNING: a risk of injury or death. When the two risks apply, use WARNING.
- CAUTION: a risk of damage to equipment or other objects.
- A note is not a safety instruction. A note that describes a risk is a caution or a warning with the wrong label.

STE does not say where a warning goes. Put it immediately before the step it applies to, as S1000D and ANSI practice do. A warning that the reader sees after the action has already failed.

## Workflow

1. Classify each block: procedure, description, safety instruction, or note.
2. Save the original in a temporary directory outside the repository. Run the checker:

   ```sh
   python3 <skill-dir>/scripts/check.py /tmp/ste/original.md
   ```

   `--mode procedure` or `--mode descriptive` overrides the automatic classification. Numbered steps and sentences that start with a command count as procedure.
3. Rewrite. Use the rules above in this order:
   - Split each sentence that has more than one instruction or topic.
   - Make each instruction imperative, and put each condition first.
   - Change the verb forms, and use one term for each thing.
   - Break long noun groups, and move each warning before its step.

   The source can leave out something that the reader needs, such as a command, a value, or the items of a list. Then put a visible placeholder in the text: `[TO BE SUPPLIED: production deploy command]`. Do not guess the value. A gap that only the report mentions is lost when the document goes to the technician.
4. Check the meaning:

   ```sh
   python3 <skill-dir>/scripts/compare.py /tmp/ste/original.md /tmp/ste/rewrite.md
   ```

   Exit code 1 means that a number, URL, code span, or code block disappeared or appeared. Restore it or explain it. Look at each changed hedge: a `may` that became `must` changes the claim.
5. Run `check.py --fail-on error` on the rewrite. Fix each error, or keep it and give the reason in the report.
6. Report in one short list:
   - The changes
   - Each choice that you made for an ambiguous sentence
   - Each word that you kept and flagged
   - The checker summary

   The checker cannot confirm word meanings. Thus, say that a clean result is not a compliance claim.

## 한국어

여기부터는 ASD-STE100 규격이 아니다. 규격은 영어 전용이고 한국어판 승인 어휘는 없다. 옮길 수 있는 것은 규율이다. 이 규율로 쓴 한국어 글을 "STE 준수"라고 부르지 않는다.

- 한 문장에는 지시를 하나만 쓴다. 동작이 둘이면 문장을 나눈다.
- 절차 문장과 경고 문장은 20어절 이하, 설명 문장은 25어절 이하로 쓴다. 설명 문단은 6문장 이하로 쓴다. 공식 한국어 기준에는 어절 한도가 없다. 이 숫자는 이 스킬의 기준이다.
- 조건을 앞에 쓰고 동작을 뒤에 쓴다. 예: "설정이 없으면 기본값을 씁니다."
- 절차는 `-세요`와 `-지 마세요`로, 설명은 `-ㅂ니다`로, 의무는 `-어야 합니다`로 끝낸다. 한 문서에서는 한 체계만 쓴다.
- 행위자를 주어로 쓴다. 이중 피동, 불필요한 `-되다`와 `-시키다`, 빈 한자어 동사(`수행`, `진행`, `실시`)를 쓰지 않는다.
- 한 개념에는 한 용어만 쓴다. 약어는 처음에 풀어 쓴다. 예: "인공지능(AI)"
- 모호어(`적절히`, `필요시`, `가능한 한`)를 수치나 조건으로 바꾼다. `등`을 쓰지 말고 항목을 모두 쓴다.
- 명사를 넷 이상 이어 붙이지 않는다. 조사나 어미로 관계를 밝힌다.
- 경고는 해당 동작 바로 앞에 쓴다. 경고에는 위험의 내용을 쓴다.
- 확인한 것은 단정한다. 확인하지 않은 것은 확인하지 않았다고 쓴다. 두 가지를 한 문장에 섞지 않는다.
- 원문에 없는 값은 추측하지 않는다. 문서 안에 `[작성 필요: 프로덕션 배포 명령]`처럼 빈칸을 표시한다.

[references/korean.md](references/korean.md)에 문체표, 경고 형식, 오류 메시지 형식, 고쳐 쓰기 예시가 있다. `check.py`는 한국어 문장도 검사한다. 어절 수, 이중 피동, 모호어, 빈 동사, 명사 나열, 절차문의 완곡 표현을 본다.

## While this skill is loaded

It governs the text you produce, in any language: the files you write, the commit messages, and your replies to the user. Use plain mode for your replies. It does not change the language you reply in.

It governs your writing, not the user's writing. Do not correct how the user wrote something. Do not rewrite text that nobody asked you to change.

## Code artifacts

- Error and log messages: what failed, what the program did, and what the reader does next. "Cannot read config.yaml: the file does not exist. The program uses the default values. To use a different file, set CONFIG_PATH."
- Commit subjects: the imperative, one change, within the line limit of the repository.
- Comments: why the code does something, in the simple present. A comment that repeats the code is noise.
- UI text: the second person, the imperative, and no idioms. Translators work on this text first.
- API reference: one sentence for each parameter. Give what it is, then the default, then the limit.

## Where it does not apply

STE is not for marketing copy, narrative, or tutorials that use analogy on purpose. It is also not for text where the reader's interest is more important than speed. STE makes text unambiguous, not interesting. If the user asks for STE on such text, tell them.

The evidence for STE is strongest for complex documents and non-native readers. One large field study found no consistent benefit outside the US, and controlled-language rules did not measurably help neural machine translation in one study. Do not promise translation savings.

## Gotchas

- `and/or`, number style, units, uppercase, and formatting are not STE rules. Follow the house style.
- Do not change prose into bullet points to stay under the paragraph limit. Each list item is a sentence with the same limit.
- STE approves `could` only as the past tense of `can`.
- The two scripts use only the Python 3.10+ standard library. Run them with `python3` and the absolute path of this skill's `scripts/` directory. Keep temporary files out of the user's working tree.
