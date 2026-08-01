"""Grading tests. Implement the stubs in src/controls until these pass.

    pytest tests/            # everything
    pytest tests/ -k c03     # just one control
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from controls import (  # noqa: E402
    AuditLogCoverage, DormantPrivilegedAccounts, MFACoverage,
    OrphanedAccounts, PrivilegeCreep, StaleCredentials,
)
from environment import Environment  # noqa: E402


def account(**kw):
    base = dict(
        username="test01", role="Registered Nurse", department="Emergency",
        groups=["Clinical-Staff", "EHR-Read", "EHR-Write"], enabled=True,
        hr_status="ACTIVE", termination_date=None, days_since_termination=None,
        mfa_enabled=True, ephi_access=True, password_age_days=10,
        days_since_last_login=1,
    )
    base.update(kw)
    return base


def env_with(accounts, **kw):
    e = Environment(accounts=accounts)
    e.rbac = {"Registered Nurse": ["Clinical-Staff", "EHR-Read", "EHR-Write"]}
    for k, v in kw.items():
        setattr(e, k, v)
    return e


# ---------------------------------------------------------------- C01 (given)
def test_c01_flags_missing_mfa():
    env = env_with([account(username="a"), account(username="b", mfa_enabled=False)])
    r = MFACoverage().evaluate(env)
    assert r.evaluated == 2
    assert r.failures == 1
    assert r.findings[0]["account"] == "b"


# ---------------------------------------------------------------- C02
def test_c02_flags_terminated_but_enabled():
    env = env_with([
        account(username="ok", hr_status="ACTIVE"),
        account(username="disabled_ok", hr_status="TERMINATED", enabled=False),
        account(username="orphan", hr_status="TERMINATED", enabled=True,
                days_since_termination=30, termination_date="2026-06-01"),
    ])
    r = OrphanedAccounts().evaluate(env)
    assert r.evaluated == 3, "population is every account"
    assert r.failures == 1
    f = r.findings[0]
    assert f["account"] == "orphan"
    assert f["severity"] == "CRITICAL"
    assert f["days_enabled_after_termination"] == 30


# ---------------------------------------------------------------- C03
def test_c03_flags_groups_outside_rbac():
    env = env_with([
        account(username="clean"),
        account(username="creep", groups=["Clinical-Staff", "EHR-Read", "EHR-Write", "Revenue-Cycle"]),
        account(username="admin_creep", groups=["Clinical-Staff", "Domain-Admin"]),
    ])
    r = PrivilegeCreep().evaluate(env)
    assert r.failures == 2
    by = {f["account"]: f for f in r.findings}
    assert by["creep"]["unauthorized_groups"] == ["Revenue-Cycle"]
    assert by["creep"]["severity"] == "MEDIUM"
    assert by["admin_creep"]["severity"] == "HIGH", "Admin groups are HIGH severity"


def test_c03_ignores_disabled_accounts():
    env = env_with([account(username="off", enabled=False, groups=["Domain-Admin"])])
    r = PrivilegeCreep().evaluate(env)
    assert r.evaluated == 0 and r.failures == 0


# ---------------------------------------------------------------- C04
def test_c04_flags_old_passwords():
    env = env_with([
        account(username="fresh", password_age_days=89),
        account(username="stale", password_age_days=91),
    ])
    r = StaleCredentials().evaluate(env)
    assert r.failures == 1
    assert r.findings[0]["account"] == "stale"
    assert r.findings[0]["password_age_days"] == 91


# ---------------------------------------------------------------- C05
def test_c05_population_is_admins_only():
    env = env_with([
        account(username="nurse", days_since_last_login=200),                 # not admin
        account(username="admin_active", groups=["EHR-Admin"], days_since_last_login=10),
        account(username="admin_dormant", groups=["Domain-Admin"], days_since_last_login=60),
    ])
    r = DormantPrivilegedAccounts().evaluate(env)
    assert r.evaluated == 2, "only privileged accounts are in scope"
    assert r.failures == 1
    assert r.findings[0]["account"] == "admin_dormant"


# ---------------------------------------------------------------- C06
def test_c06_flags_missing_log_days():
    env = env_with(
        [],
        log_expectations=[("EHR", "2026-07-01"), ("PACS", "2026-07-01"), ("PACS", "2026-07-02")],
        log_days_seen={("EHR", "2026-07-01"), ("PACS", "2026-07-01")},
    )
    r = AuditLogCoverage().evaluate(env)
    assert r.evaluated == 3
    assert r.failures == 1
    assert r.findings[0]["system"] == "PACS"
    assert r.findings[0]["date"] == "2026-07-02"


# ---------------------------------------------------------------- framework
def test_status_thresholds():
    env = env_with([account(username=f"u{i}") for i in range(100)])
    r = MFACoverage().evaluate(env)
    assert r.status == "PASS" and r.compliance_rate == 1.0
