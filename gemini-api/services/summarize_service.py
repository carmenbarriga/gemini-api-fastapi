import json
import logging
import re

from fastapi import HTTPException

from core import errors
from core.gemini import client, gemini_types
from models.summarize import SummarizeRequest, SummarizeResponse

logger = logging.getLogger(__name__)


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
    logger.info(
        "Summarize request received ✅ "
        f"(length={request.length}, "
        f"focus={request.focus}, "
        f"text_length={len(request.text)})"
    )

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
        logger.debug("Sending prompt to Gemini model...")
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
        logger.debug("Response received from Gemini model")

        text = getattr(response, "text", None)
        if not text:
            logger.error("Empty response from Gemini model ❌")
            raise errors.EMPTY_RESPONSE_ERROR

        response_text = text.strip()
        logger.debug(f"Raw response text (truncated): {response_text[:100]}...")

        # Clean extra formatting (e.g., ```json ... ```)
        if not response_text.startswith("{"):
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            response_text = json_match.group(0) if json_match else response_text

        parsed_data = json.loads(response_text)

        if "summary" not in parsed_data or "topic" not in parsed_data:
            logger.error("Missing keys in response JSON ❌")
            raise errors.MISSING_KEYS_ERROR

        logger.info("Summarization completed successfully ✅")
        return SummarizeResponse(
            summary=parsed_data["summary"], topic=parsed_data["topic"]
        )

    except json.JSONDecodeError:
        logger.exception("Failed to decode JSON from model response ❌")
        raise errors.INVALID_JSON_ERROR
    except HTTPException:
        raise
    except Exception:
        logger.exception("Unexpected error during summarization ❌")
        raise errors.UNEXPECTED_ERROR
