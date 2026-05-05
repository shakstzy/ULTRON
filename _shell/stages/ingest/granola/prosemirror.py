"""ProseMirror JSON → Markdown walker. Lock 4a of format.md.

Granola's last_viewed_panel.content is a ProseMirror doc. We render the
subset of node and mark types observed in real Granola exports.

Pure function, no I/O. Returns the rendered markdown string with
trailing whitespace stripped.
"""
from __future__ import annotations

from typing import Any

# Order matters: innermost-first wrapping for marks.
_MARK_ORDER = ("code", "strike", "italic", "em", "bold", "strong", "underline", "link")


def render_prosemirror(node: Any) -> str:
    """Render a ProseMirror node (or any subtree) to markdown.

    Accepts None, strings (returns empty — Granola sometimes serves
    `last_viewed_panel` as a panel-id string instead of a dict), dicts,
    or lists. Unknown node types fall through and walk their children.
    """
    if not isinstance(node, dict):
        return ""
    out: list[str] = []
    _render(node, out, depth=0)
    text = "".join(out)
    # Strip per-line trailing whitespace; collapse 3+ blank lines to 2.
    lines = [line.rstrip() for line in text.split("\n")]
    text = "\n".join(lines)
    while "\n\n\n" in text:
        text = text.replace("\n\n\n", "\n\n")
    return text.strip()


def _render(node: Any, out: list[str], depth: int) -> None:
    if not isinstance(node, dict):
        return
    t = node.get("type")
    if t == "text":
        out.append(_render_text(node))
        return
    if t in ("doc", None):
        for c in node.get("content") or []:
            _render(c, out, depth)
        return
    if t == "paragraph":
        for c in node.get("content") or []:
            _render(c, out, depth)
        out.append("\n\n")
        return
    if t == "heading":
        level = (node.get("attrs") or {}).get("level") or 1
        level = max(1, min(6, int(level)))
        out.append("#" * level + " ")
        for c in node.get("content") or []:
            _render(c, out, depth)
        out.append("\n\n")
        return
    if t == "bulletList":
        _render_list(node, out, depth, ordered=False)
        return
    if t == "orderedList":
        _render_list(node, out, depth, ordered=True)
        return
    if t == "listItem":
        # Items are emitted by _render_list to control numbering / depth.
        for c in node.get("content") or []:
            _render(c, out, depth)
        return
    if t == "blockquote":
        # Render children to a sub-buffer, prefix every line with `> `.
        sub: list[str] = []
        for c in node.get("content") or []:
            _render(c, sub, depth)
        block = "".join(sub).rstrip()
        out.append("\n".join("> " + ln for ln in block.split("\n")) + "\n\n")
        return
    if t == "codeBlock":
        lang = (node.get("attrs") or {}).get("language") or ""
        text = "".join(c.get("text", "") for c in (node.get("content") or [])
                       if isinstance(c, dict))
        out.append(f"```{lang}\n{text}\n```\n\n")
        return
    if t == "horizontalRule":
        out.append("\n---\n\n")
        return
    if t == "hardBreak":
        out.append("  \n")
        return
    # Unknown node type → walk children, drop the wrapper.
    for c in node.get("content") or []:
        _render(c, out, depth)


def _render_list(node: dict, out: list[str], depth: int, ordered: bool) -> None:
    indent = "  " * depth
    items = [c for c in (node.get("content") or [])
             if isinstance(c, dict) and c.get("type") == "listItem"]
    for i, item in enumerate(items, start=1):
        bullet = f"{i}. " if ordered else "- "
        # Render item children to a sub-buffer, then split into lines so we
        # can prefix the first line with the bullet and indent continuations.
        sub: list[str] = []
        for c in item.get("content") or []:
            if isinstance(c, dict) and c.get("type") in ("bulletList", "orderedList"):
                _render(c, sub, depth + 1)
            else:
                _render(c, sub, depth + 1)
        block = "".join(sub).rstrip("\n")
        if not block:
            out.append(f"{indent}{bullet}\n")
            continue
        lines = block.split("\n")
        out.append(f"{indent}{bullet}{lines[0].lstrip()}\n")
        for ln in lines[1:]:
            out.append(f"{indent}  {ln.lstrip() if not ln.startswith(' ') else ln}\n")
    out.append("\n")


def _render_text(node: dict) -> str:
    text = node.get("text") or ""
    marks = node.get("marks") or []
    mark_types = {m.get("type"): m for m in marks if isinstance(m, dict)}
    # Apply in defined order so the wrapping nests deterministically.
    for mt in _MARK_ORDER:
        if mt not in mark_types:
            continue
        if mt == "code":
            text = f"`{text}`"
        elif mt in ("italic", "em"):
            text = f"_{text}_"
        elif mt in ("bold", "strong"):
            text = f"**{text}**"
        elif mt == "strike":
            text = f"~~{text}~~"
        elif mt == "underline":
            text = f"<u>{text}</u>"
        elif mt == "link":
            href = (mark_types[mt].get("attrs") or {}).get("href") or ""
            text = f"[{text}]({href})"
    return text
