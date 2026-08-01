# Control catalog

Each control maps to a HIPAA Security Rule citation and a NIST CSF 2.0 subcategory.
Mapping matters: an auditor does not want "we check MFA," they want the citation the
check satisfies and the evidence it produced.

| ID | Control | HIPAA Security Rule | NIST CSF 2.0 | Population | Severity |
|---|---|---|---|---|---|
| C01 | MFA on ePHI-access accounts | 164.312(d) Person or Entity Authentication | PR.AA-03 | Enabled accounts with ePHI access | HIGH |
| C02 | Accounts disabled on termination | 164.308(a)(3)(ii)(C) Termination Procedures | PR.AA-01 | All accounts | CRITICAL |
| C03 | Group membership within RBAC | 164.308(a)(4) Information Access Management | PR.AA-05 | Enabled accounts | HIGH / MEDIUM |
| C04 | Password rotation within 90 days | 164.308(a)(5)(ii)(D) Password Management | PR.AA-01 | Enabled accounts | MEDIUM |
| C05 | Privileged accounts not dormant | 164.308(a)(4)(ii)(B) Access Authorization | PR.AA-05 | Enabled admin accounts | HIGH |
| C06 | Audit log coverage on ePHI systems | 164.312(b) Audit Controls | DE.CM-09 | Expected (system, day) pairs | HIGH |

## Scoring

Each control yields a compliance rate = `(population - failures) / population`.

| Rate | Status | Weight |
|---|---|---|
| >= 98% | PASS | 1.0 |
| >= 90% | WARN | 0.5 |
| < 90% | FAIL | 0.0 |

Posture score = mean of the control weights, expressed as a percentage. It is a blunt
instrument on purpose - it exists to show *direction over time*, not to be precise.

## Why thresholds instead of pass/fail

A single orphaned account out of 500 is a finding, not a broken control. Grading on a
rate lets the tool distinguish "one exception to chase" from "this control isn't working."
