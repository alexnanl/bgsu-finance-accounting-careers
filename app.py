"""BGSU Career Openings — Streamlit app.

Public side (default): students browse Active job/internship postings.
Admin side (password-gated): editors add, standardize, edit, and manage postings.
"""
from __future__ import annotations

import html
from typing import Any

import streamlit as st

from utils.config import get_admin_password
from utils.openai_client import OpenAIConfigError, standardize_posting
from utils.storage import (
    DEFAULT_STATUS,
    OPENING_FIELDS,
    VALID_STATUSES,
    storage,
)
from utils.url_fetch import UrlFetchError, fetch_text_from_url

st.set_page_config(
    page_title="BGSU Finance & Accounting Career Openings",
    page_icon="🟠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- styling ----------
CUSTOM_CSS = """
<style>
:root {
    --bgsu-orange: #FE5000;
    --bgsu-brown: #4F2C1D;
    --bgsu-cream: #FFF4EC;
    --bgsu-ink: #231F20;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1180px;
}

.hero {
    background: linear-gradient(120deg, #FE5000 0%, #C84100 100%);
    color: white;
    padding: 1.6rem 1.8rem;
    border-radius: 14px;
    margin-bottom: 1.4rem;
    box-shadow: 0 6px 20px rgba(254, 80, 0, 0.18);
}
.hero h1 { margin: 0; font-size: 1.85rem; font-weight: 700; letter-spacing: -0.01em; }
.hero p  { margin: 0.35rem 0 0 0; opacity: 0.95; font-size: 1rem; }

.opening-company {
    color: var(--bgsu-ink);
    font-weight: 600;
    font-size: 1.02rem;
    margin: 0.65rem 0 0 0;
}
.opening-badges {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-top: 0.95rem;
}

.badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-right: 6px;
    background: var(--bgsu-cream);
    color: var(--bgsu-brown);
    border: 1px solid #F5E4D4;
}
.badge-accent   { background: var(--bgsu-orange); color: white; border-color: var(--bgsu-orange); }
.badge-draft    { background: #FFF7DB; color: #7A5C00; border-color: #F1DF99; }
.badge-active   { background: #E4F6E4; color: #1F6B1F; border-color: #B8E0B8; }
.badge-closed   { background: #EDEDED; color: #6B635D; border-color: #D8D2CC; }
.badge-deadline { background: white;   color: var(--bgsu-brown); border-color: #F8C9A3; }

.detail-section h4 {
    color: var(--bgsu-brown);
    margin-bottom: 0.3rem;
    margin-top: 1.1rem;
    border-bottom: 2px solid var(--bgsu-cream);
    padding-bottom: 0.25rem;
}
.detail-section .field-value { white-space: pre-wrap; color: var(--bgsu-ink); line-height: 1.5; }

.empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: #8a807a;
    border: 2px dashed #EFE6DE;
    border-radius: 12px;
    background: #FBF8F5;
}

.footer-note {
    margin-top: 3rem;
    padding-top: 1rem;
    border-top: 1px solid #EFE6DE;
    color: #8a807a;
    font-size: 0.82rem;
    text-align: center;
}

/* Job-title button styled to look like a card link */
[class*="st-key-jobtitle-"] button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    min-height: 0 !important;
    height: auto !important;
    text-align: left !important;
    justify-content: flex-start !important;
    width: auto !important;
}
[class*="st-key-jobtitle-"] button p {
    color: var(--bgsu-brown);
    font-size: 1.34rem !important;
    font-weight: 700 !important;
    margin: 0 !important;
    line-height: 1.3 !important;
    letter-spacing: -0.01em;
    transition: color 0.1s ease;
}
[class*="st-key-jobtitle-"] button:hover {
    background: transparent !important;
}
[class*="st-key-jobtitle-"] button:hover p {
    color: var(--bgsu-orange);
    text-decoration: underline;
    text-underline-offset: 3px;
}
[class*="st-key-jobtitle-"] button:focus p {
    color: var(--bgsu-orange);
}

/* Bordered Streamlit containers — used for Browse cards */
[data-testid="stVerticalBlockBorderWrapper"] {
    border: 1px solid #EFE6DE !important;
    border-left: 5px solid var(--bgsu-orange) !important;
    border-radius: 14px !important;
    /* top right bottom left — bottom is intentionally larger so the */
    /* badge row's hard bottom edge visually balances the title's    */
    /* line-height air at the top.                                    */
    padding: 1.5rem 1.65rem 1.85rem 1.65rem !important;
    background: white !important;
    box-shadow: 0 1px 3px rgba(35, 31, 32, 0.04) !important;
    margin-bottom: 1.15rem !important;
    transition: transform 0.14s ease,
                box-shadow 0.18s ease,
                border-color 0.18s ease;
}
[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 24px rgba(35, 31, 32, 0.08) !important;
    border-color: #F1D7BD !important;
    border-left-color: var(--bgsu-orange) !important;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


FIELD_LABELS = {
    "job_title": "Job Title",
    "company": "Company / Organization",
    "location": "Location",
    "work_mode": "Remote / Hybrid / Onsite",
    "job_type": "Job Type",
    "eligibility": "Eligibility",
    "required_skills": "Required Skills",
    "preferred_qualifications": "Preferred Qualifications",
    "application_deadline": "Application Deadline",
    "application_link": "Application Link",
    "contact_email": "Contact Email",
    "full_description": "Full Description",
}

WORK_MODES = ["", "Remote", "Hybrid", "Onsite"]


# ---------- helpers ----------
def _init_state() -> None:
    st.session_state.setdefault("page", "Browse")
    st.session_state.setdefault("selected_id", None)
    st.session_state.setdefault("preview", None)
    st.session_state.setdefault("preview_raw", "")
    st.session_state.setdefault("preview_source_url", "")
    st.session_state.setdefault("admin_authed", False)
    st.session_state.setdefault("admin_tab", "Add new")
    st.session_state.setdefault("edit_id", None)


def _go(page: str, opening_id: str | None = None) -> None:
    st.session_state.page = page
    st.session_state.selected_id = opening_id


def _badge(text: str, cls: str = "badge") -> str:
    if not text:
        return ""
    return f'<span class="{cls}">{html.escape(text)}</span>'


def _status_badge(status: str) -> str:
    cls_map = {"Draft": "badge badge-draft", "Active": "badge badge-active", "Closed": "badge badge-closed"}
    return _badge(status, cls_map.get(status, "badge"))


def render_hero(title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="hero"><h1>{title}</h1><p>{subtitle}</p></div>',
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown("### 🟠 BGSU Finance & Accounting Career Openings")
        st.caption("AI-formatted job & internship postings for BGSU students.")
        st.divider()
        if st.button("🏠  Browse Openings", use_container_width=True):
            _go("Browse")
            st.rerun()
        if st.button("🔐  Admin / Editor", use_container_width=True):
            _go("Admin")
            st.rerun()
        st.divider()
        active_count = len(storage.list_openings(statuses=("Active",)))
        st.metric("Active openings", active_count)

        if st.session_state.get("admin_authed"):
            st.divider()
            st.success("Signed in as editor")
            if st.button("Sign out", use_container_width=True):
                st.session_state.admin_authed = False
                _go("Browse")
                st.rerun()


def render_footer() -> None:
    st.markdown(
        '<div class="footer-note">Built for BGSU students · '
        "Postings are AI-formatted from sources submitted by editors. "
        "Always verify details on the employer's official site before applying."
        "</div>",
        unsafe_allow_html=True,
    )


# ---------- public pages ----------
def page_browse() -> None:
    render_hero(
        "BGSU Finance & Accounting Career Openings",
        "Browse job and internship opportunities curated for BGSU students.",
    )

    openings = storage.list_openings(statuses=("Active",))

    all_companies = sorted({o.get("company", "") for o in openings if o.get("company")})
    all_locations = sorted({o.get("location", "") for o in openings if o.get("location")})
    all_types = sorted({o.get("job_type", "") for o in openings if o.get("job_type")})

    query = st.text_input(
        "Search",
        placeholder="Search title, company, skill, keyword...",
        label_visibility="collapsed",
    )

    fc1, fc2, fc3, fc4 = st.columns(4)
    company_pick = fc1.selectbox(
        "Company", ["All companies"] + all_companies, label_visibility="collapsed",
    )
    location_pick = fc2.selectbox(
        "Location", ["All locations"] + all_locations, label_visibility="collapsed",
    )
    type_pick = fc3.selectbox(
        "Job type", ["All job types"] + all_types, label_visibility="collapsed",
    )
    mode_pick = fc4.selectbox(
        "Work mode", ["All work modes", "Remote", "Hybrid", "Onsite"],
        label_visibility="collapsed",
    )

    # Apply filters
    def _matches(op: dict[str, Any]) -> bool:
        if query:
            blob = " ".join(str(op.get(k, "")) for k in [
                "job_title", "company", "location", "job_type", "work_mode",
                "required_skills", "preferred_qualifications", "full_description",
            ]).lower()
            if query.lower() not in blob:
                return False
        if company_pick != "All companies" and op.get("company") != company_pick:
            return False
        if location_pick != "All locations" and op.get("location") != location_pick:
            return False
        if type_pick != "All job types" and op.get("job_type") != type_pick:
            return False
        if mode_pick != "All work modes" and op.get("work_mode") != mode_pick:
            return False
        return True

    filtered = [o for o in openings if _matches(o)]

    st.caption(f"Showing {len(filtered)} of {len(openings)} active openings")

    if not filtered:
        st.markdown(
            """
            <div class="empty-state">
                <h3 style="margin-top:0;">No openings match your filters</h3>
                <p>Try clearing search or changing the filters above.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        render_footer()
        return

    for op in filtered:
        title = op.get("job_title") or "Untitled Position"
        company = op.get("company") or "Unknown organization"
        location = op.get("location") or ""
        work_mode = op.get("work_mode") or ""
        job_type = op.get("job_type") or ""
        deadline = op.get("application_deadline") or ""

        badges = "".join([
            _badge(job_type, cls="badge badge-accent") if job_type else "",
            _badge(location) if location else "",
            _badge(work_mode) if work_mode else "",
            _badge(f"⏰ {deadline}", cls="badge badge-deadline") if deadline else "",
        ])

        with st.container(border=True):
            if st.button(title, key=f"jobtitle-{op['id']}"):
                _go("Detail", op["id"])
                st.rerun()
            st.markdown(
                f"""
                <p class="opening-company">{html.escape(company)}</p>
                <div class="opening-badges">{badges}</div>
                """,
                unsafe_allow_html=True,
            )

    render_footer()


def page_detail() -> None:
    opening_id = st.session_state.get("selected_id")
    opening = storage.get_opening(opening_id) if opening_id else None

    if not opening:
        st.warning("That opening could not be found.")
        if st.button("← Back to listings"):
            _go("Browse")
            st.rerun()
        return

    if opening.get("status") != "Active" and not st.session_state.get("admin_authed"):
        st.warning("This posting is not currently published.")
        if st.button("← Back to listings"):
            _go("Browse")
            st.rerun()
        return

    if st.button("← Back to listings"):
        _go("Browse")
        st.rerun()

    render_hero(
        opening.get("job_title") or "Untitled Position",
        opening.get("company") or "Unknown organization",
    )

    meta_cols = st.columns(3)
    meta_cols[0].markdown(f"**📍 Location**  \n{opening.get('location') or '—'}")
    meta_cols[1].markdown(f"**🏢 Mode**  \n{opening.get('work_mode') or '—'}")
    meta_cols[2].markdown(f"**💼 Type**  \n{opening.get('job_type') or '—'}")

    meta_cols2 = st.columns(3)
    meta_cols2[0].markdown(f"**⏰ Deadline**  \n{opening.get('application_deadline') or '—'}")
    link = opening.get("application_link") or ""
    meta_cols2[1].markdown(f"**🔗 Apply**  \n[{link}]({link})" if link else "**🔗 Apply**  \n—")
    email = opening.get("contact_email") or ""
    meta_cols2[2].markdown(f"**✉️ Contact**  \n{email}" if email else "**✉️ Contact**  \n—")

    st.markdown('<div class="detail-section">', unsafe_allow_html=True)
    for field in ["eligibility", "required_skills", "preferred_qualifications", "full_description"]:
        value = opening.get(field) or ""
        if not value:
            continue
        st.markdown(f"#### {FIELD_LABELS[field]}")
        st.markdown(f'<div class="field-value">{value}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.get("admin_authed"):
        st.divider()
        st.caption(f"Status: {opening.get('status')} · Updated: {opening.get('updated_at')}")
        if st.button("✏️  Edit this posting"):
            st.session_state.edit_id = opening["id"]
            st.session_state.admin_tab = "Manage postings"
            _go("Admin")
            st.rerun()


# ---------- admin pages ----------
def _admin_gate() -> bool:
    expected = get_admin_password()
    if not expected:
        st.error(
            "Admin access is disabled because **ADMIN_PASSWORD** is not set. "
            "Add it to `.streamlit/secrets.toml` (or as an environment variable) "
            "to enable the editor page."
        )
        return False

    if st.session_state.get("admin_authed"):
        return True

    st.info("This page is for the BGSU editor / admin only.")
    with st.form("admin-login", clear_on_submit=False):
        pwd = st.text_input("Admin password", type="password")
        ok = st.form_submit_button("Sign in", type="primary")
    if ok:
        if pwd == expected:
            st.session_state.admin_authed = True
            st.success("Signed in.")
            st.rerun()
        else:
            st.error("Incorrect password.")
    return False


def page_admin() -> None:
    render_hero(
        "Admin / Editor",
        "Add, standardize, and manage job & internship postings.",
    )

    if not _admin_gate():
        return

    tab_add, tab_manage = st.tabs(["➕  Add new posting", "🗂  Manage postings"])
    with tab_add:
        _admin_add_tab()
    with tab_manage:
        _admin_manage_tab()


def _admin_add_tab() -> None:
    st.markdown("##### 1. Provide the raw posting")
    mode = st.radio(
        "Input method",
        ["Paste raw text", "Paste URL"],
        horizontal=True,
        label_visibility="collapsed",
    )

    raw_text = st.session_state.get("preview_raw", "")
    source_url = st.session_state.get("preview_source_url", "")

    if mode == "Paste raw text":
        raw_text = st.text_area(
            "Raw posting text",
            value=raw_text,
            height=240,
            placeholder=(
                "Paste the full employer email, flyer text, or job description here…"
            ),
        )
        st.session_state.preview_raw = raw_text
    else:
        url = st.text_input(
            "Job posting URL",
            value=source_url,
            placeholder="https://example.com/careers/software-intern",
        )
        st.session_state.preview_source_url = url
        st.caption(
            "We'll try to extract the posting text from the URL. **If extraction fails, "
            "paste the job posting text manually** using the other option."
        )
        if st.button("Fetch text from URL"):
            try:
                with st.spinner("Fetching page…"):
                    extracted = fetch_text_from_url(url)
                st.session_state.preview_raw = extracted
                st.success(f"Fetched {len(extracted):,} characters. Review below, then standardize.")
                raw_text = extracted
            except UrlFetchError as e:
                st.error(
                    f"{e}\n\nFallback: copy the job description from the page "
                    "and paste it using **Paste raw text** instead."
                )

        if st.session_state.get("preview_raw"):
            with st.expander("Fetched text (preview)", expanded=False):
                st.text_area(
                    "Fetched text",
                    value=st.session_state.preview_raw,
                    height=200,
                    label_visibility="collapsed",
                    key="fetched_preview_display",
                )
            raw_text = st.session_state.preview_raw

    st.markdown("##### 2. Standardize with OpenAI")
    col_a, col_b = st.columns(2)
    if col_a.button("✨  Standardize", type="primary", use_container_width=True):
        if not (raw_text or "").strip():
            st.warning("Please provide raw text or fetch from a URL first.")
        else:
            try:
                with st.spinner("Asking OpenAI to standardize the posting…"):
                    structured = standardize_posting(
                        raw_text, source_url=st.session_state.get("preview_source_url", "")
                    )
                st.session_state.preview = structured
                st.success("Standardized! Review and edit below, then save.")
            except OpenAIConfigError as e:
                st.error(str(e))
            except Exception as e:  # noqa: BLE001
                st.error(f"OpenAI request failed: {e}")
    if col_b.button("Clear form", use_container_width=True):
        st.session_state.preview = None
        st.session_state.preview_raw = ""
        st.session_state.preview_source_url = ""
        st.rerun()

    preview = st.session_state.get("preview")
    if not preview:
        return

    st.divider()
    st.markdown("##### 3. Review, edit, and save")
    _opening_edit_form(
        preview,
        form_key="new-opening",
        save_label="💾  Save posting",
        on_save_new=True,
    )


def _admin_manage_tab() -> None:
    edit_id = st.session_state.get("edit_id")
    if edit_id:
        opening = storage.get_opening(edit_id)
        if not opening:
            st.warning("That posting could not be found.")
            st.session_state.edit_id = None
            return
        st.markdown(f"### Editing: {opening.get('job_title') or 'Untitled'}")
        if st.button("← Back to list"):
            st.session_state.edit_id = None
            st.rerun()
        _opening_edit_form(
            opening,
            form_key=f"edit-{opening['id']}",
            save_label="💾  Save changes",
            on_save_new=False,
            opening_id=opening["id"],
            initial_status=opening.get("status", DEFAULT_STATUS),
        )
        st.divider()
        if st.button("🗑️  Delete this posting", type="secondary"):
            storage.delete_opening(opening["id"])
            st.session_state.edit_id = None
            st.success("Deleted.")
            st.rerun()
        return

    # List view
    status_filter = st.selectbox(
        "Filter by status",
        ["All", "Draft", "Active", "Closed"],
        index=0,
    )
    statuses = None if status_filter == "All" else (status_filter,)
    items = storage.list_openings(statuses=statuses)
    if not items:
        st.info("No postings match this filter.")
        return

    for op in items:
        c1, c2, c3, c4, c5 = st.columns([3.5, 2, 1.5, 1, 1])
        c1.markdown(
            f"**{op.get('job_title') or '(untitled)'}**  \n"
            f"<span style='color:#6B635D;font-size:0.85rem'>{op.get('company') or ''}</span>",
            unsafe_allow_html=True,
        )
        c2.markdown(f"{op.get('location') or '—'}  \n*{op.get('job_type') or ''}*")
        c3.markdown(_status_badge(op.get("status", DEFAULT_STATUS)), unsafe_allow_html=True)
        if c4.button("Edit", key=f"edit-btn-{op['id']}"):
            st.session_state.edit_id = op["id"]
            st.rerun()
        if c5.button("View", key=f"viewadmin-{op['id']}"):
            _go("Detail", op["id"])
            st.rerun()
        st.markdown("<hr style='margin: 0.4rem 0; border: none; border-top: 1px solid #EFE6DE;'/>", unsafe_allow_html=True)


def _opening_edit_form(
    data: dict[str, Any],
    *,
    form_key: str,
    save_label: str,
    on_save_new: bool,
    opening_id: str | None = None,
    initial_status: str = DEFAULT_STATUS,
) -> None:
    with st.form(form_key, clear_on_submit=False):
        edited: dict[str, str] = {}
        c1, c2 = st.columns(2)
        edited["job_title"] = c1.text_input(FIELD_LABELS["job_title"], data.get("job_title", ""))
        edited["company"] = c2.text_input(FIELD_LABELS["company"], data.get("company", ""))

        c3, c4, c5 = st.columns(3)
        edited["location"] = c3.text_input(FIELD_LABELS["location"], data.get("location", ""))

        mode_opts = list(WORK_MODES)
        current_mode = data.get("work_mode", "") or ""
        if current_mode not in mode_opts:
            mode_opts.append(current_mode)
        edited["work_mode"] = c4.selectbox(
            FIELD_LABELS["work_mode"], mode_opts, index=mode_opts.index(current_mode),
        )
        edited["job_type"] = c5.text_input(FIELD_LABELS["job_type"], data.get("job_type", ""))

        edited["eligibility"] = st.text_area(FIELD_LABELS["eligibility"], data.get("eligibility", ""), height=80)
        edited["required_skills"] = st.text_area(FIELD_LABELS["required_skills"], data.get("required_skills", ""), height=110)
        edited["preferred_qualifications"] = st.text_area(
            FIELD_LABELS["preferred_qualifications"], data.get("preferred_qualifications", ""), height=110,
        )

        c6, c7, c8 = st.columns(3)
        edited["application_deadline"] = c6.text_input(FIELD_LABELS["application_deadline"], data.get("application_deadline", ""))
        edited["application_link"] = c7.text_input(FIELD_LABELS["application_link"], data.get("application_link", ""))
        edited["contact_email"] = c8.text_input(FIELD_LABELS["contact_email"], data.get("contact_email", ""))

        edited["full_description"] = st.text_area(FIELD_LABELS["full_description"], data.get("full_description", ""), height=200)

        st.markdown("---")
        status = st.radio(
            "Status",
            options=list(VALID_STATUSES),
            index=list(VALID_STATUSES).index(initial_status if initial_status in VALID_STATUSES else DEFAULT_STATUS),
            horizontal=True,
            help="Only Active postings are visible to students on the public site.",
        )

        submitted = st.form_submit_button(save_label, type="primary")
        if not submitted:
            return

        for f in OPENING_FIELDS:
            edited.setdefault(f, "")

        if on_save_new:
            raw_text = st.session_state.get("preview_raw", "")
            source_url = st.session_state.get("preview_source_url", "")
            record = storage.add_opening(
                edited, raw_text=raw_text, source_url=source_url, status=status,
            )
            st.session_state.preview = None
            st.session_state.preview_raw = ""
            st.session_state.preview_source_url = ""
            st.success(f"Saved as **{status}**.")
            if status == "Active":
                _go("Detail", record["id"])
                st.rerun()
        else:
            assert opening_id is not None
            updates = dict(edited)
            updates["status"] = status
            storage.update_opening(opening_id, updates)
            st.success("Changes saved.")
            st.session_state.edit_id = None
            st.rerun()


# ---------- main ----------
def main() -> None:
    _init_state()
    render_sidebar()
    page = st.session_state.page
    if page == "Admin":
        page_admin()
    elif page == "Detail":
        page_detail()
    else:
        page_browse()


if __name__ == "__main__":
    main()
