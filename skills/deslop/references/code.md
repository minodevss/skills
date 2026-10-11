# Code, tests, and git artifacts

Contents: 1. Procedure · 2. Comments · 3. Error handling · 4. Types · 5. Structure · 6. Dead and duplicate code · 7. Tests · 8. Logging · 9. Naming · 10. Files and READMEs · 11. Commits, PRs, review comments · 12. Example

The surrounding file is the standard. A check, comment, or name that the file already uses everywhere is a convention, not slop. Judge each added line against its own file and siblings, not against a universal rule.

## 1. Procedure

1. Scope to the branch. `BASE=$(git merge-base origin/HEAD HEAD)` (fall back to `main` or `master`), then `git diff $BASE...HEAD` plus uncommitted changes. Touch only lines the branch added. Pre-existing slop is out of scope unless the user asks.
2. Baseline. Run the project's formatter, linter, type checker, and tests, and record the result. If a risky item has no coverage, leave it and report it, or add a characterization test first.
3. Learn the local standard for each touched file: comment density, docstring style, the error-handling idiom at that layer, the logger, naming, type strictness, and how sibling files solve the same problem. Read AGENTS.md, CLAUDE.md, CONTRIBUTING, and lint config.
4. Sort every hit into delete, rewrite (keep the why, drop the narration), keep, or escalate (removing it would change behavior or a contract).
5. Edit from safe to risky: comments, emoji, banners, and debug prints; unused imports and locals; unrequested files; casts; defensive code; abstractions and shims; tests. Stop at the first step whose change you cannot verify.
6. Verify. Rerun the same checks. Confirm no assertion was removed: `git diff -U0 $BASE -- '*test*' '*spec*' | grep -E '^-.*\b(assert|expect)'` should print nothing you did not intend.
7. Report in one to three sentences, and list anything escalated. Keep the cleanup in its own commit, separate from behavior changes.

## 2. Comments

- Narration (strong): `# Initialize the counter` above `count = 0`, `// Step 1: Load config`, `// Loop through users`. Delete. Keep numbered steps only when they mirror a spec, and keep teaching comments in tutorial code.
- Addressed to the reviewer (strong): `// Updated to use new API`, `# Fixed bug where...`, `# Added per your request`, `// Now uses async`, `// removed`, `// previously X, now Y`. These explain the change to the person reviewing it and become noise the moment it merges. Delete. If a real constraint hides inside, rewrite it as the constraint: `// Fixed: avoid double free` becomes `// caller frees the buffer`.
- Changelog in comments (strong): `# v2: changed retry logic`. History belongs in git. Keep license headers and header changelogs the project already maintains.
- Docstrings that restate the signature (medium): `Args: user_id (str): The user ID.` Delete, or keep only what the signature does not say. Keep them where public API docs are required (Go exported names, `missing_docs` lints, generated references) or where every function in the file has one.
- Invented justification (medium): a "why" comment describing a failure the codebase never shows, usually guarding a defensive branch. Judge the comment and the branch together; both often go.
- Prompt leakage (strong): `# You can extend this to support Redis later`, `# In a real implementation you would...`, `# For simplicity`, `# special case for test_xyz`.
- Keep: hidden constraints, invariants, workarounds with an issue link, `SAFETY:` notes, performance rationale, regex explanations, and lint pragmas that match the repo's own usage.

## 3. Error handling

- Swallowing catches (strong): `except Exception: return None`, `catch {}`, `.catch(() => null)`, `catch (e) { console.log(e) }`. They turn a failure into a wrong value. Remove the try, and confirm a caller or top-level handler expects the exception.
- Fake success (strong): a catch that returns sample data so the output looks right. Remove it.
- Rethrow only (strong): `except Exception: raise`. Delete the try.
- Impossible-state checks (medium): `if user is None` right after `user = User(...)`, `?.` on non-nullable types, `isinstance` or `hasattr` on objects of a known type, re-validating what the caller already validated.
- Keep at trust boundaries: user input; request, CLI, env, and config parsing; deserialization; network and third-party responses; file and IPC I/O; nullable database fields; public library entry points; auth and sanitization; resource cleanup (`finally`, `with`, `defer`); retries on known-transient errors; top-level crash handlers; and broad catches the file already uses at that layer.

Removing a catch changes behavior. Treat it as risky and verify it.

## 4. Types

- Casts that silence the checker (strong): `as any`, `as unknown as T`, `// @ts-ignore`, `@ts-expect-error`, `# type: ignore`, `cast(Any, ...)`, `eslint-disable`, `// nolint`. Fix the type. If that is not possible within scope, keep the cast with a one-line reason and report it.
- Type erosion (medium): `dict[str, Any]` or `Record<string, unknown>` passed deep into internal code; generic `safe_int` and `ensure_dict` helpers.
- Keep: untyped third-party boundaries, test fixtures, `as const`, and casts the repo already justifies.

## 5. Structure

- Single-use abstraction (medium): an interface, factory, or base class with one implementation; a helper called once. Inline it. Three similar lines beat a premature abstraction.
- Speculative configurability (medium): options, flags, and parameters nobody asked for.
- Compatibility shims nobody asked for (strong in application code): aliases like `oldName = newName`, re-exports, `_unused` renames, feature flags around a direct change. Keep them in published libraries with semver obligations or in a staged migration the task requires.
- Deep nesting that early returns would flatten (medium).
- Hallucinated APIs and packages (strong, security): a new import or dependency the codebase never used. Confirm it exists in the registry and in the lockfile history before keeping it.

## 6. Dead and duplicate code

- Unused imports, helpers, parameters, variables (strong). Before deleting, check exports, `__all__`, entry points, plugin or DI registries, reflection, templates, and external consumers.
- Duplicate utilities (strong): a new `formatDate` beside an existing one. Switch to the existing helper only when its edge-case behavior is identical.
- Reimplemented standard library (medium): hand-rolled `chunk`, `deepClone`, `retry` when the language or an existing dependency has it.
- Half-finished stubs (strong): `raise NotImplementedError`, `pass  # TODO`, `throw new Error("Not implemented")`, `todo!()` in shipped paths. Finish or remove, and report which.

## 7. Tests

Never weaken a test to make a cleanup pass.

- Special-casing (strong): `if input == [3, 1, 2]: return [1, 2, 3]`, `if NODE_ENV === 'test'` in production code. Remove the special case and report the real failure.
- Weakened or deleted tests (strong): removed assertions, new `skip`, `xit`, `@Disabled`, widened tolerances, `|| true` in CI, `--passWithNoTests`. Restore them.
- Tautological tests (medium): the only assertion is `toHaveBeenCalled()`, `is not None`, or `toBeTruthy()`; expected values copied from current output; mocking the unit under test.
- Keep: skips with an issue link, snapshot tests the repo already uses, mocks at real I/O seams.

## 8. Logging and output

- Emoji in logs and prints (strong in backend code): `print("✅ Done!")`, `console.log("🚀 Server started")`. Keep them in CLIs and UIs whose style already uses emoji.
- Banners and debug prints (medium): `print("=" * 50)`, `console.log` in library code, `print` in a file that uses a logger.
- Over-logging (medium): entry and exit logs everywhere, log-and-rethrow at every layer. Check whether alerts, dashboards, or tests parse a line before removing it.

## 9. Naming

- Version-ish names (medium): `processDataV2`, `fixed_parse`, `enhancedClient`, `_new`, `_final`. Use the plain name and replace the old one.
- Enterprise suffixes (weak): `UserDataManager`, `ConfigHelper`, `ResponseHandlerService` where sibling code uses plain names. Framework conventions (Django `Manager`, Express handlers) are fine.
- Vocabulary drift (medium): `fetchUser` in a file that says `getUser`.

## 10. Files and READMEs

- Unrequested files (strong): `IMPLEMENTATION_SUMMARY.md`, `CHANGES.md`, `NOTES.md`, `example_usage.py`, `demo.ts`, `test_quick.py`, `*_backup.*`, `*.orig`. Find them with `git diff --name-status --diff-filter=A $BASE...HEAD`. Delete only after confirming the user did not ask for them.
- README slop (medium): emoji headings (`## 🚀 Features`), `Key Features` bullet walls, badge farms, and words like `comprehensive`, `robust`, `seamless`, `powerful`, `production-ready`, `blazing fast`. Replace with what the project does, how to install it, and one real usage example. Use [prose-en.md](prose-en.md) or [prose-ko.md](prose-ko.md) for the text itself.

## 11. Commits, PRs, review comments

- Commit messages (medium): vague subjects (`enhance functionality and improve code quality`), bullet bodies that restate the diff, trial-and-error narration (`Initially tried...`), counts like `All 47 tests passing`. Write the reason for the change in the project's own format. Assistant trailers (`Generated with`, `Co-Authored-By` naming an AI) are a tell, but some projects require disclosure; follow the project's rule.
- PR descriptions (medium): `This PR introduces...`, default `Summary / Changes / Test Plan` sections the repo's template does not ask for, file-by-file lists, pasted CI logs. Say what changed for the user, why, and how it was verified. Follow the repo's PR template when one exists.
- Review comments (medium): flattery, overstated severity, multi-paragraph explanations of a one-line issue. State the problem, the evidence, and the suggested fix.

## 12. Example

Before (added in the branch):

```python
def load_user(user_id: str) -> User:
    # Step 1: Fetch the user from the database
    try:
        user = db.get_user(user_id)  # Updated to use new db API
    except Exception as e:
        print(f"❌ Error loading user: {e}")
        return None
    # Ensure user is valid
    if user is None or not isinstance(user, User):
        return None
    return user
```

After, when `db.get_user` already raises `UserNotFound` and the rest of the module lets database errors propagate:

```python
def load_user(user_id: str) -> User:
    return db.get_user(user_id)
```

Report: removed narrating and reviewer comments, an emoji print, a catch that hid database errors behind `None`, and a type check on a typed return. Behavior change: callers now receive `UserNotFound` instead of `None`; `api/users.py` already handles it. Tests pass.
