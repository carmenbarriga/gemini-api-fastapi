import json
import re

from fastapi import HTTPException

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

        if not response or not getattr(response, "text", None):
            raise HTTPException(
                status_code=502, detail="Empty response from Gemini model"
            )

        response_text = response.text.strip()

        # Clean extra formatting (e.g., ```json ... ```)
        if not response_text.startswith("{"):
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            response_text = json_match.group(0) if json_match else response_text

        parsed_data = json.loads(response_text)

        if "summary" not in parsed_data or "topic" not in parsed_data:
            raise HTTPException(
                status_code=502,
                detail="Missing keys in Gemini JSON response ('summary' or 'topic')",
            )

        return SummarizeResponse(
            summary=parsed_data["summary"], topic=parsed_data["topic"]
        )

    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="Invalid JSON from Gemini model")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=502, detail="Unexpected error from Gemini model"
        )
