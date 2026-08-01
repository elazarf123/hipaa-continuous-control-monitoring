"""Posture trend analysis over the snapshot history.

Two questions an auditor actually asks:
  1. Is our posture improving or degrading?
  2. Which specific control regressed, and when?

Chart rendering is hand-written SVG rather than matplotlib, so the whole project stays
dependency-free and the output diffs cleanly in git.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HISTORY = ROOT / "history"
OUTPUT = ROOT / "output"


@dataclass
class Regression:
    control_id: str
    title: str
    previous: float
    current: float

    @property
    def delta(self) -> float:
        return round(self.current - self.previous, 4)


def load_snapshots(history: Path = HISTORY) -> list[dict]:
    """Snapshots in chronological order (filenames are ISO timestamps, so name sort works)."""
    return [
        json.loads(p.read_text(encoding="utf-8"))
        for p in sorted(history.glob("*.json"))
    ]


def find_regressions(snapshots: list[dict]) -> list[Regression]:
    """Controls whose compliance rate dropped between the last two runs."""
    if len(snapshots) < 2:
        return []

    prev = {c["control_id"]: c for c in snapshots[-2]["controls"]}
    curr = {c["control_id"]: c for c in snapshots[-1]["controls"]}

    out = []
    for cid, c in curr.items():
        if cid not in prev:
            continue
        before, after = prev[cid]["compliance_rate"], c["compliance_rate"]
        if after < before:
            out.append(Regression(cid, c["title"], before, after))
    return sorted(out, key=lambda r: r.delta)


def render_svg(snapshots: list[dict], path: Path) -> Path:
    """Minimal line chart of posture score over time. No plotting library."""
    scores = [s["posture_score"] for s in snapshots]
    w, h, pad = 640, 200, 32

    if len(scores) < 2:
        body = ('<text x="320" y="100" text-anchor="middle" fill="#8a9bb5" '
                'font-family="sans-serif" font-size="13">Need at least two runs to plot a trend</text>')
    else:
        step = (w - 2 * pad) / (len(scores) - 1)
        pts = [
            (pad + i * step, h - pad - (v / 100) * (h - 2 * pad))
            for i, v in enumerate(scores)
        ]
        line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        dots = "".join(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" fill="#4a9eff"/>' for x, y in pts
        )
        body = (
            f'<polyline points="{line}" fill="none" stroke="#4a9eff" stroke-width="2"/>{dots}'
            f'<text x="{pad}" y="{h - 8}" fill="#8a9bb5" font-family="sans-serif" '
            f'font-size="11">{len(scores)} runs</text>'
            f'<text x="{w - pad}" y="{h - 8}" text-anchor="end" fill="#8a9bb5" '
            f'font-family="sans-serif" font-size="11">latest {scores[-1]}%</text>'
        )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
        f'<rect width="{w}" height="{h}" fill="#0f1923"/>'
        f'<text x="{pad}" y="20" fill="#e8eaf0" font-family="sans-serif" font-size="13">'
        f'Security posture over time</text>{body}</svg>'
    )
    path.write_text(svg, encoding="utf-8")
    return path


def main() -> int:
    OUTPUT.mkdir(exist_ok=True)
    snapshots = load_snapshots()
    if not snapshots:
        print("No snapshots yet - run src/run_monitor.py first.")
        return 0

    render_svg(snapshots, OUTPUT / "posture_trend.svg")
    regressions = find_regressions(snapshots)

    print(f"Snapshots: {len(snapshots)}  |  latest posture: {snapshots[-1]['posture_score']}%")
    if regressions:
        print("Regressions since previous run:")
        for r in regressions:
            print(f"  {r.control_id}  {r.previous:.1%} -> {r.current:.1%}  ({r.delta:+.1%})  {r.title}")
    else:
        print("No control regressed since the previous run.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
