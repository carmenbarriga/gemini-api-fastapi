from fastapi import HTTPException

# Gemini errors
EMPTY_RESPONSE_ERROR = HTTPException(
    status_code=502, detail="Empty response from Gemini model"
)

INVALID_JSON_ERROR = HTTPException(
    status_code=502, detail="Invalid JSON from Gemini model"
)

MISSING_KEYS_ERROR = HTTPException(
    status_code=502,
    detail="Missing keys in Gemini JSON response ('summary' or 'topic')",
)

UNEXPECTED_ERROR = HTTPException(
    status_code=502, detail="Unexpected error from Gemini model"
)
