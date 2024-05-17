from cat.mad_hatter.decorators import tool
from cat.looking_glass.stray_cat import StrayCat
from cat.log import log
from duckduckgo_search import DDGS
from .scraper import webscrape
from json import loads as json_parse
from typing import List, Dict

@tool(examples=["GOOG stocks", "What is Meta stock price?"])
def duck_stocks(company: str, cat: StrayCat) -> str:
    """What is the stock price of company? The input is a company name or its stock symbol"""
    with DDGS() as ddg:
        query: str = f"{company} stock price"
        results: List[Dict] = ddg.text(query, region="us", max_results=1)
        text: str = ""
        for result in results:
            href: str = result.get('href', '')
            log.info(f"webscraping {href}")
            text: str = webscrape(href)
        if not text:
            return f"I don't have access to the current stock price of {company}"
        return f"Please extract from this text the stock price of {company} and its trend. Text:\n{text}"

@tool(examples=["Can you search for the next music events in Milan?", "Can you find me a good movie on netflix?"])
def duck_search(query: str, cat: StrayCat) -> str:
    """Search for answers. The input is a query"""
    with DDGS() as ddg:
        pages: List[str] = []
        for result in ddg.text(query, region="us", max_results=3):
            href: str = result.get('href', '')
            log.info(f"webscraping {href}")
            body = webscrape(href)
            llm_text_eval = cat.llm(f"this is the content i scraped from a webpage, please clean up all the page artifacts and return me onlythe relevant and meaningful content of this page. I need also to know if this content is enough to answer to the question: {query}. The output MUST be only a json object with two keys, relevant_text(str) and is_enough(bool).\ncontent:\n {body}")
            log.info(f"eval result: {llm_text_eval}")
            llm_eval = json_parse(llm_text_eval)
            pages.append(llm_eval.get("relevant_text", ''))
            if llm_eval.get("is_enough", False) == True:
                break
        text: str = '\n'.join(pages)
        # trunc the results to 12k bytes to fit the models
        text = text[:1024*12]
        return f"Please summarize the most important information about {query} from the text found online:\n{text}"

@tool(examples=["BBC website"])
def duck_website(entity: str, cat: StrayCat) -> str:
    """what is the website of that entity?. The input is an entity"""
    with DDGS() as ddg:
        sections: List[str] = []
        for result in ddg.text(entity, region="us", max_results=3):
            title = result.get('title', '')
            href = result.get('href', '')
            body = result.get('body', '')
            sections.append(f"{title}\n{href}\n{body}\n\n")
        text: str = '\n'.join(sections)
        # trunc the results to 12k bytes to fit the models
        text = text[:1024*12]
        return f"Websites related to {entity}: \n{text}"
