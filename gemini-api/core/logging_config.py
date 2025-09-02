import logging

from core.config import settings


def setup_logging() -> None:
    log_level = settings.log_level

    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info(f"✅ Logging is configured (level={log_level})")
