# Changelog

All notable changes to the BGSU Career Openings project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and the project (loosely) follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Changed
- **Branding**: page/tab title and sidebar brand are now **"BGSU Finance & Accounting Career Openings"** (was "BGSU Career Openings" / "BGSU Career Hub"). BGSU orange-and-brown theme preserved.
- **Browse layout**: the keyword search now takes its own full-width row; the four filter dropdowns (Company, Location, Job type, Work mode) sit on a single row below with equal-width columns. Placeholder text updated to `Search title, company, skill, keyword...`.
- **Job posting cards**: removed the separate "View details" button. The **position title is now itself the clickable link** that opens the detail view. The title shows in BGSU brown, turns BGSU orange and underlines on hover. Cards keep brief info only: position title, company, job type, location, work mode (if present), application deadline (if present). Empty badges are no longer rendered.
- Cards are now built with `st.container(border=True)` so the clickable title sits inside the card box.

### Card design refresh
- **Bigger, more polished cards**: increased internal padding (`1.4rem × 1.6rem`), bigger radius (14px), and `1.15rem` margin between cards so the page feels less crowded.
- **Subtle hover lift**: cards translate up 2px and gain a soft shadow on hover; border tint warms slightly. BGSU orange accent stripe on the left is preserved.
- **Bolder, larger title**: title font size bumped to `1.34rem` with tighter letter-spacing.
- **Comfortable internal spacing**: clear separation between title, company, and badges.
- **Deadline is now a badge** in the same row as job type, location, and work mode. Subtle orange-tinted border highlights it without being loud. Badges wrap neatly when there are many.

### Removed
- The 1–2-line description preview under the badges has been removed from cards. Cards now show only: position title, company, job type, location, work mode (if present), deadline (if present). The `_preview_text` helper and `.opening-preview` CSS rule were deleted along with it. The full description continues to appear on the detail page.

### Card spacing fix
- Increased bottom padding inside each Browse card so the badge row no longer sits flush against the bottom border. New card padding: `1.5rem (top) · 1.65rem (sides) · 1.85rem (bottom)`. The asymmetry is intentional — the title's line-height adds intrinsic air above the text at the top, while the badge row has a hard bottom edge, so equal numeric padding *looks* unbalanced. The new values make top and bottom whitespace visually match without making cards noticeably taller.

### Security
- `_badge` now HTML-escapes its text content; company name and preview text are also escaped before injection into card markup. Prevents stray `<` / `>` / `&` in user-supplied posting data from breaking the layout.

---

## [0.2.0] — 2026-05-23

Turned the prototype into a **public student-facing site with a separate, password-protected admin/editor area**, and prepared the project for Streamlit Community Cloud deployment.

### Added
- **Public Browse page is now the default homepage** — students can visit without logging in and only see `Active` postings.
- **Search + filters** on Browse: keyword, company, location, job type, and work mode.
- **Password-gated Admin / Editor page** (`ADMIN_PASSWORD` via Streamlit secrets or env var). Sign-in/sign-out flow with session state.
- **Status workflow** for postings: `Draft`, `Active`, `Closed`. Only `Active` postings are visible on the public site.
- **URL ingestion**: editors can paste a job posting URL; the app fetches the page and extracts readable text via BeautifulSoup. Friendly fallback message when extraction fails (e.g. JS-only sites, login walls).
- **Manage postings tab** in the admin area — filter by status, edit any field, change status, or delete.
- **Edit existing postings** from the detail page when signed in as admin.
- New `utils/config.py` to centralize secret/env access (`OPENAI_API_KEY`, `ADMIN_PASSWORD`, `OPENAI_MODEL`).
- New `utils/url_fetch.py` for URL → readable-text extraction.
- README section covering Streamlit Community Cloud deployment, GitHub upload, and where each secret goes.
- README section explaining that local JSON storage is temporary and how to upgrade to Supabase / Firebase / Google Sheets later.

### Changed
- `utils/storage.py` rewritten as a `JsonStorage` class with a clear interface (`list_openings`, `get_opening`, `add_opening`, `update_opening`, `delete_opening`). The module exports a `storage` singleton so a cloud-DB backend can be swapped in by replacing one line.
- Records gained `status`, `updated_at`, and `source_url` fields. Older records without these fields are normalized on read (default status: `Active`).
- `utils/openai_client.py` now imports config helpers from `utils/config.py` and accepts an optional `source_url` for additional context to the model.
- Sidebar reorganized — top-level entries are now `🏠 Browse Openings` (default) and `🔐 Admin / Editor`.
- `.streamlit/secrets.toml.example` extended with `ADMIN_PASSWORD`.
- `requirements.txt` adds `requests` and `beautifulsoup4`.

### Deployment / docs
- README §7 walks through deploying publicly on Streamlit Community Cloud step by step.
- README §8 documents the "JSON storage is temporary" caveat and the abstract storage interface for upgrading to a cloud DB.
- `.gitignore` already excludes `.streamlit/secrets.toml`, `.env`, and `data/openings.json`.

---

## [0.1.0] — 2026-05-23

Initial prototype.

### Added
- Streamlit web app for BGSU students, themed in BGSU orange/brown.
- Single-page app with a sidebar that lets a user switch between **Browse Openings**, **Submit New Posting**, and a posting detail view.
- Submit form takes a raw posting (employer email / flyer / pasted text).
- OpenAI API integration (`gpt-4o-mini` by default) that standardizes raw text into a consistent JSON schema covering:
  job title, company, location, work mode, job type, eligibility, required skills, preferred qualifications, application deadline, application link, contact email, full description.
- Editable review form so the user can adjust AI output before saving.
- Local persistence to `data/openings.json` (auto-created), with insert / read / delete operations.
- Card-based listings view with simple keyword search.
- Detail view with structured sections and a collapsible "original raw text" panel.
- BGSU-themed Streamlit config (`primaryColor = "#FE5000"`, cream secondary background).
- `.streamlit/secrets.toml.example` template — `OPENAI_API_KEY` (and optional `OPENAI_MODEL`).
- `.gitignore` covering `__pycache__/`, virtualenvs, `.streamlit/secrets.toml`, `.env`, and `data/openings.json`.
- README with local setup, secret configuration, run instructions, and troubleshooting.

[Unreleased]: #unreleased
[0.2.0]: #020--2026-05-23
[0.1.0]: #010--2026-05-23
