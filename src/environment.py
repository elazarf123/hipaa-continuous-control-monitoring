"""Synthetic clinic environment. No real identities, credentials, or PHI.

Seeded so every run is reproducible - important for a control-monitoring tool,
because you want posture changes to come from the controls, not from randomness.
"""
from __future__ import annotations

import random
from dataclasses import dataclass, field
from datetime import date, timedelta

RBAC = {
    "Registered Nurse":      ["Clinical-Staff", "EHR-Read", "EHR-Write"],
    "Physician":             ["Clinical-Staff", "EHR-Read", "EHR-Write", "Orders-Entry"],
    "Billing Specialist":    ["Revenue-Cycle", "Claims-Read", "Claims-Write"],
    "Front Desk":            ["Scheduling", "Demographics-Write"],
    "IT Support":            ["Helpdesk", "Workstation-Admin"],
    "Security Analyst":      ["Security-Ops", "Log-Read"],
    "Lab Technician":        ["Lab-Systems", "EHR-Read"],
}
EPHI_SYSTEMS = ["EHR", "PACS", "LIS", "Billing"]
FIRST = ["Ava", "Miguel", "Priya", "Jordan", "Chen", "Nia", "Omar", "Lena", "Ruth", "Diego"]
LAST = ["Alvarez", "Bennett", "Okafor", "Reyes", "Nakamura", "Silva", "Hassan", "Doyle"]


@dataclass
class Environment:
    accounts: list[dict] = field(default_factory=list)
    rbac: dict[str, list[str]] = field(default_factory=lambda: dict(RBAC))
    log_expectations: list[tuple[str, str]] = field(default_factory=list)
    log_days_seen: set[tuple[str, str]] = field(default_factory=set)


def build_environment(seed: int = 42, n_accounts: int = 80, window_days: int = 14) -> Environment:
    rng = random.Random(seed)
    env = Environment()
    roles = list(RBAC)

    for i in range(n_accounts):
        role = rng.choice(roles)
        username = f"{rng.choice(FIRST)[0].lower()}{rng.choice(LAST).lower()}{i:02d}"
        groups = list(RBAC[role])

        # planted: privilege creep on ~12% of accounts
        if rng.random() < 0.12:
            groups.append(rng.choice(["Domain-Admin", "EHR-Admin", "Revenue-Cycle", "Log-Read"]))

        hr_status = "TERMINATED" if rng.random() < 0.09 else "ACTIVE"
        days_since_term = rng.randint(1, 120) if hr_status == "TERMINATED" else None
        # planted: some terminated accounts never got disabled
        enabled = True if hr_status == "ACTIVE" else rng.random() < 0.45

        env.accounts.append(
            {
                "username": username,
                "role": role,
                "department": rng.choice(["Emergency", "Oncology", "Radiology", "Billing", "IT"]),
                "groups": groups,
                "enabled": enabled,
                "hr_status": hr_status,
                "termination_date": (
                    str(date.today() - timedelta(days=days_since_term)) if days_since_term else None
                ),
                "days_since_termination": days_since_term,
                "mfa_enabled": rng.random() > 0.14,          # planted: ~14% missing MFA
                "ephi_access": "EHR-Read" in groups or "Claims-Read" in groups,
                "password_age_days": rng.choice([12, 30, 61, 88, 95, 140, 210]),
                "days_since_last_login": rng.randint(0, 120),
            }
        )

    # audit-log coverage: every ePHI system should log every day in the window
    for d in range(window_days):
        day = str(date.today() - timedelta(days=d))
        for system in EPHI_SYSTEMS:
            env.log_expectations.append((system, day))
            # planted: PACS drops out for a few days
            if system == "PACS" and d in (3, 4, 5):
                continue
            env.log_days_seen.add((system, day))

    return env
