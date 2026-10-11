# English prose patterns

Contents: 1. Chat leftovers · 2. Inflated significance · 3. Staging and structure · 4. Vocabulary · 5. Formatting · 6. Stance · 7. Content · 8. Fiction · 9. Not slop · 10. Over-correction · 11. Worked example

Tiers: **strong** means one sighting justifies an edit. **medium** means act when it repeats or sits near another tell. **weak** means it counts only inside a cluster. Every fix below changes the sentence or deletes it; none of them is a synonym.

## 1. Chat leftovers (strong)

Text that was addressed to the person who prompted the model, not to the final reader.

- Openers and closers: `Certainly! Here's`, `Great question`, `I hope this helps`, `Let me know if you'd like`, `Would you like me to`, `Feel free to reach out`. Delete them.
- Self-reference and cutoff talk: `As an AI language model`, `as of my last knowledge update`. Delete them. If the sentence carried a real limit, state the limit plainly.
- Placeholders and citation residue: `[Your Name]`, `INSERT_SOURCE_URL`, `2025-XX-XX`, `contentReference[oaicite:0]`, `turn0search3`, `utm_source=chatgpt.com`, `[cite: 2]`, `【4†L10-L12】`. Remove the residue. Ask for the real value instead of guessing it.
- Process talk: `ensuring clarity and flow`, `preserving the original meaning`. Delete it.

## 2. Inflated significance (strong)

The model adds importance that nobody established.

- `stands as a testament to`, `plays a pivotal role in`, `marks a significant shift`, `enduring legacy`, `indelible mark`, `setting the stage for`, `reflects broader trends`, `in the evolving landscape of`.
- Fix: delete the clause. If the importance matters, show it with the consequence, the number, or the person who said so.
- `Despite these challenges ... the future looks promising` is a formula. Name the specific problem with its evidence and drop the upbeat tag.
- Promotional words in neutral text: `nestled`, `in the heart of`, `boasts`, `vibrant`, `rich heritage`, `world-class`, `cutting-edge`, `game-changer`. Replace the adjective with the fact it stood in for (a date, a size, a count) or delete it. In ad copy these are medium, not strong.

## 3. Staging and structure

The shape is a stronger tell than the vocabulary, and it survives word-level edits.

- Negative parallelism (medium, strong when repeated): `It's not X, it's Y`, `not just X but Y`, `No X. No Y. Just Z.`, and its newer form `Y rather than X`. State Y. Keep a contrast only when a real reader believes X, and then say who.
- Evaluative -ing tails (medium): `..., highlighting its importance`, `..., ensuring seamless integration`, `..., contributing to growth`. Delete the tail, or make it its own sentence with a subject and evidence.
- Rule of three (medium): triads of adjectives or clauses. Use as many items as the facts support. Two is fine. One is often better.
- Staged reveals (medium): `Here's the thing:`, `The result?`, `The best part?`, a rhetorical question answered in the next sentence, a colon that unveils the point. State the point.
- Punch fragments (medium): one-line paragraphs like `And that changes everything.` or `Simple. Fast. Reliable.` Merge into the previous paragraph or delete.
- Signposting (medium): `Let's explore`, `Let's break it down`, `In this section, we will`. Delete it and start with the content.
- Summary closers (medium): a final `In conclusion` or `Overall` paragraph that repeats the body. End on the last new fact or its consequence. Student essays and formal reports may keep a conclusion.
- Avoided copulas (medium): `serves as`, `functions as`, `features`, `offers` where `is` or `has` was meant. Use `is` and `has`.
- Elegant variation (weak): rotating synonyms for one thing. Pick one term and repeat it.
- Uniform rhythm (weak): every sentence 12 to 20 words, every paragraph the same size. Let the content set the length; do not randomize.
- Too-perfect balance (weak): every benefit paired with a drawback. Give the reader the judgment the evidence supports.

## 4. Vocabulary (weak alone, dated)

Single words prove little: one or two may be coincidence, and human technical writing uses many of them. Look for three or more distinct items within about 200 words, combined with a tell from another section.

Watch list as of 2026: `delve`, `tapestry`, `testament`, `intricate`, `interplay`, `pivotal`, `underscore`, `showcase`, `meticulous`, `garner`, `bolster`, `realm`, `multifaceted`, `nuanced`, `commendable`, `groundbreaking`, `invaluable`, `noteworthy`, `seamless`, `vibrant`, `enduring`, `foster`, `leverage`, `robust`, `crucial`, `holistic`, `paramount`, `transformative`, `empower`, `streamline`, `harness`, `navigate`, `landscape`, `align with`, `resonate`, sentence-initial `Additionally,` and `Moreover,`. Newer models have moved to `core`, `modern`, `quietly`, `steady`, `matters`, `dependable`.

The list goes stale with every model release, so treat it as a prompt to reread the sentence. The fix is to write the fact the word was covering. Replacing `delve into` with `dig into` leaves the sentence as empty as before.

Nominalizations (`the implementation of`, `facilitate the utilization of`) and stiff verbs (`utilize`, `commence`, `endeavor`) are medium. Turn the noun back into a verb and name who acts. Legal and academic prose uses them legitimately.

## 5. Formatting

Judge against the medium. A README can use headings and lists; an email, a chat reply, or a paragraph of argument usually cannot.

- Markdown in a medium that does not render it: `**bold**`, `##`, `---` in email, wiki, or chat text (strong).
- Bold-label bullets: `- **Scalability:** The system scales...` (medium, strong when every bullet has it). Write the list plainly or turn it into a paragraph.
- Bullets carrying an argument (medium). Arguments need connectives (`because`, `so`, `but`) that bullets drop.
- Emoji as bullets or heading decoration: `✅`, `🚀`, `💡`, `📌` (strong in professional prose).
- Bold scattered through a paragraph (medium). Bold one thing or nothing.
- Title Case Headings when the project uses sentence case (weak). `Conclusion` or `Key Takeaways` headings on a short piece (medium).
- Arrows and symbols in running prose: `→`, `≈` (weak).
- Em dashes: weak in 2026. Recent models emit fewer of them, and suppressing them produced its own tell (only commas and periods). Flag them only when dense and used for dramatic asides. Never remove them globally, and keep the ones that belong to the author.

## 6. Stance and tone

- Sycophancy (strong): `You're absolutely right`, praise for the question. Delete it.
- Hedge stacks (medium): `may potentially`, `could arguably`. Keep one hedge, attached to the part that is actually uncertain. Never delete a hedge that carried real uncertainty.
- Upbeat vagueness (medium): `the possibilities are endless`, `a beacon of hope`, `only time will tell`. Delete it.
- Faceless balance (medium): when the reader asked for a judgment, give one and the reason for it.
- Over-explaining (medium): restating what the reader just said, defining terms the reader uses daily. Cut to what they do not know.

## 7. Content

These are the patterns readers actually judge as slop. In expert annotation studies, density, relevance, and tone predicted a slop judgment better than any word list.

- Portability test (strong): could this sentence move unchanged into an article on another product or topic? If yes, cut it or replace it with a fact from the source.
- Vague attribution (strong when no source follows): `experts argue`, `studies show`, `some critics`, `industry reports suggest`. Name the source from the original, or cut the claim.
- Knowledge disclaimers (strong): `while specific details are limited`, `not widely documented`, `based on available information`. Find the fact or leave the topic out.
- Relevance drift (strong): the text answers a nearby question. Cut back to the one asked.
- Fabricated specifics (strong): invented experts, quotes, statistics, DOIs. Verify or remove. Never replace them with new invented ones.
- No concrete detail (medium): no names, numbers, or examples. Add them only from the source or the user; otherwise mark the gap.

## 8. Fiction

Stock names (`Elara`, `Kael`, `Seraphina`, `Aris Thorne`, `Elena Vasquez`, `Marcus Chen`) and stock phrases (`barely above a whisper`, `shivers down her spine`, `heart hammered against his ribs`, `a smile playing on her lips`, `eyes never leaving`, `the air thick with`, `couldn't help but`, `a mix of X and Y`, `maybe, just maybe`, `palpable`, `ministrations`) are strong. So are endings like `they would face it together` and imagery that is uniformly whispering, humming, and woven. Replace stock phrases with the specific physical detail of this scene, or cut them.

## 9. Not slop

Leave these alone unless other tells surround them:

- Perfect grammar, formal register, plain vocabulary, transition words, and repeated words. These are ineffective indicators, and many non-native writers are taught them.
- Genre conventions: headings and lists in docs, superlatives in ads, a conclusion in a student essay, Chicago title case, nominalizations in legal text.
- Technical senses: `robust regression`, `leverage ratio`, `underscore` as a character, `landscape` orientation.
- Words in quotations, code, or text that discusses these patterns.
- Hedges that carry real uncertainty, `in order to`, `the fact that`, `very`, and plain `is` and `has`. Human writers use all of them.

## 10. Over-correction

A rewrite can trade one set of tells for another. Check the result for:

- Staccato fragments and a uniform short rhythm.
- Commas and periods only, after removing every dash, colon, and semicolon.
- Forced casualness: slang, contractions sprinkled everywhere, deliberate typos, invented anecdotes, `honestly` and `I think` added for color.
- `Y, not X` and `rather than X` replacing `not X but Y`. The structure is the same.
- Lost meaning: a hedge, quantifier, or negation dropped (`most` becoming `all`, `may` becoming `will`).
- A new metaphor in place of a deleted one. Delete it; do not upgrade it.

## 11. Worked example

Before:

> In today's fast-paced digital landscape, observability isn't just a nice-to-have — it's a necessity. Our new tracing pipeline stands as a testament to our commitment to reliability, seamlessly integrating with existing tools, enhancing visibility, and empowering teams to move faster. It's important to note that results may vary.

After:

> The new tracing pipeline works with the tools teams already use. Results depend on the service.

Notes for the report: the original makes one checkable claim (it integrates with existing tools) and one caveat (results vary), and both survive. Everything else was framing. The rewrite does not add tool names or a latency number, because the source does not contain them. Ask the user which tools and what measured change, instead of inventing them.
