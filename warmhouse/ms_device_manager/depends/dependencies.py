from asyncpg import Pool

from warmhouse.ms_device_manager.utils import DEPS


def get_db() -> Pool:
    return DEPS["db"]


def get_client():
    return DEPS["client"]
