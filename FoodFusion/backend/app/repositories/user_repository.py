import uuid
from typing import Optional

import asyncpg


def _row_to_user(row: asyncpg.Record) -> dict:
    result = dict(row)
    result["id"] = str(result["id"])
    return result


async def get_user_by_email(conn: asyncpg.Connection, email: str) -> Optional[dict]:
    row = await conn.fetchrow("SELECT * FROM users WHERE email = $1", email)
    return _row_to_user(row) if row else None


async def get_user_by_id(conn: asyncpg.Connection, user_id: str) -> Optional[dict]:
    row = await conn.fetchrow("SELECT * FROM users WHERE id = $1::uuid", user_id)
    return _row_to_user(row) if row else None


async def create_user(
    conn: asyncpg.Connection,
    email: str,
    password_hash: str,
    full_name: str,
    role: str,
) -> dict:
    row = await conn.fetchrow(
        """
        INSERT INTO users (id, email, password_hash, full_name, role, created_at)
        VALUES ($1, $2, $3, $4, $5, NOW())
        RETURNING *
        """,
        uuid.uuid4(),
        email,
        password_hash,
        full_name,
        role,
    )
    return _row_to_user(row)


async def store_refresh_token(
    conn: asyncpg.Connection, user_id: str, token: str
) -> None:
    await conn.execute(
        """
        INSERT INTO refresh_tokens (user_id, token, created_at)
        VALUES ($1::uuid, $2, NOW())
        ON CONFLICT (user_id) DO UPDATE
            SET token = EXCLUDED.token, created_at = NOW()
        """,
        user_id,
        token,
    )


async def get_refresh_token_record(
    conn: asyncpg.Connection, token: str
) -> Optional[dict]:
    row = await conn.fetchrow(
        "SELECT * FROM refresh_tokens WHERE token = $1", token
    )
    if row is None:
        return None
    result = dict(row)
    result["user_id"] = str(result["user_id"])
    return result


async def delete_refresh_token(conn: asyncpg.Connection, user_id: str) -> None:
    await conn.execute(
        "DELETE FROM refresh_tokens WHERE user_id = $1::uuid", user_id
    )
