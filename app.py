import os

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.genai import Client
from pydantic import BaseModel

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
APP_API_KEY = os.getenv("APP_API_KEY")

client = Client(api_key=GEMINI_API_KEY)

app = FastAPI()
security = HTTPBearer()


def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != APP_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True


class Question(BaseModel):
    question: str


@app.post("/ask")
def ask_gemini(q: Question, _: bool = Depends(verify_api_key)):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=q.question
        )
        return {"answer": response.text}
    except Exception:
        # Hide internal errors from clients
        raise HTTPException(status_code=502, detail="Upstream model error")


@app.get("/health")
def health():
    return {"status": "ok"}
