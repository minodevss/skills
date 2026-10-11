import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SKILL = Path(__file__).resolve().parents[1] / "skills/deslop"


def load(name):
    spec = importlib.util.spec_from_file_location(f"deslop_{name}", SKILL / f"scripts/{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


scan = load("scan")
compare = load("compare")


def rules(text, path="doc.md"):
    lines = [(n, line, True) for n, line in enumerate(text.splitlines(), 1)]
    return [hit["rule"] for hit in scan.scan_lines(path, lines)[0]]


class ScanTests(unittest.TestCase):
    def test_english_chat_leftovers_and_puffery_are_strong(self):
        hits = scan.scan_lines("doc.md", [(1, "Certainly! Here is the plan. It stands as a testament to "
                                              "our work. I hope this helps!", True)])[0]
        self.assertEqual({hit["rule"] for hit in hits},
                         {"en-chat-opener", "en-testament", "en-chat-closer"})
        self.assertTrue(all(hit["level"] == "strong" for hit in hits))

    def test_negative_parallelism_with_noun_subject(self):
        self.assertIn("en-negative-parallelism",
                      rules("Observability isn't just a nice-to-have — it's a necessity."))

    def test_korean_patterns(self):
        found = rules("물론입니다! 원격 근무는 단순한 근무 형태가 아니라 새로운 패러다임입니다.\n"
                      "블로그를 운영함에 있어 시간을 가졌다. 도움이 되셨기를 바랍니다!")
        for rule_id in ("ko-chat-opener", "ko-antithesis", "ko-cliche", "ko-translationese-strong",
                        "ko-translationese", "ko-chat-closer"):
            self.assertIn(rule_id, found)

    def test_forms_humans_use_more_are_not_flagged(self):
        self.assertEqual(rules("이번 기회를 통해 배운 것이다. 계약에 대해 논의했다. 문이 열려 진행했다."), [])

    def test_plain_prose_has_no_hits(self):
        text = ("Run the tests before you push. The cache lives in ~/.cache/app and is safe to delete.\n"
                "We moved the job to 3 a.m. because the backup window overlapped with it.\n"
                "회의는 3시에 시작합니다. 자료는 공유 폴더에 올려 두었고 질문은 스레드에 남겨 주세요.")
        self.assertEqual(rules(text), [])

    def test_quotes_code_and_front_matter_are_skipped(self):
        text = ("---\ntitle: I hope this helps\n---\n> Certainly! Here is a quote.\n"
                "Use `delve into` here.\n```\nIt stands as a testament to code.\n```\n")
        self.assertEqual(rules(text), [])

    def test_overlapping_matches_report_the_highest_level_once(self):
        self.assertEqual(rules("It is a testament to them."), ["en-testament"])

    def test_code_rules_apply_only_to_code(self):
        self.assertEqual(rules("Cast it as any value.", "notes.md"), [])
        found = rules("const data = resp as any;\nconst x = 1  // Updated to use new API\n", "api.ts")
        self.assertEqual(found, ["code-type-escape", "comment-change-note"])

    def test_two_line_swallowed_exception(self):
        found = rules("try:\n    run()\nexcept Exception:\n    pass\n", "job.py")
        self.assertEqual(found, ["code-swallowed-error"])

    def test_diff_scans_only_added_lines_with_new_numbers(self):
        diff = ("diff --git a/x.py b/x.py\n--- a/x.py\n+++ b/x.py\n@@ -1,2 +1,3 @@\n"
                " # Step 1: old comment\n+# Step 2: new comment\n value = 1\n")
        files = scan.parse_diff(diff)
        hits = scan.scan_lines("x.py", files["x.py"])[0]
        self.assertEqual([(hit["rule"], hit["line"]) for hit in hits], [("comment-step", 2)])

    def test_cli_exit_codes(self):
        script = SKILL / "scripts/scan.py"
        run = lambda *args, text="": subprocess.run([sys.executable, str(script), *args], input=text,
                                                    capture_output=True, text=True, timeout=30)
        self.assertEqual(run("--fail-on", "strong", text="I hope this helps!\n").returncode, 1)
        self.assertEqual(run("--fail-on", "strong", text="The build is green.\n").returncode, 0)
        self.assertEqual(run("/nonexistent/file.md").returncode, 2)

    def test_skill_documents_pass_their_own_scanner(self):
        for path in [SKILL / "SKILL.md", *sorted((SKILL / "references").glob("*.md"))]:
            with self.subTest(path=path.name):
                lines = [(n, line, True) for n, line in enumerate(path.read_text().splitlines(), 1)]
                self.assertEqual(scan.scan_lines(str(path), lines)[0], [])

    def test_repository_skill_documents_have_no_strong_or_medium_hits(self):
        for path in sorted(SKILL.parent.glob("*/SKILL.md")) + sorted(SKILL.parent.glob("*/references/*.md")):
            with self.subTest(path=str(path.relative_to(SKILL.parent))):
                lines = [(n, line, True) for n, line in enumerate(path.read_text().splitlines(), 1)]
                hits = scan.scan_lines(str(path), lines)[0]
                self.assertEqual([hit for hit in hits if hit["level"] != "weak"], [])


class CompareTests(unittest.TestCase):
    def test_identical_text_passes(self):
        text = "Latency fell 37% in most regions. See [docs](https://example.com).\n"
        result = compare.compare(text, text)
        self.assertEqual(result["blocking"], {})
        self.assertEqual(result["warnings"], {})

    def test_changed_number_url_and_code_block(self):
        before = "It cut latency by 37%. See https://a.example.\n```sh\nmake test\n```\n"
        after = "It cut latency by 40%. See https://b.example.\n```sh\nmake check\n```\n"
        blocking = compare.compare(before, after)["blocking"]
        self.assertEqual(blocking["numbers"], {"lost": ["37"], "added": ["40"]})
        self.assertEqual(set(blocking), {"numbers", "urls", "code_blocks"})

    def test_dropping_a_repeated_mention_is_not_a_loss(self):
        before = "Ledgerline 2.0 is out. Version 2.0 adds sync.\n"
        self.assertEqual(compare.compare(before, "Ledgerline 2.0 adds sync.\n")["blocking"], {})

    def test_list_markers_and_thousands_separators_are_not_facts(self):
        before = "1. Ship 1,000 units.\n2. Ship again.\n"
        after = "Ship 1000 units, then ship again.\n"
        self.assertEqual(compare.compare(before, after)["blocking"], {})

    def test_hedge_and_quantifier_changes_are_reported(self):
        warnings = compare.compare("Most users may see it. 일부 사용자에게 적용될 수 있습니다.",
                                   "All users see it. 사용자에게 적용됩니다.")["warnings"]
        self.assertEqual(warnings["hedges"], {"lost": ["may", "most", "수 있", "일부"], "added": ["all"]})

    def test_cli_exit_codes(self):
        script = SKILL / "scripts/compare.py"
        with tempfile.TemporaryDirectory() as folder:
            original, same, changed = (Path(folder) / name for name in ("a.md", "b.md", "c.md"))
            original.write_text("Revenue grew 12%.\n")
            same.write_text("Revenue grew 12%.\n")
            changed.write_text("Revenue grew a lot.\n")
            run = lambda *args: subprocess.run([sys.executable, str(script), *map(str, args)],
                                               capture_output=True, text=True, timeout=30)
            self.assertEqual(run(original, same).returncode, 0)
            self.assertEqual(run(original, changed).returncode, 1)
            self.assertEqual(run(original, Path(folder) / "missing.md").returncode, 2)


if __name__ == "__main__":
    unittest.main()
