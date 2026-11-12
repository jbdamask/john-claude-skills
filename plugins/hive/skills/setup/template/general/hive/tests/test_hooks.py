"""Hooks: what they add stays under Claude Code's limit, and each guard refuses what it should and passes the rest.

Claude Code cuts a hook's added text at about 10,000 characters; the limit here is 8,500. Every command hook in
.claude/settings.json must be measured below, so a new hook fails this test until it is.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HOOKS = ROOT / "hive" / "hooks"
LIMIT = 8500
sys.path.insert(0, str(HOOKS))
sys.path.insert(0, str(ROOT / "hive" / "tools"))
import no_close_blocked  # noqa: E402
import no_push_main  # noqa: E402
import shared_tree_guard  # noqa: E402
import worktree_write_guard  # noqa: E402


def hook(name, data, env=None, args=()):
    full = {**os.environ, "CLAUDE_PROJECT_DIR": str(ROOT), **(env or {})}
    out = subprocess.run([sys.executable, str(HOOKS / name), *args], input=json.dumps(data), capture_output=True,
                         text=True, env=full, cwd=ROOT, timeout=30)
    assert out.returncode == 0, out.stderr
    return out.stdout


def context(stdout):
    stdout = stdout.strip()
    if not stdout:
        return ""
    data = json.loads(stdout)
    spec = data.get("hookSpecificOutput") or {}
    return spec.get("additionalContext") or spec.get("permissionDecisionReason") or ""


def denied(stdout):
    return bool(stdout.strip()) and json.loads(stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"


def commands():
    settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    return [(e, h["command"]) for e, groups in settings.get("hooks", {}).items() for g in groups
            for h in g.get("hooks", []) if h.get("type") == "command"]


def prime_hook(stdin):
    cmd = next(c for e, c in commands() if e == "SubagentStart" and "bd prime" in c)
    with tempfile.TemporaryDirectory() as d:
        stub = Path(d) / "bd"
        stub.write_text("#!/bin/sh\nprintf 'PRIME STUB\\n'\n")
        stub.chmod(0o755)
        env = {**os.environ, "CLAUDE_PROJECT_DIR": str(ROOT), "PATH": d + os.pathsep + os.environ["PATH"]}
        return subprocess.run(["/bin/sh", "-c", cmd], input=stdin, capture_output=True, text=True, env=env,
                              cwd=ROOT, timeout=30).stdout


class Sizes(unittest.TestCase):
    def measure(self, event, cmd):
        if "lead_context.py start" in cmd:
            return context(hook("lead_context.py", {}, {"HIVE_ROLE": "lead"}, ["start"]))
        if "lead_context.py checkin" in cmd:
            return context(hook("lead_context.py", {"prompt": "HIVE CHECK-IN"}, args=["checkin"]))
        if "term.py --hook" in cmd:
            out = subprocess.run([sys.executable, str(ROOT / "hive/tools/term.py"), "--hook", event],
                                 capture_output=True, text=True, cwd=ROOT).stdout
            return context(out)
        if "bd prime" in cmd:
            return (ROOT / ".beads" / "PRIME.md").read_text(encoding="utf-8")
        if "no_email.py" in cmd:
            return context(hook("no_email.py", {"tool_name": "Bash", "tool_input": {"command": "curl -A a@b.co x"}}))
        if "no_push_main.py" in cmd:
            return context(hook("no_push_main.py", {"tool_name": "Bash", "agent_id": "a",
                                                    "tool_input": {"command": "git push origin HEAD:main"}}))
        if "no_close_blocked.py" in cmd:
            return json.dumps(no_close_blocked.deny({"x-1": ["x-2", "x-3"]}))
        if "worktree_write_guard.py" in cmd:
            return context(hook("worktree_write_guard.py", {"tool_name": "Bash", "cwd": "/r/.claude/worktrees/a",
                                                            "tool_input": {"command": "echo x > src/x.py"}}))
        if "shared_tree_guard.py" in cmd:
            return context(hook("shared_tree_guard.py", {"tool_name": "Write", "agent_id": "a",
                                                         "tool_input": {"file_path": str(ROOT / "src" / "x.py")}}))
        if "protected_guard.py" in cmd:
            import protected_guard
            return max(protected_guard.READ_REASON.format(folder="~/" + "x" * 200, label="x" * 60, lead=", or the lead"),
                       protected_guard.UNKNOWN_REASON.format(folder="~/" + "x" * 200, why="x" * 120),
                       protected_guard.LABEL_REASON.format(label="x" * 60), key=len)
        if "spawn_gate.py" in cmd:
            import contextlib
            import io
            import spawn_gate
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                spawn_gate.deny_stale("ab-1", ["target: " + "x" * 120] * 3)
            return context(buf.getvalue())
        raise AssertionError(f"{event} hook is not measured by this test; add it: {cmd}")

    def test_every_settings_hook_is_measured_and_under_the_limit(self):
        for event, cmd in commands():
            text = self.measure(event, cmd)
            self.assertLessEqual(len(text), LIMIT, f"{event}: {cmd[:60]}")

    def test_brief_under_the_limit(self):
        self.assertLessEqual(len((ROOT / ".beads" / "PRIME.md").read_text(encoding="utf-8")), LIMIT)

    @unittest.skipIf(shutil.which("bd") is None, "bd not installed")
    def test_bd_prime_prints_the_brief_under_the_limit(self):
        out = subprocess.run(["bd", "prime", "--no-memories"], capture_output=True, text=True, cwd=ROOT).stdout
        self.assertIn("agent brief", out)
        self.assertLessEqual(len(out), LIMIT)

    def test_lead_gets_its_runbook_only_as_lead(self):
        self.assertIn("## Spawning", context(hook("lead_context.py", {}, {"HIVE_ROLE": "lead"}, ["start"])))
        self.assertEqual(hook("lead_context.py", {}, {"HIVE_ROLE": ""}, ["start"]), "")
        self.assertIn("## Check-in", context(hook("lead_context.py", {"prompt": "HIVE CHECK-IN"}, args=["checkin"])))

    @unittest.skipIf(shutil.which("jq") is None, "jq not installed")
    def test_fresh_eyes_reader_gets_no_brief_and_others_do(self):
        self.assertEqual(prime_hook(json.dumps({"agent_type": "fresh-eyes-reader"})), "")
        out = json.loads(prime_hook(json.dumps({"agent_type": "general-purpose"})))
        self.assertEqual(out["hookSpecificOutput"]["additionalContext"], "PRIME STUB\n")


class Guards(unittest.TestCase):
    def test_no_push_main(self):
        for cmd in ["git push", "git push origin", "git push origin HEAD:main", "git push origin main",
                    "git -C /r push origin +HEAD:refs/heads/main", "cd x && git push --all origin"]:
            self.assertTrue(no_push_main.pushes_main(cmd), cmd)
        for cmd in ["git push origin my-branch", "git push origin HEAD:feature", "git status", "echo git push"]:
            self.assertFalse(no_push_main.pushes_main(cmd), cmd)

    def test_no_push_main_spares_the_lead(self):
        data = {"tool_name": "Bash", "tool_input": {"command": "git push"}}
        self.assertEqual(hook("no_push_main.py", data), "")
        self.assertTrue(denied(hook("no_push_main.py", {**data, "agent_id": "a1"})))

    def test_worktree_write_guard(self):
        self.assertTrue(worktree_write_guard.bash_reason("cat > src/a.py <<EOF\nx\nEOF"))
        self.assertTrue(worktree_write_guard.bash_reason("sed -i '' s/a/b/ src/a.py"))
        self.assertIsNone(worktree_write_guard.bash_reason("python3 -m unittest 2>&1 | tail -5"))
        self.assertIsNone(worktree_write_guard.bash_reason("echo hi > ~/.hive/p/scratch/e-x-1/out.txt"))

    def test_shared_tree_guard(self):
        allowed = shared_tree_guard.DEFAULT_MAY_EDIT
        root = shared_tree_guard.shared_root()
        self.assertEqual(shared_tree_guard.guarded(str(root / "src" / "a.py"), allowed), "src/a.py")
        self.assertEqual(shared_tree_guard.guarded(str(root / "hive" / "tools" / "x.py"), allowed), "hive/tools/x.py")
        self.assertIsNone(shared_tree_guard.guarded(str(root / "hive" / "specs" / "1-a.md"), allowed))
        self.assertIsNone(shared_tree_guard.guarded(str(root / "README.md"), allowed))
        self.assertIsNone(shared_tree_guard.guarded(str(root / ".claude/worktrees/a/src/a.py"), allowed))

    def test_no_email(self):
        self.assertTrue(denied(hook("no_email.py", {"tool_name": "Bash", "tool_input": {"command": "x a@b.co"}})))
        self.assertEqual(hook("no_email.py", {"tool_name": "Bash", "tool_input": {"command": "git log"}}), "")

    def test_no_close_blocked_reads_the_close(self):
        recs = no_close_blocked.closes('BEADS_ACTOR=e bd close ab-1 --reason "x: done"')
        self.assertEqual(recs[0]["ids"], ["ab-1"])
        self.assertEqual(no_close_blocked.closes("bd show ab-1"), [])


if __name__ == "__main__":
    unittest.main()
