"""One-time manual login into neetcode.io.

Run from the project root.

Opens Edge with the persistent profile at .claude/scripts/.neetcode-profile/.
Log in manually, then close the browser window — the session is saved to disk
and will be reused by fetch_problem.py in headless mode.
"""

import os

from playwright.sync_api import sync_playwright


def main() -> None:
    profile_dir = os.path.join(".claude", "scripts", ".neetcode-profile")
    os.makedirs(profile_dir, exist_ok=True)

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=profile_dir,
            headless=False,
            channel="msedge",
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://neetcode.io/login")
        print("Log in, then close the browser window to save the session.")
        page.wait_for_event("close", timeout=0)
        context.close()


if __name__ == "__main__":
    main()
