#!/usr/bin/env python3
import argparse
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import uuid

DEFAULT_MODEL = "swe-2-max"


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def free_model(payload, model):
    families = payload["families"]
    if not isinstance(families, list):
        raise ValueError("Unrecognized model listing")
    matches = [variant for family in families for variant in family["variants"]
               if variant["model_uid"] == model]
    if len(matches) != 1 or matches[0].get("cost_tier") != "Free":
        raise ValueError(f"{model} is not unambiguously advertised as Free")
    return matches[0]


def verify_free(binary, model):
    try:
        result = subprocess.run([binary, "models", "list", "--format", "json"],
                                capture_output=True, text=True, timeout=60, check=True)
        free_model(json.loads(result.stdout), model)
    except (subprocess.SubprocessError, OSError, ValueError, KeyError, TypeError) as error:
        raise ValueError("Could not verify the exact model as Free; no task started") from error
    return timestamp()


def command(binary, model, prompt, export, resume=None):
    result = [binary, "--model", model, "--permission-mode", "dangerous",
              "--respect-workspace-trust", "false", "--prompt-file", str(prompt),
              "--export", str(export), "-p"]
    if resume:
        result.extend(["--resume", resume])
    return result


def write_manifest(path, value):
    with path.open("w", encoding="utf-8") as output:
        json.dump(value, output, indent=2)
        output.write("\n")


def stop_owned_process(process):
    if process.poll() is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.wait()


def run(args, binary, checked_at):
    workspace = args.workspace.expanduser().resolve()
    prompt = args.prompt.expanduser().resolve()
    if not workspace.is_dir() or not prompt.is_file():
        raise ValueError("Workspace must be a directory and prompt must be a readable file")
    if not prompt.read_text(encoding="utf-8").strip():
        raise ValueError("Prompt must not be empty")
    if os.environ.get("DEVIN_SANDBOX", "").strip().lower() not in {"", "0", "false", "no"}:
        raise ValueError("DEVIN_SANDBOX is enabled; resolve this conflict before using dangerous mode")
    state = args.state_dir.expanduser().resolve()
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = None
    if args.resume:
        lock_name = hashlib.sha256(f"{workspace}\0{args.resume}".encode()).hexdigest()
        lock = (state / f"session-{lock_name}.lock").open("a")
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            lock.close()
            raise ValueError("This exact session is already locked by another runner") from error
    process = None
    manifest_path = None
    manifest = None
    try:
        slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", prompt.stem)[:60] or "task"
        folder = state / "runs" / f"{datetime.now(timezone.utc):%Y%m%dT%H%M%SZ}-{slug}-{uuid.uuid4().hex[:10]}"
        folder.mkdir(parents=True, mode=0o700)
        prompt_copy = folder / "prompt.md"
        prompt_copy.write_bytes(prompt.read_bytes())
        log = folder / "output.log"
        export = folder / "session.json"
        manifest_path = folder / "run.json"
        manifest = {"model": args.model, "cost_tier": "Free", "pricing_checked_at": checked_at,
                    "workspace": str(workspace), "prompt": str(prompt_copy),
                    "resume_session_id": args.resume, "log": str(log), "export": str(export),
                    "timeout_seconds": args.timeout_seconds, "started_at": timestamp(), "status": "starting"}
        write_manifest(manifest_path, manifest)
        with log.open("x", encoding="utf-8") as output:
            process = subprocess.Popen(command(binary, args.model, prompt_copy, export, args.resume),
                                       cwd=workspace, stdout=output, stderr=subprocess.STDOUT,
                                       start_new_session=True)
            manifest.update(pid=process.pid, status="running")
            write_manifest(manifest_path, manifest)
            print(f"{args.model} · Free (checked {checked_at})", flush=True)
            print(f"PID: {process.pid}\nLog: {log}\nManifest: {manifest_path}", flush=True)
            try:
                code = process.wait(timeout=args.timeout_seconds)
                manifest.update(status="completed" if code == 0 else "failed", returncode=code)
            except subprocess.TimeoutExpired:
                stop_owned_process(process)
                code = 124
                manifest.update(status="timed_out", returncode=code)
            except KeyboardInterrupt:
                stop_owned_process(process)
                code = 130
                manifest.update(status="interrupted", returncode=code)
        manifest["finished_at"] = timestamp()
        write_manifest(manifest_path, manifest)
        print(f"Outcome: {manifest['status']} (exit {code})\nManifest: {manifest_path}", flush=True)
        if code:
            print("Partial edits may remain. Inspect the log and workspace before resuming the exact session.",
                  file=sys.stderr)
        return code if code >= 0 else 128 - code
    except BaseException:
        if process is not None:
            stop_owned_process(process)
        if manifest is not None:
            manifest.update(status="runner_error", finished_at=timestamp())
            write_manifest(manifest_path, manifest)
        raise
    finally:
        if lock is not None:
            lock.close()


def handle_termination(*_):
    raise KeyboardInterrupt()


def main():
    parser = argparse.ArgumentParser(description="Run bounded Devin work only on an explicitly free SWE-2 model")
    parser.add_argument("--workspace", type=Path)
    parser.add_argument("--prompt", type=Path)
    parser.add_argument("--resume")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--timeout-seconds", type=int, default=3600)
    state_home = Path(os.environ.get("XDG_STATE_HOME") or Path.home() / ".local/state")
    parser.add_argument("--state-dir", type=Path, default=state_home / "devin-maxxing")
    parser.add_argument("--check", action="store_true", help="Check current free availability without starting an agent")
    args = parser.parse_args()
    if not re.fullmatch(r"swe-2(?:-[a-z0-9]+)*", args.model):
        parser.error("Use an exact SWE-2 model UID")
    if args.timeout_seconds < 1:
        parser.error("Timeout must be positive")
    if not args.check and (args.workspace is None or args.prompt is None):
        parser.error("--workspace and --prompt are required to start a task")
    if args.resume is not None and (not args.resume.strip() or args.resume.startswith("-")):
        parser.error("--resume requires an exact session ID")
    binary = shutil.which("devin")
    if binary is None:
        parser.error("Install and authenticate Devin CLI first")
    os.umask(0o077)
    signal.signal(signal.SIGTERM, handle_termination)
    try:
        checked_at = verify_free(binary, args.model)
        if args.check:
            print(f"{args.model} · Free (checked {checked_at}); no agent started")
            return 0
        return run(args, binary, checked_at)
    except (ValueError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
