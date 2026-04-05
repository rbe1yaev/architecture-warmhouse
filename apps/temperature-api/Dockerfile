# первый слой для зависимостей
FROM python:3.12-alpine AS builder

ENV PYTHONDONTWRITEBYTECODE=1  PYTHONUNBUFFERED=1

WORKDIR /build

COPY requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir --prefix=/install -r requirements.txt

# второй слой для запуска приложения
FROM python:3.12-alpine AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTHONPATH=/app

RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

COPY --from=builder /install /usr/local

COPY --chown=appuser:appgroup main.py .

USER appuser

EXPOSE 8081

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081", "--workers", "1", "--no-access-log"]
