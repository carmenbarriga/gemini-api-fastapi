import json
import logging
import re

from fastapi import HTTPException

from core import errors
from core.gemini import client, gemini_types

logger = logging.getLogger(__name__)


def length_rule(length: str) -> str:
    return {
        "short": "Write exactly 1 paragraph between 80 and 120 words.",
        "medium": "Write 2 paragraphs totaling between 160 and 240 words.",
        "detailed": "Write 3 paragraphs totaling between 240 and 360 words.",
    }[length]


def focus_rule(focus: str) -> str:
    return {
        "simple": "Use very simple language, explain like to a child.",
        "normal": "Neutral tone, easy to understand.",
        "professional": "Formal and precise tone, include technical terms.",
    }[focus]


def summarize_text(text: str, length: str, focus: str) -> dict:
    logger.info(
        "Summarize request received ✅ "
        f"(length={length}, "
        f"focus={focus}, "
        f"text_length={len(text)})"
    )

    user_prompt = f"""
    Return ONLY a JSON object with the following format:
    {{
        "summary": "<string>",
        "topic": "<string>"
    }}
    Rules:
    - 'summary' must follow:
        - {length_rule(length)}
        - {focus_rule(focus)}
    - 'topic' must be a single clear sentence describing the main theme.
    Text to summarize:
    \"\"\"{text}\"\"\"
    """

    try:
        logger.debug("Sending prompt to Gemini model...")
        logger.debug(f"❌❌❌❌USER PROMPT: {user_prompt} ❌❌❌❌❌❌❌❌")

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

        response_text = getattr(response, "text", None)
        if not response_text:
            raise errors.EMPTY_RESPONSE_ERROR

        response_text = response_text.strip()
        logger.debug(f"Raw response text (truncated): {response_text[:100]}...")

        # Clean extra formatting (e.g., ```json ... ```)
        if not response_text.startswith("{"):
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            response_text = json_match.group(0) if json_match else response_text

        parsed_data = json.loads(response_text)

        if "summary" not in parsed_data or "topic" not in parsed_data:
            raise errors.MISSING_KEYS_ERROR

        logger.info("Summarization completed successfully ✅")
        return {
            "summary": parsed_data["summary"],
            "topic": parsed_data["topic"],
            "length": length,
        }

    except json.JSONDecodeError:
        logger.exception("summarize_text: Failed to decode JSON from model response ❌")
        raise errors.INVALID_JSON_ERROR
    except HTTPException:
        raise
    except Exception:
        logger.exception("summarize_text: Unexpected error ❌")
        raise errors.UNEXPECTED_ERROR
