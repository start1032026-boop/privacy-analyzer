import requests
from bs4 import BeautifulSoup


def fetch_policy(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "identity",  # ← KEY FIX: disables compression
        "Connection": "keep-alive",
    }

    session = requests.Session()
    response = session.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    # Force UTF-8 decoding
    response.encoding = "utf-8"
    html = response.text

    soup = BeautifulSoup(html, "html.parser")

    # Remove noise
    for tag in soup(["script", "style", "nav", "footer", "header", "iframe", "noscript"]):
        tag.decompose()

    text = soup.get_text(separator=" ", strip=True)

    # Clean up excessive whitespace
    import re
    text = re.sub(r'\s+', ' ', text).strip()

    if len(text) < 200:
        raise Exception("Page returned insufficient content — site may be blocking scrapers.")

    return text[:10000]