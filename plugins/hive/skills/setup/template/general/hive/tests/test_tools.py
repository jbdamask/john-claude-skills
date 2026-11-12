"""The team's tools: the spec brief check, the issue check, the rule budget, generated files, rule pointers, scratch."""
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "hive" / "tools"))
import issue_check  # noqa: E402
import scratch  # noqa: E402
import spec_brief  # noqa: E402
import team_use  # noqa: E402

GOOD = ("""**You asked for**: "Do the thing"

**You will get**
- The thing.

**You will not get**
- The other thing.

**Cost**: two tasks, no money.

**Decide**
1. Spend $5 on a run?
   Recommended: yes.

""" + spec_brief.HOW + """

Detail for agents: [spec](https://github.com/o/r/blob/main/hive/specs/1-thing.md)
""")


def spec_root(d):
    (Path(d) / "hive" / "specs").mkdir(parents=True)
    (Path(d) / "hive" / "specs" / "1-thing.md").write_text("spec")
    return Path(d)


class SpecBrief(unittest.TestCase):
    def test_good_brief_passes(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertEqual(spec_brief.problems(GOOD, spec_root(d)), [])

    def test_long_brief_fails(self):
        with tempfile.TemporaryDirectory() as d:
            bad = spec_brief.problems(GOOD.replace("- The thing.", "- " + "word " * 250), spec_root(d))
            self.assertTrue(any("the limit is 200" in b for b in bad))

    def test_missing_part_time_estimate_and_questions_fail(self):
        with tempfile.TemporaryDirectory() as d:
            root = spec_root(d)
            self.assertTrue(spec_brief.problems(GOOD.replace("**Cost**", "Cost"), root))
            self.assertTrue(spec_brief.problems(GOOD.replace("no money.", "about three days."), root))
            four = GOOD.replace("1. Spend $5 on a run?\n   Recommended: yes.", "1. A?\n2. B?\n3. C?\n4. D?")
            self.assertTrue(spec_brief.problems(four, root))


class IssueCheck(unittest.TestCase):
    def states(self, issues, epics=()):
        return {r["number"]: r["state"] for r in issue_check.needs_action(issues, list(epics), "2026-01-01")}

    @staticmethod
    def issue(n, labels=(), created="2026-02-01"):
        return {"number": n, "title": f"t{n}", "labels": [{"name": l} for l in labels], "createdAt": created}

    def test_new_bug_and_approved_are_reported(self):
        got = self.states([self.issue(10), self.issue(11, ["bug"]), self.issue(12, ["approved_spec"])])
        self.assertEqual(got, {10: "new", 11: "bug", 12: "approved"})

    def test_issues_in_hand_or_older_than_the_flow_are_not(self):
        issues = [self.issue(10, ["drafting"]), self.issue(11, ["pending_approval"]), self.issue(12, ["proposal"]),
                  self.issue(13, ["approved_spec"]), self.issue(14, created="2025-12-01")]
        self.assertEqual(self.states(issues, ["Feature (#13)"]), {})
        self.assertEqual(self.states([self.issue(9, ["approved_spec"])], ["Epic for #90"]), {9: "approved"})


class Rules(unittest.TestCase):
    def test_team_rules_stay_within_their_budget(self):
        r = team_use.rules()
        self.assertEqual(len(r["team"]), len(team_use.TEAM_RULE_FILES), "a team rule file is missing")
        self.assertLessEqual(r["team_total"], team_use.TEAM_BUDGET, r["team"])

    def test_generated_files_match_a_fresh_build(self):
        out = subprocess.run([sys.executable, str(ROOT / "hive/tools/generated.py"), "check"], cwd=ROOT,
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)

    def test_every_path_and_section_a_rule_file_names_exists(self):
        path = re.compile(r"(?<![\w/~.<-])((?:hive|\.beads|\.claude)/[\w./-]*[\w/])")
        section = re.compile(r"((?:[\w.-]+/)*[A-Z][\w-]*\.md) \"([^\"]+)\"")
        files = team_use.TEAM_RULE_FILES + team_use.PROJECT_RULE_FILES + ["hive/README.md", ".beads/PRIME.md"]
        bad = []
        for rel in files:
            text = (ROOT / rel).read_text(encoding="utf-8")
            for m in path.finditer(text):
                p = m.group(1).rstrip(".,;:)")
                if text[m.end():m.end() + 1] in "<*" or any(c in p for c in "<>*{}"):
                    continue
                if p.startswith(".claude/worktrees") or p.startswith(".beads/plans"):
                    continue
                if not (ROOT / p).exists():
                    bad.append(f"{rel}: {p}")
            for name, sec in section.findall(text):
                target = next((c for c in (name, f"hive/{name}") if (ROOT / c).is_file()), None)
                heads = [] if target is None else [l.lstrip("#").strip() for l in
                                                   (ROOT / target).read_text(encoding="utf-8").splitlines()
                                                   if l.startswith("#")]
                if not any(h.startswith(sec) for h in heads):
                    bad.append(f'{rel}: {name} "{sec}"')
        self.assertEqual(bad, [])


class Scratch(unittest.TestCase):
    def test_closed_beads_folders_are_listed_for_deletion(self):
        with tempfile.TemporaryDirectory() as d:
            for name in ("e-ab-1", "e-ab-2-1", "e-zz-9"):
                (Path(d) / name).mkdir()
                (Path(d) / name / "f").write_text("x" * 10)
            by_name = {scratch.agent_name("ab-1"): {"id": "ab-1", "status": "closed"},
                       scratch.agent_name("ab-2.1"): {"id": "ab-2.1", "status": "open"}}
            groups = scratch.sort(Path(d), by_name)
            self.assertEqual([p.name for p, _, _ in groups["closed"]], ["e-ab-1"])
            self.assertEqual([p.name for p, _, _ in groups["open"]], ["e-ab-2-1"])
            self.assertEqual([p.name for p, _, _ in groups["unknown"]], ["e-zz-9"])
            self.assertEqual(groups["closed"][0][1], 10)


if __name__ == "__main__":
    unittest.main()
