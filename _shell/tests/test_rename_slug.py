"""
test_rename_slug.py — edge-case tests for rename-slug.py's text rewriter.

Run:
    python3 -m pytest _shell/tests/test_rename_slug.py
    OR
    python3 _shell/tests/test_rename_slug.py
"""
from __future__ import annotations

import sys
from pathlib import Path

ULTRON_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ULTRON_ROOT / "_shell" / "bin"))

# Use importlib to load the script (it's a CLI, not a module on PYTHONPATH).
import importlib.util  # noqa: E402

_spec = importlib.util.spec_from_file_location(
    "rename_slug", ULTRON_ROOT / "_shell" / "bin" / "rename-slug.py"
)
rs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(rs)


def _check(input_text: str, expected: str, old: str = "jake-paul", new: str = "jake-paul-eclipse") -> None:
    out = rs.patch_text(input_text, old, new)
    assert out == expected, f"mismatch:\n  in:  {input_text!r}\n  out: {out!r}\n  exp: {expected!r}"


def test_plain_wikilink():
    _check("see [[jake-paul]] for context.\n", "see [[jake-paul-eclipse]] for context.\n")


def test_with_display_label():
    _check("[[jake-paul|Jake]] is the lead.\n", "[[jake-paul-eclipse|Jake]] is the lead.\n")


def test_global_prefix():
    _check("[[@jake-paul]]\n", "[[@jake-paul-eclipse]]\n")


def test_ws_prefix_short():
    _check("[[ws:eclipse/jake-paul]]\n", "[[ws:eclipse/jake-paul-eclipse]]\n")


def test_ws_prefix_full_path():
    _check(
        "[[ws:eclipse/entities/people/jake-paul]]\n",
        "[[ws:eclipse/entities/people/jake-paul-eclipse]]\n",
    )


def test_embed():
    _check("![[jake-paul]]\n", "![[jake-paul-eclipse]]\n")


def test_embed_with_label():
    _check("![[jake-paul|Jake]]\n", "![[jake-paul-eclipse|Jake]]\n")


def test_in_inline_code_NOT_rewritten():
    _check("inline `[[jake-paul]]` survives\n", "inline `[[jake-paul]]` survives\n")


def test_in_fenced_code_NOT_rewritten():
    src = "```\n[[jake-paul]]\n```\n[[jake-paul]] outside\n"
    expected = "```\n[[jake-paul]]\n```\n[[jake-paul-eclipse]] outside\n"
    _check(src, expected)


def test_in_tilde_fence_NOT_rewritten():
    src = "~~~md\n[[jake-paul]]\n~~~\n[[jake-paul]] outside\n"
    expected = "~~~md\n[[jake-paul]]\n~~~\n[[jake-paul-eclipse]] outside\n"
    _check(src, expected)


def test_yaml_list_in_frontmatter_IS_rewritten():
    src = "---\nrelated:\n  - [[jake-paul]]\n---\n"
    expected = "---\nrelated:\n  - [[jake-paul-eclipse]]\n---\n"
    _check(src, expected)


def test_multiple_on_same_line_only_match():
    src = "[[a]] [[jake-paul]] [[c]]\n"
    expected = "[[a]] [[jake-paul-eclipse]] [[c]]\n"
    _check(src, expected)


def test_idempotent():
    src = "[[jake-paul-eclipse]]\n"
    out = rs.patch_text(src, "jake-paul", "jake-paul-eclipse")
    assert out == src


def test_concept_synthesis_raw_NOT_touched():
    src = (
        "[[concept:jake-paul]]\n"
        "[[synthesis:jake-paul]]\n"
        "[[raw:jake-paul.md]]\n"
    )
    out = rs.patch_text(src, "jake-paul", "jake-paul-eclipse")
    assert out == src, f"concept:/synthesis:/raw: prefixes should not be rewritten by slug rename"


# ---- runner -------------------------------------------------------------

def main() -> int:
    tests = [
        v for k, v in globals().items()
        if k.startswith("test_") and callable(v)
    ]
    failures = 0
    for t in tests:
        try:
            t()
            print(f"PASS  {t.__name__}")
        except AssertionError as e:
            failures += 1
            print(f"FAIL  {t.__name__}: {e}")
    print(f"\n{len(tests) - failures}/{len(tests)} passed")
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
