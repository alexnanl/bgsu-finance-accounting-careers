"""JSON-backed storage for job/internship openings.

The `Storage` class defines the interface the rest of the app uses to
read/write openings. `JsonStorage` is the local prototype backend. To swap to
a cloud database (Supabase, Firebase, Google Sheets, etc.), implement a new
class with the same methods and assign it to the module-level `storage`
singleton at the bottom of this file.
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime
from pathlib import Path
from threading import Lock
from typing import Any

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_DATA_FILE = _DATA_DIR / "openings.json"

OPENING_FIELDS = [
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

VALID_STATUSES = ("Draft", "Active", "Closed")
DEFAULT_STATUS = "Active"


def _now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def _normalize_record(item: dict[str, Any]) -> dict[str, Any]:
    """Defensive normalization for records read from disk."""
    out = dict(item)
    out.setdefault("id", uuid.uuid4().hex[:12])
    out.setdefault("created_at", _now_iso())
    out.setdefault("updated_at", out.get("created_at"))
    out.setdefault("status", DEFAULT_STATUS)
    out.setdefault("raw_text", "")
    out.setdefault("source_url", "")
    for f in OPENING_FIELDS:
        out.setdefault(f, "")
    if out["status"] not in VALID_STATUSES:
        out["status"] = DEFAULT_STATUS
    return out


class JsonStorage:
    """Local JSON-file storage. Single-process safe via threading.Lock."""

    def __init__(self, path: Path = _DATA_FILE) -> None:
        self._path = path
        self._lock = Lock()

    def _ensure_file(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        if not self._path.exists():
            self._path.write_text("[]", encoding="utf-8")

    def _read_all(self) -> list[dict[str, Any]]:
        self._ensure_file()
        try:
            data = json.loads(self._path.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                return []
            return [_normalize_record(d) for d in data if isinstance(d, dict)]
        except json.JSONDecodeError:
            return []

    def _write_all(self, items: list[dict[str, Any]]) -> None:
        self._ensure_file()
        self._path.write_text(
            json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8"
        )

    # ----- public API -----

    def list_openings(
        self,
        statuses: tuple[str, ...] | None = None,
    ) -> list[dict[str, Any]]:
        with self._lock:
            items = self._read_all()
        if statuses:
            items = [i for i in items if i.get("status") in statuses]
        items.sort(key=lambda r: r.get("created_at", ""), reverse=True)
        return items

    def get_opening(self, opening_id: str) -> dict[str, Any] | None:
        with self._lock:
            for item in self._read_all():
                if item.get("id") == opening_id:
                    return item
        return None

    def add_opening(
        self,
        opening: dict[str, Any],
        raw_text: str = "",
        source_url: str = "",
        status: str = DEFAULT_STATUS,
    ) -> dict[str, Any]:
        now = _now_iso()
        record: dict[str, Any] = {
            "id": uuid.uuid4().hex[:12],
            "created_at": now,
            "updated_at": now,
            "status": status if status in VALID_STATUSES else DEFAULT_STATUS,
            "raw_text": raw_text,
            "source_url": source_url,
        }
        for field in OPENING_FIELDS:
            value = opening.get(field, "")
            record[field] = (value or "").strip() if isinstance(value, str) else value

        with self._lock:
            items = self._read_all()
            items.insert(0, record)
            self._write_all(items)
        return record

    def update_opening(
        self,
        opening_id: str,
        updates: dict[str, Any],
    ) -> dict[str, Any] | None:
        with self._lock:
            items = self._read_all()
            for idx, item in enumerate(items):
                if item.get("id") != opening_id:
                    continue
                merged = dict(item)
                for k, v in updates.items():
                    if k in {"id", "created_at"}:
                        continue
                    if k == "status" and v not in VALID_STATUSES:
                        continue
                    merged[k] = (v or "").strip() if isinstance(v, str) else v
                merged["updated_at"] = _now_iso()
                items[idx] = merged
                self._write_all(items)
                return merged
        return None

    def delete_opening(self, opening_id: str) -> bool:
        with self._lock:
            items = self._read_all()
            new_items = [i for i in items if i.get("id") != opening_id]
            if len(new_items) == len(items):
                return False
            self._write_all(new_items)
            return True


# Module-level singleton — swap this assignment to plug in another backend.
storage: JsonStorage = JsonStorage()
