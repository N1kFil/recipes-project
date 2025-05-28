import json
import asyncio
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from app.database.crud import RecipeCrud
from app.database.database import async_session
from sberchat import get_short_description
import re


def setup_driver():
	options = webdriver.ChromeOptions()
	options.add_argument("--disable-blink-features=AutomationControlled")
	options.add_argument(
		"user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
	options.add_argument("--window-size=1920,1080")
	options.add_experimental_option("excludeSwitches", ["enable-automation"])
	options.add_experimental_option("useAutomationExtension", False)

	driver = webdriver.Chrome(service=Service(), options=options)
	driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
		"source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """
	})
	return driver


def get_recipe_links(driver, max_links=1):
    driver.get("https://www.allrecipes.com/")
    time.sleep(random.uniform(3, 5))

    driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2)")
    time.sleep(1)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(1)

    selectors = [
        'a[href*="/recipe/"]:not([href*="javascript"])',
        'article a[href*="/recipe/"]'
    ]

    links = set()
    for selector in selectors:
        try:
            elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
            )
            for el in elements:
                href = el.get_attribute('href')
                if href and "/recipe/" in href:
                    links.add(href)
        except Exception as e:
            print(f"Ошибка при поиске по селектору {selector}: {str(e)}")
            continue

    links = list(links)
    random.shuffle(links)
    return links[:max_links]

def parse_iso8601_duration(duration_str):
    """
    Преобразует строку длительности в формате ISO 8601 в общее количество минут.
    """
    if not duration_str:
        return 0

    pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?')
    match = pattern.match(duration_str)

    if not match:
        return 0

    hours = int(match.group(1)) if match.group(1) else 0
    minutes = int(match.group(2)) if match.group(2) else 0

    return hours * 60 + minutes

def extract_recipe_data(driver):
    scripts = driver.find_elements(By.XPATH, '//script[@type="application/ld+json"]')
    for script in scripts:
        try:
            content = script.get_attribute('innerHTML')
            data_json = json.loads(content)

            def extract_steps(steps_field):
                steps_text = []
                if isinstance(steps_field, list):
                    for step in steps_field:
                        if isinstance(step, dict) and 'text' in step:
                            steps_text.append(step['text'])
                        elif isinstance(step, str):
                            steps_text.append(step)
                elif isinstance(steps_field, str):
                    steps_text.append(steps_field)
                return steps_text

            if isinstance(data_json, list):
                for entry in data_json:
                    if isinstance(entry, dict):
                        type_field = entry.get('@type')
                        if isinstance(type_field, list) and 'Recipe' in type_field or type_field == 'Recipe':
                            ingredients = entry.get('recipeIngredient', [])
                            cuisine = entry.get('recipeCuisine', 'other')
                            time_str = entry.get('totalTime', '')
                            time_minutes = parse_iso8601_duration(time_str)
                            steps = extract_steps(entry.get('recipeInstructions', []))
                            image = entry.get('image', {}).get('url') if isinstance(entry.get('image'), dict) else entry.get('image', '')
                            return ingredients, cuisine, time_minutes, steps, image
            elif isinstance(data_json, dict):
                type_field = data_json.get('@type')
                if isinstance(type_field, list) and 'Recipe' in type_field or type_field == 'Recipe':
                    ingredients = data_json.get('recipeIngredient', [])
                    cuisine = data_json.get('recipeCuisine', 'other')
                    time_str = data_json.get('totalTime', '')
                    time_minutes = parse_iso8601_duration(time_str)
                    steps = extract_steps(data_json.get('recipeInstructions', []))
                    image = data_json.get('image', {}).get('url') if isinstance(data_json.get('image'), dict) else data_json.get('image', '')
                    return ingredients, cuisine, time_minutes, steps, image

        except json.JSONDecodeError:
            continue
    return [], 'other', 0, [], ''


def parse_recipe_page(driver, url):
	try:
		driver.get(url)
		WebDriverWait(driver, 15).until(
			EC.presence_of_element_located((By.CSS_SELECTOR, "h1")))

		data = {
			'title': driver.find_element(By.CSS_SELECTOR, "h1").text,
			'description': "",
			'cuisine': "",
			'ingredients': [],
			'steps':[],
			'timem': 0,
			'url': url,
			'image_url': ""
		}

		try:
			data['description'] = driver.find_element(
				By.CSS_SELECTOR, 'p.article-subheading, div.recipe-summary-description, p.recipe-summary__description'
			).text.strip()
		except Exception as e:
			print(f"Не найдено описание: {str(e)}")

		try:
			data['ingredients'], data['cuisine'], data['timem'], data['steps'], data['image_url'] = extract_recipe_data(driver)
		except Exception as e:
			print(f"Не найдены дополнительные сведения: {str(e)}")

		print("\n Парсинг завершен. Данные:")
		print(json.dumps(data, indent=2, ensure_ascii=False))
		return data

	except Exception as e:
		print(f"Ошибка парсинга {url}: {str(e)}")
		return None

def make_meal_details(meal):
	"""Выводит полную информацию о блюде"""
	s = f"""Title: {meal['title']}
Country: {meal['cuisine'][0]}
Time cooking: {meal['timem']} minutes

Ingredients:
{"\n".join(item for item in meal["ingredients"])}

Instructions:
{".".join(item for item in meal["steps"])}
""".strip()
	return s

async def save_recipe(data):

	info = make_meal_details(data)
	json_string_meal = json.dumps(data)
	short_info = get_short_description(json_string_meal)


	async with async_session() as db:
		try:

			await RecipeCrud.create_recipe(db=db, title=data['title'], description=info,
			                               cuisine=data['cuisine'][0], giga_chat_description=short_info,
			                               cooking_time=data['timem'], image_url=data['image_url'])

			print(f"Успешно сохранено")
			return True
		except Exception as e:
			print(f"Ошибка сохранения: {str(e)}")
			await db.rollback()
			return False


async def main():
	n = int(input('Введите количество рецептов для парсинга: '))
	driver = setup_driver()
	try:
		links = get_recipe_links(driver, max_links=n)

		for i, link in enumerate(links, 1):

			data = parse_recipe_page(driver, link)
			if data:
				await save_recipe(data)

			delay = random.uniform(2, 5)
			time.sleep(delay)

	finally:
		driver.quit()


if __name__ == "__main__":
	asyncio.run(main())