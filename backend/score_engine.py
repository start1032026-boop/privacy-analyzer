"""
Privacy Score Engine v2
=======================
Combines policy risk, trackers, permissions, retention and user control into 0-100 score.

Weights:
  Policy Risk     : 35%
  Tracker Risk    : 25%
  Permission Risk : 20%
  Retention Risk  : 10%
  User Control    : 10%
"""

HIGH_RISK_PERMISSIONS = [
    "location", "precise location", "contacts", "microphone",
    "camera", "call logs", "sms", "read messages", "record audio",
    "background location", "read contacts", "access fine location"
]

MEDIUM_RISK_PERMISSIONS = [
    "bluetooth", "storage", "read external storage",
    "write external storage", "body sensors", "activity recognition"
]

# Retention penalty map
RETENTION_PENALTIES = {
    "indefinitely": 10,
    "indefinite": 10,
    "forever": 10,
    "not specified": 7,
    "unknown": 7,
    "until account deletion": 3,
    "90 days": 1,
    "30 days": 0,
}

# User control penalty map
USER_CONTROL_PENALTIES = {
    "no": 10,
    "none": 10,
    "limited": 7,
    "partial": 5,
    "yes": 0,
    "full": 0,
    "unknown": 6,
    "not specified": 6,
}


def analyze_permissions(permissions: list) -> dict:
    high = []
    medium = []

    for perm in permissions:
        perm_lower = perm.lower()
        if any(h in perm_lower for h in HIGH_RISK_PERMISSIONS):
            high.append(perm)
        elif any(m in perm_lower for m in MEDIUM_RISK_PERMISSIONS):
            medium.append(perm)

    deduction = min(len(high) * 4 + len(medium) * 2, 20)

    return {
        "high_risk": high,
        "medium_risk": medium,
        "total": len(permissions),
        "deduction": deduction,
    }


def get_retention_penalty(retention: str) -> int:
    if not retention:
        return 7
    r = retention.lower().strip()
    for key, penalty in RETENTION_PENALTIES.items():
        if key in r:
            return penalty
    return 4


def get_user_control_penalty(user_control: str) -> int:
    if not user_control:
        return 6
    u = user_control.lower().strip()
    for key, penalty in USER_CONTROL_PENALTIES.items():
        if key in u:
            return penalty
    return 4


def get_risk_level(score: float) -> str:
    if score >= 70:
        return "LOW"
    elif score >= 45:
        return "MODERATE"
    elif score >= 20:
        return "HIGH"
    return "CRITICAL"


def get_risk_emoji(level: str) -> str:
    return {
        "LOW": "🟢",
        "MODERATE": "🟡",
        "HIGH": "🔴",
        "CRITICAL": "⛔"
    }.get(level, "❓")


def get_grade(score: float) -> str:
    if score >= 80: return "A"
    if score >= 65: return "B"
    if score >= 50: return "C"
    if score >= 35: return "D"
    return "F"


def calculate_privacy_score(
    policy_risk_score: float,
    tracker_data: dict,
    permissions: list,
    data_retention: str = "",
    user_control: str = "",
) -> dict:
    base = 100

    # --- Policy risk (max deduction: 35) ---
    policy_deduction = round((policy_risk_score / 10) * 35)

    # --- Tracker risk (max deduction: 25) ---
    tracker_count = tracker_data.get("tracker_count", 0)
    high_risk_trackers = tracker_data.get("high_risk_trackers", [])
    tracker_deduction = min(tracker_count * 3 + len(high_risk_trackers) * 4, 25)

    # --- Permission risk (max deduction: 20) ---
    perm_analysis = analyze_permissions(permissions)
    perm_deduction = perm_analysis["deduction"]

    # --- Retention penalty (max: 10) ---
    retention_deduction = get_retention_penalty(data_retention)

    # --- User control penalty (max: 10) ---
    control_deduction = get_user_control_penalty(user_control)

    final = max(0, base - policy_deduction - tracker_deduction - perm_deduction - retention_deduction - control_deduction)
    level = get_risk_level(final)

    return {
        "privacy_score": round(final),
        "grade": get_grade(final),
        "risk_level": level,
        "risk_emoji": get_risk_emoji(level),
        "breakdown": {
            "policy_risk": policy_deduction,
            "tracker_risk": tracker_deduction,
            "permission_risk": perm_deduction,
            "retention_risk": retention_deduction,
            "control_risk": control_deduction,
        },
        "permission_analysis": perm_analysis,
        "summary": _build_summary(final, level, tracker_count, perm_analysis, data_retention, user_control),
    }


def _build_summary(score, level, tracker_count, perm_analysis, retention, user_control):
    parts = []
    if tracker_count > 3:
        parts.append(f"{tracker_count} embedded trackers detected")
    if perm_analysis["high_risk"]:
        parts.append(f"{len(perm_analysis['high_risk'])} high-risk permissions")
    if retention and any(w in retention.lower() for w in ["indefinite", "forever", "not specified"]):
        parts.append("data retained indefinitely")
    if user_control and any(w in user_control.lower() for w in ["no", "none", "limited"]):
        parts.append("limited user control over data")
    if score < 40:
        parts.append("serious privacy concerns found in policy")
    if not parts:
        parts.append("no critical issues detected")
    return ". ".join(parts).capitalize() + "."