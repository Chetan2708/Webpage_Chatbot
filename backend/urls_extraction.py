import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

DOCUMENTATION_URL = "https://docs.chaicode.com/youtube/getting-started/"
SECTION_ROOT_URL = f"{DOCUMENTATION_URL}/youtube/"
HEADERS = requests.utils.default_headers()
HEADERS['User-Agent'] = os.getenv("USER_AGENT", "WebQueryBot/1.0")

def check_url_status(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False

def extract_valid_links():
    try:
        response = requests.get(DOCUMENTATION_URL, headers=HEADERS)
        response.raise_for_status()
    except requests.RequestException as error:
        print(f"Failed to fetch base page: {error}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    valid_links = set()

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]

        if href.startswith("/youtube/"):
            full_link = urljoin(DOCUMENTATION_URL, href)
            if full_link == SECTION_ROOT_URL:
                continue
            if check_url_status(full_link):
                valid_links.add(full_link)

    return sorted(valid_links)
