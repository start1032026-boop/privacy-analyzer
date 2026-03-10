import requests
from bs4 import BeautifulSoup

def fetch_policy(url):

    response = requests.get(url)

    soup = BeautifulSoup(response.text, "html.parser")

    text = soup.get_text(separator=" ", strip=True)

    return text[:8000]