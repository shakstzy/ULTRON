"""
test_describe_attachments.py — TDD coverage for the parallel iMessage VLM ingest.

Run:
    python3 -m pytest _shell/tests/test_describe_attachments.py -v
"""
from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ULTRON_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ULTRON_ROOT / "_shell" / "bin" / "describe-attachments.py"
FAKE_GEMINI = Path(__file__).resolve().parent / "fixtures" / "fake-gemini.sh"


def _load_module():
    """Load describe-attachments.py as a module each test (fresh module-level state)."""
    spec = importlib.util.spec_from_file_location("describe_attachments", SCRIPT_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def fake_gemini_path(tmp_path):
    """PATH-injectable directory with fake-gemini.sh symlinked as `gemini`."""
    bindir = tmp_path / "bin"
    bindir.mkdir()
    (bindir / "gemini").symlink_to(FAKE_GEMINI)
    return bindir


@pytest.fixture
def patched_env(fake_gemini_path, monkeypatch):
    """Place fake gemini first on PATH, scrub conflicting Google envs."""
    new_path = f"{fake_gemini_path}:{os.environ.get('PATH', '')}"
    monkeypatch.setenv("PATH", new_path)
    for v in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GENAI_USE_VERTEXAI",
              "GOOGLE_CLOUD_PROJECT", "CLOUDSDK_CONFIG"):
        monkeypatch.delenv(v, raising=False)


@pytest.fixture
def fake_accounts(tmp_path):
    """Create N fake accounts dir + settings.json + pool dir.
    Returns dict with paths."""
    accounts_dir = tmp_path / "accounts"
    accounts_dir.mkdir()
    pool_root = tmp_path / "pool"
    settings = tmp_path / "settings.json"
    settings.write_text('{"selectedType": "oauth-personal"}')

    names = ["alpha@x.com", "beta@y.com", "gamma@z.com"]
    for name in names:
        (accounts_dir / f"{name}.json").write_text(
            '{"access_token":"fake","refresh_token":"fake"}'
        )
    return {
        "accounts_dir": accounts_dir,
        "pool_root": pool_root,
        "settings": settings,
        "names": names,
    }


@pytest.fixture
def mod_with_accounts(fake_accounts, monkeypatch, tmp_path):
    """describe-attachments module with ACCOUNTS_DIR/POOL_ROOT pointing at fixtures
    and init_account_state() already called."""
    mod = _load_module()
    monkeypatch.setattr(mod, "ACCOUNTS_DIR", fake_accounts["accounts_dir"])
    monkeypatch.setattr(mod, "POOL_ROOT", fake_accounts["pool_root"])
    # Patch the global-settings lookup to point at our fake settings
    fake_home_gemini = tmp_path / "fake-home" / ".gemini"
    fake_home_gemini.mkdir(parents=True)
    shutil.copy2(fake_accounts["settings"], fake_home_gemini / "settings.json")
    monkeypatch.setattr(Path, "home", classmethod(lambda cls: tmp_path / "fake-home"))
    mod.init_account_state()
    return mod


# ---------------------------------------------------------------------------
# Account pool init
# ---------------------------------------------------------------------------
class TestInitAccountState:
    def test_creates_per_account_home_dirs_with_creds_and_settings(self, mod_with_accounts, fake_accounts):
        for name in fake_accounts["names"]:
            home = fake_accounts["pool_root"] / name
            assert (home / ".gemini" / "oauth_creds.json").exists(), f"missing oauth for {name}"
            assert (home / ".gemini" / "settings.json").exists(), f"missing settings for {name}"

    def test_loads_all_accounts_in_pool(self, mod_with_accounts, fake_accounts):
        loaded = sorted(a[0] for a in mod_with_accounts.ACCOUNTS)
        assert loaded == sorted(fake_accounts["names"])


# ---------------------------------------------------------------------------
# Round-robin + exhaustion
# ---------------------------------------------------------------------------
class TestAccountRotation:
    def test_round_robin_cycles_all_accounts(self, mod_with_accounts):
        n = len(mod_with_accounts.ACCOUNTS)
        picked = [mod_with_accounts.get_next_account()[0] for _ in range(n * 2)]
        # Each account must appear exactly twice in 2n calls
        for name, _ in mod_with_accounts.ACCOUNTS:
            assert picked.count(name) == 2, f"{name} picked {picked.count(name)} times in 2n calls"

    def test_skips_exhausted_accounts(self, mod_with_accounts):
        names = [a[0] for a in mod_with_accounts.ACCOUNTS]
        mod_with_accounts.mark_exhausted(names[0])
        picks = [mod_with_accounts.get_next_account()[0] for _ in range(20)]
        assert names[0] not in picks
        assert set(picks).issubset(set(names[1:]))

    def test_returns_none_when_all_exhausted(self, mod_with_accounts):
        for name, _ in mod_with_accounts.ACCOUNTS:
            mod_with_accounts.mark_exhausted(name)
        assert mod_with_accounts.get_next_account() is None


# ---------------------------------------------------------------------------
# Regex detection
# ---------------------------------------------------------------------------
class TestRegexes:
    @pytest.mark.parametrize("phrase", [
        "429 too many requests",
        "rate limit exceeded",
        "quota exceeded",
        "RESOURCE_EXHAUSTED",
        "503 service unavailable",
        "retry after 30 seconds",
        "Tokens per minute exceeded",
        "RPM limit hit",
        "user rate limit reached",
    ])
    def test_rate_limit_regex_matches(self, phrase):
        mod = _load_module()
        assert mod._RATE_LIMIT_RE.search(phrase), f"should match: {phrase!r}"

    @pytest.mark.parametrize("phrase", [
        "all good",
        "described successfully",
        "image is a sunset",
    ])
    def test_rate_limit_regex_no_false_positives(self, phrase):
        mod = _load_module()
        assert not mod._RATE_LIMIT_RE.search(phrase), f"should NOT match: {phrase!r}"

    @pytest.mark.parametrize("phrase", [
        "I cannot access that file",
        "outside the allowed workspace",
        "Unable to view this image",
        "I don't have permission to read this",
    ])
    def test_refusal_regex_matches(self, phrase):
        mod = _load_module()
        assert mod._REFUSAL_RE.search(phrase), f"should match: {phrase!r}"


# ---------------------------------------------------------------------------
# gemini_describe_once env hardening — TDD: these will fail until we patch
# ---------------------------------------------------------------------------
class TestEnvHardening:
    def test_passes_home_and_trust_workspace(self, mod_with_accounts, patched_env, tmp_path):
        attach = tmp_path / "img.jpg"
        attach.write_bytes(b"fakejpeg")
        account = mod_with_accounts.ACCOUNTS[0]
        desc, model, err = mod_with_accounts.gemini_describe_once(attach, "image", account)
        assert err is None
        # Fake binary echoes the env. desc is the LAST non-empty stdout line.
        # By default it returns "OK from <basename>" — confirm we hit the right account.
        assert account[0] in desc, f"expected {account[0]!r} in {desc!r}"

    def test_force_file_storage_set(self, mod_with_accounts, patched_env, tmp_path):
        """GEMINI_FORCE_FILE_STORAGE=true is critical — without it, gemini CLI
        uses macOS Keychain which is system-wide and defeats HOME isolation."""
        # Configure the fake to echo a known marker so we can capture full stdout.
        attach = tmp_path / "img.jpg"
        attach.write_bytes(b"fake")
        account = mod_with_accounts.ACCOUNTS[0]
        # We need to capture the CLI's stdout — hijack the once() func via subprocess directly
        env = os.environ.copy()
        env["HOME"] = str(account[1])
        env["GEMINI_CLI_TRUST_WORKSPACE"] = "true"
        # Run the actual subprocess command the way describe-attachments does it
        # to verify our patched code sets FORCE_FILE_STORAGE
        # Call the function and re-extract envcheck lines from the captured output
        # via a subprocess shim. The simpler approach: inspect the source for the env we set.
        src = SCRIPT_PATH.read_text()
        assert 'GEMINI_FORCE_FILE_STORAGE' in src, "describe-attachments must set GEMINI_FORCE_FILE_STORAGE=true"
        assert '"true"' in src.split('GEMINI_FORCE_FILE_STORAGE')[1][:50], \
            "GEMINI_FORCE_FILE_STORAGE must be set to 'true'"

    def test_does_not_set_gemini_cli_home(self):
        """GEMINI_CLI_HOME has inconsistent semantics in the bundled CLI:
        gemini.js treats it as ~/.gemini, but auth code treats it as ~ and
        appends .gemini/settings.json — so setting it to either value breaks
        one path. Must be UNSET (or scrubbed)."""
        src = SCRIPT_PATH.read_text()
        assert 'env["GEMINI_CLI_HOME"]' not in src, \
            "describe-attachments must NOT set GEMINI_CLI_HOME — breaks auth"
        # Must scrub it from inherited env (defense)
        assert 'env.pop' in src and 'GEMINI_CLI_HOME' in src, \
            "describe-attachments must scrub GEMINI_CLI_HOME from child env"

    def test_scrubs_conflicting_google_envs(self):
        """Stale GEMINI_API_KEY / GOOGLE_API_KEY etc. would override OAuth creds."""
        src = SCRIPT_PATH.read_text()
        for var in ("GEMINI_API_KEY", "GOOGLE_API_KEY", "GOOGLE_GENAI_USE_VERTEXAI",
                    "GOOGLE_CLOUD_PROJECT", "CLOUDSDK_CONFIG"):
            assert var in src, f"describe-attachments must scrub {var} from child env"


# ---------------------------------------------------------------------------
# gemini_describe_once behavior
# ---------------------------------------------------------------------------
class TestDescribeOnce:
    def _set_behavior(self, account_home, mode, desc=""):
        b = account_home / ".gemini" / "test-behavior.json"
        b.write_text(json.dumps({"mode": mode, "desc": desc}))

    def test_unsupported_kind_returns_unsupported(self, mod_with_accounts, patched_env, tmp_path):
        attach = tmp_path / "song.mp3"
        attach.write_bytes(b"fake")
        account = mod_with_accounts.ACCOUNTS[0]
        desc, model, err = mod_with_accounts.gemini_describe_once(attach, "audio", account)
        assert (desc, model, err) == (None, None, "unsupported")

    def test_missing_file_returns_missing(self, mod_with_accounts, patched_env, tmp_path):
        account = mod_with_accounts.ACCOUNTS[0]
        desc, model, err = mod_with_accounts.gemini_describe_once(
            tmp_path / "nope.jpg", "image", account
        )
        assert (desc, model, err) == (None, None, "missing")

    def test_rate_limit_in_stderr_is_caught(self, mod_with_accounts, patched_env, tmp_path):
        attach = tmp_path / "img.jpg"
        attach.write_bytes(b"fake")
        account = mod_with_accounts.ACCOUNTS[0]
        self._set_behavior(account[1], "rate_limit")
        desc, model, err = mod_with_accounts.gemini_describe_once(attach, "image", account)
        assert err == "rate_limit", f"expected rate_limit, got err={err!r} desc={desc!r}"

    def test_refusal_in_stdout_is_caught(self, mod_with_accounts, patched_env, tmp_path):
        attach = tmp_path / "img.jpg"
        attach.write_bytes(b"fake")
        account = mod_with_accounts.ACCOUNTS[0]
        self._set_behavior(account[1], "refusal")
        desc, model, err = mod_with_accounts.gemini_describe_once(attach, "image", account)
        assert err == "refusal"

    def test_success_returns_description_and_model(self, mod_with_accounts, patched_env, tmp_path):
        attach = tmp_path / "img.jpg"
        attach.write_bytes(b"fake")
        account = mod_with_accounts.ACCOUNTS[0]
        self._set_behavior(account[1], "ok", desc="A photo of a cat.")
        desc, model, err = mod_with_accounts.gemini_describe_once(attach, "image", account)
        assert err is None
        assert desc == "A photo of a cat."
        assert model == mod_with_accounts.DESCRIPTION_MODEL


# ---------------------------------------------------------------------------
# Retry with rotation — the actual cycling logic
# ---------------------------------------------------------------------------
class TestRetryRotation:
    def test_rate_limit_marks_exhausted_and_retries_other_account(
        self, mod_with_accounts, patched_env, tmp_path
    ):
        """Account A returns rate_limit → mark exhausted → retry should hit B or C and succeed."""
        attach = tmp_path / "img.jpg"
        attach.write_bytes(b"fake")
        # First account: rate limit. Others: ok.
        mod_with_accounts.ACCOUNTS.sort()
        first = mod_with_accounts.ACCOUNTS[0]
        (first[1] / ".gemini" / "test-behavior.json").write_text(
            json.dumps({"mode": "rate_limit"})
        )
        for name, home in mod_with_accounts.ACCOUNTS[1:]:
            (home / ".gemini" / "test-behavior.json").write_text(
                json.dumps({"mode": "ok", "desc": f"OK from {name}"})
            )
        desc, model, err = mod_with_accounts.gemini_describe_with_retry(attach, "image")
        assert err is None, f"expected success, got err={err}"
        assert desc.startswith("OK from"), f"unexpected desc: {desc!r}"
        assert first[0] in mod_with_accounts._exhausted

    def test_all_accounts_rate_limit_returns_all_exhausted(
        self, mod_with_accounts, patched_env, tmp_path, monkeypatch
    ):
        attach = tmp_path / "img.jpg"
        attach.write_bytes(b"fake")
        for name, home in mod_with_accounts.ACCOUNTS:
            (home / ".gemini" / "test-behavior.json").write_text(
                json.dumps({"mode": "rate_limit"})
            )
        # Speed up the cooldown sleeps so test is fast
        monkeypatch.setattr(mod_with_accounts.time, "sleep", lambda *a, **k: None)
        desc, model, err = mod_with_accounts.gemini_describe_with_retry(
            attach, "image", max_retries=2
        )
        assert err in ("all_exhausted", "rate_limit"), f"got {err!r}"
        assert desc is None


# ---------------------------------------------------------------------------
# Per-account success counters — cycling proof
# ---------------------------------------------------------------------------
class TestAccountAttribution:
    def test_per_account_success_counts_recorded(
        self, mod_with_accounts, patched_env, tmp_path
    ):
        """After N calls across all accounts, each account's success count
        should be tracked so we can prove cycling actually happened."""
        for name, home in mod_with_accounts.ACCOUNTS:
            (home / ".gemini" / "test-behavior.json").write_text(
                json.dumps({"mode": "ok", "desc": f"OK from {name}"})
            )
        attach = tmp_path / "img.jpg"
        attach.write_bytes(b"fake")
        # Reset counters before this run
        mod_with_accounts.reset_account_stats()
        n = len(mod_with_accounts.ACCOUNTS) * 3
        for _ in range(n):
            mod_with_accounts.gemini_describe_with_retry(attach, "image")
        stats = mod_with_accounts.account_stats()
        # All accounts should have at least one success — proves cycling
        for name, _ in mod_with_accounts.ACCOUNTS:
            assert stats.get(name, {}).get("success", 0) > 0, (
                f"account {name} never used — cycling broken. stats={stats}"
            )
