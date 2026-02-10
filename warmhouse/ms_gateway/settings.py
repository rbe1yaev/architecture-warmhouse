import os

SERVICES = {
    "auth": os.getenv("AUTH_SERVICE_URL", "http://auth-service:8001"),
    "device": os.getenv("DEVICE_SERVICE_URL", "http://device-service:8002"),
    "device_manager": os.getenv("DEVICE_MANAGER_URL", "http://device-manager:8003"),
    "telemetry": os.getenv("TELEMETRY_SERVICE_URL", "http://telemetry-service:8004"),
    "notification": os.getenv("NOTIFICATION_SERVICE_URL", "http://notification-service:8005"),
}
