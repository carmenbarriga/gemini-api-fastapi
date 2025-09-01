from fastapi import FastAPI

from routes import ask, health, summarize

app = FastAPI()

app.include_router(ask.router)
app.include_router(summarize.router)
app.include_router(health.router)
