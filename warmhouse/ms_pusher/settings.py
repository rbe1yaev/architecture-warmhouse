import os

PUSHER_CLUSTER = os.getenv("PUSHER_CLUSTER", "cluster1")
KAFKA_BROKERS = os.getenv("KAFKA_BROKERS", "kafka:9092")
PUSHER_APP_ID = os.getenv("PUSHER_APP_ID", "app_id")
PUSHER_KEY = os.getenv("PUSHER_KEY", "app_id")
PUSHER_SECRET = os.getenv("PUSHER_SECRET", "app_id")
FAKE_PUSHER = os.getenv("FAKE_PUSHER", True)
