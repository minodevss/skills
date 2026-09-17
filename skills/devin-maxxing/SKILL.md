---
name: devin-maxxing
description: Orchestrates Devin CLI with free SWE-2 Max workers to maximize implementation quality through substantial parallel development, competing designs, adversarial review, and verified integration. Use when the user asks to use Devin or SWE-2 for coding, burn free tokens, max out parallel agents, or says "devin으로 개발", "swe-2 맥싱", "무료 토큰 태워", or "병렬로 빡세게". Not for ordinary coding without a Devin delegation request or for Devin Cloud administration.
license: MIT
compatibility: Authenticated Devin CLI, Python 3.10+, and macOS or Linux. The requested exact SWE-2 model must be advertised as Free by the current account.
---

# Devin Maxxing

Use free model capacity generously to improve the deliverable. Optimize for correct, cohesive, well-verified results and elapsed time; token count is not a success metric. Default to the exact model UID `swe-2-max`. Do not silently choose another model or start a paid run.

The supervising agent owns decomposition, interface decisions, integration, verification, and communication. Delegate substantial implementation and investigation to SWE-2, not just peripheral notes. Use the supervising model for decisions and concise evidence rather than replaying full worker logs or redoing every analysis. Devin workers execute bounded assignments. This skill applies across languages and project types; derive conventions and build commands from the actual workspace.

## Start with current facts

1. Read the user's goal, workspace instructions, current code, and working-tree state. Preserve existing changes. Identify what the user has authorized, what success looks like, and the highest-risk unknowns.
2. Check `devin --version` and `devin --help` on first use in a task. Consult the official [CLI reference](https://docs.devin.ai/cli/reference/commands), [permissions](https://docs.devin.ai/cli/reference/permissions), and [models](https://docs.devin.ai/cli/models) when installed behavior differs. Do not reinstall or upgrade merely to follow stale examples.
3. Inspect `devin models list --format json`. A model must match the requested UID exactly and advertise `cost_tier: Free`. Historical free pricing is not authorization for present charges. If unavailable, paid, ambiguous, or unparseable, stop delegation, report the blocker, and continue only independent local work that does not require that model.
4. Use the bundled runner for every launch and resume. It checks pricing again immediately before starting. A free listing does not guarantee unlimited quota, future pricing, or exemption from other service charges; do not create cloud machines or paid services as an implicit fallback.

## Spend capacity where it changes the answer

For substantial work, start with 3–4 independent assignments. Expand toward 6–8 only when there are enough useful tasks and the machine and service remain responsive. These are defaults, not targets. Small tasks may need one writer and one reviewer; tightly coupled work may require sequential implementation.

Useful concurrent work includes:

- Different modules whose interfaces and file ownership are settled.
- Two isolated approaches to a consequential design uncertainty, with a concrete evaluation criterion.
- An independent reviewer trying to falsify the proposed fix, using a specific snapshot or diff.
- Tests for failure boundaries, lifecycle behavior, cancellation, migrations, or compatibility.
- Checking actual upstream documentation and pinned dependencies while implementation proceeds.
- Performance measurement or user-flow validation appropriate to the product.

Use repeated reasoning to resolve identified uncertainty. Do not send the same vague whole-project prompt to many writers, fill the workspace with near-duplicate drafts, or run open-ended critique loops. Extra workers are useful only if their results can be integrated or change a decision.

## Establish ownership before starting writers

Keep a compact local ledger outside tracked source, with one row per task:

`task | goal | workspace | owned paths | shared contract | session ID | PID/log | status | validation`

- Assign one writer per file or module. State allowed files and read-only files in every prompt.
- Keep shared interfaces, dependency changes, global configuration, and integration under one owner.
- Reviewers read a fixed revision, copied snapshot, or a clearly identified completed change. A review racing ongoing edits can describe code that no longer exists.
- Use separate worktrees or temporary copies for competing implementations or overlapping edits. Do not reset the user's checkout to create isolation. For a dirty baseline, deliberately include the relevant changes in each isolated copy; a worktree from HEAD alone does not include them.
- Shared-checkout workers may only edit disjoint paths. A branch name alone provides no filesystem isolation.
- Budget CPU, memory, disk, network, and compiler jobs across the whole team. Prefer one shared integration build. Workers needing builds use separate output/cache paths; do not let several package managers mutate the same checkout or lockfile.
- Workers do not create additional workers unless the supervisor explicitly assigns them a bounded share of the concurrency budget.

## Write concrete assignments

Put each prompt in its own local file. Supply relevant context directly rather than forwarding an entire transcript. Use this structure, scaled to the task:

```text
Goal: The user-visible result or question to resolve.
Evidence: Observed behavior, reproduction, constraints, and known uncertainties.
Read first: The few relevant files and applicable workspace instructions.
Ownership: Exact writable paths; everything else is read-only.
Contract: Interfaces, invariants, inputs/outputs, and assumptions agreed with peers.
Acceptance: Concrete behavior and failure cases that must hold.
Validation: Commands or measurements appropriate to the owned work; output isolation.
Boundaries: Authorized actions, excluded operations, and external side-effect limits.
Deliver: Changes/findings, evidence, remaining risks, and integration needs.
```

Ask reviewers to distinguish verified defects from hypotheses and preferences. Ask implementers to finish working changes rather than stop at a plan. When a worker discovers a shared-contract problem, it reports the smallest required change instead of silently editing another worker's files.

Do not put credentials, private recordings, or unrelated sensitive data in prompts or logs. Normal source-code delegation to Devin is part of using this skill, but unrelated data and additional external destinations are not.

## Execute unattended, within the assignment

Run [scripts/run_task.py](scripts/run_task.py) with Python using its absolute path resolved from this skill directory. Execute it; there is no need to paste the script into the project.

```sh
python3 /absolute/path/to/devin-maxxing/scripts/run_task.py --check
python3 /absolute/path/to/devin-maxxing/scripts/run_task.py --workspace /absolute/project --prompt /absolute/local/task.md
python3 /absolute/path/to/devin-maxxing/scripts/run_task.py --workspace /absolute/project --prompt /absolute/local/follow-up.md --resume exact-session-id
```

The runner uses:

```text
--model swe-2-max
--permission-mode dangerous
--respect-workspace-trust false
--prompt-file <file>
--export <local-json>
-p
```

Dangerous mode makes the CLI unattended; it does not authorize actions outside the user's request or override system/organization protections. Do not combine it with `--sandbox`. The runner rejects an enabled `DEVIN_SANDBOX` environment setting rather than silently changing it. Keep commits, publishing, deployments, credential changes, account changes, purchases, and destructive operations out of worker scope unless specifically authorized and assigned.

Default timeout is 60 minutes per invocation; override `--timeout-seconds` when the assignment warrants it. Launch with the host's background/streaming execution mechanism so long work does not block supervision. Independent runner commands can run concurrently.

Outputs go to the local state directory (`$XDG_STATE_HOME/devin-maxxing`, otherwise `~/.local/state/devin-maxxing`). `--state-dir` overrides it. Logs and exports may contain source code and commands; treat them as private local data, never release artifacts. Each run writes a manifest containing its workspace, PID, paths, requested model, timestamps, and outcome.

## Supervise without thrashing

- Identify sessions from their export or `devin list --format json` in the exact workspace, matching the assignment and start time. Record the exact ID as soon as available. Do not assume an arbitrary exporter JSON field or select a session solely because it is most recent.
- Never use `--continue`, bare `--resume`, or an inferred latest session. Resume the exact ID with the requested model pinned again.
- Before resuming, verify the previous process for that session has exited. The runner prevents overlapping resumes launched through this runner; it cannot detect sessions started by another orchestrator. Check the ledger and only act on processes owned by the current task.
- Monitor logs and actual progress, while doing useful local work. Large Max turns can be quiet for many minutes. Quiet stdout alone is not evidence of a hang.
- Tell the user what was learned and what is being resolved. Do not narrate each poll or dump raw worker streams.
- Intervene for an ownership conflict, a changed requirement, a concrete blocker, sustained failure, or the assigned deadline. Do not interrupt merely to obtain a faster summary and repeatedly discard context.
- On interruption or timeout, inspect partial edits before another writer starts. Resume the same session when its context remains useful, or explicitly reassign ownership after it has stopped.
- On rate limits, lower concurrency and back off. Do not rotate accounts, bypass quota controls, or silently fall back to a paid model.

## Integrate and challenge the result

1. Read the actual diff and compare it with the assignment. Reject unrelated changes, placeholders, invented measurements, weakened assertions, hidden errors, or dependency churn without justification.
2. Resolve shared contracts explicitly and integrate in dependency order. Keep one owner for integration conflicts.
3. For meaningful changes, spend an independent review pass on specific risks: concurrency, cancellation, data loss, compatibility, security boundaries, or the user-visible workflow. Treat findings as leads, not authority.
4. Run the relevant real build/tests/checks yourself against the integrated tree. A worker saying "passed" is not equivalent to this check. Use direct inspection or rendering for simple visual edits instead of pointless tests.
5. Exercise the actual user flow when authorized and feasible. Fakes, compilation, and static reasoning do not prove real hardware, model accuracy, external integrations, or deployment success.
6. Send focused repair assignments for reproducible failures, then verify the changed areas again. Broaden testing only when new evidence calls for it.

Stop expanding once acceptance criteria and required checks pass and no material uncertainty is left unaddressed. More free inference should improve confidence or product quality, not create perpetual rewrites. If an essential constraint remains, identify it clearly instead of claiming completion.

Report the completed result, meaningful validation, material limitations, and the exact model/free listing observed. Mention delegated work only where it explains the outcome. Keep local plans, ledgers, prompts, exports, and review diaries out of source control unless the user explicitly requests them.
