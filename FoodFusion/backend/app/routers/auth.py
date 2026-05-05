import asyncpg
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from app.config.settings import settings
from app.db.database import get_pool
from app.repositories import user_repository
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest
from app.security.dependencies import get_current_user
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


def _cookie_opts() -> dict:
    return {
        "httponly": True,
        "secure": settings.ENVIRONMENT == "production",
        "samesite": "lax",
    }


def _set_auth_cookies(
    response: Response, access_token: str, refresh_token: str
) -> None:
    opts = _cookie_opts()
    response.set_cookie(
        "access_token",
        access_token,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        **opts,
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        **opts,
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: RegisterRequest,
    response: Response,
    pool: asyncpg.Pool = Depends(get_pool),
) -> AuthResponse:
    result = await auth_service.register_user(pool, data)
    user = result["user"]
    _set_auth_cookies(response, result["access_token"], result["refresh_token"])
    return AuthResponse(
        user_id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        active_role=user["role"],
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    data: LoginRequest,
    response: Response,
    pool: asyncpg.Pool = Depends(get_pool),
) -> AuthResponse:
    result = await auth_service.login_user(pool, data)
    user = result["user"]
    _set_auth_cookies(response, result["access_token"], result["refresh_token"])
    return AuthResponse(
        user_id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        active_role=user["role"],
    )


@router.post("/refresh", response_model=AuthResponse)
async def refresh(
    request: Request,
    response: Response,
    pool: asyncpg.Pool = Depends(get_pool),
) -> AuthResponse:
    token = request.cookies.get("refresh_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token missing",
        )
    result = await auth_service.refresh_tokens(pool, token)
    _set_auth_cookies(response, result["access_token"], result["refresh_token"])

    async with pool.acquire() as conn:
        user = await user_repository.get_user_by_id(conn, result["user_id"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return AuthResponse(
        user_id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        active_role=user["role"],
    )


@router.get("/me", response_model=AuthResponse)
async def me(
    current_user: dict = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_pool),
) -> AuthResponse:
    async with pool.acquire() as conn:
        user = await user_repository.get_user_by_id(conn, current_user["sub"])
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return AuthResponse(
        user_id=user["id"],
        email=user["email"],
        full_name=user["full_name"],
        active_role=user["role"],
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    current_user: dict = Depends(get_current_user),
    pool: asyncpg.Pool = Depends(get_pool),
) -> None:
    await auth_service.logout_user(pool, current_user["sub"])
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
