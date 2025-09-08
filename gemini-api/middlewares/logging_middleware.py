import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("middleware")


class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.url.path == "/health":
            return await call_next(request)

        request_id = str(uuid.uuid4())[:8]
        start_time = time.perf_counter()

        try:
            response = await call_next(request)
        except Exception as exc:
            process_time = (time.perf_counter() - start_time) * 1000
            logger.error(
                "[%s] ❌ %s %s failed after %.2fms - %s",
                request_id,
                request.method,
                request.url.path,
                process_time,
                str(exc),
            )
            raise

        process_time = (time.perf_counter() - start_time) * 1000
        logger.info(
            "[%s] %s %s %d completed in %.2fms",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            process_time,
        )

        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time"] = f"{process_time:.2f}ms"

        return response
