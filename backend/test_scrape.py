import requests
import re
from bs4 import BeautifulSoup

resp = requests.get(
    'https://play.google.com/store/apps/details?id=com.spotify.music&hl=en',
    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'},
    timeout=10
)

text = resp.text

# Look for Android permissions
perms = re.findall(r'android\.permission\.[A-Z_]+', text)
perms = list(set(perms))
print('Permissions found:', len(perms))
for p in perms[:20]:
    print(' -', p)

# Look for tracker SDKs in the page
tracker_keywords = [
    'firebase', 'crashlytics', 'adjust', 'appsflyer', 'branch',
    'admob', 'facebook', 'amplitude', 'mixpanel', 'segment',
    'mopub', 'unity', 'ironsource', 'chartboost', 'applovin'
]
print('\nTracker keywords found in page:')
for kw in tracker_keywords:
    if kw.lower() in text.lower():
        print(f' - {kw}')

# Look for data safety section
if 'Data safety' in text or 'data safety' in text.lower():
    print('\nData safety section found!')
    idx = text.lower().find('data safety')
    print(text[idx:idx+500])