"""Tests for the forbidden-string scanner (python3 -m unittest discover -s scripts -p "test_*.py")."""
import pathlib
import sys
import tempfile
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import kitlib  # noqa: E402


class ScanForbiddenTest(unittest.TestCase):
    def scan(self, files, local=None):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            for name, text in files.items():
                (root / name).write_text(text, encoding="utf-8")
            if local is not None:
                (root / kitlib.LOCAL_FORBIDDEN_FILE).write_text(local, encoding="utf-8")
            return kitlib.scan_forbidden(root)

    def test_builtin_patterns(self):
        cases = {
            "aws account id": "account " + "1234" + "56789012",
            "aws arn": "arn" + ":aws:iam::x",
            "ip address": "host 10." + "1.2.3",
            "github token": "token gh" + "p_abc",
            "google oauth secret": "GOC" + "SPX-abc",
            "private key": "-----BEGIN RSA PRIVATE" + " KEY-----",
            "password literal": "Pass" + "word: x",
        }
        for label, text in cases.items():
            with self.subTest(label=label):
                hits = self.scan({"a.md": text})
                self.assertTrue(any(label in h for h in hits), hits)

    def test_clean_text_and_long_hex_pass(self):
        self.assertEqual(self.scan({"a.md": "uses: x@3d3c42e5aac5ba805825da76410c181273ba90b1\nplain text\n"}), [])

    def test_local_patterns_apply_and_file_itself_is_skipped(self):
        local = "# comment\nexample-corp\\.com\n"
        hits = self.scan({"a.md": "see example-corp.com"}, local=local)
        self.assertEqual(len(hits), 1)
        self.assertIn("local pattern", hits[0])
        self.assertEqual(self.scan({"a.md": "clean"}, local=local), [])

    def test_invalid_local_regex_raises(self):
        with self.assertRaises(ValueError):
            self.scan({"a.md": "x"}, local="(unclosed\n")


class CheckAttributionTest(unittest.TestCase):
    LICENSES = "".join(f"{m}\n{kitlib.MIT_PERMISSION}\n" for m in kitlib.UPSTREAM_LICENSE_MARKERS)

    def check(self, files):
        with tempfile.TemporaryDirectory() as d:
            root = pathlib.Path(d)
            for name, text in files.items():
                (root / name).parent.mkdir(parents=True, exist_ok=True)
                (root / name).write_text(text, encoding="utf-8")
            return kitlib.check_attribution(root)

    def test_complete_attribution_passes(self):
        self.assertEqual(self.check({
            "THIRD-PARTY-NOTICES.md": self.LICENSES + "- `core/skills/x/`\n",
            "core/skills/x/UPSTREAM.md": "src",
            "core/skills/x/LICENSE.upstream": kitlib.MIT_PERMISSION,
        }), [])

    def test_missing_license_upstream(self):
        errs = self.check({"THIRD-PARTY-NOTICES.md": self.LICENSES + "`core/skills/x/`",
                           "core/skills/x/UPSTREAM.md": "src"})
        self.assertTrue(any("without LICENSE.upstream" in e for e in errs), errs)

    def test_unlisted_upstream_dir(self):
        errs = self.check({"THIRD-PARTY-NOTICES.md": self.LICENSES,
                           "core/skills/x/UPSTREAM.md": "src",
                           "core/skills/x/LICENSE.upstream": kitlib.MIT_PERMISSION})
        self.assertTrue(any("not listed" in e for e in errs), errs)

    def test_notices_must_contain_both_licenses(self):
        errs = self.check({"THIRD-PARTY-NOTICES.md": kitlib.UPSTREAM_LICENSE_MARKERS[0] + kitlib.MIT_PERMISSION})
        self.assertTrue(any(kitlib.UPSTREAM_LICENSE_MARKERS[1] in e for e in errs), errs)
        self.assertTrue(any("in full" in e for e in errs), errs)

    def test_missing_notices_file(self):
        self.assertIn("missing THIRD-PARTY-NOTICES.md", self.check({}))

    def test_real_kit_notices_pass_forbidden_scan(self):
        files = [kitlib.KIT / kitlib.NOTICES_FILE] + sorted((kitlib.KIT / "core").rglob("*.upstream"))
        hits = kitlib.scan_forbidden(kitlib.KIT)
        self.assertEqual([h for h in hits if any(h.startswith(str(f.relative_to(kitlib.KIT))) for f in files)], [])


if __name__ == "__main__":
    unittest.main()
