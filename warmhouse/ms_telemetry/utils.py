import logging

import aiohttp

from warmhouse.ms_telemetry.settings import CLICKHOUSE_DB, CLICKHOUSE_URL

logger = logging.getLogger(__name__)


async def execute_clickhouse_query(query: str):
    try:
        async with aiohttp.ClientSession() as session:
            params = {
                "database": CLICKHOUSE_DB,
                "query": query
            }
            async with session.post(CLICKHOUSE_URL, params=params) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    text = await resp.text()
                    logger.error(f"ClickHouse error: {text}")
                    return None
    except Exception as e:
        logger.error(f"ClickHouse connection error: {e}")
        return None
