"""Slug derivation tests — Lock 1."""
import unittest

import conftest  # noqa: F401 — sys.path side-effect

from slug import account_slug, title_slug


class AccountSlugTest(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(account_slug("adithya@outerscope.xyz"), "adithya-outerscope")

    def test_eclipse_builders(self):
        self.assertEqual(account_slug("adithya@eclipse.builders"), "adithya-eclipse")

    def test_uppercase_and_dots(self):
        self.assertEqual(
            account_slug("ADITHYA.SHAK.KUMAR@gmail.com"),
            "adithya-shak-kumar-gmail",
        )

    def test_no_domain(self):
        # No @ - degrades to local-part only.
        self.assertEqual(account_slug("nobody"), "nobody")

    def test_empty(self):
        self.assertEqual(account_slug(""), "unknown")

    def test_strips_outer_dashes(self):
        self.assertEqual(account_slug("--weird--@example.com"), "weird-example")


class TitleSlugTest(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(title_slug("Sydney <> Adi"), "sydney-adi")

    def test_lowercase(self):
        self.assertEqual(title_slug("ECLIPSE Standup"), "eclipse-standup")

    def test_strip_re_fwd_prefixes(self):
        self.assertEqual(title_slug("Re: Fwd: Project Alpha"), "project-alpha")
        self.assertEqual(title_slug("RE: RE: hello"), "hello")

    def test_truncate_60(self):
        s = title_slug("a" * 100)
        self.assertEqual(len(s), 60)
        self.assertEqual(s, "a" * 60)

    def test_truncate_strips_trailing_dash(self):
        # Truncating mid-dash-run must not leave a trailing dash.
        s = title_slug("a" * 59 + "-bbbb")
        self.assertFalse(s.endswith("-"))

    def test_punctuation_runs_collapse(self):
        self.assertEqual(title_slug("Hello!!! ??? World"), "hello-world")

    def test_emoji_stripped(self):
        # Emojis aren't ASCII letters/digits → collapsed away.
        self.assertEqual(title_slug("Hello 🚀 World"), "hello-world")

    def test_non_latin_falls_back(self):
        # Japanese / RTL etc — NFKD doesn't yield ASCII letters → fallback.
        self.assertEqual(title_slug("プロジェクト会議"), "untitled-meeting")
        self.assertEqual(title_slug("שלום עולם"), "untitled-meeting")

    def test_empty(self):
        self.assertEqual(title_slug(""), "untitled-meeting")
        self.assertEqual(title_slug("   "), "untitled-meeting")
        self.assertEqual(title_slug("---"), "untitled-meeting")

    def test_unicode_accents_fold(self):
        # NFKD fold: café → cafe.
        self.assertEqual(title_slug("Café Meeting"), "cafe-meeting")


if __name__ == "__main__":
    unittest.main()
