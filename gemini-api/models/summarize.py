from typing import Literal

from pydantic import BaseModel, Field, model_validator


class SummarizeRequest(BaseModel):
    text: str = Field(
        min_length=20,
        max_length=2000,
        description="Text to resume (20 characters minimum)",
        examples=[
            "Artificial Intelligence is a branch of computer science that focuses on "
            "creating machines capable of performing tasks that typically "
            "require human intelligence."
        ],
    )
    length: Literal["short", "medium", "detailed"] = Field(
        default="medium", description="Length of the summary", examples=["short"]
    )
    focus: Literal["simple", "normal", "professional"] = Field(
        default="normal",
        description="Level of complexity or style for the summary",
        examples=["simple"],
    )


WORD_LIMITS = {
    "short": (80, 120),
    "medium": (160, 240),
    "detailed": (240, 360),
}

TOLERANCE = 0.1


def in_tolerance_range(length_type: str, word_count: int) -> bool:
    min_words, max_words = WORD_LIMITS[length_type]
    min_allowed = int(min_words * (1 - TOLERANCE))
    max_allowed = int(max_words * (1 + TOLERANCE))
    return min_allowed <= word_count <= max_allowed


class SummarizeResponse(BaseModel):
    summary: str = Field(
        description="The generated summary of the text",
        examples=["AI enables machines to perform intelligent tasks."],
    )
    topic: str = Field(
        min_length=3,
        max_length=200,
        description="The main topic of the text",
        examples=["Artificial Intelligence"],
    )
    length: Literal["short", "medium", "detailed"] = Field(
        default="medium",
        description="Requested summary length (for validation)",
        exclude=True,
    )

    @model_validator(mode="after")
    def check_summary_word_count(self):
        word_count = len(self.summary.split())

        min_words, max_words = WORD_LIMITS[self.length]

        min_allowed = int(min_words * (1 - TOLERANCE))
        max_allowed = int(max_words * (1 + TOLERANCE))

        if not (min_allowed <= word_count <= max_allowed):
            raise ValueError(
                f"Summary word count out of range for '{self.length}' mode "
                f"(expected {min_words}-{max_words} words, allowed "
                f"{min_allowed}-{max_allowed}, got {word_count})"
            )
        return self
