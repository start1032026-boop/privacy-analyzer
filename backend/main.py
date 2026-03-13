from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from policy_fetcher import fetch_policy
from text_chunker import split_text
from llm_analyzer import analyze_policy
from risk_utils import combine_results, build_tracker_data_from_sdks
from app_lookup import lookup_app, KNOWN_POLICIES
from tracker_detector import get_trackers, get_trackers_by_name
from score_engine import calculate_privacy_score

app = FastAPI(title="PrivacyLens API", version="2.2")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class RequestData(BaseModel):
    url: Optional[str] = None
    app_name: Optional[str] = None


@app.post("/analyze")
def analyze(data: RequestData):
    app_info = None
    tracker_data = {
        "trackers": [], "tracker_details": [], "tracker_count": 0,
        "high_risk_trackers": [], "permissions": [], "permission_count": 0,
        "version": "Unknown", "category_counts": {}, "exodus_url": "",
        "package_name": "", "source": "none"
    }
    permissions = []
    policy_url = data.url

    # --- App name lookup ---
    if data.app_name:
        app_info = lookup_app(data.app_name)

        if app_info:
            permissions = app_info.get("permissions", [])
            app_key = data.app_name.strip()

            # Use android_package_id first (from KNOWN_PACKAGES),
            # then app_id if source is playstore
            android_package = app_info.get("android_package_id", "")
            play_package = app_info.get("app_id", "") if app_info.get("source") == "playstore" else ""
            package_id = android_package or play_package

            if package_id:
                print(f"Fetching trackers via package: {package_id}")
                tracker_data = get_trackers(package_id)
            else:
                print(f"Fetching trackers by name: {app_key}")
                tracker_data = get_trackers_by_name(app_key)

            if not policy_url:
                policy_url = app_info.get("privacy_policy_url", "")

        # Last resort — check KNOWN_POLICIES directly
        if not policy_url:
            key = data.app_name.lower().strip()
            policy_url = KNOWN_POLICIES.get(key, "")
            if policy_url and not app_info:
                app_info = {
                    "source": "known",
                    "app_id": key,
                    "name": data.app_name.title(),
                    "developer": "Unknown",
                    "installs": "N/A",
                    "rating": 0,
                    "privacy_policy_url": policy_url,
                    "permissions": [],
                    "icon": "",
                    "description": "",
                    "category": "App",
                }

    if not policy_url:
        raise HTTPException(
            status_code=400,
            detail=f"Could not find privacy policy for '{data.app_name}'. Try using the Policy URL tab instead."
        )

    # --- Policy analysis ---
    try:
        policy_text = fetch_policy(policy_url)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not fetch policy: {str(e)}")

    chunks = split_text(policy_text)
    results = []
    for chunk in chunks[:3]:
        result = analyze_policy(chunk)
        results.append(result)

    combined = combine_results(results)

    # --- Use LLM-extracted SDKs as tracker data if Play Store gave nothing ---
    llm_sdks = combined.get("third_party_sdks", [])
    if tracker_data["tracker_count"] == 0 and llm_sdks:
        print(f"Using LLM-extracted SDKs as tracker data: {llm_sdks}")
        llm_tracker_data = build_tracker_data_from_sdks(llm_sdks)
        if llm_tracker_data:
            tracker_data = llm_tracker_data

    # --- Unified score ---
    score_data = calculate_privacy_score(
        policy_risk_score=combined["final_risk_score"],
        tracker_data=tracker_data,
        permissions=permissions,
        data_retention=combined.get("data_retention", ""),
        user_control=combined.get("user_control", ""),
    )

    return {
        "app_info": app_info,
        **combined,
        "trackers": tracker_data,
        **score_data,
    }


@app.get("/health")
def health():
    return {"status": "ok", "version": "2.2"}