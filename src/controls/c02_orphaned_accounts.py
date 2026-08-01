from .base import Control


class OrphanedAccounts(Control):
    control_id = "C02"
    title = "Accounts disabled promptly on termination"
    hipaa = "164.308(a)(3)(ii)(C) Termination Procedures"
    nist_csf = "PR.AA-01"

    def evaluate(self, env):
        pop = env.accounts
        findings = [
            {
                "account": a["username"],
                "role": a["role"],
                "terminated_on": a["termination_date"],
                "days_enabled_after_termination": a["days_since_termination"],
                "issue": "Terminated worker's account still enabled",
                "severity": "CRITICAL",
            }
            for a in pop
            if a["hr_status"] == "TERMINATED" and a["enabled"]
        ]
        return self._result(len(pop), findings)
