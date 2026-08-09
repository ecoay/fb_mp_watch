# fb_mp_watch

A Facebook Marketplace listing-ID collector.

## Secure local setup

Authenticated searches run locally. Your Facebook password is entered only into Facebook's own browser page. The saved browser session remains on your computer and is excluded from Git.

Requirements:

- Python 3.10 or newer
- A Facebook account with Marketplace access

From PowerShell in the repository folder:

```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install --requirement requirements.txt
.\.venv\Scripts\python -m playwright install chromium
```

## Authenticate

Run:

```powershell
.\.venv\Scripts\python python/authenticate.py
```

A browser window opens. Log into Facebook, complete any verification it requests, wait until Marketplace is visible, then return to PowerShell and press Enter.

The session is stored at `data/auth/facebook_storage_state.json`. Treat this file like a password. Never upload, share, or commit it.

## Run a search

The defaults search Kansas City for `car or truck`:

```powershell
.\.venv\Scripts\python python/extract_id.py
```

To change the search:

```powershell
$env:MARKETPLACE_LOCATION = "kansas-city"
$env:MARKETPLACE_QUERY = "pickup truck"
.\.venv\Scripts\python python/extract_id.py
```

Results and a diagnostic screenshot are saved under `data/extracted_id`.

## Security notes

- Do not store a Facebook password in GitHub Secrets.
- Do not upload `facebook_storage_state.json`; it contains session cookies.
- Re-run `python/authenticate.py` if Facebook expires the session.
- GitHub-hosted runners cannot access your local authenticated session. Authenticated Marketplace searches should remain local.
