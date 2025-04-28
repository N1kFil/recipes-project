# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from sqlalchemy import update
# from passlib.context import CryptContext
# from app.database.models import User, Recipe, Review
#
# # Инициализация bcrypt
# # создается объект для шифрования паролей, использующий алгоритм bcrypt
# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
#
# # Этот класс группирует все операции над пользователями (регистрация, вход и поиск
# class UserCrud:
#
#     @staticmethod
#     async def create_user(db: AsyncSession, username: str, password: str):
#         hashed_password = pwd_context.hash(password)
#         new_user = User(username=username, hashed_password=hashed_password)
#         db.add(new_user) #Создаёт нового пользователя и добавляет его в базу данны
#         await db.commit() # сохраняет изменения
#         await db.refresh(new_user) # обновляет объект new_user, чтобы получить его id из базы
#         return new_user
#
#     @staticmethod # Ищет пользователя по имени, проверяет пароль, сверяя его с захешированным паролем, возвр юзера если все гуд
#     async def authenticate_user(db: AsyncSession, username: str, password: str):
#         query = await db.execute(select(User).where(User.username == username))
#         user = query.scalars().first()
#         if user and pwd_context.verify(password, user.hashed_password):
#             return user
#         return None
#
#     @staticmethod #Просто находит пользователя по ID
#     async def get_user_by_id(db: AsyncSession, user_id: int):
#         query = await db.execute(select(User).where(User.id == user_id))
#         return query.scalars().first()
#
#     @staticmethod # Просто находит пользователя по имени
#     async def get_user_by_username(db: AsyncSession, username: str):
#         query = await db.execute(select(User).where(User.username == username))
#         return query.scalars().first()
#
#
# # Этот класс отвечает за создание рецептов, их поиск и добавление отзывов
# class RecipeCrud:
#
#     @staticmethod
#     async def create_recipe(db: AsyncSession, title: str, description: str, cuisine: str):
#         new_recipe = Recipe(
#             title=title,
#             description=description,
#             cuisine=cuisine,
#             ratings=[],
#             average_rating=0.0,
#             ratings_count=0
#         )
#         db.add(new_recipe)
#         await db.commit()
#         await db.refresh(new_recipe)
#         return new_recipe
#
#     @staticmethod
#     async def get_recipe(db: AsyncSession, recipe_id: int):
#         query = await db.execute(select(Recipe).where(Recipe.id == recipe_id))
#         return query.scalars().first()
#
#     @staticmethod
#     async def get_recipes_by_cuisine(db: AsyncSession, cuisine: str):
#         query = await db.execute(select(Recipe).where(Recipe.cuisine == cuisine))
#         return query.scalars().all()
#
#     @staticmethod
#     async def add_review(db: AsyncSession, recipe_id: int, user_id: int, rating: int, text: str):
#         # Добавляем отзыв
#         new_review = Review(
#             recipe_id=recipe_id,
#             user_id=user_id,
#             rating=rating,
#             text=text
#         )
#         db.add(new_review)
#
#         # Обновляем список оценок рецепта
#         query = await db.execute(select(Recipe).where(Recipe.id == recipe_id))
#         recipe = query.scalars().first()
#         if recipe:
#             recipe.ratings.append(rating)
#             recipe.ratings_count = len(recipe.ratings)
#             recipe.average_rating = sum(recipe.ratings) / recipe.ratings_count
#             await db.commit()
#             await db.refresh(recipe)
#
#         await db.commit()
#         await db.refresh(new_review)
#         return new_review


import bcrypt
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.database.models import User, Recipe, Review

# Инициализация bcrypt
# для bcrypt соль генерируется автоматически в процессе хэширования
# Также bcrypt безопасно хранит соль в самом хэшированном значении

# Этот класс группирует все операции над пользователями (регистрация, вход и поиск)
class UserCrud:

    @staticmethod
    async def create_user(db: AsyncSession, username: str, password: str):
        # Генерация соли для bcrypt
        salt = bcrypt.gensalt()

        # Хэширование пароля с добавлением соли
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

        new_user = User(username=username, hashed_password=hashed_password)
        db.add(new_user)  # Создаёт нового пользователя и добавляет его в базу данных
        await db.commit()  # сохраняет изменения
        await db.refresh(new_user)  # обновляет объект new_user, чтобы получить его id из базы
        return new_user

    @staticmethod  # Ищет пользователя по имени, проверяет пароль, сверяя его с захешированным паролем, возвращает пользователя если все правильно
    async def authenticate_user(db: AsyncSession, username: str, password: str):
        query = await db.execute(select(User).where(User.username == username))
        user = query.scalars().first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.hashed_password):
            return user
        return None

    @staticmethod  # Просто находит пользователя по ID
    async def get_user_by_id(db: AsyncSession, user_id: int):
        query = await db.execute(select(User).where(User.id == user_id))
        return query.scalars().first()

    @staticmethod  # Просто находит пользователя по имени
    async def get_user_by_username(db: AsyncSession, username: str):
        query = await db.execute(select(User).where(User.username == username))
        return query.scalars().first()


# Этот класс отвечает за создание рецептов, их поиск и добавление отзывов
class RecipeCrud:

    @staticmethod
    async def create_recipe(db: AsyncSession, title: str, description: str, cuisine: str):
        new_recipe = Recipe(
            title=title,
            description=description,
            cuisine=cuisine,
            ratings=[],
            average_rating=0.0,
            ratings_count=0
        )
        db.add(new_recipe)
        await db.commit()
        await db.refresh(new_recipe)
        return new_recipe

    @staticmethod
    async def get_recipe(db: AsyncSession, recipe_id: int):
        query = await db.execute(select(Recipe).where(Recipe.id == recipe_id))
        return query.scalars().first()

    @staticmethod
    async def get_recipes_by_cuisine(db: AsyncSession, cuisine: str):
        query = await db.execute(select(Recipe).where(Recipe.cuisine == cuisine))
        return query.scalars().all()

    @staticmethod
    async def add_review(db: AsyncSession, recipe_id: int, user_id: int, rating: int, text: str):
        # Добавляем отзыв
        new_review = Review(
            recipe_id=recipe_id,
            user_id=user_id,
            rating=rating,
            text=text
        )
        db.add(new_review)

        # Обновляем список оценок рецепта
        query = await db.execute(select(Recipe).where(Recipe.id == recipe_id))
        recipe = query.scalars().first()
        if recipe:
            recipe.ratings.append(rating)
            recipe.ratings_count = len(recipe.ratings)
            recipe.average_rating = sum(recipe.ratings) / recipe.ratings_count
            await db.commit()
            await db.refresh(recipe)

        await db.commit()
        await db.refresh(new_review)
        return new_review
