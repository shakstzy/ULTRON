"""Routing tests — route.py."""
import unittest

import conftest  # noqa: F401

from route import route


class RouteTest(unittest.TestCase):
    def test_no_folder_titles_returns_empty(self):
        doc = {"id": "abc", "folder_titles": []}
        cfg = {"eclipse": {"sources": {"granola": {"folders": ["ECLIPSE"]}}}}
        self.assertEqual(route(doc, cfg), [])

    def test_no_subscribers_returns_empty(self):
        doc = {"id": "abc", "folder_titles": ["ECLIPSE"]}
        cfg = {"eclipse": {"sources": {"gmail": {}}}}
        self.assertEqual(route(doc, cfg), [])

    def test_exact_match_routes(self):
        doc = {"id": "abc", "folder_titles": ["ECLIPSE"]}
        cfg = {"eclipse": {"sources": {"granola": {"folders": ["ECLIPSE"]}}}}
        self.assertEqual(
            route(doc, cfg),
            [{"workspace": "eclipse", "rule": "folder:ECLIPSE"}],
        )

    def test_case_sensitive(self):
        doc = {"id": "abc", "folder_titles": ["eclipse"]}
        cfg = {"eclipse": {"sources": {"granola": {"folders": ["ECLIPSE"]}}}}
        self.assertEqual(route(doc, cfg), [])

    def test_multi_folder_doc_forks_to_two_workspaces(self):
        doc = {"id": "abc", "folder_titles": ["ECLIPSE", "PERSONAL"]}
        cfg = {
            "eclipse": {"sources": {"granola": {"folders": ["ECLIPSE"]}}},
            "personal": {"sources": {"granola": {"folders": ["PERSONAL"]}}},
        }
        result = route(doc, cfg)
        self.assertEqual(
            result,
            [
                {"workspace": "eclipse", "rule": "folder:ECLIPSE"},
                {"workspace": "personal", "rule": "folder:PERSONAL"},
            ],
        )

    def test_multiple_folders_one_workspace_picks_first_match(self):
        doc = {"id": "abc", "folder_titles": ["B", "A"]}
        cfg = {"ws": {"sources": {"granola": {"folders": ["A", "B"]}}}}
        # First entry in workspace's own folder list that matches wins.
        self.assertEqual(
            route(doc, cfg),
            [{"workspace": "ws", "rule": "folder:A"}],
        )

    def test_workspace_with_no_granola_block_ignored(self):
        doc = {"id": "abc", "folder_titles": ["ECLIPSE"]}
        cfg = {"eclipse": {}}
        self.assertEqual(route(doc, cfg), [])

    def test_results_sorted_by_workspace_slug(self):
        doc = {"id": "abc", "folder_titles": ["X"]}
        cfg = {
            "zeta": {"sources": {"granola": {"folders": ["X"]}}},
            "alpha": {"sources": {"granola": {"folders": ["X"]}}},
        }
        result = route(doc, cfg)
        self.assertEqual([r["workspace"] for r in result], ["alpha", "zeta"])


if __name__ == "__main__":
    unittest.main()
