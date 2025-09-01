import logging

from fastapi import APIRouter, Depends

from core.security import verify_api_key
from models.question import Question
from services.ask_service import ask_gemini

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/ask")
def ask(question: Question, _: bool = Depends(verify_api_key)):
    """
    Ask Gemini a free-form question.
    """
    logger.info("POST /ask called ✅ (question_length=%d)", len(question.text))

    answer = ask_gemini(question.text)

    logger.info("POST /ask completed ✅ (answer_length=%d)", len(answer))

    return {"answer": answer}
