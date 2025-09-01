import json
import re

from fastapi import HTTPException

from core import errors
from core.gemini import client, gemini_types
from models.summarize import SummarizeRequest, SummarizeResponse


def length_rule(length: str) -> str:
    return {
        "short": "1–2 sentences, max ~50 words.",
        "medium": "One cohesive paragraph (~80–120 words).",
        "detailed": "5–7 bullet points with key information.",
    }[length]


def focus_rule(focus: str) -> str:
    return {
        "simple": "Use very simple language, explain like to a child.",
        "normal": "Neutral tone, easy to understand.",
        "professional": "Formal and precise tone, include technical terms.",
    }[focus]


def summarize_text(request: SummarizeRequest) -> SummarizeResponse:
    user_prompt = f"""
    Return ONLY a JSON object with the following format:
    {{
        "summary": "<string>",
        "topic": "<string>"
    }}
    Rules:
    - 'summary' must follow:
        - {length_rule(request.length)}
        - {focus_rule(request.focus)}
    - 'topic' must be a single clear sentence describing the main theme.
    Text to summarize:
    \"\"\"{request.text}\"\"\"
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=user_prompt,
            config=gemini_types.GenerateContentConfig(
                system_instruction=(
                    "You are an assistant that always returns VALID JSON."
                ),
                response_mime_type="application/json",
            ),
        )

        text = getattr(response, "text", None)
        if not text:
            raise errors.EMPTY_RESPONSE_ERROR

        response_text = text.strip()

        # Clean extra formatting (e.g., ```json ... ```)
        if not response_text.startswith("{"):
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            response_text = json_match.group(0) if json_match else response_text

        parsed_data = json.loads(response_text)

        if "summary" not in parsed_data or "topic" not in parsed_data:
            raise errors.MISSING_KEYS_ERROR

        return SummarizeResponse(
            summary=parsed_data["summary"], topic=parsed_data["topic"]
        )

    except json.JSONDecodeError:
        raise errors.INVALID_JSON_ERROR
    except HTTPException:
        raise
    except Exception:
        raise errors.UNEXPECTED_ERROR
