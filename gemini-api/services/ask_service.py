from typing import cast

from fastapi import HTTPException

from core.gemini import client


def ask_gemini(question: str) -> str:
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=question,
    )

    if not response or not getattr(response, "text", None):
        raise HTTPException(status_code=502, detail="Empty response from Gemini model")

    return cast(str, response.text)
