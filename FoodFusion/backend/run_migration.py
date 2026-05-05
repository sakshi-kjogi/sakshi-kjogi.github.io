import asyncio
import os
import re
import ssl
from pathlib import Path
from urllib.parse import unquote

import asyncpg
from dotenv import load_dotenv

_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE

load_dotenv()


def _parse_dsn(dsn: str):
    m = re.match(r"postgresql://([^:]+):(.+)@([^:]+):(\d+)/(.+)", dsn)
    user, password_encoded, host, port, db = m.groups()
    return user, unquote(password_encoded), host, int(port), db


async def main():
    dsn = os.environ["SUPABASE_DB_URL"]
    user, password, host, port, db = _parse_dsn(dsn)
    sql = Path("migrations/001_init.sql").read_text()

    print("Connecting to database...")
    conn = await asyncpg.connect(
        host=host, port=port, user=user, password=password,
        database=db, ssl=_ssl_ctx,
    )
    try:
        await conn.execute(sql)
        print("Migration applied successfully.")
    finally:
        await conn.close()


asyncio.run(main())
