# Code walkthrough

Study notes for this repository. If you are going to present this project, you should be
able to answer every question below without opening the file.

## Module map

| Module | Responsibility |
|---|---|
| `src/environment.py` | Builds the seeded synthetic clinic (accounts, HR status, groups, logs) |
| `src/controls/base.py` | `Control` base class + `ControlResult` — the shared contract |
| `src/controls/c0*.py` | One module per control; each returns a `ControlResult` |
| `src/exceptions.py` | Risk-exception register with mandatory expiry |
| `src/trend.py` | Snapshot history, regression detection, dependency-free SVG chart |
| `src/run_monitor.py` | Orchestrates: evaluate, suppress, score, persist, report |

## Design decisions, and why

**Every control returns the same `ControlResult`.** Scoring, the evidence pack, and the
trend chart never branch on which control produced a result. Adding a seventh control
requires changing zero downstream code — that is the payoff of a stable interface.

**`compliance_rate` and `status` are `@property`, not stored fields.** They are derived
from `evaluated` and `failures`. Storing them would let them drift out of sync with the
numbers they came from. Store source values, compute derived ones.

**Population is chosen per control, deliberately.** `compliance_rate` divides by
population, so the denominator *is* the analytical decision. C05 scans only accounts
holding an Admin group — if it scanned all 80, a serious dormant-admin problem would show
as ~90% compliant instead of 45%. Explaining that choice is worth more than the loop.

**Grading on a rate, not pass/fail.** One orphaned account out of 500 is an exception to
chase; fifty is a broken process. Thresholds (98% PASS / 90% WARN) tell those apart.

**`set` in C06 and C03.** `(system, date) in some_list` rescans the list — O(n). A set
lookup is O(1). At 4 systems x 14 days it is irrelevant; at 200 systems x 365 days it is
the whole runtime. C03 uses set difference because "held but not approved" *is* a set
difference — matching the data structure to the question.

**Exceptions carry a mandatory expiry.** `Exception_.from_dict` raises `ValueError` if
`expires_on` is missing. An accepted risk with no end date is an unfixed finding with
better paperwork. Expired entries stop suppressing automatically and are reported.

**Exceptions are scoped to a control.** An exception for C01 must not silently suppress a
C04 finding for the same account. There is a test for exactly this.

**SVG is hand-written instead of matplotlib.** Keeps the project dependency-free, makes CI
faster, and the output diffs cleanly in git instead of being an opaque binary blob.

**`@dataclass(frozen=True)` on `Exception_`.** An approved exception should not be mutated
after loading; freezing makes that a language guarantee rather than a convention.

## Python features used

dataclasses (`@dataclass`, `frozen=True`, `field(default_factory=...)`) · properties ·
class inheritance with a template method · list/dict comprehensions · generator
expressions with `any()` · set operations and membership testing · `pathlib` · `json` ·
`datetime.date` arithmetic and ISO parsing · type hints including `X | None` · raising
`ValueError` for validation · `pytest` fixtures (`tmp_path`) and `pytest.raises`

## Questions you should be able to answer

1. Why does C05's population exclude non-admin accounts, and what breaks if it does not?
2. What happens on the run after an exception expires, and where is that handled?
3. Why is `ControlResult.status` a property instead of being set in `__init__`?
4. How would you add a seventh control? Which files change? (One new module and one line
   in `controls/__init__.py`. Nothing else.)
5. Why is the environment seeded, and what would break in trend analysis if it were not?
6. Where would this design struggle at 50,000 accounts, and what would you change?

Question 6 is the one senior interviewers ask. Honest answer: everything is in memory and
each control re-scans the full account list, so it is O(controls x accounts). At 50k you
would stream from a database and push filtering into SQL, or evaluate all controls in a
single pass. Say that — do not pretend the design scales unchanged.

## Where to extend next

- **A seventh control** — shared/generic accounts, or a directory/HR department mismatch.
- **Severity-weighted scoring** — one CRITICAL should outweigh ten MEDIUMs.
- **Per-department posture** — same data, grouped differently; a natural pandas exercise.
