from fastapi import FastAPI
from app.db import DATABASE_URL, REDIS_URL
import logging
from contextlib import asynccontextmanager
from psycopg_pool import AsyncConnectionPool

# for logs, we can use: debug(), info(), warning(), error()
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
            open=False
    )

    try:
        await pool.open(wait=True, timeout=10)
        async with pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute("SELECT 1")
                row = await cur.fetchone()
                if not row or row[0] != 1:
                    raise RuntimeError("Unexpected healthcheck result")
        logging.info("postgres ok")
        app.state.pool = pool
    except Exception as e:
        logging.error("postgres check failed: %s", type(e).__name__)
        await pool.close()
        raise

    
    yield

    logging.info("gateway shutting down...")

    await pool.close()

app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"status": "gateway service running"}

@app.get("/health")
def health():
    return {"status": "ok"}
