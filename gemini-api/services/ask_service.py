from fastapi import HTTPException

from core import errors
from core.gemini import client


def ask_gemini(question: str) -> str:
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=question,
        )

        text = getattr(response, "text", None)

        if not text:
            raise errors.EMPTY_RESPONSE_ERROR

        return text
    except HTTPException:
        raise
    except Exception:
        raise errors.UNEXPECTED_ERROR
