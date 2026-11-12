"""hive/tools/land.py pushes a merge only when the fast tests pass on it, against a local bare remote."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LAND = ROOT / "hive" / "tools" / "land.py"
ENV = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.invalid",
       "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.invalid"}


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, env=ENV, check=True).stdout.strip()


class Land(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.remote = self.tmp / "remote.git"
        git(self.tmp, "init", "-q", "--bare", "-b", "main", str(self.remote))
        self.work = self.tmp / "work"
        git(self.tmp, "clone", "-q", str(self.remote), str(self.work))
        git(self.work, "checkout", "-q", "-b", "main")
        (self.work / "hive" / "tools").mkdir(parents=True)
        for f in ("land.py", "project.py"):
            shutil.copy(ROOT / "hive" / "tools" / f, self.work / "hive" / "tools" / f)
        (self.work / "ok").write_text("1")
        self.config("test -s ok")
        git(self.work, "add", ".")
        git(self.work, "commit", "-q", "-m", "start")
        git(self.work, "push", "-q", "origin", "HEAD:main")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def config(self, tests):
        (self.work / "hive" / "project.json").write_text(json.dumps({"slug": "t", "fast_tests": tests}))

    def land(self):
        return subprocess.run([sys.executable, str(self.work / "hive/tools/land.py"), "--wait", "5"], cwd=self.work,
                              capture_output=True, text=True, env=ENV)

    def remote_head(self):
        return git(self.remote, "rev-parse", "main")

    def test_failing_tests_push_nothing_and_passing_tests_push(self):
        before = self.remote_head()
        (self.work / "ok").write_text("")  # the fast tests (`test -s ok`) now fail
        git(self.work, "commit", "-q", "-am", "break it")
        r = self.land()
        self.assertEqual(r.returncode, 1, r.stdout + r.stderr)
        self.assertIn("nothing was pushed", r.stdout)
        self.assertEqual(self.remote_head(), before)
        (self.work / "ok").write_text("2")
        git(self.work, "commit", "-q", "-am", "fix it")
        r = self.land()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        self.assertEqual(self.remote_head(), git(self.work, "rev-parse", "HEAD"))

    def test_main_that_moved_is_merged_before_the_tests(self):
        other = self.tmp / "other"
        git(self.tmp, "clone", "-q", str(self.remote), str(other))
        (other / "theirs").write_text("x")
        git(other, "add", "theirs")
        git(other, "commit", "-q", "-m", "theirs")
        git(other, "push", "-q", "origin", "HEAD:main")
        (self.work / "mine").write_text("y")
        git(self.work, "add", "mine")
        git(self.work, "commit", "-q", "-m", "mine")
        r = self.land()
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
        files = git(self.remote, "ls-tree", "--name-only", "main").split()
        self.assertIn("theirs", files)
        self.assertIn("mine", files)

    def test_attribution_and_a_dirty_tree_are_refused(self):
        (self.work / "a").write_text("1")
        git(self.work, "add", "a")
        git(self.work, "commit", "-q", "-m", "a\n\nCo-Authored-By: Claude <noreply@anthropic.com>")
        self.assertEqual(self.land().returncode, 2)
        git(self.work, "reset", "-q", "--soft", "HEAD~1")
        git(self.work, "commit", "-q", "-m", "a")
        (self.work / "ok").write_text("dirty")
        self.assertEqual(self.land().returncode, 2)


if __name__ == "__main__":
    unittest.main()
