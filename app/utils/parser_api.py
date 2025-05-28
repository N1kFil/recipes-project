import aiohttp
import asyncio
import json
from sberchat import get_short_description
from app.database.crud import RecipeCrud
from app.database.database import get_db

# Словарь с оценочным временем готовки
COOKING_TIMES = {
    "Beef": 90, "Chicken": 45, "Pasta": 20, "Seafood": 25,
    "Vegetarian": 30, "Vegan": 35, "Dessert": 60, "Starter": 15,
    "Breakfast": 10, "Lamb": 120, "Pork": 60, "Side": 25,
    "Miscellaneous": 40
}


async def fetch_random_meal():
    """Асинхронно получает случайный рецепт"""
    url = "https://www.themealdb.com/api/json/v1/1/random.php"
    connector = aiohttp.TCPConnector(ssl=False)  # Отключаем проверку SSL
    async with aiohttp.ClientSession(connector=connector) as session:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data["meals"][0] if data["meals"] else None
            return None


async def get_meal_details():
    """Получает детали рецепта с временем и страной кухни"""
    meal = await fetch_random_meal()
    if not meal:
        return None

    category = meal["strCategory"]
    return {
        "title": meal["strMeal"],
        "category": category,
        "cuisine": meal["strArea"],
        "image_url": meal["strMealThumb"],  # Добавляем URL изображения
        "cooking_time": COOKING_TIMES.get(category, COOKING_TIMES["Miscellaneous"]),
        "ingredients": await extract_ingredients(meal),
        "instructions": meal["strInstructions"]
    }


async def extract_ingredients(meal):
    """Асинхронно извлекает ингредиенты"""
    ingredients = []
    for i in range(1, 21):
        ingredient = meal.get(f"strIngredient{i}")
        measure = meal.get(f"strMeasure{i}")
        if ingredient and ingredient.strip():
            ingredients.append(f"{measure.strip()} {ingredient.strip()}")
    return ingredients


def make_meal_details(meal):
    """Выводит полную информацию о блюде"""
    s = f"""Title: {meal['title']}
Country: {meal['cuisine']}
Category: {meal['category']}
Time cooking: {meal['cooking_time']} minutes

Ingredients:
{"\n".join(item for item in meal["ingredients"])}

Instructions:
{meal["instructions"]}
""".strip()
    return s


async def main():
    n = int(input('Введите количество рецептов для парсинга: '))
    for _ in range(n):
        meal = await get_meal_details()
        info = make_meal_details(meal)

        json_string_meal = json.dumps(meal)
        short_info = get_short_description(json_string_meal)

        async for db in get_db():
            await RecipeCrud.create_recipe(
                db=db,
                title=meal['title'],
                description=info,
                cuisine=meal['cuisine'],
                giga_chat_description=short_info,
                cooking_time=meal['cooking_time'],
                image_url=meal['image_url']  # Добавляем URL изображения в базу
            )

        print(f"Добавил рецепт '{meal['title']}' в базу (изображение: {meal['image_url']})")


# Запуск асинхронного кода
if __name__ == "__main__":
    asyncio.run(main())