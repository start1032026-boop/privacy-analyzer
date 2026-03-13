import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def analyze_policy(policy_text):

    prompt = f"""
You are a privacy risk analyst.

Analyze this section of a privacy policy.

Return ONLY JSON with no extra text or markdown:

{{
  "risk_score": number (1-10),
  "red_flags": ["", "", ""],
  "worst_case": ""
}}

Policy section:
{policy_text}
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=500
    )

    result = response.choices[0].message.content
    print("MODEL OUTPUT:", result)

    try:
        return json.loads(result)
    except json.JSONDecodeError:
        return {
            "risk_score": 0,
            "red_flags": ["Failed to parse response"],
            "worst_case": result
        }


