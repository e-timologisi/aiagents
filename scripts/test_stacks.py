"""Tests for stack profiles, the conversational-start pack and the additive-only baseline."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import stacks  # noqa: E402
from kitlib import KIT  # noqa: E402

APPLY = str(KIT / "scripts" / "apply-kit.py")
VALUES = ["--set", "PROJECT_NAME=Smoke", "--set", "ORG=example", "--set", "DOCS_REPO=smoke-docs"]


def run(*args):
    return subprocess.run([sys.executable, APPLY, *args], capture_output=True, text=True)


class ParserTest(unittest.TestCase):
    def test_nested_lists_maps_and_flow(self):
        data = stacks.parse_stack_yaml(
            'id: x\nfits: [a, "b c"]\nos_support: {windows: yes, macos: no}\ntoolchain:\n'
            '  - id: node  # comment\n    admin: false\n    install:\n      windows: "winget install a#b"\n'
            '  - id: git\n    admin: true\nrisks:\n  - "one"\n')
        self.assertEqual(data["fits"], ["a", "b c"])
        self.assertEqual(data["os_support"], {"windows": "yes", "macos": "no"})
        self.assertEqual(data["toolchain"][0], {"id": "node", "admin": False, "install": {"windows": "winget install a#b"}})
        self.assertIs(data["toolchain"][1]["admin"], True)
        self.assertEqual(data["risks"], ["one"])

    def test_bad_indentation_is_an_error(self):
        with self.assertRaises(ValueError):
            stacks.parse_stack_yaml("a: 1\n    b: 2\n")


class CatalogueTest(unittest.TestCase):
    PACKS = [p.name for p in (KIT / "packs").iterdir() if p.is_dir()]

    def test_catalogue_and_schema(self):
        self.assertEqual(stacks.stack_ids(), ["api-go", "api-node", "data-python", "docs-hub", "mobile-expo",
                                              "serverless-sam", "web-nextjs"])
        for sid in stacks.stack_ids():
            self.assertEqual(stacks.validate_stack(sid, self.PACKS), [], sid)

    def test_aliases_point_to_existing_repo_types(self):
        want = {"web-nextjs": "frontend-nextjs", "api-go": "backend-go", "docs-hub": "docs-hub",
                "serverless-sam": "serverless-sam"}
        for sid, rtype in want.items():
            self.assertEqual(stacks.load_stack(sid)["repo_type"], rtype)

    def test_missing_install_command_is_reported(self):
        spec = stacks.load_stack("api-node")
        del spec["toolchain"][0]["install"]["windows"]
        orig = stacks.load_stack
        stacks.load_stack = lambda sid: spec
        try:
            errors = stacks.validate_stack("api-node", self.PACKS)
        finally:
            stacks.load_stack = orig
        self.assertTrue(any("no install command for windows" in e for e in errors), errors)


class ApplyTest(unittest.TestCase):
    def apply(self, *args, name="proj"):
        d = pathlib.Path(tempfile.mkdtemp()) / name
        d.mkdir()
        subprocess.run(["git", "init", "-q", "-b", "main", str(d)], check=True)
        res = run(*args, "--target", str(d), *VALUES)
        return d, res

    def test_stack_alias_equals_type_output(self):
        a, ra = self.apply("--stack", "api-go")
        b, rb = self.apply("--type", "backend-go")
        self.assertEqual(ra.returncode, 0, ra.stderr)
        self.assertEqual(rb.returncode, 0, rb.stderr)
        files = lambda d: {p.relative_to(d).as_posix(): p.read_bytes() for p in d.rglob("*")
                           if p.is_file() and ".git/" not in p.as_posix() and p.name != ".aiagents-manifest.json"}
        self.assertEqual(files(a), files(b))
        self.assertEqual(json.loads((a / ".aiagents-manifest.json").read_text())["stack"], "api-go")
        self.assertNotIn("stack", json.loads((b / ".aiagents-manifest.json").read_text()))

    def test_own_stack_with_pack_and_update(self):
        d, res = self.apply("--stack", "api-node", "--pack", "conversational-start")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertIn("Node.js, TypeScript strict", (d / "AGENTS.md").read_text(encoding="utf-8"))
        start = (d / ".opencode" / "commands" / "start-here.md").read_text(encoding="utf-8")
        self.assertIn("agent: lead", start)
        self.assertIn("agent: lead", (d / ".github" / "prompts" / "start-here.prompt.md").read_text(encoding="utf-8"))
        self.assertNotIn("global_agent", (d / ".opencode" / "commands" / "setup.md").read_text(encoding="utf-8"))
        self.assertIn("conversational start", (d / "agents" / "lead.md").read_text(encoding="utf-8").lower())
        upd = run("--target", str(d), "--update", "--dry-run")
        self.assertEqual(upd.returncode, 0, upd.stdout + upd.stderr)
        self.assertIn("updated: 0", upd.stdout)

    def test_pack_is_inert_without_it(self):
        d, res = self.apply("--stack", "web-nextjs")
        self.assertEqual(res.returncode, 0, res.stderr)
        self.assertNotIn("conversational start", (d / "agents" / "lead.md").read_text(encoding="utf-8").lower())
        self.assertFalse((d / "agents" / "setup.md").exists())

    def test_type_and_stack_are_exclusive_and_unknown_stack_fails(self):
        self.assertEqual(run("--type", "docs-hub", "--stack", "docs-hub", "--target", tempfile.gettempdir()).returncode, 2)
        self.assertEqual(run("--stack", "nope", "--target", tempfile.gettempdir()).returncode, 2)

    def test_list_and_info(self):
        out = run("--list-stacks")
        self.assertIn("mobile-expo\tbeta", out.stdout)
        info = json.loads(run("--stack-info", "web-nextjs", "--os", "windows").stdout)
        self.assertTrue(all(t["install"].startswith("winget") for t in info["toolchain"]))


class BootstrapAndBaselineTest(unittest.TestCase):
    def test_bootstrap_files_are_current_and_global_has_no_project_agent(self):
        res = subprocess.run([sys.executable, str(KIT / "scripts" / "build-bootstrap.py"), "--check"], capture_output=True, text=True)
        self.assertEqual(res.returncode, 0, res.stderr)
        out = stacks.bootstrap_outputs()
        self.assertIn("agent: setup", out["commands/opencode/setup.md"])
        self.assertNotIn("agent: lead", out["commands/opencode/start-here.md"])
        self.assertNotIn("agent: setup", out["commands/vscode/setup.prompt.md"])
        self.assertNotIn("model:", out["commands/opencode-agents/setup.md"])

    def test_baseline_holds_and_detects_change(self):
        self.assertEqual(stacks.baseline_problems(), [])
        with tempfile.TemporaryDirectory() as d:
            data = json.loads(stacks.BASELINE.read_text(encoding="utf-8"))
            data["files"]["core/agents/developer.md"] = "0" * 64
            data["files"]["core/agents/gone.md"] = "0" * 64
            fake = pathlib.Path(d) / "b.json"
            fake.write_text(json.dumps(data), encoding="utf-8")
            orig, stacks.BASELINE = stacks.BASELINE, fake
            try:
                problems = stacks.baseline_problems()
            finally:
                stacks.BASELINE = orig
        self.assertEqual(len(problems), 2, problems)


if __name__ == "__main__":
    unittest.main()
