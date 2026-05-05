import asyncio
import os
import re
import ssl
import sys
from urllib.parse import unquote

import asyncpg
from dotenv import load_dotenv

load_dotenv()

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE


def parse_dsn(dsn: str) -> dict:
    m = re.match(r"postgresql://([^:]+):(.+)@([^:/?]+):(\d+)/([^?]+)", dsn)
    if not m:
        raise ValueError(f"Cannot parse DSN: {dsn}")
    user, pwd_enc, host, port, db = m.groups()
    return dict(user=user, password=unquote(pwd_enc), host=host, port=int(port), database=db)


async def main():
    raw = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("SUPABASE_DB_URL", "")
    if not raw:
        print("No DSN. Pass as argument or set SUPABASE_DB_URL in .env")
        return

    try:
        params = parse_dsn(raw)
    except ValueError as e:
        print(f"Parse error: {e}")
        return

    print(f"Connecting to {params['host']}:{params['port']} as {params['user']} ...")
    try:
        conn = await asyncio.wait_for(
            asyncpg.connect(**params, ssl=ssl_ctx), timeout=10
        )
        version = await conn.fetchval("SELECT version()")
        await conn.close()
        print(f"SUCCESS -- {version[:80]}")
    except Exception as e:
        print(f"FAILED  -- {e}")


asyncio.run(main())
