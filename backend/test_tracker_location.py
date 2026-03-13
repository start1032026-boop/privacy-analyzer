import requests
import re
from bs4 import BeautifulSoup

package_id = "com.spotify.music"

resp = requests.get(
    f"https://play.google.com/store/apps/details?id={package_id}&hl=en",
    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"},
    timeout=10
)

text = resp.text

# Check where exactly each tracker keyword appears
trackers_to_check = ["adjust", "facebook", "unity", "meta", "twitter", "snapchat", "firebase", "crashlytics"]

for kw in trackers_to_check:
    positions = [m.start() for m in re.finditer(kw, text.lower())]
    print(f"\n'{kw}' found {len(positions)} times:")
    for pos in positions[:3]:
        # Show 100 chars before and after
        snippet = text[max(0, pos-80):pos+80].replace('\n', ' ').strip()
        print(f"  ...{snippet}...")

# Also check if there's a specific "About this app" or developer section
print("\n\n=== LOOKING FOR APP-SPECIFIC SECTIONS ===")
soup = BeautifulSoup(text, "html.parser")

# Find script tags with JSON data (Play Store embeds app data as JSON)
scripts = soup.find_all("script")
for s in scripts:
    content = s.string or ""
    if "adjust" in content.lower() or "firebase" in content.lower():
        print("Found tracker in script tag!")
        # Find the relevant part
        for kw in ["adjust", "firebase"]:
            idx = content.lower().find(kw)
            if idx != -1:
                print(f"  {kw}: ...{content[max(0,idx-50):idx+100]}...")
        break