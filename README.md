# BGSU Career Openings

A public-facing Streamlit website where **BGSU students browse curated job and internship postings**, and a **password-protected admin/editor** ingests raw postings (from text or URL), standardizes them with the OpenAI API, and manages the listings.

- **Public side** (default): no login required. Students see only **Active** postings, with search and filters.
- **Admin side**: password-gated. Editor can add, edit, delete, and set status (Draft / Active / Closed). Postings can be ingested from raw text *or* a job posting URL.

Postings are stored locally in `data/openings.json` for prototyping.

> 📝  See [**CHANGELOG.md**](./CHANGELOG.md) for a version history of features and changes.

---

## Features

- 🏠  Browse Openings (default homepage) — clean cards with brief info
- 🔍  Search + filters (keyword, company, location, job type, work mode)
- 📄  Detail view with full posting info
- 🔐  Password-protected Admin / Editor page
- ✏️  Two ingestion modes — paste raw text **or** paste a URL
- ✨  OpenAI standardization into a consistent schema
- ✅  Review/edit AI output before saving
- 🏷️  Status workflow: **Draft / Active / Closed** (only Active is public)
- 🗂️  Edit and delete existing postings from the admin page
- 🎨  BGSU-themed styling (orange + brown palette)

---

## 1. Requirements

- **Python 3.10+** (3.11 or 3.12 recommended; 3.9 also works because the code uses `from __future__ import annotations`).
- An **OpenAI API key** — create one at <https://platform.openai.com/api-keys>.
- An admin password of your choosing.

You do **not** need a Streamlit Cloud or GitHub account just to run it locally.

---

## 2. Local setup (Windows / PowerShell)

From the project folder (`Career Website/`):

```powershell
# 1. Create and activate a virtual environment (recommended)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Install dependencies
pip install -r requirements.txt
```

On macOS / Linux, activate with `source .venv/bin/activate` instead.

---

## 3. Configure secrets

Pick **one** of these two options. Don't hard-code secrets into the source.

### Option A — Streamlit secrets file (recommended)

1. Copy the example file:

   ```powershell
   Copy-Item .streamlit\secrets.toml.example .streamlit\secrets.toml
   ```

2. Open `.streamlit\secrets.toml` and fill in real values:

   ```toml
   OPENAI_API_KEY = "sk-...your-real-key..."
   ADMIN_PASSWORD = "a-strong-long-password"
   # OPENAI_MODEL = "gpt-4o-mini"   # optional override
   ```

`.streamlit/secrets.toml` is already in `.gitignore`, so it won't be committed.

### Option B — Environment variables

```powershell
$env:OPENAI_API_KEY = "sk-...your-real-key..."
$env:ADMIN_PASSWORD = "a-strong-long-password"
# Optional:
# $env:OPENAI_MODEL = "gpt-4o-mini"
```

(macOS/Linux: `export OPENAI_API_KEY="sk-..."` etc.)

> If `ADMIN_PASSWORD` is not set, the Admin page is disabled — the public site still works.

---

## 4. Run the app

```powershell
python -m streamlit run app.py
```

Open <http://localhost:8501>. The default page is **Browse Openings** (public). Click **🔐 Admin / Editor** in the sidebar to sign in and add postings.

---

## 5. How to use

### Public (students)

1. Visit the site — no account or login required.
2. Browse Active postings as cards (job title, company, location, mode, type, deadline).
3. Use the search box and filter dropdowns to narrow results.
4. Click **View details →** to see the full posting.

### Admin (editor)

1. Click **🔐 Admin / Editor** in the sidebar, enter the admin password.
2. **Add new posting** — choose either:
   - **Paste raw text** — paste the employer's email or flyer content.
   - **Paste URL** — paste a job posting URL; the app extracts the page text. If extraction fails (e.g. site requires JavaScript or login), the fallback message will appear and you should copy the description manually and use **Paste raw text** instead.
3. Click **✨ Standardize** to call OpenAI and produce structured fields.
4. Review/edit each field, choose a **Status**:
   - **Draft** — not visible to students.
   - **Active** — visible on the public site.
   - **Closed** — archived, not visible.
5. **Manage postings** tab — filter by status, edit any field, change status, or delete.

All saved openings live in `data/openings.json`. Delete that file to reset.

---

## 6. Project structure

```
Career Website/
├── app.py                       # Streamlit entry point
├── requirements.txt
├── README.md
├── CHANGELOG.md                 # Version history & notable changes
├── .gitignore
├── .streamlit/
│   ├── config.toml              # BGSU theme
│   └── secrets.toml.example     # Copy to secrets.toml and fill values
├── utils/
│   ├── __init__.py
│   ├── config.py                # Reads secrets/env (OPENAI_API_KEY, ADMIN_PASSWORD, …)
│   ├── openai_client.py         # Standardize raw text → structured JSON
│   ├── storage.py               # JsonStorage backend (swap class to upgrade)
│   └── url_fetch.py             # Fetch + extract text from job-posting URLs
└── data/
    └── openings.json            # Created automatically on first save
```

---

## 7. Deploying publicly on Streamlit Community Cloud

This is the simplest way to give students a public URL.

### Step 1 — Push to GitHub

1. Create a new GitHub repository (private or public is fine).

2. From this folder:

   ```powershell
   git init
   git add .
   git commit -m "Initial BGSU career site"
   git branch -M main
   git remote add origin https://github.com/<your-username>/<your-repo>.git
   git push -u origin main
   ```

3. **Important — confirm no secrets were committed.** `.streamlit/secrets.toml`, `.env`, and `data/openings.json` are in `.gitignore`, but double-check on GitHub before deploying.

### Step 2 — Deploy on Streamlit Community Cloud

1. Sign in at <https://streamlit.io/cloud> with your GitHub account.
2. Click **New app**.
3. Select your repository, branch (`main`), and main file (`app.py`).
4. Click **Advanced settings → Secrets** and paste:

   ```toml
   OPENAI_API_KEY = "sk-...your-real-key..."
   ADMIN_PASSWORD = "a-strong-long-password"
   # OPENAI_MODEL = "gpt-4o-mini"
   ```

5. Click **Deploy**. After ~1 minute you'll get a public URL like `https://<your-app>.streamlit.app`.

6. Share the URL with students. They will see the **Browse Openings** page directly.

### What you need vs. what you provide

| You need | Where it goes |
|---|---|
| **OpenAI API key** | Streamlit Cloud → *Settings → Secrets* (or local `.streamlit/secrets.toml`). Never put it in source code. |
| **Admin password** | Same place. Pick something long and random. |
| **GitHub account** | Only needed for the Streamlit Cloud workflow (Step 1). |
| **Streamlit account** | Only needed for cloud deployment, free at streamlit.io/cloud. |

---

## 8. ⚠️ Storage is temporary

The current code stores openings in a **local JSON file** (`data/openings.json`). This is fine for local prototyping and a small single-editor deployment, but it has limits when deployed publicly:

- **Streamlit Community Cloud has an ephemeral filesystem.** When the app restarts (after inactivity, redeploys, or config changes), the JSON file is wiped and **all postings are lost**.
- It is not safe for multiple concurrent editors.
- It does not scale to many postings or large traffic.

**For a real public multi-user deployment, upgrade the storage backend.** Good options:

- **Supabase** (Postgres + REST + auth, generous free tier)
- **Firebase / Firestore**
- **Google Sheets** (via `gspread`) — simplest if you want a non-technical editor experience

### How to upgrade later

The code is structured to make this easy. `utils/storage.py` defines a `JsonStorage` class with these methods:

```
list_openings(statuses=None)
get_opening(id)
add_opening(opening, raw_text, source_url, status)
update_opening(id, updates)
delete_opening(id)
```

To swap backends:

1. Add a new class (e.g. `SupabaseStorage`) implementing the same methods.
2. Replace the bottom of `utils/storage.py`:

   ```python
   storage: JsonStorage = JsonStorage()
   ```

   with your new class:

   ```python
   storage = SupabaseStorage()
   ```

3. Nothing else in `app.py` has to change.

---

## 9. Troubleshooting

- **`OPENAI_API_KEY is not set`** — you didn't complete step 3. Either create `.streamlit/secrets.toml` or set the env variable in the same shell that runs `streamlit`.
- **Admin page says "ADMIN_PASSWORD is not set"** — same fix: add `ADMIN_PASSWORD` to your secrets file or env.
- **`401` from OpenAI** — the key is wrong, revoked, or has no billing attached. Check <https://platform.openai.com/api-keys>.
- **URL extraction returns "Could not extract enough readable text"** — many sites (LinkedIn, Indeed, Handshake) block scrapers or require JavaScript. Use the **Paste raw text** option instead.
- **Postings disappeared after deploy / restart** — expected on Streamlit Community Cloud (see §8). Upgrade to a cloud database for persistence.
- **`ModuleNotFoundError`** — your virtual environment isn't activated, or `pip install -r requirements.txt` hasn't been run.
- **Port already in use** — `python -m streamlit run app.py --server.port 8502`.

---

Built for BGSU 🟠🟤
