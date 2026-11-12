"""Roles: the agent definitions match their sources, and the spawn gate refuses an agent in the wrong role.

Run: python3 -m unittest discover -s hive/tests
"""
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "hive" / "tools"))
sys.path.insert(0, str(ROOT / "hive" / "hooks"))
import roles  # noqa: E402
import spawn_gate  # noqa: E402

GATE = ROOT / "hive" / "hooks" / "spawn_gate.py"
BEADS = {
    "ab-gard": {"status": "open", "dependencies": [], "labels": ["role:gardener"]},
    "ab-plain": {"status": "open", "dependencies": [], "labels": []},
    "ab-later": {"status": "open", "dependencies": [{"id": "ab-first", "dependency_type": "blocks", "status": "open"}],
                 "labels": []},
}
FAKE_BD = f"""#!{sys.executable}
import json, sys
beads = json.loads({json.dumps(json.dumps(BEADS))})
args = sys.argv[1:]
if args and args[0] == "ready":
    print(json.dumps([{{"id": i}} for i, b in beads.items() if not b["dependencies"]]))
elif args and args[0] == "show":
    print(json.dumps([{{"id": args[1], **beads[args[1]]}}] if args[1] in beads else []))
else:
    sys.exit(2)
"""


def gate(prompt, agent_type=None):
    """(the hook's decision or None, the logged record) for one spawn, with bd replaced by a fake."""
    with tempfile.TemporaryDirectory() as d:
        (Path(d) / "bd").write_text(FAKE_BD)
        (Path(d) / "bd").chmod(0o755)
        env = {**os.environ, "PATH": d + os.pathsep + os.environ.get("PATH", ""),
               "HIVE_SPAWN_GATE_LOG": str(Path(d) / "gate.jsonl")}
        tool_input = {"prompt": prompt, "description": "d"}
        if agent_type:
            tool_input["subagent_type"] = agent_type
        out = subprocess.run([sys.executable, str(GATE)], env=env, capture_output=True, text=True, check=True,
                             input=json.dumps({"tool_name": "Agent", "tool_input": tool_input, "cwd": d})).stdout
        rec = json.loads((Path(d) / "gate.jsonl").read_text().splitlines()[-1])
    return (json.loads(out)["hookSpecificOutput"] if out.strip() else None), rec


class Definitions(unittest.TestCase):
    def test_definitions_match_their_sources(self):
        self.assertEqual(roles.stale(), [], "run python3 hive/tools/roles.py build")

    def test_each_definition_carries_its_whole_brief(self):
        for role in roles.roles():
            text = (ROOT / ".claude" / "agents" / f"{role['name']}.md").read_text(encoding="utf-8")
            self.assertIn(f"\nname: {role['name']}\n", text)
            for src in role["sources"]:
                self.assertIn(roles.source(src), text)

    def test_every_agent_definition_is_in_the_registry(self):
        known = {r["name"] for r in roles.roles()}
        on_disk = {p.stem for p in (ROOT / ".claude" / "agents").glob("*.md")}
        self.assertLessEqual(on_disk, known, "agent definitions not in hive/ROLES.json")

    def test_roles_without_the_brief_are_the_ones_the_hook_skips(self):
        settings = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
        cmd = next(h["command"] for g in settings["hooks"]["SubagentStart"] for h in g["hooks"]
                   if "bd prime" in h["command"])
        for role in roles.roles():
            self.assertEqual(f'.agent_type == "{role["name"]}"' in cmd, not role["agent_brief"], role["name"])

    def test_scheduled_roles_are_in_the_cron_table(self):
        crons = (ROOT / "hive" / "CRONS.md").read_text(encoding="utf-8")
        for role in roles.roles():
            if role.get("every_days"):
                self.assertIn(f"-l role:{role['name']}", crons)
                self.assertIn(f'subagent_type "{role["name"]}"', crons)

    def test_no_two_roles_share_a_lane(self):
        lanes = [r["lane"] for r in roles.roles()]
        self.assertEqual(len(lanes), len(set(lanes)))


class SpawnGate(unittest.TestCase):
    def test_role_bead_with_its_agent_type_passes(self):
        out, rec = gate("Your name: e-ab-gard. Do bead ab-gard.", "gardener")
        self.assertIsNone(out)
        self.assertEqual(rec["decision"], "passed")

    def test_role_bead_spawned_as_a_plain_agent_is_refused(self):
        out, rec = gate("Your name: e-ab-gard. Do bead ab-gard.")
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertIn('subagent_type "gardener"', out["permissionDecisionReason"])
        self.assertEqual(rec["decision"], "role_mismatch")

    def test_role_bead_spawned_as_another_role_is_refused(self):
        out, rec = gate("Your name: e-ab-gard. Do bead ab-gard.", "strategist")
        self.assertEqual(rec["decision"], "role_mismatch")

    def test_role_agent_on_a_plain_bead_or_no_bead_is_refused(self):
        self.assertEqual(gate("Your name: e-ab-plain. Do bead ab-plain.", "gardener")[1]["decision"], "role_mismatch")
        self.assertEqual(gate("Write the memo.", "gardener")[1]["decision"], "role_mismatch")

    def test_plain_agent_and_the_beadless_role_pass(self):
        self.assertIsNone(gate("Your name: e-ab-plain. Do bead ab-plain.")[0])
        self.assertIsNone(gate("Read the attached work and answer.", "fresh-eyes-reader")[0])

    def test_bead_with_an_open_blocker_is_refused(self):
        out, rec = gate("Your name: e-ab-later. Do bead ab-later.")
        self.assertEqual(rec["decision"], "refused")
        self.assertIn("ab-first", out["permissionDecisionReason"])

    def test_notes_that_overrule_the_text_are_caught_until_spec_ok(self):
        bead = {"title": "Edit docs/a.md", "description": "Read: docs/a.md", "acceptance_criteria": "",
                "notes": "LEAD: edit docs/b.md, not docs/a.md"}
        self.assertTrue(spawn_gate.stale_text(bead))
        bead["notes"] += "\nSPEC-OK: target moved to docs/b.md"
        self.assertEqual(spawn_gate.stale_text(bead), [])


if __name__ == "__main__":
    unittest.main()
