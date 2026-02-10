import os


DB_CONFIG = {
    "host": os.getenv("DB_HOST", "device-manager-db"),
    "port": os.getenv("DB_PORT", 5432),
    "database": os.getenv("DB_NAME", "device_manager"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password")
}

DEVICE_SERVICE_URL = os.getenv("DEVICE_SERVICE_URL", "http://device-service:8002")
