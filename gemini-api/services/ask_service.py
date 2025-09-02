import logging

from fastapi import HTTPException

from core import errors
from core.gemini import client

logger = logging.getLogger(__name__)


def ask_gemini(question: str) -> str:
    try:
        logger.info("Sending request to Gemini ✅ (question_length=%d)", len(question))

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=question,
        )

        text = getattr(response, "text", None)
        text = None

        if not text:
            raise errors.EMPTY_RESPONSE_ERROR

        logger.info("Received response from Gemini ✅ (text_length=%d)", len(text))
        return text
    except HTTPException:
        raise
    except Exception:
        logger.exception("ask_gemini: Unexpected error while calling Gemini ❌")
        raise errors.UNEXPECTED_ERROR
