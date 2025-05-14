from gigachat import GigaChat
from app.core.config import settings

promt1 = "Сделай подробное описание рецепта на английском, верни только ответ"
promt2 = "Сделай очень краткое описание рецепта на английском своими словами, верни только ответ"


def get_long_description(json_string_recipe: str) -> str:
    with GigaChat(credentials=settings.GIGACHAT_API_KEY, verify_ssl_certs=False, model="GigaChat") as giga:
        response = giga.chat(f"{promt1}: {json_string_recipe}")
        return response.choices[0].message.content.replace("*", "")


def get_short_description(json_string_recipe: str) -> str:
    with GigaChat(credentials=settings.GIGACHAT_API_KEY, verify_ssl_certs=False, model="GigaChat") as giga:
        response = giga.chat(f"{promt2}: {json_string_recipe}")
        return response.choices[0].message.content.replace("*", "")
