from .base import Control

DORMANT_DAYS = 45


class DormantPrivilegedAccounts(Control):
    control_id = "C05"
    title = f"Privileged accounts used within {DORMANT_DAYS} days"
    hipaa = "164.308(a)(4)(ii)(B) Access Authorization"
    nist_csf = "PR.AA-05"

    def evaluate(self, env):
        pop = [
            a for a in env.accounts
            if a["enabled"] and any("Admin" in g for g in a["groups"])
        ]
        findings = [
            {
                "account": a["username"],
                "role": a["role"],
                "days_since_last_login": a["days_since_last_login"],
                "issue": "Privileged account dormant - standing access without use",
                "severity": "HIGH",
            }
            for a in pop
            if a["days_since_last_login"] > DORMANT_DAYS
        ]
        return self._result(len(pop), findings)
