from asyncpg import Pool

from warmhouse.ms_device.app import DEPS


def get_db() -> Pool:
    return DEPS["db"]

def get_kafka():
    return DEPS["kafka"]