# Interface design and UI copy

Generated interfaces converge on the same defaults because the model samples from the center of its training data. A default is not wrong. It is a choice nobody made. The fix is to replace each unchosen default with a choice that comes from the brief, the brand, or the content; banning a list only moves the convergence to the next default.

## Snapshot of common defaults (2026)

These go stale fast. Treat them as calibration, not rules. The brief's own words always win.

- Earlier wave: Inter, Roboto, or Space Grotesk everywhere; purple-to-blue gradients and gradient text; glassmorphism; an emoji or icon tile above every heading; a centered hero with a big-number stat row; identical rounded card grids, cards nested in cards; gray text on colored backgrounds; dark mode with neon glow; fade-and-slide-up on every section; hover lift on every card.
- Later wave: cream background with a serif and a terracotta accent; near-black with acid green; hairline rules with zero radius; one radius and one soft shadow on every surface; tracked all-caps eyebrows above headings; `A · B · C` meta lines; `WORD — fragment` labels; mono labels; `→` appended to every link; `01 / 02 / 03` markers on content that is not a sequence.

## Procedure

1. List the visual decisions in the current UI: type, color, layout, components, motion.
2. For each, ask whether the brief or the brand chose it. If not, and it appears above, it is a default.
3. Replace defaults with choices derived from the content. Spend boldness in one place; remove decoration that does no job.
4. Ask: would a similar prompt for a different product land on the same page? Revise the parts that would.
5. Render and screenshot the result. Visual changes are not verified until they are seen.

## UI copy

Use [prose-en.md](prose-en.md) or [prose-ko.md](prose-ko.md) for the text itself. Interface-specific points:

- Buttons name the action: `Save changes`, `Delete project`, not `Submit` or `Continue` when the action is known.
- Errors say what happened and what to do next. They do not apologize or blame the user.
- Sentence case, plain verbs, no filler. Each element does one job.
- Empty states say what goes here and how to add it, not `Nothing to see here! 🎉`.

For deeper visual work, use a dedicated frontend design skill if one is installed.
