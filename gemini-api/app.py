import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.logging_config import setup_logging
from middlewares.logging_middleware import LoggingMiddleware
from routes import ask, health, summarize

setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup ---
    logger.info("🚀 Gemini API is starting up...")

    yield
    # --- Shutdown ---
    logger.info("🛑 Gemini API is shutting down...")


app = FastAPI(
    title="Gemini API",
    description=(
        "An API powered by the Gemini model that provides two main features:\n\n"
        "- **Ask**: Send a question and get a direct response.\n"
        "- **Summarize**: Generate a summary and main topic from a given text. "
        "Supports different summary lengths and focus levels.\n\n"
        "All responses are structured and validated to ensure consistency."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(ask.router)
app.include_router(summarize.router)
app.include_router(health.router)

app.add_middleware(LoggingMiddleware)


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError):
    error_list = exc.errors()
    details = []

    for error in error_list:
        loc = ".".join(str(x) for x in error.get("loc", []))
        msg = error.get("msg", "Request validation error")
        details.append(f"{loc}: {msg}")

    logger.warning(
        "⚠️ Request validation failed on %s %s - %s",
        request.method,
        request.url.path,
        "; ".join(details),
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Request validation failed"},
    )


@app.exception_handler(ResponseValidationError)
async def response_validation_handler(request: Request, exc: ResponseValidationError):
    error_list = exc.errors()
    details = []

    for error in error_list:
        loc = ".".join(str(x) for x in error.get("loc", []))
        msg = error.get("msg", "Response validation error")
        details.append(f"{loc}: {msg}")

    logger.error(
        "❌ Response validation failed on %s %s - %s",
        request.method,
        request.url.path,
        "; ".join(details),
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    log_level = logging.ERROR if exc.status_code >= 500 else logging.WARNING

    logger.log(
        log_level,
        "HTTPException (%d) on %s %s - %s",
        exc.status_code,
        request.method,
        request.url.path,
        exc.detail,
    )

    detail = exc.detail if exc.status_code < 500 else "Internal Server Error"

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": detail},
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "❌ Unhandled exception on %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )
