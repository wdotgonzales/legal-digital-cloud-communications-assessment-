import os 
from dotenv import load_dotenv
from pathlib import Path
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

load_dotenv()

REQUIRED_VARIABLES = ["DATABASE_URL", "REDIS_URL"] 

for variable in REQUIRED_VARIABLES:
    if not os.environ.get(variable):
        logging.error(f"{variable} is not set")
        raise RuntimeError(f"{variable} is not set.")

logging.info("Config loaded successfully")

DATABASE_URL: str | None = os.getenv("DATABASE_URL")
REDIS_URL: str | None = os.getenv("REDIS_URL")
