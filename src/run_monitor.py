"""Run every control, score the posture, write a timestamped snapshot + evidence pack."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from controls import ALL_CONTROLS          # noqa: E402
from environment import build_environment  # noqa: E402
from exceptions import ExceptionRegister   # noqa: E402
from trend import find_regressions, load_snapshots, render_svg  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history"
OUTPUT = ROOT / "output"
STATUS_WEIGHT = {"PASS": 1.0, "WARN": 0.5, "FAIL": 0.0}


def main() -> int:
    HISTORY.mkdir(exist_ok=True)
    OUTPUT.mkdir(exist_ok=True)

    env = build_environment()
    results = [c.evaluate(env) for c in ALL_CONTROLS]

    register = ExceptionRegister.load(ROOT / "exceptions.json")
    suppressed = sum(register.apply(r) for r in results)

    posture = round(sum(STATUS_WEIGHT[r.status] for r in results) / len(results) * 100, 1)
    stamp = datetime.now(timezone.utc)

    snapshot = {
        "run_at": stamp.isoformat(timespec="seconds"),
        "posture_score": posture,
        "controls": [r.to_dict() for r in results],
    }

    snap_path = HISTORY / f"{stamp.strftime('%Y-%m-%dT%H%M%S')}.json"
    snap_path.write_text(json.dumps(snapshot, indent=2), encoding="utf-8")

    _write_evidence_pack(snapshot)

    if register.expired:
        print(f"NOTE: {len(register.expired)} exception(s) have expired and no longer suppress findings.")
    print(f"Posture score: {posture}%  ({suppressed} finding(s) suppressed by active exceptions)")
    for r in results:
        print(f"  [{r.status:4}] {r.control_id}  {r.compliance_rate:>7.1%}  "
              f"{r.failures} finding(s)  {r.title}")
    print(f"\nSnapshot: {snap_path.relative_to(ROOT)}")

    snapshots = load_snapshots()
    render_svg(snapshots, OUTPUT / "posture_trend.svg")
    for r in find_regressions(snapshots):
        print(f"REGRESSION  {r.control_id}  {r.previous:.1%} -> {r.current:.1%} ({r.delta:+.1%})")
    return 0


def _write_evidence_pack(snapshot: dict) -> None:
    lines = [
        "# HIPAA Continuous Control Monitoring - Evidence Pack",
        "",
        f"**Run:** {snapshot['run_at']}  ",
        f"**Posture score:** {snapshot['posture_score']}%",
        "",
        "> Synthetic environment. No real identities, credentials, or PHI.",
        "",
        "| Control | Status | Compliance | Findings | HIPAA | NIST CSF 2.0 |",
        "|---|---|---|---|---|---|",
    ]
    for c in snapshot["controls"]:
        lines.append(
            f"| {c['control_id']} {c['title']} | {c['status']} | "
            f"{c['compliance_rate']:.1%} | {c['failures']} | {c['hipaa']} | {c['nist_csf']} |"
        )

    for c in snapshot["controls"]:
        if not c["findings"]:
            continue
        lines += ["", f"### {c['control_id']} - {c['title']}", ""]
        for f in c["findings"][:10]:
            lines.append(f"- `{f.get('severity','')}` " +
                         ", ".join(f"{k}={v}" for k, v in f.items() if k != "severity"))
        if len(c["findings"]) > 10:
            lines.append(f"- ...and {len(c['findings']) - 10} more")

    (OUTPUT / "evidence_pack.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
