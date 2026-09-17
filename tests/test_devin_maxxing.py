import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import fcntl
import hashlib

SCRIPT = Path(__file__).resolve().parents[1] / "skills/devin-maxxing/scripts/run_task.py"
spec = importlib.util.spec_from_file_location("devin_maxxing_runner", SCRIPT)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def listing(*variants):
    return {"families": [{"variants": list(variants)}]}


class PricingTests(unittest.TestCase):
    def test_exact_free_model(self):
        variant = {"model_uid": "swe-2-max", "cost_tier": "Free"}
        self.assertEqual(runner.free_model(listing(variant), "swe-2-max"), variant)

    def test_paid_unknown_or_other_variants_are_not_fallbacks(self):
        for variant in [{"model_uid": "swe-2-max", "cost_tier": "Paid"},
                        {"model_uid": "swe-2-max"},
                        {"model_uid": "swe-2", "cost_tier": "Free"},
                        {"model_uid": "swe-2-max", "cost_tier": "free"}]:
            with self.subTest(variant=variant), self.assertRaises(ValueError):
                runner.free_model(listing(variant), "swe-2-max")

    def test_duplicate_model_is_rejected(self):
        variant = {"model_uid": "swe-2-max", "cost_tier": "Free"}
        with self.assertRaises(ValueError):
            runner.free_model(listing(variant, variant), "swe-2-max")

    def test_no_ambiguous_resume_or_sandbox_in_command(self):
        args = runner.command("devin", "swe-2-max", "prompt with spaces.md", "export.json", "exact-id")
        self.assertEqual(args[args.index("--model") + 1], "swe-2-max")
        self.assertEqual(args[args.index("--permission-mode") + 1], "dangerous")
        self.assertEqual(args[args.index("--resume") + 1], "exact-id")
        self.assertIn("prompt with spaces.md", args)
        self.assertNotIn("--continue", args)
        self.assertNotIn("--sandbox", args)


class RunnerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="devin-maxxing-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.workspace = self.root / "workspace"
        self.workspace.mkdir()
        self.prompt = self.root / "task.md"
        self.prompt.write_text("Synthetic runner fixture; no agent work.")
        self.state = self.root / "state"
        self.calls = self.root / "calls.jsonl"
        self.binary = self.root / "devin"
        self.binary.write_text("#!" + sys.executable + "\n" + '''import json, os, sys, time
from pathlib import Path
args = sys.argv[1:]
with Path(os.environ['FAKE_CALLS']).open('a') as output:
    output.write(json.dumps(args) + '\\n')
if args == ['models', 'list', '--format', 'json']:
    print(os.environ['FAKE_LISTING'])
    raise SystemExit(int(os.environ.get('FAKE_LISTING_EXIT', '0')))
if os.environ.get('FAKE_SLEEP'):
    time.sleep(30)
if '--export' in args:
    Path(args[args.index('--export') + 1]).write_text(json.dumps({'fixture': True}))
print('Synthetic CLI fixture completed')
raise SystemExit(int(os.environ.get('FAKE_RUN_EXIT', '0')))
''')
        self.binary.chmod(0o700)
        self.env = dict(os.environ, PATH=str(self.root) + os.pathsep + os.environ.get("PATH", ""),
                        FAKE_CALLS=str(self.calls), DEVIN_SANDBOX="false",
                        FAKE_LISTING=json.dumps(listing({"model_uid": "swe-2-max", "cost_tier": "Free"})))

    def execute(self, *extra):
        return subprocess.run([sys.executable, str(SCRIPT), "--workspace", str(self.workspace),
                               "--prompt", str(self.prompt), "--state-dir", str(self.state), *extra],
                              env=self.env, text=True, capture_output=True, timeout=15)

    def recorded(self):
        return [json.loads(line) for line in self.calls.read_text().splitlines()]

    def manifest(self):
        return json.loads(next((self.state / "runs").glob("*/run.json")).read_text())

    def test_check_only_never_starts_task_or_writes_state(self):
        result = self.execute("--check")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(self.recorded()), 1)
        self.assertFalse(self.state.exists())

    def test_run_pins_model_preserves_prompt_and_records_evidence(self):
        result = self.execute()
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.recorded()
        self.assertEqual(calls[0], ["models", "list", "--format", "json"])
        self.assertEqual(calls[1][calls[1].index("--model") + 1], "swe-2-max")
        manifest = self.manifest()
        self.assertEqual(manifest["status"], "completed")
        self.assertEqual(manifest["workspace"], str(self.workspace.resolve()))
        self.assertEqual(Path(manifest["prompt"]).read_text(), self.prompt.read_text())
        self.assertEqual(list(self.workspace.iterdir()), [])
        self.assertEqual(Path(manifest["log"]).stat().st_mode & 0o077, 0)

    def test_changed_pricing_and_invalid_schema_never_launch(self):
        for value in [listing({"model_uid": "swe-2-max", "cost_tier": "Paid"}), {}, {"families": None}]:
            with self.subTest(value=value):
                self.env["FAKE_LISTING"] = json.dumps(value)
                result = self.execute()
                self.assertEqual(result.returncode, 2)
                self.assertFalse(self.state.exists())
        self.assertTrue(all(call == ["models", "list", "--format", "json"] for call in self.recorded()))

    def test_listing_failure_never_launches(self):
        self.env["FAKE_LISTING_EXIT"] = "1"
        result = self.execute()
        self.assertEqual(result.returncode, 2)
        self.assertEqual(len(self.recorded()), 1)

    def test_sandbox_conflict_never_launches(self):
        self.env["DEVIN_SANDBOX"] = "1"
        result = self.execute()
        self.assertEqual(result.returncode, 2)
        self.assertIn("DEVIN_SANDBOX", result.stderr)
        self.assertEqual(len(self.recorded()), 1)

    def test_exact_resume_rechecks_pricing(self):
        result = self.execute("--resume", "fixture-exact-id")
        self.assertEqual(result.returncode, 0, result.stderr)
        args = self.recorded()[1]
        self.assertEqual(args[args.index("--resume") + 1], "fixture-exact-id")
        self.assertEqual(self.manifest()["resume_session_id"], "fixture-exact-id")

    def test_duplicate_resume_lock_prevents_second_run(self):
        self.state.mkdir()
        name = hashlib.sha256(f"{self.workspace.resolve()}\0fixture-id".encode()).hexdigest()
        with (self.state / f"session-{name}.lock").open("a") as held:
            fcntl.flock(held, fcntl.LOCK_EX | fcntl.LOCK_NB)
            result = self.execute("--resume", "fixture-id")
        self.assertEqual(result.returncode, 2)
        self.assertIn("already locked", result.stderr)
        self.assertEqual(len(self.recorded()), 1)

    def test_failure_records_nonzero_outcome(self):
        self.env["FAKE_RUN_EXIT"] = "7"
        result = self.execute()
        self.assertEqual(result.returncode, 7)
        self.assertEqual(self.manifest()["status"], "failed")

    def test_timeout_stops_only_owned_fixture(self):
        self.env["FAKE_SLEEP"] = "1"
        result = self.execute("--timeout-seconds", "1")
        self.assertEqual(result.returncode, 124, result.stderr)
        manifest = self.manifest()
        self.assertEqual(manifest["status"], "timed_out")
        with self.assertRaises(ProcessLookupError):
            os.kill(manifest["pid"], 0)


if __name__ == "__main__":
    unittest.main()
