#!/usr/bin/env python3
"""Describe a single image via the cloud-llm dispatcher.

Spawned per-image by ingest.mjs. Prints one JSON object on stdout:
  {"ok": true,  "engine": "...", "output": "..."}
  {"ok": false, "error": "..."}

Stdin / argv contract: pass the absolute image path as argv[1].
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

CLOUD_LLM_DIR = Path(__file__).resolve().parents[2] / "cloud-llm"
sys.path.insert(0, str(CLOUD_LLM_DIR))

PROMPT = "Describe this image in one short, factual sentence under 20 words. No preamble, no markdown, no quotes."


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"ok": False, "error": "usage: describe-image.py <abs-path>"}))
        return 2
    image_path = sys.argv[1]
    try:
        from client import describe_images, CloudLLMUnreachable  # noqa: WPS433
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": f"import failed: {type(e).__name__}: {e}"}))
        return 1
    try:
        result = describe_images([image_path], PROMPT)
        output = (result.get("output") or "").strip().strip('"').strip("'")
        if not output:
            print(json.dumps({"ok": False, "error": "empty output"}))
            return 1
        print(json.dumps({"ok": True, "engine": result.get("engine"), "output": output}))
        return 0
    except CloudLLMUnreachable as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 1
    except Exception as e:  # noqa: BLE001
        print(json.dumps({"ok": False, "error": f"{type(e).__name__}: {e}"}))
        return 1


if __name__ == "__main__":
    sys.exit(main())
