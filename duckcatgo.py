from cat.mad_hatter.decorators import tool
from cat.looking_glass.stray_cat import StrayCat
from cat.log import log
from duckduckgo_search import DDGS
from json import loads, JSONDecodeError
from typing import List, Dict, Any, Tuple
from .settings import DuckGoSettings
from .scraper import webscrape


def json_parse(input_str: str) -> Tuple[Dict[str, Any], bool]:
    try:
        result_dict = loads(input_str)
        return result_dict, True
    except JSONDecodeError:
        return {}, False


@tool(examples=["Can you search for the next music events in Milan?", "Can you find me a good movie on Netflix?"])
def duckcat_search(query: str, cat: StrayCat) -> str:
    """
    Useful for searching online information that can change over
    time, like upcoming events, prices, values, ages, rates,
    weather, addresses, road conditions, breaking news, and
    means of transportation. For example, a user may inquire,
    "What is the current value of a bitcon." The "query" argument is the
    input text submitted to a search engine.
    """
    settings: DuckGoSettings = cat.mad_hatter.get_plugin().load_settings()
    pages: List[str] = []
    language_code = settings.get("lang_code", "en")
    max_bytes = settings.get("max_bytes_scraped", 8192)

    with DDGS() as ddg:
        for result in ddg.text(query, region=language_code, max_results=3):
            href: str = result.get("href", "")
            log.info(f"webscraping {href}")
            body = webscrape(href, cat)
            llm_request = (
                f"This is the content I scraped from a webpage, please clean up all the page artifacts "
                f"and return only the relevant and meaningful content of this page. I also need to know if "
                f"this content is sufficient to answer the question: {query}. The output must be only a JSON object "
                f"with two keys: 'relevant_text' (str) and 'is_enough' (bool).\ncontent:\n{body}"
            )
            llm_text_eval = cat.llm(llm_request)
            eval_result, success = json_parse(llm_text_eval)
            if not success:
                log.info(f"error parsing llm result: {llm_text_eval}")
                continue
            if "relevant_text" not in eval_result or "is_enough" not in eval_result:
                log.info(f"eval_results is missing relevant_text or is_enough keys: {eval_result}")
                continue
            pages.append(eval_result.get("relevant_text", ''))
            if eval_result.get("is_enough", False):
                break

        combined_text = "\n".join(pages)[:max_bytes]
        return (
            f"Please summarize the most important information about {query} from the text found online: "
            f"\n{combined_text}"
        )


@tool(examples=["BBC website"])
def duckcat_website(entity: str, cat: StrayCat) -> str:
    """
    Retrieves the website associated with a specified entity.
    The 'entity' parameter refers to the name or identifier of the
    entity for which the website needs to be found.
    """
    settings = cat.mad_hatter.get_plugin().load_settings()
    language_code = settings.get("lang_code", "en")
    max_bytes = settings.get("max_bytes_scraped", 8192)

    with DDGS() as ddg:
        sections: List[str] = []
        for result in ddg.text(entity, region=language_code, max_results=5):
            title = result.get('title', '')
            href = result.get('href', '')
            body = result.get('body', '')
            sections.append(f"{title}\n{href}\n{body}\n\n")
        combined_text = "\n".join(sections)[:max_bytes]
        return f"Websites related to {entity}: \n{combined_text}"
