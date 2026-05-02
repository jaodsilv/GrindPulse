"""Interactive one-time login for neetcode.io.

Launches a visible browser with a persistent user-data-dir. User logs in
manually. The script auto-detects successful login by polling localStorage
for `last-login-provider`. Persists login in user-data-dir so
fetch_problem.py can reuse it.

Run from project root: python .claude/scripts/auth_neetcode.py
"""

import os
import sys
import time

from playwright.sync_api import sync_playwright

PROFILE_PATH = os.path.join(".claude", "scripts", ".neetcode-profile")
POLL_INTERVAL_SEC = 2
TIMEOUT_SEC = 600  # 10 minutes to log in


def _is_logged_in(page) -> bool:
    """Login detected when neetcode sets `last-login-provider` in localStorage."""
    try:
        provider = page.evaluate("() => localStorage.getItem('last-login-provider')")
    except Exception:
        return False
    return bool(provider)


def main():
    os.makedirs(PROFILE_PATH, exist_ok=True)
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            PROFILE_PATH, headless=False, channel="msedge"
        )
        page = context.new_page()
        page.goto("https://neetcode.io/", wait_until="networkidle", timeout=30000)
        # Wait for the Angular app to finish its first render before polling
        page.wait_for_timeout(3000)

        print(
            "Log in to neetcode.io in the browser window. "
            f"The script will auto-detect login (polling every {POLL_INTERVAL_SEC}s, "
            f"timeout {TIMEOUT_SEC}s).",
            flush=True,
        )

        deadline = time.time() + TIMEOUT_SEC
        while time.time() < deadline:
            if _is_logged_in(page):
                print("Login detected.", flush=True)
                break
            time.sleep(POLL_INTERVAL_SEC)
        else:
            print("Timed out waiting for login.", file=sys.stderr, flush=True)
            context.close()
            sys.exit(1)

        # Give the app a moment to finish populating localStorage/cookies
        time.sleep(2)

        print(f"Session persisted in {PROFILE_PATH}", flush=True)

        context.close()


if __name__ == "__main__":
    main()
