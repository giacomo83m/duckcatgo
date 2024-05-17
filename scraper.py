import requests
import re
from bs4 import BeautifulSoup
from cat.log import log

def webscrape(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            return re.sub(r'\n+', '\n', text)
        else:
            log.warning(f"Error retriving content {url}: http code {response.status_code}")
    except Exception as e:
        log.warning(f"Error contacting {url}: {str(e)}")
    return ""
