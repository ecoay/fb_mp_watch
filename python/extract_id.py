from __future__ import annotations

import csv
import datetime as dt
import os
import re
from pathlib import Path
from urllib.parse import quote_plus

from playwright.sync_api import sync_playwright

DEFAULT_LOCATION = "kansas-city"
DEFAULT_QUERY = "car or truck"
SAFE_LOCATION = re.compile(r"^[a-z0-9-]+$")
ITEM_PATTERN = re.compile(r"/marketplace/item/(\d+)")
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STATE_FILE = PROJECT_ROOT / "data" / "auth" / "facebook_storage_state.json"


def search_url(location: str, query: str) -> str:
    if not SAFE_LOCATION.fullmatch(location):
        raise ValueError("MARKETPLACE_LOCATION must use lowercase letters, numbers, and hyphens only")
    if not query.strip() or len(query) > 100:
        raise ValueError("MARKETPLACE_QUERY must be between 1 and 100 characters")
    return (
        f"https://www.facebook.com/marketplace/{location}/search"
        f"?daysSinceListed=1&query={quote_plus(query.strip())}"
    )


def run() -> Path:
    location = os.getenv("MARKETPLACE_LOCATION", DEFAULT_LOCATION).strip()
    query = os.getenv("MARKETPLACE_QUERY", DEFAULT_QUERY).strip()
    state_file = Path(os.getenv("FB_STORAGE_STATE_PATH", str(DEFAULT_STATE_FILE)))
    output_dir = PROJECT_ROOT / "data" / "extracted_id"
    output_dir.mkdir(parents=True, exist_ok=True)

    if not state_file.is_file():
        raise RuntimeError(
            f"No local Facebook session found at {state_file}. "
            "Run: python python/authenticate.py"
        )

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(storage_state=str(state_file), locale="en-US")
        page = context.new_page()
        try:
            url = search_url(location, query)
            print(f"Searching {url}")
            page.goto(url, wait_until="domcontentloaded", timeout=60_000)
            page.wait_for_timeout(5_000)

            if "login" in page.url.lower():
                raise RuntimeError(
                    "The saved Facebook session has expired. "
                    "Run: python python/authenticate.py"
                )

            item_ids: set[str] = set()
            for tag in page.query_selector_all('a[href*="/marketplace/item/"]'):
                href = tag.get_attribute("href")
                if not href:
                    continue
                match = ITEM_PATTERN.search(href)
                if match:
                    item_ids.add(match.group(1))

            timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d-%H-%M-%S")
            output_file = output_dir / f"{timestamp}_extracted_ids.csv"
            with output_file.open("w", newline="", encoding="utf-8") as handle:
                writer = csv.writer(handle)
                writer.writerow(["item_id", "item_url", "location", "query"])
                for item_id in sorted(item_ids):
                    writer.writerow([
                        item_id,
                        f"https://www.facebook.com/marketplace/item/{item_id}",
                        location,
                        query,
                    ])

            page.screenshot(path=str(output_dir / f"{timestamp}_search.png"), full_page=True)
            print(f"Found {len(item_ids)} unique listings")
            print(f"Saved results to {output_file}")
            return output_file
        finally:
            context.close()
            browser.close()


if __name__ == "__main__":
    run()
