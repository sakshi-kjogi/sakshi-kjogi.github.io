import asyncpg
from fastapi import HTTPException, status
from jose import JWTError

from app.repositories import user_repository
from app.schemas.auth import LoginRequest, RegisterRequest
from app.security.jwt_handler import create_token, decode_token
from app.security.password import hash_password, verify_password


async def register_user(pool: asyncpg.Pool, data: RegisterRequest) -> dict:
    async with pool.acquire() as conn:
        if await user_repository.get_user_by_email(conn, data.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        user = await user_repository.create_user(
            conn, data.email, hash_password(data.password), data.full_name, data.role
        )
        access_token = create_token(user["id"], user["email"], user["role"], "access")
        refresh_token = create_token(user["id"], user["email"], user["role"], "refresh")
        await user_repository.store_refresh_token(conn, user["id"], refresh_token)

    return {"user": user, "access_token": access_token, "refresh_token": refresh_token}


async def login_user(pool: asyncpg.Pool, data: LoginRequest) -> dict:
    async with pool.acquire() as conn:
        user = await user_repository.get_user_by_email(conn, data.email)
        if not user or not verify_password(data.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )
        access_token = create_token(user["id"], user["email"], user["role"], "access")
        refresh_token = create_token(user["id"], user["email"], user["role"], "refresh")
        await user_repository.store_refresh_token(conn, user["id"], refresh_token)

    return {"user": user, "access_token": access_token, "refresh_token": refresh_token}


async def refresh_tokens(pool: asyncpg.Pool, token: str) -> dict:
    try:
        payload = decode_token(token)
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
        )

    async with pool.acquire() as conn:
        if not await user_repository.get_refresh_token_record(conn, token):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh token not recognised",
            )
        user_id: str = payload["sub"]
        email: str = payload["email"]
        role: str = payload["active_role"]

        new_access = create_token(user_id, email, role, "access")
        new_refresh = create_token(user_id, email, role, "refresh")
        await user_repository.store_refresh_token(conn, user_id, new_refresh)

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "user_id": user_id,
        "email": email,
        "active_role": role,
    }


async def logout_user(pool: asyncpg.Pool, user_id: str) -> None:
    async with pool.acquire() as conn:
        await user_repository.delete_refresh_token(conn, user_id)
