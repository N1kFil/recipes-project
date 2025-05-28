# RecipesProject

RecipesProject — это веб-приложение для хранения рецептов с возможностью оценки, фильтрации и интеграции с AI (GigaChat/SberAI) для генерации описаний. Парсер автоматически наполняет базу рецептами с AllRecipes.com и themealdb.

---

## Технологический стек
| Категория       | Технологии                                                                 |
|----------------|---------------------------------------------------------------------------|
| Backend    | Python 3.11, FastAPI, SQLAlchemy 2.0, AsyncPG, Pydantic                  |
| Frontend   | HTML/CSS, Jinja2 (шаблоны), JavaScript (для динамических элементов)       |
| База данных | PostgreSQL 15                                                            |
| Парсинг    | Selenium                                 |
| AI         | SberAI/GigaChat (для генерации кратких описаний)                          |
| Деплой     | Docker (опционально)                                              |

## Инструкция

1. Перейти в recipes-project/app и создать папку certs
2. Перейти в recipes-project/app/certs использовать команды из auth/README.md
