from asyncpg import Pool

from warmhouse.ms_auth.utils import DEPS


def get_db() -> Pool:
    return DEPS["db"]
