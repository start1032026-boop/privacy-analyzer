import requests
from dotenv import load_dotenv

load_dotenv()

# Known scraper-friendly privacy policy URLs
KNOWN_POLICIES = {
    "facebook": "https://tosdr.org/en/service/182",
    "instagram": "https://tosdr.org/en/service/219",
    "tiktok": "https://tosdr.org/en/service/1448",
    "whatsapp": "https://tosdr.org/en/service/198",
    "snapchat": "https://tosdr.org/en/service/156",
    "twitter": "https://tosdr.org/en/service/195",
    "x": "https://tosdr.org/en/service/195",
    "youtube": "https://tosdr.org/en/service/274",
    "google": "https://tosdr.org/en/service/217",
    "gmail": "https://tosdr.org/en/service/217",
    "shein": "https://www.shein.com/Privacy-Security-Policy-a-282.html",
    "grab": "https://www.grab.com/sg/privacy/",
    "uber": "https://tosdr.org/en/service/237",
    "linkedin": "https://tosdr.org/en/service/513",
    "reddit": "https://tosdr.org/en/service/194",
    "telegram": "https://tosdr.org/en/service/280",
    "spotify": "https://tosdr.org/en/service/225",
    "netflix": "https://tosdr.org/en/service/256",
    "amazon": "https://tosdr.org/en/service/190",
    "pinterest": "https://tosdr.org/en/service/180",
    "discord": "https://tosdr.org/en/service/536",
    "zoom": "https://tosdr.org/en/service/2540",
    "microsoft": "https://tosdr.org/en/service/244",
    "apple": "https://tosdr.org/en/service/158",
    "bereal": "https://bere.al/en/privacy",
    "bumble": "https://tosdr.org/en/service/2507",
    "tinder": "https://tosdr.org/en/service/438",
    "paypal": "https://tosdr.org/en/service/218",
    "cashapp": "https://cash.app/legal/us/en-us/privacy",
    "cash app": "https://cash.app/legal/us/en-us/privacy",
}

# Known Android package IDs — only for apps where Play Store scraper
# returns None as appId (known scraper bug for certain top results)
KNOWN_PACKAGES = {
    "spotify": "com.spotify.music",
    "netflix": "com.netflix.mediaclient",
    "amazon": "com.amazon.mShop.android.shopping",
    "youtube": "com.google.android.youtube",
    "whatsapp": "com.whatsapp",
    "instagram": "com.instagram.android",
    "facebook": "com.facebook.katana",
    "tiktok": "com.zhiliaoapp.musically",
    "snapchat": "com.snapchat.android",
    "twitter": "com.twitter.android",
    "x": "com.twitter.android",
    "telegram": "org.telegram.messenger",
    "discord": "com.discord",
    "reddit": "com.reddit.frontpage",
    "linkedin": "com.linkedin.android",
    "uber": "com.ubercab",
    "pinterest": "com.pinterest",
    "zoom": "us.zoom.videomeetings",
    "shazam": "com.shazam.android",
    "duolingo": "com.duolingo",
    "bumble": "com.bumble.app",
    "tinder": "com.tinder",
    "grab": "com.grabtaxi.passenger",
    "brave": "com.brave.browser",
    "firefox": "org.mozilla.firefox",
    "opera": "com.opera.browser",
    "signal": "org.thoughtcrime.securesms",
    "protonmail": "ch.protonmail.android",
    "duckduckgo": "com.duckduckgo.mobile.android",
}


def is_valid_policy_url(url: str) -> bool:
    """Check if a URL looks like a real privacy policy page."""
    if not url:
        return False
    invalid_patterns = ["/mobile", "/download", "/app", "/home", "/login", "/signup", "/register"]
    clean = url.rstrip("/").lower()
    has_privacy_word = any(w in clean for w in ["privacy", "policy", "legal", "terms", "tosdr"])
    is_homepage = clean in [
        "https://www.facebook.com", "https://facebook.com",
        "https://www.instagram.com", "https://instagram.com",
        "https://www.tiktok.com", "https://tiktok.com",
    ]
    has_invalid = any(p in clean for p in invalid_patterns)
    return has_privacy_word and not is_homepage and not has_invalid


def find_privacy_policy_url(app_name: str) -> str:
    """Auto-search for an app's privacy policy URL using DuckDuckGo."""
    try:
        query = f"{app_name} app privacy policy"
        resp = requests.get(
            "https://api.duckduckgo.com/",
            params={
                "q": query,
                "format": "json",
                "no_redirect": "1",
                "no_html": "1",
                "skip_disambig": "1"
            },
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        data = resp.json()

        if data.get("AbstractURL"):
            url = data["AbstractURL"]
            if is_valid_policy_url(url):
                return url

        for topic in data.get("RelatedTopics", [])[:5]:
            url = topic.get("FirstURL", "")
            if any(w in url.lower() for w in ["privacy", "legal", "policy"]):
                return url

        return ""
    except Exception as e:
        print(f"Policy search error: {e}")
        return ""


def search_privacy_policy(app_name: str) -> str:
    """Try multiple strategies to find a privacy policy URL."""

    # Strategy 1 — DuckDuckGo instant answers
    url = find_privacy_policy_url(app_name)
    if url:
        return url

    # Strategy 2 — Common URL patterns
    slug = app_name.lower().replace(" ", "")
    candidates = [
        f"https://www.{slug}.com/privacy",
        f"https://www.{slug}.com/privacy-policy",
        f"https://www.{slug}.com/legal/privacy",
        f"https://{slug}.com/privacy",
        f"https://{slug}.com/privacy-policy",
        f"https://www.{slug}.com/legal",
    ]
    for candidate in candidates:
        try:
            resp = requests.head(
                candidate, timeout=5, allow_redirects=True,
                headers={"User-Agent": "Mozilla/5.0"}
            )
            if resp.status_code == 200:
                print(f"Found via pattern: {candidate}")
                return candidate
        except:
            continue

    return ""


def get_play_store_data(app_name: str):
    """Search Google Play Store for an app and return its details."""
    try:
        from google_play_scraper import search, app as get_app

        results = search(app_name, n_hits=3, lang="en", country="us")
        if not results:
            return None

        # Find first result with a valid appId
        app_id = None
        for r in results:
            if r.get("appId"):
                app_id = r["appId"]
                break

        if not app_id:
            print(f"Play Store search returned no valid appId for: {app_name}")
            return None

        details = get_app(app_id, lang="en", country="us")

        return {
            "source": "playstore",
            "app_id": app_id,
            "name": details.get("title", app_name),
            "developer": details.get("developer", "Unknown"),
            "installs": details.get("installs", "Unknown"),
            "rating": round(details.get("score", 0), 1),
            "privacy_policy_url": details.get("privacyPolicy", ""),
            "permissions": details.get("permissions", []),
            "icon": details.get("icon", ""),
            "description": details.get("description", "")[:500],
            "category": details.get("genre", "Unknown"),
        }
    except Exception as e:
        print(f"Play Store lookup error: {e}")
        return None


def get_itunes_data(app_name: str):
    """Search Apple App Store (iTunes API) for an app."""
    try:
        resp = requests.get(
            "https://itunes.apple.com/search",
            params={"term": app_name, "entity": "software", "limit": 1},
            timeout=10,
        )
        data = resp.json()
        if not data.get("results"):
            return None

        app = data["results"][0]
        return {
            "source": "appstore",
            "app_id": str(app.get("trackId", "")),
            "name": app.get("trackName", app_name),
            "developer": app.get("artistName", "Unknown"),
            "installs": "N/A",
            "rating": round(app.get("averageUserRating", 0), 1),
            "privacy_policy_url": app.get("sellerUrl", ""),
            "permissions": [],
            "icon": app.get("artworkUrl100", ""),
            "description": app.get("description", "")[:500],
            "category": app.get("primaryGenreName", "Unknown"),
        }
    except Exception as e:
        print(f"App Store lookup error: {e}")
        return None


def lookup_app(app_name: str):
    """Try Play Store first, fall back to App Store, then auto-search."""
    data = get_play_store_data(app_name)
    if not data:
        data = get_itunes_data(app_name)

    key = app_name.lower().strip()

    # Priority 1 — hardcoded known policies (most reliable)
    if key in KNOWN_POLICIES:
        if data:
            data["privacy_policy_url"] = KNOWN_POLICIES[key]
        else:
            data = {
                "source": "known",
                "app_id": key,
                "name": app_name.title(),
                "developer": "Unknown",
                "installs": "N/A",
                "rating": 0,
                "privacy_policy_url": KNOWN_POLICIES[key],
                "permissions": [],
                "icon": "",
                "description": "",
                "category": "App",
            }

    # Priority 2 — use store URL if valid
    elif data and is_valid_policy_url(data.get("privacy_policy_url", "")):
        pass  # already has a good URL

    # Priority 3 — auto-search for policy URL
    else:
        print(f"Auto-searching policy URL for: {app_name}")
        found_url = search_privacy_policy(app_name)
        if found_url:
            print(f"Found policy URL: {found_url}")
            if data:
                data["privacy_policy_url"] = found_url
            else:
                data = {
                    "source": "searched",
                    "app_id": key,
                    "name": app_name.title(),
                    "developer": "Unknown",
                    "installs": "N/A",
                    "rating": 0,
                    "privacy_policy_url": found_url,
                    "permissions": [],
                    "icon": "",
                    "description": "",
                    "category": "App",
                }

    # Always inject known Android package ID if available
    # This fixes google_play_scraper returning None appId for some apps
    if data and key in KNOWN_PACKAGES:
        data["android_package_id"] = KNOWN_PACKAGES[key]
        # If app_id is missing or wrong, fix it and mark as playstore
        if not data.get("app_id") or data.get("source") != "playstore":
            data["app_id"] = KNOWN_PACKAGES[key]
            data["source"] = "playstore"

    return data