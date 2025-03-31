from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(level=logging.INFO)
    redis = aioredis.from_url("redis://redis_app:5370/0")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    app.state.redis = redis
    yield
    await redis.close()

app = FastAPI(lifespan=lifespan)

# Настройки CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
