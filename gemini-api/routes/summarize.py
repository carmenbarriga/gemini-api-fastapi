from fastapi import APIRouter, Depends

from core.security import verify_api_key
from models.summarize import SummarizeRequest, SummarizeResponse
from services.summarize_service import summarize_text

router = APIRouter()


@router.post("/summarize", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest, _: bool = Depends(verify_api_key)):
    """
    Summarizes the input text according to the chosen 'length' and 'focus',
    and returns both the summary and the main topic.
    """
    return summarize_text(request)
