"""Fetch and extract readable text from a job posting URL.

Best-effort: many job boards (LinkedIn, Indeed, Handshake) require JavaScript
or block scrapers. When extraction fails or returns little usable text, the
caller should fall back to manual paste.
"""
from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0 Safari/537.36"
)

MIN_USEFUL_LENGTH = 200


class UrlFetchError(RuntimeError):
    pass


def _strip_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "svg"]):
        tag.decompose()
    main = soup.find("main") or soup.find("article") or soup.body or soup
    text = main.get_text("\n")
    lines = [ln.strip() for ln in text.splitlines()]
    text = "\n".join(ln for ln in lines if ln)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def fetch_text_from_url(url: str, timeout: int = 12) -> str:
    """Fetches the URL and returns extracted readable text.

    Raises `UrlFetchError` with a human-friendly message on failure or when
    the extracted text is too short to be useful.
    """
    url = (url or "").strip()
    if not url:
        raise UrlFetchError("Please enter a URL.")
    if not re.match(r"^https?://", url, re.IGNORECASE):
        raise UrlFetchError("URL must start with http:// or https://.")

    try:
        response = requests.get(
            url,
            timeout=timeout,
            headers={"User-Agent": USER_AGENT, "Accept-Language": "en-US,en;q=0.9"},
            allow_redirects=True,
        )
    except requests.exceptions.Timeout as exc:
        raise UrlFetchError("The site took too long to respond.") from exc
    except requests.exceptions.RequestException as exc:
        raise UrlFetchError(f"Could not reach the URL: {exc}") from exc

    if response.status_code >= 400:
        raise UrlFetchError(
            f"The site returned HTTP {response.status_code}. "
            "It may be blocking automated access."
        )

    content_type = (response.headers.get("Content-Type") or "").lower()
    if "html" not in content_type and "text" not in content_type:
        raise UrlFetchError(
            f"Unsupported content type: {content_type or 'unknown'}."
        )

    text = _strip_html(response.text)
    if len(text) < MIN_USEFUL_LENGTH:
        raise UrlFetchError(
            "Could not extract enough readable text from this page. "
            "The site may require JavaScript or login."
        )
    return text
