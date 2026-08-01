"""Exception register: suppression, expiry, and validation."""
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from controls.base import ControlResult  # noqa: E402
from exceptions import Exception_, ExceptionRegister  # noqa: E402


def make_exc(**kw):
    base = dict(
        control_id="C01", subject="jdoe", reason="accepted",
        approved_by="Security Manager", expires_on=date.today() + timedelta(days=30),
    )
    base.update(kw)
    return Exception_(**base)


def result_with(findings, control_id="C01"):
    return ControlResult(
        control_id=control_id, title="t", hipaa="", nist_csf="",
        evaluated=10, failures=len(findings), findings=findings,
    )


def test_active_exception_suppresses_matching_finding():
    reg = ExceptionRegister([make_exc(subject="jdoe")])
    res = result_with([{"account": "jdoe"}, {"account": "asmith"}])
    removed = reg.apply(res)
    assert removed == 1
    assert res.failures == 1
    assert res.findings[0]["account"] == "asmith"


def test_expired_exception_does_not_suppress():
    reg = ExceptionRegister([make_exc(subject="jdoe", expires_on=date.today() - timedelta(days=1))])
    res = result_with([{"account": "jdoe"}])
    assert reg.apply(res) == 0
    assert res.failures == 1
    assert len(reg.expired) == 1


def test_exception_is_scoped_to_its_control():
    reg = ExceptionRegister([make_exc(control_id="C01", subject="jdoe")])
    res = result_with([{"account": "jdoe"}], control_id="C04")
    assert reg.apply(res) == 0, "an exception for C01 must not suppress a C04 finding"


def test_subject_for_log_findings():
    subj = ExceptionRegister.subject_of({"system": "PACS", "date": "2026-07-02"})
    assert subj == "PACS|2026-07-02"


def test_missing_expiry_is_rejected():
    with pytest.raises(ValueError, match="expires_on"):
        Exception_.from_dict({
            "control_id": "C01", "subject": "jdoe",
            "reason": "r", "approved_by": "a",
        })
