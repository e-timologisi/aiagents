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


if __name__ == "__main__":
    unittest.main()
