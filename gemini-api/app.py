import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError, ResponseValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from core.logging_config import setup_logging
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


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(
        "❌ Unhandled error (500) on %s %s",
        request.method,
        request.url.path,
    )
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(
        "❌ HTTPException (%d) on %s %s - %s",
        exc.status_code,
        request.method,
        request.url.path,
        exc.detail,
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def request_validation_handler(request: Request, exc: RequestValidationError):
    error_list = exc.errors()
    details = []

    for err in error_list:
        loc = ".".join(str(x) for x in err.get("loc", []))
        msg = err.get("msg", "Request validation error")
        details.append(f"{loc}: {msg}")

    logger.error(
        "❌ Request validation failed (422) on %s %s - %s",
        request.method,
        request.url.path,
        "; ".join(details),
    )

    return JSONResponse(
        status_code=422,
        content={"detail": "Request validation failed (invalid input)"},
    )


@app.exception_handler(ResponseValidationError)
async def response_validation_handler(request: Request, exc: ResponseValidationError):
    error_list = exc.errors()
    details = []

    for err in error_list:
        loc = ".".join(str(x) for x in err.get("loc", []))
        msg = err.get("msg", "Response Validation Error")
        details.append(f"{loc}: {msg}")

    logger.error(
        "❌ Response validation failed (422) on %s %s - %s",
        request.method,
        request.url.path,
        "; ".join(details),
    )

    return JSONResponse(
        status_code=422,
        content={"detail": "Response validation failed (invalid response)"},
    )
