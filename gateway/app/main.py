import logging
from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI
from psycopg_pool import AsyncConnectionPool

from app.db import DATABASE_URL, REDIS_URL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("gateway starting...")
    pool = AsyncConnectionPool(
        conninfo=DATABASE_URL,
        min_size=1,
        max_size=10,
        open=False,
    )
    redis_client = redis.from_url(
        REDIS_URL,
        decode_responses=True,
        socket_connect_timeout=5,
    )

    try:
        try:
            await pool.open(wait=True, timeout=10)
            async with pool.connection() as conn:
                async with conn.cursor() as cur:
                    await cur.execute("SELECT 1")
                    row = await cur.fetchone()
                    if not row or row[0] != 1:
                        raise RuntimeError("Unexpected healthcheck result")
            app.state.pool = pool
            logging.info("postgres ok")
        except Exception as e:
            logging.error("postgres check failed: %s", type(e).__name__)
            raise

        try:
            if not await redis_client.ping():
                raise RuntimeError("redis ping failed")
            app.state.redis = redis_client
            logging.info("redis ok")
        except Exception as e:
            logging.error("redis check failed: %s", type(e).__name__)
            raise

        yield  # App runs and serves requests here

    finally:
        logging.info("gateway shutting down...")
        await redis_client.aclose()
        await pool.close()


app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_root():
    return {"status": "gateway service running"}


@app.get("/health")
def health():
    return {"status": "ok"}
