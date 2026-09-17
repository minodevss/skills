---
name: commit
description: "Creates atomic commits from the working tree, then optionally pushes, opens a PR, and merges it after CI passes. Use when the user asks to commit, push, open a pull request, or ship/land/merge their changes (커밋, 푸시, PR 올려, 머지). Args in any order: push, pr, merge; each implies the earlier steps. Not for reviewing a diff, drafting a message without committing, or merging branches locally."
license: MIT
---

# Commit

Turn the working tree into atomic commits, then optionally `push`, open a `pr`, and `merge` it. Each arg implies the earlier steps. Without args, infer the mode from the request. Go past commit only when the user clearly asked for it; when unclear, commit only and say which steps were skipped.

Precedence: explicit user instruction, then project guidance (AGENTS.md, CLAUDE.md, commit template, commitlint, PR template, git hooks), then a consistent recent `git log` style, then the defaults below.

## How to run

- One read-only inspection call, then one script per phase. Scripts use `set -euo pipefail`, quiet flags (`-q`, `--stat`), and end with that phase's evidence commands.
- Print the numbered plan before the commit script runs.
- Never ask a question mid-run. On a stop condition, report the reason and the single next command, then stop.
- Slow steps (test suites, CI watch) get their own call.

## Stop conditions

Stop when: nothing to commit; a merge, rebase, cherry-pick, or bisect is in progress; the diff contains conflict markers; a hook fails after one retry; the push is rejected; CI fails; the PR is a draft in merge mode.

Never: `git add -A` or `git add .`, `--no-verify`, `--force`, `--allow-empty`, `--admin`, co-author or assistant trailers, committing secrets, `.env*`, or build output. `--force-with-lease` only when the user asked for it in this request, after `git fetch origin <branch>`.

## 1. Inspect

```bash
git status --short --branch
git diff HEAD
git log --oneline -10
```

Read untracked files that belong in a commit. For push, pr, or merge also collect: current branch and upstream (`git rev-parse --abbrev-ref @{u}`), default branch (`git symbolic-ref --short refs/remotes/origin/HEAD`, else `gh repo view --json defaultBranchRef --jq .defaultBranchRef.name`), `gh auth status`, `gh pr list --head <branch> --state open --json number,url`, and for merge `gh repo view --json mergeCommitAllowed,rebaseMergeAllowed,squashMergeAllowed`.

## 2. Plan

One commit per reason to exist, not per file:

- Hunks with the same reason go together even across files (a rename plus every call site). Hunks with different reasons split even inside one file.
- Formatting-only changes, dependency or config changes, renames, and pure moves each get their own commit.
- Tests commit with the code they test. Each submodule pointer update is its own commit.
- Every commit must build or parse on its own; when a split would break that, keep the larger unit.
- Changes the user already staged stay together as one commit.
- Leave out junk such as `.DS_Store` or build output and mention it in the report.

Print one line per commit: `n. type: description — files or hunks`.

## 3. Commit

For each planned commit in dependency order: stage only its paths. For a file whose hunks belong to different commits, put the wanted hunks (copied from the inspected diff) in a heredoc and `git apply --cached`, adding `--recount` if a hunk was trimmed by hand. Then `git commit -q -m "<message>"`. If a hook fails after rewriting staged files, re-stage those files and retry once.

Evidence: `git status --short --branch` and `git log --oneline -<n>`.

Message defaults: `type: description` with type in feat, fix, chore, refactor, docs, test, perf. Lowercase, one line, no period, no scope unless the project uses scopes.

## 4. Push

Branch: on the default branch or detached HEAD, `git switch -c <prefix>/<slug>`. On a never-pushed branch whose name is auto-generated (the worktree directory name, a uuid or timestamp, wip, tmp, scratch), `git branch -m <prefix>/<slug>`. On a branch that has an upstream, keep it. Prefix by the branch's net intent: `feature/`, `fix/`, `chore/`. Slug: lowercase kebab-case from the diff, under 40 characters. Report `created`, `renamed`, or `kept branch: <name>`.

Run the project's pre-push checks unless a git hook already enforces them; if they fail, stop. Never push to the default branch or a release branch. Then `git push -u origin <branch>`, or plain `git push` when an upstream exists.

## 5. Pull request

Without an authenticated `gh`: print `https://github.com/<owner>/<repo>/compare/<base>...<branch>?expand=1` and stop. If an open PR exists for the branch, the push already updated it; skip creation. Base is the default branch unless the user named one. Body follows the repo's PR template, else `## Summary` and `## Verification`. Title: the single commit's subject, or the branch's net intent; lowercase, under 70 characters. `--draft` only when the user asked or checks were skipped.

```bash
gh pr create --base <base> --head <branch> --title "<title>" --body "$(cat <<'EOF'
<body>
EOF
)"
```

## 6. Merge

Draft PR: stop. Wait with `gh pr checks <n> --watch --fail-fast` in its own call with a long timeout or in the background; a non-zero exit means stop. Strategy: the user's choice, else the first allowed of merge, rebase, squash. Then `gh pr merge <n> --<strategy> --delete-branch`; inside a git worktree omit `--delete-branch` and run `git push origin --delete <branch>` instead. Output that mentions a merge queue means queued, which counts as success.

## Report

End with one block: each commit as `<short-hash> <message>`, the branch, the PR URL, the merge state, and any files left uncommitted.
