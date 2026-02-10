FROM python:3.11-slim

WORKDIR /app

COPY warmhouse/ms_device/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

CMD ["uvicorn", "warmhouse.ms_device.app:app", "--reload", "--host", "0.0.0.0", "--port", "8002"]