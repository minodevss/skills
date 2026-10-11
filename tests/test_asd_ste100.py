import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/asd-ste100"
SCRIPT = SKILL / "scripts/check.py"
spec = importlib.util.spec_from_file_location("ste_check", SCRIPT)
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)


def rules(text, mode="auto"):
    return [hit["rule"] for hit in check.check_text("doc.md", text, mode)[0]]


class LimitTests(unittest.TestCase):
    def test_procedure_and_descriptive_limits(self):
        step = "1. " + " ".join(["Remove"] + ["the cover"] * 10) + ".\n"
        self.assertIn("procedure-length", rules(step))
        description = "The pump " + " ".join(["supplies fuel"] * 12) + ".\n"
        self.assertIn("descriptive-length", rules(description))
        self.assertNotIn("descriptive-length", rules("The pump supplies fuel to the engine.\n"))

    def test_word_count_conventions(self):
        sentence = 'Set the TEST SWITCH to OFF and torque the bolt to 25 Nm (see Fig. 3).'
        self.assertEqual(len(check.words(sentence, False)), 12)
        self.assertEqual(len(check.words('Push the "PUSH TO TEST" button on panel No. 4.', False)), 7)

    def test_paragraph_limit_and_contents_line(self):
        paragraph = " ".join(["The pump supplies fuel."] * 7) + "\n"
        self.assertIn("paragraph-length", rules(paragraph))
        self.assertEqual(rules("Contents: 1. Words · 2. Verbs · 3. Sentences · 4. Procedures\n"), [])

    def test_sentence_split_keeps_abbreviations_and_quotes(self):
        self.assertEqual(len(check.sentences('Remove the cover, e.g. the top panel. Then stop.')), 2)
        self.assertEqual(len(check.sentences('Write "Remove the seal." A step can have a result.')), 2)
        self.assertEqual(len(check.sentences('This is Issue 9. It is current.')), 2)


class GrammarTests(unittest.TestCase):
    def test_verb_rules(self):
        found = rules("The pump is supplying fuel. The valve has been opened. It's on; stop.\n")
        for rule_id in ("progressive", "perfect", "contraction", "semicolon"):
            self.assertIn(rule_id, found)

    def test_modal_construction_reports_once(self):
        self.assertEqual(rules("1. The filter should be replaced.\n"), ["auxiliary-construction"])

    def test_state_participle_is_only_a_warning(self):
        hits = check.check_text("doc.md", "The valve is closed.\n", "auto")[0]
        self.assertEqual([(hit["rule"], hit["level"]) for hit in hits], [("passive-descriptive", "warn")])

    def test_unapproved_word_gives_alternative(self):
        hits = check.check_text("doc.md", "1. Utilize the torque wrench.\n", "auto")[0]
        self.assertIn("'use'", hits[0]["hint"])

    def test_approved_ing_words_and_quotes_are_not_flagged(self):
        self.assertNotIn("ing-form", rules("During the test, the remaining fuel goes out.\n"))
        self.assertEqual(rules('Do not write "the valve is being opened" in a step.\n'), [])

    def test_procedure_review_rules(self):
        found = rules("1. Remove the cover and then disconnect the cable.\n2. Open the valve if the light comes on.\n")
        self.assertIn("two-instructions", found)
        self.assertIn("condition-after-command", found)


class KoreanTests(unittest.TestCase):
    def test_korean_rules(self):
        found = rules("1. 사용자 인증 토큰 만료 시간 설정을 변경할 것.\n2. 초기화를 수행합니다.\n\n"
                      "서버 성능을 향상시키기 위해 데이터가 저장되어집니다. 재시도는 적절히 합니다.\n")
        for rule_id in ("ko-noun-instruction", "ko-noun-chain", "ko-empty-verb", "ko-needless-passive",
                        "ko-double-passive", "ko-vague"):
            self.assertIn(rule_id, found)

    def test_korean_counts_eojeol(self):
        sentence = "설정 " * 26 + "합니다."
        self.assertIn("descriptive-length", rules(sentence + "\n"))
        self.assertEqual(rules("설정이 없으면 기본값을 씁니다.\n"), [])


class CliTests(unittest.TestCase):
    def run_check(self, *args, text=""):
        return subprocess.run([sys.executable, str(SCRIPT), *args], input=text, capture_output=True,
                              text=True, timeout=30)

    def test_exit_codes(self):
        self.assertEqual(self.run_check("--fail-on", "error", text="The valve should open.\n").returncode, 1)
        self.assertEqual(self.run_check("--fail-on", "error", text="The valve opens.\n").returncode, 0)
        self.assertEqual(self.run_check("/nonexistent.md").returncode, 2)


class SkillTests(unittest.TestCase):
    def test_compare_copy_matches_deslop(self):
        self.assertEqual((SKILL / "scripts/compare.py").read_bytes(),
                         (ROOT / "skills/deslop/scripts/compare.py").read_bytes())

    def test_skill_documents_have_no_checker_errors(self):
        for path in [SKILL / "SKILL.md", *sorted((SKILL / "references").glob("*.md"))]:
            with self.subTest(path=path.name):
                hits = check.check_text(str(path), path.read_text(), "auto")[0]
                self.assertEqual([hit for hit in hits if hit["level"] == "error"], [])


if __name__ == "__main__":
    unittest.main()
