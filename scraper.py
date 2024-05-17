from bs4 import BeautifulSoup
from cat.log import log
from cat.looking_glass.stray_cat import StrayCat
from re import sub as regex_sub
from requests import get as httpget


def webscrape(url: str, cat: StrayCat) -> str:
    settings = cat.mad_hatter.get_plugin().load_settings()
    headers = {
        'Accept-Language': settings.get("lang_code", "en")
    }
    try:
        response = httpget(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text()
            return regex_sub(r'\n+', '\n', text)
        else:
            log.warning(f"Error retriving content {url}: http code {response.status_code}")
    except Exception as e:
        log.warning(f"Error contacting {url}: {str(e)}")
    return ""
