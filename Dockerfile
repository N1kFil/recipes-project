# Используем официальный образ Python как базовый
FROM python:3.10-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем все файлы проекта в контейнер
COPY . .

# Устанавливаем зависимости из requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Устанавливаем зависимости для работы с PostgreSQL (если они не указаны в requirements.txt)
RUN apt-get update && apt-get install -y libpq-dev

# Открываем порт для FastAPI (по умолчанию 8000)
EXPOSE 8000

# Запуск приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
