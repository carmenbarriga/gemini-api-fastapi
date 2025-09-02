import logging

from fastapi import APIRouter, Depends

from core.security import verify_api_key
from models.ask import AskRequest, AskResponse
from services.ask_service import ask_gemini

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/ask", response_model=AskResponse, tags=["Ask"])
def ask(request: AskRequest, _: bool = Depends(verify_api_key)):
    """
    Ask Gemini a free-form question.
    """
    logger.info("POST /ask called ✅ (question_length=%d)", len(request.question))

    answer = ask_gemini(request.question)

    logger.info("POST /ask completed ✅ (answer_length=%d)", len(answer))

    return {"answer": answer}
