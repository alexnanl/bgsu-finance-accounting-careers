"""Standardize raw job/internship postings into structured fields via OpenAI."""
from __future__ import annotations

import json
from typing import Any

from openai import OpenAI

from .config import get_openai_api_key, get_openai_model

SYSTEM_PROMPT = """You are a career-services assistant for Bowling Green State University (BGSU).
You receive raw, unstructured job or internship postings copied from employer emails,
flyers, or web pages, and you reformat them into a clean, consistent JSON structure
for student review.

Rules:
- Output ONLY a single JSON object that matches the requested schema. No prose, no markdown.
- Use the exact field names provided. Use empty string "" for any field you genuinely cannot
  determine from the source. Do not invent facts.
- "work_mode" must be one of: "Remote", "Hybrid", "Onsite", or "" if unclear.
- "job_type" should be a short label like "Full-time", "Part-time", "Internship",
  "Co-op", "Contract", or "" if unclear.
- "required_skills" and "preferred_qualifications" should be concise bullet-style strings
  separated by newlines (one item per line, no leading dashes).
- "application_deadline" should be a human-readable date if a date is given, otherwise "".
- "full_description" should be a cleaned, readable summary of the role (3–8 short paragraphs
  or bullet lines). Fix obvious typos but keep the meaning faithful.
- If both an application link and a contact email are present, populate both fields.
- If the source text appears to be a scraped web page, ignore navigation/footer/cookie text
  and focus only on the actual job description.
"""

SCHEMA_FIELDS = [
    "job_title",
    "company",
    "location",
    "work_mode",
    "job_type",
    "eligibility",
    "required_skills",
    "preferred_qualifications",
    "application_deadline",
    "application_link",
    "contact_email",
    "full_description",
]


class OpenAIConfigError(RuntimeError):
    """Raised when the OpenAI API key isn't configured."""


def _require_api_key() -> str:
    key = get_openai_api_key()
    if not key:
        raise OpenAIConfigError(
            "OPENAI_API_KEY is not set. Add it to .streamlit/secrets.toml or "
            "set it as an environment variable before running the app."
        )
    return key


def _build_user_prompt(raw_text: str, source_url: str = "") -> str:
    fields_block = "\n".join(f'  "{f}": ""' for f in SCHEMA_FIELDS)
    src = f"\nSource URL (for context only): {source_url}\n" if source_url else ""
    return (
        "Reformat the following raw posting into a JSON object with exactly these keys:\n"
        "{\n" + fields_block + "\n}\n"
        + src
        + "\nRaw posting:\n\"\"\"\n"
        + raw_text.strip()
        + "\n\"\"\""
    )


def standardize_posting(raw_text: str, source_url: str = "") -> dict[str, Any]:
    """Send raw text to OpenAI and parse the structured response."""
    if not raw_text or not raw_text.strip():
        raise ValueError("Raw posting text is empty.")

    client = OpenAI(api_key=_require_api_key())
    response = client.chat.completions.create(
        model=get_openai_model(),
        temperature=0.2,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(raw_text, source_url)},
        ],
    )

    content = response.choices[0].message.content or "{}"
    try:
        data = json.loads(content)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"OpenAI returned non-JSON output: {content[:200]}") from exc

    cleaned: dict[str, Any] = {}
    for field in SCHEMA_FIELDS:
        value = data.get(field, "")
        if isinstance(value, list):
            value = "\n".join(str(v).strip() for v in value if str(v).strip())
        cleaned[field] = (value or "").strip() if isinstance(value, str) else value
    return cleaned
