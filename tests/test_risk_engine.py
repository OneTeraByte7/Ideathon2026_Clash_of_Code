"""
Tests for the Asclepius AI risk scoring engine.
Run: pytest tests/
"""
import pytest
from backend.core.risk_engine import compute_risk, VitalReading


def make_vital(**overrides) -> VitalReading:
    defaults = dict(
        heart_rate=75, systolic_bp=120, respiratory_rate=16,
        temperature=37.0, spo2=98, lactate=1.0
    )
    return VitalReading(**{**defaults, **overrides})


def test_normal_vitals_low_risk():
    result = compute_risk(make_vital())
    assert result.risk_score < 40
    assert result.risk_level == "normal"
    assert result.qsofa_score == 0


def test_critical_vitals_high_risk():
    result = compute_risk(make_vital(
        heart_rate=120, systolic_bp=85, respiratory_rate=30,
        temperature=39.5, spo2=87, lactate=4.5
    ))
    assert result.risk_score >= 70
    assert result.risk_level == "critical"
    assert result.qsofa_score >= 2


def test_warning_vitals_mid_range():
    result = compute_risk(make_vital(
        heart_rate=98, systolic_bp=105, respiratory_rate=22,
        temperature=38.5, spo2=93, lactate=2.2
    ))
    assert 40 <= result.risk_score < 70
    assert result.risk_level == "warning"


def test_qsofa_low_sbp():
    result = compute_risk(make_vital(systolic_bp=95))
    assert result.qsofa_score >= 1


def test_qsofa_high_rr():
    result = compute_risk(make_vital(respiratory_rate=24))
    assert result.qsofa_score >= 1


def test_trend_penalty_applied():
    history = [
        make_vital(heart_rate=85, systolic_bp=115, lactate=1.5),
        make_vital(heart_rate=92, systolic_bp=108, lactate=1.8),
    ]
    worsening = make_vital(heart_rate=102, systolic_bp=100, lactate=2.1)
    result_with_trend = compute_risk(worsening, history)
    result_no_trend = compute_risk(worsening, [])
    assert result_with_trend.risk_score >= result_no_trend.risk_score


def test_high_lactate_alone_raises_score():
    normal_but_high_lactate = make_vital(lactate=4.0)
    result = compute_risk(normal_but_high_lactate)
    assert result.risk_score > 12  # Lactate (weight=22) at critical tier = 14.5


def test_contributing_factors_populated():
    result = compute_risk(make_vital(heart_rate=115, systolic_bp=88))
    assert len(result.contributing_factors) > 0