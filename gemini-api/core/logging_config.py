import logging
import os

from dotenv import load_dotenv


def setup_logging() -> None:
    load_dotenv()

    log_level = os.getenv("LOG_LEVEL", "INFO").upper()

    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info(f"✅ Logging is configured (level={log_level})")
