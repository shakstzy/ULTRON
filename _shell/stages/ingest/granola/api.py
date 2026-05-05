"""Granola HTTP API client. Lock 8 of format.md.

Pure stdlib. Handles gzip, 401-retry-with-refresh, 429/5xx exponential
backoff. One client instance per robot run.
"""
from __future__ import annotations

import gzip
import json
import time
import urllib.error
import urllib.request
from typing import Any

from auth import get_access_token, refresh_token, SUPABASE_PATH

API_BASE = "https://api.granola.ai"
DEFAULT_CLIENT_VERSION = "7.195.0"
BATCH_SIZE = 20

# Retry policy
MAX_RETRIES = 5
BACKOFF_BASE = 2.0
BACKOFF_CAP = 60.0


class GranolaAPIError(Exception):
    pass


class GranolaClient:
    def __init__(self, client_version: str = DEFAULT_CLIENT_VERSION,
                 supabase_path=SUPABASE_PATH):
        self.client_version = client_version
        self.supabase_path = supabase_path
        self._token: str | None = None

    def _ensure_token(self) -> str:
        if self._token is None:
            self._token = get_access_token(self.supabase_path)
        return self._token

    def _do_request(self, path: str, body: dict | None) -> tuple[int, bytes, dict]:
        token = self._ensure_token()
        req = urllib.request.Request(
            f"{API_BASE}{path}",
            data=json.dumps(body or {}).encode(),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
                "X-Client-Version": self.client_version,
                "Accept-Encoding": "identity",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                data = r.read()
                if data[:2] == b"\x1f\x8b" or r.headers.get("Content-Encoding") == "gzip":
                    data = gzip.decompress(data)
                return r.status, data, dict(r.headers)
        except urllib.error.HTTPError as e:
            data = e.read()
            try:
                if data[:2] == b"\x1f\x8b":
                    data = gzip.decompress(data)
            except Exception:
                pass
            return e.code, data, dict(e.headers or {})

    def post(self, path: str, body: dict | None = None) -> Any:
        """POST to api.granola.ai{path}. Returns parsed JSON.

        On 401: refresh under flock, retry once. Second 401 → raise.
        On 429 / 5xx: exponential backoff up to MAX_RETRIES.
        Other 4xx: raise immediately.
        """
        attempt = 0
        refreshed = False
        while True:
            attempt += 1
            status, data, _ = self._do_request(path, body)

            if 200 <= status < 300:
                try:
                    return json.loads(data.decode("utf-8") or "null")
                except UnicodeDecodeError:
                    return json.loads(data.decode("utf-8", errors="replace") or "null")

            text_preview = data.decode("utf-8", errors="replace")[:300]

            if status == 401 and not refreshed:
                # Lock 7: re-read + refresh under flock; retry once.
                stale = self._token
                self._token = refresh_token(stale, self.supabase_path)
                refreshed = True
                continue

            if status in (429,) or 500 <= status < 600:
                if attempt >= MAX_RETRIES:
                    raise GranolaAPIError(
                        f"{path} exhausted retries; last status={status} body={text_preview!r}"
                    )
                delay = min(BACKOFF_CAP, BACKOFF_BASE * (2 ** (attempt - 1)))
                time.sleep(delay)
                continue

            # Hard error.
            raise GranolaAPIError(
                f"{path} status={status} body={text_preview!r}"
            )

    # ---- High-level endpoints --------------------------------------------

    def list_folders(self) -> dict[str, dict]:
        """Return {folder_id: folder_dict}. Each folder includes
        document_ids when present."""
        resp = self.post(
            "/v1/get-document-lists-metadata",
            {"include_document_ids": True, "include_only_joined_lists": False},
        )
        if not isinstance(resp, dict):
            raise GranolaAPIError(f"unexpected list-folders response: {type(resp)}")
        lists = resp.get("lists")
        if isinstance(lists, dict):
            return lists
        if isinstance(lists, list):
            # Defensive: older shape returns array.
            return {l.get("id") or str(i): l for i, l in enumerate(lists)}
        return {}

    def get_documents_batch(self, document_ids: list[str]) -> list[dict]:
        """Fetch docs in chunks of BATCH_SIZE; return concatenated docs."""
        out: list[dict] = []
        unique = list(dict.fromkeys(document_ids))  # preserve order, dedupe
        for i in range(0, len(unique), BATCH_SIZE):
            chunk = unique[i:i + BATCH_SIZE]
            resp = self.post("/v1/get-documents-batch", {"document_ids": chunk})
            if isinstance(resp, dict):
                out.extend(resp.get("docs") or [])
        return out

    def get_transcript(self, document_id: str) -> list[dict]:
        """Return transcript segments. 404 → empty list (the doc was
        never transcribed or the transcript was deleted). Anything else
        propagates so the orchestrator can freeze the cursor."""
        try:
            resp = self.post("/v1/get-document-transcript", {"document_id": document_id})
        except GranolaAPIError as e:
            if "status=404" in str(e):
                return []
            raise
        if isinstance(resp, list):
            return resp
        return []
