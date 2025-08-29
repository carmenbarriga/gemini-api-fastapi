import json
import os
import re
from typing import Annotated, Literal

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from google.genai import Client, types
from pydantic import BaseModel, Field, StringConstraints

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
APP_API_KEY = os.getenv("APP_API_KEY")

client = Client(api_key=GEMINI_API_KEY)

app = FastAPI()
security = HTTPBearer()


def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != APP_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True


class Question(BaseModel):
    text: str


@app.post("/ask")
def ask_gemini(question: Question, _: bool = Depends(verify_api_key)):
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=question.text
        )
        return {"answer": response.text}
    except Exception:
        raise HTTPException(status_code=502, detail="Upstream model error")


class SummarizeRequest(BaseModel):
    text: Annotated[str, StringConstraints(min_length=20)] = Field(
        ..., description="Text to resume (20 characters minimum)"
    )
    length: Literal["short", "medium", "detailed"] = "medium"
    focus: Literal["simple", "normal", "professional"] = "normal"


class SummarizeResponse(BaseModel):
    summary: str
    topic: str


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


@app.post("/summarize", response_model=SummarizeResponse)
def summarize(request: SummarizeRequest, _: bool = Depends(verify_api_key)):
    """
    Summarizes the input text according to the chosen 'length' and 'focus',
    and returns both the summary and the main topic.
    """

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
            config=types.GenerateContentConfig(
                system_instruction=(
                    "You are an assistant that always returns VALID JSON."
                ),
                response_mime_type="application/json",
            ),
        )

        if not response or not getattr(response, "text", None):
            raise HTTPException(status_code=502, detail="Empty response from model")

        response_text = response.text.strip()

        # Clean extra formatting (e.g., ```json ... ```)
        if not response_text.startswith("{"):
            json_match = re.search(r"\{.*\}", response_text, re.DOTALL)
            response_text = json_match.group(0) if json_match else response_text

        parsed_data = json.loads(response_text)

        if "summary" not in parsed_data or "topic" not in parsed_data:
            raise HTTPException(status_code=502, detail="Missing keys in JSON response")

        return SummarizeResponse(
            summary=parsed_data["summary"], topic=parsed_data["topic"]
        )

    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="Invalid JSON from model")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=502, detail="Upstream model error")


@app.get("/health")
def health():
    return {"status": "ok"}
