"""Trend analysis: regression detection and chart rendering."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from trend import find_regressions, render_svg  # noqa: E402


def snap(score, controls):
    return {"run_at": "x", "posture_score": score,
            "controls": [{"control_id": cid, "title": cid, "compliance_rate": rate}
                         for cid, rate in controls]}


def test_no_regressions_with_single_snapshot():
    assert find_regressions([snap(90, [("C01", 1.0)])]) == []


def test_detects_dropped_compliance():
    a = snap(90, [("C01", 1.00), ("C02", 0.90)])
    b = snap(70, [("C01", 0.80), ("C02", 0.95)])
    regs = find_regressions([a, b])
    assert [r.control_id for r in regs] == ["C01"], "only C01 dropped"
    assert regs[0].delta == -0.20


def test_ignores_new_controls():
    a = snap(90, [("C01", 1.0)])
    b = snap(90, [("C01", 1.0), ("C99", 0.10)])
    assert find_regressions([a, b]) == []


def test_renders_svg(tmp_path):
    p = render_svg([snap(80, [("C01", 1.0)]), snap(60, [("C01", 0.5)])], tmp_path / "t.svg")
    svg = p.read_text()
    assert svg.startswith("<svg") and "polyline" in svg
