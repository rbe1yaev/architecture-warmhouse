import os

CLICKHOUSE_URL = f"http://{os.getenv('CLICKHOUSE_HOST', 'clickhouse')}:8123"
CLICKHOUSE_DB = os.getenv('CLICKHOUSE_DB', 'telemetry')
