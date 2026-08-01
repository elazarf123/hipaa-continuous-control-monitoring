from .c01_mfa_coverage import MFACoverage
from .c02_orphaned_accounts import OrphanedAccounts
from .c03_privilege_creep import PrivilegeCreep
from .c04_stale_credentials import StaleCredentials
from .c05_dormant_privileged import DormantPrivilegedAccounts
from .c06_audit_log_coverage import AuditLogCoverage

ALL_CONTROLS = [
    MFACoverage(),
    OrphanedAccounts(),
    PrivilegeCreep(),
    StaleCredentials(),
    DormantPrivilegedAccounts(),
    AuditLogCoverage(),
]
