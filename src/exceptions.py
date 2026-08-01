"""Risk-exception register.

Real GRC tooling has to answer: "we know about that one, it's accepted until March."
An exception suppresses a specific finding for a specific control until it expires.
Expired exceptions stop suppressing automatically - that is the whole point, and it is
why the expiry date is mandatory rather than optional.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class Exception_:
    control_id: str
    subject: str          # account username, or "SYSTEM|DATE" for log controls
    reason: str
    approved_by: str
    expires_on: date

    @property
    def expired(self) -> bool:
        return date.today() > self.expires_on

    @classmethod
    def from_dict(cls, d: dict) -> "Exception_":
        missing = {"control_id", "subject", "reason", "approved_by", "expires_on"} - d.keys()
        if missing:
            raise ValueError(f"exception missing required field(s): {sorted(missing)}")
        return cls(
            control_id=d["control_id"],
            subject=d["subject"],
            reason=d["reason"],
            approved_by=d["approved_by"],
            expires_on=date.fromisoformat(d["expires_on"]),
        )


class ExceptionRegister:
    """Loads exceptions and decides whether a given finding is suppressed."""

    def __init__(self, exceptions: list[Exception_] | None = None) -> None:
        self._by_control: dict[str, set[str]] = {}
        self.expired: list[Exception_] = []
        self.active: list[Exception_] = []
        for exc in exceptions or []:
            if exc.expired:
                self.expired.append(exc)
                continue
            self.active.append(exc)
            self._by_control.setdefault(exc.control_id, set()).add(exc.subject)

    @classmethod
    def load(cls, path: str | Path) -> "ExceptionRegister":
        p = Path(path)
        if not p.exists():
            return cls([])
        raw = json.loads(p.read_text(encoding="utf-8"))
        return cls([Exception_.from_dict(d) for d in raw.get("exceptions", [])])

    @staticmethod
    def subject_of(finding: dict) -> str:
        """Stable identifier for a finding, whichever control produced it."""
        if "account" in finding:
            return finding["account"]
        if "system" in finding and "date" in finding:
            return f"{finding['system']}|{finding['date']}"
        return json.dumps(finding, sort_keys=True)

    def is_suppressed(self, control_id: str, finding: dict) -> bool:
        return self.subject_of(finding) in self._by_control.get(control_id, set())

    def apply(self, result) -> int:
        """Drop suppressed findings from a ControlResult. Returns how many were removed."""
        kept = [f for f in result.findings if not self.is_suppressed(result.control_id, f)]
        removed = len(result.findings) - len(kept)
        result.findings = kept
        result.failures = len(kept)
        return removed
