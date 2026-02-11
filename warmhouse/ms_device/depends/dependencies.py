from asyncpg import Pool

DEPS = {}


def get_db() -> Pool:
    return DEPS["db"]


def get_kafka():
    return DEPS["kafka"]
