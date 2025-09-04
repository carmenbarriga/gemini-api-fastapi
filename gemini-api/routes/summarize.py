import logging

from fastapi import APIRouter, Depends

from core.security import verify_api_key
from models.summarize import SummarizeRequest, SummarizeResponse
from services.summarize_service import summarize_text

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/summarize", response_model=SummarizeResponse, tags=["Summarize"])
def summarize(request: SummarizeRequest, _: bool = Depends(verify_api_key)):
    """
    Summarizes the input text according to the chosen 'length' and 'focus',
    and returns both the summary and the main topic.
    """
    logger.info(
        "POST /summarize called ✅ (text_length=%d, length=%s, focus=%s)",
        len(request.text),
        request.length,
        request.focus,
    )

    response = summarize_text(request.text, request.length, request.focus)

    logger.info(
        "POST /summarize completed ✅ (summary_length=%d, topic=%s)",
        len(response["summary"]),
        response["topic"],
    )

    return response
