from .base import Control

MAX_PASSWORD_AGE_DAYS = 90


class StaleCredentials(Control):
    control_id = "C04"
    title = f"Passwords rotated within {MAX_PASSWORD_AGE_DAYS} days"
    hipaa = "164.308(a)(5)(ii)(D) Password Management"
    nist_csf = "PR.AA-01"

    def evaluate(self, env):
        pop = [a for a in env.accounts if a["enabled"]]
        findings = [
            {
                "account": a["username"],
                "role": a["role"],
                "password_age_days": a["password_age_days"],
                "issue": f"Password older than {MAX_PASSWORD_AGE_DAYS} days",
                "severity": "MEDIUM",
            }
            for a in pop
            if a["password_age_days"] > MAX_PASSWORD_AGE_DAYS
        ]
        return self._result(len(pop), findings)
