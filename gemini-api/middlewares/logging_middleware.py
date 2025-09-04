import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("middleware")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid.uuid4())[:8]
        start = time.time()

        try:
            response = await call_next(request)
        except Exception as exc:
            process_time = (time.time() - start) * 1000
            logger.error(
                "[%s] ❌ %s %s failed after %.2fms - %s",
                request_id,
                request.method,
                request.url.path,
                process_time,
                str(exc),
            )
            raise

        process_time = (time.time() - start) * 1000
        logger.info(
            "[%s] %s %s %d completed in %.2fms",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            process_time,
        )

        response.headers["X-Request-ID"] = request_id
        return response
