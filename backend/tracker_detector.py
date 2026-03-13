import requests
import re
from bs4 import BeautifulSoup

# Known tracker SDKs to detect from Play Store page content
KNOWN_TRACKERS = {
    "adjust": {"category": "analytics", "high_risk": True},
    "appsflyer": {"category": "analytics", "high_risk": True},
    "branch": {"category": "analytics", "high_risk": True},
    "kochava": {"category": "analytics", "high_risk": False},
    "singular": {"category": "analytics", "high_risk": False},
    "firebase": {"category": "analytics", "high_risk": False},
    "google analytics": {"category": "analytics", "high_risk": False},
    "mixpanel": {"category": "analytics", "high_risk": False},
    "amplitude": {"category": "analytics", "high_risk": False},
    "segment": {"category": "analytics", "high_risk": False},
    "admob": {"category": "advertising", "high_risk": True},
    "doubleclick": {"category": "advertising", "high_risk": True},
    "mopub": {"category": "advertising", "high_risk": True},
    "unity ads": {"category": "advertising", "high_risk": True},
    "unity": {"category": "advertising", "high_risk": True},
    "ironsource": {"category": "advertising", "high_risk": True},
    "chartboost": {"category": "advertising", "high_risk": True},
    "applovin": {"category": "advertising", "high_risk": True},
    "vungle": {"category": "advertising", "high_risk": False},
    "inmobi": {"category": "advertising", "high_risk": False},
    "facebook": {"category": "social", "high_risk": True},
    "meta": {"category": "social", "high_risk": True},
    "twitter": {"category": "social", "high_risk": False},
    "snapchat": {"category": "social", "high_risk": False},
    "crashlytics": {"category": "crash_reporting", "high_risk": True},
    "sentry": {"category": "crash_reporting", "high_risk": False},
    "bugsnag": {"category": "crash_reporting", "high_risk": False},
    "instabug": {"category": "crash_reporting", "high_risk": False},
    "foursquare": {"category": "location", "high_risk": True},
    "safegraph": {"category": "location", "high_risk": True},
    "x-mode": {"category": "location", "high_risk": True},
    "moat": {"category": "fingerprinting", "high_risk": True},
    "comscore": {"category": "fingerprinting", "high_risk": False},
}


def scrape_play_store(package_id: str) -> dict:
    """Scrape Google Play Store page for tracker and permission info."""
    try:
        url = f"https://play.google.com/store/apps/details?id={package_id}&hl=en"
        resp = requests.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"},
            timeout=10
        )
        if resp.status_code != 200:
            return {}

        text = resp.text

        # Detect trackers by scanning page text
        found_trackers = []
        seen = set()
        for tracker_name, meta in KNOWN_TRACKERS.items():
            if tracker_name.lower() in text.lower() and tracker_name not in seen:
                seen.add(tracker_name)
                found_trackers.append({
                    "name": tracker_name.title(),
                    "category": meta["category"],
                    "high_risk": meta["high_risk"],
                    "website": "",
                })

        # Extract permissions from page source
        perms_found = re.findall(r'android\.permission\.([A-Z_]+)', text)
        perms_found = list(set(perms_found))

        # Extract data safety section text
        soup = BeautifulSoup(text, "html.parser")
        data_safety_items = []
        for div in soup.find_all("div"):
            txt = div.get_text(strip=True)
            if txt and 10 < len(txt) < 200:
                lower = txt.lower()
                if any(w in lower for w in ["location", "contacts", "microphone", "camera", "storage", "bluetooth", "personal", "financial", "health"]):
                    data_safety_items.append(txt)

        # Extract version
        version_match = re.search(r'Current Version.*?([0-9][0-9a-zA-Z._-]+)', text)
        version = version_match.group(1) if version_match else "Unknown"

        return {
            "trackers_raw": found_trackers,
            "permissions_raw": perms_found,
            "data_safety": list(set(data_safety_items))[:20],
            "version": version,
        }

    except Exception as e:
        print(f"Play Store scrape error: {e}")
        return {}


def get_trackers(package_name: str) -> dict:
    """Fetch tracker data using a known package ID."""
    print(f"Scraping Play Store for package: {package_name}")
    return _build_tracker_data(package_name)


def get_trackers_by_name(app_name: str) -> dict:
    """Search for trackers by app name — no hardcoded package IDs."""

    # Strategy 1 — get real package IDs from Play Store search
    try:
        from google_play_scraper import search
        print(f"Searching Play Store for: {app_name}")
        results = search(app_name, n_hits=5, lang="en", country="us")
        for r in results:
            pkg = r.get("appId", "")
            if not pkg:
                continue
            print(f"Trying package: {pkg}")
            result = _build_tracker_data(pkg)
            if result["tracker_count"] > 0 or result["permission_count"] > 0:
                return result
    except Exception as e:
        print(f"Play Store search error: {e}")

    # Strategy 2 — common package patterns
    slug = app_name.lower().replace(" ", "").replace("-", "")
    candidates = [
        f"com.{slug}.music",
        f"com.{slug}.android",
        f"com.{slug}.browser",
        f"com.{slug}.app",
        f"com.{slug}",
        f"org.{slug}",
        f"io.{slug}",
    ]
    for candidate in candidates:
        print(f"Trying pattern: {candidate}")
        result = _build_tracker_data(candidate)
        if result["tracker_count"] > 0 or result["permission_count"] > 0:
            print(f"Found via pattern: {candidate}")
            return result

    print(f"No tracker data found for: {app_name}")
    return _empty()


def _build_tracker_data(package_id: str) -> dict:
    """Build full tracker data from Play Store scrape."""
    scraped = scrape_play_store(package_id)
    if not scraped:
        return _empty()

    tracker_details = scraped.get("trackers_raw", [])
    tracker_names = [t["name"] for t in tracker_details]
    high_risk = [t["name"] for t in tracker_details if t["high_risk"]]

    category_counts = {}
    for t in tracker_details:
        cat = t["category"]
        category_counts[cat] = category_counts.get(cat, 0) + 1

    raw_perms = scraped.get("permissions_raw", [])
    permissions = [f"android.permission.{p}" for p in raw_perms]

    # Infer permissions if none found directly
    if not permissions:
        data_safety = scraped.get("data_safety", [])
        permissions = _infer_permissions(data_safety, tracker_details)

    return {
        "trackers": tracker_names,
        "tracker_details": tracker_details,
        "tracker_count": len(tracker_names),
        "high_risk_trackers": high_risk,
        "permissions": permissions,
        "permission_count": len(permissions),
        "version": scraped.get("version", "Unknown"),
        "category_counts": category_counts,
        "exodus_url": f"https://reports.exodus-privacy.eu.org/en/search/?q={package_id}",
        "package_name": package_id,
        "source": "playstore_scrape",
    }


def _infer_permissions(data_safety: list, trackers: list) -> list:
    """Infer permissions from data safety text and tracker types."""
    inferred = set()
    safety_text = " ".join(data_safety).lower()

    if "location" in safety_text:
        inferred.add("android.permission.ACCESS_FINE_LOCATION")
    if "contacts" in safety_text:
        inferred.add("android.permission.READ_CONTACTS")
    if "microphone" in safety_text or "audio" in safety_text:
        inferred.add("android.permission.RECORD_AUDIO")
    if "camera" in safety_text or "photo" in safety_text:
        inferred.add("android.permission.CAMERA")
    if "storage" in safety_text or "files" in safety_text:
        inferred.add("android.permission.READ_EXTERNAL_STORAGE")
    if "bluetooth" in safety_text:
        inferred.add("android.permission.BLUETOOTH")

    for t in trackers:
        cat = t.get("category", "")
        if cat in ["advertising", "analytics"]:
            inferred.add("android.permission.INTERNET")
            inferred.add("com.google.android.gms.permission.AD_ID")
        if cat == "location":
            inferred.add("android.permission.ACCESS_FINE_LOCATION")

    return list(inferred)


def _empty() -> dict:
    return {
        "trackers": [],
        "tracker_details": [],
        "tracker_count": 0,
        "high_risk_trackers": [],
        "permissions": [],
        "permission_count": 0,
        "version": "Unknown",
        "category_counts": {},
        "exodus_url": "",
        "package_name": "",
        "source": "none",
    }


def get_tracker_risk_score(tracker_data: dict) -> int:
    count = tracker_data.get("tracker_count", 0)
    high_risk = len(tracker_data.get("high_risk_trackers", []))
    deduction = min(count * 3, 20) + min(high_risk * 5, 15)
    return deduction