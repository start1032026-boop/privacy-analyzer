import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


def analyze_policy(policy_text: str) -> dict:
    prompt = f"""You are a privacy risk analyst. Analyze this privacy policy section.
You MUST return ONLY a valid JSON object. No markdown, no explanation, no extra text.
The JSON must have exactly these fields:
{{
  "risk_score": <integer 1-10>,
  "red_flags": ["<specific risk 1>", "<specific risk 2>", "<specific risk 3>"],
  "worst_case": "<one sentence worst case for the user>",
  "data_shared_with": ["<company or entity>", "<company or entity>"],
  "data_retention": "<how long data is kept>",
  "user_control": "<can users delete/opt out>",
  "transparency_score": <integer 1-10>,
  "third_party_sdks": ["<any third-party SDK, analytics tool, ad network, or tracking service explicitly mentioned e.g. Google Analytics, Facebook SDK, Adjust, Firebase, Crashlytics, AppsFlyer, Branch, AdMob, Unity Ads, Mixpanel, Amplitude, Segment, Sentry, etc. Only include if explicitly named in the policy.>"]
}}
Policy section:
{policy_text}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=800,
    )
    result = response.choices[0].message.content.strip()
    print("MODEL OUTPUT:", result)

    # Strip markdown fences if present
    result = re.sub(r'^```json\s*', '', result)
    result = re.sub(r'^```\s*', '', result)
    result = re.sub(r'\s*```$', '', result)
    result = result.strip()

    try:
        return json.loads(result)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', result, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
        return {
            "risk_score": 5,
            "red_flags": ["Could not fully parse policy response"],
            "worst_case": result[:200],
            "data_shared_with": [],
            "data_retention": "Unknown",
            "user_control": "Unknown",
            "transparency_score": 5,
            "third_party_sdks": [],
        }