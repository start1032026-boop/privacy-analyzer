# Tracker category classification
TRACKER_CATEGORIES = {
    "analytics": [
        "google analytics", "firebase", "mixpanel", "amplitude", "segment",
        "appsflyer", "adjust", "branch", "kochava", "singular", "heap",
        "localytics", "flurry", "clevertap", "braze", "moengage"
    ],
    "advertising": [
        "admob", "google ads", "facebook ads", "meta ads", "mopub",
        "unity ads", "ironsource", "chartboost", "vungle", "applovin",
        "inmobi", "doubleclick", "dfp", "appnexus", "criteo", "taboola"
    ],
    "crash_reporting": [
        "crashlytics", "sentry", "bugsnag", "acra", "instabug",
        "firebase crashlytics", "raygun", "rollbar"
    ],
    "social": [
        "facebook sdk", "meta sdk", "twitter sdk", "snapchat sdk",
        "tiktok sdk", "linkedin sdk", "pinterest sdk"
    ],
    "location": [
        "foursquare", "factual", "safegraph", "x-mode", "placer.ai"
    ],
    "fingerprinting": [
        "moat", "integral ad science", "doubleverify", "comscore", "nielsen"
    ],
}

HIGH_RISK_SDKS = [
    "facebook", "meta", "tiktok", "doubleclick", "crashlytics",
    "appsflyer", "adjust", "branch", "mopub", "admob",
    "unity ads", "ironsource", "chartboost", "applovin", "foursquare",
    "safegraph", "x-mode", "moat"
]


def classify_sdk(name: str) -> str:
    """Classify an SDK into a category."""
    n = name.lower()
    for category, keywords in TRACKER_CATEGORIES.items():
        if any(k in n for k in keywords):
            return category
    return "other"


def is_high_risk_sdk(name: str) -> bool:
    """Check if an SDK is high risk."""
    n = name.lower()
    return any(h in n for h in HIGH_RISK_SDKS)


def build_tracker_data_from_sdks(sdk_list: list) -> dict:
    """Build a tracker_data dict from LLM-extracted SDK names."""
    if not sdk_list:
        return None

    tracker_details = []
    tracker_names = []
    high_risk = []
    seen = set()

    for sdk in sdk_list:
        if not sdk or sdk.lower() in seen:
            continue
        seen.add(sdk.lower())

        category = classify_sdk(sdk)
        is_high = is_high_risk_sdk(sdk)
        if is_high:
            high_risk.append(sdk)

        tracker_names.append(sdk)
        tracker_details.append({
            "name": sdk,
            "category": category,
            "high_risk": is_high,
            "website": "",
        })

    category_counts = {}
    for td in tracker_details:
        cat = td["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1

    return {
        "trackers": tracker_names,
        "tracker_details": tracker_details,
        "tracker_count": len(tracker_names),
        "high_risk_trackers": high_risk,
        "permissions": [],
        "permission_count": 0,
        "version": "Unknown",
        "category_counts": category_counts,
        "exodus_url": "",
        "package_name": "",
        "source": "llm_extracted",
    }


def combine_results(results: list) -> dict:
    scores = []
    red_flags = []
    worst_cases = []
    data_shared = set()
    retention_notes = []
    user_controls = []
    transparency_scores = []
    all_sdks = []

    for r in results:
        try:
            scores.append(float(r.get("risk_score", 5)))
            red_flags.extend(r.get("red_flags", []))
            if r.get("worst_case"):
                worst_cases.append(r["worst_case"])
            data_shared.update(r.get("data_shared_with", []))
            if r.get("data_retention"):
                retention_notes.append(r["data_retention"])
            if r.get("user_control"):
                user_controls.append(r["user_control"])
            if r.get("transparency_score"):
                transparency_scores.append(float(r["transparency_score"]))
            # Collect SDKs from all chunks
            sdks = r.get("third_party_sdks", [])
            if sdks:
                all_sdks.extend(sdks)
        except Exception as e:
            print("Parsing error:", e)

    avg_score = round(sum(scores) / len(scores), 1) if scores else 5.0
    avg_transparency = round(sum(transparency_scores) / len(transparency_scores), 1) if transparency_scores else 5.0

    # Deduplicate red flags
    seen = set()
    unique_flags = []
    for f in red_flags:
        if f.lower() not in seen:
            seen.add(f.lower())
            unique_flags.append(f)

    # Deduplicate SDKs
    seen_sdks = set()
    unique_sdks = []
    for sdk in all_sdks:
        if sdk and sdk.lower() not in seen_sdks:
            seen_sdks.add(sdk.lower())
            unique_sdks.append(sdk)

    return {
        "final_risk_score": avg_score,
        "top_red_flags": unique_flags[:5],
        "worst_case": worst_cases[0] if worst_cases else "",
        "data_shared_with": list(data_shared)[:6],
        "data_retention": retention_notes[0] if retention_notes else "Not specified",
        "user_control": user_controls[0] if user_controls else "Not specified",
        "transparency_score": avg_transparency,
        "third_party_sdks": unique_sdks,
    }