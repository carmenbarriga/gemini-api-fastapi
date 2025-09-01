from fastapi import APIRouter, Depends

from core.security import verify_api_key
from models.question import Question
from services.ask_service import ask_gemini

router = APIRouter()


@router.post("/ask")
def ask(question: Question, _: bool = Depends(verify_api_key)):
    """
    Ask Gemini a free-form question.
    """
    return {"answer": ask_gemini(question.text)}
