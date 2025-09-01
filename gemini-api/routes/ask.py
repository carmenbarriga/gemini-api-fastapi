from fastapi import APIRouter, Depends, HTTPException

from core.security import verify_api_key
from models.question import Question
from services.ask_service import ask_gemini

router = APIRouter()


@router.post("/ask")
def ask(question: Question, _: bool = Depends(verify_api_key)):
    """
    Ask Gemini a free-form question.
    """
    try:
        return {"answer": ask_gemini(question.text)}
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=502, detail="Unexpected error from Gemini model"
        )
