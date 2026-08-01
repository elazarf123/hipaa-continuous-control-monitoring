from .base import Control


class MFACoverage(Control):
    control_id = "C01"
    title = "Multi-factor authentication enabled on all accounts with ePHI access"
    hipaa = "164.312(d) Person or Entity Authentication"
    nist_csf = "PR.AA-03"

    def evaluate(self, env):
        pop = [a for a in env.accounts if a["enabled"] and a["ephi_access"]]
        findings = [
            {
                "account": a["username"],
                "role": a["role"],
                "department": a["department"],
                "issue": "ePHI-access account without MFA",
                "severity": "HIGH",
            }
            for a in pop
            if not a["mfa_enabled"]
        ]
        return self._result(len(pop), findings)
