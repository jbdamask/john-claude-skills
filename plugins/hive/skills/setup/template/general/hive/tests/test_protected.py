"""The protected-folders guard: a protected folder is refused to everyone but the agent of its labelled bead.

Run: python3 -m unittest discover -s hive/tests
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
sys.path.insert(0, str(ROOT / "hive" / "tools"))
sys.path.insert(0, str(ROOT / "hive" / "hooks"))
import protected_guard as guard  # noqa: E402

LABEL = "held-out-check"
BEADS = {
    "ab-check": {"status": "in_progress", "labels": [LABEL]},
    "ab-plain": {"status": "in_progress", "labels": []},
    "ab-unclaimed": {"status": "open", "labels": [LABEL]},
}
FAKE_BD = f"""#!{sys.executable}
import json, sys
beads = json.loads({json.dumps(json.dumps(BEADS))})
a = sys.argv[1:]
if a[:1] == ["show"] and a[1] in beads:
    print(json.dumps([{{"id": a[1], **beads[a[1]]}}]))
else:
    sys.exit(1)
"""
AGENTS = {"a-check": "ab-check", "a-plain": "ab-plain", "a-unclaimed": "ab-unclaimed"}


class Protected(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = os.path.realpath(tempfile.mkdtemp())
        cls.env = dict(os.environ)
        home = cls.tmp
        cls.prot = os.path.join(home, "held-out")
        cls.open = os.path.join(home, "notes")
        for d in (cls.prot, cls.open):
            os.makedirs(d)
            Path(d, "item.txt").write_text("x\n")
        os.symlink(cls.prot, os.path.join(home, "shortcut"))
        bindir = os.path.join(home, "bin")
        os.makedirs(bindir)
        Path(bindir, "bd").write_text(FAKE_BD)
        os.chmod(os.path.join(bindir, "bd"), 0o755)
        os.environ["PATH"] = bindir + os.pathsep + os.environ["PATH"]
        os.environ["HOME"] = home
        cls.transcript = os.path.join(home, "sess.jsonl")
        Path(cls.transcript).write_text("{}\n")
        sub = Path(home, "sess", "subagents")
        sub.mkdir(parents=True)
        for aid, bid in AGENTS.items():
            first = {"agentId": aid, "type": "user",
                     "message": {"role": "user", "content": f"Your name: e-{bid}. Do bead {bid}."}}
            (sub / f"agent-{aid}.jsonl").write_text(json.dumps(first) + "\n")
        cls.cfg = {"protected_folders": [{"path": "~/held-out", "label": LABEL}]}

    @classmethod
    def tearDownClass(cls):
        os.environ.clear()
        os.environ.update(cls.env)
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def call(self, tool, inp, agent="a-plain", cfg=None):
        data = {"tool_name": tool, "tool_input": inp, "cwd": self.tmp, "session_id": "sess",
                "transcript_path": self.transcript}
        if agent:
            data["agent_id"] = agent
        return guard.decide(data, self.cfg if cfg is None else cfg)

    def bash(self, cmd, agent="a-plain", cfg=None):
        return self.call("Bash", {"command": cmd}, agent, cfg)

    def test_a_plain_agent_is_refused_by_read_cat_ls_and_grep(self):
        item = os.path.join(self.prot, "item.txt")
        self.assertIn("protected folder", self.call("Read", {"file_path": item}))
        for cmd in [f"cat {item}", f"ls {self.prot}", f"ls -la {self.prot}/", f"grep -n x {item}",
                    "cat ~/held-out/item.txt", "head $HOME/held-out/item.txt", "ls ${HOME}/held-out",
                    "cd ~ && cat held-out/item.txt", "cat held-out/item.txt", "D=~/held-out; cat $D/item.txt",
                    "cat ~/held-o*/item.txt", "cat shortcut/item.txt", "grep -r x ~", f"rg x {self.tmp}",
                    f"python3 -c \"print(open('{item}').read())\"", f"cd {self.prot} && cat item.txt"]:
            self.assertIsNotNone(self.bash(cmd), cmd)
        self.assertIsNotNone(self.call("Grep", {"pattern": "x", "path": self.prot}))
        self.assertIsNotNone(self.call("Grep", {"pattern": "x", "path": self.tmp}))
        self.assertIsNotNone(self.call("Glob", {"pattern": "held-out/*", "path": self.tmp}))
        self.assertIsNotNone(self.call("Glob", {"pattern": "**/*.txt", "path": self.tmp}))

    def test_the_labelled_beads_agent_may_read(self):
        item = os.path.join(self.prot, "item.txt")
        self.assertIsNone(self.call("Read", {"file_path": item}, "a-check"))
        for cmd in [f"cat {item}", f"ls {self.prot}", f"grep -n x {item}", "cat ~/held-out/item.txt"]:
            self.assertIsNone(self.bash(cmd, "a-check"), cmd)
        self.assertIsNone(self.call("Grep", {"pattern": "x", "path": self.prot}, "a-check"))

    def test_an_unclaimed_labelled_bead_or_an_unknown_agent_is_refused(self):
        self.assertIsNotNone(self.bash(f"ls {self.prot}", "a-unclaimed"))
        self.assertIn("could not tell", self.bash(f"ls {self.prot}", "a-nobody"))

    def test_the_lead_only_when_the_entry_says_so(self):
        self.assertIsNotNone(self.bash(f"ls {self.prot}", agent=None))
        cfg = {"protected_folders": [{"path": "~/held-out", "label": LABEL, "lead_may_read": True}]}
        self.assertIsNone(self.bash(f"ls {self.prot}", agent=None, cfg=cfg))
        self.assertIsNotNone(self.bash(f"ls {self.prot}", cfg=cfg))

    def test_an_unprotected_folder_is_untouched(self):
        item = os.path.join(self.open, "item.txt")
        self.assertIsNone(self.call("Read", {"file_path": item}))
        for cmd in [f"cat {item}", f"ls {self.open}", f"grep -rn x {self.open}", "cat ~/notes/item.txt",
                    "ls ~/held-out-not", "git status"]:
            self.assertIsNone(self.bash(cmd), cmd)
        self.assertIsNone(self.call("Grep", {"pattern": "x", "path": self.open}))
        self.assertIsNone(self.call("Glob", {"pattern": "*.txt", "path": self.open}))

    def test_an_empty_list_changes_nothing(self):
        self.assertIsNone(self.bash(f"cat {self.prot}/item.txt", cfg={}))
        self.assertIsNone(self.bash(f"cat {self.prot}/item.txt", cfg={"protected_folders": []}))

    def test_only_the_lead_adds_the_label(self):
        self.assertIn("only the lead", self.bash(f"bd update ab-plain --add-label {LABEL}"))
        self.assertIn("only the lead", self.bash(f"BEADS_ACTOR=e bd create x -l {LABEL} -d y"))
        self.assertIsNone(self.bash(f"bd update ab-plain --add-label {LABEL}", agent=None))
        self.assertIsNone(self.bash("bd update ab-plain --add-label role:gardener"))

    def test_the_hook_as_installed(self):
        """The script itself, in a copy of the hive tree whose project.json protects the folder."""
        tree = Path(self.tmp, "repo", "hive")
        (tree / "hooks").mkdir(parents=True, exist_ok=True)
        (tree / "tools").mkdir(exist_ok=True)
        shutil.copy(ROOT / "hive" / "hooks" / "protected_guard.py", tree / "hooks")
        shutil.copy(ROOT / "hive" / "tools" / "project.py", tree / "tools")
        (tree / "project.json").write_text(json.dumps(self.cfg))

        def run(agent):
            data = {"tool_name": "Bash", "tool_input": {"command": "cat ~/held-out/item.txt"}, "cwd": self.tmp,
                    "agent_id": agent, "session_id": "sess", "transcript_path": self.transcript}
            return subprocess.run([sys.executable, str(tree / "hooks" / "protected_guard.py")],
                                  input=json.dumps(data), capture_output=True, text=True, timeout=30).stdout

        out = json.loads(run("a-plain"))["hookSpecificOutput"]
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertEqual(run("a-check"), "")


if __name__ == "__main__":
    unittest.main()
