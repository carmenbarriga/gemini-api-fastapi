from fastapi import FastAPI

from core.logging_config import setup_logging
from routes import ask, health, summarize

setup_logging()

app = FastAPI()

app.include_router(ask.router)
app.include_router(summarize.router)
app.include_router(health.router)
