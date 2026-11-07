"""Tests for the process gates: handover-check.sh, check-pinned-actions.py, ticket-key and install wiring."""
import copy
import importlib.util
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import kitlib  # noqa: E402

CORE = kitlib.KIT / "core"
GATE = CORE / "scripts" / "handover-check.sh"
HEAD = "a" * 40
OLD = "b" * 40


def load_pinned():
    spec = importlib.util.spec_from_file_location("check_pinned", CORE / "scripts" / "check-pinned-actions.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def check(name, conclusion, started, status="COMPLETED"):
    return {"__typename": "CheckRun", "name": name, "status": status, "conclusion": conclusion, "startedAt": started}


CLEAN = {
    "pr": {
        "state": "OPEN", "mergeStateStatus": "CLEAN", "headRefOid": HEAD,
        "labels": [{"name": "agent-reported"}],
        "comments": [
            {"author": {"login": "x"}, "createdAt": "2026-01-01T10:00:00Z", "body": f"AGENT-REPORT tip={OLD}\nold"},
            {"author": {"login": "x"}, "createdAt": "2026-01-01T11:00:00Z", "body": f"AGENT-REPORT tip={HEAD}\nPR ..."},
            {"author": {"login": "y"}, "createdAt": "2026-01-01T12:00:00Z", "body": "looks good, AGENT-REPORT tip=nope"},
        ],
        "statusCheckRollup": [
            check("test", "SUCCESS", "2026-01-01T09:30:00Z"),  # latest by time, not by list order
            check("test", "FAILURE", "2026-01-01T09:00:00Z"),
            {"__typename": "StatusContext", "context": "ext", "state": "SUCCESS", "startedAt": "2026-01-01T09:00:00Z"},
        ],
    },
    "threads": [{"isResolved": True}],
}


@unittest.skipUnless(shutil.which("bash"), "bash not available")
class HandoverCheckTest(unittest.TestCase):
    def run_gate(self, data, *extra, env=None):
        with tempfile.TemporaryDirectory() as d:
            f = pathlib.Path(d) / "pr.json"
            f.write_text(json.dumps(data), encoding="utf-8")
            return subprocess.run(["bash", str(GATE), "--json-file", str(f), "example/repo", "7", *extra],
                                  capture_output=True, text=True, env={**os.environ, **(env or {})})

    def variant(self, fn):
        data = copy.deepcopy(CLEAN)
        fn(data)
        return data

    def test_clean_and_latest_run_wins(self):
        res = self.run_gate(CLEAN)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("CLEAN", res.stdout)
        self.assertIn("label 'agent-reported' present", res.stdout)

    def test_latest_failed_run_is_not_clean(self):
        data = self.variant(lambda d: d["pr"]["statusCheckRollup"].append(check("test", "FAILURE", "2026-01-01T09:45:00Z")))
        res = self.run_gate(data)
        self.assertEqual(res.returncode, 1)
        self.assertIn("latest run of check 'test' is FAILURE", res.stdout)

    def test_pending_check_is_not_clean(self):
        data = self.variant(lambda d: d["pr"]["statusCheckRollup"].append(check("lint", None, "2026-01-01T09:00:00Z", "IN_PROGRESS")))
        self.assertEqual(self.run_gate(data).returncode, 1)

    def test_merged_pr_is_not_clean(self):
        data = self.variant(lambda d: d["pr"].update(state="MERGED", mergeStateStatus="UNKNOWN"))
        res = self.run_gate(data)
        self.assertEqual(res.returncode, 1)
        self.assertIn("PR state is MERGED", res.stdout)

    def test_stale_report_tip_is_not_clean(self):
        data = self.variant(lambda d: d["pr"].update(headRefOid="c" * 40))
        res = self.run_gate(data)
        self.assertEqual(res.returncode, 1)
        self.assertIn("new push invalidates", res.stdout)

    def test_missing_report_unresolved_threads_and_blocked(self):
        def fn(d):
            d["pr"]["comments"] = d["pr"]["comments"][2:]
            d["pr"]["mergeStateStatus"] = "BLOCKED"
            d["threads"].append({"isResolved": False})
        res = self.run_gate(self.variant(fn))
        self.assertEqual(res.returncode, 1)
        for text in ("no AGENT-REPORT comment", "1 unresolved review thread", "mergeStateStatus is BLOCKED"):
            self.assertIn(text, res.stdout)

    def test_missing_label_is_info_only(self):
        res = self.run_gate(self.variant(lambda d: d["pr"].update(labels=[])))
        self.assertEqual(res.returncode, 0, res.stdout)
        self.assertIn("label 'agent-reported' absent", res.stdout)

    def test_custom_label_name(self):
        res = self.run_gate(CLEAN, env={"AGENT_REPORT_LABEL": "verified"})
        self.assertIn("label 'verified' absent", res.stdout)

    def test_local_clone_without_head_is_info(self):
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(["git", "init", "-q", d], check=True)
            res = self.run_gate(CLEAN, d)
        self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
        self.assertIn("lacks the head commit", res.stdout)

    def test_usage_errors(self):
        for args in ([], ["example/repo"], ["bad repo", "7"], ["example/repo", "0"]):
            with self.subTest(args=args):
                res = subprocess.run(["bash", str(GATE), *args], capture_output=True, text=True)
                self.assertEqual(res.returncode, 2)

    def test_script_is_read_only(self):
        self.assertEqual(kitlib.mutating_lines(GATE.read_text(encoding="utf-8")), [])
        for bad in ("gh pr merge 1", "gh api repos/x/y/issues -X POST", "git push origin x",
                    "git -C repo fetch", "gh api graphql -f query='mutation { x }'", "gh pr comment 3 -b hi"):
            with self.subTest(bad=bad):
                self.assertTrue(kitlib.mutating_lines(bad))


class PinnedActionsTest(unittest.TestCase):
    pin = load_pinned()
    SHA = "3d3c42e5aac5ba805825da76410c181273ba90b1"

    def bad(self, text):
        return [ref for _, ref in self.pin.check_text(textwrap.dedent(text))]

    def test_fixture(self):
        wf = f"""
        jobs:
          a:
            uses: org/repo/.github/workflows/x.yml@main
            steps:
              - uses: actions/checkout@{self.SHA} # v7.0.1
              - uses: actions/setup-node@v4
              - "uses": 'org/action@{self.SHA[:7]}'
              - {{ name: flow, uses: "org/flow@v1", with: {{ uses: ignored }} }}
              - {{ "uses": org/flow2@{self.SHA} }}
              - name: local
                uses: ./.github/actions/local
              - uses: docker://alpine:3
              - uses: docker://alpine@sha256:{'0' * 64}
              - name: with keys
                uses: org/ok@{self.SHA}
                with:
                  uses: not-an-action
                env:
                  uses: also-ignored
        """
        self.assertEqual(self.bad(wf), ["org/repo/.github/workflows/x.yml@main", "actions/setup-node@v4",
                                        f"org/action@{self.SHA[:7]}", "org/flow@v1", "docker://alpine:3"])

    def test_kit_templates_are_pinned(self):
        for wf in sorted(CORE.rglob("*.yml*")):
            with self.subTest(wf=wf.name):
                self.assertEqual(self.pin.check_text(wf.read_text(encoding="utf-8")), [])

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as d:
            f = pathlib.Path(d) / "w.yml"
            f.write_text("steps:\n  - uses: a/b@v1\n", encoding="utf-8")
            script = CORE / "scripts" / "check-pinned-actions.py"
            self.assertEqual(subprocess.run([sys.executable, str(script), d], capture_output=True).returncode, 1)
            f.write_text(f"steps:\n  - uses: a/b@{self.SHA}\n", encoding="utf-8")
            self.assertEqual(subprocess.run([sys.executable, str(script), d], capture_output=True).returncode, 0)


class TicketKeyTest(unittest.TestCase):
    def run_rule(self, prefix, title):
        text = (CORE / "ci-templates" / "ticket-key.yml.tmpl").read_text(encoding="utf-8")
        code = textwrap.dedent(re.search(r"<<'PY'\n(.*?)\n\s*PY\n", text, re.S).group(1))
        return subprocess.run([sys.executable, "-c", code], capture_output=True, text=True,
                              env={**os.environ, "KEY_PREFIX": prefix, "PR_TITLE": title})

    def test_placeholder_keys_are_rejected(self):
        cases = [("ABC", "ABC-12: real work", 0), ("ABC", "ABC-0: placeholder", 1), ("ABC", "ABC-007: x", 1),
                 ("ABC", "ABC-1:missing space", 1), ("ABC", "XYZ-3: other", 1), ("ABC", "abc-3: lower", 1),
                 ("(ticket key prefix not set)", "ABC-1: x", 1)]
        for prefix, title, want in cases:
            with self.subTest(title=title):
                self.assertEqual(self.run_rule(prefix, title).returncode, want)


class RolePermissionsTest(unittest.TestCase):
    spec = importlib.util.spec_from_file_location("sync_agents", CORE / "scripts" / "sync-agents.py")
    sync = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sync)

    def shell(self, role):
        return [(r["resource"], r["effect"]) for r in self.sync.role_permissions(role) if r["action"] == "shell"]

    def test_no_role_has_broad_shell_allow_or_stray_ask(self):
        for role in self.sync.ROLES:
            with self.subTest(role=role):
                self.assertNotIn(("*", "allow"), self.shell(role))
                self.assertEqual(self.sync.shell_rule_problems(self.sync.role_permissions(role), role), [])
                if role != "inspector":
                    self.assertNotIn(("*", "ask"), self.shell(role))

    def test_inspector_reappends_denies_after_its_ask(self):
        rules = self.shell("inspector")
        ask = rules.index(("*", "ask"))
        self.assertEqual(rules[ask + 1:], [(d, "deny") for d in self.sync.DENY_SHELL])

    def test_reviewer_roles_are_read_only_by_rule(self):
        for role in ("reviewer", "planner"):
            rules = self.shell(role)
            with self.subTest(role=role):
                self.assertNotIn(("*", "allow"), rules)
                self.assertEqual(rules[-len(self.sync.REVIEWER_SHELL_RULES):], list(self.sync.REVIEWER_SHELL_RULES))
                for deny in ("git push *", "git commit *", "git restore *", "git branch *", "gh pr merge*",
                             "gh pr comment*", "gh api -X POST*", "gh api * --method DELETE*", "gh api *--input*",
                             "rm *", "sed -i*"):
                    self.assertIn((deny, "deny"), rules)
                allows = [r for r, e in rules if e == "allow"]
                self.assertTrue(all(r.startswith(("git branch", "git status", "git diff", "git log", "git show",
                                                  "gh issue view", "gh pr view", "gh pr diff")) for r in allows), allows)

    def test_docs_role_may_commit_but_not_rewrite(self):
        rules = self.shell("docs")
        self.assertNotIn(("git commit *", "deny"), rules)
        self.assertNotIn(("git push *", "deny"), rules)
        for deny in ("git reset *", "git rebase *", "git branch -D*", "gh pr merge*", "gh api *--input*", "rm *"):
            self.assertIn((deny, "deny"), rules)
        self.assertNotIn(("cp *", "deny"), rules)

    def test_drift_check_against_opencode_json(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            (root / "agents").mkdir()
            (root / "agents" / "x.md").write_text("---\nname: x\ndescription: d\nrole: reviewer\n---\nbody\n",
                                                  encoding="utf-8")
            script = CORE / "scripts" / "sync-agents.py"
            run = lambda: subprocess.run([sys.executable, str(script), "--root", d] + ["--check"],
                                         capture_output=True, text=True)
            subprocess.run([sys.executable, str(script), "--root", d], check=True, capture_output=True)
            self.assertEqual(run().returncode, 0)
            rules = [{"action": "shell", "resource": r, "effect": "deny"} for r in self.sync.DENY_SHELL]
            (root / "opencode.json").write_text(json.dumps({"permissions": rules}), encoding="utf-8")
            self.assertEqual(run().returncode, 0)
            (root / "opencode.json").write_text(json.dumps({"permissions": rules[:-1]}), encoding="utf-8")
            res = run()
            self.assertEqual(res.returncode, 1)
            self.assertIn("DENY_SHELL differs", res.stderr)

    def test_checker_catches_bad_rules(self):
        r = self.sync.rule
        self.assertTrue(self.sync.shell_rule_problems([r("shell", "*", "allow")], "implementer"))
        self.assertTrue(self.sync.shell_rule_problems([r("shell", "*", "ask")], "reviewer"))
        self.assertTrue(self.sync.shell_rule_problems([r("shell", "*", "ask")], "inspector"))
        self.assertTrue(self.sync.shell_rule_problems([], "inspector"))

    def test_autonomy_recipe_covers_the_exceptions(self):
        text = (CORE / "docs-templates" / "autonomy-policy.md.tmpl").read_text(encoding="utf-8")
        for needle in ('"shell", "resource": "*", "effect": "allow"', "external_directory", "ssh *", "sudo *",
                       "rm -rf *", "rm --recursive*", "git reset --hard*", "git clean *", "git branch -D *", "docker * prune*",
                       "docker volume *", "aws *", "terraform destroy*", "kubectl *", "helm *", "sam validate*",
                       "gh api */rulesets*", "gh api */branches/*/protection*", "gh api *--input*", "Residual gaps",
                       "gh secret *", "gh variable *", "gh repo edit *", "gh release create*", "gh workflow run *",
                       "*prod*", "bash -", "zsh -", "sh -", "*.env", "last match wins"):
            with self.subTest(needle=needle):
                self.assertIn(needle, text)
        for deny in self.sync.DENY_SHELL:
            self.assertIn(f'"resource": "{deny}", "effect": "deny"', text)


class InstallWiringTest(unittest.TestCase):
    def test_lean_installs_gates_as_opt_in_copies(self):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d) / "repo"
            root.mkdir()
            res = subprocess.run([sys.executable, str(kitlib.KIT / "scripts" / "apply-kit.py"), "--target", str(root),
                                  "--type", "docs-hub", "--profile", "lean", "--set", "PROJECT_NAME=Smoke",
                                  "--set", "ORG=example", "--set", "DOCS_REPO=smoke-docs"], capture_output=True, text=True)
            self.assertEqual(res.returncode, 0, res.stdout + res.stderr)
            for f in ("docs/agents/handover-rules.md", "docs/agents/autonomy-policy.md",
                      "docs/agents/templates/decision-log.md", "docs/agents/templates/retro-template.md",
                      "scripts/handover-check.sh", "scripts/check-pinned-actions.py",
                      "docs/ci-templates/agent-report.yml", "docs/ci-templates/pinned-actions.yml",
                      "docs/ci-templates/ticket-key.yml"):
                self.assertTrue((root / f).is_file(), f)
            self.assertFalse((root / ".github" / "workflows").exists())
            self.assertTrue(os.access(root / "scripts" / "handover-check.sh", os.X_OK))
            rendered = (root / "docs/ci-templates/agent-report.yml").read_text(encoding="utf-8")
            self.assertIn('LABEL: "agent-reported"', rendered)
            self.assertIn("${{ github.token }}", rendered)


if __name__ == "__main__":
    unittest.main()
