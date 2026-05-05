"""ProseMirror walker tests — Lock 4a."""
import json
import unittest

import conftest  # noqa: F401
from conftest import FIXTURES

from prosemirror import render_prosemirror


class ProseMirrorTest(unittest.TestCase):
    def test_empty_doc(self):
        self.assertEqual(render_prosemirror({"type": "doc", "content": []}).strip(), "")

    def test_none_input(self):
        self.assertEqual(render_prosemirror(None), "")

    def test_string_input_returns_empty(self):
        # Live-probe finding: doc.last_viewed_panel is sometimes a string id, not a dict.
        self.assertEqual(render_prosemirror("some-panel-id"), "")

    def test_text_node(self):
        n = {"type": "doc", "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": "hello"}]}
        ]}
        self.assertEqual(render_prosemirror(n).strip(), "hello")

    def test_bold(self):
        n = {"type": "doc", "content": [
            {"type": "paragraph", "content": [
                {"type": "text", "text": "hi", "marks": [{"type": "bold"}]}
            ]}
        ]}
        self.assertIn("**hi**", render_prosemirror(n))

    def test_italic(self):
        n = {"type": "doc", "content": [
            {"type": "paragraph", "content": [
                {"type": "text", "text": "hi", "marks": [{"type": "italic"}]}
            ]}
        ]}
        self.assertIn("_hi_", render_prosemirror(n))

    def test_code_mark(self):
        n = {"type": "doc", "content": [
            {"type": "paragraph", "content": [
                {"type": "text", "text": "x", "marks": [{"type": "code"}]}
            ]}
        ]}
        self.assertIn("`x`", render_prosemirror(n))

    def test_link_mark(self):
        n = {"type": "doc", "content": [
            {"type": "paragraph", "content": [
                {"type": "text", "text": "click",
                 "marks": [{"type": "link", "attrs": {"href": "https://x.test"}}]}
            ]}
        ]}
        self.assertIn("[click](https://x.test)", render_prosemirror(n))

    def test_heading_levels(self):
        for level in (1, 2, 3, 4, 5, 6):
            n = {"type": "doc", "content": [
                {"type": "heading", "attrs": {"level": level},
                 "content": [{"type": "text", "text": "title"}]}
            ]}
            md = render_prosemirror(n)
            self.assertIn("#" * level + " title", md)

    def test_heading_default_level_1(self):
        n = {"type": "doc", "content": [
            {"type": "heading", "content": [{"type": "text", "text": "title"}]}
        ]}
        self.assertIn("# title", render_prosemirror(n))

    def test_bullet_list(self):
        n = {"type": "doc", "content": [
            {"type": "bulletList", "content": [
                {"type": "listItem", "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": "a"}]}
                ]},
                {"type": "listItem", "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": "b"}]}
                ]},
            ]}
        ]}
        md = render_prosemirror(n)
        self.assertIn("- a", md)
        self.assertIn("- b", md)

    def test_ordered_list(self):
        n = {"type": "doc", "content": [
            {"type": "orderedList", "content": [
                {"type": "listItem", "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": "x"}]}
                ]},
                {"type": "listItem", "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": "y"}]}
                ]},
            ]}
        ]}
        md = render_prosemirror(n)
        self.assertIn("1. x", md)
        self.assertIn("2. y", md)

    def test_nested_bullet_list(self):
        n = {"type": "doc", "content": [
            {"type": "bulletList", "content": [
                {"type": "listItem", "content": [
                    {"type": "paragraph", "content": [{"type": "text", "text": "outer"}]},
                    {"type": "bulletList", "content": [
                        {"type": "listItem", "content": [
                            {"type": "paragraph", "content": [{"type": "text", "text": "inner"}]}
                        ]}
                    ]}
                ]}
            ]}
        ]}
        md = render_prosemirror(n)
        self.assertIn("- outer", md)
        self.assertIn("  - inner", md)

    def test_unknown_node_walks_children(self):
        n = {"type": "doc", "content": [
            {"type": "weirdWrapper", "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": "kept"}]}
            ]}
        ]}
        self.assertIn("kept", render_prosemirror(n))

    def test_real_fixture_has_real_content(self):
        # Use the captured live doc-with-notes fixture as a smoke test.
        d = json.loads((FIXTURES / "doc-with-notes.json").read_text())
        content = d["last_viewed_panel"]["content"]
        md = render_prosemirror(content)
        self.assertGreater(len(md), 200)
        self.assertIn("###", md)  # had headings

    def test_render_strips_trailing_whitespace(self):
        n = {"type": "doc", "content": [
            {"type": "paragraph", "content": [{"type": "text", "text": "hi"}]}
        ]}
        md = render_prosemirror(n)
        self.assertFalse(md.endswith("\n\n\n"))


if __name__ == "__main__":
    unittest.main()
