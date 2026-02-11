import os

SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "auth-db"),
    "port": os.getenv("DB_PORT", 5432),
    "database": os.getenv("DB_NAME", "auth_service"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "password"),
}
