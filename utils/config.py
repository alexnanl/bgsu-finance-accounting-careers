"""Centralized access to secrets and config values.

Reads from `st.secrets` (Streamlit secrets.toml) first, then environment
variables. Never hard-codes secrets.
"""
from __future__ import annotations

import os

try:
    import streamlit as st
except ImportError:
    st = None  # type: ignore


def get_secret(key: str, default: str | None = None) -> str | None:
    if st is not None:
        try:
            if key in st.secrets:
                return str(st.secrets[key])
        except Exception:
            pass
    return os.environ.get(key, default)


def get_openai_api_key() -> str | None:
    return get_secret("OPENAI_API_KEY")


def get_openai_model() -> str:
    return get_secret("OPENAI_MODEL") or "gpt-4o-mini"


def get_admin_password() -> str | None:
    """Returns the admin password from secrets, or None if unset."""
    return get_secret("ADMIN_PASSWORD")
