import re
import ssl
from typing import Optional
from urllib.parse import unquote

import asyncpg

from app.config.settings import settings

_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE

_pool: Optional[asyncpg.Pool] = None


def _parse_dsn(dsn: str) -> dict:
    m = re.match(r"postgresql://([^:]+):(.+)@([^:]+):(\d+)/(.+)", dsn)
    user, password_encoded, host, port, db = m.groups()
    return {
        "user": user,
        "password": unquote(password_encoded),
        "host": host,
        "port": int(port),
        "database": db,
    }


async def init_db() -> None:
    global _pool
    params = _parse_dsn(settings.SUPABASE_DB_URL)
    _pool = await asyncpg.create_pool(
        **params,
        min_size=2,
        max_size=10,
        ssl=_ssl_ctx,
    )


async def close_db() -> None:
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def get_pool() -> asyncpg.Pool:
    if _pool is None:
        raise RuntimeError("Database pool is not initialized")
    return _pool
