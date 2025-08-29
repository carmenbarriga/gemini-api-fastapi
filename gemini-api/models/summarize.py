from typing import Annotated, Literal

from pydantic import BaseModel, Field, StringConstraints


class SummarizeRequest(BaseModel):
    text: Annotated[str, StringConstraints(min_length=20)] = Field(
        ..., description="Text to resume (20 characters minimum)"
    )
    length: Literal["short", "medium", "detailed"] = "medium"
    focus: Literal["simple", "normal", "professional"] = "normal"


class SummarizeResponse(BaseModel):
    summary: str
    topic: str
