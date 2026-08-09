from __future__ import annotations

import os
from pathlib import Path

from playwright.sync_api import sync_playwright

STATE_FILE = Path(__file__).resolve().parent.parent / "data" / "auth" / "facebook_storage_state.json"
MARKETPLACE_URL = "https://www.facebook.com/marketplace/"


def main() -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(locale="en-US")
        page = context.new_page()
        page.goto(MARKETPLACE_URL, wait_until="domcontentloaded", timeout=60_000)

        print("Log in to Facebook in the browser window.")
        print("Complete any verification Facebook requests.")
        input("When Marketplace is visible, return here and press Enter to save the session: ")

        if "login" in page.url.lower():
            browser.close()
            raise RuntimeError("Facebook still shows the login page. The session was not saved.")

        context.storage_state(path=str(STATE_FILE))
        try:
            os.chmod(STATE_FILE, 0o600)
        except OSError:
            pass
        browser.close()

    print(f"Authentication saved locally to {STATE_FILE}")
    print("Treat this file like a password. It is excluded from Git by .gitignore.")


if __name__ == "__main__":
    main()
