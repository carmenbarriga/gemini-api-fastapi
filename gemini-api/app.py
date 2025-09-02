import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
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
    logger.exception("Unhandled error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error("HTTPExceptionCARMEN: %s - %s", exc.status_code, exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail_CARMEN": exc.detail},
    )
