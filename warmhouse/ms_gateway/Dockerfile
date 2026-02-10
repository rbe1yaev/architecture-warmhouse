FROM python:3.11-slim

WORKDIR /app

# Установка зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Запуск приложения
CMD ["uvicorn", "app:app", "--reload", "--host", "0.0.0.0", "--port", "8001"]