import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.db.database import close_db, init_db
from app.routers import auth as auth_router

logger = logging.getLogger("foodfusion")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Retry DB connection up to 5 times (handles resumed Supabase projects)
    for attempt in range(1, 6):
        try:
            await init_db()
            logger.info("Database pool ready.")
            break
        except Exception as exc:
            if attempt == 5:
                raise RuntimeError(f"Could not connect to database after 5 attempts: {exc}") from exc
            wait = attempt * 3
            logger.warning("DB connection attempt %d failed (%s) — retrying in %ds", attempt, exc, wait)
            await asyncio.sleep(wait)
    yield
    await close_db()


app = FastAPI(title="FoodFusion API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router, prefix="/api/v1")


@app.get("/health", tags=["health"])
async def health() -> dict:
    return {"status": "ok"}
