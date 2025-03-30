from fastapi import FastAPI
from contextlib import asynccontextmanager
import logging
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.basicConfig(level=logging.INFO)
    redis = aioredis.from_url("redis://localhost:6379")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    app.state.redis = redis
    yield
    await redis.close()

app = FastAPI(lifespan=lifespan)