from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import google.generativeai as genai
import os


genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

APP_API_KEY = os.getenv("APP_API_KEY")

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
        model = genai.GenerativeModel("gemini-1.5-flash")
        resp = model.generate_content(q.question)
        return {"answer": resp.text}
    except Exception:
        # Hide internal errors from clients
        raise HTTPException(status_code=502, detail="Upstream model error")


@app.get("/health")
def health():
    return {"status": "ok"}
