"""Control framework: every control returns the same shaped result.

Keeping one result shape is what makes the evidence pack, the scoring, and the
trend analysis possible without special-casing each control.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any


@dataclass
class ControlResult:
    control_id: str
    title: str
    hipaa: str                 # HIPAA Security Rule citation
    nist_csf: str              # NIST CSF 2.0 subcategory
    evaluated: int             # population size the control examined
    failures: int              # how many items failed
    findings: list[dict[str, Any]] = field(default_factory=list)
    threshold_warn: float = 0.98   # >= this compliance rate -> PASS
    threshold_fail: float = 0.90   # >= this -> WARN, below -> FAIL

    @property
    def compliance_rate(self) -> float:
        if self.evaluated == 0:
            return 1.0
        return round((self.evaluated - self.failures) / self.evaluated, 4)

    @property
    def status(self) -> str:
        rate = self.compliance_rate
        if rate >= self.threshold_warn:
            return "PASS"
        if rate >= self.threshold_fail:
            return "WARN"
        return "FAIL"

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["compliance_rate"] = self.compliance_rate
        d["status"] = self.status
        return d


class Control:
    """Base class. Subclasses implement evaluate(env) -> ControlResult."""

    control_id: str = "C00"
    title: str = "unnamed control"
    hipaa: str = ""
    nist_csf: str = ""

    def evaluate(self, env) -> ControlResult:  # pragma: no cover - interface
        raise NotImplementedError

    def _result(self, evaluated: int, findings: list[dict]) -> ControlResult:
        return ControlResult(
            control_id=self.control_id,
            title=self.title,
            hipaa=self.hipaa,
            nist_csf=self.nist_csf,
            evaluated=evaluated,
            failures=len(findings),
            findings=findings,
        )
