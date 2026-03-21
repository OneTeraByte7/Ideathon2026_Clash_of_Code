"""
Risk Engine — Asclepius AI
Computes sepsis risk score (0–100) using:
  - qSOFA (bedside: BP, RR, altered mentation proxy)
  - Weighted vital sign deviations from normal ranges
  - Trend penalty (worsening over sliding window)
"""
from dataclasses import dataclass
from typing import List


@dataclass
class VitalReading:
    heart_rate: float
    systolic_bp: float
    respiratory_rate: float
    temperature: float
    spo2: float
    lactate: float


@dataclass
class RiskResult:
    risk_score: float           # 0–100
    risk_level: str             # normal | warning | critical
    qsofa_score: int            # 0–3
    sofa_partial: float         # partial SOFA from available vitals
    contributing_factors: list[str]
    trend_penalty: float        # extra points for worsening trend


# ── Normal ranges ──────────────────────────────────────────────────────────────
NORMAL = {
    "heart_rate": (60, 90),
    "systolic_bp": (100, 140),
    "respiratory_rate": (12, 20),
    "temperature": (36.0, 38.0),
    "spo2": (95, 100),
    "lactate": (0.5, 2.0),
}

# ── Weights (sum to 100 at maximum deviation) ──────────────────────────────────
WEIGHTS = {
    "lactate": 22,          # Best early biomarker
    "systolic_bp": 20,      # qSOFA criterion, hemodynamic
    "respiratory_rate": 18, # qSOFA criterion, early warning
    "heart_rate": 16,       # SIRS criterion
    "temperature": 12,      # Infection indicator
    "spo2": 12,             # Respiratory compromise
}


def _compute_qsofa(v: VitalReading) -> tuple[int, list[str]]:
    score = 0
    factors = []
    if v.systolic_bp <= 100:
        score += 1
        factors.append(f"Low SBP ({v.systolic_bp} mmHg)")
    if v.respiratory_rate >= 22:
        score += 1
        factors.append(f"High RR ({v.respiratory_rate} breaths/min)")
    # Proxy for altered mentation: not directly measurable via vitals,
    # but SpO2 <90 strongly suggests it
    if v.spo2 < 90:
        score += 1
        factors.append(f"Very low SpO2 ({v.spo2}%) — possible altered mentation")
    return score, factors


def _vital_deviation_score(v: VitalReading) -> tuple[float, list[str]]:
    """
    Score each vital using clinical severity tiers (mild / moderate / severe).
    Each tier yields 0.33 / 0.66 / 1.0 of the metric's max weight.
    """
    total = 0.0
    factors = []

    def tier_score(value, normal_low, normal_high, warn_low, warn_high, crit_low, crit_high,
                   metric_name, unit) -> float:
        if normal_low <= value <= normal_high:
            return 0.0
        if (warn_low is not None and value <= warn_low) or (warn_high is not None and value >= warn_high):
            sev = 0.66
        elif (crit_low is not None and value <= crit_low) or (crit_high is not None and value >= crit_high):
            sev = 1.0
        else:
            sev = 0.33
        direction = "Low" if value < normal_low else "High"
        factors.append(f"{direction} {metric_name} ({value}{unit})")
        return sev

    scores = {
        # metric: tier_score(value, norm_lo, norm_hi, warn_lo, warn_hi, crit_lo, crit_hi)
        "heart_rate": tier_score(
            v.heart_rate, 60, 90,
            warn_low=None, warn_high=100,
            crit_low=None, crit_high=110,
            metric_name="HR", unit="bpm"
        ),
        "systolic_bp": tier_score(
            v.systolic_bp, 100, 140,
            warn_low=105, warn_high=None,
            crit_low=90, crit_high=None,
            metric_name="SBP", unit="mmHg"
        ),
        "respiratory_rate": tier_score(
            v.respiratory_rate, 12, 20,
            warn_low=None, warn_high=22,
            crit_low=None, crit_high=26,
            metric_name="RR", unit="br/min"
        ),
        "temperature": tier_score(
            v.temperature, 36.0, 38.0,
            warn_low=35.5, warn_high=38.3,
            crit_low=35.0, crit_high=39.0,
            metric_name="Temp", unit="°C"
        ),
        "spo2": tier_score(
            v.spo2, 95, 100,
            warn_low=92, warn_high=None,
            crit_low=88, crit_high=None,
            metric_name="SpO2", unit="%"
        ),
        "lactate": tier_score(
            v.lactate, 0.5, 2.0,
            warn_low=None, warn_high=2.2,
            crit_low=None, crit_high=4.0,
            metric_name="Lactate", unit="mmol/L"
        ),
    }

    for metric, sev in scores.items():
        total += sev * WEIGHTS[metric]

    return min(total, 100.0), factors


def _trend_penalty(history: List[VitalReading]) -> float:
    """
    Extra risk points if vitals are consistently worsening.
    Looks at last 3 readings. Returns 0–15 penalty.
    """
    if len(history) < 3:
        return 0.0

    last3 = history[-3:]
    penalties = 0.0

    def worsening(vals, direction="up"):
        return (vals[0] < vals[1] < vals[2]) if direction == "up" else (vals[0] > vals[1] > vals[2])

    hrs = [r.heart_rate for r in last3]
    if worsening(hrs, "up") and last3[-1].heart_rate > 90:
        penalties += 5.0

    sbps = [r.systolic_bp for r in last3]
    if worsening(sbps, "down") and last3[-1].systolic_bp < 110:
        penalties += 5.0

    lactates = [r.lactate for r in last3]
    if worsening(lactates, "up") and last3[-1].lactate > 1.5:
        penalties += 5.0

    return min(penalties, 15.0)


def compute_risk(current: VitalReading, history: List[VitalReading] | None = None) -> RiskResult:
    """Main entry point. Returns RiskResult with 0–100 score."""
    history = history or []

    qsofa, qsofa_factors = _compute_qsofa(current)
    base_score, vital_factors = _vital_deviation_score(current)

    # qSOFA multiplier: each point adds 10 base points
    qsofa_bonus = qsofa * 10

    trend = _trend_penalty(history + [current])

    raw = base_score + qsofa_bonus + trend
    risk_score = round(min(raw, 100.0), 1)

    if risk_score >= 70:
        level = "critical"
    elif risk_score >= 40:
        level = "warning"
    else:
        level = "normal"

    # Partial SOFA from vitals we have (respiratory + cardiovascular proxies)
    sofa_partial = (
        (1 if current.spo2 < 94 else 0) +         # Respiratory
        (1 if current.systolic_bp < 100 else 0) +  # Cardiovascular
        (1 if current.lactate > 2.0 else 0)         # Coagulation proxy
    )

    return RiskResult(
        risk_score=risk_score,
        risk_level=level,
        qsofa_score=qsofa,
        sofa_partial=sofa_partial,
        contributing_factors=list(dict.fromkeys(qsofa_factors + vital_factors)),
        trend_penalty=trend,
    )