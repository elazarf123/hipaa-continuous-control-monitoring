from .base import Control


class AuditLogCoverage(Control):
    control_id = "C06"
    title = "ePHI systems emit audit logs every day in the review window"
    hipaa = "164.312(b) Audit Controls"
    nist_csf = "DE.CM-09"

    def evaluate(self, env):
        expected = env.log_expectations          # [(system, date), ...]
        seen = env.log_days_seen                 # {(system, date)}
        findings = [
            {
                "system": system,
                "date": date,
                "issue": "No audit events recorded for an ePHI system on this day",
                "severity": "HIGH",
            }
            for (system, date) in expected
            if (system, date) not in seen
        ]
        return self._result(len(expected), findings)
