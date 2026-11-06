"""Tests for install profiles, the /setup command and detection (python3 -m unittest discover -s scripts -p "test_*.py")."""
import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import kitlib  # noqa: E402

APPLY = kitlib.KIT / "scripts" / "apply-kit.py"
BASE = ["--set", "PROJECT_NAME=Smoke", "--set", "ORG=example", "--set", "DOCS_REPO=smoke-docs"]


def run(target, *args):
    return subprocess.run([sys.executable, str(APPLY), "--target", str(target), *args],
                          capture_output=True, text=True)


def files(root):
    return {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file() and ".git" not in p.parts}


class TempRepo(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self._tmp.name) / "repo"
        self.root.mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def apply(self, *args, ok=True):
        res = run(self.root, *args)
        if ok:
            self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        return res

    def manifest(self):
        return json.loads((self.root / ".aiagents-manifest.json").read_text(encoding="utf-8"))


class ProfileTest(TempRepo):
    def test_default_is_full_and_backwards_compatible(self):
        self.apply("--type", "backend-go", *BASE)
        got = files(self.root)
        for f in ("agents/developer.md", "agents/architect.md", ".agents/skills/project-intake/SKILL.md",
                  ".agents/skills/add-endpoint/SKILL.md", "docs/agents/prompts/00-start-here.md",
                  ".github/prompts/start-here.prompt.md", "README.md", "CONTRIBUTING.md",
                  ".opencode/commands/setup.md", ".github/prompts/setup.prompt.md"):
            self.assertIn(f, got)
        self.assertEqual(self.manifest()["profile"], "full")

    def test_lean_installs_only_the_core_minimum(self):
        self.apply("--type", "backend-go", "--profile", "lean", *BASE)
        got = files(self.root)
        agents = {f.split("/")[1] for f in got if f.startswith("agents/")}
        skills = {f.split("/")[2] for f in got if f.startswith(".agents/skills/")}
        self.assertEqual(agents, {f"{a}.md" for a in kitlib.LEAN_AGENTS})
        self.assertEqual(skills, set(kitlib.LEAN_SKILLS))
        for f in ("AGENTS.md", "docs/agents/interaction-standard.md", "docs/agents/access-and-conflicts.md",
                  "docs/agents/templates/work-log.md", "docs/agents/THIRD-PARTY-NOTICES.md",
                  ".opencode/commands/setup.md", ".github/prompts/setup.prompt.md",
                  ".opencode/agents/lead.md", ".github/agents/explorer.agent.md"):
            self.assertIn(f, got)
        for f in ("README.md", "CONTRIBUTING.md", "docs/agents/prompts/00-start-here.md", ".github/CODEOWNERS"):
            self.assertNotIn(f, got)
        m = self.manifest()
        self.assertEqual((m["profile"], m["agents"]), ("lean", []))

    def test_lean_with_pack_and_agent_uses_overrides(self):
        self.apply("--type", "backend-go", "--profile", "lean", "--pack", "postgres-infra",
                   "--agent", "developer", *BASE)
        got = files(self.root)
        self.assertIn("agents/developer.md", got)
        self.assertIn("agents/server-inspector.md", got)
        self.assertIn("docs/rules/postgresql-infrastructure.md", got)
        self.assertNotIn("agents/architect.md", got)
        dev = (self.root / "agents/developer.md").read_text(encoding="utf-8")
        typed = (kitlib.KIT / "repo-types/backend-go/agents/developer.md").read_text(encoding="utf-8")
        self.assertEqual(dev.splitlines()[1], typed.splitlines()[1])

    def test_unknown_agent_is_rejected(self):
        res = self.apply("--type", "docs-hub", "--profile", "lean", "--agent", "nope", *BASE, ok=False)
        self.assertEqual(res.returncode, 2)
        self.assertIn("unknown --agent", res.stderr)

    def test_update_keeps_profile_and_adds_pack(self):
        self.apply("--type", "docs-hub", "--profile", "lean", *BASE)
        self.apply("--update", "--pack", "multi-tenant-saas", "--agent", "architect")
        m = self.manifest()
        self.assertEqual((m["profile"], m["packs"], m["agents"]), ("lean", ["multi-tenant-saas"], ["architect"]))
        got = files(self.root)
        self.assertIn(".agents/skills/tenant-table/SKILL.md", got)
        self.assertIn("agents/architect.md", got)
        self.assertNotIn("agents/developer.md", got)

    def test_update_of_old_manifest_without_profile_stays_full(self):
        self.apply("--type", "docs-hub", *BASE)
        m = self.manifest()
        del m["profile"], m["agents"]
        (self.root / ".aiagents-manifest.json").write_text(json.dumps(m), encoding="utf-8")
        res = self.apply("--update", "--dry-run")
        self.assertIn("profile full", res.stdout)


class BootstrapTest(TempRepo):
    def test_bootstrap_then_install_adopts_command_files(self):
        self.apply("--bootstrap")
        self.assertEqual(files(self.root), {".opencode/commands/setup.md", ".github/prompts/setup.prompt.md",
                                            ".aiagents/kit.local", ".aiagents/.gitignore"})
        self.assertEqual((self.root / ".aiagents/.gitignore").read_text(encoding="utf-8"), "kit.local\n")
        res = self.apply("--type", "docs-hub", "--profile", "lean", *BASE)
        self.assertNotIn("setup.md", res.stdout.split("skipped")[1])
        self.assertIn(".opencode/commands/setup.md", self.manifest()["files"])

    def test_bootstrap_dry_run_writes_nothing(self):
        self.apply("--bootstrap", "--dry-run")
        self.assertEqual(files(self.root), set())


class CommandRenderTest(unittest.TestCase):
    def test_setup_renders_for_both_tools(self):
        out = kitlib.render_command(kitlib.KIT / "core" / "commands" / "setup.md")
        oc_path, oc = out["opencode"]
        vs_path, vs = out["vscode"]
        self.assertEqual((oc_path, vs_path), (".opencode/commands/setup.md", ".github/prompts/setup.prompt.md"))
        self.assertTrue(oc.startswith("---\ndescription: "))
        self.assertIn("$ARGUMENTS", oc)
        self.assertNotIn(kitlib.ARGS_TOKEN, oc + vs)
        self.assertIn("\nname: setup\n", vs)
        self.assertIn("\nagent: agent\n", vs)
        self.assertNotIn("$ARGUMENTS", vs)
        self.assertEqual(kitlib.PLACEHOLDER.findall(oc + vs), [])

    def test_bad_sources_are_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "x.md"
            for text in ("no frontmatter", "---\nname: y\ndescription: d\nargument-hint: h\n---\nbody <ARGUMENTS>\n",
                         "---\nname: x\ndescription: d\nargument-hint: h\n---\nbody without token\n"):
                p.write_text(text, encoding="utf-8")
                with self.subTest(text=text[:20]), self.assertRaises(ValueError):
                    kitlib.render_command(p)


class LeanKeepTest(unittest.TestCase):
    def test_rules(self):
        keep = set(kitlib.LEAN_AGENTS)
        cases = [
            ("agents/lead.md", "core", True), ("agents/developer.md", "type:backend-go", False),
            ("agents/server-inspector.md", "pack:postgres-infra", True),
            (".agents/skills/tdd/SKILL.md", "core", True), (".agents/skills/project-intake/SKILL.md", "core", False),
            (".agents/skills/add-endpoint/SKILL.md", "type:backend-go", False),
            ("docs/rules/x.md", "pack:p", True), ("AGENTS.md", "core+type+packs", True),
            ("README.md", "type:backend-go", False), (".github/CODEOWNERS", "core", False),
        ]
        for dest, origin, want in cases:
            with self.subTest(dest=dest):
                self.assertIs(kitlib.lean_keep(dest, origin, keep), want)


class DetectTest(TempRepo):
    def write(self, name, text=""):
        (self.root / name).parent.mkdir(parents=True, exist_ok=True)
        (self.root / name).write_text(text, encoding="utf-8")

    def test_types(self):
        self.assertEqual(kitlib.detect(self.root)["types"], ["docs-hub"])
        self.write("go.mod", "module x\nrequire github.com/jackc/pgx/v5 v5.0.0\n")
        self.write("package.json", '{"dependencies": {"next": "1"}}')
        self.write("template.yaml", "Transform: AWS::Serverless-2016-10-31\n")
        d = kitlib.detect(self.root)
        self.assertEqual(d["types"], ["backend-go", "frontend-nextjs", "serverless-sam"])
        self.assertIn("postgres-infra", d["packs"])
        self.assertIn("aws-serverless-cost", d["packs"])
        self.assertIn("developer", d["agents"])

    def test_name_owner_host_and_tool_from_repo(self):
        self.write(".git/config", '[remote "origin"]\n\turl = https://user@git.example.invalid/acme/shop.git\n')
        self.write(".opencode/x", "")
        d = kitlib.detect(self.root)
        self.assertEqual((d["project_name"], d["owner"], d["code_host"]), ("shop", "acme", "git.example.invalid"))
        self.assertEqual(d["ai_tools"], ["opencode"])
        self.assertNotIn("user", json.dumps(d))

    def test_keywords_suggest_packs(self):
        self.write("README.md", "Multi-tenant payroll app with TOTP MFA")
        self.assertEqual(kitlib.detect(self.root)["packs"], ["auth-sessions-mfa", "multi-tenant-saas", "payroll-gr"])

    def test_cli_detect_prints_json(self):
        res = self.apply("--detect")
        self.assertEqual(json.loads(res.stdout)["type"], "docs-hub")


if __name__ == "__main__":
    unittest.main()
