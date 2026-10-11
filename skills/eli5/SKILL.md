---
name: eli5
description: Explains a concept, system, piece of code, error, or decision in plain words to someone outside the field, while keeping every claim true. Use when the user says ELI5, explain like I'm five, explain it simply or in plain English, asks for an explanation for a beginner, a non-engineer, a manager, a parent, or a child, or says 쉽게 설명해줘, 5살도 이해하게, 초등학생도 알아듣게, 비전공자도 알게, 쉽게 풀어줘, 무슨 말인지 하나도 모르겠어. Also use when the user is visibly lost in jargon. Not for rewriting manuals or procedures into controlled language, removing AI tone from a draft, or quizzing the user as a tutor.
license: MIT
---

# ELI5

ELI5 means explaining to a smart adult who knows nothing about the field, not talking to a five-year-old. The reader should finish able to retell the idea and use it, and nothing they take away should be false. Simplify the telling, never the claims.

## Rules

1. Answer in the first sentence. No preamble and no praise for the question.
2. Keep every claim true at the level of detail it claims. Do not widen the scope (a result in mice is not a result in people; one benchmark is not "always"), turn an estimate into a fact, or drop a hedge the reader needs. When you simplify, say so: "roughly", "this skips X".
3. Explain the mechanism, not only the label. Give the context, the mechanism, and the impact on the reader. A technical term never stands in for the mechanism; jargon makes an explanation feel complete without making it understood.
4. Write for this reader. The default is an intelligent adult outside the field. When the user names the reader (a manager, a new hire, a parent, a lawyer), use that person's world and goal. Treat the reader as a child only when the user says the reader is a child. Never condescend: no "don't worry, it's super easy", no baby talk.
5. One new idea per sentence and at most one new term per sentence. Give a term the reader will meet again as "plain description (term)" on first use, then repeat the same term. Drop terms the reader will not need.
6. If you do not know, say so instead of guessing. If the question rests on a false premise, correct the premise first.

## Procedure

1. Understand it yourself first. Write the mechanism privately as three to five causal steps. If a step is missing, read the code or the docs, or tell the reader which step is uncertain. An analogy cannot cover a gap in your own understanding.
2. Find the reader and their goal. Use what the user said; otherwise use the default reader. Ask a question only when the answer would change the explanation substantially.
3. Write in layers and stop at the layer the question needs:
   - The answer in one sentence.
   - A simple model: one concrete example traced from start to end, then the general rule with the real term. Go from the concrete case to the abstract rule, not the other way round.
   - Details and edge cases, only when the reader needs them to use the idea correctly.
   - One line on what you left out, and one way to go further.

   Sometimes a claim is true only because of a mechanism the reader did not ask about ("it is hard to tamper with" is true because of the computing race). Compress that mechanism into one or two plain sentences and offer the full version as the next layer. Dropping it makes the claim false; expanding it into its own section makes the answer too long.
4. Add an analogy only when it carries the mechanism. Follow the protocol below.
5. Make numbers relatable. Keep the real number and add a comparison the reader can picture: "about one per person", "roughly the weight of a car".
6. Check the draft against the list in "Before you send".

## Analogies

An analogy is a model, and a model makes predictions. A wrong analogy teaches a wrong prediction that is hard to remove later.

- Choose an analog with the same causal structure as the part you are explaining, taken from the reader's world.
- Map it explicitly: which part of the analog is which part of the real thing.
- State in one line where it breaks.
- Use one main analogy. Add a second only to repair a named failure of the first. A wall of analogies teaches nothing.
- If no honest analogy exists, explain directly and say that nothing familiar behaves this way.
- For second-language readers, prefer a direct explanation. Idioms and culture-bound analogies do not travel.

Example: "A cache is like keeping the things you use most on your desk instead of in a drawer (the disk). Reaching the desk is fast, so repeated work speeds up. The analogy breaks in one way: the desk is small, so things you have not used for a while go back into the drawer automatically."

## Code, errors, and decisions

- Code: what problem it solves and for whom, then one real input traced through it to the output, then the general rule. Name each file or function once.
- Errors: what happened in plain words, why it happened, and what to do next.
- Decisions: the options as trade-offs in the reader's terms (cost, risk, time, effort), then the recommendation and the one reason that decides it.

## Korean

- 기본 문체는 해요체다. 사용자의 말투를 따르되, 요청이 없으면 반말로 내려가지 않는다. 성인에게 아기 말투("~란다", "친구야")를 쓰지 않는다.
- 외래어, 영어 약어, 한자어 전문어도 전문용어다. 처음 한 번 "쉬운 말(원어)"로 풀고 그 뒤로는 같은 말을 쓴다. 예: "지연 시간(레이턴시)", "침방울(비말)". 한자어는 글자의 뜻을 풀면 쉬워진다. 예: 슬개골은 무릎을 덮는 뼈, 곧 무릎뼈다.
- 한 문장에는 서술어 하나만 둔다. `~에 있어서`, `~를 통해`, `~되어지다` 같은 번역투를 피한다.
- 비유는 지금 독자의 생활에서 고른다. 택배 송장(패킷 경로), 은행 번호표(대기열), 책상 위와 서랍(캐시와 디스크)은 잘 통한다. 114 전화번호 안내(DNS)처럼 낡은 비유는 젊은 독자에게 통하지 않는다.
- 영어 자료를 번역하지 말고 처음부터 한국어로 쓴다.

## Format

- Short paragraphs. Use headings only for a long explanation. No emoji and no cheerleading.
- Use a diagram only for a flow, a hierarchy, or a comparison.
- Keep the length in proportion to the question. A "what is X" answer for a lay reader usually needs the one-sentence answer plus three to eight sentences, about 150 to 350 words (in Korean, about 500 to 1,200 characters). Go longer only when the user asks for depth.
- End with at most one line: an offer of the next layer, or a question that asks the reader to predict something ("What do you think happens if two people edit the same line?"). Do not ask "Does that make sense?"; a yes tells you nothing.

## Before you send

- Accuracy: every statement is true at its level of detail, no claim got wider, and every simplification is marked. A failure here fails the whole explanation.
- The first sentence answers the question.
- Context, mechanism, and impact are all present.
- Every term is defined at first use or removed, and no term is doing the mechanism's job.
- The analogy, if any, is mapped and says where it breaks.
- No preamble, no trivia, no tangent the reader did not ask for.
- What you left out is named.

When the explanation is long or important and you can start a fresh agent, run a reader test, because your own sense that a text is clear is not evidence. Give the fresh agent only the explanation and the reader description. Ask it to retell the idea in its own words, answer one question that needs the idea rather than the wording, and say where the analogy stops working. Every misunderstanding is a defect in the explanation; fix the text, not the reader.

Read [references/examples.md](references/examples.md) for paired bad and good examples of each failure mode in English and Korean.
