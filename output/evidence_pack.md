# HIPAA Continuous Control Monitoring - Evidence Pack

**Run:** 2026-08-01T23:05:51+00:00  
**Posture score:** 33.3%

> Synthetic environment. No real identities, credentials, or PHI.

| Control | Status | Compliance | Findings | HIPAA | NIST CSF 2.0 |
|---|---|---|---|---|---|
| C01 Multi-factor authentication enabled on all accounts with ePHI access | FAIL | 80.5% | 8 | 164.312(d) Person or Entity Authentication | PR.AA-03 |
| C02 Accounts disabled promptly on termination | PASS | 100.0% | 0 | 164.308(a)(3)(ii)(C) Termination Procedures | PR.AA-01 |
| C03 Group membership stays within the approved RBAC matrix | WARN | 90.9% | 7 | 164.308(a)(4) Information Access Management | PR.AA-05 |
| C04 Passwords rotated within 90 days | FAIL | 50.6% | 38 | 164.308(a)(5)(ii)(D) Password Management | PR.AA-01 |
| C05 Privileged accounts used within 45 days | FAIL | 40.0% | 9 | 164.308(a)(4)(ii)(B) Access Authorization | PR.AA-05 |
| C06 ePHI systems emit audit logs every day in the review window | WARN | 94.6% | 3 | 164.312(b) Audit Controls | DE.CM-09 |

### C01 - Multi-factor authentication enabled on all accounts with ePHI access

- `HIGH` account=nnakamura04, role=Billing Specialist, department=IT, issue=ePHI-access account without MFA
- `HIGH` account=jalvarez17, role=Billing Specialist, department=Emergency, issue=ePHI-access account without MFA
- `HIGH` account=mreyes22, role=Billing Specialist, department=IT, issue=ePHI-access account without MFA
- `HIGH` account=mdoyle26, role=Physician, department=Emergency, issue=ePHI-access account without MFA
- `HIGH` account=adoyle34, role=Registered Nurse, department=Emergency, issue=ePHI-access account without MFA
- `HIGH` account=rdoyle38, role=Billing Specialist, department=Emergency, issue=ePHI-access account without MFA
- `HIGH` account=oreyes65, role=Lab Technician, department=Billing, issue=ePHI-access account without MFA
- `HIGH` account=dalvarez74, role=Registered Nurse, department=Radiology, issue=ePHI-access account without MFA

### C03 - Group membership stays within the approved RBAC matrix

- `HIGH` account=mhassan01, role=IT Support, unauthorized_groups=['Domain-Admin'], issue=Group membership outside approved role definition
- `MEDIUM` account=csilva14, role=IT Support, unauthorized_groups=['Log-Read'], issue=Group membership outside approved role definition
- `HIGH` account=oalvarez40, role=Security Analyst, unauthorized_groups=['EHR-Admin'], issue=Group membership outside approved role definition
- `HIGH` account=rdoyle58, role=Lab Technician, unauthorized_groups=['EHR-Admin'], issue=Group membership outside approved role definition
- `HIGH` account=mdoyle69, role=Billing Specialist, unauthorized_groups=['Domain-Admin'], issue=Group membership outside approved role definition
- `HIGH` account=oreyes73, role=Front Desk, unauthorized_groups=['EHR-Admin'], issue=Group membership outside approved role definition
- `MEDIUM` account=odoyle75, role=Registered Nurse, unauthorized_groups=['Revenue-Cycle'], issue=Group membership outside approved role definition

### C04 - Passwords rotated within 90 days

- `MEDIUM` account=malvarez00, role=Security Analyst, password_age_days=140, issue=Password older than 90 days
- `MEDIUM` account=mhassan01, role=IT Support, password_age_days=95, issue=Password older than 90 days
- `MEDIUM` account=csilva05, role=IT Support, password_age_days=210, issue=Password older than 90 days
- `MEDIUM` account=onakamura09, role=Billing Specialist, password_age_days=140, issue=Password older than 90 days
- `MEDIUM` account=osilva11, role=IT Support, password_age_days=210, issue=Password older than 90 days
- `MEDIUM` account=csilva14, role=IT Support, password_age_days=140, issue=Password older than 90 days
- `MEDIUM` account=palvarez16, role=Lab Technician, password_age_days=210, issue=Password older than 90 days
- `MEDIUM` account=rokafor18, role=Registered Nurse, password_age_days=95, issue=Password older than 90 days
- `MEDIUM` account=mreyes22, role=Billing Specialist, password_age_days=95, issue=Password older than 90 days
- `MEDIUM` account=lalvarez24, role=Front Desk, password_age_days=140, issue=Password older than 90 days
- ...and 28 more

### C05 - Privileged accounts used within 45 days

- `HIGH` account=lnakamura13, role=IT Support, days_since_last_login=87, issue=Privileged account dormant - standing access without use
- `HIGH` account=pbennett15, role=IT Support, days_since_last_login=47, issue=Privileged account dormant - standing access without use
- `HIGH` account=oreyes19, role=IT Support, days_since_last_login=85, issue=Privileged account dormant - standing access without use
- `HIGH` account=dalvarez32, role=IT Support, days_since_last_login=119, issue=Privileged account dormant - standing access without use
- `HIGH` account=oalvarez40, role=Security Analyst, days_since_last_login=55, issue=Privileged account dormant - standing access without use
- `HIGH` account=rdoyle58, role=Lab Technician, days_since_last_login=59, issue=Privileged account dormant - standing access without use
- `HIGH` account=abennett67, role=IT Support, days_since_last_login=48, issue=Privileged account dormant - standing access without use
- `HIGH` account=mdoyle69, role=Billing Specialist, days_since_last_login=99, issue=Privileged account dormant - standing access without use
- `HIGH` account=oreyes73, role=Front Desk, days_since_last_login=103, issue=Privileged account dormant - standing access without use

### C06 - ePHI systems emit audit logs every day in the review window

- `HIGH` system=PACS, date=2026-07-29, issue=No audit events recorded for an ePHI system on this day
- `HIGH` system=PACS, date=2026-07-28, issue=No audit events recorded for an ePHI system on this day
- `HIGH` system=PACS, date=2026-07-27, issue=No audit events recorded for an ePHI system on this day
