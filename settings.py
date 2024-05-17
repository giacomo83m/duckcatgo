from cat.mad_hatter.decorators import plugin
from pydantic import BaseModel, field_validator
from pycountry import languages


class DuckGoSettings(BaseModel):
    max_bytes_scraped: int = 1024*12
    lang_code: str = "en"

    @field_validator("max_bytes_scraped")
    @classmethod
    def max_bytes_scraped_validator(cls, max_bytes):
        min_limit = 256
        max_limit = 1024*128
        if max_bytes < min_limit or max_bytes > max_limit:
            raise ValueError("The maximum buffer size used by scraper needs to be between {min_limit} and {max_limit}. Adjustthis value according the context size of the llm model you are using")

    @field_validator("lang_code")
    @classmethod
    def langcode_validator(cls, code):
        try:
            languages.get(alpha_2=code.lower())
        except:
            raise ValueError("Please select a valid ISO 639-1 language code (en, es, fr, it, ..)")
                


@plugin
def settings_model():
    return DuckGoSettings
