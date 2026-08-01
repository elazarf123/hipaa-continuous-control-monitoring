from .base import Control


class PrivilegeCreep(Control):
    control_id = "C03"
    title = "Group membership stays within the approved RBAC matrix"
    hipaa = "164.308(a)(4) Information Access Management"
    nist_csf = "PR.AA-05"

    def evaluate(self, env):
        pop = [a for a in env.accounts if a["enabled"]]
        findings = []
        for a in pop:
            allowed = set(env.rbac.get(a["role"], []))
            extra = sorted(set(a["groups"]) - allowed)
            if extra:
                findings.append(
                    {
                        "account": a["username"],
                        "role": a["role"],
                        "unauthorized_groups": extra,
                        "issue": "Group membership outside approved role definition",
                        "severity": "HIGH" if any("Admin" in g for g in extra) else "MEDIUM",
                    }
                )
        return self._result(len(pop), findings)
